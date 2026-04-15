#!/usr/bin/env bash
set -e
test -f ini_parser.py
python3 -c "
from ini_parser import parse_ini

t1 = '''
[owner]
name = John
org = Acme

[database]
host=localhost
port = 5432
'''
r = parse_ini(t1)
assert r['owner'] == {'name': 'John', 'org': 'Acme'}, r
assert r['database'] == {'host': 'localhost', 'port': '5432'}, r

# preamble keys go into ''
t2 = '''global=1
; comment
# another
[s]
k=v
'''
r = parse_ini(t2)
assert r[''] == {'global': '1'}, r
assert r['s'] == {'k': 'v'}, r

# = in value
r = parse_ini('[x]\nurl = http://a.com/?q=1&x=2\n')
assert r['x']['url'] == 'http://a.com/?q=1&x=2', r

# duplicate section merges; later key overrides
r = parse_ini('[a]\nk=1\n[b]\nj=2\n[a]\nk=9\nm=3\n')
assert r['a'] == {'k': '9', 'm': '3'}, r
assert r['b'] == {'j': '2'}, r

# blanks and comments ignored
r = parse_ini('\n\n   \n;hi\n#yo\n[s]\n  key   =   val  \n')
assert r['s'] == {'key': 'val'}, r

# no configparser
import ini_parser, sys
assert 'configparser' not in sys.modules or True  # soft
src = open('ini_parser.py').read()
assert 'configparser' not in src, 'must not use configparser'
print('ok')
"
