# Phase 2i repeated median bench

This report repeats the Phase 2e fast/standard benchmark and summarizes median resource metrics.

| scenario | backend | mode | operation | storage bytes | median wall | median user | median system | median cpu percent | median rss kb | matches | parity |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| needle_haystack_large | gzip | gzip-6 | build | 14936213 | 1.809784 | 1.773151 | 0.044043 | 99.964082 | 32152.000000 | n/a | n/a |
| needle_haystack_large | plain | n/a | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| needle_haystack_large | zlg_fast | fast | build | 14807773 | 1.567921 | 1.263149 | 0.323824 | 99.962194 | 44676.000000 | n/a | n/a |
| needle_haystack_large | zlg_standard | standard | build | 12945933 | 2.369447 | 2.044591 | 0.304052 | 99.972992 | 44676.000000 | n/a | n/a |
| needle_haystack_large | gzip | gzip-6 | head | 14936213 | 1.946713 | 1.141806 | 1.306620 | 125.884406 | 44676.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | head | 126450608 | 0.005494 | 0.004823 | 0.000000 | 91.399814 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | head | 14807773 | 0.020467 | 0.007947 | 0.011920 | 97.942911 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | head | 12945933 | 0.019655 | 0.007693 | 0.011480 | 98.032960 | 44676.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | search | 14936213 | 0.664595 | 0.661235 | 0.120006 | 115.317986 | 44676.000000 | 1 | ok |
| needle_haystack_large | plain | n/a | search | 126450608 | 0.073980 | 0.044733 | 0.028466 | 98.804603 | 44676.000000 | 1 | ok |
| needle_haystack_large | zlg_fast | fast | search | 14807773 | 0.020609 | 0.010491 | 0.010491 | 97.688997 | 44676.000000 | 1 | ok |
| needle_haystack_large | zlg_standard | standard | search | 12945933 | 0.019749 | 0.007734 | 0.011649 | 97.905585 | 44676.000000 | 1 | ok |
| needle_haystack_large | gzip | gzip-6 | tail | 14936213 | 2.555441 | 1.749249 | 1.420361 | 123.598318 | 44676.000000 | 10 | ok |
| needle_haystack_large | plain | n/a | tail | 126450608 | 0.005711 | 0.002705 | 0.002705 | 91.958957 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_fast | fast | tail | 14807773 | 0.010081 | 0.009589 | 0.000000 | 95.279852 | 44676.000000 | 10 | ok |
| needle_haystack_large | zlg_standard | standard | tail | 12945933 | 0.010744 | 0.004632 | 0.004632 | 95.118015 | 44676.000000 | 10 | ok |
| needle_haystack_large | gzip | gzip-6 | tail_large | 14936213 | 2.555135 | 1.722987 | 1.359005 | 123.662669 | 44676.000000 | 5000 | ok |
| needle_haystack_large | plain | n/a | tail_large | 126450608 | 0.006297 | 0.002888 | 0.002888 | 89.916091 | 44676.000000 | 5000 | ok |
| needle_haystack_large | zlg_fast | fast | tail_large | 14807773 | 0.025753 | 0.012606 | 0.013690 | 97.982550 | 44676.000000 | 5000 | ok |
| needle_haystack_large | zlg_standard | standard | tail_large | 12945933 | 0.025740 | 0.011700 | 0.015600 | 98.653840 | 44676.000000 | 5000 | ok |
| repeated_regex | gzip | gzip-6 | build | 1233402 | 0.212365 | 0.207060 | 0.007964 | 99.578662 | 19800.000000 | n/a | n/a |
| repeated_regex | plain | n/a | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | n/a | n/a |
| repeated_regex | zlg_fast | fast | build | 1185857 | 0.131995 | 0.108683 | 0.024156 | 99.524708 | 21016.000000 | n/a | n/a |
| repeated_regex | zlg_standard | standard | build | 967824 | 0.242521 | 0.209507 | 0.028444 | 99.745169 | 21016.000000 | n/a | n/a |
| repeated_regex | gzip | gzip-6 | head | 1233402 | 1.874999 | 1.106203 | 1.303555 | 126.619417 | 38604.000000 | 10 | ok |
| repeated_regex | plain | n/a | head | 15692090 | 0.006404 | 0.000000 | 0.005802 | 91.987703 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | head | 1185857 | 0.020026 | 0.012250 | 0.008166 | 97.849474 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | head | 967824 | 0.020521 | 0.008187 | 0.012162 | 97.965343 | 32152.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | search | 1233402 | 0.112281 | 0.112860 | 0.057904 | 152.304745 | 32152.000000 | 80000 | ok |
| repeated_regex | plain | n/a | search | 15692090 | 0.047857 | 0.036331 | 0.012110 | 98.598263 | 21016.000000 | 80000 | ok |
| repeated_regex | zlg_fast | fast | search | 1185857 | 0.053496 | 0.034809 | 0.019338 | 98.934859 | 32152.000000 | 80000 | ok |
| repeated_regex | zlg_standard | standard | search | 967824 | 0.054473 | 0.032551 | 0.029070 | 99.108535 | 32152.000000 | 80000 | ok |
| repeated_regex | gzip | gzip-6 | tail | 1233402 | 2.066998 | 1.180709 | 1.380944 | 125.645015 | 38468.000000 | 10 | ok |
| repeated_regex | plain | n/a | tail | 15692090 | 0.006357 | 0.000000 | 0.005818 | 91.518394 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_fast | fast | tail | 1185857 | 0.018484 | 0.008386 | 0.008386 | 98.036763 | 32152.000000 | 10 | ok |
| repeated_regex | zlg_standard | standard | tail | 967824 | 0.017699 | 0.004497 | 0.012180 | 98.236693 | 32152.000000 | 10 | ok |
| repeated_regex | gzip | gzip-6 | tail_large | 1233402 | 1.907811 | 1.148746 | 1.358367 | 125.999234 | 38872.000000 | 5000 | ok |
| repeated_regex | plain | n/a | tail_large | 15692090 | 0.007052 | 0.000000 | 0.006535 | 91.884042 | 32152.000000 | 5000 | ok |
| repeated_regex | zlg_fast | fast | tail_large | 1185857 | 0.020698 | 0.016303 | 0.004048 | 97.922238 | 32152.000000 | 5000 | ok |
| repeated_regex | zlg_standard | standard | tail_large | 967824 | 0.019805 | 0.011573 | 0.007715 | 97.994595 | 32152.000000 | 5000 | ok |

## Median wall-time ratios

- needle_haystack_large build: zlg_fast vs gzip median wall ratio 0.866
- needle_haystack_large build: zlg_standard vs gzip median wall ratio 1.309
- needle_haystack_large build: zlg_fast vs zlg_standard median wall ratio 0.662
- needle_haystack_large search: zlg_fast vs gzip median wall ratio 0.031
- needle_haystack_large search: zlg_standard vs gzip median wall ratio 0.030
- needle_haystack_large search: zlg_fast vs plain median wall ratio 0.279
- needle_haystack_large search: zlg_fast vs zlg_standard median wall ratio 1.044
- needle_haystack_large head: zlg_fast vs gzip median wall ratio 0.011
- needle_haystack_large head: zlg_standard vs gzip median wall ratio 0.010
- needle_haystack_large head: zlg_fast vs plain median wall ratio 3.725
- needle_haystack_large head: zlg_fast vs zlg_standard median wall ratio 1.041
- needle_haystack_large tail: zlg_fast vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_standard vs gzip median wall ratio 0.004
- needle_haystack_large tail: zlg_fast vs plain median wall ratio 1.765
- needle_haystack_large tail: zlg_fast vs zlg_standard median wall ratio 0.938
- needle_haystack_large tail_large: zlg_fast vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_standard vs gzip median wall ratio 0.010
- needle_haystack_large tail_large: zlg_fast vs plain median wall ratio 4.090
- needle_haystack_large tail_large: zlg_fast vs zlg_standard median wall ratio 1.001
- repeated_regex build: zlg_fast vs gzip median wall ratio 0.622
- repeated_regex build: zlg_standard vs gzip median wall ratio 1.142
- repeated_regex build: zlg_fast vs zlg_standard median wall ratio 0.544
- repeated_regex search: zlg_fast vs gzip median wall ratio 0.476
- repeated_regex search: zlg_standard vs gzip median wall ratio 0.485
- repeated_regex search: zlg_fast vs plain median wall ratio 1.118
- repeated_regex search: zlg_fast vs zlg_standard median wall ratio 0.982
- repeated_regex head: zlg_fast vs gzip median wall ratio 0.011
- repeated_regex head: zlg_standard vs gzip median wall ratio 0.011
- repeated_regex head: zlg_fast vs plain median wall ratio 3.127
- repeated_regex head: zlg_fast vs zlg_standard median wall ratio 0.976
- repeated_regex tail: zlg_fast vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_standard vs gzip median wall ratio 0.009
- repeated_regex tail: zlg_fast vs plain median wall ratio 2.908
- repeated_regex tail: zlg_fast vs zlg_standard median wall ratio 1.044
- repeated_regex tail_large: zlg_fast vs gzip median wall ratio 0.011
- repeated_regex tail_large: zlg_standard vs gzip median wall ratio 0.010
- repeated_regex tail_large: zlg_fast vs plain median wall ratio 2.935
- repeated_regex tail_large: zlg_fast vs zlg_standard median wall ratio 1.045
