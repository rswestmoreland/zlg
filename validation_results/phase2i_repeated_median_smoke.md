# Phase 2i repeated median bench

This report repeats the Phase 2e fast/standard benchmark and summarizes median resource metrics.

| scenario | backend | mode | operation | storage bytes | median wall | median user | median system | median cpu percent | median rss kb | matches | parity |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.804707 | 1.763905 | 0.043968 | 99.961232 | 32128.000000 | n/a | n/a |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.514777 | 1.165645 | 0.348512 | 99.885007 | 44652.000000 | n/a | n/a |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 2.359259 | 2.043518 | 0.291499 | 99.814298 | 44652.000000 | n/a | n/a |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 1.950444 | 1.079433 | 1.367229 | 127.353407 | 44652.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005014 | 0.000000 | 0.004413 | 91.463609 | 44652.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.019079 | 0.006982 | 0.010474 | 98.036870 | 44652.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.018384 | 0.004505 | 0.013516 | 98.104234 | 44652.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.673527 | 0.658900 | 0.119253 | 116.702193 | 44652.000000 | 1 | ok |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.067594 | 0.047189 | 0.023854 | 99.079726 | 44652.000000 | 1 | ok |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.019774 | 0.012496 | 0.008330 | 97.803463 | 44652.000000 | 1 | ok |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.017990 | 0.013072 | 0.004357 | 97.966720 | 44652.000000 | 1 | ok |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 2.449926 | 1.706536 | 1.334516 | 122.319831 | 44652.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.005042 | 0.000000 | 0.004609 | 92.773777 | 44652.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.010025 | 0.005881 | 0.002940 | 95.278410 | 44652.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.008456 | 0.004068 | 0.004068 | 96.147126 | 44652.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.496234 | 1.674777 | 1.415446 | 122.710112 | 44652.000000 | 5000 | ok |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.005632 | 0.000000 | 0.005126 | 91.017548 | 44652.000000 | 5000 | ok |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.026137 | 0.011035 | 0.014687 | 98.220357 | 44652.000000 | 5000 | ok |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.024285 | 0.007977 | 0.015519 | 98.545576 | 44652.000000 | 5000 | ok |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.216448 | 0.202071 | 0.011889 | 99.544491 | 19788.000000 | n/a | n/a |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.137513 | 0.102193 | 0.027358 | 98.395607 | 20928.000000 | n/a | n/a |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.226078 | 0.204569 | 0.019989 | 99.697579 | 20928.000000 | n/a | n/a |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 1.809724 | 0.981137 | 1.309849 | 126.617209 | 38436.000000 | 10 | ok |
| repeated_regex | plain | n/a | head | 15692090 | 0.006097 | 0.005424 | 0.000000 | 91.403504 | 32128.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.019236 | 0.004527 | 0.013582 | 98.365446 | 32128.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.018736 | 0.009132 | 0.009132 | 97.934860 | 32128.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.107156 | 0.130457 | 0.032671 | 152.730579 | 32128.000000 | 80000 | ok |
| repeated_regex | plain | n/a | search | 15692090 | 0.047535 | 0.035181 | 0.011727 | 98.681669 | 20928.000000 | 80000 | ok |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.054997 | 0.034981 | 0.016699 | 98.936692 | 32128.000000 | 80000 | ok |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.052914 | 0.033417 | 0.014862 | 99.083501 | 32128.000000 | 80000 | ok |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 1.900374 | 1.062536 | 1.306835 | 125.831775 | 38228.000000 | 10 | ok |
| repeated_regex | plain | n/a | tail | 15692090 | 0.005560 | 0.000000 | 0.004567 | 90.901913 | 32128.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.016816 | 0.008336 | 0.008206 | 98.114047 | 32128.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.016688 | 0.007881 | 0.008159 | 97.784813 | 32128.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 1.998219 | 1.176021 | 1.407389 | 126.200144 | 38572.000000 | 5000 | ok |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.007689 | 0.006008 | 0.000000 | 91.055456 | 32128.000000 | 5000 | ok |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.020402 | 0.007979 | 0.011969 | 97.793153 | 32128.000000 | 5000 | ok |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.019480 | 0.007881 | 0.011707 | 98.356495 | 32128.000000 | 5000 | ok |

## Median wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip median wall ratio 0.839
- needle_haystack_large build: zlg_standard vs gzip median wall ratio 1.307
- needle_haystack_large build: zlg_fast vs zlg_standard median wall ratio 0.642
- needle_haystack_large search: zlg_fast vs gzip median wall ratio 0.029
- needle_haystack_large search: zlg_standard vs gzip median wall ratio 0.027
- needle_haystack_large search: zlg_fast vs plain median wall ratio 0.293
- needle_haystack_large search: zlg_fast vs zlg_standard median wall ratio 1.099
- needle_haystack_large head: zlg_fast vs gzip median wall ratio 0.010
- needle_haystack_large head: zlg_standard vs gzip median wall ratio 0.009
- needle_haystack_large head: zlg_fast vs plain median wall ratio 3.805
- needle_haystack_large head: zlg_fast vs zlg_standard median wall ratio 1.038
- needle_haystack_large tail: zlg_fast vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_standard vs gzip median wall ratio 0.003
- needle_haystack_large tail: zlg_fast vs plain median wall ratio 1.988
- needle_haystack_large tail: zlg_fast vs zlg_standard median wall ratio 1.186
- needle_haystack_large tail_large: zlg_fast vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_standard vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_fast vs plain median wall ratio 4.641
- needle_haystack_large tail_large: zlg_fast vs zlg_standard median wall ratio 1.076
- repeated_regex build: zlg_fast vs gzip median wall ratio 0.635
- repeated_regex build: zlg_standard vs gzip median wall ratio 1.044
- repeated_regex build: zlg_fast vs zlg_standard median wall ratio 0.608
- repeated_regex search: zlg_fast vs gzip median wall ratio 0.513
- repeated_regex search: zlg_standard vs gzip median wall ratio 0.494
- repeated_regex search: zlg_fast vs plain median wall ratio 1.157
- repeated_regex search: zlg_fast vs zlg_standard median wall ratio 1.039
- repeated_regex head: zlg_fast vs gzip median wall ratio 0.011
- repeated_regex head: zlg_standard vs gzip median wall ratio 0.010
- repeated_regex head: zlg_fast vs plain median wall ratio 3.155
- repeated_regex head: zlg_fast vs zlg_standard median wall ratio 1.027
- repeated_regex tail: zlg_fast vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_standard vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_fast vs plain median wall ratio 3.024
- repeated_regex tail: zlg_fast vs zlg_standard median wall ratio 1.008
- repeated_regex tail_large: zlg_fast vs gzip median wall ratio 0.010
- repeated_regex tail_large: zlg_standard vs gzip median wall ratio 0.010
- repeated_regex tail_large: zlg_fast vs plain median wall ratio 2.653
- repeated_regex tail_large: zlg_fast vs zlg_standard median wall ratio 1.047
