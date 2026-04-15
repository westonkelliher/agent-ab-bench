#!/usr/bin/env bash
set -e
python3 -c "
from sum_range import sum_range
assert sum_range(1, 10) == 55, sum_range(1, 10)
assert sum_range(0, 0) == 0
assert sum_range(-3, 3) == 0
assert sum_range(5, 5) == 5
assert sum_range(1, 100) == 5050
print('ok')
"
