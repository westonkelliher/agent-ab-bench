#!/usr/bin/env bash
set -e
test -f cart.py
test -f test_cart.py
python3 test_cart.py
