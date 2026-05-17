# Phase 2e performance smoke bench

This bench compares plain logs, gzip streams, zlg fast, and zlg standard for build, search, head, and tail.
Resource metrics are captured with Linux os.wait4().

| scenario | backend | mode | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.209878 | 0.183280 | 0.023913 | 98.720735 | 19952 | n/a | n/a | 0 |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.161652 | 0.138388 | 0.020353 | 98.199395 | 21104 | n/a | n/a | 0 |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.282395 | 0.255150 | 0.023920 | 98.822426 | 21104 | n/a | n/a | 0 |
| repeated_regex | plain | n/a | search | 15692090 | 0.053438 | 0.029961 | 0.022520 | 98.210024 | 21104 | 80000 | ok | 0 |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.177911 | 0.108684 | 0.080659 | 106.425471 | 32240 | 80000 | ok | 0 |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.073795 | 0.045241 | 0.026417 | 97.104291 | 32240 | 80000 | ok | 0 |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.070084 | 0.044153 | 0.020069 | 91.636014 | 32240 | 80000 | ok | 0 |
| repeated_regex | plain | n/a | head | 15692090 | 0.007893 | 0.006753 | 0.000000 | 85.553365 | 32240 | 10 | ok | 0 |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 2.950504 | 1.207544 | 1.696116 | 98.412337 | 38804 | 10 | ok | 0 |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.027756 | 0.008200 | 0.016401 | 88.631693 | 32240 | 10 | ok | 0 |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.025094 | 0.015939 | 0.007969 | 95.272772 | 32240 | 10 | ok | 0 |
| repeated_regex | plain | n/a | tail | 15692090 | 0.018524 | 0.005774 | 0.000000 | 31.170151 | 32240 | 10 | ok | 0 |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 2.984798 | 1.313505 | 1.606312 | 97.822919 | 38500 | 10 | ok | 0 |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.031994 | 0.007147 | 0.014295 | 67.019065 | 32240 | 10 | ok | 0 |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.021375 | 0.013495 | 0.006747 | 94.697222 | 32240 | 10 | ok | 0 |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.009975 | 0.004491 | 0.004491 | 90.047667 | 32240 | 5000 | ok | 0 |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 3.370692 | 1.461119 | 1.868879 | 98.792700 | 39184 | 5000 | ok | 0 |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.020768 | 0.015961 | 0.003990 | 96.064985 | 32240 | 5000 | ok | 0 |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.022326 | 0.010782 | 0.010782 | 96.585762 | 32240 | 5000 | ok | 0 |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.834983 | 1.805128 | 0.012035 | 99.028860 | 32240 | n/a | n/a | 0 |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.678452 | 1.318708 | 0.355494 | 99.746776 | 44728 | n/a | n/a | 0 |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 3.468260 | 2.811514 | 0.388771 | 92.273501 | 44728 | n/a | n/a | 0 |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.084800 | 0.023490 | 0.050895 | 87.718453 | 44728 | 1 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.878693 | 0.652509 | 0.146957 | 90.983543 | 44728 | 1 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.021764 | 0.008487 | 0.012731 | 97.489998 | 44728 | 1 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.025611 | 0.010646 | 0.014194 | 96.989972 | 44728 | 1 | ok | 0 |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005368 | 0.000000 | 0.004687 | 87.320673 | 44728 | 10 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 2.857962 | 1.159822 | 1.705799 | 100.268002 | 44728 | 10 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.025747 | 0.019382 | 0.004845 | 94.095756 | 44728 | 10 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.026862 | 0.021533 | 0.004306 | 96.193165 | 44728 | 10 | ok | 0 |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.008286 | 0.003839 | 0.003839 | 92.665319 | 44728 | 10 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 4.114602 | 1.968220 | 1.736228 | 90.031753 | 44728 | 10 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.010428 | 0.000000 | 0.010042 | 96.298898 | 44728 | 10 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.010649 | 0.000000 | 0.009918 | 93.134360 | 44728 | 10 | ok | 0 |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.005597 | 0.000000 | 0.005122 | 91.507654 | 44728 | 5000 | ok | 0 |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.612258 | 1.665062 | 1.527287 | 122.206515 | 44728 | 5000 | ok | 0 |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.028111 | 0.019540 | 0.007705 | 96.919890 | 44728 | 5000 | ok | 0 |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.027917 | 0.015590 | 0.011693 | 97.729168 | 44728 | 5000 | ok | 0 |

## Wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip wall ratio 0.915
- needle_haystack_large build: zlg_standard vs gzip wall ratio 1.890
- needle_haystack_large build: zlg_fast vs zlg_standard wall ratio 0.484
- needle_haystack_large search: zlg_fast vs gzip wall ratio 0.025
- needle_haystack_large search: zlg_fast vs plain wall ratio 0.257
- needle_haystack_large search: zlg_standard vs gzip wall ratio 0.029
- needle_haystack_large search: zlg_standard vs plain wall ratio 0.302
- needle_haystack_large search: zlg_fast vs zlg_standard wall ratio 0.850
- needle_haystack_large head: zlg_fast vs gzip wall ratio 0.009
- needle_haystack_large head: zlg_fast vs plain wall ratio 4.796
- needle_haystack_large head: zlg_standard vs gzip wall ratio 0.009
- needle_haystack_large head: zlg_standard vs plain wall ratio 5.004
- needle_haystack_large head: zlg_fast vs zlg_standard wall ratio 0.958
- needle_haystack_large tail: zlg_fast vs gzip wall ratio 0.003
- needle_haystack_large tail: zlg_fast vs plain wall ratio 1.259
- needle_haystack_large tail: zlg_standard vs gzip wall ratio 0.003
- needle_haystack_large tail: zlg_standard vs plain wall ratio 1.285
- needle_haystack_large tail: zlg_fast vs zlg_standard wall ratio 0.979
- needle_haystack_large tail_large: zlg_fast vs gzip wall ratio 0.011
- needle_haystack_large tail_large: zlg_fast vs plain wall ratio 5.023
- needle_haystack_large tail_large: zlg_standard vs gzip wall ratio 0.011
- needle_haystack_large tail_large: zlg_standard vs plain wall ratio 4.988
- needle_haystack_large tail_large: zlg_fast vs zlg_standard wall ratio 1.007
- repeated_regex build: zlg_fast vs gzip wall ratio 0.770
- repeated_regex build: zlg_standard vs gzip wall ratio 1.346
- repeated_regex build: zlg_fast vs zlg_standard wall ratio 0.572
- repeated_regex search: zlg_fast vs gzip wall ratio 0.415
- repeated_regex search: zlg_fast vs plain wall ratio 1.381
- repeated_regex search: zlg_standard vs gzip wall ratio 0.394
- repeated_regex search: zlg_standard vs plain wall ratio 1.312
- repeated_regex search: zlg_fast vs zlg_standard wall ratio 1.053
- repeated_regex head: zlg_fast vs gzip wall ratio 0.009
- repeated_regex head: zlg_fast vs plain wall ratio 3.517
- repeated_regex head: zlg_standard vs gzip wall ratio 0.009
- repeated_regex head: zlg_standard vs plain wall ratio 3.179
- repeated_regex head: zlg_fast vs zlg_standard wall ratio 1.106
- repeated_regex tail: zlg_fast vs gzip wall ratio 0.011
- repeated_regex tail: zlg_fast vs plain wall ratio 1.727
- repeated_regex tail: zlg_standard vs gzip wall ratio 0.007
- repeated_regex tail: zlg_standard vs plain wall ratio 1.154
- repeated_regex tail: zlg_fast vs zlg_standard wall ratio 1.497
- repeated_regex tail_large: zlg_fast vs gzip wall ratio 0.006
- repeated_regex tail_large: zlg_fast vs plain wall ratio 2.082
- repeated_regex tail_large: zlg_standard vs gzip wall ratio 0.007
- repeated_regex tail_large: zlg_standard vs plain wall ratio 2.238
- repeated_regex tail_large: zlg_fast vs zlg_standard wall ratio 0.930
