import sys
from .parser import parse_file, LEVELS
from .stats import count_by_level


def main(argv):
    if len(argv) < 1:
        print("usage: main.py <logfile> [--since TIMESTAMP]", file=sys.stderr)
        return 2
    path = argv[0]
    records = parse_file(path)
    counts = count_by_level(records)
    for lvl in LEVELS:
        print(f"{lvl} {counts[lvl]}")
    return 0
