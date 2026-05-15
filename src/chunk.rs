use anyhow::Result;
use std::io::BufRead;

#[derive(Clone, Copy, Debug)]
pub enum ChunkPolicy {
    FixedLines { lines: u64, byte_cap: Option<usize> },
    ProgressiveLines { byte_cap: Option<usize> },
    ByteTarget { bytes: usize },
}

impl ChunkPolicy {
    pub fn id(self) -> u32 {
        match self {
            ChunkPolicy::FixedLines {
                lines: 512,
                byte_cap: None,
            } => 13,
            ChunkPolicy::FixedLines {
                lines: 1024,
                byte_cap: None,
            } => 14,
            ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: None,
            } => 1,
            ChunkPolicy::ProgressiveLines { byte_cap: None } => 2,
            ChunkPolicy::ByteTarget { bytes } if bytes == 1024 * 1024 => 3,
            ChunkPolicy::ByteTarget { bytes } if bytes == 4 * 1024 * 1024 => 4,
            ChunkPolicy::ByteTarget { bytes } if bytes == 8 * 1024 * 1024 => 5,
            ChunkPolicy::ProgressiveLines {
                byte_cap: Some(bytes),
            } if bytes == 4 * 1024 * 1024 => 6,
            ChunkPolicy::ProgressiveLines {
                byte_cap: Some(bytes),
            } if bytes == 8 * 1024 * 1024 => 7,
            ChunkPolicy::ProgressiveLines {
                byte_cap: Some(bytes),
            } if bytes == 16 * 1024 * 1024 => 8,
            ChunkPolicy::ProgressiveLines {
                byte_cap: Some(bytes),
            } if bytes == 32 * 1024 * 1024 => 9,
            ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(bytes),
            } if bytes == 8 * 1024 * 1024 => 10,
            ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(bytes),
            } if bytes == 16 * 1024 * 1024 => 11,
            ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(bytes),
            } if bytes == 32 * 1024 * 1024 => 12,
            _ => 0,
        }
    }
}

#[derive(Debug)]
pub struct PlainChunk {
    pub index: u64,
    pub first_line_number: u64,
    pub line_count: u64,
    pub data: Vec<u8>,
    pub flags: u16,
}

#[derive(Debug)]
pub struct Chunker {
    policy: ChunkPolicy,
    next_index: u64,
    next_line_number: u64,
}

impl Chunker {
    pub fn new(policy: ChunkPolicy) -> Self {
        Self {
            policy,
            next_index: 0,
            next_line_number: 1,
        }
    }

    pub fn next_chunk<R: BufRead>(&mut self, reader: &mut R) -> Result<Option<PlainChunk>> {
        let line_limit = self.current_line_limit();
        let byte_cap = self.current_byte_cap();

        let mut data = Vec::new();
        let mut line = Vec::new();
        let mut line_count = 0u64;
        let mut oversized_line = false;

        loop {
            line.clear();
            let bytes_read = reader.read_until(b'\n', &mut line)?;

            if bytes_read == 0 {
                break;
            }

            if data.is_empty() && byte_cap.is_some_and(|cap| line.len() > cap) {
                oversized_line = true;
                data.extend_from_slice(&line);
                line_count += 1;
                break;
            }

            if !data.is_empty() && byte_cap.is_some_and(|cap| data.len() + line.len() > cap) {
                break;
            }

            data.extend_from_slice(&line);
            line_count += 1;

            if line_count >= line_limit {
                break;
            }
        }

        if data.is_empty() {
            return Ok(None);
        }

        let chunk = PlainChunk {
            index: self.next_index,
            first_line_number: self.next_line_number,
            line_count,
            data,
            flags: if oversized_line { 0x0002 } else { 0x0001 },
        };

        self.next_index += 1;
        self.next_line_number += line_count;

        Ok(Some(chunk))
    }

    fn current_line_limit(&self) -> u64 {
        match self.policy {
            ChunkPolicy::FixedLines { lines, .. } => lines,
            ChunkPolicy::ProgressiveLines { .. } => match self.next_index {
                0 => 4_096,
                1 => 8_192,
                2 => 16_384,
                3 => 32_768,
                _ => 65_536,
            },
            ChunkPolicy::ByteTarget { .. } => u64::MAX,
        }
    }

    fn current_byte_cap(&self) -> Option<usize> {
        match self.policy {
            ChunkPolicy::FixedLines { byte_cap, .. } => byte_cap,
            ChunkPolicy::ProgressiveLines { byte_cap } => byte_cap,
            ChunkPolicy::ByteTarget { bytes } => Some(bytes),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn progressive_line_limits_ramp_to_64k() {
        let mut chunker = Chunker::new(ChunkPolicy::ProgressiveLines { byte_cap: None });
        assert_eq!(chunker.current_line_limit(), 4_096);
        chunker.next_index = 1;
        assert_eq!(chunker.current_line_limit(), 8_192);
        chunker.next_index = 2;
        assert_eq!(chunker.current_line_limit(), 16_384);
        chunker.next_index = 3;
        assert_eq!(chunker.current_line_limit(), 32_768);
        chunker.next_index = 4;
        assert_eq!(chunker.current_line_limit(), 65_536);
    }
}
