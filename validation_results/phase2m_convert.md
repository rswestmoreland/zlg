# Phase 2m convert smoke

| Format | Helper | Status | Detail |
|---|---|---|---|
| plain | none | ok | plain input rejected; use compress |
| zst | zstd | skipped | zstd not found in PATH |
| gz | gzip | ok | roundtrip and overwrite policy passed |
| bz2 | bzip2 | ok | roundtrip and overwrite policy passed |
| xz | xz | ok | roundtrip and overwrite policy passed |
