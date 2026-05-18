# Phase 2m convert smoke

| Format | Helper | Status | Detail |
|---|---|---|---|
| plain | none | ok | plain input rejected; use compress |
| zst | internal | ok | covered by cargo test using internal zstd decoder |
| gz | gzip | ok | roundtrip and overwrite policy passed |
| bz2 | bzip2 | ok | roundtrip and overwrite policy passed |
| xz | xz | ok | roundtrip and overwrite policy passed |
