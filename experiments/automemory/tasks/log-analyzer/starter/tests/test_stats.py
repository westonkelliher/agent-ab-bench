"""Plain-Python tests. Run with: python3 tests/test_stats.py"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.parser import LogRecord
from analyzer.stats import count_by_level


def test_count_by_level():
    recs = [
        LogRecord(datetime(2024, 1, 1), "INFO", "a"),
        LogRecord(datetime(2024, 1, 1), "INFO", "b"),
        LogRecord(datetime(2024, 1, 1), "ERROR", "c"),
    ]
    c = count_by_level(recs)
    assert c == {"DEBUG": 0, "INFO": 2, "WARN": 0, "ERROR": 1}, c


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    if failed:
        sys.exit(1)
    print(f"ok ({len(tests)} tests)")


if __name__ == "__main__":
    main()
