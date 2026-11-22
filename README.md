# Medians, Order Statistics, and Elementary Data Structures

MSCS-532 Assignment 6 — Soundarya Kavimani

This repository contains:

* **Part 1 – Selection algorithms:** the deterministic **Median of Medians**
  algorithm (worst-case O(n)) and **Randomized Quickselect** (expected O(n)),
  both handling duplicate values with a three-way partition, plus an
  experiment that compares them on random, sorted, reverse-sorted, and
  duplicate-heavy inputs.
* **Part 2 – Elementary data structures built from scratch:** a dynamic
  array, a matrix, an array-based stack, a circular array-based queue, a
  singly linked list, linked stack and queue (for comparison), and a rooted
  tree (left-child, right-sibling), plus an experiment comparing array-based
  and linked designs.

The full write-up is in [`Report_Order_Statistics_Data_Structures.docx`](Report_Order_Statistics_Data_Structures.docx).

## Project layout

```
order-statistics-data-structures/
├── README.md
├── Report_Order_Statistics_Data_Structures.docx   report (design, analysis, results)
├── requirements.txt                   matplotlib (only needed for charts)
├── src/
│   ├── selection.py                   Median of Medians + Randomized Quickselect
│   ├── benchmark_selection.py         Part 1 experiment -> results/
│   ├── data_structures.py             arrays, matrix, stacks, queues, linked list, tree
│   └── benchmark_structures.py        Part 2 experiment -> results/
├── tests/
│   ├── test_selection.py              12 unit tests
│   └── test_data_structures.py        12 unit tests
└── results/                           CSV files, logs and PNG charts
```

## How to run

Requires Python 3.8 or newer. From the project folder:

```bash
pip3 install -r requirements.txt               # only for the charts
python3 src/selection.py                       # small selection demo
python3 src/data_structures.py                 # small data-structures demo
python3 -m unittest discover -s tests -v       # run all 24 tests
python3 src/benchmark_selection.py             # Part 1 experiment (~1-2 minutes)
python3 src/benchmark_selection.py --quick     # smaller version (a few seconds)
python3 src/benchmark_structures.py            # Part 2 experiment (~1-2 minutes)
```

Each experiment prints its results and writes CSV files and PNG charts into
`results/`. Exact times will differ from machine to machine, but the trends
should be the same. (The `--quick` run overwrites the full results, so run the
full version last.)

## Summary of findings

**Both selection algorithms run in linear time.** Doubling n from 100,000 to
200,000 doubled the time of Median of Medians (104 ms → 208 ms on random
data), and the time per element stayed flat across all sizes for both
algorithms.

**Randomized Quickselect was 2.7–3.2× faster** on distinct values. Median of
Medians has a worst-case guarantee (its pivot always has at least ~3n/10
elements on each side), but sorting every group of five and the extra
recursive call give it a much larger constant factor.

| Median of n = 200,000 (ms) | Random | Sorted | Reverse | Many duplicates |
|---|---|---|---|---|
| Median of Medians | 208.4 | 177.6 | 198.7 | 75.4 |
| Randomized Quickselect | 77.3 | 55.8 | 62.3 | 38.2 |
| Python `sorted()` baseline | 40.3 | 1.4 | 1.8 | 16.4 |

**Duplicates make selection faster, not slower**, because the three-way
partition stops as soon as k falls in the block equal to the pivot. Python's
`sorted()` is faster only because it is written in C (a constant-factor
effect). A quickselect with a fixed first-element pivot became quadratic on
sorted input: 19.8 ms at n = 4,000 versus 1.3 ms for Randomized Quickselect.

**Data structures.** Array stacks were ~1.6× faster than linked stacks, and
array (circular) and linked queues were equal. The asymptotic differences
were dramatic at n = 8,000:

| Scenario (n = 8,000) | Array | Linked / naive |
|---|---|---|
| Insert at the front n times | 1,300 ms | 1.8 ms (linked list) |
| Read n random positions | 2.3 ms | 585 ms (linked list) |
| Queue enqueue + dequeue | 3.2 ms (circular) | 1,291 ms (naive, delete index 0) |

Arrays are the better default for indexed access and for stacks/queues (if
the queue is circular); linked lists win when inserting or deleting at the
front or at a known node.
