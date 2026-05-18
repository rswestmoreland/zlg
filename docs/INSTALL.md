# Install

## Build from source

```bash
git clone https://github.com/rswestmoreland/zlg.git
cd zlg
cargo build --release
install -Dm755 target/release/zlg "$HOME/.local/bin/zlg"
```

Make sure `$HOME/.local/bin` is in your `PATH`.

```bash
zlg version
zlg version --long
```

## Helper commands for convert

`zlg convert` uses internal zstd support for `.zst` files. Other common Linux compressed formats use helper commands from `PATH`:

```text
.gz   gzip -dc
.bz2  bzip2 -dc
.xz   xz -dc
```

If a helper is missing, zlg reports that the format is unsupported in the current environment.

## Uninstall

```bash
rm -f "$HOME/.local/bin/zlg"
```
