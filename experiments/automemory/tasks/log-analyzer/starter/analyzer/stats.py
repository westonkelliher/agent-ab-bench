from .parser import LEVELS


def count_by_level(records):
    counts = {lvl: 0 for lvl in LEVELS}
    for r in records:
        counts[r.level] += 1
    return counts
