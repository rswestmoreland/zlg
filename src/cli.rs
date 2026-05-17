use crate::chunk::{ChunkPolicy, Chunker};
use crate::format::{
    default_build_profile_name, default_chunk_policy_name, default_compression_mode_name,
    default_summary_type_name, read_archive_metadata, read_raw_chunk_at, zlg_format_version,
    ArchiveMetadata, BuildProfile, CompressionMode, DecodedChunk, RawChunk, StreamDecodeOutcome,
    ZlgReader, ZlgWriter,
};
use crate::search::{GrepOptions, MatchCounters, Matcher, SearchSummaryMode};

use anyhow::{anyhow, Context, Result};
use clap::{Args, Parser, Subcommand, ValueEnum};
use std::collections::VecDeque;
use std::fs::{File, OpenOptions};
use std::io::{self, BufReader, BufWriter, Read, Write};
use std::path::PathBuf;

#[derive(Debug, Parser)]
#[command(name = "zlg")]
#[command(about = "Searchable zstd-backed log compression prototype")]
#[command(version)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Debug, Subcommand)]
pub enum Commands {
    Compress(CompressArgs),
    Decompress(CatArgs),
    Cat(CatArgs),
    Grep(GrepArgs),
    Head(HeadTailArgs),
    Tail(HeadTailArgs),
    Test(TestArgs),
    Info(InfoStatsArgs),
    Stats(InfoStatsArgs),
    Version(VersionArgs),
}

#[derive(Clone, Debug, ValueEnum)]
pub enum ChunkPolicyArg {
    FixedLines512,
    FixedLines1024,
    FixedLines2048,
    FixedLines4096,
    FixedLines8192,
    FixedLines16384,
    FixedLines64k,
    ProgressiveLines,
    Byte1m,
    Byte4m,
    Byte8m,
    HybridProgressiveCap4m,
    HybridProgressiveCap8m,
    HybridProgressiveCap16m,
    HybridProgressiveCap32m,
    HybridFixed64kCap8m,
    HybridFixed64kCap16m,
    HybridFixed64kCap32m,
    FixedLines8192Cap4m,
    FixedLines8192Cap8m,
    FixedLines8192Cap16m,
}

impl From<ChunkPolicyArg> for ChunkPolicy {
    fn from(value: ChunkPolicyArg) -> Self {
        match value {
            ChunkPolicyArg::FixedLines512 => ChunkPolicy::FixedLines {
                lines: 512,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines1024 => ChunkPolicy::FixedLines {
                lines: 1024,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines2048 => ChunkPolicy::FixedLines {
                lines: 2048,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines4096 => ChunkPolicy::FixedLines {
                lines: 4096,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines8192 => ChunkPolicy::FixedLines {
                lines: 8192,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines16384 => ChunkPolicy::FixedLines {
                lines: 16_384,
                byte_cap: None,
            },
            ChunkPolicyArg::FixedLines64k => ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: None,
            },
            ChunkPolicyArg::ProgressiveLines => ChunkPolicy::ProgressiveLines { byte_cap: None },
            ChunkPolicyArg::Byte1m => ChunkPolicy::ByteTarget { bytes: 1024 * 1024 },
            ChunkPolicyArg::Byte4m => ChunkPolicy::ByteTarget {
                bytes: 4 * 1024 * 1024,
            },
            ChunkPolicyArg::Byte8m => ChunkPolicy::ByteTarget {
                bytes: 8 * 1024 * 1024,
            },
            ChunkPolicyArg::HybridProgressiveCap4m => ChunkPolicy::ProgressiveLines {
                byte_cap: Some(4 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridProgressiveCap8m => ChunkPolicy::ProgressiveLines {
                byte_cap: Some(8 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridProgressiveCap16m => ChunkPolicy::ProgressiveLines {
                byte_cap: Some(16 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridProgressiveCap32m => ChunkPolicy::ProgressiveLines {
                byte_cap: Some(32 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridFixed64kCap8m => ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(8 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridFixed64kCap16m => ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(16 * 1024 * 1024),
            },
            ChunkPolicyArg::HybridFixed64kCap32m => ChunkPolicy::FixedLines {
                lines: 65_536,
                byte_cap: Some(32 * 1024 * 1024),
            },
            ChunkPolicyArg::FixedLines8192Cap4m => ChunkPolicy::FixedLines {
                lines: 8_192,
                byte_cap: Some(4 * 1024 * 1024),
            },
            ChunkPolicyArg::FixedLines8192Cap8m => ChunkPolicy::FixedLines {
                lines: 8_192,
                byte_cap: Some(8 * 1024 * 1024),
            },
            ChunkPolicyArg::FixedLines8192Cap16m => ChunkPolicy::FixedLines {
                lines: 8_192,
                byte_cap: Some(16 * 1024 * 1024),
            },
        }
    }
}

#[derive(Clone, Debug, ValueEnum)]
pub enum SummaryModeArg {
    Bitmap,
    PathWindow,
    MeshBigram,
    None,
}

impl From<SummaryModeArg> for SearchSummaryMode {
    fn from(value: SummaryModeArg) -> Self {
        match value {
            SummaryModeArg::Bitmap => SearchSummaryMode::Bitmap,
            SummaryModeArg::PathWindow => SearchSummaryMode::PathWindow,
            SummaryModeArg::MeshBigram => SearchSummaryMode::MeshBigram,
            SummaryModeArg::None => SearchSummaryMode::None,
        }
    }
}

#[derive(Clone, Debug, ValueEnum)]
pub enum BuildProfileArg {
    CombinedBitsetSeen,
}

impl From<BuildProfileArg> for BuildProfile {
    fn from(value: BuildProfileArg) -> Self {
        match value {
            BuildProfileArg::CombinedBitsetSeen => BuildProfile::CombinedBitsetSeen,
        }
    }
}

#[derive(Clone, Debug, ValueEnum)]
pub enum CompressionModeArg {
    None,
    Fast,
    Standard,
    Best,
}

impl From<CompressionModeArg> for CompressionMode {
    fn from(value: CompressionModeArg) -> Self {
        match value {
            CompressionModeArg::None => CompressionMode::None,
            CompressionModeArg::Fast => CompressionMode::Fast,
            CompressionModeArg::Standard => CompressionMode::Standard,
            CompressionModeArg::Best => CompressionMode::Best,
        }
    }
}

#[derive(Debug, Args)]
pub struct CompressArgs {
    pub input: Option<PathBuf>,

    #[arg(short, long)]
    pub output: Option<PathBuf>,

    #[arg(long, value_enum, default_value_t = CompressionModeArg::Standard)]
    pub mode: CompressionModeArg,

    #[arg(long, value_enum, default_value_t = ChunkPolicyArg::FixedLines8192Cap8m, hide = true)]
    pub chunk_policy: ChunkPolicyArg,

    #[arg(long, value_enum, default_value_t = SummaryModeArg::MeshBigram, hide = true)]
    pub summary_mode: SummaryModeArg,

    #[arg(long, value_enum, default_value_t = BuildProfileArg::CombinedBitsetSeen, hide = true)]
    pub build_profile: BuildProfileArg,

    #[arg(long, hide = true)]
    pub build_stats_json: Option<PathBuf>,

    #[arg(long)]
    pub force: bool,
}

#[derive(Debug, Args)]
pub struct CatArgs {
    pub input: Option<PathBuf>,

    #[arg(short, long)]
    pub output: Option<PathBuf>,

    #[arg(long)]
    pub force: bool,
}

#[derive(Debug, Args)]
pub struct HeadTailArgs {
    pub input: Option<PathBuf>,

    #[arg(short = 'n', long, default_value_t = 10)]
    pub lines: usize,
}

#[derive(Debug, Args)]
pub struct TestArgs {
    pub input: Option<PathBuf>,

    #[arg(long)]
    pub json: bool,

    #[arg(long)]
    pub quiet: bool,
}

#[derive(Debug, Args)]
pub struct InfoStatsArgs {
    pub input: Option<PathBuf>,

    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct VersionArgs {
    #[arg(long)]
    pub long: bool,
}

#[derive(Debug, Args)]
pub struct GrepArgs {
    pub pattern: String,

    pub input: Vec<PathBuf>,

    #[arg(short = 'f', long)]
    pub fixed: bool,

    #[arg(short = 'p', long)]
    pub pcre2: bool,

    #[arg(short = 'o', long)]
    pub only_matching: bool,

    #[arg(short = 'n', long)]
    pub line_number: bool,

    #[arg(short = 'i', long)]
    pub ignore_case: bool,

    #[arg(short = 'c', long)]
    pub count: bool,

    #[arg(short = 'l', long)]
    pub files_with_matches: bool,

    #[arg(short = 'v', long)]
    pub invert_match: bool,

    #[arg(long)]
    pub no_filename: bool,

    #[arg(long)]
    pub with_filename: bool,

    #[arg(long, hide = true)]
    pub stats_json: Option<PathBuf>,

    #[arg(long)]
    pub head: Option<usize>,
}

pub fn run_compress(args: CompressArgs) -> Result<()> {
    let input = open_input(args.input.as_ref())?;
    let output = open_output(args.output.as_ref(), args.force)?;
    let mode: CompressionMode = args.mode.into();
    let policy: ChunkPolicy = args.chunk_policy.into();
    let summary_mode: SearchSummaryMode = args.summary_mode.into();

    let mut reader = BufReader::new(input);
    let writer = BufWriter::new(output);

    let build_profile: BuildProfile = args.build_profile.into();
    let mut zlg_writer =
        ZlgWriter::new_with_profile(writer, policy.id(), mode, summary_mode, build_profile)?;
    let mut chunker = Chunker::new(policy);

    while let Some(chunk) = chunker.next_chunk(&mut reader)? {
        zlg_writer.write_chunk(&chunk)?;
    }

    let build_stats = zlg_writer.build_stats();
    zlg_writer.finish()?;

    if let Some(path) = args.build_stats_json {
        std::fs::write(path, build_stats.to_json(build_profile))
            .context("failed to write build stats json")?;
    }

    Ok(())
}

pub fn run_cat(args: CatArgs) -> Result<()> {
    let input = open_input(args.input.as_ref())?;
    let output = open_output(args.output.as_ref(), args.force)?;

    let mut reader = ZlgReader::new(BufReader::new(input))?;
    let mut writer = BufWriter::new(output);

    while let Some(raw_chunk) = reader.next_raw_chunk()? {
        let decoded = raw_chunk.decode()?;
        writer.write_all(&decoded.data)?;
    }

    writer.flush()?;
    Ok(())
}

#[derive(Debug, Default)]
struct GrepStats {
    files: u64,
    chunks_total: u64,
    chunks_skipped: u64,
    candidate_chunks: u64,
    chunks_decoded: u64,
    decoded_bytes: u64,
    matching_lines: u64,
    selector_kind: &'static str,
    selector_len: usize,
    selector_count: usize,
    stream_decode: bool,
    crc_checked_chunks: u64,
    stream_early_stopped_chunks: u64,
    lines_scanned: u64,
    fixed_calls: u64,
    rust_regex_calls: u64,
    pcre2_calls: u64,
    fast_path_calls: u64,
    prefilter_rejects: u64,
}

impl GrepStats {
    fn add_match_counters(&mut self, counters: MatchCounters) {
        self.lines_scanned += counters.lines_scanned;
        self.fixed_calls += counters.fixed_calls;
        self.rust_regex_calls += counters.rust_regex_calls;
        self.pcre2_calls += counters.pcre2_calls;
        self.fast_path_calls += counters.fast_path_calls;
        self.prefilter_rejects += counters.prefilter_rejects;
    }

    fn to_json(&self) -> String {
        format!(
            "{{\n  \"files\": {},\n  \"chunks_total\": {},\n  \"chunks_skipped\": {},\n  \"candidate_chunks\": {},\n  \"chunks_decoded\": {},\n  \"decoded_bytes\": {},\n  \"matching_lines\": {},\n  \"selector_kind\": \"{}\",\n  \"selector_len\": {},\n  \"selector_count\": {},\n  \"stream_decode\": {},\n  \"crc_checked_chunks\": {},\n  \"stream_early_stopped_chunks\": {},\n  \"lines_scanned\": {},\n  \"fixed_calls\": {},\n  \"rust_regex_calls\": {},\n  \"pcre2_calls\": {},\n  \"fast_path_calls\": {},\n  \"prefilter_rejects\": {}\n}}\n",
            self.files,
            self.chunks_total,
            self.chunks_skipped,
            self.candidate_chunks,
            self.chunks_decoded,
            self.decoded_bytes,
            self.matching_lines,
            self.selector_kind,
            self.selector_len,
            self.selector_count,
            self.stream_decode,
            self.crc_checked_chunks,
            self.stream_early_stopped_chunks,
            self.lines_scanned,
            self.fixed_calls,
            self.rust_regex_calls,
            self.pcre2_calls,
            self.fast_path_calls,
            self.prefilter_rejects
        )
    }
}

pub fn run_grep(args: GrepArgs) -> Result<()> {
    if args.fixed && args.pcre2 {
        return Err(anyhow!("cannot combine -f and -p"));
    }

    let options = GrepOptions {
        fixed_strings: args.fixed,
        perl_regexp: args.pcre2,
        only_matching: args.only_matching,
        line_number: args.line_number,
        ignore_case: args.ignore_case,
        count: args.count,
        files_with_matches: args.files_with_matches,
        invert_match: args.invert_match,
        max_count: args.head,
        stream_decode: true,
    };

    let matcher = Matcher::new(&args.pattern, options.clone())?;
    let mut stdout = BufWriter::new(io::stdout().lock());
    let mut stats = GrepStats {
        selector_kind: matcher.selector_kind(),
        selector_len: matcher.selector_len(),
        selector_count: matcher.selector_count(),
        stream_decode: options.stream_decode,
        ..GrepStats::default()
    };

    if args.input.is_empty() {
        let input = open_input(None)?;
        let matches = grep_one(
            input,
            None,
            false,
            &matcher,
            &options,
            &mut stdout,
            &mut stats,
        )?;
        write_grep_stats(args.stats_json.as_ref(), &stats)?;
        return grep_exit(matches);
    }

    let show_filename = if args.no_filename {
        false
    } else if args.with_filename {
        true
    } else {
        args.input.len() > 1
    };

    let mut total_matches = 0usize;
    for path in &args.input {
        let input = open_input(Some(path))?;
        total_matches += grep_one(
            input,
            Some(path),
            show_filename,
            &matcher,
            &options,
            &mut stdout,
            &mut stats,
        )?;
    }

    stdout.flush()?;
    write_grep_stats(args.stats_json.as_ref(), &stats)?;
    grep_exit(total_matches)
}

fn write_grep_stats(path: Option<&PathBuf>, stats: &GrepStats) -> Result<()> {
    if let Some(path) = path {
        std::fs::write(path, stats.to_json())
            .with_context(|| format!("failed to write grep stats {}", path.display()))?;
    }
    Ok(())
}

fn grep_exit(matches: usize) -> Result<()> {
    if matches == 0 {
        std::process::exit(1);
    }
    Ok(())
}

fn grep_one(
    input: Box<dyn Read>,
    path: Option<&PathBuf>,
    show_filename: bool,
    matcher: &Matcher,
    options: &GrepOptions,
    writer: &mut dyn Write,
    stats: &mut GrepStats,
) -> Result<usize> {
    let mut reader = ZlgReader::new(BufReader::new(input))?;
    stats.files += 1;
    let mut match_count = 0usize;
    let mut file_has_match = false;

    while let Some(raw_head) = reader.next_chunk_head()? {
        stats.chunks_total += 1;
        if !matcher.chunk_may_match(&raw_head.summary) {
            reader.skip_chunk_payload(&raw_head.header)?;
            stats.chunks_skipped += 1;
            continue;
        }

        if options.max_count.is_some_and(|limit| match_count >= limit) {
            break;
        }

        stats.candidate_chunks += 1;
        let raw_chunk = reader.read_chunk_payload(raw_head)?;
        let remaining = options
            .max_count
            .map(|limit| limit.saturating_sub(match_count));
        let chunk_result = if options.stream_decode {
            let (chunk_matches, outcome, counters) = grep_streaming_chunk(
                raw_chunk,
                path,
                show_filename,
                matcher,
                options,
                writer,
                remaining,
            )?;
            stats.add_match_counters(counters);
            stats.chunks_decoded += 1;
            stats.decoded_bytes += outcome.decoded_bytes;
            if outcome.crc_checked {
                stats.crc_checked_chunks += 1;
            }
            if outcome.stopped_early {
                stats.stream_early_stopped_chunks += 1;
            }
            chunk_matches
        } else {
            let decoded = raw_chunk.decode()?;
            stats.chunks_decoded += 1;
            stats.decoded_bytes += decoded.data.len() as u64;
            let (chunk_matches, counters) = grep_decoded_chunk(
                &decoded,
                path,
                show_filename,
                matcher,
                options,
                writer,
                remaining,
            )?;
            stats.add_match_counters(counters);
            chunk_matches
        };

        if chunk_result > 0 {
            file_has_match = true;
            match_count += chunk_result;
            stats.matching_lines += chunk_result as u64;

            if options.files_with_matches
                || options.max_count.is_some_and(|limit| match_count >= limit)
            {
                break;
            }
        }
    }

    if options.files_with_matches && file_has_match {
        if let Some(path) = path {
            writeln!(writer, "{}", path.display())?;
        }
    } else if options.count {
        if show_filename {
            if let Some(path) = path {
                write!(writer, "{}:", path.display())?;
            }
        }
        writeln!(writer, "{match_count}")?;
    }

    Ok(match_count)
}

fn grep_streaming_chunk(
    raw_chunk: RawChunk,
    path: Option<&PathBuf>,
    show_filename: bool,
    matcher: &Matcher,
    options: &GrepOptions,
    writer: &mut dyn Write,
    max_matches: Option<usize>,
) -> Result<(usize, StreamDecodeOutcome, MatchCounters)> {
    let mut matches = 0usize;
    let mut counters = MatchCounters::default();
    let outcome = raw_chunk.decode_streaming_lines(|line_number, line| {
        let line_matches = matcher.line_matches_profiled(line, &mut counters)?;
        let selected = if options.invert_match {
            !line_matches
        } else {
            line_matches
        };

        if selected {
            if max_matches.is_some_and(|limit| matches >= limit) {
                return Ok(false);
            }

            matches += 1;

            if !options.count && !options.files_with_matches {
                if options.only_matching && !options.invert_match {
                    for item in matcher.find_matches(line)? {
                        write_prefix(
                            writer,
                            path,
                            show_filename,
                            options.line_number,
                            line_number,
                        )?;
                        writer.write_all(&item)?;
                        writer.write_all(b"\n")?;
                    }
                } else {
                    write_prefix(
                        writer,
                        path,
                        show_filename,
                        options.line_number,
                        line_number,
                    )?;
                    writer.write_all(trim_trailing_newline(line))?;
                    writer.write_all(b"\n")?;
                }
            }

            if options.files_with_matches || max_matches.is_some_and(|limit| matches >= limit) {
                return Ok(false);
            }
        }

        Ok(true)
    })?;

    Ok((matches, outcome, counters))
}

fn grep_decoded_chunk(
    decoded: &DecodedChunk,
    path: Option<&PathBuf>,
    show_filename: bool,
    matcher: &Matcher,
    options: &GrepOptions,
    writer: &mut dyn Write,
    max_matches: Option<usize>,
) -> Result<(usize, MatchCounters)> {
    let mut matches = 0usize;
    let mut counters = MatchCounters::default();
    let mut line_number = decoded.header.first_line_number;

    for line in split_lines_preserve(&decoded.data) {
        let line_matches = matcher.line_matches_profiled(line, &mut counters)?;
        let selected = if options.invert_match {
            !line_matches
        } else {
            line_matches
        };

        if selected {
            if max_matches.is_some_and(|limit| matches >= limit) {
                break;
            }

            matches += 1;

            if !options.count && !options.files_with_matches {
                if options.only_matching && !options.invert_match {
                    for item in matcher.find_matches(line)? {
                        write_prefix(
                            writer,
                            path,
                            show_filename,
                            options.line_number,
                            line_number,
                        )?;
                        writer.write_all(&item)?;
                        writer.write_all(b"\n")?;
                    }
                } else {
                    write_prefix(
                        writer,
                        path,
                        show_filename,
                        options.line_number,
                        line_number,
                    )?;
                    writer.write_all(trim_trailing_newline(line))?;
                    writer.write_all(b"\n")?;
                }
            }

            if max_matches.is_some_and(|limit| matches >= limit) {
                break;
            }
        }

        line_number += 1;
    }

    Ok((matches, counters))
}

pub fn run_head(args: HeadTailArgs) -> Result<()> {
    let input = open_input(args.input.as_ref())?;
    let mut reader = ZlgReader::new(BufReader::new(input))?;
    let mut writer = BufWriter::new(io::stdout().lock());
    let mut remaining = args.lines;

    while remaining > 0 {
        let Some(raw_chunk) = reader.next_raw_chunk()? else {
            break;
        };
        let decoded = raw_chunk.decode()?;
        for line in split_lines_preserve(&decoded.data) {
            if remaining == 0 {
                break;
            }
            writer.write_all(line)?;
            remaining -= 1;
        }
    }

    writer.flush()?;
    Ok(())
}

pub fn run_tail(args: HeadTailArgs) -> Result<()> {
    if args.lines == 0 {
        return Ok(());
    }

    if let Some(path) = args.input.as_ref() {
        return run_tail_seekable(path, args.lines);
    }

    run_tail_streaming(args.lines)
}

fn run_tail_seekable(path: &PathBuf, lines_wanted: usize) -> Result<()> {
    let mut file =
        File::open(path).with_context(|| format!("failed to open input {}", path.display()))?;
    let metadata = read_archive_metadata(&mut file)
        .with_context(|| format!("failed to read zlg metadata from {}", path.display()))?;

    let mut covered = 0u64;
    let mut start = metadata.entries.len();
    for index in (0..metadata.entries.len()).rev() {
        start = index;
        covered = covered.saturating_add(metadata.entries[index].line_count);
        if covered >= lines_wanted as u64 {
            break;
        }
    }

    let mut lines: VecDeque<Vec<u8>> = VecDeque::new();
    if start < metadata.entries.len() {
        for entry in &metadata.entries[start..] {
            let raw_chunk = read_raw_chunk_at(&mut file, entry)?;
            let decoded = raw_chunk.decode()?;
            push_tail_lines(&mut lines, &decoded.data, lines_wanted);
        }
    }

    write_tail_lines(lines)
}

fn run_tail_streaming(lines_wanted: usize) -> Result<()> {
    let input = open_input(None)?;
    let mut reader = ZlgReader::new(BufReader::new(input))?;
    let mut lines: VecDeque<Vec<u8>> = VecDeque::new();

    while let Some(raw_chunk) = reader.next_raw_chunk()? {
        let decoded = raw_chunk.decode()?;
        push_tail_lines(&mut lines, &decoded.data, lines_wanted);
    }

    write_tail_lines(lines)
}

fn push_tail_lines(lines: &mut VecDeque<Vec<u8>>, data: &[u8], lines_wanted: usize) {
    if lines_wanted == 0 {
        return;
    }
    for line in split_lines_preserve(data) {
        if lines.len() == lines_wanted {
            lines.pop_front();
        }
        lines.push_back(line.to_vec());
    }
}

fn write_tail_lines(lines: VecDeque<Vec<u8>>) -> Result<()> {
    let mut writer = BufWriter::new(io::stdout().lock());
    for line in lines {
        writer.write_all(&line)?;
    }
    writer.flush()?;
    Ok(())
}

pub fn run_test(args: TestArgs) -> Result<()> {
    if args.json && args.quiet {
        return Err(anyhow!("cannot combine --json and --quiet"));
    }

    let expected_metadata = if let Some(path) = args.input.as_ref() {
        let mut file =
            File::open(path).with_context(|| format!("failed to open input {}", path.display()))?;
        Some(
            read_archive_metadata(&mut file)
                .with_context(|| format!("failed to read zlg metadata from {}", path.display()))?,
        )
    } else {
        None
    };

    let input = open_input(args.input.as_ref())?;
    let mut reader = ZlgReader::new(BufReader::new(input))?;
    let mut chunks = 0u64;
    let mut lines = 0u64;
    let mut bytes = 0u64;

    while let Some(raw_chunk) = reader.next_raw_chunk()? {
        let chunk_index = raw_chunk.header.chunk_index;
        let decoded = raw_chunk
            .decode()
            .with_context(|| format!("failed to decode zlg chunk {chunk_index}"))?;
        chunks += 1;
        lines += decoded.header.line_count;
        bytes += decoded.data.len() as u64;
    }

    if let Some(metadata) = expected_metadata.as_ref() {
        if chunks != metadata.chunk_count {
            return Err(anyhow!(
                "zlg test chunk count mismatch: decoded {}, metadata {}",
                chunks,
                metadata.chunk_count
            ));
        }
        if lines != metadata.total_lines {
            return Err(anyhow!(
                "zlg test line count mismatch: decoded {}, metadata {}",
                lines,
                metadata.total_lines
            ));
        }
        if bytes != metadata.total_uncompressed_bytes {
            return Err(anyhow!(
                "zlg test byte count mismatch: decoded {}, metadata {}",
                bytes,
                metadata.total_uncompressed_bytes
            ));
        }
    }

    if args.quiet {
        return Ok(());
    }

    if args.json {
        println!(
            "{{\n  \"status\": \"ok\",\n  \"chunks\": {},\n  \"lines\": {},\n  \"uncompressed_bytes\": {},\n  \"metadata_checked\": {}\n}}",
            chunks,
            lines,
            bytes,
            expected_metadata.is_some()
        );
    } else {
        println!("zlg test");
        println!("========");
        println!("status: ok");
        println!("chunks: {chunks}");
        println!("lines: {lines}");
        println!("uncompressed-bytes: {bytes}");
        println!(
            "metadata: {}",
            if expected_metadata.is_some() {
                "checked"
            } else {
                "streamed"
            }
        );
    }

    Ok(())
}

#[derive(Debug, Default)]
struct ArchiveStats {
    chunks: u64,
    lines: u64,
    uncompressed_bytes: u64,
    payload_bytes: u64,
    summary_bytes: u64,
    directory_offset: Option<u64>,
    directory_bytes: u64,
    file_bytes: Option<u64>,
    format_version: Option<u16>,
    flags: Option<u32>,
    chunk_policy_id: Option<u32>,
    compression_mode_id: Option<u32>,
    used_metadata: bool,
}

impl ArchiveStats {
    fn read(args: &InfoStatsArgs) -> Result<Self> {
        if let Some(path) = args.input.as_ref() {
            let mut file = File::open(path)
                .with_context(|| format!("failed to open input {}", path.display()))?;
            let metadata = read_archive_metadata(&mut file)
                .with_context(|| format!("failed to read zlg metadata from {}", path.display()))?;
            return Ok(Self::from_metadata(&metadata));
        }

        Self::read_streaming()
    }

    fn from_metadata(metadata: &ArchiveMetadata) -> Self {
        Self {
            chunks: metadata.chunk_count,
            lines: metadata.total_lines,
            uncompressed_bytes: metadata.total_uncompressed_bytes,
            payload_bytes: metadata.total_payload_bytes(),
            summary_bytes: metadata.total_summary_bytes(),
            directory_offset: Some(metadata.directory_offset),
            directory_bytes: metadata.directory_len,
            file_bytes: Some(metadata.file_len),
            format_version: Some(metadata.format_version),
            flags: Some(metadata.flags),
            chunk_policy_id: Some(metadata.chunk_policy_id),
            compression_mode_id: Some(metadata.compression_mode_id),
            used_metadata: true,
        }
    }

    fn read_streaming() -> Result<Self> {
        let input = open_input(None)?;
        let mut reader = ZlgReader::new(BufReader::new(input))?;
        let mut stats = Self::default();

        while let Some(raw_chunk) = reader.next_raw_chunk()? {
            stats.chunks += 1;
            stats.lines += raw_chunk.header.line_count;
            stats.uncompressed_bytes += raw_chunk.header.uncompressed_len;
            stats.payload_bytes += raw_chunk.header.compressed_len;
            stats.summary_bytes += raw_chunk.header.summary_len as u64;
            let _ = raw_chunk.decode()?;
        }

        Ok(stats)
    }

    fn total_component_bytes(&self) -> u64 {
        self.payload_bytes + self.summary_bytes + self.directory_bytes
    }

    fn metadata_bytes(&self) -> u64 {
        self.summary_bytes + self.directory_bytes
    }

    fn container_overhead_bytes(&self) -> Option<u64> {
        self.file_bytes.map(|file_bytes| {
            file_bytes
                .saturating_sub(self.payload_bytes + self.summary_bytes + self.directory_bytes)
        })
    }

    fn compression_ratio(&self) -> Option<f64> {
        self.file_bytes.and_then(|file_bytes| {
            if file_bytes == 0 {
                None
            } else {
                Some(self.uncompressed_bytes as f64 / file_bytes as f64)
            }
        })
    }

    fn archive_percent_of_raw(&self) -> Option<f64> {
        self.file_bytes.and_then(|file_bytes| {
            if self.uncompressed_bytes == 0 {
                None
            } else {
                Some(file_bytes as f64 / self.uncompressed_bytes as f64 * 100.0)
            }
        })
    }

    fn avg_lines_per_chunk(&self) -> Option<f64> {
        if self.chunks == 0 {
            None
        } else {
            Some(self.lines as f64 / self.chunks as f64)
        }
    }

    fn avg_uncompressed_bytes_per_chunk(&self) -> Option<f64> {
        if self.chunks == 0 {
            None
        } else {
            Some(self.uncompressed_bytes as f64 / self.chunks as f64)
        }
    }

    fn compression_mode_name(&self) -> &'static str {
        self.compression_mode_id
            .map(crate::format::compression_mode_name_from_id)
            .unwrap_or("unknown")
    }

    fn chunk_policy_name(&self) -> &'static str {
        self.chunk_policy_id
            .map(crate::format::chunk_policy_name_from_id)
            .unwrap_or("unknown")
    }
}

pub fn run_info(args: InfoStatsArgs) -> Result<()> {
    let stats = ArchiveStats::read(&args)?;
    if args.json {
        println!(
            "{{\n  \"format\": \"zlg\",\n  \"format_version\": {},\n  \"chunks\": {},\n  \"lines\": {},\n  \"uncompressed_bytes\": {},\n  \"payload_bytes\": {},\n  \"summary_bytes\": {},\n  \"directory_offset\": {},\n  \"directory_bytes\": {},\n  \"known_component_bytes\": {},\n  \"archive_bytes\": {},\n  \"compression_mode\": \"{}\",\n  \"chunk_policy\": \"{}\",\n  \"used_metadata\": {}\n}}",
            json_u16_or_null(stats.format_version),
            stats.chunks,
            stats.lines,
            stats.uncompressed_bytes,
            stats.payload_bytes,
            stats.summary_bytes,
            json_u64_or_null(stats.directory_offset),
            stats.directory_bytes,
            stats.total_component_bytes(),
            json_u64_or_null(stats.file_bytes),
            stats.compression_mode_name(),
            stats.chunk_policy_name(),
            stats.used_metadata
        );
    } else {
        println!("format: zlg");
        if let Some(version) = stats.format_version {
            println!("format-version: {version}");
        }
        if let Some(flags) = stats.flags {
            println!("flags: {flags}");
        }
        println!("chunks: {}", stats.chunks);
        println!("lines: {}", stats.lines);
        println!("uncompressed-bytes: {}", stats.uncompressed_bytes);
        println!("payload-bytes: {}", stats.payload_bytes);
        println!("summary-bytes: {}", stats.summary_bytes);
        if let Some(directory_offset) = stats.directory_offset {
            println!("directory-offset: {directory_offset}");
        }
        println!("directory-bytes: {}", stats.directory_bytes);
        println!("known-component-bytes: {}", stats.total_component_bytes());
        if let Some(file_bytes) = stats.file_bytes {
            println!("archive-bytes: {file_bytes}");
        }
        println!("compression-mode: {}", stats.compression_mode_name());
        println!("chunk-policy: {}", stats.chunk_policy_name());
        println!(
            "metadata: {}",
            if stats.used_metadata {
                "seekable"
            } else {
                "streamed"
            }
        );
    }
    Ok(())
}

pub fn run_stats(args: InfoStatsArgs) -> Result<()> {
    let stats = ArchiveStats::read(&args)?;
    if args.json {
        println!(
            "{{\n  \"format\": \"zlg\",\n  \"format_version\": {},\n  \"lines\": {},\n  \"uncompressed_bytes\": {},\n  \"chunks\": {},\n  \"payload_bytes\": {},\n  \"summary_bytes\": {},\n  \"directory_offset\": {},\n  \"directory_bytes\": {},\n  \"metadata_bytes\": {},\n  \"container_overhead_bytes\": {},\n  \"archive_bytes\": {},\n  \"compression_ratio\": {},\n  \"archive_percent_of_raw\": {},\n  \"avg_lines_per_chunk\": {},\n  \"avg_uncompressed_bytes_per_chunk\": {},\n  \"compression_mode\": \"{}\",\n  \"chunk_policy\": \"{}\",\n  \"used_metadata\": {}\n}}",
            json_u16_or_null(stats.format_version),
            stats.lines,
            stats.uncompressed_bytes,
            stats.chunks,
            stats.payload_bytes,
            stats.summary_bytes,
            json_u64_or_null(stats.directory_offset),
            stats.directory_bytes,
            stats.metadata_bytes(),
            json_u64_or_null(stats.container_overhead_bytes()),
            json_u64_or_null(stats.file_bytes),
            json_f64_or_null(stats.compression_ratio()),
            json_f64_or_null(stats.archive_percent_of_raw()),
            json_f64_or_null(stats.avg_lines_per_chunk()),
            json_f64_or_null(stats.avg_uncompressed_bytes_per_chunk()),
            stats.compression_mode_name(),
            stats.chunk_policy_name(),
            stats.used_metadata
        );
    } else {
        print_stats_report(&stats);
    }
    Ok(())
}

fn print_stats_report(stats: &ArchiveStats) {
    println!("zlg archive stats");
    println!("=================");
    println!();
    println!("Content");
    print_stat_row("Lines", format_count(stats.lines));
    print_stat_row("Uncompressed bytes", format_bytes(stats.uncompressed_bytes));
    print_stat_row("Chunks", format_count(stats.chunks));
    print_stat_row(
        "Avg lines/chunk",
        format_optional_float(stats.avg_lines_per_chunk(), 1),
    );
    print_stat_row(
        "Avg raw bytes/chunk",
        format_optional_bytes_float(stats.avg_uncompressed_bytes_per_chunk()),
    );
    println!();
    println!("Storage");
    print_stat_row("Archive bytes", format_optional_bytes(stats.file_bytes));
    print_stat_row("Payload bytes", format_bytes(stats.payload_bytes));
    print_stat_row("Summary bytes", format_bytes(stats.summary_bytes));
    print_stat_row("Directory bytes", format_bytes(stats.directory_bytes));
    print_stat_row(
        "Other overhead bytes",
        format_optional_bytes(stats.container_overhead_bytes()),
    );
    print_stat_row("Compression ratio", format_ratio(stats.compression_ratio()));
    print_stat_row(
        "Archive/raw size",
        format_percent(stats.archive_percent_of_raw()),
    );
    println!();
    println!("Format");
    print_stat_row(
        "Compression mode",
        stats.compression_mode_name().to_string(),
    );
    print_stat_row("Chunk policy", stats.chunk_policy_name().to_string());
    print_stat_row("Format version", format_optional_u16(stats.format_version));
    print_stat_row(
        "Metadata source",
        if stats.used_metadata {
            "seekable".to_string()
        } else {
            "streamed".to_string()
        },
    );
}

fn print_stat_row(label: &str, value: String) {
    println!("  {label:<28} {value}");
}

fn format_count(value: u64) -> String {
    let raw = value.to_string();
    let mut out = String::new();
    for (index, ch) in raw.chars().rev().enumerate() {
        if index > 0 && index % 3 == 0 {
            out.push(',');
        }
        out.push(ch);
    }
    out.chars().rev().collect()
}

fn format_bytes(value: u64) -> String {
    let human = if value >= 1024 * 1024 * 1024 {
        format!("{:.2} GiB", value as f64 / 1024.0 / 1024.0 / 1024.0)
    } else if value >= 1024 * 1024 {
        format!("{:.2} MiB", value as f64 / 1024.0 / 1024.0)
    } else if value >= 1024 {
        format!("{:.2} KiB", value as f64 / 1024.0)
    } else {
        "".to_string()
    };

    if human.is_empty() {
        format!("{} B", format_count(value))
    } else {
        format!("{} B ({human})", format_count(value))
    }
}

fn format_optional_bytes(value: Option<u64>) -> String {
    value
        .map(format_bytes)
        .unwrap_or_else(|| "unknown".to_string())
}

fn format_optional_bytes_float(value: Option<f64>) -> String {
    value
        .map(|value| format_bytes(value.round().max(0.0) as u64))
        .unwrap_or_else(|| "unknown".to_string())
}

fn format_optional_float(value: Option<f64>, precision: usize) -> String {
    match value {
        Some(value) => format!("{value:.precision$}"),
        None => "unknown".to_string(),
    }
}

fn format_ratio(value: Option<f64>) -> String {
    value
        .map(|value| format!("{value:.2}x"))
        .unwrap_or_else(|| "unknown".to_string())
}

fn format_percent(value: Option<f64>) -> String {
    value
        .map(|value| format!("{value:.2}%"))
        .unwrap_or_else(|| "unknown".to_string())
}

fn format_optional_u16(value: Option<u16>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "unknown".to_string())
}

pub fn run_version(args: VersionArgs) -> Result<()> {
    if args.long {
        println!("zlg {}", env!("CARGO_PKG_VERSION"));
        println!("author: Richard S. Westmoreland <dev@rswestmore.land>");
        println!("license: MIT OR Apache-2.0");
        println!("format-version: {}", zlg_format_version());
        println!(
            "default-compression-mode: {}",
            default_compression_mode_name()
        );
        println!("default-chunk-policy: {}", default_chunk_policy_name());
        println!("default-summary-type: {}", default_summary_type_name());
        println!("default-build-profile: {}", default_build_profile_name());
        println!("compression modes: none, fast, standard, best");
    } else {
        println!("zlg {}", env!("CARGO_PKG_VERSION"));
    }
    Ok(())
}

fn json_u64_or_null(value: Option<u64>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string())
}

fn json_u16_or_null(value: Option<u16>) -> String {
    value
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string())
}

fn json_f64_or_null(value: Option<f64>) -> String {
    value
        .map(|value| format!("{value:.6}"))
        .unwrap_or_else(|| "null".to_string())
}

fn write_prefix(
    writer: &mut dyn Write,
    path: Option<&PathBuf>,
    show_filename: bool,
    show_line_number: bool,
    line_number: u64,
) -> Result<()> {
    if show_filename {
        if let Some(path) = path {
            write!(writer, "{}:", path.display())?;
        }
    }
    if show_line_number {
        write!(writer, "{line_number}:")?;
    }
    Ok(())
}

fn split_lines_preserve(data: &[u8]) -> impl Iterator<Item = &[u8]> {
    data.split_inclusive(|b| *b == b'\n')
}

fn trim_trailing_newline(line: &[u8]) -> &[u8] {
    if line.ends_with(b"\n") {
        let line = &line[..line.len() - 1];
        if line.ends_with(b"\r") {
            &line[..line.len() - 1]
        } else {
            line
        }
    } else {
        line
    }
}

fn open_input(path: Option<&PathBuf>) -> Result<Box<dyn Read>> {
    match path {
        Some(path) => {
            let file = File::open(path)
                .with_context(|| format!("failed to open input {}", path.display()))?;
            Ok(Box::new(file))
        }
        None => Ok(Box::new(io::stdin().lock())),
    }
}

fn open_output(path: Option<&PathBuf>, force: bool) -> Result<Box<dyn Write>> {
    match path {
        Some(path) => {
            let mut options = OpenOptions::new();
            options.write(true);
            if force {
                options.create(true).truncate(true);
            } else {
                options.create_new(true);
            }
            let file = options.open(path).with_context(|| {
                if force {
                    format!("failed to create output {}", path.display())
                } else {
                    format!(
                        "failed to create output {} (use --force to overwrite)",
                        path.display()
                    )
                }
            })?;
            Ok(Box::new(file))
        }
        None => Ok(Box::new(io::stdout().lock())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn compression_modes_are_locked() {
        assert_eq!(CompressionMode::None.level(), None);
        assert_eq!(CompressionMode::Fast.level(), Some(3));
        assert_eq!(CompressionMode::Standard.level(), Some(6));
        assert_eq!(CompressionMode::Best.level(), Some(8));
        assert_eq!(CompressionMode::None.as_str(), "none");
        assert_eq!(CompressionMode::Fast.as_str(), "fast");
        assert_eq!(CompressionMode::Standard.as_str(), "standard");
        assert_eq!(CompressionMode::Best.as_str(), "best");
    }

    #[test]
    fn production_options_are_hidden_from_normal_compress_help() {
        let mut command = Cli::command();
        let compress = command
            .find_subcommand_mut("compress")
            .expect("compress subcommand exists");
        let help = compress.render_long_help().to_string();
        assert!(help.contains("--mode"));
        assert!(!help.contains("--level"));
        assert!(!help.contains("--preset"));
        assert!(!help.contains("--chunk-policy"));
        assert!(!help.contains("--summary-mode"));
        assert!(!help.contains("--build-profile"));
        assert!(!help.contains("--build-stats-json"));
        assert!(help.contains("--force"));
    }

    #[test]
    fn grep_help_uses_lowercase_option_policy() {
        let mut command = Cli::command();
        let grep = command
            .find_subcommand_mut("grep")
            .expect("grep subcommand exists");
        let help = grep.render_long_help().to_string();
        assert!(help.contains("-f"));
        assert!(help.contains("--fixed"));
        assert!(help.contains("-p"));
        assert!(help.contains("--pcre2"));
        assert!(help.contains("--head"));
        assert!(!help.contains("--max-count"));
        assert!(!help.contains("-P,"));
        assert!(!help.contains("-F,"));
        assert!(!help.contains("--stats-json"));
    }

    #[test]
    fn test_help_exposes_json_and_quiet_options() {
        let mut command = Cli::command();
        let test = command
            .find_subcommand_mut("test")
            .expect("test subcommand exists");
        let help = test.render_long_help().to_string();
        assert!(help.contains("--json"));
        assert!(help.contains("--quiet"));
    }

    #[test]
    fn version_long_defaults_are_available() {
        assert_eq!(zlg_format_version(), 1);
        assert_eq!(default_compression_mode_name(), "standard");
        assert_eq!(default_chunk_policy_name(), "fixed-lines8192-cap8m");
        assert_eq!(default_summary_type_name(), "mesh-bigram ZBM1 v2");
        assert_eq!(default_build_profile_name(), "combined-bitset-seen");
    }

    #[test]
    fn stats_formatting_is_screenshot_friendly() {
        assert_eq!(format_count(1_234_567), "1,234,567");
        assert_eq!(format_bytes(999), "999 B");
        assert!(format_bytes(2 * 1024 * 1024).contains("2.00 MiB"));
        assert_eq!(format_ratio(Some(3.25)), "3.25x");
        assert_eq!(format_percent(Some(12.5)), "12.50%");
    }
}
