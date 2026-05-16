use crate::chunk::PlainChunk;
use crate::search::{
    encode_bigram_mesh_summary_bitset_paged_seen_into, encode_bigram_mesh_summary_bitset_seen_into,
    encode_bigram_mesh_summary_bucket256_into, encode_bigram_mesh_summary_case_raw_into,
    encode_bigram_mesh_summary_grouped_buckets_into, encode_bigram_mesh_summary_hash_into,
    encode_bigram_mesh_summary_identity_hash_into,
    encode_bigram_mesh_summary_inline_lower_delta_into, encode_bigram_mesh_summary_into,
    encode_bigram_mesh_summary_lower_only_bitset_seen_into,
    encode_bigram_mesh_summary_lower_only_into, encode_bigram_mesh_summary_radix_into,
    encode_bigram_mesh_summary_rdst_into, encode_bigram_mesh_summary_rdxsort_into,
    encode_bigram_mesh_summary_sparse_first_bitset_into,
    encode_bigram_mesh_summary_trie_pair_bitset_into, MeshSummaryBuildStats, SearchSummary,
    SearchSummaryMode,
};

use anyhow::{anyhow, Context, Result};
use crc32fast::Hasher;
use std::io::{Cursor, ErrorKind, Read, Write};
use std::time::Instant;

const GLOBAL_MAGIC: &[u8; 8] = b"ZLG1P0\0\0";
const CHUNK_MAGIC: &[u8; 4] = b"ZCH1";
const DIR_MAGIC: &[u8; 4] = b"ZDR1";
const FOOTER_MAGIC: &[u8; 4] = b"ZFT1";
const GLOBAL_HEADER_LEN: u16 = 32;
const CHUNK_HEADER_LEN: u16 = 64;
const DIRECTORY_ENTRY_LEN: u32 = 64;
const FORMAT_VERSION: u16 = 1;

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

#[derive(Debug)]
pub struct RawChunk {
    pub header: ChunkHeader,
    pub summary: SearchSummary,
    compressed: Vec<u8>,
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
    pub fn decode(self) -> Result<DecodedChunk> {
        let data = zstd::stream::decode_all(Cursor::new(&self.compressed))
            .context("failed to decode zstd chunk")?;

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

            let mut start = 0usize;
            let mut stopped_early = false;
            for idx in 0..read {
                if buffer[idx] == b'\n' {
                    line.extend_from_slice(&buffer[start..=idx]);
                    if !on_line(line_number, &line)? {
                        stopped_early = true;
                        break;
                    }
                    line.clear();
                    line_number += 1;
                    start = idx + 1;
                }
            }

            if stopped_early {
                return Ok(StreamDecodeOutcome {
                    decoded_bytes,
                    crc_checked: false,
                    stopped_early: true,
                });
            }

            if start < read {
                line.extend_from_slice(&buffer[start..read]);
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

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BuildProfile {
    Current,
    MeshScratch,
    ZstdBulk,
    Combined,
    CombinedRadix,
    CombinedHash,
    CombinedIdentityHash,
    CombinedRdxsort,
    CombinedRdst,
    CombinedCaseRaw,
    CombinedLowerOnly,
    CombinedInlineLowerDelta,
    CombinedBitsetSeen,
    CombinedBitsetSeenStreamZstd,
    CombinedBitsetPagedSeen,
    CombinedLowerOnlyBitsetSeen,
    CombinedSparseFirstBitset,
    CombinedTriePairBitset,
    CombinedGroupedBuckets,
    CombinedBucket256,
}

impl BuildProfile {
    fn uses_mesh_scratch(self) -> bool {
        matches!(
            self,
            Self::MeshScratch
                | Self::Combined
                | Self::CombinedRadix
                | Self::CombinedHash
                | Self::CombinedIdentityHash
                | Self::CombinedRdxsort
                | Self::CombinedRdst
                | Self::CombinedCaseRaw
                | Self::CombinedLowerOnly
                | Self::CombinedInlineLowerDelta
                | Self::CombinedBitsetSeen
                | Self::CombinedBitsetSeenStreamZstd
                | Self::CombinedBitsetPagedSeen
                | Self::CombinedLowerOnlyBitsetSeen
                | Self::CombinedSparseFirstBitset
                | Self::CombinedTriePairBitset
                | Self::CombinedGroupedBuckets
                | Self::CombinedBucket256
        )
    }

    fn uses_zstd_bulk(self) -> bool {
        matches!(
            self,
            Self::ZstdBulk
                | Self::Combined
                | Self::CombinedRadix
                | Self::CombinedHash
                | Self::CombinedIdentityHash
                | Self::CombinedRdxsort
                | Self::CombinedRdst
                | Self::CombinedCaseRaw
                | Self::CombinedLowerOnly
                | Self::CombinedInlineLowerDelta
                | Self::CombinedBitsetSeen
                | Self::CombinedBitsetPagedSeen
                | Self::CombinedLowerOnlyBitsetSeen
                | Self::CombinedSparseFirstBitset
                | Self::CombinedTriePairBitset
                | Self::CombinedGroupedBuckets
                | Self::CombinedBucket256
        )
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Current => "current",
            Self::MeshScratch => "mesh-scratch",
            Self::ZstdBulk => "zstd-bulk",
            Self::Combined => "combined",
            Self::CombinedRadix => "combined-radix",
            Self::CombinedHash => "combined-hash",
            Self::CombinedIdentityHash => "combined-identity-hash",
            Self::CombinedRdxsort => "combined-rdxsort",
            Self::CombinedRdst => "combined-rdst",
            Self::CombinedCaseRaw => "combined-case-raw",
            Self::CombinedLowerOnly => "combined-lower-only",
            Self::CombinedInlineLowerDelta => "combined-inline-lower-delta",
            Self::CombinedBitsetSeen => "combined-bitset-seen",
            Self::CombinedBitsetSeenStreamZstd => "combined-bitset-seen-stream-zstd",
            Self::CombinedBitsetPagedSeen => "combined-bitset-paged-seen",
            Self::CombinedLowerOnlyBitsetSeen => "combined-lower-only-bitset-seen",
            Self::CombinedSparseFirstBitset => "combined-sparse-first-bitset",
            Self::CombinedTriePairBitset => "combined-trie-pair-bitset",
            Self::CombinedGroupedBuckets => "combined-grouped-buckets",
            Self::CombinedBucket256 => "combined-bucket256",
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
}

impl BuildStats {
    pub fn to_json(self, profile: BuildProfile) -> String {
        format!(
            "{{\n  \"build_profile\": \"{}\",\n  \"chunks\": {},\n  \"summary_ns\": {},\n  \"zstd_ns\": {},\n  \"write_ns\": {},\n  \"total_ns\": {},\n  \"summary_bytes\": {},\n  \"compressed_bytes\": {},\n  \"uncompressed_bytes\": {},\n  \"raw_edge_windows\": {},\n  \"pushed_edges\": {},\n  \"unique_edges\": {},\n  \"bitset_resizes\": {},\n  \"bitset_cleared_edges\": {},\n  \"touched_first_buckets\": {},\n  \"scratch_bytes\": {},\n  \"bitset_scratch_bytes\": {},\n  \"first_bitset_scratch_bytes\": {},\n  \"edge_scratch_capacity_bytes\": {},\n  \"sort_scratch_capacity_bytes\": {},\n  \"lower_scratch_capacity_bytes\": {},\n  \"summary_scratch_capacity_bytes\": {},\n  \"group_bucket_scratch_bytes\": {},\n  \"max_chunk_uncompressed_bytes\": {},\n  \"max_chunk_compressed_bytes\": {},\n  \"max_chunk_summary_bytes\": {}\n}}\n",
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
            self.pushed_edges,
            self.unique_edges,
            self.bitset_resizes,
            self.bitset_cleared_edges,
            self.touched_first_buckets,
            self.scratch_bytes,
            self.bitset_scratch_bytes,
            self.first_bitset_scratch_bytes,
            self.edge_scratch_capacity_bytes,
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
    level: i32,
    summary_mode: SearchSummaryMode,
    build_profile: BuildProfile,
    build_stats: BuildStats,
    directory: Vec<DirectoryEntry>,
    total_uncompressed_len: u64,
    total_lines: u64,
    mesh_edges_scratch: Vec<u32>,
    mesh_sort_scratch: Vec<u32>,
    mesh_bitset_scratch: Vec<u64>,
    mesh_first_bitsets_scratch: Vec<Vec<u64>>,
    mesh_trie_pair_index_scratch: Vec<[u16; 256]>,
    mesh_trie_pair_bitsets_scratch: Vec<Vec<[u64; 4]>>,
    mesh_trie_touched_pairs_scratch: Vec<(u8, u8)>,
    mesh_group_buckets_scratch: Vec<Vec<u32>>,
    mesh_lower_scratch: Vec<u8>,
    mesh_summary_scratch: Vec<u8>,
    zstd_compressor: Option<zstd::bulk::Compressor<'static>>,
}

impl<W: Write> ZlgWriter<W> {
    #[allow(dead_code)]
    pub fn new(
        writer: W,
        chunk_policy_id: u32,
        level: i32,
        summary_mode: SearchSummaryMode,
    ) -> Result<Self> {
        Self::new_with_profile(
            writer,
            chunk_policy_id,
            level,
            summary_mode,
            BuildProfile::Current,
        )
    }

    pub fn new_with_profile(
        writer: W,
        chunk_policy_id: u32,
        level: i32,
        summary_mode: SearchSummaryMode,
        build_profile: BuildProfile,
    ) -> Result<Self> {
        let mut writer = CountingWriter::new(writer);

        writer.write_all(GLOBAL_MAGIC)?;
        write_u16(&mut writer, FORMAT_VERSION)?;
        write_u16(&mut writer, GLOBAL_HEADER_LEN)?;
        write_u32(&mut writer, 0)?;
        write_u32(&mut writer, chunk_policy_id)?;
        write_u32(&mut writer, 0)?;
        writer.write_all(&[0u8; 8])?;

        let zstd_compressor = if build_profile.uses_zstd_bulk() {
            Some(
                zstd::bulk::Compressor::new(level)
                    .context("failed to create reusable zstd bulk compressor")?,
            )
        } else {
            None
        };

        Ok(Self {
            writer,
            level,
            summary_mode,
            build_profile,
            build_stats: BuildStats::default(),
            directory: Vec::new(),
            total_uncompressed_len: 0,
            total_lines: 0,
            mesh_edges_scratch: Vec::new(),
            mesh_sort_scratch: Vec::new(),
            mesh_bitset_scratch: Vec::new(),
            mesh_first_bitsets_scratch: Vec::new(),
            mesh_trie_pair_index_scratch: Vec::new(),
            mesh_trie_pair_bitsets_scratch: Vec::new(),
            mesh_trie_touched_pairs_scratch: Vec::new(),
            mesh_group_buckets_scratch: Vec::new(),
            mesh_lower_scratch: Vec::new(),
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
            mesh_stats = match self.build_profile {
                BuildProfile::CombinedRadix => encode_bigram_mesh_summary_radix_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_sort_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedHash => encode_bigram_mesh_summary_hash_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedIdentityHash => {
                    encode_bigram_mesh_summary_identity_hash_into(
                        &chunk.data,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_lower_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedRdxsort => encode_bigram_mesh_summary_rdxsort_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedRdst => encode_bigram_mesh_summary_rdst_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedCaseRaw => encode_bigram_mesh_summary_case_raw_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedLowerOnly => encode_bigram_mesh_summary_lower_only_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                BuildProfile::CombinedInlineLowerDelta => {
                    encode_bigram_mesh_summary_inline_lower_delta_into(
                        &chunk.data,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedBitsetSeen | BuildProfile::CombinedBitsetSeenStreamZstd => {
                    encode_bigram_mesh_summary_bitset_seen_into(
                        &chunk.data,
                        &mut self.mesh_bitset_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                },
                BuildProfile::CombinedBitsetPagedSeen => {
                    encode_bigram_mesh_summary_bitset_paged_seen_into(
                        &chunk.data,
                        &mut self.mesh_first_bitsets_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedLowerOnlyBitsetSeen => {
                    encode_bigram_mesh_summary_lower_only_bitset_seen_into(
                        &chunk.data,
                        &mut self.mesh_bitset_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedSparseFirstBitset => {
                    encode_bigram_mesh_summary_sparse_first_bitset_into(
                        &chunk.data,
                        &mut self.mesh_first_bitsets_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedTriePairBitset => {
                    encode_bigram_mesh_summary_trie_pair_bitset_into(
                        &chunk.data,
                        &mut self.mesh_trie_pair_index_scratch,
                        &mut self.mesh_trie_pair_bitsets_scratch,
                        &mut self.mesh_trie_touched_pairs_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedGroupedBuckets => {
                    encode_bigram_mesh_summary_grouped_buckets_into(
                        &chunk.data,
                        &mut self.mesh_group_buckets_scratch,
                        &mut self.mesh_edges_scratch,
                        &mut self.mesh_summary_scratch,
                    )
                }
                BuildProfile::CombinedBucket256 => encode_bigram_mesh_summary_bucket256_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_sort_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
                _ => encode_bigram_mesh_summary_into(
                    &chunk.data,
                    &mut self.mesh_edges_scratch,
                    &mut self.mesh_lower_scratch,
                    &mut self.mesh_summary_scratch,
                ),
            };
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
        let compressed = if let Some(compressor) = self.zstd_compressor.as_mut() {
            compressor
                .compress(&chunk.data)
                .context("failed to encode zstd chunk with reusable bulk compressor")?
        } else {
            zstd::stream::encode_all(Cursor::new(&chunk.data), self.level)
                .context("failed to encode zstd chunk")?
        };
        let zstd_ns = zstd_start.elapsed().as_nanos();

        let header = ChunkHeader {
            flags: chunk.flags,
            chunk_index: chunk.index,
            first_line_number: chunk.first_line_number,
            line_count: chunk.line_count,
            uncompressed_len: chunk.data.len() as u64,
            compressed_len: compressed.len() as u64,
            summary_len: summary_len as u32,
            crc32: crc32(&chunk.data),
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
        let sort_bytes = self.mesh_sort_scratch.capacity() as u64 * 4;
        let bitset_bytes = self.mesh_bitset_scratch.len() as u64 * 8;
        let sparse_first_bitset_bytes: u64 = self
            .mesh_first_bitsets_scratch
            .iter()
            .map(|bucket| bucket.len() as u64 * 8)
            .sum();
        let trie_pair_index_bytes = self.mesh_trie_pair_index_scratch.len() as u64 * 256 * 2;
        let trie_pair_bitset_bytes: u64 = self
            .mesh_trie_pair_bitsets_scratch
            .iter()
            .map(|bucket| bucket.capacity() as u64 * 32)
            .sum();
        let first_bitset_bytes =
            sparse_first_bitset_bytes + trie_pair_index_bytes + trie_pair_bitset_bytes;
        let group_bucket_bytes: u64 = self
            .mesh_group_buckets_scratch
            .iter()
            .map(|bucket| bucket.capacity() as u64 * 4)
            .sum();
        let lower_bytes = self.mesh_lower_scratch.capacity() as u64;
        let summary_bytes = self.mesh_summary_scratch.capacity() as u64;
        let total = edge_bytes
            + sort_bytes
            + bitset_bytes
            + first_bitset_bytes
            + group_bucket_bytes
            + lower_bytes
            + summary_bytes;

        self.build_stats.scratch_bytes = self.build_stats.scratch_bytes.max(total);
        self.build_stats.bitset_scratch_bytes = self
            .build_stats
            .bitset_scratch_bytes
            .max(bitset_bytes.max(mesh_stats.bitset_scratch_bytes));
        self.build_stats.first_bitset_scratch_bytes = self
            .build_stats
            .first_bitset_scratch_bytes
            .max(first_bitset_bytes.max(mesh_stats.first_bitset_scratch_bytes));
        self.build_stats.edge_scratch_capacity_bytes =
            self.build_stats.edge_scratch_capacity_bytes.max(edge_bytes);
        self.build_stats.sort_scratch_capacity_bytes =
            self.build_stats.sort_scratch_capacity_bytes.max(sort_bytes);
        self.build_stats.lower_scratch_capacity_bytes = self
            .build_stats
            .lower_scratch_capacity_bytes
            .max(lower_bytes);
        self.build_stats.summary_scratch_capacity_bytes = self
            .build_stats
            .summary_scratch_capacity_bytes
            .max(summary_bytes);
        self.build_stats.group_bucket_scratch_bytes = self
            .build_stats
            .group_bucket_scratch_bytes
            .max(group_bucket_bytes.max(mesh_stats.group_bucket_scratch_bytes));
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
        let _reserved0 = read_u32(&mut reader)?;

        let mut reserved = [0u8; 8];
        reader.read_exact(&mut reserved)?;

        Ok(Self {
            reader,
            finished: false,
        })
    }

    pub fn next_raw_chunk(&mut self) -> Result<Option<RawChunk>> {
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

        let mut summary_bytes = vec![0u8; header.summary_len as usize];
        self.reader
            .read_exact(&mut summary_bytes)
            .context("failed to read chunk search summary")?;
        let summary = SearchSummary::decode(&summary_bytes)?;

        let mut compressed = vec![0u8; header.compressed_len as usize];
        self.reader
            .read_exact(&mut compressed)
            .context("failed to read compressed chunk payload")?;

        Ok(Some(RawChunk {
            header,
            summary,
            compressed,
        }))
    }

    fn read_chunk_header_after_magic(&mut self) -> Result<ChunkHeader> {
        let header_len = read_u16(&mut self.reader)?;
        if header_len != CHUNK_HEADER_LEN {
            return Err(anyhow!("unsupported zlg chunk header length {header_len}"));
        }

        let flags = read_u16(&mut self.reader)?;
        let chunk_index = read_u64(&mut self.reader)?;
        let first_line_number = read_u64(&mut self.reader)?;
        let line_count = read_u64(&mut self.reader)?;
        let uncompressed_len = read_u64(&mut self.reader)?;
        let compressed_len = read_u64(&mut self.reader)?;
        let summary_len = read_u32(&mut self.reader)?;
        let crc32 = read_u32(&mut self.reader)?;
        let _reserved = read_u64(&mut self.reader)?;

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

    fn skip_directory(&mut self) -> Result<()> {
        let entry_len = read_u32(&mut self.reader)?;
        if entry_len != DIRECTORY_ENTRY_LEN {
            return Err(anyhow!(
                "unsupported zlg directory entry length {entry_len}"
            ));
        }

        let entry_count = read_u64(&mut self.reader)?;
        let total_len = entry_len as u64 * entry_count;
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

fn copy_n_to_sink<R: Read>(reader: &mut R, mut len: u64) -> Result<()> {
    let mut buffer = [0u8; 8192];

    while len > 0 {
        let want = buffer.len().min(len as usize);
        reader.read_exact(&mut buffer[..want])?;
        len -= want as u64;
    }

    Ok(())
}

fn crc32(bytes: &[u8]) -> u32 {
    let mut hasher = Hasher::new();
    hasher.update(bytes);
    hasher.finalize()
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
            BuildProfile::Current,
        );
    }

    #[test]
    fn round_trip_utf8_payload_bytes_exactly() {
        assert_round_trip_bytes(
            b"username=\xe3\x81\x9f\xe3\x82\x8d\xe3\x81\x86 user=\xe3\x82\xab\xe3\x83\x8a msg=\"\xe3\x83\xad\xe3\x82\xb0\xe3\x82\xa4\xe3\x83\xb3\xe6\x88\x90\xe5\x8a\x9f\"\n",
            SearchSummaryMode::MeshBigram,
            BuildProfile::CombinedGroupedBuckets,
        );
    }

    #[test]
    fn round_trip_binary_payload_bytes_exactly() {
        assert_round_trip_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00IHDR\x00zlg\x00IDAT\xff\x00END",
            SearchSummaryMode::MeshBigram,
            BuildProfile::CombinedSparseFirstBitset,
        );
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
            flags: 1,
        };

        let mut out = Vec::new();
        {
            let mut writer =
                ZlgWriter::new_with_profile(&mut out, 17, 1, summary_mode, build_profile).unwrap();
            writer.write_chunk(&chunk).unwrap();
            writer.finish().unwrap();
        }

        let mut reader = ZlgReader::new(Cursor::new(out)).unwrap();
        let raw = reader.next_raw_chunk().unwrap().unwrap();
        let decoded = raw.decode().unwrap();

        assert_eq!(decoded.data, data);
        assert!(reader.next_raw_chunk().unwrap().is_none());
    }
}
