use anyhow::{anyhow, Result};
use memchr::memmem::Finder;
use regex::bytes::RegexBuilder;

const SUMMARY_MAGIC: &[u8; 4] = b"ZSM1";
const SUMMARY_VERSION: u16 = 1;
const BYTE_CLASS_LEN: usize = 32;
const BIGRAM_LEN: usize = 8192;
const SUMMARY_LEN: usize = 4 + 2 + 2 + BYTE_CLASS_LEN + BIGRAM_LEN + BYTE_CLASS_LEN + BIGRAM_LEN;

#[derive(Clone, Debug)]
pub struct GrepOptions {
    pub fixed_strings: bool,
    pub perl_regexp: bool,
    pub only_matching: bool,
    pub line_number: bool,
    pub ignore_case: bool,
    pub count: bool,
    pub files_with_matches: bool,
    pub invert_match: bool,
}

#[derive(Clone, Debug)]
pub struct SearchSummary {
    disabled: bool,
    byte_class: [u8; BYTE_CLASS_LEN],
    bigram: [u8; BIGRAM_LEN],
    lower_byte_class: [u8; BYTE_CLASS_LEN],
    lower_bigram: [u8; BIGRAM_LEN],
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SearchSummaryMode {
    Bitmap,
    None,
}

impl SearchSummary {
    pub fn disabled() -> Self {
        Self {
            disabled: true,
            byte_class: [0u8; BYTE_CLASS_LEN],
            bigram: [0u8; BIGRAM_LEN],
            lower_byte_class: [0u8; BYTE_CLASS_LEN],
            lower_bigram: [0u8; BIGRAM_LEN],
        }
    }

    pub fn from_bytes(bytes: &[u8]) -> Self {
        let mut summary = Self {
            disabled: false,
            byte_class: [0u8; BYTE_CLASS_LEN],
            bigram: [0u8; BIGRAM_LEN],
            lower_byte_class: [0u8; BYTE_CLASS_LEN],
            lower_bigram: [0u8; BIGRAM_LEN],
        };

        for byte in bytes {
            set_byte_bit(&mut summary.byte_class, *byte);
            set_byte_bit(&mut summary.lower_byte_class, byte.to_ascii_lowercase());
        }

        for pair in bytes.windows(2) {
            set_bigram_bit(&mut summary.bigram, pair[0], pair[1]);
            set_bigram_bit(
                &mut summary.lower_bigram,
                pair[0].to_ascii_lowercase(),
                pair[1].to_ascii_lowercase(),
            );
        }

        summary
    }

    pub fn encode(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(SUMMARY_LEN);
        out.extend_from_slice(SUMMARY_MAGIC);
        out.extend_from_slice(&SUMMARY_VERSION.to_le_bytes());
        out.extend_from_slice(&0u16.to_le_bytes());
        out.extend_from_slice(&self.byte_class);
        out.extend_from_slice(&self.bigram);
        out.extend_from_slice(&self.lower_byte_class);
        out.extend_from_slice(&self.lower_bigram);
        out
    }

    pub fn decode(bytes: &[u8]) -> Result<Self> {
        if bytes.is_empty() {
            return Ok(Self::disabled());
        }

        if bytes.len() != SUMMARY_LEN {
            return Err(anyhow!(
                "invalid search summary length: expected {}, got {}",
                SUMMARY_LEN,
                bytes.len()
            ));
        }

        if &bytes[..4] != SUMMARY_MAGIC {
            return Err(anyhow!("invalid search summary magic"));
        }

        let version = u16::from_le_bytes([bytes[4], bytes[5]]);
        if version != SUMMARY_VERSION {
            return Err(anyhow!("unsupported search summary version {version}"));
        }

        let mut offset = 8;

        let mut byte_class = [0u8; BYTE_CLASS_LEN];
        byte_class.copy_from_slice(&bytes[offset..offset + BYTE_CLASS_LEN]);
        offset += BYTE_CLASS_LEN;

        let mut bigram = [0u8; BIGRAM_LEN];
        bigram.copy_from_slice(&bytes[offset..offset + BIGRAM_LEN]);
        offset += BIGRAM_LEN;

        let mut lower_byte_class = [0u8; BYTE_CLASS_LEN];
        lower_byte_class.copy_from_slice(&bytes[offset..offset + BYTE_CLASS_LEN]);
        offset += BYTE_CLASS_LEN;

        let mut lower_bigram = [0u8; BIGRAM_LEN];
        lower_bigram.copy_from_slice(&bytes[offset..offset + BIGRAM_LEN]);

        Ok(Self {
            disabled: false,
            byte_class,
            bigram,
            lower_byte_class,
            lower_bigram,
        })
    }

    pub fn may_contain_literal(&self, literal: &[u8], ignore_case: bool) -> bool {
        if self.disabled {
            return true;
        }

        if literal.is_empty() {
            return true;
        }

        let mut normalized;
        let literal = if ignore_case {
            normalized = literal.to_vec();
            normalized.make_ascii_lowercase();
            normalized.as_slice()
        } else {
            literal
        };

        let byte_class = if ignore_case {
            &self.lower_byte_class
        } else {
            &self.byte_class
        };

        let bigram = if ignore_case {
            &self.lower_bigram
        } else {
            &self.bigram
        };

        if literal.len() == 1 {
            return has_byte_bit(byte_class, literal[0]);
        }

        literal
            .windows(2)
            .all(|pair| has_bigram_bit(bigram, pair[0], pair[1]))
    }
}

#[derive(Debug)]
pub struct Matcher {
    engine: Engine,
    options: GrepOptions,
    selector_literal: Option<Vec<u8>>,
}

#[derive(Debug)]
enum Engine {
    Fixed { pattern: Vec<u8> },
    Regex { regex: regex::bytes::Regex },
    Fancy { regex: fancy_regex::Regex },
}

impl Matcher {
    pub fn new(pattern: &str, options: GrepOptions) -> Result<Self> {
        let selector_literal = selector_literal(pattern, &options);

        let engine = if options.fixed_strings {
            Engine::Fixed {
                pattern: pattern.as_bytes().to_vec(),
            }
        } else if options.perl_regexp {
            let pattern = if options.ignore_case {
                format!("(?i:{pattern})")
            } else {
                pattern.to_string()
            };
            Engine::Fancy {
                regex: fancy_regex::Regex::new(&pattern)?,
            }
        } else {
            Engine::Regex {
                regex: RegexBuilder::new(pattern)
                    .case_insensitive(options.ignore_case)
                    .build()?,
            }
        };

        Ok(Self {
            engine,
            options,
            selector_literal,
        })
    }

    pub fn chunk_may_match(&self, summary: &SearchSummary) -> bool {
        match &self.selector_literal {
            Some(literal) => summary.may_contain_literal(literal, self.options.ignore_case),
            None => true,
        }
    }

    pub fn selector_kind(&self) -> &'static str {
        if self.selector_literal.is_some() {
            "literal"
        } else {
            "none"
        }
    }

    pub fn selector_len(&self) -> usize {
        self.selector_literal.as_ref().map_or(0, Vec::len)
    }

    pub fn line_matches(&self, line: &[u8]) -> Result<bool> {
        match &self.engine {
            Engine::Fixed { pattern } => {
                Ok(fixed_contains(line, pattern, self.options.ignore_case))
            }
            Engine::Regex { regex } => Ok(regex.is_match(line)),
            Engine::Fancy { regex } => {
                let line = String::from_utf8_lossy(line);
                Ok(regex.is_match(&line)?)
            }
        }
    }

    pub fn find_matches(&self, line: &[u8]) -> Result<Vec<Vec<u8>>> {
        match &self.engine {
            Engine::Fixed { pattern } => {
                Ok(fixed_find_all(line, pattern, self.options.ignore_case))
            }
            Engine::Regex { regex } => Ok(regex
                .find_iter(line)
                .map(|m| m.as_bytes().to_vec())
                .collect()),
            Engine::Fancy { regex } => {
                let line = String::from_utf8_lossy(line);
                let mut out = Vec::new();

                for item in regex.find_iter(&line) {
                    let item = item?;
                    out.push(item.as_str().as_bytes().to_vec());
                }

                Ok(out)
            }
        }
    }
}

fn selector_literal(pattern: &str, options: &GrepOptions) -> Option<Vec<u8>> {
    if options.fixed_strings {
        return non_empty(pattern.as_bytes());
    }

    if options.perl_regexp {
        return selector_from_positive_lookbehind(pattern)
            .or_else(|| conservative_regex_literal(pattern));
    }

    conservative_regex_literal(pattern)
}

fn conservative_regex_literal(pattern: &str) -> Option<Vec<u8>> {
    if has_unescaped_top_level_or(pattern) {
        return None;
    }

    let mut best = Vec::new();
    let mut current = Vec::new();
    let mut in_class = false;
    let mut escaped = false;

    for byte in pattern.bytes() {
        if escaped {
            if is_literal_escape(byte) {
                current.push(unescape_literal(byte));
            } else {
                flush_best(&mut best, &mut current);
            }
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => {
                escaped = true;
            }
            b'[' => {
                flush_best(&mut best, &mut current);
                in_class = true;
            }
            b']' => {
                in_class = false;
            }
            b'(' | b')' | b'{' | b'}' | b'*' | b'+' | b'?' | b'^' | b'$' | b'.' if !in_class => {
                flush_best(&mut best, &mut current);
            }
            b'|' if !in_class => {
                return None;
            }
            _ if !in_class => {
                current.push(byte);
            }
            _ => {}
        }
    }

    flush_best(&mut best, &mut current);

    if best.len() >= 2 {
        Some(best)
    } else {
        None
    }
}

fn selector_from_positive_lookbehind(pattern: &str) -> Option<Vec<u8>> {
    let prefix = "(?<=";
    let start = pattern.find(prefix)?;
    let after = start + prefix.len();
    let rest = &pattern[after..];
    let end = rest.find(')')?;
    let candidate = &rest[..end];

    if candidate.bytes().all(|b| {
        !matches!(
            b,
            b'[' | b']'
                | b'('
                | b')'
                | b'{'
                | b'}'
                | b'*'
                | b'+'
                | b'?'
                | b'|'
                | b'^'
                | b'$'
                | b'.'
        )
    }) {
        non_empty(candidate.as_bytes())
    } else {
        None
    }
}

fn has_unescaped_top_level_or(pattern: &str) -> bool {
    let mut escaped = false;
    let mut in_class = false;
    let mut depth = 0i32;

    for byte in pattern.bytes() {
        if escaped {
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => escaped = true,
            b'[' if !in_class => in_class = true,
            b']' if in_class => in_class = false,
            b'(' if !in_class => depth += 1,
            b')' if !in_class && depth > 0 => depth -= 1,
            b'|' if !in_class && depth == 0 => return true,
            _ => {}
        }
    }

    false
}

fn non_empty(bytes: &[u8]) -> Option<Vec<u8>> {
    if bytes.is_empty() {
        None
    } else {
        Some(bytes.to_vec())
    }
}

fn flush_best(best: &mut Vec<u8>, current: &mut Vec<u8>) {
    if current.len() > best.len() {
        *best = current.clone();
    }
    current.clear();
}

fn is_literal_escape(byte: u8) -> bool {
    matches!(
        byte,
        b'\\' | b'"' | b'\'' | b'/' | b'.' | b'-' | b'_' | b'=' | b':' | b' '
    )
}

fn unescape_literal(byte: u8) -> u8 {
    byte
}

fn fixed_contains(line: &[u8], pattern: &[u8], ignore_case: bool) -> bool {
    if pattern.is_empty() {
        return true;
    }

    if ignore_case {
        let mut line = line.to_vec();
        let mut pattern = pattern.to_vec();
        line.make_ascii_lowercase();
        pattern.make_ascii_lowercase();
        Finder::new(&pattern).find(&line).is_some()
    } else {
        Finder::new(pattern).find(line).is_some()
    }
}

fn fixed_find_all(line: &[u8], pattern: &[u8], ignore_case: bool) -> Vec<Vec<u8>> {
    if pattern.is_empty() {
        return Vec::new();
    }

    if ignore_case {
        let mut lower_line = line.to_vec();
        let mut lower_pattern = pattern.to_vec();
        lower_line.make_ascii_lowercase();
        lower_pattern.make_ascii_lowercase();

        let finder = Finder::new(&lower_pattern);
        finder
            .find_iter(&lower_line)
            .map(|start| line[start..start + pattern.len()].to_vec())
            .collect()
    } else {
        let finder = Finder::new(pattern);
        finder
            .find_iter(line)
            .map(|start| line[start..start + pattern.len()].to_vec())
            .collect()
    }
}

fn set_byte_bit(bits: &mut [u8; BYTE_CLASS_LEN], byte: u8) {
    let idx = byte as usize;
    bits[idx / 8] |= 1 << (idx % 8);
}

fn has_byte_bit(bits: &[u8; BYTE_CLASS_LEN], byte: u8) -> bool {
    let idx = byte as usize;
    (bits[idx / 8] & (1 << (idx % 8))) != 0
}

fn set_bigram_bit(bits: &mut [u8; BIGRAM_LEN], first: u8, second: u8) {
    let idx = ((first as usize) << 8) | second as usize;
    bits[idx / 8] |= 1 << (idx % 8);
}

fn has_bigram_bit(bits: &[u8; BIGRAM_LEN], first: u8, second: u8) -> bool {
    let idx = ((first as usize) << 8) | second as usize;
    (bits[idx / 8] & (1 << (idx % 8))) != 0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn summary_detects_literal_bigrams() {
        let summary = SearchSummary::from_bytes(b"alpha beta gamma\n");
        assert!(summary.may_contain_literal(b"alpha", false));
        assert!(summary.may_contain_literal(b"beta", false));
        assert!(!summary.may_contain_literal(b"delta", false));
    }

    #[test]
    fn summary_supports_ascii_ignore_case() {
        let summary = SearchSummary::from_bytes(b"Failed Password\n");
        assert!(summary.may_contain_literal(b"failed password", true));
        assert!(!summary.may_contain_literal(b"failed password", false));
    }

    #[test]
    fn fixed_find_all_preserves_original_case() {
        let matches = fixed_find_all(b"Error ERROR error", b"error", true);
        assert_eq!(
            matches,
            vec![b"Error".to_vec(), b"ERROR".to_vec(), b"error".to_vec()]
        );
    }

    #[test]
    fn conservative_literal_extracts_key_prefix() {
        let lit = conservative_regex_literal(r#"key="[^"]+""#).unwrap();
        assert_eq!(lit, br#"key=""#.to_vec());
    }
}
