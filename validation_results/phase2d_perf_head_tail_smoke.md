# Phase 2d performance smoke bench

This bench compares plain logs, gzip streams, and zlg archives for search, head, and tail.
Resource metrics are captured with Linux os.wait4().

| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| repeated_regex | plain_grep | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| repeated_regex | gzip_zgrep | build | 1233402 | 0.215752 | 0.205230 | 0.008048 | 98.853144 | 19832 | n/a | n/a | 0 |
| repeated_regex | zlg | build | 967824 | 0.259927 | 0.223215 | 0.035873 | 99.677029 | 21040 | n/a | n/a | 0 |
| repeated_regex | plain_grep | search | 15692090 | 0.049416 | 0.028251 | 0.020179 | 98.004368 | 21040 | 80000 | ok | 0 |
| repeated_regex | gzip_zgrep | search | 1233402 | 0.124819 | 0.116808 | 0.066208 | 146.625429 | 32176 | 80000 | ok | 0 |
| repeated_regex | zlg | search | 967824 | 0.054570 | 0.041235 | 0.011246 | 96.171482 | 32176 | 80000 | ok | 0 |
| repeated_regex | plain_grep | head | 15692090 | 0.007063 | 0.000000 | 0.006439 | 91.164143 | 32176 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | head | 1233402 | 1.791742 | 1.009043 | 1.232048 | 125.078869 | 39148 | 10 | ok | 0 |
| repeated_regex | zlg | head | 967824 | 0.018159 | 0.013300 | 0.004433 | 97.654190 | 32176 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail | 15692090 | 0.005474 | 0.002449 | 0.002449 | 89.472365 | 32176 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | tail | 1233402 | 1.919256 | 1.103421 | 1.301939 | 125.327734 | 37412 | 10 | ok | 0 |
| repeated_regex | zlg | tail | 967824 | 0.018385 | 0.008858 | 0.008858 | 96.362957 | 32176 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail_large | 15692090 | 0.006517 | 0.000000 | 0.005887 | 90.330092 | 32176 | 5000 | ok | 0 |
| repeated_regex | gzip_zgrep | tail_large | 1233402 | 1.930657 | 1.197207 | 1.231016 | 125.771828 | 38568 | 5000 | ok | 0 |
| repeated_regex | zlg | tail_large | 967824 | 0.018706 | 0.013679 | 0.004559 | 97.498509 | 32176 | 5000 | ok | 0 |
| needle_haystack_large | plain_grep | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| needle_haystack_large | gzip_zgrep | build | 14936213 | 1.778245 | 1.724682 | 0.051906 | 99.906823 | 32176 | n/a | n/a | 0 |
| needle_haystack_large | zlg | build | 12945933 | 2.873492 | 2.537692 | 0.332279 | 99.877451 | 44700 | n/a | n/a | 0 |
| needle_haystack_large | plain_grep | search | 126450608 | 0.071809 | 0.035338 | 0.035338 | 98.422734 | 44700 | 1 | ok | 0 |
| needle_haystack_large | gzip_zgrep | search | 14936213 | 0.683221 | 0.590003 | 0.210979 | 117.236231 | 44700 | 1 | ok | 0 |
| needle_haystack_large | zlg | search | 12945933 | 0.020674 | 0.016252 | 0.004038 | 98.143796 | 44700 | 1 | ok | 0 |
| needle_haystack_large | plain_grep | head | 126450608 | 0.006074 | 0.000000 | 0.005672 | 93.381949 | 44700 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | head | 14936213 | 1.880966 | 1.063854 | 1.302028 | 125.780163 | 44700 | 10 | ok | 0 |
| needle_haystack_large | zlg | head | 12945933 | 0.019099 | 0.007430 | 0.011145 | 97.257302 | 44700 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail | 126450608 | 0.004942 | 0.004505 | 0.000000 | 91.159658 | 44700 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail | 14936213 | 2.468057 | 1.574335 | 1.448728 | 122.487587 | 44700 | 10 | ok | 0 |
| needle_haystack_large | zlg | tail | 12945933 | 0.010218 | 0.003278 | 0.006557 | 96.251581 | 44700 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail_large | 126450608 | 0.005569 | 0.000000 | 0.005164 | 92.725301 | 44700 | 5000 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail_large | 14936213 | 2.466093 | 1.600727 | 1.423617 | 122.637077 | 44700 | 5000 | ok | 0 |
| needle_haystack_large | zlg | tail_large | 12945933 | 0.024676 | 0.012086 | 0.012086 | 97.957299 | 44700 | 5000 | ok | 0 |

## Wall-time ratios

- needle_haystack_large search: zlg vs gzip/zgrep wall ratio 0.030
- needle_haystack_large search: zlg vs plain wall ratio 0.288
- needle_haystack_large head: zlg vs gzip/zgrep wall ratio 0.010
- needle_haystack_large head: zlg vs plain wall ratio 3.144
- needle_haystack_large tail: zlg vs gzip/zgrep wall ratio 0.004
- needle_haystack_large tail: zlg vs plain wall ratio 2.068
- needle_haystack_large tail_large: zlg vs gzip/zgrep wall ratio 0.010
- needle_haystack_large tail_large: zlg vs plain wall ratio 4.431
- repeated_regex search: zlg vs gzip/zgrep wall ratio 0.437
- repeated_regex search: zlg vs plain wall ratio 1.104
- repeated_regex head: zlg vs gzip/zgrep wall ratio 0.010
- repeated_regex head: zlg vs plain wall ratio 2.571
- repeated_regex tail: zlg vs gzip/zgrep wall ratio 0.010
- repeated_regex tail: zlg vs plain wall ratio 3.359
- repeated_regex tail_large: zlg vs gzip/zgrep wall ratio 0.010
- repeated_regex tail_large: zlg vs plain wall ratio 2.870
