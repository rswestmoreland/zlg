use anyhow::Result;
use crc32fast::Hasher;
use std::io::BufRead;

const INITIAL_CHUNK_CAPACITY: usize = 256 * 1024;
const MAX_RETAINED_LINE_CAPACITY: usize = 1024 * 1024;

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
                lines: 2048,
                byte_cap: None,
            } => 15,
            ChunkPolicy::FixedLines {
                lines: 4096,
                byte_cap: None,
            } => 16,
            ChunkPolicy::FixedLines {
                lines: 8192,
                byte_cap: None,
            } => 17,
            ChunkPolicy::FixedLines {
                lines: 16_384,
                byte_cap: None,
            } => 18,
            ChunkPolicy::FixedLines {
                lines: 8192,
                byte_cap: Some(bytes),
            } if bytes == 4 * 1024 * 1024 => 19,
            ChunkPolicy::FixedLines {
                lines: 8192,
                byte_cap: Some(bytes),
            } if bytes == 8 * 1024 * 1024 => 20,
            ChunkPolicy::FixedLines {
                lines: 8192,
                byte_cap: Some(bytes),
            } if bytes == 16 * 1024 * 1024 => 21,
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
    pub crc32: u32,
}

#[derive(Debug)]
pub struct Chunker {
    policy: ChunkPolicy,
    next_index: u64,
    next_line_number: u64,
    pending_line: Vec<u8>,
    line_scratch: Vec<u8>,
}

impl Chunker {
    pub fn new(policy: ChunkPolicy) -> Self {
        Self {
            policy,
            next_index: 0,
            next_line_number: 1,
            pending_line: Vec::new(),
            line_scratch: Vec::new(),
        }
    }

    pub fn next_chunk<R: BufRead>(&mut self, reader: &mut R) -> Result<Option<PlainChunk>> {
        let line_limit = self.current_line_limit();
        let byte_cap = self.current_byte_cap();

        let mut data = Vec::with_capacity(self.initial_chunk_capacity());
        let mut line_count = 0u64;
        let mut crc32 = Hasher::new();
        let mut oversized_line = false;

        loop {
            if self.pending_line.is_empty() {
                self.line_scratch.clear();
                let bytes_read = reader.read_until(b'\n', &mut self.line_scratch)?;
                if bytes_read == 0 {
                    break;
                }
            } else {
                self.line_scratch.clear();
                std::mem::swap(&mut self.line_scratch, &mut self.pending_line);
            }

            let line_len = self.line_scratch.len();
            if data.is_empty() && byte_cap.is_some_and(|cap| line_len > cap) {
                oversized_line = true;
                data.extend_from_slice(&self.line_scratch);
                crc32.update(&self.line_scratch);
                line_count += 1;
                break;
            }

            if !data.is_empty() && byte_cap.is_some_and(|cap| data.len() + line_len > cap) {
                std::mem::swap(&mut self.pending_line, &mut self.line_scratch);
                break;
            }

            data.extend_from_slice(&self.line_scratch);
            crc32.update(&self.line_scratch);
            line_count += 1;

            if line_count >= line_limit {
                break;
            }
        }

        if data.is_empty() {
            self.trim_line_scratch_if_empty();
            return Ok(None);
        }

        self.trim_line_scratch_if_empty();

        let chunk = PlainChunk {
            index: self.next_index,
            first_line_number: self.next_line_number,
            line_count,
            data,
            flags: if oversized_line { 0x0002 } else { 0x0001 },
            crc32: crc32.finalize(),
        };

        self.next_index += 1;
        self.next_line_number += line_count;

        Ok(Some(chunk))
    }

    fn initial_chunk_capacity(&self) -> usize {
        self.current_byte_cap()
            .map(|cap| cap.min(INITIAL_CHUNK_CAPACITY))
            .unwrap_or(INITIAL_CHUNK_CAPACITY)
    }

    fn trim_line_scratch_if_empty(&mut self) {
        if self.line_scratch.is_empty() && self.line_scratch.capacity() > MAX_RETAINED_LINE_CAPACITY {
            self.line_scratch.shrink_to(MAX_RETAINED_LINE_CAPACITY);
        }
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
    #[test]
    fn fixed_lines_cap8m_defers_overflow_line_without_dropping() {
        let mut chunker = Chunker::new(ChunkPolicy::FixedLines {
            lines: 8_192,
            byte_cap: Some(8 * 1024 * 1024),
        });
        let first = vec![b'a'; 5 * 1024 * 1024];
        let second = vec![b'b'; 5 * 1024 * 1024];
        let mut input = Vec::new();
        input.extend_from_slice(&first);
        input.push(b'\n');
        input.extend_from_slice(&second);
        input.push(b'\n');
        let mut reader = std::io::Cursor::new(input.clone());

        let chunk0 = chunker.next_chunk(&mut reader).unwrap().unwrap();
        let chunk1 = chunker.next_chunk(&mut reader).unwrap().unwrap();
        assert!(chunker.next_chunk(&mut reader).unwrap().is_none());

        let mut output = Vec::new();
        output.extend_from_slice(&chunk0.data);
        output.extend_from_slice(&chunk1.data);
        assert_eq!(output, input);
    }

    #[test]
    fn chunk_crc_matches_chunk_bytes() {
        let mut chunker = Chunker::new(ChunkPolicy::FixedLines {
            lines: 2,
            byte_cap: None,
        });
        let mut reader = std::io::Cursor::new(b"alpha\nbeta\n".to_vec());
        let chunk = chunker.next_chunk(&mut reader).unwrap().unwrap();
        assert_eq!(chunk.crc32, crc32fast::hash(&chunk.data));
    }
}
