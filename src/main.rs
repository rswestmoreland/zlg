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
    }
}
