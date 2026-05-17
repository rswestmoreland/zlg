# Phase 2d performance smoke bench

This bench compares plain logs, gzip streams, and zlg archives for search, head, and tail.
Resource metrics are captured with Linux os.wait4().

| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | cpu percent | max rss kb | matches | parity | exit |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| repeated_regex | plain_grep | build | 15692090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| repeated_regex | gzip_zgrep | build | 1233402 | 0.216132 | 0.204099 | 0.008006 | 98.136719 | 20128 | n/a | n/a | 0 |
| repeated_regex | zlg | build | 967824 | 0.284599 | 0.245919 | 0.036289 | 99.159906 | 21336 | n/a | n/a | 0 |
| repeated_regex | plain_grep | search | 15692090 | 0.055438 | 0.031031 | 0.023273 | 97.954095 | 21336 | 80000 | ok | 0 |
| repeated_regex | gzip_zgrep | search | 1233402 | 0.157981 | 0.116918 | 0.065067 | 115.194337 | 32472 | 80000 | ok | 0 |
| repeated_regex | zlg | search | 967824 | 0.059218 | 0.038057 | 0.019028 | 96.398292 | 32472 | 80000 | ok | 0 |
| repeated_regex | plain_grep | head | 15692090 | 0.007567 | 0.006702 | 0.000000 | 88.567931 | 32472 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | head | 1233402 | 2.921693 | 1.234576 | 1.684580 | 99.913159 | 38816 | 10 | ok | 0 |
| repeated_regex | zlg | head | 967824 | 0.028653 | 0.018858 | 0.007552 | 92.172010 | 32472 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail | 15692090 | 0.022026 | 0.000000 | 0.006047 | 27.454243 | 32472 | 10 | ok | 0 |
| repeated_regex | gzip_zgrep | tail | 1233402 | 2.961209 | 1.383668 | 1.561761 | 99.467108 | 37800 | 10 | ok | 0 |
| repeated_regex | zlg | tail | 967824 | 0.039316 | 0.023548 | 0.000000 | 59.893673 | 32472 | 10 | ok | 0 |
| repeated_regex | plain_grep | tail_large | 15692090 | 0.008879 | 0.000000 | 0.008242 | 92.830536 | 32472 | 5000 | ok | 0 |
| repeated_regex | gzip_zgrep | tail_large | 1233402 | 3.250807 | 1.455445 | 1.806660 | 100.347532 | 38272 | 5000 | ok | 0 |
| repeated_regex | zlg | tail_large | 967824 | 0.044334 | 0.016222 | 0.020302 | 82.384608 | 32472 | 5000 | ok | 0 |
| needle_haystack_large | plain_grep | build | 126450608 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | n/a | n/a | 0 |
| needle_haystack_large | gzip_zgrep | build | 14936213 | 1.946408 | 1.826233 | 0.075932 | 97.726943 | 32472 | n/a | n/a | 0 |
| needle_haystack_large | zlg | build | 12945933 | 2.703897 | 2.347058 | 0.347188 | 99.643055 | 44960 | n/a | n/a | 0 |
| needle_haystack_large | plain_grep | search | 126450608 | 0.073209 | 0.044348 | 0.028221 | 99.126217 | 44960 | 1 | ok | 0 |
| needle_haystack_large | gzip_zgrep | search | 14936213 | 0.689843 | 0.576903 | 0.171923 | 108.550256 | 44960 | 1 | ok | 0 |
| needle_haystack_large | zlg | search | 12945933 | 0.020689 | 0.012073 | 0.008048 | 97.252361 | 44960 | 1 | ok | 0 |
| needle_haystack_large | plain_grep | head | 126450608 | 0.005680 | 0.000000 | 0.005258 | 92.568858 | 44960 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | head | 14936213 | 2.273214 | 1.086321 | 1.390764 | 108.968386 | 44960 | 10 | ok | 0 |
| needle_haystack_large | zlg | head | 12945933 | 0.020255 | 0.015723 | 0.003941 | 97.081660 | 44960 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail | 126450608 | 0.006033 | 0.000000 | 0.005506 | 91.268644 | 44960 | 10 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail | 14936213 | 3.593777 | 1.768078 | 1.795711 | 99.165547 | 44960 | 10 | ok | 0 |
| needle_haystack_large | zlg | tail | 12945933 | 0.013412 | 0.000000 | 0.012717 | 94.815839 | 44960 | 10 | ok | 0 |
| needle_haystack_large | plain_grep | tail_large | 126450608 | 0.008774 | 0.004056 | 0.004056 | 92.453526 | 44960 | 5000 | ok | 0 |
| needle_haystack_large | gzip_zgrep | tail_large | 14936213 | 3.547906 | 1.873613 | 1.664789 | 99.732111 | 44960 | 5000 | ok | 0 |
| needle_haystack_large | zlg | tail_large | 12945933 | 0.030769 | 0.007449 | 0.022349 | 96.845533 | 44960 | 5000 | ok | 0 |

## Wall-time ratios

- needle_haystack_large search: zlg vs gzip/zgrep wall ratio 0.030
- needle_haystack_large search: zlg vs plain wall ratio 0.283
- needle_haystack_large head: zlg vs gzip/zgrep wall ratio 0.009
- needle_haystack_large head: zlg vs plain wall ratio 3.566
- needle_haystack_large tail: zlg vs gzip/zgrep wall ratio 0.004
- needle_haystack_large tail: zlg vs plain wall ratio 2.223
- needle_haystack_large tail_large: zlg vs gzip/zgrep wall ratio 0.009
- needle_haystack_large tail_large: zlg vs plain wall ratio 3.507
- repeated_regex search: zlg vs gzip/zgrep wall ratio 0.375
- repeated_regex search: zlg vs plain wall ratio 1.068
- repeated_regex head: zlg vs gzip/zgrep wall ratio 0.010
- repeated_regex head: zlg vs plain wall ratio 3.787
- repeated_regex tail: zlg vs gzip/zgrep wall ratio 0.013
- repeated_regex tail: zlg vs plain wall ratio 1.785
- repeated_regex tail_large: zlg vs gzip/zgrep wall ratio 0.014
- repeated_regex tail_large: zlg vs plain wall ratio 4.993
