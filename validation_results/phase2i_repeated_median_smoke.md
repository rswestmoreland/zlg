# Phase 2i repeated median bench

This report repeats the Phase 2e fast/standard benchmark and summarizes median resource metrics.

| scenario | backend | mode | operation | storage bytes | median wall | median user | median system | median cpu percent | median rss kb | matches | parity |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.854285 | 1.784491 | 0.048010 | 99.838861 | 32112.000000 | n/a | n/a |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.705221 | 1.390866 | 0.315316 | 99.833189 | 44640.000000 | n/a | n/a |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 2.747890 | 2.437643 | 0.315610 | 99.912898 | 44640.000000 | n/a | n/a |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 1.957472 | 1.135663 | 1.318266 | 124.611692 | 44640.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005482 | 0.000000 | 0.004713 | 88.148609 | 44640.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.020492 | 0.007962 | 0.012080 | 97.897187 | 44640.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.023174 | 0.004415 | 0.016370 | 97.325305 | 44640.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.645893 | 0.601552 | 0.151570 | 116.478632 | 44640.000000 | 1 | ok |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.067856 | 0.036069 | 0.032061 | 98.686456 | 44640.000000 | 1 | ok |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.022278 | 0.004309 | 0.016206 | 96.723668 | 44640.000000 | 1 | ok |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.021480 | 0.008047 | 0.015937 | 98.099178 | 44640.000000 | 1 | ok |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 2.568091 | 1.722680 | 1.491319 | 122.067085 | 44640.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.006689 | 0.005968 | 0.000000 | 89.224364 | 44640.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.011195 | 0.003602 | 0.007169 | 95.197666 | 44640.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.010621 | 0.004394 | 0.004394 | 95.468937 | 44640.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.467322 | 1.600621 | 1.499881 | 122.587786 | 44640.000000 | 5000 | ok |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.005952 | 0.003281 | 0.003281 | 93.166555 | 44640.000000 | 5000 | ok |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.026101 | 0.008417 | 0.016835 | 96.746848 | 44640.000000 | 5000 | ok |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.028235 | 0.019021 | 0.007973 | 98.062558 | 44640.000000 | 5000 | ok |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.222840 | 0.214009 | 0.004030 | 99.621849 | 19824.000000 | n/a | n/a |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.164084 | 0.139563 | 0.019597 | 99.607862 | 20976.000000 | n/a | n/a |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.263294 | 0.239415 | 0.023826 | 99.703669 | 20976.000000 | n/a | n/a |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 1.846197 | 1.022283 | 1.297510 | 125.172806 | 38444.000000 | 10 | ok |
| repeated_regex | plain | n/a | head | 15692090 | 0.005974 | 0.000000 | 0.005046 | 89.600605 | 32112.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.021569 | 0.012578 | 0.007981 | 97.189376 | 32112.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.022522 | 0.010930 | 0.010930 | 98.065879 | 32112.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.109028 | 0.114581 | 0.063769 | 150.865913 | 32112.000000 | 80000 | ok |
| repeated_regex | plain | n/a | search | 15692090 | 0.051330 | 0.029968 | 0.018730 | 98.609513 | 20976.000000 | 80000 | ok |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.060145 | 0.032512 | 0.031746 | 98.990666 | 32112.000000 | 80000 | ok |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.056127 | 0.035748 | 0.019860 | 99.060962 | 32112.000000 | 80000 | ok |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 2.077944 | 1.183516 | 1.351610 | 124.911976 | 38068.000000 | 10 | ok |
| repeated_regex | plain | n/a | tail | 15692090 | 0.005874 | 0.000000 | 0.005133 | 87.378690 | 32112.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.017201 | 0.008280 | 0.012097 | 96.275532 | 32112.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.016941 | 0.008067 | 0.008211 | 96.652679 | 32112.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 2.060430 | 1.163550 | 1.403430 | 124.576466 | 38552.000000 | 5000 | ok |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.006946 | 0.003150 | 0.003916 | 90.701054 | 32112.000000 | 5000 | ok |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.020480 | 0.011885 | 0.007923 | 96.720729 | 32112.000000 | 5000 | ok |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.019568 | 0.004707 | 0.014121 | 97.986943 | 32112.000000 | 5000 | ok |

## Median wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip median wall ratio 0.920
- needle_haystack_large build: zlg_standard vs gzip median wall ratio 1.482
- needle_haystack_large build: zlg_fast vs zlg_standard median wall ratio 0.621
- needle_haystack_large search: zlg_fast vs gzip median wall ratio 0.034
- needle_haystack_large search: zlg_standard vs gzip median wall ratio 0.033
- needle_haystack_large search: zlg_fast vs plain median wall ratio 0.328
- needle_haystack_large search: zlg_fast vs zlg_standard median wall ratio 1.037
- needle_haystack_large head: zlg_fast vs gzip median wall ratio 0.010
- needle_haystack_large head: zlg_standard vs gzip median wall ratio 0.012
- needle_haystack_large head: zlg_fast vs plain median wall ratio 3.738
- needle_haystack_large head: zlg_fast vs zlg_standard median wall ratio 0.884
- needle_haystack_large tail: zlg_fast vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_standard vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_fast vs plain median wall ratio 1.674
- needle_haystack_large tail: zlg_fast vs zlg_standard median wall ratio 1.054
- needle_haystack_large tail_large: zlg_fast vs gzip median wall ratio 0.011
- needle_haystack_large tail_large: zlg_standard vs gzip median wall ratio 0.011
- needle_haystack_large tail_large: zlg_fast vs plain median wall ratio 4.385
- needle_haystack_large tail_large: zlg_fast vs zlg_standard median wall ratio 0.924
- repeated_regex build: zlg_fast vs gzip median wall ratio 0.736
- repeated_regex build: zlg_standard vs gzip median wall ratio 1.182
- repeated_regex build: zlg_fast vs zlg_standard median wall ratio 0.623
- repeated_regex search: zlg_fast vs gzip median wall ratio 0.552
- repeated_regex search: zlg_standard vs gzip median wall ratio 0.515
- repeated_regex search: zlg_fast vs plain median wall ratio 1.172
- repeated_regex search: zlg_fast vs zlg_standard median wall ratio 1.072
- repeated_regex head: zlg_fast vs gzip median wall ratio 0.012
- repeated_regex head: zlg_standard vs gzip median wall ratio 0.012
- repeated_regex head: zlg_fast vs plain median wall ratio 3.610
- repeated_regex head: zlg_fast vs zlg_standard median wall ratio 0.958
- repeated_regex tail: zlg_fast vs gzip median wall ratio 0.008
- repeated_regex tail: zlg_standard vs gzip median wall ratio 0.008
- repeated_regex tail: zlg_fast vs plain median wall ratio 2.928
- repeated_regex tail: zlg_fast vs zlg_standard median wall ratio 1.015
- repeated_regex tail_large: zlg_fast vs gzip median wall ratio 0.010
- repeated_regex tail_large: zlg_standard vs gzip median wall ratio 0.009
- repeated_regex tail_large: zlg_fast vs plain median wall ratio 2.948
- repeated_regex tail_large: zlg_fast vs zlg_standard median wall ratio 1.047
