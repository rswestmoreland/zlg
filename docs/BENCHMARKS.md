# Benchmarks

These benchmark snapshots are smoke-test results from the project validation harness. They are useful for comparing relative behavior on the same host, but they are not universal guarantees. CPU, storage, kernel, filesystem cache state, and host load all affect absolute timings.

## Build and storage

| Scenario | Backend | Archive bytes | Median build time |
|---|---:|---:|---:|
| Repeated regex log | gzip -6 | 1,233,402 | 0.212365s |
| Repeated regex log | zlg fast | 1,185,857 | 0.131995s |
| Repeated regex log | zlg standard | 967,824 | 0.242521s |
| Large needle log | gzip -6 | 14,936,213 | 1.809784s |
| Large needle log | zlg fast | 14,807,773 | 1.567921s |
| Large needle log | zlg standard | 12,945,933 | 2.369447s |

## Search

| Scenario | Backend | Median search time | Matches |
|---|---:|---:|---:|
| Repeated regex log | plain grep | 0.047857s | 80,000 |
| Repeated regex log | zgrep | 0.112281s | 80,000 |
| Repeated regex log | zlg fast | 0.053496s | 80,000 |
| Repeated regex log | zlg standard | 0.054473s | 80,000 |
| Large needle log | plain grep | 0.073980s | 1 |
| Large needle log | zgrep | 0.664595s | 1 |
| Large needle log | zlg fast | 0.020609s | 1 |
| Large needle log | zlg standard | 0.019749s | 1 |

The large needle test is where chunk skipping is most visible. zlg can reject most chunks through summaries and only decode candidates.

## Head and tail on compressed archives

| Scenario | Operation | gzip stream | zlg fast | zlg standard |
|---|---|---:|---:|---:|
| Repeated regex log | head | 1.874999s | 0.020026s | 0.020521s |
| Repeated regex log | tail | 2.066998s | 0.018484s | 0.017699s |
| Large needle log | head | 1.946713s | 0.020467s | 0.019655s |
| Large needle log | tail | 2.555441s | 0.010081s | 0.010744s |

zlg head and tail can use chunk boundaries and directory metadata instead of streaming a whole gzip file.

## Measurement notes

The benchmark scripts use Linux process resource accounting for wall time, user CPU, system CPU, CPU percent, and max RSS. See `docs/BENCHMARK_MEASUREMENT_RELIABILITY.md` for details.
