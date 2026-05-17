# Phase 2c performance smoke bench

This is a compact smoke comparison, not the full historical benchmark matrix.

| scenario | backend | operation | storage bytes | wall seconds | user seconds | system seconds | max rss kb | match count | exit |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated_regex | plain_grep | build | 6406015 | 0.000000 | 0.000000 | 0.000000 | n/a | 0 | 0 |
| repeated_regex | gzip_zgrep | build | 613232 | 0.108112 |  |  |  | 2815 | 0 |
| repeated_regex | zlg | build | 482971 | 0.137137 |  |  |  | 0 | 0 |
| repeated_regex | plain_grep | search | 6406015 | 0.026859 |  |  |  | 40000 | 0 |
| repeated_regex | gzip_zgrep | search | 613232 | 0.079224 |  |  |  | 40000 | 0 |
| repeated_regex | zlg | search | 482971 | 0.036721 |  |  |  | 40000 | 0 |
| needle_haystack | plain_grep | build | 5928889 | 0.000000 | 0.000000 | 0.000000 | n/a | 0 | 0 |
| needle_haystack | gzip_zgrep | build | 609208 | 0.078147 |  |  |  | 739 | 0 |
| needle_haystack | zlg | build | 521414 | 0.125109 |  |  |  | 0 | 0 |
| needle_haystack | plain_grep | search | 5928889 | 0.009328 |  |  |  | 1 | 0 |
| needle_haystack | gzip_zgrep | search | 609208 | 0.065900 |  |  |  | 1 | 0 |
| needle_haystack | zlg | search | 521414 | 0.014879 |  |  |  | 1 | 0 |
