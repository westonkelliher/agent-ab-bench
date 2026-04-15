#!/usr/bin/env bash
set -e
test -f convert.py
# re-run fresh to make sure the script works
rm -f output.json
python3 convert.py
test -f output.json
python3 -c "
import json
data = json.load(open('output.json'))
assert isinstance(data, list), type(data)
assert len(data) == 3, len(data)
assert data[0] == {'name': 'Alice', 'age': '30', 'city': 'Portland'}, data[0]
assert data[1]['name'] == 'Bob'
assert data[2]['city'] == 'Denver'
print('ok')
"
