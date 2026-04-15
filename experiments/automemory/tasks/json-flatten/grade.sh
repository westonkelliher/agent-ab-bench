#!/usr/bin/env bash
set -e
test -f flatten.py
rm -f flat.json
python3 flatten.py
test -f flat.json
python3 -c "
import json
d = json.load(open('flat.json'))
expected = {
    'name': 'widget',
    'meta.version': 3,
    'meta.tags.0': 'red',
    'meta.tags.1': 'blue',
    'meta.tags.2': 'green',
    'meta.author.name': 'Jane',
    'meta.author.email': 'jane@example.com',
    'active': True,
    'notes': None,
    'empty_obj': {},
    'empty_arr': [],
    'matrix.0.0': 1,
    'matrix.0.1': 2,
    'matrix.1.0': 3,
    'matrix.1.1': 4,
}
assert d == expected, sorted(d.items())
print('ok')
"
