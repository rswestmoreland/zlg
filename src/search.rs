use anyhow::{anyhow, Result};
use std::hash::{BuildHasherDefault, Hasher};
use memchr::memmem::{self, Finder};
use pcre2::bytes::RegexBuilder as Pcre2RegexBuilder;
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
    pub max_count: Option<usize>,
    pub stream_decode: bool,
}

#[derive(Clone, Debug)]
pub struct SearchSummary {
    disabled: bool,
    path_windows: Option<PathWindowSummary>,
    mesh_bigrams: Option<BigramMeshSummary>,
    byte_class: [u8; BYTE_CLASS_LEN],
    bigram: [u8; BIGRAM_LEN],
    lower_byte_class: [u8; BYTE_CLASS_LEN],
    lower_bigram: [u8; BIGRAM_LEN],
}

#[derive(Clone, Debug)]
struct PathWindowSummary {
    hashes: Vec<u64>,
}

#[derive(Clone, Debug)]
struct BigramMeshSummary {
    edges: Vec<u32>,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct MeshSummaryBuildStats {
    pub raw_edge_windows: u64,
    pub pushed_edges: u64,
    pub unique_edges: u64,
    pub bitset_resizes: u64,
    pub bitset_cleared_edges: u64,
    pub touched_first_buckets: u64,
    pub bitset_scratch_bytes: u64,
    pub first_bitset_scratch_bytes: u64,
    pub group_bucket_scratch_bytes: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SearchSummaryMode {
    Bitmap,
    PathWindow,
    MeshBigram,
    None,
}

const PATH_WINDOW_MAGIC: &[u8; 4] = b"ZPW1";
const PATH_WINDOW_VERSION: u16 = 1;
const BIGRAM_MESH_MAGIC: &[u8; 4] = b"ZBM1";
const BIGRAM_MESH_VERSION: u16 = 2;
const U24_EDGE_SPACE_BITS: usize = 1 << 24;
const U24_EDGE_SPACE_WORDS: usize = U24_EDGE_SPACE_BITS / 64;
const FIRST_BYTE_SUFFIX_BITS: usize = 1 << 16;
const FIRST_BYTE_SUFFIX_WORDS: usize = FIRST_BYTE_SUFFIX_BITS / 64;
const GROUPED_FIRST_BYTE_BUCKETS: usize = 32;
const PATH_WINDOW_MIN: usize = 6;
const PATH_WINDOW_MID: usize = 8;
const PATH_WINDOW_MAX: usize = 12;
const FNV_OFFSET: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

impl SearchSummary {
    pub fn disabled() -> Self {
        Self {
            disabled: true,
            path_windows: None,
            mesh_bigrams: None,
            byte_class: [0u8; BYTE_CLASS_LEN],
            bigram: [0u8; BIGRAM_LEN],
            lower_byte_class: [0u8; BYTE_CLASS_LEN],
            lower_bigram: [0u8; BIGRAM_LEN],
        }
    }

    pub fn from_bytes(bytes: &[u8]) -> Self {
        let mut summary = Self {
            disabled: false,
            path_windows: None,
            mesh_bigrams: None,
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

    pub fn from_path_windows(bytes: &[u8]) -> Self {
        let mut hashes = Vec::new();
        collect_window_hashes(bytes, &mut hashes);

        if has_ascii_uppercase(bytes) {
            let mut lower = bytes.to_vec();
            lower.make_ascii_lowercase();
            collect_window_hashes(&lower, &mut hashes);
        }

        hashes.sort_unstable();
        hashes.dedup();

        Self {
            disabled: false,
            path_windows: Some(PathWindowSummary { hashes }),
            mesh_bigrams: None,
            byte_class: [0u8; BYTE_CLASS_LEN],
            bigram: [0u8; BIGRAM_LEN],
            lower_byte_class: [0u8; BYTE_CLASS_LEN],
            lower_bigram: [0u8; BIGRAM_LEN],
        }
    }

    pub fn from_bigram_mesh(bytes: &[u8]) -> Self {
        let mut edges = Vec::with_capacity(bytes.len().saturating_sub(2));
        collect_bigram_edges(bytes, &mut edges);

        if has_ascii_uppercase(bytes) {
            let mut lower = bytes.to_vec();
            lower.make_ascii_lowercase();
            edges.reserve(lower.len().saturating_sub(2));
            collect_bigram_edges(&lower, &mut edges);
        }

        edges.sort_unstable();
        edges.dedup();

        Self {
            disabled: false,
            path_windows: None,
            mesh_bigrams: Some(BigramMeshSummary { edges }),
            byte_class: [0u8; BYTE_CLASS_LEN],
            bigram: [0u8; BIGRAM_LEN],
            lower_byte_class: [0u8; BYTE_CLASS_LEN],
            lower_bigram: [0u8; BIGRAM_LEN],
        }
    }

    pub fn encode(&self) -> Vec<u8> {
        if let Some(path_windows) = &self.path_windows {
            let mut out = Vec::with_capacity(12 + path_windows.hashes.len() * 8);
            out.extend_from_slice(PATH_WINDOW_MAGIC);
            out.extend_from_slice(&PATH_WINDOW_VERSION.to_le_bytes());
            out.extend_from_slice(&0u16.to_le_bytes());
            out.extend_from_slice(&(path_windows.hashes.len() as u32).to_le_bytes());
            for hash in &path_windows.hashes {
                out.extend_from_slice(&hash.to_le_bytes());
            }
            return out;
        }

        if let Some(mesh) = &self.mesh_bigrams {
            let mut out = Vec::with_capacity(12 + mesh.edges.len() * 3);
            encode_bigram_mesh_edges_into(&mesh.edges, &mut out);
            return out;
        }

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

        if bytes.len() >= 12 && &bytes[..4] == PATH_WINDOW_MAGIC {
            let version = u16::from_le_bytes([bytes[4], bytes[5]]);
            if version != PATH_WINDOW_VERSION {
                return Err(anyhow!("unsupported path-window summary version {version}"));
            }

            let count = u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize;
            let expected = 12 + count * 8;
            if bytes.len() != expected {
                return Err(anyhow!(
                    "invalid path-window summary length: expected {}, got {}",
                    expected,
                    bytes.len()
                ));
            }

            let mut hashes = Vec::with_capacity(count);
            let mut offset = 12;
            for _ in 0..count {
                let mut raw = [0u8; 8];
                raw.copy_from_slice(&bytes[offset..offset + 8]);
                hashes.push(u64::from_le_bytes(raw));
                offset += 8;
            }
            hashes.sort_unstable();
            hashes.dedup();

            return Ok(Self {
                disabled: false,
                path_windows: Some(PathWindowSummary { hashes }),
                mesh_bigrams: None,
                byte_class: [0u8; BYTE_CLASS_LEN],
                bigram: [0u8; BIGRAM_LEN],
                lower_byte_class: [0u8; BYTE_CLASS_LEN],
                lower_bigram: [0u8; BIGRAM_LEN],
            });
        }

        if bytes.len() >= 12 && &bytes[..4] == BIGRAM_MESH_MAGIC {
            let version = u16::from_le_bytes([bytes[4], bytes[5]]);
            if version != 1 && version != BIGRAM_MESH_VERSION {
                return Err(anyhow!("unsupported bigram mesh summary version {version}"));
            }

            let count = u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize;
            let mut edges = Vec::with_capacity(count);

            if version == 1 {
                let expected = 12 + count * 4;
                if bytes.len() != expected {
                    return Err(anyhow!(
                        "invalid bigram mesh summary length: expected {}, got {}",
                        expected,
                        bytes.len()
                    ));
                }

                let mut offset = 12;
                for _ in 0..count {
                    let mut raw = [0u8; 4];
                    raw.copy_from_slice(&bytes[offset..offset + 4]);
                    edges.push(u32::from_le_bytes(raw) & 0x00ff_ffff);
                    offset += 4;
                }
            } else {
                let mut offset = 12;
                let mut previous = 0u32;
                for index in 0..count {
                    let delta = read_varint_u32(bytes, &mut offset)?;
                    let edge = if index == 0 {
                        delta
                    } else {
                        previous.checked_add(delta).ok_or_else(|| {
                            anyhow!("bigram mesh edge delta overflow at index {index}")
                        })?
                    };
                    if edge > 0x00ff_ffff {
                        return Err(anyhow!(
                            "bigram mesh edge out of range at index {}: {}",
                            index,
                            edge
                        ));
                    }
                    edges.push(edge);
                    previous = edge;
                }

                if offset != bytes.len() {
                    return Err(anyhow!(
                        "invalid bigram mesh summary length: consumed {}, got {}",
                        offset,
                        bytes.len()
                    ));
                }
            }

            edges.sort_unstable();
            edges.dedup();

            return Ok(Self {
                disabled: false,
                path_windows: None,
                mesh_bigrams: Some(BigramMeshSummary { edges }),
                byte_class: [0u8; BYTE_CLASS_LEN],
                bigram: [0u8; BIGRAM_LEN],
                lower_byte_class: [0u8; BYTE_CLASS_LEN],
                lower_bigram: [0u8; BIGRAM_LEN],
            });
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
            path_windows: None,
            mesh_bigrams: None,
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

        if let Some(path_windows) = &self.path_windows {
            return path_windows.may_contain_literal(literal);
        }

        if let Some(mesh) = &self.mesh_bigrams {
            return mesh.may_contain_literal(literal);
        }

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

impl PathWindowSummary {
    fn may_contain_literal(&self, literal: &[u8]) -> bool {
        if literal.len() < PATH_WINDOW_MIN {
            return true;
        }

        let window = if literal.len() >= PATH_WINDOW_MAX {
            PATH_WINDOW_MAX
        } else if literal.len() >= PATH_WINDOW_MID {
            PATH_WINDOW_MID
        } else {
            PATH_WINDOW_MIN
        };

        literal.windows(window).all(|part| {
            self.hashes
                .binary_search(&hash_window(window as u8, part))
                .is_ok()
        })
    }
}

impl BigramMeshSummary {
    fn may_contain_literal(&self, literal: &[u8]) -> bool {
        if literal.len() < 3 {
            return true;
        }

        literal
            .windows(3)
            .all(|edge| self.edges.binary_search(&pack_bigram_edge(edge)).is_ok())
    }
}

fn has_ascii_uppercase(bytes: &[u8]) -> bool {
    bytes.iter().any(|byte| byte.is_ascii_uppercase())
}

pub fn encode_bigram_mesh_summary_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    let mut stats = collect_bigram_mesh_edges(bytes, edges, lower);
    finish_bigram_mesh_summary(edges, out, &mut stats);
    stats
}

pub fn encode_bigram_mesh_summary_radix_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    sort_scratch: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    let mut stats = collect_bigram_mesh_edges(bytes, edges, lower);
    radix_sort_u24(edges, sort_scratch);
    edges.dedup();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_identity_hash_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    type EdgeSet = std::collections::HashSet<u32, BuildHasherDefault<EdgeIdentityHasher>>;

    edges.clear();
    let capacity = bytes.len().saturating_sub(2);
    let mut seen = EdgeSet::with_capacity_and_hasher(capacity, BuildHasherDefault::default());
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };
    collect_bigram_edges_unique_identity(bytes, &mut seen, edges, &mut stats);

    if has_ascii_uppercase(bytes) {
        lower.clear();
        lower.extend_from_slice(bytes);
        lower.make_ascii_lowercase();
        collect_bigram_edges_unique_identity(lower, &mut seen, edges, &mut stats);
    }

    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_hash_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    use std::collections::HashSet;

    edges.clear();
    let capacity = bytes.len().saturating_sub(2);
    let mut seen = HashSet::with_capacity(capacity);
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };
    collect_bigram_edges_unique(bytes, &mut seen, edges, &mut stats);

    if has_ascii_uppercase(bytes) {
        lower.clear();
        lower.extend_from_slice(bytes);
        lower.make_ascii_lowercase();
        collect_bigram_edges_unique(lower, &mut seen, edges, &mut stats);
    }

    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_case_raw_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };
    collect_bigram_edges_counted(bytes, edges, &mut stats);
    finish_bigram_mesh_summary(edges, out, &mut stats);
    stats
}

pub fn encode_bigram_mesh_summary_lower_only_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            edges.push(pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            ));
            stats.pushed_edges += 1;
        }
    }

    finish_bigram_mesh_summary(edges, out, &mut stats);
    stats
}

pub fn encode_bigram_mesh_summary_inline_lower_delta_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2).saturating_mul(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let original = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
            edges.push(original);
            stats.pushed_edges += 1;

            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            if lowered != original {
                edges.push(lowered);
                stats.pushed_edges += 1;
            }
        }
    }

    finish_bigram_mesh_summary(edges, out, &mut stats);
    stats
}

pub fn encode_bigram_mesh_summary_bitset_seen_into(
    bytes: &[u8],
    bitset: &mut Vec<u64>,
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    let resized = ensure_full_u24_bitset(bitset);
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2).saturating_mul(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        bitset_resizes: resized as u64,
        bitset_scratch_bytes: bitset.len() as u64 * 8,
        ..MeshSummaryBuildStats::default()
    };

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let original = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
            push_edge_if_unseen(original, bitset, edges, &mut stats);

            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            if lowered != original {
                push_edge_if_unseen(lowered, bitset, edges, &mut stats);
            }
        }
    }

    clear_full_bitset_edges(edges, bitset, &mut stats);
    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_lower_only_bitset_seen_into(
    bytes: &[u8],
    bitset: &mut Vec<u64>,
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    let resized = ensure_full_u24_bitset(bitset);
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        bitset_resizes: resized as u64,
        bitset_scratch_bytes: bitset.len() as u64 * 8,
        ..MeshSummaryBuildStats::default()
    };

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            push_edge_if_unseen(lowered, bitset, edges, &mut stats);
        }
    }

    clear_full_bitset_edges(edges, bitset, &mut stats);
    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_sparse_first_bitset_into(
    bytes: &[u8],
    first_bitsets: &mut Vec<Vec<u64>>,
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    if first_bitsets.len() < 256 {
        first_bitsets.resize_with(256, Vec::new);
    }

    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2).saturating_mul(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        first_bitset_scratch_bytes: first_bitset_scratch_bytes(first_bitsets),
        ..MeshSummaryBuildStats::default()
    };
    let mut touched_first = [false; 256];

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let original = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
            push_edge_if_unseen_first_bitset(
                original,
                first_bitsets,
                &mut touched_first,
                edges,
                &mut stats,
            );

            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            if lowered != original {
                push_edge_if_unseen_first_bitset(
                    lowered,
                    first_bitsets,
                    &mut touched_first,
                    edges,
                    &mut stats,
                );
            }
        }
    }

    for edge in edges.iter().copied() {
        clear_first_bitset_edge(edge, first_bitsets);
        stats.bitset_cleared_edges += 1;
    }
    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    stats.touched_first_buckets = touched_first.iter().filter(|value| **value).count() as u64;
    stats.first_bitset_scratch_bytes = first_bitset_scratch_bytes(first_bitsets);
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_trie_pair_bitset_into(
    bytes: &[u8],
    pair_index: &mut Vec<[u16; 256]>,
    pair_bitsets: &mut Vec<Vec<[u64; 4]>>,
    touched_pairs: &mut Vec<(u8, u8)>,
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    if pair_index.len() < 256 {
        pair_index.resize(256, [u16::MAX; 256]);
    }
    if pair_bitsets.len() < 256 {
        pair_bitsets.resize_with(256, Vec::new);
    }

    touched_pairs.clear();
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2).saturating_mul(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        first_bitset_scratch_bytes: trie_pair_bitset_scratch_bytes(pair_index, pair_bitsets),
        ..MeshSummaryBuildStats::default()
    };
    let mut touched_first = [false; 256];

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let original = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
            push_edge_if_unseen_trie_pair(
                original,
                pair_index,
                pair_bitsets,
                touched_pairs,
                &mut touched_first,
                edges,
                &mut stats,
            );

            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            if lowered != original {
                push_edge_if_unseen_trie_pair(
                    lowered,
                    pair_index,
                    pair_bitsets,
                    touched_pairs,
                    &mut touched_first,
                    edges,
                    &mut stats,
                );
            }
        }
    }

    for edge in edges.iter().copied() {
        clear_trie_pair_edge(edge, pair_index, pair_bitsets);
        stats.bitset_cleared_edges += 1;
    }
    for (first, second) in touched_pairs.iter().copied() {
        pair_index[first as usize][second as usize] = u16::MAX;
    }
    for bucket in pair_bitsets.iter_mut() {
        bucket.clear();
    }

    edges.sort_unstable();
    stats.unique_edges = edges.len() as u64;
    stats.touched_first_buckets = touched_first.iter().filter(|value| **value).count() as u64;
    stats.first_bitset_scratch_bytes = trie_pair_bitset_scratch_bytes(pair_index, pair_bitsets);
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_rdxsort_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    use rdxsort::RdxSort;

    let mut stats = collect_bigram_mesh_edges(bytes, edges, lower);
    edges.rdxsort();
    edges.dedup();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_rdst_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    use rdst::RadixSort;

    let mut stats = collect_bigram_mesh_edges(bytes, edges, lower);
    edges.radix_sort_unstable();
    edges.dedup();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_grouped_buckets_into(
    bytes: &[u8],
    buckets: &mut Vec<Vec<u32>>,
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    if buckets.len() < GROUPED_FIRST_BYTE_BUCKETS {
        buckets.resize_with(GROUPED_FIRST_BYTE_BUCKETS, Vec::new);
    }
    for bucket in buckets.iter_mut() {
        bucket.clear();
    }

    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };

    if bytes.len() >= 3 {
        for index in 0..bytes.len() - 2 {
            let original = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
            push_edge_to_grouped_bucket(original, buckets, &mut stats);

            let lowered = pack_bigram_edge_bytes(
                ascii_lower_byte(bytes[index]),
                ascii_lower_byte(bytes[index + 1]),
                ascii_lower_byte(bytes[index + 2]),
            );
            if lowered != original {
                push_edge_to_grouped_bucket(lowered, buckets, &mut stats);
            }
        }
    }

    edges.clear();
    for bucket in buckets.iter_mut() {
        if bucket.is_empty() {
            continue;
        }
        bucket.sort_unstable();
        bucket.dedup();
        edges.extend(bucket.iter().copied());
    }

    stats.unique_edges = edges.len() as u64;
    stats.group_bucket_scratch_bytes = grouped_bucket_scratch_bytes(buckets);
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

pub fn encode_bigram_mesh_summary_bucket256_into(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    sort_scratch: &mut Vec<u32>,
    lower: &mut Vec<u8>,
    out: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    let mut stats = collect_bigram_mesh_edges(bytes, edges, lower);
    bucket_sort_dedup_u24(edges, sort_scratch);
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
    stats
}

fn finish_bigram_mesh_summary(
    edges: &mut Vec<u32>,
    out: &mut Vec<u8>,
    stats: &mut MeshSummaryBuildStats,
) {
    edges.sort_unstable();
    edges.dedup();
    stats.unique_edges = edges.len() as u64;
    encode_bigram_mesh_edges_into(edges, out);
}

fn collect_bigram_mesh_edges(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    lower: &mut Vec<u8>,
) -> MeshSummaryBuildStats {
    edges.clear();
    edges.reserve(bytes.len().saturating_sub(2));
    let mut stats = MeshSummaryBuildStats {
        raw_edge_windows: raw_edge_windows(bytes),
        ..MeshSummaryBuildStats::default()
    };
    collect_bigram_edges_counted(bytes, edges, &mut stats);

    if has_ascii_uppercase(bytes) {
        lower.clear();
        lower.extend_from_slice(bytes);
        lower.make_ascii_lowercase();
        edges.reserve(lower.len().saturating_sub(2));
        collect_bigram_edges_counted(lower, edges, &mut stats);
    }
    stats
}

fn raw_edge_windows(bytes: &[u8]) -> u64 {
    bytes.len().saturating_sub(2) as u64
}

fn ascii_lower_byte(byte: u8) -> u8 {
    if byte.is_ascii_uppercase() {
        byte + 32
    } else {
        byte
    }
}

fn collect_bigram_edges_counted(
    bytes: &[u8],
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    if bytes.len() < 3 {
        return;
    }

    for index in 0..bytes.len() - 2 {
        edges.push(pack_bigram_edge_bytes(
            bytes[index],
            bytes[index + 1],
            bytes[index + 2],
        ));
        stats.pushed_edges += 1;
    }
}

fn push_edge_if_unseen(
    edge: u32,
    bitset: &mut [u64],
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    let word = (edge >> 6) as usize;
    let mask = 1u64 << (edge & 63);
    if bitset[word] & mask == 0 {
        bitset[word] |= mask;
        edges.push(edge);
        stats.pushed_edges += 1;
    }
}

fn clear_edge_bit(edge: u32, bitset: &mut [u64]) {
    let word = (edge >> 6) as usize;
    let mask = 1u64 << (edge & 63);
    bitset[word] &= !mask;
}

fn ensure_full_u24_bitset(bitset: &mut Vec<u64>) -> bool {
    if bitset.len() < U24_EDGE_SPACE_WORDS {
        bitset.resize(U24_EDGE_SPACE_WORDS, 0);
        true
    } else {
        false
    }
}

fn clear_full_bitset_edges(edges: &[u32], bitset: &mut [u64], stats: &mut MeshSummaryBuildStats) {
    for edge in edges.iter().copied() {
        clear_edge_bit(edge, bitset);
        stats.bitset_cleared_edges += 1;
    }
}

fn push_edge_if_unseen_first_bitset(
    edge: u32,
    first_bitsets: &mut [Vec<u64>],
    touched_first: &mut [bool; 256],
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    let first = ((edge >> 16) & 0xff) as usize;
    if first_bitsets[first].is_empty() {
        first_bitsets[first].resize(FIRST_BYTE_SUFFIX_WORDS, 0);
        stats.bitset_resizes += 1;
    }

    let suffix = (edge & 0xffff) as usize;
    let word = suffix >> 6;
    let mask = 1u64 << (suffix & 63);
    if first_bitsets[first][word] & mask == 0 {
        first_bitsets[first][word] |= mask;
        touched_first[first] = true;
        edges.push(edge);
        stats.pushed_edges += 1;
    }
}

fn clear_first_bitset_edge(edge: u32, first_bitsets: &mut [Vec<u64>]) {
    let first = ((edge >> 16) & 0xff) as usize;
    if first_bitsets[first].is_empty() {
        return;
    }
    let suffix = (edge & 0xffff) as usize;
    let word = suffix >> 6;
    let mask = 1u64 << (suffix & 63);
    first_bitsets[first][word] &= !mask;
}

fn push_edge_if_unseen_trie_pair(
    edge: u32,
    pair_index: &mut [[u16; 256]],
    pair_bitsets: &mut [Vec<[u64; 4]>],
    touched_pairs: &mut Vec<(u8, u8)>,
    touched_first: &mut [bool; 256],
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    let first = ((edge >> 16) & 0xff) as usize;
    let second = ((edge >> 8) & 0xff) as usize;
    let third = (edge & 0xff) as usize;

    let mut pair_pos = pair_index[first][second];
    if pair_pos == u16::MAX {
        let new_pos = pair_bitsets[first].len();
        debug_assert!(new_pos <= u16::MAX as usize);
        pair_bitsets[first].push([0; 4]);
        pair_pos = new_pos as u16;
        pair_index[first][second] = pair_pos;
        touched_pairs.push((first as u8, second as u8));
        touched_first[first] = true;
        stats.bitset_resizes += 1;
    }

    let bits = &mut pair_bitsets[first][pair_pos as usize];
    let word = third >> 6;
    let mask = 1u64 << (third & 63);
    if bits[word] & mask == 0 {
        bits[word] |= mask;
        edges.push(edge);
        stats.pushed_edges += 1;
    }
}

fn clear_trie_pair_edge(
    edge: u32,
    pair_index: &[[u16; 256]],
    pair_bitsets: &mut [Vec<[u64; 4]>],
) {
    let first = ((edge >> 16) & 0xff) as usize;
    let second = ((edge >> 8) & 0xff) as usize;
    let third = (edge & 0xff) as usize;
    let pair_pos = pair_index[first][second];
    if pair_pos == u16::MAX {
        return;
    }
    let bits = &mut pair_bitsets[first][pair_pos as usize];
    let word = third >> 6;
    let mask = 1u64 << (third & 63);
    bits[word] &= !mask;
}

fn trie_pair_bitset_scratch_bytes(
    pair_index: &[[u16; 256]],
    pair_bitsets: &[Vec<[u64; 4]>],
) -> u64 {
    let index_bytes = pair_index.len() as u64 * 256 * 2;
    let bitset_bytes: u64 = pair_bitsets
        .iter()
        .map(|bucket| bucket.capacity() as u64 * 32)
        .sum();
    index_bytes + bitset_bytes
}

fn first_bitset_scratch_bytes(first_bitsets: &[Vec<u64>]) -> u64 {
    first_bitsets
        .iter()
        .map(|bucket| bucket.len() as u64 * 8)
        .sum()
}

fn push_edge_to_grouped_bucket(
    edge: u32,
    buckets: &mut [Vec<u32>],
    stats: &mut MeshSummaryBuildStats,
) {
    let group = grouped_first_byte_bucket(((edge >> 16) & 0xff) as u8);
    buckets[group].push(edge);
    stats.pushed_edges += 1;
}

fn grouped_first_byte_bucket(first: u8) -> usize {
    match first {
        0..=47 => 0,
        b'0'..=b'9' => 1,
        58..=64 => 2,
        b'A'..=b'Z' => 3,
        91..=96 => 4,
        b'a'..=b'z' => 5 + (first - b'a') as usize,
        _ => 31,
    }
}

fn grouped_bucket_scratch_bytes(buckets: &[Vec<u32>]) -> u64 {
    buckets
        .iter()
        .map(|bucket| bucket.capacity() as u64 * 4)
        .sum()
}

fn bucket_sort_dedup_u24(values: &mut Vec<u32>, scratch: &mut Vec<u32>) {
    if values.len() < 2 {
        return;
    }

    let mut counts = [0usize; 256];
    for value in values.iter().copied() {
        counts[((value >> 16) & 0xff) as usize] += 1;
    }

    let mut starts = [0usize; 256];
    let mut total = 0usize;
    for (index, count) in counts.iter().copied().enumerate() {
        starts[index] = total;
        total += count;
    }

    scratch.clear();
    scratch.resize(values.len(), 0);
    let mut positions = starts;
    for value in values.iter().copied() {
        let bucket = ((value >> 16) & 0xff) as usize;
        let position = positions[bucket];
        scratch[position] = value;
        positions[bucket] += 1;
    }

    values.clear();
    for bucket in 0..256 {
        let start = starts[bucket];
        let end = start + counts[bucket];
        if start == end {
            continue;
        }
        scratch[start..end].sort_unstable();
        let mut last: Option<u32> = None;
        for value in scratch[start..end].iter().copied() {
            if last != Some(value) {
                values.push(value);
                last = Some(value);
            }
        }
    }
}

fn collect_bigram_edges(bytes: &[u8], edges: &mut Vec<u32>) {
    if bytes.len() < 3 {
        return;
    }

    for index in 0..bytes.len() - 2 {
        edges.push(pack_bigram_edge_bytes(
            bytes[index],
            bytes[index + 1],
            bytes[index + 2],
        ));
    }
}

fn collect_bigram_edges_unique(
    bytes: &[u8],
    seen: &mut std::collections::HashSet<u32>,
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    if bytes.len() < 3 {
        return;
    }

    for index in 0..bytes.len() - 2 {
        let edge = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
        if seen.insert(edge) {
            edges.push(edge);
            stats.pushed_edges += 1;
        }
    }
}

#[derive(Default)]
struct EdgeIdentityHasher {
    value: u64,
}

impl Hasher for EdgeIdentityHasher {
    fn finish(&self) -> u64 {
        self.value
    }

    fn write(&mut self, bytes: &[u8]) {
        let mut value = 0u64;
        for (index, byte) in bytes.iter().take(8).enumerate() {
            value |= (*byte as u64) << (index * 8);
        }
        self.value = value;
    }

    fn write_u8(&mut self, value: u8) {
        self.value = value as u64;
    }

    fn write_u16(&mut self, value: u16) {
        self.value = value as u64;
    }

    fn write_u32(&mut self, value: u32) {
        self.value = value as u64;
    }

    fn write_u64(&mut self, value: u64) {
        self.value = value;
    }

    fn write_usize(&mut self, value: usize) {
        self.value = value as u64;
    }
}

fn collect_bigram_edges_unique_identity(
    bytes: &[u8],
    seen: &mut std::collections::HashSet<u32, BuildHasherDefault<EdgeIdentityHasher>>,
    edges: &mut Vec<u32>,
    stats: &mut MeshSummaryBuildStats,
) {
    if bytes.len() < 3 {
        return;
    }

    for index in 0..bytes.len() - 2 {
        let edge = pack_bigram_edge_bytes(bytes[index], bytes[index + 1], bytes[index + 2]);
        if seen.insert(edge) {
            edges.push(edge);
            stats.pushed_edges += 1;
        }
    }
}

fn encode_bigram_mesh_edges_into(edges: &[u32], out: &mut Vec<u8>) {
    out.clear();
    out.extend_from_slice(BIGRAM_MESH_MAGIC);
    out.extend_from_slice(&BIGRAM_MESH_VERSION.to_le_bytes());
    out.extend_from_slice(&0u16.to_le_bytes());
    out.extend_from_slice(&(edges.len() as u32).to_le_bytes());

    let mut previous = 0u32;
    for (index, edge) in edges.iter().copied().enumerate() {
        debug_assert!(edge <= 0x00ff_ffff);
        let delta = if index == 0 { edge } else { edge - previous };
        write_varint_u32(delta, out);
        previous = edge;
    }
}

fn radix_sort_u24(values: &mut [u32], scratch: &mut Vec<u32>) {
    if values.len() < 2 {
        return;
    }

    scratch.clear();
    scratch.resize(values.len(), 0);

    radix_sort_u24_pass(values, scratch, 0);
    radix_sort_u24_pass(scratch, values, 8);
    radix_sort_u24_pass(values, scratch, 16);
    values.copy_from_slice(scratch);
}

fn radix_sort_u24_pass(input: &[u32], output: &mut [u32], shift: u32) {
    let mut counts = [0usize; 256];
    for value in input {
        counts[((value >> shift) & 0xff) as usize] += 1;
    }

    let mut total = 0usize;
    for count in &mut counts {
        let current = *count;
        *count = total;
        total += current;
    }

    for value in input {
        let bucket = ((value >> shift) & 0xff) as usize;
        let index = counts[bucket];
        output[index] = *value;
        counts[bucket] += 1;
    }
}

fn pack_bigram_edge(edge: &[u8]) -> u32 {
    debug_assert!(edge.len() == 3);
    pack_bigram_edge_bytes(edge[0], edge[1], edge[2])
}

fn pack_bigram_edge_bytes(first: u8, second: u8, third: u8) -> u32 {
    ((first as u32) << 16) | ((second as u32) << 8) | third as u32
}

fn write_varint_u32(mut value: u32, out: &mut Vec<u8>) {
    while value >= 0x80 {
        out.push((value as u8 & 0x7f) | 0x80);
        value >>= 7;
    }
    out.push(value as u8);
}

fn read_varint_u32(bytes: &[u8], offset: &mut usize) -> Result<u32> {
    let mut value = 0u32;
    let mut shift = 0u32;

    loop {
        if *offset >= bytes.len() {
            return Err(anyhow!("truncated bigram mesh varint"));
        }

        let byte = bytes[*offset];
        *offset += 1;

        value |= ((byte & 0x7f) as u32) << shift;

        if byte & 0x80 == 0 {
            return Ok(value);
        }

        shift += 7;
        if shift >= 35 {
            return Err(anyhow!("bigram mesh varint is too long"));
        }
    }
}

fn collect_window_hashes(bytes: &[u8], hashes: &mut Vec<u64>) {
    for window in [PATH_WINDOW_MIN, PATH_WINDOW_MID, PATH_WINDOW_MAX] {
        if bytes.len() < window {
            continue;
        }

        for part in bytes.windows(window) {
            hashes.push(hash_window(window as u8, part));
        }
    }
}

fn hash_window(window_len: u8, bytes: &[u8]) -> u64 {
    let mut hash = FNV_OFFSET;
    hash ^= window_len as u64;
    hash = hash.wrapping_mul(FNV_PRIME);
    for byte in bytes {
        hash ^= *byte as u64;
        hash = hash.wrapping_mul(FNV_PRIME);
    }
    hash
}

#[derive(Clone, Debug, Default)]
pub struct MatchCounters {
    pub lines_scanned: u64,
    pub fixed_calls: u64,
    pub rust_regex_calls: u64,
    pub pcre2_calls: u64,
    pub fast_path_calls: u64,
    pub prefilter_rejects: u64,
}

#[derive(Clone, Debug)]
struct LookbehindUntilDelimiter {
    prefix: Vec<u8>,
    delimiter: u8,
}

#[derive(Debug)]
pub struct Matcher {
    engine: Engine,
    options: GrepOptions,
    selector_plan: SelectorPlan,
}

#[derive(Clone, Debug)]
enum SelectorPlan {
    None,
    All(Vec<Vec<u8>>),
    Any(Vec<Vec<u8>>),
}

impl SelectorPlan {
    fn may_match(&self, summary: &SearchSummary, ignore_case: bool) -> bool {
        match self {
            SelectorPlan::None => true,
            SelectorPlan::All(literals) => literals
                .iter()
                .all(|literal| summary.may_contain_literal(literal, ignore_case)),
            SelectorPlan::Any(literals) => literals
                .iter()
                .any(|literal| summary.may_contain_literal(literal, ignore_case)),
        }
    }

    fn line_may_match(&self, line: &[u8], ignore_case: bool) -> bool {
        match self {
            SelectorPlan::None => true,
            SelectorPlan::All(literals) => literals
                .iter()
                .all(|literal| fixed_contains(line, literal, ignore_case)),
            SelectorPlan::Any(literals) => literals
                .iter()
                .any(|literal| fixed_contains(line, literal, ignore_case)),
        }
    }

    fn kind(&self) -> &'static str {
        match self {
            SelectorPlan::None => "none",
            SelectorPlan::All(_) => "literal_all",
            SelectorPlan::Any(_) => "literal_any",
        }
    }

    fn byte_len(&self) -> usize {
        match self {
            SelectorPlan::None => 0,
            SelectorPlan::All(literals) | SelectorPlan::Any(literals) => {
                literals.iter().map(Vec::len).sum()
            }
        }
    }

    fn count(&self) -> usize {
        match self {
            SelectorPlan::None => 0,
            SelectorPlan::All(literals) | SelectorPlan::Any(literals) => literals.len(),
        }
    }

    fn from_all(literals: Vec<Vec<u8>>) -> Self {
        let literals = dedup_literals(literals);
        if literals.is_empty() {
            SelectorPlan::None
        } else {
            SelectorPlan::All(literals)
        }
    }

    fn from_any(literals: Vec<Vec<u8>>) -> Self {
        let literals = dedup_literals(literals);
        if literals.is_empty() {
            SelectorPlan::None
        } else {
            SelectorPlan::Any(literals)
        }
    }
}

#[derive(Debug)]
enum Engine {
    Fixed {
        pattern: Vec<u8>,
    },
    Regex {
        regex: regex::bytes::Regex,
    },
    Pcre2 {
        regex: pcre2::bytes::Regex,
        fast_path: Option<LookbehindUntilDelimiter>,
    },
}

impl Matcher {
    pub fn new(pattern: &str, options: GrepOptions) -> Result<Self> {
        let selector_plan = selector_plan(pattern, &options);

        let engine = if options.fixed_strings {
            Engine::Fixed {
                pattern: pattern.as_bytes().to_vec(),
            }
        } else if options.perl_regexp {
            Engine::Pcre2 {
                regex: Pcre2RegexBuilder::new()
                    .caseless(options.ignore_case)
                    .build(pattern)?,
                fast_path: if options.ignore_case {
                    None
                } else {
                    lookbehind_until_delimiter(pattern)
                },
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
            selector_plan,
        })
    }

    pub fn chunk_may_match(&self, summary: &SearchSummary) -> bool {
        self.selector_plan
            .may_match(summary, self.options.ignore_case)
    }

    pub fn selector_kind(&self) -> &'static str {
        self.selector_plan.kind()
    }

    pub fn selector_len(&self) -> usize {
        self.selector_plan.byte_len()
    }

    pub fn selector_count(&self) -> usize {
        self.selector_plan.count()
    }

    pub fn line_matches_profiled(&self, line: &[u8], counters: &mut MatchCounters) -> Result<bool> {
        counters.lines_scanned += 1;

        match &self.engine {
            Engine::Fixed { pattern } => {
                counters.fixed_calls += 1;
                Ok(fixed_contains(line, pattern, self.options.ignore_case))
            }
            Engine::Regex { regex } => {
                if !self
                    .selector_plan
                    .line_may_match(line, self.options.ignore_case)
                {
                    counters.prefilter_rejects += 1;
                    return Ok(false);
                }

                counters.rust_regex_calls += 1;
                Ok(regex.is_match(line))
            }
            Engine::Pcre2 { regex, fast_path } => {
                if !self
                    .selector_plan
                    .line_may_match(line, self.options.ignore_case)
                {
                    counters.prefilter_rejects += 1;
                    return Ok(false);
                }

                if let Some(fast_path) = fast_path {
                    counters.fast_path_calls += 1;
                    return Ok(fast_path.is_match(line));
                }

                counters.pcre2_calls += 1;
                Ok(regex.is_match(line)?)
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
            Engine::Pcre2 { regex, fast_path } => {
                if let Some(fast_path) = fast_path {
                    return Ok(fast_path.find_all(line));
                }

                let mut out = Vec::new();

                for item in regex.find_iter(line) {
                    let item = item?;
                    out.push(item.as_bytes().to_vec());
                }

                Ok(out)
            }
        }
    }
}

impl LookbehindUntilDelimiter {
    fn is_match(&self, line: &[u8]) -> bool {
        self.find_ranges(line).next().is_some()
    }

    fn find_all(&self, line: &[u8]) -> Vec<Vec<u8>> {
        self.find_ranges(line)
            .map(|(start, end)| line[start..end].to_vec())
            .collect()
    }

    fn find_ranges<'a>(&'a self, line: &'a [u8]) -> impl Iterator<Item = (usize, usize)> + 'a {
        let prefix_len = self.prefix.len();
        let delimiter = self.delimiter;
        memmem::find_iter(line, &self.prefix).filter_map(move |start| {
            let value_start = start + prefix_len;
            let rest = &line[value_start..];
            let end_rel = rest.iter().position(|byte| *byte == delimiter)?;
            if end_rel == 0 {
                None
            } else {
                Some((value_start, value_start + end_rel))
            }
        })
    }
}

fn selector_plan(pattern: &str, options: &GrepOptions) -> SelectorPlan {
    if options.fixed_strings {
        return SelectorPlan::from_all(non_empty(pattern.as_bytes()).into_iter().collect());
    }

    if options.perl_regexp {
        if let Some(literal) = selector_from_positive_lookbehind(pattern) {
            return SelectorPlan::from_all(vec![literal]);
        }
    }

    regex_selector_plan(pattern)
}

fn regex_selector_plan(pattern: &str) -> SelectorPlan {
    if let Some(branches) = split_top_level_alternation(pattern) {
        let mut branch_literals = Vec::new();
        for branch in branches {
            if let Some(best) = best_literal_run(branch) {
                branch_literals.push(best);
            } else {
                return SelectorPlan::None;
            }
        }
        return SelectorPlan::from_any(branch_literals);
    }

    if let Some(branch_literals) = noncapturing_alternation_literals(pattern) {
        return SelectorPlan::from_any(branch_literals);
    }

    if has_unescaped_or_any_depth(pattern) || has_unhandled_group(pattern) {
        return SelectorPlan::None;
    }

    SelectorPlan::from_all(literal_runs(pattern))
}

fn split_top_level_alternation(pattern: &str) -> Option<Vec<&str>> {
    let mut escaped = false;
    let mut in_class = false;
    let mut depth = 0i32;
    let mut last = 0usize;
    let mut parts = Vec::new();

    for (idx, byte) in pattern.bytes().enumerate() {
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
            b'|' if !in_class && depth == 0 => {
                parts.push(&pattern[last..idx]);
                last = idx + 1;
            }
            _ => {}
        }
    }

    if parts.is_empty() {
        None
    } else {
        parts.push(&pattern[last..]);
        Some(parts)
    }
}

fn noncapturing_alternation_literals(pattern: &str) -> Option<Vec<Vec<u8>>> {
    let prefix = "(?:";
    if !pattern.starts_with(prefix) {
        return None;
    }

    let mut escaped = false;
    let mut depth = 0i32;
    let mut end = None;

    for (idx, byte) in pattern.bytes().enumerate().skip(prefix.len()) {
        if escaped {
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => escaped = true,
            b'(' => depth += 1,
            b')' if depth == 0 => {
                end = Some(idx);
                break;
            }
            b')' => depth -= 1,
            _ => {}
        }
    }

    let end = end?;
    let body = &pattern[prefix.len()..end];
    if body.is_empty() || body.contains('(') || body.contains('[') {
        return None;
    }

    let mut out = Vec::new();
    for branch in body.split('|') {
        if branch.len() < 2 || !is_plain_literal(branch) {
            return None;
        }
        out.push(branch.as_bytes().to_vec());
    }

    Some(out)
}

fn literal_runs(pattern: &str) -> Vec<Vec<u8>> {
    let mut literals = Vec::new();
    let mut current = Vec::new();
    let mut in_class = false;
    let mut escaped = false;

    for byte in pattern.bytes() {
        if escaped {
            if is_literal_escape(byte) {
                current.push(unescape_literal(byte));
            } else {
                flush_literal(&mut literals, &mut current);
            }
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => escaped = true,
            b'[' => {
                flush_literal(&mut literals, &mut current);
                in_class = true;
            }
            b']' => {
                in_class = false;
            }
            b'(' | b')' | b'{' | b'}' | b'*' | b'+' | b'?' | b'^' | b'$' | b'.' | b'|'
                if !in_class =>
            {
                flush_literal(&mut literals, &mut current);
            }
            _ if !in_class => {
                current.push(byte);
            }
            _ => {}
        }
    }

    flush_literal(&mut literals, &mut current);
    literals
}

fn best_literal_run(pattern: &str) -> Option<Vec<u8>> {
    literal_runs(pattern).into_iter().max_by_key(Vec::len)
}

fn selector_from_positive_lookbehind(pattern: &str) -> Option<Vec<u8>> {
    let prefix = "(?<=";
    let start = pattern.find(prefix)?;
    let after = start + prefix.len();
    let rest = &pattern[after..];
    let end = rest.find(')')?;
    let candidate = &rest[..end];

    let literal = unescape_fixed_literal(candidate)?;
    if literal.len() >= 2 {
        Some(literal)
    } else {
        None
    }
}

fn lookbehind_until_delimiter(pattern: &str) -> Option<LookbehindUntilDelimiter> {
    let prefix = "(?<=";
    if !pattern.starts_with(prefix) {
        return None;
    }

    let after = prefix.len();
    let rest = &pattern[after..];
    let end = rest.find(')')?;
    let lookbehind = unescape_fixed_literal(&rest[..end])?;
    let suffix = &rest[end + 1..];

    let delimiter = parse_negated_byte_class_plus(suffix)?;
    Some(LookbehindUntilDelimiter {
        prefix: lookbehind,
        delimiter,
    })
}

fn parse_negated_byte_class_plus(value: &str) -> Option<u8> {
    let bytes = value.as_bytes();
    if bytes.len() < 5 || bytes[0] != b'[' || bytes[1] != b'^' {
        return None;
    }

    let mut idx = 2usize;
    let delimiter = if bytes[idx] == b'\\' {
        idx += 1;
        let escaped = *bytes.get(idx)?;
        if !is_literal_escape(escaped) {
            return None;
        }
        unescape_literal(escaped)
    } else {
        let byte = bytes[idx];
        if matches!(byte, b'[' | b']' | b'^' | b'-') {
            return None;
        }
        byte
    };

    idx += 1;
    if bytes.get(idx) != Some(&b']') || bytes.get(idx + 1) != Some(&b'+') || idx + 2 != bytes.len()
    {
        return None;
    }

    Some(delimiter)
}

fn unescape_fixed_literal(value: &str) -> Option<Vec<u8>> {
    let mut out = Vec::new();
    let mut escaped = false;

    for byte in value.bytes() {
        if escaped {
            if is_literal_escape(byte) {
                out.push(unescape_literal(byte));
                escaped = false;
                continue;
            }
            return None;
        }

        if byte == b'\\' {
            escaped = true;
            continue;
        }

        if matches!(
            byte,
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
        ) {
            return None;
        }

        out.push(byte);
    }

    if escaped {
        return None;
    }

    Some(out)
}

fn has_unescaped_or_any_depth(pattern: &str) -> bool {
    let mut escaped = false;
    let mut in_class = false;

    for byte in pattern.bytes() {
        if escaped {
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => escaped = true,
            b'[' if !in_class => in_class = true,
            b']' if in_class => in_class = false,
            b'|' if !in_class => return true,
            _ => {}
        }
    }

    false
}

fn has_unhandled_group(pattern: &str) -> bool {
    let mut escaped = false;
    let mut in_class = false;

    for byte in pattern.bytes() {
        if escaped {
            escaped = false;
            continue;
        }

        match byte {
            b'\\' => escaped = true,
            b'[' if !in_class => in_class = true,
            b']' if in_class => in_class = false,
            b'(' | b')' if !in_class => return true,
            _ => {}
        }
    }

    false
}

fn is_plain_literal(value: &str) -> bool {
    value.bytes().all(|byte| {
        !matches!(
            byte,
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
                | b'\\'
        )
    })
}

fn non_empty(bytes: &[u8]) -> Option<Vec<u8>> {
    if bytes.is_empty() {
        None
    } else {
        Some(bytes.to_vec())
    }
}

fn flush_literal(literals: &mut Vec<Vec<u8>>, current: &mut Vec<u8>) {
    if current.len() >= 2 {
        literals.push(current.clone());
    }
    current.clear();
}

fn dedup_literals(mut literals: Vec<Vec<u8>>) -> Vec<Vec<u8>> {
    literals.retain(|literal| !literal.is_empty());
    literals.sort();
    literals.dedup();
    literals
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
        ascii_case_insensitive_contains(line, pattern)
    } else {
        memmem::find(line, pattern).is_some()
    }
}

fn ascii_case_insensitive_contains(line: &[u8], pattern: &[u8]) -> bool {
    if pattern.is_empty() {
        return true;
    }

    if pattern.len() > line.len() {
        return false;
    }

    line.windows(pattern.len()).any(|window| {
        window
            .iter()
            .zip(pattern)
            .all(|(left, right)| left.eq_ignore_ascii_case(right))
    })
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
    fn path_window_summary_filters_long_literals() {
        let summary = SearchSummary::from_path_windows(b"alpha src_ip=198.18.99.123 omega\n");
        assert!(summary.may_contain_literal(b"198.18.99.123", false));
        assert!(!summary.may_contain_literal(b"198.18.99.124", false));
    }

    #[test]
    fn positive_lookbehind_unescapes_literal_selector() {
        let literal = selector_from_positive_lookbehind(r#"(?<=key=\")[^\"]+"#).unwrap();
        assert_eq!(literal, br#"key=""#.to_vec());
    }

    #[test]
    fn regex_plan_extracts_required_literal() {
        let plan = regex_selector_plan(r#"key="[^"]+""#);
        assert_eq!(plan.kind(), "literal_all");
        assert_eq!(plan.count(), 1);
    }

    #[test]
    fn regex_plan_extracts_top_level_alternation() {
        let plan = regex_selector_plan("error|failed|denied");
        assert_eq!(plan.kind(), "literal_any");
        assert_eq!(plan.count(), 3);
    }

    #[test]
    fn regex_plan_extracts_noncapturing_alternation_prefix() {
        let plan = regex_selector_plan(r"(?:foo|bar)[0-9]");
        assert_eq!(plan.kind(), "literal_any");
        assert_eq!(plan.count(), 2);
    }

    #[test]
    fn inline_sparse_and_grouped_profiles_match_combined_summary() {
        let data = b"Alpha ERROR beta src_ip=192.168.102.55 username=Admin\n";
        let mut edges = Vec::new();
        let mut lower = Vec::new();
        let mut out_combined = Vec::new();
        encode_bigram_mesh_summary_into(data, &mut edges, &mut lower, &mut out_combined);

        let mut bitsets = Vec::new();
        let mut out_sparse = Vec::new();
        encode_bigram_mesh_summary_sparse_first_bitset_into(
            data,
            &mut bitsets,
            &mut edges,
            &mut out_sparse,
        );
        assert_eq!(out_sparse, out_combined);

        let mut buckets = Vec::new();
        let mut out_grouped = Vec::new();
        encode_bigram_mesh_summary_grouped_buckets_into(
            data,
            &mut buckets,
            &mut edges,
            &mut out_grouped,
        );
        assert_eq!(out_grouped, out_combined);

        let mut pair_index = Vec::new();
        let mut pair_bitsets = Vec::new();
        let mut touched_pairs = Vec::new();
        let mut out_trie = Vec::new();
        encode_bigram_mesh_summary_trie_pair_bitset_into(
            data,
            &mut pair_index,
            &mut pair_bitsets,
            &mut touched_pairs,
            &mut edges,
            &mut out_trie,
        );
        assert_eq!(out_trie, out_combined);

        let mut out_identity = Vec::new();
        encode_bigram_mesh_summary_identity_hash_into(
            data,
            &mut edges,
            &mut lower,
            &mut out_identity,
        );
        assert_eq!(out_identity, out_combined);

        let mut out_rdxsort = Vec::new();
        encode_bigram_mesh_summary_rdxsort_into(data, &mut edges, &mut lower, &mut out_rdxsort);
        assert_eq!(out_rdxsort, out_combined);

        let mut out_rdst = Vec::new();
        encode_bigram_mesh_summary_rdst_into(data, &mut edges, &mut lower, &mut out_rdst);
        assert_eq!(out_rdst, out_combined);
    }

    #[test]
    fn lower_only_bitset_matches_lower_only_summary() {
        let data = b"Alpha ERROR beta src_ip=192.168.102.55 username=Admin\n";
        let mut edges = Vec::new();
        let mut out_lower = Vec::new();
        encode_bigram_mesh_summary_lower_only_into(data, &mut edges, &mut out_lower);

        let mut bitset = Vec::new();
        let mut out_bitset = Vec::new();
        encode_bigram_mesh_summary_lower_only_bitset_seen_into(
            data,
            &mut bitset,
            &mut edges,
            &mut out_bitset,
        );
        assert_eq!(out_bitset, out_lower);
    }

    #[test]
    fn mesh_summary_handles_utf8_as_bytes() {
        let data = b"username=\xe3\x81\x9f\xe3\x82\x8d\xe3\x81\x86 user=\xe3\x82\xab\xe3\x83\x8a msg=\"\xe3\x83\xad\xe3\x82\xb0\xe3\x82\xa4\xe3\x83\xb3\xe6\x88\x90\xe5\x8a\x9f\"\n";
        let summary = SearchSummary::from_bigram_mesh(data);
        assert!(
            summary.may_contain_literal(b"username=\xe3\x81\x9f\xe3\x82\x8d\xe3\x81\x86", false)
        );
        assert!(summary.may_contain_literal(
            b"\xe3\x83\xad\xe3\x82\xb0\xe3\x82\xa4\xe3\x83\xb3\xe6\x88\x90\xe5\x8a\x9f",
            false
        ));
        assert!(!summary.may_contain_literal(b"username=\xe3\x81\xaf\xe3\x81\xaa", false));
    }

    #[test]
    fn mesh_summary_handles_binary_bytes() {
        let data = b"\x89PNG\r\n\x1a\n\x00\x00IHDR\x00zlg\x00IDAT\xff\x00END";
        let summary = SearchSummary::from_bigram_mesh(data);
        assert!(summary.may_contain_literal(b"PNG\r\n", false));
        assert!(summary.may_contain_literal(b"IDAT\xff", false));
        assert!(!summary.may_contain_literal(b"GIF89a", false));
    }
}
