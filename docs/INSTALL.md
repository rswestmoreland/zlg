# Installing zlg

zlg is currently pre-1.0 and the `.zlg` file format remains experimental.

## Build from source

```bash
cargo build --release
```

The release binary is expected at:

```text
target/release/zlg
```

## Local install

Example local install:

```bash
install -Dm755 target/release/zlg "$HOME/.local/bin/zlg"
```

Confirm it is available:

```bash
zlg version
zlg version --long
```

## System install

Example system install:

```bash
sudo install -Dm755 target/release/zlg /usr/local/bin/zlg
```

Optional man page install after a release package includes it:

```bash
sudo install -Dm644 docs/man/zlg.1 /usr/local/share/man/man1/zlg.1
sudo mandb || true
```

## Uninstall

For local install:

```bash
rm -f "$HOME/.local/bin/zlg"
```

For system install:

```bash
sudo rm -f /usr/local/bin/zlg
sudo rm -f /usr/local/share/man/man1/zlg.1
```

## Convert helper requirements

`zlg convert` uses internal zstd support for `.zst` input. It uses helper programs for common Linux compressed files:

```text
.gz   gzip
.bz2  bzip2
.xz   xz
```

If a helper is missing, zlg reports that the format is unsupported in the current environment.

## Release artifact layout

The intended release tarball layout is:

```text
zlg-<version>-linux-x86_64/
  zlg
  README.md
  LICENSE
  LICENSE-MIT
  LICENSE-APACHE
  docs/COMMAND_REFERENCE.md
  docs/INSTALL.md
  docs/man/zlg.1
```

Generated tarballs and checksums must not be committed to the repository.
