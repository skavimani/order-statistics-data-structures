"""
selection.py - Part 1: Selection algorithms (order statistics)

The "k-th order statistic" of a list is the k-th smallest value in it.
k = 1 is the minimum, k = n is the maximum, and k = (n + 1) // 2 is the
(lower) median.

This file contains two ways to find it without sorting the whole list:

1. deterministic_select(...)  - "Median of Medians" (Blum, Floyd, Pratt,
   Rivest & Tarjan, 1973). Worst-case O(n) time.
2. randomized_select(...)     - "Randomized Quickselect" (Hoare, 1961, with
   a random pivot). Expected O(n) time, worst case O(n^2) (very unlikely).

A third function, first_pivot_select(...), always uses the first element as
the pivot. It is NOT part of the assignment's required algorithms; it is only
here so the benchmark can show what goes wrong without a good pivot rule
(it takes O(n^2) time on already-sorted input).

Design choices
--------------
* k is 1-based (k = 1 means "smallest"), matching textbook notation.
* The input list is never changed. Each function copies it once and then
  works on the copy *in place* (no new lists are created while partitioning).
* Duplicates are handled with a THREE-WAY partition: the range is split into
  [ < pivot | == pivot | > pivot ]. If k lands in the middle block we are
  done immediately. Without this, a list full of equal values can make a
  two-way partition loop forever or degrade to O(n^2).
"""

import random

GROUP_SIZE = 5  # Median of Medians uses groups of 5 elements


# ---------------------------------------------------------------------------
# Helpers shared by all selection functions
# ---------------------------------------------------------------------------

def _check_arguments(values, k):
    """Raise a clear error for empty input or an out-of-range k."""
    if len(values) == 0:
        raise ValueError("cannot select from an empty list")
    if not 1 <= k <= len(values):
        raise ValueError(f"k must be between 1 and {len(values)}, got {k}")


def three_way_partition(a, lo, hi, pivot):
    """
    Rearrange a[lo:hi] (hi is exclusive) into three blocks:

        a[lo:lt]   values  < pivot
        a[lt:gt]   values == pivot
        a[gt:hi]   values  > pivot

    and return (lt, gt). This is Dijkstra's "Dutch national flag" scheme.
    It makes one pass over the range and uses O(1) extra memory.
    """
    lt = lo          # next slot for a "< pivot" value
    i = lo           # current element being examined
    gt = hi          # one past the last unexamined element
    while i < gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            gt -= 1
            a[gt], a[i] = a[i], a[gt]
            # do not advance i: the value swapped in has not been examined yet
        else:
            i += 1
    return lt, gt


def _insertion_sort(a, lo, hi):
    """Sort the small range a[lo:hi] in place (used on groups of <= 5)."""
    for i in range(lo + 1, hi):
        current = a[i]
        j = i - 1
        while j >= lo and a[j] > current:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = current


# ---------------------------------------------------------------------------
# 1. Deterministic selection: Median of Medians, worst-case O(n)
# ---------------------------------------------------------------------------

def deterministic_select(values, k):
    """
    Return the k-th smallest element of `values` (k is 1-based) in
    worst-case linear time using the Median of Medians pivot rule.

    Steps on each round (range a[lo:hi]):
      1. Split the range into groups of 5 and sort each tiny group.
      2. Move each group's median to the front of the range.
      3. Recursively find the median of those medians -> the pivot.
      4. Three-way partition around the pivot.
      5. Keep only the block that contains position k and repeat.

    The pivot is guaranteed to have at least ~3n/10 elements on each side,
    so each round throws away at least ~30% of the range. This gives the
    recurrence T(n) <= T(n/5) + T(7n/10) + O(n), which solves to O(n).
    """
    _check_arguments(values, k)
    a = list(values)                      # work on a copy
    return _mom_select(a, 0, len(a), k - 1)


def _mom_select(a, lo, hi, target):
    """
    Return the value that would be at index `target` if a[lo:hi] were
    sorted (target is an absolute 0-based index into `a`).
    The outer loop is iterative; only the "median of medians" step recurses,
    so the recursion depth is O(log n).
    """
    while True:
        n = hi - lo
        if n <= GROUP_SIZE:               # base case: just sort the few left
            _insertion_sort(a, lo, hi)
            return a[target]

        # Steps 1 + 2: sort each group of 5 and move its median to the front.
        num_medians = 0
        for group_start in range(lo, hi, GROUP_SIZE):
            group_end = min(group_start + GROUP_SIZE, hi)
            _insertion_sort(a, group_start, group_end)
            median_index = group_start + (group_end - group_start - 1) // 2
            front = lo + num_medians
            a[front], a[median_index] = a[median_index], a[front]
            num_medians += 1

        # Step 3: the pivot is the median of the medians (recursive call).
        middle = lo + (num_medians - 1) // 2
        pivot = _mom_select(a, lo, lo + num_medians, middle)

        # Step 4: three-way partition around the pivot.
        lt, gt = three_way_partition(a, lo, hi, pivot)

        # Step 5: continue in the block that holds the target position.
        if target < lt:
            hi = lt
        elif target >= gt:
            lo = gt
        else:
            return pivot                  # target is inside the "== pivot" block


# ---------------------------------------------------------------------------
# 2. Randomized selection: Randomized Quickselect, expected O(n)
# ---------------------------------------------------------------------------

def randomized_select(values, k, rng=None):
    """
    Return the k-th smallest element of `values` (k is 1-based) in expected
    linear time.

    Each round picks a pivot uniformly at random from the current range,
    three-way partitions around it, and keeps only the block that contains
    position k. On average the pivot lands near the middle, so the range
    shrinks by a constant fraction per round and the total work is about
    n + 3n/4 + (3/4)^2 n + ... = O(n) in expectation.

    `rng` lets tests pass a seeded random.Random for repeatable runs.
    """
    _check_arguments(values, k)
    rng = rng or random
    a = list(values)                      # work on a copy
    lo, hi, target = 0, len(a), k - 1
    while True:
        if hi - lo == 1:
            return a[lo]
        pivot = a[rng.randrange(lo, hi)]  # random pivot from a[lo:hi]
        lt, gt = three_way_partition(a, lo, hi, pivot)
        if target < lt:
            hi = lt
        elif target >= gt:
            lo = gt
        else:
            return pivot


# ---------------------------------------------------------------------------
# 3. For contrast only: quickselect with a fixed (first-element) pivot
# ---------------------------------------------------------------------------

def first_pivot_select(values, k):
    """
    Quickselect that always uses the FIRST element as the pivot.
    Same code as randomized_select except for the pivot choice.
    On sorted or reverse-sorted input every partition removes only one
    element, so it takes Theta(n^2) time. Used in the benchmark to show why
    the pivot rule matters.
    """
    _check_arguments(values, k)
    a = list(values)
    lo, hi, target = 0, len(a), k - 1
    while True:
        if hi - lo == 1:
            return a[lo]
        pivot = a[lo]
        lt, gt = three_way_partition(a, lo, hi, pivot)
        if target < lt:
            hi = lt
        elif target >= gt:
            lo = gt
        else:
            return pivot


def median(values, method="deterministic"):
    """Convenience wrapper: return the lower median of `values`."""
    k = (len(values) + 1) // 2
    if method == "deterministic":
        return deterministic_select(values, k)
    return randomized_select(values, k)


if __name__ == "__main__":
    # Small demo you can run with:  python3 src/selection.py
    data = [7, 2, 9, 4, 4, 1, 8, 4, 6, 3, 5]
    print("Data:          ", data)
    print("Sorted (check):", sorted(data))
    for k in (1, 3, 6, len(data)):
        d = deterministic_select(data, k)
        r = randomized_select(data, k)
        print(f"k={k:2d}  deterministic={d}  randomized={r}")
    print("Median:", median(data))
