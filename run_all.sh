#!/bin/bash
# run_all.sh - runs everything for Assignment 6 on this computer and saves a log.
# Usage (from the project folder):   bash run_all.sh
cd "$(dirname "$0")"
LOG="results/mac_run_log.txt"
mkdir -p results
{
  echo "=== Machine ==="
  date
  sw_vers 2>/dev/null
  uname -m
  python3 --version
  echo
  python3 -c "import matplotlib" 2>/dev/null || pip3 install -r requirements.txt
  echo "=== Unit tests ==="
  python3 -m unittest discover -s tests -v 2>&1
  echo
  echo "=== Selection demo ==="
  python3 src/selection.py
  echo
  echo "=== Data structures demo ==="
  python3 src/data_structures.py
  echo
  echo "=== Part 1 benchmark (about 1-2 minutes) ==="
  python3 src/benchmark_selection.py | tee results/selection_log.txt
  echo
  echo "=== Part 2 benchmark (about 1-2 minutes) ==="
  python3 src/benchmark_structures.py | tee results/structures_log.txt
  echo
  echo "=== ALL DONE ==="
} 2>&1 | tee "$LOG"
