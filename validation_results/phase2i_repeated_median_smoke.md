# Phase 2i repeated median bench

This report repeats the Phase 2e fast/standard benchmark and summarizes median resource metrics.

| scenario | backend | mode | operation | storage bytes | median wall | median user | median system | median cpu percent | median rss kb | matches | parity |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.801872 | 1.752775 | 0.048005 | 99.957856 | 32152.000000 | n/a | n/a |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.535889 | 1.190952 | 0.343733 | 99.820108 | 44676.000000 | n/a | n/a |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 2.358001 | 2.039664 | 0.307663 | 99.968125 | 44676.000000 | n/a | n/a |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 1.811905 | 1.030083 | 1.205161 | 125.558440 | 44676.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005463 | 0.004429 | 0.000000 | 90.392828 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.019405 | 0.010171 | 0.010182 | 97.998794 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.018728 | 0.009166 | 0.009166 | 97.894434 | 44676.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.669633 | 0.653403 | 0.119201 | 115.282568 | 44676.000000 | 1 | ok |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.070832 | 0.042827 | 0.027288 | 98.889780 | 44676.000000 | 1 | ok |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.021076 | 0.011670 | 0.008223 | 97.535285 | 44676.000000 | 1 | ok |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.019907 | 0.007473 | 0.014946 | 97.526641 | 44676.000000 | 1 | ok |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 2.411239 | 1.547685 | 1.417161 | 122.959454 | 44676.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.005417 | 0.000000 | 0.004976 | 91.474590 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.010718 | 0.005130 | 0.005213 | 95.725680 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.009469 | 0.009220 | 0.000000 | 96.764353 | 44676.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.443816 | 1.551527 | 1.408301 | 121.489026 | 44676.000000 | 5000 | ok |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.005911 | 0.005501 | 0.000000 | 93.071558 | 44676.000000 | 5000 | ok |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.024433 | 0.016729 | 0.007945 | 97.953986 | 44676.000000 | 5000 | ok |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.023694 | 0.011691 | 0.011691 | 98.671413 | 44676.000000 | 5000 | ok |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.213858 | 0.204554 | 0.008123 | 99.336831 | 19864.000000 | n/a | n/a |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.127478 | 0.104351 | 0.019828 | 99.545938 | 21016.000000 | n/a | n/a |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.224367 | 0.195816 | 0.035590 | 99.742218 | 21016.000000 | n/a | n/a |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 1.758650 | 1.015520 | 1.199246 | 125.741943 | 37868.000000 | 10 | ok |
| repeated_regex | plain | n/a | head | 15692090 | 0.006059 | 0.005473 | 0.000000 | 90.323726 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.018306 | 0.008955 | 0.008870 | 98.041372 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.020284 | 0.007517 | 0.011276 | 98.556175 | 32152.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.112058 | 0.130821 | 0.041900 | 154.135429 | 32152.000000 | 80000 | ok |
| repeated_regex | plain | n/a | search | 15692090 | 0.048482 | 0.031835 | 0.015917 | 98.493866 | 21016.000000 | 80000 | ok |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.064243 | 0.031785 | 0.028065 | 98.951871 | 32152.000000 | 80000 | ok |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.055639 | 0.035749 | 0.019872 | 98.845644 | 32152.000000 | 80000 | ok |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 1.901219 | 0.997950 | 1.369123 | 124.993462 | 38436.000000 | 10 | ok |
| repeated_regex | plain | n/a | tail | 15692090 | 0.004603 | 0.000000 | 0.003983 | 91.938497 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.017429 | 0.006785 | 0.010178 | 98.068271 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.016943 | 0.008201 | 0.008276 | 97.767145 | 32152.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 1.819900 | 1.008448 | 1.238191 | 124.779036 | 38824.000000 | 5000 | ok |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.006835 | 0.003381 | 0.002926 | 91.568326 | 32152.000000 | 5000 | ok |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.021732 | 0.012636 | 0.008244 | 97.764253 | 32152.000000 | 5000 | ok |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.019678 | 0.007751 | 0.011627 | 98.476731 | 32152.000000 | 5000 | ok |

## Median wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip median wall ratio 0.852
- needle_haystack_large build: zlg_standard vs gzip median wall ratio 1.309
- needle_haystack_large build: zlg_fast vs zlg_standard median wall ratio 0.651
- needle_haystack_large search: zlg_fast vs gzip median wall ratio 0.031
- needle_haystack_large search: zlg_standard vs gzip median wall ratio 0.030
- needle_haystack_large search: zlg_fast vs plain median wall ratio 0.298
- needle_haystack_large search: zlg_fast vs zlg_standard median wall ratio 1.059
- needle_haystack_large head: zlg_fast vs gzip median wall ratio 0.011
- needle_haystack_large head: zlg_standard vs gzip median wall ratio 0.010
- needle_haystack_large head: zlg_fast vs plain median wall ratio 3.552
- needle_haystack_large head: zlg_fast vs zlg_standard median wall ratio 1.036
- needle_haystack_large tail: zlg_fast vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_standard vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_fast vs plain median wall ratio 1.979
- needle_haystack_large tail: zlg_fast vs zlg_standard median wall ratio 1.132
- needle_haystack_large tail_large: zlg_fast vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_standard vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_fast vs plain median wall ratio 4.133
- needle_haystack_large tail_large: zlg_fast vs zlg_standard median wall ratio 1.031
- repeated_regex build: zlg_fast vs gzip median wall ratio 0.596
- repeated_regex build: zlg_standard vs gzip median wall ratio 1.049
- repeated_regex build: zlg_fast vs zlg_standard median wall ratio 0.568
- repeated_regex search: zlg_fast vs gzip median wall ratio 0.573
- repeated_regex search: zlg_standard vs gzip median wall ratio 0.497
- repeated_regex search: zlg_fast vs plain median wall ratio 1.325
- repeated_regex search: zlg_fast vs zlg_standard median wall ratio 1.155
- repeated_regex head: zlg_fast vs gzip median wall ratio 0.010
- repeated_regex head: zlg_standard vs gzip median wall ratio 0.012
- repeated_regex head: zlg_fast vs plain median wall ratio 3.021
- repeated_regex head: zlg_fast vs zlg_standard median wall ratio 0.902
- repeated_regex tail: zlg_fast vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_standard vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_fast vs plain median wall ratio 3.786
- repeated_regex tail: zlg_fast vs zlg_standard median wall ratio 1.029
- repeated_regex tail_large: zlg_fast vs gzip median wall ratio 0.012
- repeated_regex tail_large: zlg_standard vs gzip median wall ratio 0.011
- repeated_regex tail_large: zlg_fast vs plain median wall ratio 3.180
- repeated_regex tail_large: zlg_fast vs zlg_standard median wall ratio 1.104
