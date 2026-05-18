# Release checklist

## Metadata

- [ ] `Cargo.toml` name is correct.
- [ ] Version is correct.
- [ ] Repository URL is correct.
- [ ] License is `MIT OR Apache-2.0`.
- [ ] Author/contact metadata is correct.
- [ ] README is public-facing.

## Validation

- [ ] `cargo fmt --check`
- [ ] `cargo check`
- [ ] `cargo test`
- [ ] `cargo clippy --all-targets --all-features -- -D warnings`
- [ ] `cargo build --release`
- [ ] smoke test commands pass
- [ ] archive hardening checks pass
- [ ] convert checks pass
- [ ] release-readiness audit passes

## Documentation

- [ ] README explains what zlg is and how to use it.
- [ ] Command reference is current.
- [ ] Install notes are current.
- [ ] Format overview is current.
- [ ] Benchmark snapshot is current.
- [ ] Man page draft is current.
- [ ] No internal planning or handoff language appears in public docs.

## Release artifact

- [ ] Release binary is built from a clean checkout.
- [ ] Artifact name is correct.
- [ ] SHA256 checksum is generated.
- [ ] Archive contains the binary and license files.
- [ ] Generated release artifacts are not committed accidentally.

## Final smoke check

```bash
zlg version
zlg compress -m fast sample.log sample.log.zlg
zlg grep -r 'error|warn|fail' sample.log.zlg
zlg grep --extract --top 'status=[a-z]+' sample.log.zlg
zlg stats sample.log.zlg
zlg test sample.log.zlg
```
