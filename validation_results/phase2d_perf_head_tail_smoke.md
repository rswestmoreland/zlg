# Phase 2d performance smoke bench

This bench compares plain logs, gzip streams, and zlg archives for search, head, and tail.
Resource metrics are captured with Linux os.wait4().

| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| repeated_regex | plain_grep | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| repeated_regex | gzip_zgrep | build | 1233402 | 0.210082 | 0.200817 | 0.008034 | 99.413845 | 19764 | n/a | n/a | 0 |
| repeated_regex | zlg | build | 967824 | 0.212531 | 0.192083 | 0.020011 | 99.794445 | 20924 | n/a | n/a | 0 |
| repeated_regex | plain_grep | search | 15692090 | 0.045717 | 0.040931 | 0.004095 | 98.488592 | 20924 | 80000 | ok | 0 |
| repeated_regex | gzip_zgrep | search | 1233402 | 0.129397 | 0.105306 | 0.077478 | 141.257781 | 32060 | 80000 | ok | 0 |
| repeated_regex | zlg | search | 967824 | 0.047917 | 0.031537 | 0.015768 | 98.722637 | 32060 | 80000 | ok | 0 |
| repeated_regex | plain_grep | head | 15692090 | 0.005279 | 0.004767 | 0.000000 | 90.297482 | 32060 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | head | 1233402 | 1.618099 | 0.864130 | 1.158098 | 124.975561 | 38544 | 10 | ok | 0 |
| repeated_regex | zlg | head | 967824 | 0.018556 | 0.009079 | 0.009079 | 97.855067 | 32060 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail | 15692090 | 0.004690 | 0.004177 | 0.000000 | 89.069050 | 32060 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | tail | 1233402 | 1.751855 | 0.998360 | 1.170928 | 123.828062 | 37996 | 10 | ok | 0 |
| repeated_regex | zlg | tail | 967824 | 0.017064 | 0.008369 | 0.008369 | 98.089045 | 32060 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail_large | 15692090 | 0.005787 | 0.000000 | 0.005341 | 92.300248 | 32060 | 5000 | ok | 0 |
| repeated_regex | gzip_zgrep | tail_large | 1233402 | 1.762780 | 1.028337 | 1.165917 | 124.476922 | 39428 | 5000 | ok | 0 |
| repeated_regex | zlg | tail_large | 967824 | 0.020969 | 0.020532 | 0.000000 | 97.915014 | 32060 | 5000 | ok | 0 |
| needle_haystack_large | plain_grep | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| needle_haystack_large | gzip_zgrep | build | 14936213 | 1.800395 | 1.758334 | 0.039964 | 99.883515 | 32060 | n/a | n/a | 0 |
| needle_haystack_large | zlg | build | 12945933 | 2.312940 | 2.029351 | 0.279647 | 99.829586 | 44580 | n/a | n/a | 0 |
| needle_haystack_large | plain_grep | search | 126450608 | 0.069910 | 0.052733 | 0.016212 | 98.619599 | 44580 | 1 | ok | 0 |
| needle_haystack_large | gzip_zgrep | search | 14936213 | 0.722977 | 0.685410 | 0.136161 | 113.637233 | 44580 | 1 | ok | 0 |
| needle_haystack_large | zlg | search | 12945933 | 0.019341 | 0.011455 | 0.007637 | 98.714203 | 44580 | 1 | ok | 0 |
| needle_haystack_large | plain_grep | head | 126450608 | 0.005030 | 0.000000 | 0.004538 | 90.210599 | 44580 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | head | 14936213 | 1.658275 | 0.934149 | 1.139993 | 125.078291 | 44580 | 10 | ok | 0 |
| needle_haystack_large | zlg | head | 12945933 | 0.017985 | 0.000000 | 0.017687 | 98.340647 | 44580 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail | 126450608 | 0.004339 | 0.000000 | 0.003838 | 88.456823 | 44580 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail | 14936213 | 2.409857 | 1.563225 | 1.338886 | 120.426682 | 44580 | 10 | ok | 0 |
| needle_haystack_large | zlg | tail | 12945933 | 0.009161 | 0.000000 | 0.008801 | 96.075531 | 44580 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail_large | 126450608 | 0.005297 | 0.004967 | 0.000000 | 93.775157 | 44580 | 5000 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail_large | 14936213 | 2.466979 | 1.534126 | 1.477632 | 122.082833 | 44580 | 5000 | ok | 0 |
| needle_haystack_large | zlg | tail_large | 12945933 | 0.026120 | 0.008522 | 0.017045 | 97.884321 | 44580 | 5000 | ok | 0 |

## Wall-time ratios

- needle_haystack_large search: zlg vs gzip/zgrep wall ratio 0.027
- needle_haystack_large search: zlg vs plain wall ratio 0.277
- needle_haystack_large head: zlg vs gzip/zgrep wall ratio 0.011
- needle_haystack_large head: zlg vs plain wall ratio 3.576
- needle_haystack_large tail: zlg vs gzip/zgrep wall ratio 0.004
- needle_haystack_large tail: zlg vs plain wall ratio 2.111
- needle_haystack_large tail_large: zlg vs gzip/zgrep wall ratio 0.011
- needle_haystack_large tail_large: zlg vs plain wall ratio 4.931
- repeated_regex search: zlg vs gzip/zgrep wall ratio 0.370
- repeated_regex search: zlg vs plain wall ratio 1.048
- repeated_regex head: zlg vs gzip/zgrep wall ratio 0.011
- repeated_regex head: zlg vs plain wall ratio 3.515
- repeated_regex tail: zlg vs gzip/zgrep wall ratio 0.010
- repeated_regex tail: zlg vs plain wall ratio 3.638
- repeated_regex tail_large: zlg vs gzip/zgrep wall ratio 0.012
- repeated_regex tail_large: zlg vs plain wall ratio 3.623
