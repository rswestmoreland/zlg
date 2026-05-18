# Shell Completions

Shell completion generation is not implemented yet.

The Phase 3 recommendation is to defer completions until after the command surface has stabilized through the first release candidate. zlg uses clap, so a future implementation can either:

- generate completions at runtime through a command such as `zlg completions bash`, or
- generate completion files during packaging.

Possible future shells:

```text
bash
zsh
fish
powershell
elvish
```

Guidelines for a future completion command:

- Use a subcommand, not hidden install-time behavior.
- Do not add shell-specific runtime dependencies.
- Document where users should install each shell's completion file.
- Keep generated completion files out of the source tree unless intentionally packaged.
