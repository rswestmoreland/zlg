use crate::chunk::{ChunkPolicy, Chunker};
use crate::format::{DecodedChunk, ZlgReader, ZlgWriter};
use crate::search::{GrepOptions, Matcher, SearchSummaryMode};

use anyhow::{anyhow, Context, Result};
use clap::{Args, Parser, Subcommand, ValueEnum};
use std::fs::File;
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
}

#[derive(Clone, Debug, ValueEnum)]
pub enum ChunkPolicyArg {
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
}

impl From<ChunkPolicyArg> for ChunkPolicy {
    fn from(value: ChunkPolicyArg) -> Self {
        match value {
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
        }
    }
}

#[derive(Clone, Debug, ValueEnum)]
pub enum SummaryModeArg {
    Bitmap,
    None,
}

impl From<SummaryModeArg> for SearchSummaryMode {
    fn from(value: SummaryModeArg) -> Self {
        match value {
            SummaryModeArg::Bitmap => SearchSummaryMode::Bitmap,
            SummaryModeArg::None => SearchSummaryMode::None,
        }
    }
}

#[derive(Debug, Args)]
pub struct CompressArgs {
    pub input: Option<PathBuf>,

    #[arg(short, long)]
    pub output: Option<PathBuf>,

    #[arg(short = 'l', long, default_value_t = 3)]
    pub level: i32,

    #[arg(long, value_enum, default_value_t = ChunkPolicyArg::HybridProgressiveCap16m)]
    pub chunk_policy: ChunkPolicyArg,

    #[arg(long, value_enum, default_value_t = SummaryModeArg::Bitmap)]
    pub summary_mode: SummaryModeArg,
}

#[derive(Debug, Args)]
pub struct CatArgs {
    pub input: Option<PathBuf>,

    #[arg(short, long)]
    pub output: Option<PathBuf>,
}

#[derive(Debug, Args)]
pub struct GrepArgs {
    pub pattern: String,

    pub input: Vec<PathBuf>,

    #[arg(short = 'F', long)]
    pub fixed_strings: bool,

    #[arg(short = 'P', long)]
    pub perl_regexp: bool,

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

    #[arg(short = 'H', long)]
    pub with_filename: bool,

    #[arg(long)]
    pub stats_json: Option<PathBuf>,
}

pub fn run_compress(args: CompressArgs) -> Result<()> {
    let input = open_input(args.input.as_ref())?;
    let output = open_output(args.output.as_ref())?;
    let policy: ChunkPolicy = args.chunk_policy.into();
    let summary_mode: SearchSummaryMode = args.summary_mode.into();

    let mut reader = BufReader::new(input);
    let writer = BufWriter::new(output);

    let mut zlg_writer = ZlgWriter::new(writer, policy.id(), args.level, summary_mode)?;
    let mut chunker = Chunker::new(policy);

    while let Some(chunk) = chunker.next_chunk(&mut reader)? {
        zlg_writer.write_chunk(&chunk)?;
    }

    zlg_writer.finish()?;
    Ok(())
}

pub fn run_cat(args: CatArgs) -> Result<()> {
    let input = open_input(args.input.as_ref())?;
    let output = open_output(args.output.as_ref())?;

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
}

impl GrepStats {
    fn to_json(&self) -> String {
        format!(
            "{{\n  \"files\": {},\n  \"chunks_total\": {},\n  \"chunks_skipped\": {},\n  \"candidate_chunks\": {},\n  \"chunks_decoded\": {},\n  \"decoded_bytes\": {},\n  \"matching_lines\": {},\n  \"selector_kind\": \"{}\",\n  \"selector_len\": {},\n  \"selector_count\": {}\n}}\n",
            self.files,
            self.chunks_total,
            self.chunks_skipped,
            self.candidate_chunks,
            self.chunks_decoded,
            self.decoded_bytes,
            self.matching_lines,
            self.selector_kind,
            self.selector_len,
            self.selector_count
        )
    }
}

pub fn run_grep(args: GrepArgs) -> Result<()> {
    if args.fixed_strings && args.perl_regexp {
        return Err(anyhow!("cannot combine -F and -P"));
    }

    let options = GrepOptions {
        fixed_strings: args.fixed_strings,
        perl_regexp: args.perl_regexp,
        only_matching: args.only_matching,
        line_number: args.line_number,
        ignore_case: args.ignore_case,
        count: args.count,
        files_with_matches: args.files_with_matches,
        invert_match: args.invert_match,
    };

    let matcher = Matcher::new(&args.pattern, options.clone())?;
    let mut stdout = BufWriter::new(io::stdout().lock());
    let mut stats = GrepStats {
        selector_kind: matcher.selector_kind(),
        selector_len: matcher.selector_len(),
        selector_count: matcher.selector_count(),
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

    while let Some(raw_chunk) = reader.next_raw_chunk()? {
        stats.chunks_total += 1;
        if !matcher.chunk_may_match(&raw_chunk.summary) {
            stats.chunks_skipped += 1;
            continue;
        }

        stats.candidate_chunks += 1;
        let decoded = raw_chunk.decode()?;
        stats.chunks_decoded += 1;
        stats.decoded_bytes += decoded.data.len() as u64;
        let chunk_matches =
            grep_decoded_chunk(&decoded, path, show_filename, matcher, options, writer)?;

        if chunk_matches > 0 {
            file_has_match = true;
            match_count += chunk_matches;
            stats.matching_lines += chunk_matches as u64;

            if options.files_with_matches {
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

fn grep_decoded_chunk(
    decoded: &DecodedChunk,
    path: Option<&PathBuf>,
    show_filename: bool,
    matcher: &Matcher,
    options: &GrepOptions,
    writer: &mut dyn Write,
) -> Result<usize> {
    let mut matches = 0usize;
    let mut line_number = decoded.header.first_line_number;

    for line in split_lines_preserve(&decoded.data) {
        let line_matches = matcher.line_matches(line)?;
        let selected = if options.invert_match {
            !line_matches
        } else {
            line_matches
        };

        if selected {
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
        }

        line_number += 1;
    }

    Ok(matches)
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

fn open_output(path: Option<&PathBuf>) -> Result<Box<dyn Write>> {
    match path {
        Some(path) => {
            let file = File::create(path)
                .with_context(|| format!("failed to create output {}", path.display()))?;
            Ok(Box::new(file))
        }
        None => Ok(Box::new(io::stdout().lock())),
    }
}
