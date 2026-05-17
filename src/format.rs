use crate::chunk::PlainChunk;
use crate::search::{
    encode_bigram_mesh_summary_bitset_seen_into, MeshSummaryBuildStats, SearchSummary,
    SearchSummaryMode,
};
use anyhow::{anyhow, Context, Result};
use crc32fast::{hash as crc32, Hasher};
use memchr::memchr_iter;
use std::io::{Cursor, ErrorKind, Read, Seek, SeekFrom, Write};
use std::time::Instant;

const GLOBAL_MAGIC: &[u8; 8] = b"ZLG1P0\0\0";
const CHUNK_MAGIC: &[u8; 4] = b"ZCH1";
const DIR_MAGIC: &[u8; 4] = b"ZDR1";
const FOOTER_MAGIC: &[u8; 4] = b"ZFT1";
const GLOBAL_HEADER_LEN: u16 = 32;
const CHUNK_HEADER_LEN: u16 = 64;
const DIRECTORY_ENTRY_LEN: u32 = 64;
const FORMAT_VERSION: u16 = 1;
const CHUNK_FLAG_STORED: u16 = 0x8000;
// Reader allocation guards for malformed archives. These are safety caps, not
// format guarantees; normal final-stack chunks are far below these limits.
const MAX_SUMMARY_LEN: u64 = 64 * 1024 * 1024;
const MAX_COMPRESSED_CHUNK_LEN: u64 = 1024 * 1024 * 1024;

const FOOTER_LEN: u64 = 48;
const DIRECTORY_HEADER_LEN: u64 = 16;

pub fn zlg_format_version() -> u16 {
    FORMAT_VERSION
}

pub fn default_compression_mode_name() -> &'static str {
    CompressionMode::Standard.as_str()
}

pub fn default_chunk_policy_name() -> &'static str {
    "fixed-lines8192-cap8m"
}

pub fn default_summary_type_name() -> &'static str {
    "mesh-bigram ZBM1 v2"
}

pub fn default_build_profile_name() -> &'static str {
    "combined-bitset-seen"
}

pub fn chunk_policy_name_from_id(id: u32) -> &'static str {
    match id {
        20 => "fixed-lines8192-cap8m",
        _ => "unknown",
    }
}

pub fn compression_mode_name_from_id(id: u32) -> &'static str {
    match id {
        0 => "none",
        3 => "fast",
        6 => "standard",
        8 => "best",
        _ => "unknown",
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum CompressionMode {
    None,
    Fast,
    Standard,
    Best,
}

impl CompressionMode {
    pub fn level(self) -> Option<i32> {
        match self {
            Self::None => None,
            Self::Fast => Some(3),
            Self::Standard => Some(6),
            Self::Best => Some(8),
        }
    }

    pub fn id(self) -> u32 {
        match self {
            Self::None => 0,
            Self::Fast => 3,
            Self::Standard => 6,
            Self::Best => 8,
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Fast => "fast",
            Self::Standard => "standard",
            Self::Best => "best",
        }
    }
}

#[derive(Clone, Debug)]
pub struct ChunkHeader {
    pub flags: u16,
    pub chunk_index: u64,
    pub first_line_number: u64,
    pub line_count: u64,
    pub uncompressed_len: u64,
    pub compressed_len: u64,
    pub summary_len: u32,
    pub crc32: u32,
}

#[derive(Clone, Debug)]
pub struct DirectoryEntry {
    pub chunk_offset: u64,
    pub summary_offset: u64,
    pub summary_len: u32,
    pub compressed_offset: u64,
    pub compressed_len: u64,
    pub uncompressed_len: u64,
    pub first_line_number: u64,
    pub line_count: u64,
    pub flags: u32,
}

#[derive(Clone, Debug)]
pub struct ArchiveMetadata {
    pub format_version: u16,
    pub flags: u32,
    pub chunk_policy_id: u32,
    pub compression_mode_id: u32,
    pub chunk_count: u64,
    pub total_lines: u64,
    pub total_uncompressed_bytes: u64,
    pub directory_offset: u64,
    pub directory_len: u64,
    pub file_len: u64,
    pub entries: Vec<DirectoryEntry>,
}

impl ArchiveMetadata {
    pub fn total_payload_bytes(&self) -> u64 {
        self.entries.iter().map(|entry| entry.compressed_len).sum()
    }

    pub fn total_summary_bytes(&self) -> u64 {
        self.entries
            .iter()
            .map(|entry| entry.summary_len as u64)
            .sum()
    }
}

#[derive(Debug)]
pub struct RawChunk {
    pub header: ChunkHeader,
    compressed: Vec<u8>,
}

#[derive(Debug)]
pub struct RawChunkHead {
    pub header: ChunkHeader,
    pub summary: SearchSummary,
}

#[derive(Debug)]
pub struct DecodedChunk {
    pub header: ChunkHeader,
    pub data: Vec<u8>,
}

#[derive(Debug, Clone, Copy)]
pub struct StreamDecodeOutcome {
    pub decoded_bytes: u64,
    pub crc_checked: bool,
    pub stopped_early: bool,
}

impl RawChunk {
    fn is_stored(&self) -> bool {
        self.header.flags & CHUNK_FLAG_STORED != 0
    }

    pub fn decode(self) -> Result<DecodedChunk> {
        let data = if self.is_stored() {
            self.compressed
        } else {
            zstd::stream::decode_all(Cursor::new(&self.compressed))
                .context("failed to decode zstd chunk")?
        };

        if data.len() as u64 != self.header.uncompressed_len {
            return Err(anyhow!(
                "chunk {} decoded length mismatch: expected {}, got {}",
                self.header.chunk_index,
                self.header.uncompressed_len,
                data.len()
            ));
        }

        let crc = crc32(&data);
        if crc != self.header.crc32 {
            return Err(anyhow!(
                "chunk {} crc mismatch: expected {:#010x}, got {:#010x}",
                self.header.chunk_index,
                self.header.crc32,
                crc
            ));
        }

        Ok(DecodedChunk {
            header: self.header,
            data,
        })
    }

    pub fn decode_streaming_lines<F>(self, mut on_line: F) -> Result<StreamDecodeOutcome>
    where
        F: FnMut(u64, &[u8]) -> Result<bool>,
    {
        if self.is_stored() {
            let header = self.header;
            return stream_plain_lines(header, &self.compressed, on_line);
        }
        let header = self.header;
        let mut decoder = zstd::stream::Decoder::new(Cursor::new(self.compressed))
            .context("failed to create zstd streaming decoder")?;
        let mut buffer = [0u8; 64 * 1024];
        let mut line = Vec::new();
        let mut line_number = header.first_line_number;
        let mut decoded_bytes = 0u64;
        let mut hasher = Hasher::new();

        loop {
            let read = decoder
                .read(&mut buffer)
                .context("failed to stream decode zstd chunk")?;
            if read == 0 {
                break;
            }

            decoded_bytes += read as u64;
            hasher.update(&buffer[..read]);

            let chunk = &buffer[..read];
            let mut start = 0usize;
            for newline in memchr_iter(b'\n', chunk) {
                let end = newline + 1;
                if line.is_empty() {
                    if !on_line(line_number, &chunk[start..end])? {
                        return Ok(StreamDecodeOutcome {
                            decoded_bytes,
                            crc_checked: false,
                            stopped_early: true,
                        });
                    }
                } else {
                    line.extend_from_slice(&chunk[start..end]);
                    if !on_line(line_number, &line)? {
                        return Ok(StreamDecodeOutcome {
                            decoded_bytes,
                            crc_checked: false,
                            stopped_early: true,
                        });
                    }
                    line.clear();
                }
                line_number += 1;
                start = end;
            }

            if start < read {
                line.extend_from_slice(&chunk[start..]);
            }
        }

        if !line.is_empty() && !on_line(line_number, &line)? {
            return Ok(StreamDecodeOutcome {
                decoded_bytes,
                crc_checked: false,
                stopped_early: true,
            });
        }

        if decoded_bytes != header.uncompressed_len {
            return Err(anyhow!(
                "chunk {} decoded length mismatch: expected {}, got {}",
                header.chunk_index,
                header.uncompressed_len,
                decoded_bytes
            ));
        }

        let crc = hasher.finalize();
        if crc != header.crc32 {
            return Err(anyhow!(
                "chunk {} crc mismatch: expected {:#010x}, got {:#010x}",
                header.chunk_index,
                header.crc32,
                crc
            ));
        }

        Ok(StreamDecodeOutcome {
            decoded_bytes,
            crc_checked: true,
            stopped_early: false,
        })
    }
}

fn stream_plain_lines<F>(
    header: ChunkHeader,
    data: &[u8],
    mut on_line: F,
) -> Result<StreamDecodeOutcome>
where
    F: FnMut(u64, &[u8]) -> Result<bool>,
{
    let mut line_number = header.first_line_number;
    for line in data.split_inclusive(|byte| *byte == b'\n') {
        if !on_line(line_number, line)? {
            return Ok(StreamDecodeOutcome {
                decoded_bytes: data.len() as u64,
                crc_checked: false,
                stopped_early: true,
            });
        }
        line_number += 1;
    }

    if data.len() as u64 != header.uncompressed_len {
        return Err(anyhow!(
            "chunk {} decoded length mismatch: expected {}, got {}",
            header.chunk_index,
            header.uncompressed_len,
            data.len()
        ));
    }

    let crc = crc32(data);
    if crc != header.crc32 {
        return Err(anyhow!(
            "chunk {} crc mismatch: expected {:#010x}, got {:#010x}",
            header.chunk_index,
            header.crc32,
            crc
        ));
    }

    Ok(StreamDecodeOutcome {
        decoded_bytes: data.len() as u64,
        crc_checked: true,
        stopped_early: false,
    })
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BuildProfile {
    CombinedBitsetSeen,
}

impl BuildProfile {
    fn uses_mesh_scratch(self) -> bool {
        matches!(self, Self::CombinedBitsetSeen)
    }

    fn uses_zstd_bulk(self) -> bool {
        matches!(self, Self::CombinedBitsetSeen)
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::CombinedBitsetSeen => "combined-bitset-seen",
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct BuildStats {
    pub chunks: u64,
    pub summary_ns: u128,
    pub zstd_ns: u128,
    pub write_ns: u128,
    pub total_ns: u128,
    pub summary_bytes: u64,
    pub compressed_bytes: u64,
    pub uncompressed_bytes: u64,
    pub raw_edge_windows: u64,
    pub pushed_edges: u64,
    pub unique_edges: u64,
    pub bitset_resizes: u64,
    pub bitset_cleared_edges: u64,
    pub touched_first_buckets: u64,
    pub scratch_bytes: u64,
    pub bitset_scratch_bytes: u64,
    pub first_bitset_scratch_bytes: u64,
    pub edge_scratch_capacity_bytes: u64,
    pub sort_scratch_capacity_bytes: u64,
    pub lower_scratch_capacity_bytes: u64,
    pub summary_scratch_capacity_bytes: u64,
    pub group_bucket_scratch_bytes: u64,
    pub max_chunk_uncompressed_bytes: u64,
    pub max_chunk_compressed_bytes: u64,
    pub max_chunk_summary_bytes: u64,
    pub candidate_edge_events: u64,
    pub edge_capacity_before: u64,
    pub edge_capacity_after: u64,
}

impl BuildStats {
    pub fn to_json(self, profile: BuildProfile) -> String {
        format!(
            "{{\n  \"build_profile\": \"{}\",\n  \"chunks\": {},\n  \"summary_ns\": {},\n  \"zstd_ns\": {},\n  \"write_ns\": {},\n  \"total_ns\": {},\n  \"summary_bytes\": {},\n  \"compressed_bytes\": {},\n  \"uncompressed_bytes\": {},\n  \"raw_edge_windows\": {},\n  \"candidate_edge_events\": {},\n  \"pushed_edges\": {},\n  \"unique_edges\": {},\n  \"bitset_resizes\": {},\n  \"bitset_cleared_edges\": {},\n  \"touched_first_buckets\": {},\n  \"scratch_bytes\": {},\n  \"bitset_scratch_bytes\": {},\n  \"first_bitset_scratch_bytes\": {},\n  \"edge_scratch_capacity_bytes\": {},\n  \"edge_capacity_before\": {},\n  \"edge_capacity_after\": {},\n  \"sort_scratch_capacity_bytes\": {},\n  \"lower_scratch_capacity_bytes\": {},\n  \"summary_scratch_capacity_bytes\": {},\n  \"group_bucket_scratch_bytes\": {},\n  \"max_chunk_uncompressed_bytes\": {},\n  \"max_chunk_compressed_bytes\": {},\n  \"max_chunk_summary_bytes\": {}\n}}\n",
            profile.as_str(),
            self.chunks,
            self.summary_ns,
            self.zstd_ns,
            self.write_ns,
            self.total_ns,
            self.summary_bytes,
            self.compressed_bytes,
            self.uncompressed_bytes,
            self.raw_edge_windows,
            self.candidate_edge_events,
            self.pushed_edges,
            self.unique_edges,
            self.bitset_resizes,
            self.bitset_cleared_edges,
            self.touched_first_buckets,
            self.scratch_bytes,
            self.bitset_scratch_bytes,
            self.first_bitset_scratch_bytes,
            self.edge_scratch_capacity_bytes,
            self.edge_capacity_before,
            self.edge_capacity_after,
            self.sort_scratch_capacity_bytes,
            self.lower_scratch_capacity_bytes,
            self.summary_scratch_capacity_bytes,
            self.group_bucket_scratch_bytes,
            self.max_chunk_uncompressed_bytes,
            self.max_chunk_compressed_bytes,
            self.max_chunk_summary_bytes
        )
    }
}

pub struct ZlgWriter<W: Write> {
    writer: CountingWriter<W>,
    compression_mode: CompressionMode,
    summary_mode: SearchSummaryMode,
    build_profile: BuildProfile,
    build_stats: BuildStats,
    directory: Vec<DirectoryEntry>,
    total_uncompressed_len: u64,
    total_lines: u64,
    mesh_edges_scratch: Vec<u32>,
    mesh_bitset_scratch: Vec<u64>,
    mesh_summary_scratch: Vec<u8>,
    zstd_compressor: Option<zstd::bulk::Compressor<'static>>,
}

impl<W: Write> ZlgWriter<W> {
    pub fn new_with_profile(
        writer: W,
        chunk_policy_id: u32,
        compression_mode: CompressionMode,
        summary_mode: SearchSummaryMode,
        build_profile: BuildProfile,
    ) -> Result<Self> {
        let mut writer = CountingWriter::new(writer);

        writer.write_all(GLOBAL_MAGIC)?;
        write_u16(&mut writer, FORMAT_VERSION)?;
        write_u16(&mut writer, GLOBAL_HEADER_LEN)?;
        write_u32(&mut writer, 0)?;
        write_u32(&mut writer, chunk_policy_id)?;
        write_u32(&mut writer, compression_mode.id())?;
        writer.write_all(&[0u8; 8])?;

        let zstd_compressor = if let Some(level) = compression_mode.level() {
            if build_profile.uses_zstd_bulk() {
                Some(
                    zstd::bulk::Compressor::new(level)
                        .context("failed to create reusable zstd bulk compressor")?,
                )
            } else {
                None
            }
        } else {
            None
        };

        Ok(Self {
            writer,
            compression_mode,
            summary_mode,
            build_profile,
            build_stats: BuildStats::default(),
            directory: Vec::new(),
            total_uncompressed_len: 0,
            total_lines: 0,
            mesh_edges_scratch: Vec::new(),
            mesh_bitset_scratch: Vec::new(),
            mesh_summary_scratch: Vec::new(),
            zstd_compressor,
        })
    }

    pub fn build_stats(&self) -> BuildStats {
        self.build_stats
    }

    pub fn write_chunk(&mut self, chunk: &PlainChunk) -> Result<()> {
        let total_start = Instant::now();
        let chunk_offset = self.writer.bytes_written();

        let summary_start = Instant::now();
        let summary_is_scratch = self.summary_mode == SearchSummaryMode::MeshBigram
            && self.build_profile.uses_mesh_scratch();
        let mut mesh_stats = MeshSummaryBuildStats::default();
        let summary_owned = if summary_is_scratch {
            mesh_stats = encode_bigram_mesh_summary_bitset_seen_into(
                &chunk.data,
                &mut self.mesh_bitset_scratch,
                &mut self.mesh_edges_scratch,
                &mut self.mesh_summary_scratch,
            );
            Vec::new()
        } else {
            match self.summary_mode {
                SearchSummaryMode::Bitmap => SearchSummary::from_bytes(&chunk.data).encode(),
                SearchSummaryMode::PathWindow => {
                    SearchSummary::from_path_windows(&chunk.data).encode()
                }
                SearchSummaryMode::MeshBigram => {
                    SearchSummary::from_bigram_mesh(&chunk.data).encode()
                }
                SearchSummaryMode::None => Vec::new(),
            }
        };

        let summary_ns = summary_start.elapsed().as_nanos();
        let summary_len = if summary_is_scratch {
            self.mesh_summary_scratch.len()
        } else {
            summary_owned.len()
        };

        let zstd_start = Instant::now();
        let compressed = if self.compression_mode == CompressionMode::None {
            chunk.data.clone()
        } else if let Some(compressor) = self.zstd_compressor.as_mut() {
            compressor
                .compress(&chunk.data)
                .context("failed to encode zstd chunk with reusable bulk compressor")?
        } else {
            let level = self
                .compression_mode
                .level()
                .ok_or_else(|| anyhow!("missing zstd level for compression mode"))?;
            zstd::stream::encode_all(Cursor::new(&chunk.data), level)
                .context("failed to encode zstd chunk")?
        };
        let zstd_ns = zstd_start.elapsed().as_nanos();

        let header = ChunkHeader {
            flags: if self.compression_mode == CompressionMode::None {
                chunk.flags | CHUNK_FLAG_STORED
            } else {
                chunk.flags
            },
            chunk_index: chunk.index,
            first_line_number: chunk.first_line_number,
            line_count: chunk.line_count,
            uncompressed_len: chunk.data.len() as u64,
            compressed_len: compressed.len() as u64,
            summary_len: summary_len as u32,
            crc32: chunk.crc32,
        };

        let write_start = Instant::now();
        self.write_chunk_header(&header)?;
        let summary_offset = self.writer.bytes_written();
        if summary_is_scratch {
            self.writer.write_all(&self.mesh_summary_scratch)?;
        } else {
            self.writer.write_all(&summary_owned)?;
        }
        let compressed_offset = self.writer.bytes_written();
        self.writer.write_all(&compressed)?;
        let write_ns = write_start.elapsed().as_nanos();

        self.directory.push(DirectoryEntry {
            chunk_offset,
            summary_offset,
            summary_len: header.summary_len,
            compressed_offset,
            compressed_len: header.compressed_len,
            uncompressed_len: header.uncompressed_len,
            first_line_number: header.first_line_number,
            line_count: header.line_count,
            flags: header.flags as u32,
        });

        self.total_uncompressed_len += header.uncompressed_len;
        self.total_lines += header.line_count;

        self.build_stats.chunks += 1;
        self.build_stats.summary_ns += summary_ns;
        self.build_stats.zstd_ns += zstd_ns;
        self.build_stats.write_ns += write_ns;
        self.build_stats.total_ns += total_start.elapsed().as_nanos();
        self.build_stats.summary_bytes += header.summary_len as u64;
        self.build_stats.compressed_bytes += header.compressed_len;
        self.build_stats.uncompressed_bytes += header.uncompressed_len;
        self.build_stats.max_chunk_uncompressed_bytes = self
            .build_stats
            .max_chunk_uncompressed_bytes
            .max(header.uncompressed_len);
        self.build_stats.max_chunk_compressed_bytes = self
            .build_stats
            .max_chunk_compressed_bytes
            .max(header.compressed_len);
        self.build_stats.max_chunk_summary_bytes = self
            .build_stats
            .max_chunk_summary_bytes
            .max(header.summary_len as u64);
        self.build_stats.raw_edge_windows += mesh_stats.raw_edge_windows;
        self.build_stats.pushed_edges += mesh_stats.pushed_edges;
        self.build_stats.unique_edges += mesh_stats.unique_edges;
        self.build_stats.candidate_edge_events += mesh_stats.candidate_edge_events;
        self.build_stats.edge_capacity_before = self
            .build_stats
            .edge_capacity_before
            .max(mesh_stats.edge_capacity_before);
        self.build_stats.edge_capacity_after = self
            .build_stats
            .edge_capacity_after
            .max(mesh_stats.edge_capacity_after);
        self.build_stats.bitset_resizes += mesh_stats.bitset_resizes;
        self.build_stats.bitset_cleared_edges += mesh_stats.bitset_cleared_edges;
        self.build_stats.touched_first_buckets += mesh_stats.touched_first_buckets;
        self.refresh_scratch_stats(mesh_stats);

        Ok(())
    }

    pub fn finish(mut self) -> Result<W> {
        let directory_offset = self.writer.bytes_written();

        self.writer.write_all(DIR_MAGIC)?;
        write_u32(&mut self.writer, DIRECTORY_ENTRY_LEN)?;
        write_u64(&mut self.writer, self.directory.len() as u64)?;

        for entry in &self.directory {
            write_u64(&mut self.writer, entry.chunk_offset)?;
            write_u64(&mut self.writer, entry.summary_offset)?;
            write_u32(&mut self.writer, entry.summary_len)?;
            write_u32(&mut self.writer, entry.flags)?;
            write_u64(&mut self.writer, entry.compressed_offset)?;
            write_u64(&mut self.writer, entry.compressed_len)?;
            write_u64(&mut self.writer, entry.uncompressed_len)?;
            write_u64(&mut self.writer, entry.first_line_number)?;
            write_u64(&mut self.writer, entry.line_count)?;
        }

        let directory_len = self.writer.bytes_written() - directory_offset;

        self.writer.write_all(FOOTER_MAGIC)?;
        write_u32(&mut self.writer, 48)?;
        write_u64(&mut self.writer, self.directory.len() as u64)?;
        write_u64(&mut self.writer, self.total_lines)?;
        write_u64(&mut self.writer, self.total_uncompressed_len)?;
        write_u64(&mut self.writer, directory_offset)?;
        write_u64(&mut self.writer, directory_len)?;

        self.writer.flush()?;
        Ok(self.writer.into_inner())
    }

    fn refresh_scratch_stats(&mut self, mesh_stats: MeshSummaryBuildStats) {
        let edge_bytes = self.mesh_edges_scratch.capacity() as u64 * 4;
        let bitset_bytes = self.mesh_bitset_scratch.len() as u64 * 8;
        let summary_bytes = self.mesh_summary_scratch.capacity() as u64;
        let total = edge_bytes + bitset_bytes + summary_bytes;

        self.build_stats.scratch_bytes = self.build_stats.scratch_bytes.max(total);
        self.build_stats.bitset_scratch_bytes = self
            .build_stats
            .bitset_scratch_bytes
            .max(bitset_bytes.max(mesh_stats.bitset_scratch_bytes));
        self.build_stats.first_bitset_scratch_bytes = self
            .build_stats
            .first_bitset_scratch_bytes
            .max(mesh_stats.first_bitset_scratch_bytes);
        self.build_stats.edge_scratch_capacity_bytes =
            self.build_stats.edge_scratch_capacity_bytes.max(edge_bytes);
        self.build_stats.sort_scratch_capacity_bytes = 0;
        self.build_stats.lower_scratch_capacity_bytes = 0;
        self.build_stats.summary_scratch_capacity_bytes = self
            .build_stats
            .summary_scratch_capacity_bytes
            .max(summary_bytes);
        self.build_stats.group_bucket_scratch_bytes = self
            .build_stats
            .group_bucket_scratch_bytes
            .max(mesh_stats.group_bucket_scratch_bytes);
    }

    fn write_chunk_header(&mut self, header: &ChunkHeader) -> Result<()> {
        self.writer.write_all(CHUNK_MAGIC)?;
        write_u16(&mut self.writer, CHUNK_HEADER_LEN)?;
        write_u16(&mut self.writer, header.flags)?;
        write_u64(&mut self.writer, header.chunk_index)?;
        write_u64(&mut self.writer, header.first_line_number)?;
        write_u64(&mut self.writer, header.line_count)?;
        write_u64(&mut self.writer, header.uncompressed_len)?;
        write_u64(&mut self.writer, header.compressed_len)?;
        write_u32(&mut self.writer, header.summary_len)?;
        write_u32(&mut self.writer, header.crc32)?;
        write_u64(&mut self.writer, 0)?;
        Ok(())
    }
}

#[derive(Debug)]
pub struct ZlgReader<R: Read> {
    reader: R,
    finished: bool,
}

impl<R: Read> ZlgReader<R> {
    pub fn new(mut reader: R) -> Result<Self> {
        let mut magic = [0u8; 8];
        reader
            .read_exact(&mut magic)
            .context("failed to read zlg global header")?;

        if &magic != GLOBAL_MAGIC {
            return Err(anyhow!("unsupported or invalid zlg magic"));
        }

        let version = read_u16(&mut reader)?;
        if version != FORMAT_VERSION {
            return Err(anyhow!("unsupported zlg version {version}"));
        }

        let header_len = read_u16(&mut reader)?;
        if header_len != GLOBAL_HEADER_LEN {
            return Err(anyhow!("unsupported zlg header length {header_len}"));
        }

        let _flags = read_u32(&mut reader)?;
        let _chunk_policy_id = read_u32(&mut reader)?;
        let _compression_mode_id = read_u32(&mut reader)?;

        let mut reserved = [0u8; 8];
        reader.read_exact(&mut reserved)?;

        Ok(Self {
            reader,
            finished: false,
        })
    }

    pub fn next_raw_chunk(&mut self) -> Result<Option<RawChunk>> {
        let Some(head) = self.next_chunk_head()? else {
            return Ok(None);
        };
        self.read_chunk_payload(head).map(Some)
    }

    pub fn next_chunk_head(&mut self) -> Result<Option<RawChunkHead>> {
        if self.finished {
            return Ok(None);
        }

        let mut magic = [0u8; 4];
        match self.reader.read_exact(&mut magic) {
            Ok(()) => {}
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => {
                self.finished = true;
                return Ok(None);
            }
            Err(error) => return Err(error).context("failed to read next zlg record magic"),
        }

        if &magic == DIR_MAGIC {
            self.skip_directory()?;
            self.skip_footer_if_present()?;
            self.finished = true;
            return Ok(None);
        }

        if &magic != CHUNK_MAGIC {
            return Err(anyhow!("unexpected zlg record magic: {:?}", magic));
        }

        let header = self.read_chunk_header_after_magic()?;
        let summary_len = checked_alloc_len(
            header.summary_len as u64,
            MAX_SUMMARY_LEN,
            "chunk search summary",
        )?;
        let mut summary_bytes = vec![0u8; summary_len];
        self.reader
            .read_exact(&mut summary_bytes)
            .context("failed to read chunk search summary")?;
        let summary = SearchSummary::decode(&summary_bytes)?;

        Ok(Some(RawChunkHead { header, summary }))
    }

    pub fn read_chunk_payload(&mut self, head: RawChunkHead) -> Result<RawChunk> {
        let compressed_len = checked_alloc_len(
            head.header.compressed_len,
            MAX_COMPRESSED_CHUNK_LEN,
            "compressed chunk payload",
        )?;
        let mut compressed = vec![0u8; compressed_len];
        self.reader
            .read_exact(&mut compressed)
            .context("failed to read compressed chunk payload")?;

        Ok(RawChunk {
            header: head.header,
            compressed,
        })
    }

    pub fn skip_chunk_payload(&mut self, header: &ChunkHeader) -> Result<()> {
        let mut remaining = header.compressed_len;
        let mut buffer = [0u8; 64 * 1024];
        while remaining > 0 {
            let take = remaining.min(buffer.len() as u64) as usize;
            self.reader
                .read_exact(&mut buffer[..take])
                .context("failed to skip compressed chunk payload")?;
            remaining -= take as u64;
        }
        Ok(())
    }

    fn read_chunk_header_after_magic(&mut self) -> Result<ChunkHeader> {
        read_chunk_header_after_magic_from(&mut self.reader)
    }

    fn skip_directory(&mut self) -> Result<()> {
        let entry_len = read_u32(&mut self.reader)?;
        if entry_len != DIRECTORY_ENTRY_LEN {
            return Err(anyhow!(
                "unsupported zlg directory entry length {entry_len}"
            ));
        }

        let entry_count = read_u64(&mut self.reader)?;
        let total_len = (entry_len as u64)
            .checked_mul(entry_count)
            .ok_or_else(|| anyhow!("zlg directory length overflow"))?;
        copy_n_to_sink(&mut self.reader, total_len)?;
        Ok(())
    }

    fn skip_footer_if_present(&mut self) -> Result<()> {
        let mut magic = [0u8; 4];
        match self.reader.read_exact(&mut magic) {
            Ok(()) => {}
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => return Ok(()),
            Err(error) => return Err(error).context("failed to read zlg footer magic"),
        }

        if &magic != FOOTER_MAGIC {
            return Err(anyhow!("expected zlg footer magic after directory"));
        }

        let footer_len = read_u32(&mut self.reader)?;
        if footer_len < 8 {
            return Err(anyhow!("invalid footer length {footer_len}"));
        }

        copy_n_to_sink(&mut self.reader, (footer_len - 8) as u64)?;
        Ok(())
    }
}

pub fn read_archive_metadata<R: Read + Seek>(reader: &mut R) -> Result<ArchiveMetadata> {
    let file_len = reader
        .seek(SeekFrom::End(0))
        .context("failed to seek to end of zlg archive")?;
    if file_len < GLOBAL_HEADER_LEN as u64 + DIRECTORY_HEADER_LEN + FOOTER_LEN {
        return Err(anyhow!("zlg archive is too small for metadata"));
    }

    reader
        .seek(SeekFrom::Start(0))
        .context("failed to seek to zlg global header")?;
    let mut magic = [0u8; 8];
    reader
        .read_exact(&mut magic)
        .context("failed to read zlg global header")?;
    if &magic != GLOBAL_MAGIC {
        return Err(anyhow!("unsupported or invalid zlg magic"));
    }

    let format_version = read_u16(reader)?;
    if format_version != FORMAT_VERSION {
        return Err(anyhow!("unsupported zlg version {format_version}"));
    }

    let header_len = read_u16(reader)?;
    if header_len != GLOBAL_HEADER_LEN {
        return Err(anyhow!("unsupported zlg header length {header_len}"));
    }

    let flags = read_u32(reader)?;
    let chunk_policy_id = read_u32(reader)?;
    let compression_mode_id = read_u32(reader)?;
    let mut reserved = [0u8; 8];
    reader.read_exact(&mut reserved)?;

    let footer_offset = file_len
        .checked_sub(FOOTER_LEN)
        .ok_or_else(|| anyhow!("zlg footer offset underflow"))?;
    reader
        .seek(SeekFrom::Start(footer_offset))
        .context("failed to seek to zlg footer")?;

    let mut footer_magic = [0u8; 4];
    reader
        .read_exact(&mut footer_magic)
        .context("failed to read zlg footer magic")?;
    if &footer_magic != FOOTER_MAGIC {
        return Err(anyhow!("invalid zlg footer magic"));
    }

    let footer_len = read_u32(reader)?;
    if footer_len as u64 != FOOTER_LEN {
        return Err(anyhow!("unsupported zlg footer length {footer_len}"));
    }

    let chunk_count = read_u64(reader)?;
    let total_lines = read_u64(reader)?;
    let total_uncompressed_bytes = read_u64(reader)?;
    let directory_offset = read_u64(reader)?;
    let directory_len = read_u64(reader)?;

    if directory_offset < GLOBAL_HEADER_LEN as u64 {
        return Err(anyhow!("zlg directory starts before global header"));
    }
    if directory_len < DIRECTORY_HEADER_LEN {
        return Err(anyhow!("zlg directory length is too small"));
    }
    let directory_end = checked_add_u64(directory_offset, directory_len, "directory end")?;
    if directory_end != footer_offset {
        return Err(anyhow!(
            "zlg directory/footer layout mismatch: directory ends at {}, footer starts at {}",
            directory_end,
            footer_offset
        ));
    }

    reader
        .seek(SeekFrom::Start(directory_offset))
        .context("failed to seek to zlg directory")?;
    let mut dir_magic = [0u8; 4];
    reader
        .read_exact(&mut dir_magic)
        .context("failed to read zlg directory magic")?;
    if &dir_magic != DIR_MAGIC {
        return Err(anyhow!("invalid zlg directory magic"));
    }

    let entry_len = read_u32(reader)?;
    if entry_len != DIRECTORY_ENTRY_LEN {
        return Err(anyhow!(
            "unsupported zlg directory entry length {entry_len}"
        ));
    }

    let entry_count = read_u64(reader)?;
    if entry_count != chunk_count {
        return Err(anyhow!(
            "zlg directory/footer chunk count mismatch: directory {}, footer {}",
            entry_count,
            chunk_count
        ));
    }

    let entries_bytes = (entry_len as u64)
        .checked_mul(entry_count)
        .ok_or_else(|| anyhow!("zlg directory length overflow"))?;
    let expected_directory_len = DIRECTORY_HEADER_LEN
        .checked_add(entries_bytes)
        .ok_or_else(|| anyhow!("zlg directory length overflow"))?;
    if expected_directory_len != directory_len {
        return Err(anyhow!(
            "zlg directory length mismatch: expected {}, got {}",
            expected_directory_len,
            directory_len
        ));
    }

    let entry_count_usize = usize::try_from(entry_count)
        .with_context(|| format!("zlg directory entry count does not fit usize: {entry_count}"))?;
    let mut entries = Vec::with_capacity(entry_count_usize);
    let mut summed_lines = 0u64;
    let mut summed_uncompressed = 0u64;

    for index in 0..entry_count {
        let entry = read_directory_entry(reader)?;
        validate_directory_entry(index, &entry, directory_offset)?;
        summed_lines = checked_add_u64(summed_lines, entry.line_count, "total line count")?;
        summed_uncompressed = checked_add_u64(
            summed_uncompressed,
            entry.uncompressed_len,
            "total uncompressed bytes",
        )?;
        entries.push(entry);
    }

    if summed_lines != total_lines {
        return Err(anyhow!(
            "zlg total line count mismatch: directory {}, footer {}",
            summed_lines,
            total_lines
        ));
    }
    if summed_uncompressed != total_uncompressed_bytes {
        return Err(anyhow!(
            "zlg total byte count mismatch: directory {}, footer {}",
            summed_uncompressed,
            total_uncompressed_bytes
        ));
    }

    Ok(ArchiveMetadata {
        format_version,
        flags,
        chunk_policy_id,
        compression_mode_id,
        chunk_count,
        total_lines,
        total_uncompressed_bytes,
        directory_offset,
        directory_len,
        file_len,
        entries,
    })
}

pub fn read_raw_chunk_at<R: Read + Seek>(
    reader: &mut R,
    entry: &DirectoryEntry,
) -> Result<RawChunk> {
    reader
        .seek(SeekFrom::Start(entry.chunk_offset))
        .context("failed to seek to zlg chunk")?;
    let mut magic = [0u8; 4];
    reader
        .read_exact(&mut magic)
        .context("failed to read zlg chunk magic")?;
    if &magic != CHUNK_MAGIC {
        return Err(anyhow!("invalid zlg chunk magic at directory offset"));
    }

    let header = read_chunk_header_after_magic_from(reader)?;
    validate_chunk_header_matches_entry(&header, entry)?;
    copy_n_to_sink(reader, header.summary_len as u64)
        .context("failed to skip chunk search summary")?;

    let compressed_len = checked_alloc_len(
        header.compressed_len,
        MAX_COMPRESSED_CHUNK_LEN,
        "compressed chunk payload",
    )?;
    let mut compressed = vec![0u8; compressed_len];
    reader
        .read_exact(&mut compressed)
        .context("failed to read compressed chunk payload")?;

    Ok(RawChunk { header, compressed })
}

fn read_chunk_header_after_magic_from<R: Read>(reader: &mut R) -> Result<ChunkHeader> {
    let header_len = read_u16(reader)?;
    if header_len != CHUNK_HEADER_LEN {
        return Err(anyhow!("unsupported zlg chunk header length {header_len}"));
    }

    let flags = read_u16(reader)?;
    let chunk_index = read_u64(reader)?;
    let first_line_number = read_u64(reader)?;
    let line_count = read_u64(reader)?;
    let uncompressed_len = read_u64(reader)?;
    let compressed_len = read_u64(reader)?;
    let summary_len = read_u32(reader)?;
    let crc32 = read_u32(reader)?;
    let _reserved = read_u64(reader)?;

    Ok(ChunkHeader {
        flags,
        chunk_index,
        first_line_number,
        line_count,
        uncompressed_len,
        compressed_len,
        summary_len,
        crc32,
    })
}

fn read_directory_entry<R: Read>(reader: &mut R) -> Result<DirectoryEntry> {
    Ok(DirectoryEntry {
        chunk_offset: read_u64(reader)?,
        summary_offset: read_u64(reader)?,
        summary_len: read_u32(reader)?,
        flags: read_u32(reader)?,
        compressed_offset: read_u64(reader)?,
        compressed_len: read_u64(reader)?,
        uncompressed_len: read_u64(reader)?,
        first_line_number: read_u64(reader)?,
        line_count: read_u64(reader)?,
    })
}

fn validate_directory_entry(
    index: u64,
    entry: &DirectoryEntry,
    directory_offset: u64,
) -> Result<()> {
    if entry.chunk_offset < GLOBAL_HEADER_LEN as u64 {
        return Err(anyhow!("zlg chunk {index} starts before global header"));
    }
    if entry.chunk_offset >= directory_offset {
        return Err(anyhow!(
            "zlg chunk {index} starts inside directory/footer area"
        ));
    }
    if entry.summary_offset < entry.chunk_offset {
        return Err(anyhow!(
            "zlg chunk {index} summary offset is before chunk offset"
        ));
    }
    let summary_end = checked_add_u64(
        entry.summary_offset,
        entry.summary_len as u64,
        "summary end",
    )?;
    if summary_end != entry.compressed_offset {
        return Err(anyhow!("zlg chunk {index} summary/payload layout mismatch"));
    }
    let payload_end =
        checked_add_u64(entry.compressed_offset, entry.compressed_len, "payload end")?;
    if payload_end > directory_offset {
        return Err(anyhow!(
            "zlg chunk {index} payload extends beyond directory"
        ));
    }
    Ok(())
}

fn validate_chunk_header_matches_entry(header: &ChunkHeader, entry: &DirectoryEntry) -> Result<()> {
    if header.summary_len != entry.summary_len
        || header.compressed_len != entry.compressed_len
        || header.uncompressed_len != entry.uncompressed_len
        || header.first_line_number != entry.first_line_number
        || header.line_count != entry.line_count
        || header.flags as u32 != entry.flags
    {
        return Err(anyhow!("zlg chunk header does not match directory entry"));
    }
    Ok(())
}

fn checked_add_u64(left: u64, right: u64, label: &str) -> Result<u64> {
    left.checked_add(right)
        .ok_or_else(|| anyhow!("zlg {label} overflow"))
}

#[derive(Debug)]
struct CountingWriter<W: Write> {
    inner: W,
    bytes_written: u64,
}

impl<W: Write> CountingWriter<W> {
    fn new(inner: W) -> Self {
        Self {
            inner,
            bytes_written: 0,
        }
    }

    fn bytes_written(&self) -> u64 {
        self.bytes_written
    }

    fn into_inner(self) -> W {
        self.inner
    }
}

impl<W: Write> Write for CountingWriter<W> {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        let written = self.inner.write(buf)?;
        self.bytes_written += written as u64;
        Ok(written)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.inner.flush()
    }
}

fn checked_alloc_len(len: u64, max_len: u64, label: &str) -> Result<usize> {
    if len > max_len {
        return Err(anyhow!("{label} length {len} exceeds limit {max_len}"));
    }
    usize::try_from(len).with_context(|| format!("{label} length does not fit usize: {len}"))
}

fn copy_n_to_sink<R: Read>(reader: &mut R, mut len: u64) -> Result<()> {
    let mut buffer = [0u8; 8192];

    while len > 0 {
        let want = buffer.len().min(len as usize);
        reader.read_exact(&mut buffer[..want])?;
        len -= want as u64;
    }

    Ok(())
}

fn write_u16<W: Write>(writer: &mut W, value: u16) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn write_u32<W: Write>(writer: &mut W, value: u32) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn write_u64<W: Write>(writer: &mut W, value: u64) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn read_u16<R: Read>(reader: &mut R) -> Result<u16> {
    let mut bytes = [0u8; 2];
    reader.read_exact(&mut bytes)?;
    Ok(u16::from_le_bytes(bytes))
}

fn read_u32<R: Read>(reader: &mut R) -> Result<u32> {
    let mut bytes = [0u8; 4];
    reader.read_exact(&mut bytes)?;
    Ok(u32::from_le_bytes(bytes))
}

fn read_u64<R: Read>(reader: &mut R) -> Result<u64> {
    let mut bytes = [0u8; 8];
    reader.read_exact(&mut bytes)?;
    Ok(u64::from_le_bytes(bytes))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::chunk::PlainChunk;

    #[test]
    fn round_trip_single_chunk_in_memory() {
        assert_round_trip_bytes(
            b"alpha\nbeta\n",
            SearchSummaryMode::Bitmap,
            BuildProfile::CombinedBitsetSeen,
        );
    }

    #[test]
    fn round_trip_utf8_payload_bytes_exactly() {
        assert_round_trip_bytes(
            b"username=\xe3\x81\x9f\xe3\x82\x8d\xe3\x81\x86 user=\xe3\x82\xab\xe3\x83\x8a msg=\"\xe3\x83\xad\xe3\x82\xb0\xe3\x82\xa4\xe3\x83\xb3\xe6\x88\x90\xe5\x8a\x9f\"\n",
            SearchSummaryMode::MeshBigram,
            BuildProfile::CombinedBitsetSeen,
        );
    }

    #[test]
    fn round_trip_binary_payload_bytes_exactly() {
        assert_round_trip_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00IHDR\x00zlg\x00IDAT\xff\x00END",
            SearchSummaryMode::MeshBigram,
            BuildProfile::CombinedBitsetSeen,
        );
    }

    #[test]
    fn reader_rejects_invalid_global_magic() {
        let err = ZlgReader::new(Cursor::new(b"not-zlg!".to_vec())).unwrap_err();
        assert!(err.to_string().contains("magic"));
    }

    #[test]
    fn reader_rejects_truncated_global_header() {
        let err = ZlgReader::new(Cursor::new(b"ZLG1".to_vec())).unwrap_err();
        assert!(err.to_string().contains("global header"));
    }

    #[test]
    fn reader_rejects_unsupported_global_version() {
        let mut archive = global_header_bytes();
        archive[8..10].copy_from_slice(&99u16.to_le_bytes());
        let err = ZlgReader::new(Cursor::new(archive)).unwrap_err();
        assert!(err.to_string().contains("version"));
    }

    #[test]
    fn reader_rejects_unsupported_chunk_header_length() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let header_len_offset = first_chunk_offset() + 4;
        archive[header_len_offset..header_len_offset + 2].copy_from_slice(&99u16.to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("chunk header length"));
    }

    #[test]
    fn reader_rejects_unexpected_record_magic() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        archive[first_chunk_offset()..first_chunk_offset() + 4].copy_from_slice(b"BAD!");

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("record magic"));
    }

    #[test]
    fn reader_rejects_excessive_compressed_length_before_allocating() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let compressed_len_offset = first_chunk_offset() + 4 + 2 + 2 + 8 + 8 + 8 + 8;
        archive[compressed_len_offset..compressed_len_offset + 8]
            .copy_from_slice(&(MAX_COMPRESSED_CHUNK_LEN + 1).to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let head = reader.next_chunk_head().unwrap().unwrap();
        let err = reader.read_chunk_payload(head).unwrap_err();
        assert!(err.to_string().contains("compressed chunk payload"));
    }

    #[test]
    fn reader_rejects_truncated_summary_bytes() {
        let mut archive = build_archive_bytes(b"alpha\nbeta\n", SearchSummaryMode::MeshBigram);
        let summary_len = first_chunk_summary_len(&archive) as usize;
        let summary_offset = first_chunk_offset() + CHUNK_HEADER_LEN as usize;
        archive.truncate(summary_offset + summary_len.saturating_sub(1));

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_chunk_head().unwrap_err();
        assert!(err.to_string().contains("chunk search summary"));
    }

    #[test]
    fn reader_rejects_unsupported_directory_entry_length() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&63u32.to_le_bytes());
        archive.extend_from_slice(&0u64.to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("directory entry length"));
    }

    #[test]
    fn reader_rejects_directory_length_overflow() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&DIRECTORY_ENTRY_LEN.to_le_bytes());
        archive.extend_from_slice(&u64::MAX.to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("directory length overflow"));
    }

    #[test]
    fn reader_rejects_truncated_directory_payload() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&DIRECTORY_ENTRY_LEN.to_le_bytes());
        archive.extend_from_slice(&1u64.to_le_bytes());
        archive.extend_from_slice(&[0u8; 8]);

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("failed to fill whole buffer"));
    }

    #[test]
    fn reader_rejects_invalid_footer_magic() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&DIRECTORY_ENTRY_LEN.to_le_bytes());
        archive.extend_from_slice(&0u64.to_le_bytes());
        archive.extend_from_slice(b"BAD!");

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("footer magic"));
    }

    #[test]
    fn reader_rejects_invalid_footer_length() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&DIRECTORY_ENTRY_LEN.to_le_bytes());
        archive.extend_from_slice(&0u64.to_le_bytes());
        archive.extend_from_slice(FOOTER_MAGIC);
        archive.extend_from_slice(&4u32.to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("footer length"));
    }

    #[test]
    fn reader_rejects_truncated_footer_payload() {
        let mut archive = global_header_bytes();
        archive.extend_from_slice(DIR_MAGIC);
        archive.extend_from_slice(&DIRECTORY_ENTRY_LEN.to_le_bytes());
        archive.extend_from_slice(&0u64.to_le_bytes());
        archive.extend_from_slice(FOOTER_MAGIC);
        archive.extend_from_slice(&48u32.to_le_bytes());
        archive.extend_from_slice(&[0u8; 8]);

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("failed to fill whole buffer"));
    }

    #[test]
    fn reader_rejects_excessive_summary_length_before_allocating() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let summary_len_offset = first_chunk_offset() + 4 + 2 + 2 + 8 + 8 + 8 + 8 + 8;
        archive[summary_len_offset..summary_len_offset + 4]
            .copy_from_slice(&u32::MAX.to_le_bytes());

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("summary"));
    }

    #[test]
    fn decode_rejects_crc_mismatch() {
        let mut archive = build_archive_bytes(b"alpha\nbeta\n", SearchSummaryMode::MeshBigram);
        let crc_offset = first_chunk_offset() + 4 + 2 + 2 + 8 + 8 + 8 + 8 + 8 + 4;
        archive[crc_offset] ^= 0xff;

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let raw = reader.next_raw_chunk().unwrap().unwrap();
        let err = raw.decode().unwrap_err();
        assert!(err.to_string().contains("crc mismatch"));
    }

    #[test]
    fn reader_rejects_truncated_compressed_payload() {
        let mut archive = build_archive_bytes(b"alpha\nbeta\n", SearchSummaryMode::MeshBigram);
        let summary_len = first_chunk_summary_len(&archive) as usize;
        let compressed_len = first_chunk_compressed_len(&archive) as usize;
        let payload_offset = first_chunk_offset() + CHUNK_HEADER_LEN as usize + summary_len;
        archive.truncate(payload_offset + compressed_len.saturating_sub(1));

        let mut reader = ZlgReader::new(Cursor::new(archive)).unwrap();
        let err = reader.next_raw_chunk().unwrap_err();
        assert!(err.to_string().contains("compressed chunk payload"));
    }

    #[test]
    fn metadata_reader_reads_valid_archive() {
        let archive = build_archive_bytes(b"alpha\nbeta\n", SearchSummaryMode::MeshBigram);
        let metadata = read_archive_metadata(&mut Cursor::new(archive)).unwrap();

        assert_eq!(metadata.format_version, FORMAT_VERSION);
        assert_eq!(metadata.chunk_count, 1);
        assert_eq!(metadata.total_lines, 2);
        assert_eq!(
            metadata.total_uncompressed_bytes,
            b"alpha\nbeta\n".len() as u64
        );
        assert_eq!(metadata.entries.len(), 1);
        assert_eq!(
            metadata.total_payload_bytes(),
            metadata.entries[0].compressed_len
        );
        assert_eq!(
            metadata.total_summary_bytes(),
            metadata.entries[0].summary_len as u64
        );
    }

    #[test]
    fn metadata_reader_handles_empty_archive() {
        let archive = build_empty_archive_bytes();
        let metadata = read_archive_metadata(&mut Cursor::new(archive)).unwrap();

        assert_eq!(metadata.chunk_count, 0);
        assert_eq!(metadata.total_lines, 0);
        assert_eq!(metadata.total_uncompressed_bytes, 0);
        assert!(metadata.entries.is_empty());
    }

    #[test]
    fn metadata_reader_rejects_bad_footer_magic() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let footer_offset = archive.len() - FOOTER_LEN as usize;
        archive[footer_offset..footer_offset + 4].copy_from_slice(b"BAD!");

        let err = read_archive_metadata(&mut Cursor::new(archive)).unwrap_err();
        assert!(err.to_string().contains("footer magic"));
    }

    #[test]
    fn metadata_reader_rejects_bad_directory_magic() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let metadata = read_archive_metadata(&mut Cursor::new(archive.clone())).unwrap();
        let offset = metadata.directory_offset as usize;
        archive[offset..offset + 4].copy_from_slice(b"BAD!");

        let err = read_archive_metadata(&mut Cursor::new(archive)).unwrap_err();
        assert!(err.to_string().contains("directory magic"));
    }

    #[test]
    fn metadata_reader_rejects_directory_footer_count_mismatch() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let metadata = read_archive_metadata(&mut Cursor::new(archive.clone())).unwrap();
        let directory_count_offset = metadata.directory_offset as usize + 8;
        archive[directory_count_offset..directory_count_offset + 8]
            .copy_from_slice(&2u64.to_le_bytes());

        let err = read_archive_metadata(&mut Cursor::new(archive)).unwrap_err();
        assert!(err.to_string().contains("chunk count mismatch"));
    }

    #[test]
    fn metadata_reader_rejects_out_of_bounds_payload() {
        let mut archive = build_archive_bytes(b"alpha\n", SearchSummaryMode::MeshBigram);
        let metadata = read_archive_metadata(&mut Cursor::new(archive.clone())).unwrap();
        let entry_offset = metadata.directory_offset as usize + DIRECTORY_HEADER_LEN as usize;
        let compressed_len_offset = entry_offset + 32;
        archive[compressed_len_offset..compressed_len_offset + 8]
            .copy_from_slice(&u64::MAX.to_le_bytes());

        let err = read_archive_metadata(&mut Cursor::new(archive)).unwrap_err();
        assert!(err.to_string().contains("overflow") || err.to_string().contains("beyond"));
    }

    #[test]
    fn read_raw_chunk_at_reads_directory_selected_chunk() {
        let archive = build_archive_bytes(b"alpha\nbeta\n", SearchSummaryMode::MeshBigram);
        let metadata = read_archive_metadata(&mut Cursor::new(archive.clone())).unwrap();
        let mut cursor = Cursor::new(archive);
        let raw = read_raw_chunk_at(&mut cursor, &metadata.entries[0]).unwrap();
        let decoded = raw.decode().unwrap();

        assert_eq!(decoded.data, b"alpha\nbeta\n");
    }

    fn assert_round_trip_bytes(
        data: &[u8],
        summary_mode: SearchSummaryMode,
        build_profile: BuildProfile,
    ) {
        let chunk = PlainChunk {
            index: 0,
            first_line_number: 1,
            line_count: 1,
            data: data.to_vec(),
            crc32: crc32(data),
            flags: 1,
        };

        let mut out = Vec::new();
        {
            let mut writer = ZlgWriter::new_with_profile(
                &mut out,
                17,
                CompressionMode::Fast,
                summary_mode,
                build_profile,
            )
            .unwrap();
            writer.write_chunk(&chunk).unwrap();
            writer.finish().unwrap();
        }

        let mut reader = ZlgReader::new(Cursor::new(out)).unwrap();
        let raw = reader.next_raw_chunk().unwrap().unwrap();
        let decoded = raw.decode().unwrap();

        assert_eq!(decoded.data, data);
        assert!(reader.next_raw_chunk().unwrap().is_none());
    }

    fn global_header_bytes() -> Vec<u8> {
        let mut out = Vec::new();
        out.extend_from_slice(GLOBAL_MAGIC);
        out.extend_from_slice(&FORMAT_VERSION.to_le_bytes());
        out.extend_from_slice(&GLOBAL_HEADER_LEN.to_le_bytes());
        out.extend_from_slice(&0u32.to_le_bytes());
        out.extend_from_slice(&20u32.to_le_bytes());
        out.extend_from_slice(&0u32.to_le_bytes());
        out.extend_from_slice(&[0u8; 8]);
        out
    }

    fn build_archive_bytes(data: &[u8], summary_mode: SearchSummaryMode) -> Vec<u8> {
        let chunk = PlainChunk {
            index: 0,
            first_line_number: 1,
            line_count: data.iter().filter(|byte| **byte == b'\n').count().max(1) as u64,
            data: data.to_vec(),
            crc32: crc32(data),
            flags: 1,
        };

        let mut out = Vec::new();
        {
            let mut writer = ZlgWriter::new_with_profile(
                &mut out,
                20,
                CompressionMode::Standard,
                summary_mode,
                BuildProfile::CombinedBitsetSeen,
            )
            .unwrap();
            writer.write_chunk(&chunk).unwrap();
            writer.finish().unwrap();
        }
        out
    }

    fn build_empty_archive_bytes() -> Vec<u8> {
        let mut out = Vec::new();
        {
            let writer = ZlgWriter::new_with_profile(
                &mut out,
                20,
                CompressionMode::Standard,
                SearchSummaryMode::MeshBigram,
                BuildProfile::CombinedBitsetSeen,
            )
            .unwrap();
            writer.finish().unwrap();
        }
        out
    }

    fn first_chunk_offset() -> usize {
        GLOBAL_HEADER_LEN as usize
    }

    fn first_chunk_summary_len(archive: &[u8]) -> u32 {
        let offset = first_chunk_offset() + 4 + 2 + 2 + 8 + 8 + 8 + 8 + 8;
        u32::from_le_bytes(archive[offset..offset + 4].try_into().unwrap())
    }

    fn first_chunk_compressed_len(archive: &[u8]) -> u64 {
        let offset = first_chunk_offset() + 4 + 2 + 2 + 8 + 8 + 8 + 8;
        u64::from_le_bytes(archive[offset..offset + 8].try_into().unwrap())
    }
}
