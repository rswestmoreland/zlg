# Phase 2e performance smoke bench

This bench compares plain logs, gzip streams, zlg fast, and zlg standard for build, search, head, and tail.
Resource metrics are captured with Linux os.wait4().

| scenario | backend | mode | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.239082 | 0.222359 | 0.015884 | 99.648967 | 19764 | n/a | n/a | 0 |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.145833 | 0.108856 | 0.036285 | 99.525674 | 20920 | n/a | n/a | 0 |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.216826 | 0.200316 | 0.016025 | 99.776503 | 20920 | n/a | n/a | 0 |
| repeated_regex | plain | n/a | search | 15692090 | 0.046821 | 0.037678 | 0.008373 | 98.354802 | 20920 | 80000 | ok | 0 |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.108741 | 0.110373 | 0.058327 | 155.138821 | 32056 | 80000 | ok | 0 |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.055909 | 0.039548 | 0.015819 | 99.030367 | 32056 | 80000 | ok | 0 |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.056004 | 0.027645 | 0.027633 | 98.703354 | 32056 | 80000 | ok | 0 |
| repeated_regex | plain | n/a | head | 15692090 | 0.006154 | 0.005564 | 0.000000 | 90.416736 | 32056 | 10 | ok | 0 |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 1.858274 | 1.126420 | 1.231566 | 126.891224 | 38812 | 10 | ok | 0 |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.018754 | 0.014705 | 0.003676 | 98.010317 | 32056 | 10 | ok | 0 |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.021549 | 0.008450 | 0.012676 | 98.035189 | 32056 | 10 | ok | 0 |
| repeated_regex | plain | n/a | tail | 15692090 | 0.005179 | 0.000000 | 0.004801 | 92.706914 | 32056 | 10 | ok | 0 |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 1.816902 | 1.030571 | 1.248952 | 125.462046 | 37832 | 10 | ok | 0 |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.016281 | 0.007907 | 0.007907 | 97.131727 | 32056 | 10 | ok | 0 |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.018113 | 0.014092 | 0.003523 | 97.251834 | 32056 | 10 | ok | 0 |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.007267 | 0.000000 | 0.006490 | 89.303811 | 32056 | 5000 | ok | 0 |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 1.984780 | 1.053826 | 1.445754 | 125.937379 | 38208 | 5000 | ok | 0 |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.020283 | 0.014352 | 0.004784 | 94.343306 | 32056 | 5000 | ok | 0 |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.019671 | 0.011565 | 0.007710 | 97.987567 | 32056 | 5000 | ok | 0 |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.809505 | 1.764602 | 0.043999 | 99.950046 | 32056 | n/a | n/a | 0 |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.506516 | 1.245603 | 0.260342 | 99.962129 | 44452 | n/a | n/a | 0 |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 2.359425 | 2.040358 | 0.310829 | 99.650865 | 44452 | n/a | n/a | 0 |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.069671 | 0.034462 | 0.034448 | 98.908317 | 44452 | 1 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.701428 | 0.720379 | 0.135866 | 122.071668 | 44452 | 1 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.020267 | 0.011999 | 0.007999 | 98.673795 | 44452 | 1 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.019175 | 0.007492 | 0.011238 | 97.680309 | 44452 | 1 | ok | 0 |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005630 | 0.000000 | 0.005050 | 89.698922 | 44452 | 10 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 1.748987 | 1.031144 | 1.178837 | 126.357738 | 44452 | 10 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.019103 | 0.014954 | 0.003738 | 97.846073 | 44452 | 10 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.019087 | 0.015069 | 0.003767 | 98.684178 | 44452 | 10 | ok | 0 |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.004598 | 0.000000 | 0.004140 | 90.036347 | 44452 | 10 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 2.364180 | 1.563307 | 1.321107 | 122.004829 | 44452 | 10 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.010438 | 0.003288 | 0.006576 | 94.502827 | 44452 | 10 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.009072 | 0.000000 | 0.008827 | 97.302600 | 44452 | 10 | ok | 0 |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.005227 | 0.004802 | 0.000000 | 91.861145 | 44452 | 5000 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.539592 | 1.655913 | 1.440079 | 121.909009 | 44452 | 5000 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.024160 | 0.018835 | 0.004708 | 97.446724 | 44452 | 5000 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.024356 | 0.011947 | 0.011947 | 98.101582 | 44452 | 5000 | ok | 0 |

## Wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip wall ratio 0.833
- needle_haystack_large build: zlg_standard vs gzip wall ratio 1.304
- needle_haystack_large build: zlg_fast vs zlg_standard wall ratio 0.639
- needle_haystack_large search: zlg_fast vs gzip wall ratio 0.029
- needle_haystack_large search: zlg_fast vs plain wall ratio 0.291
- needle_haystack_large search: zlg_standard vs gzip wall ratio 0.027
- needle_haystack_large search: zlg_standard vs plain wall ratio 0.275
- needle_haystack_large search: zlg_fast vs zlg_standard wall ratio 1.057
- needle_haystack_large head: zlg_fast vs gzip wall ratio 0.011
- needle_haystack_large head: zlg_fast vs plain wall ratio 3.393
- needle_haystack_large head: zlg_standard vs gzip wall ratio 0.011
- needle_haystack_large head: zlg_standard vs plain wall ratio 3.390
- needle_haystack_large head: zlg_fast vs zlg_standard wall ratio 1.001
- needle_haystack_large tail: zlg_fast vs gzip wall ratio 0.004
- needle_haystack_large tail: zlg_fast vs plain wall ratio 2.270
- needle_haystack_large tail: zlg_standard vs gzip wall ratio 0.004
- needle_haystack_large tail: zlg_standard vs plain wall ratio 1.973
- needle_haystack_large tail: zlg_fast vs zlg_standard wall ratio 1.151
- needle_haystack_large tail_large: zlg_fast vs gzip wall ratio 0.010
- needle_haystack_large tail_large: zlg_fast vs plain wall ratio 4.622
- needle_haystack_large tail_large: zlg_standard vs gzip wall ratio 0.010
- needle_haystack_large tail_large: zlg_standard vs plain wall ratio 4.660
- needle_haystack_large tail_large: zlg_fast vs zlg_standard wall ratio 0.992
- repeated_regex build: zlg_fast vs gzip wall ratio 0.610
- repeated_regex build: zlg_standard vs gzip wall ratio 0.907
- repeated_regex build: zlg_fast vs zlg_standard wall ratio 0.673
- repeated_regex search: zlg_fast vs gzip wall ratio 0.514
- repeated_regex search: zlg_fast vs plain wall ratio 1.194
- repeated_regex search: zlg_standard vs gzip wall ratio 0.515
- repeated_regex search: zlg_standard vs plain wall ratio 1.196
- repeated_regex search: zlg_fast vs zlg_standard wall ratio 0.998
- repeated_regex head: zlg_fast vs gzip wall ratio 0.010
- repeated_regex head: zlg_fast vs plain wall ratio 3.047
- repeated_regex head: zlg_standard vs gzip wall ratio 0.012
- repeated_regex head: zlg_standard vs plain wall ratio 3.502
- repeated_regex head: zlg_fast vs zlg_standard wall ratio 0.870
- repeated_regex tail: zlg_fast vs gzip wall ratio 0.009
- repeated_regex tail: zlg_fast vs plain wall ratio 3.144
- repeated_regex tail: zlg_standard vs gzip wall ratio 0.010
- repeated_regex tail: zlg_standard vs plain wall ratio 3.497
- repeated_regex tail: zlg_fast vs zlg_standard wall ratio 0.899
- repeated_regex tail_large: zlg_fast vs gzip wall ratio 0.010
- repeated_regex tail_large: zlg_fast vs plain wall ratio 2.791
- repeated_regex tail_large: zlg_standard vs gzip wall ratio 0.010
- repeated_regex tail_large: zlg_standard vs plain wall ratio 2.707
- repeated_regex tail_large: zlg_fast vs zlg_standard wall ratio 1.031
