# Phase 1l final-stack streamlining benchmark

This pass keeps the final stack fixed and compares the four edge reserve options.

## Reserve strategy rows

| corpus | mode | profile | wall_s | cpu_s | rss_kb | output_bytes | edge_capacity_after | unique_edges | candidate_edges | roundtrip | matches_current |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| high_dup | reserve-current | combined-bitset-seen | 0.44278241099527804 | 0.437267 | 9928 | 1857474 | 2431226 | 84266 | 19673747 | true | true |
| high_dup | reserve-none | combined-bitset-seen-reserve-none | 0.4208770139957778 | 0.417097 | 9928 | 1857474 | 8192 | 84266 | 19673747 | true | true |
| high_dup | reserve-capped | combined-bitset-seen-reserve-capped | 0.4580194769951049 | 0.456779 | 9984 | 1857474 | 75975 | 84266 | 19673747 | true | true |
| high_dup | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.4413959209996392 | 0.437266 | 9968 | 1857474 | 16384 | 84266 | 19673747 | true | true |
| high_cardinality | reserve-current | combined-bitset-seen | 0.5363112080012797 | 0.534338 | 10184 | 3731403 | 2672936 | 91010 | 21142595 | true | true |
| high_cardinality | reserve-none | combined-bitset-seen-reserve-none | 0.5145834360009758 | 0.508625 | 10252 | 3731403 | 8192 | 91010 | 21142595 | true | true |
| high_cardinality | reserve-capped | combined-bitset-seen-reserve-capped | 0.5573611729996628 | 0.551692 | 10336 | 3731403 | 83529 | 91010 | 21142595 | true | true |
| high_cardinality | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.5050777600044967 | 0.497190 | 10144 | 3731403 | 16384 | 91010 | 21142595 | true | true |
| unicode | reserve-current | combined-bitset-seen | 0.13089345199841773 | 0.126087 | 9584 | 81685 | 1905720 | 5776 | 3822308 | true | true |
| unicode | reserve-none | combined-bitset-seen-reserve-none | 0.1356114689988317 | 0.132140 | 9564 | 81685 | 2048 | 5776 | 3822308 | true | true |
| unicode | reserve-capped | combined-bitset-seen-reserve-capped | 0.11597763300233055 | 0.113622 | 9444 | 81685 | 59553 | 5776 | 3822308 | true | true |
| unicode | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.11991198400210124 | 0.118871 | 9556 | 81685 | 16384 | 5776 | 3822308 | true | true |
| binaryish | reserve-current | combined-bitset-seen | 0.07122622300084913 | 0.065460 | 10276 | 477802 | 434136 | 240874 | 276504 | true | true |
| binaryish | reserve-none | combined-bitset-seen-reserve-none | 0.06649769200157607 | 0.062025 | 10060 | 477802 | 262144 | 240874 | 276504 | true | true |
| binaryish | reserve-capped | combined-bitset-seen-reserve-capped | 0.0785836159993778 | 0.072694 | 10348 | 477802 | 262144 | 240874 | 276504 | true | true |
| binaryish | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.06599872699734988 | 0.063653 | 10232 | 477802 | 262144 | 240874 | 276504 | true | true |
| realistic_mixed_log | reserve-current | combined-bitset-seen | 0.5120074829974328 | 0.509368 | 10240 | 3240403 | 2741512 | 100008 | 21808700 | true | true |
| realistic_mixed_log | reserve-none | combined-bitset-seen-reserve-none | 0.609160886000609 | 0.604289 | 10132 | 3240403 | 8192 | 100008 | 21808700 | true | true |
| realistic_mixed_log | reserve-capped | combined-bitset-seen-reserve-capped | 0.5737168229970848 | 0.569635 | 10176 | 3240403 | 85672 | 100008 | 21808700 | true | true |
| realistic_mixed_log | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.6825711240016972 | 0.679922 | 10140 | 3240403 | 16384 | 100008 | 21808700 | true | true |
| long_line_log | reserve-current | combined-bitset-seen | 0.7840810289999354 | 0.780614 | 17136 | 1834252 | 16776924 | 35964 | 45277584 | true | true |
| long_line_log | reserve-none | combined-bitset-seen-reserve-none | 0.7474479910015361 | 0.743600 | 17204 | 1834252 | 8192 | 35964 | 45277584 | true | true |
| long_line_log | reserve-capped | combined-bitset-seen-reserve-capped | 0.729602163999516 | 0.726511 | 17196 | 1834252 | 262144 | 35964 | 45277584 | true | true |
| long_line_log | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.7504889670017292 | 0.748335 | 17256 | 1834252 | 16384 | 35964 | 45277584 | true | true |
| short_line_log | reserve-current | combined-bitset-seen | 0.35255115600011777 | 0.349205 | 9136 | 1959223 | 772700 | 54348 | 11792701 | true | true |
| short_line_log | reserve-none | combined-bitset-seen-reserve-none | 0.384985102005885 | 0.381794 | 9020 | 1959223 | 2048 | 54348 | 11792701 | true | true |
| short_line_log | reserve-capped | combined-bitset-seen-reserve-capped | 0.376475280005252 | 0.373852 | 9024 | 1959223 | 24146 | 54348 | 11792701 | true | true |
| short_line_log | reserve-prev-unique | combined-bitset-seen-reserve-prev-unique | 0.4308151599980192 | 0.424679 | 9016 | 1959223 | 16384 | 54348 | 11792701 | true | true |

## Notes

- Production default remains combined-bitset-seen unless a reserve option is promoted after validation.
- All reserve variants must produce byte-identical zlg output to the current reserve path.
