"""Plain-Python test runner. Run with: python3 test_cart.py"""
import math
import sys
from cart import Cart


def approx(a, b, tol=1e-9):
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def test_add_and_total():
    c = Cart()
    c.add_item("apple", 3, 1.50)
    c.add_item("bread", 2, 2.00)
    assert approx(c.total(), 3 * 1.50 + 2 * 2.00)


def test_add_same_item_accumulates():
    c = Cart()
    c.add_item("apple", 2, 1.00)
    c.add_item("apple", 3, 1.00)
    assert c.item_count() == 5
    assert approx(c.total(), 5.00)


def test_remove_item_partial():
    c = Cart()
    c.add_item("apple", 5, 1.00)
    c.remove_item("apple", 2)
    assert c.item_count() == 3


def test_remove_item_all():
    c = Cart()
    c.add_item("apple", 2, 1.00)
    c.remove_item("apple", 2)
    assert c.item_count() == 0


def test_remove_too_many_raises():
    c = Cart()
    c.add_item("apple", 2, 1.00)
    try:
        c.remove_item("apple", 3)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_remove_exact_allowed():
    c = Cart()
    c.add_item("apple", 2, 1.00)
    c.remove_item("apple", 2)  # should not raise


def test_apply_discount_returns_discounted_total():
    c = Cart()
    c.add_item("apple", 4, 2.50)  # total 10.00
    assert approx(c.apply_discount(25), 7.50), c.apply_discount(25)
    # discount should not mutate state
    assert approx(c.total(), 10.00)


def test_item_count_counts_quantity():
    c = Cart()
    c.add_item("a", 3, 1.0)
    c.add_item("b", 4, 2.0)
    assert c.item_count() == 7


def test_add_negative_qty_raises():
    c = Cart()
    try:
        c.add_item("a", 0, 1.0)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


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
