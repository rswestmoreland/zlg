mod chunk;
mod cli;
mod format;
mod search;

use anyhow::Result;
use clap::Parser;
use cli::{Cli, Commands};

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Compress(args) => cli::run_compress(args),
        Commands::Decompress(args) => cli::run_cat(args),
        Commands::Cat(args) => cli::run_cat(args),
        Commands::Grep(args) => cli::run_grep(args),
        Commands::Head(args) => cli::run_head(args),
        Commands::Tail(args) => cli::run_tail(args),
        Commands::Test(args) => cli::run_test(args),
        Commands::Info(args) => cli::run_info(args),
        Commands::Stats(args) => cli::run_stats(args),
        Commands::Version(args) => cli::run_version(args),
        Commands::Convert(args) => cli::run_convert(args),
    }
}
