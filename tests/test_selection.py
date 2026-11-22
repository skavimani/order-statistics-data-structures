"""Unit tests for selection.py. Run with:  python3 -m unittest discover -s tests -v"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from selection import (deterministic_select, first_pivot_select, median,
                       randomized_select)

ALGORITHMS = [deterministic_select, randomized_select, first_pivot_select]


class TestSelection(unittest.TestCase):

    def check_all_k(self, data):
        """Every algorithm must agree with sorting for every k."""
        expected = sorted(data)
        for algo in ALGORITHMS:
            for k in range(1, len(data) + 1):
                self.assertEqual(algo(data, k), expected[k - 1],
                                 f"{algo.__name__} failed for k={k} on {data}")

    def test_single_element(self):
        self.check_all_k([42])

    def test_small_examples(self):
        self.check_all_k([3, 1, 2])
        self.check_all_k([7, 2, 9, 4, 4, 1, 8, 4, 6, 3, 5])

    def test_all_equal(self):
        self.check_all_k([5] * 50)

    def test_many_duplicates(self):
        rng = random.Random(1)
        self.check_all_k([rng.randint(0, 3) for _ in range(200)])

    def test_sorted_and_reverse(self):
        self.check_all_k(list(range(100)))
        self.check_all_k(list(range(100, 0, -1)))

    def test_negative_and_float_values(self):
        self.check_all_k([-3.5, 2.0, -1, 0, 7.25, -10, 2.0])

    def test_random_lists_many_sizes(self):
        rng = random.Random(7)
        for n in [2, 5, 6, 10, 11, 25, 26, 99, 500]:
            data = [rng.randint(-1000, 1000) for _ in range(n)]
            expected = sorted(data)
            for k in {1, n, (n + 1) // 2, rng.randint(1, n)}:
                self.assertEqual(deterministic_select(data, k), expected[k - 1])
                self.assertEqual(randomized_select(data, k, random.Random(k)),
                                 expected[k - 1])

    def test_large_random(self):
        rng = random.Random(3)
        data = [rng.random() for _ in range(20000)]
        k = 12345
        self.assertEqual(deterministic_select(data, k), sorted(data)[k - 1])
        self.assertEqual(randomized_select(data, k), sorted(data)[k - 1])

    def test_input_not_modified(self):
        data = [4, 1, 3, 2]
        copy = list(data)
        deterministic_select(data, 2)
        randomized_select(data, 2)
        self.assertEqual(data, copy)

    def test_strings(self):
        words = ["pear", "apple", "fig", "kiwi", "banana"]
        self.assertEqual(deterministic_select(words, 1), "apple")
        self.assertEqual(randomized_select(words, 5), "pear")

    def test_median_helper(self):
        self.assertEqual(median([5, 1, 3]), 3)
        self.assertEqual(median([4, 1, 3, 2]), 2)            # lower median
        self.assertEqual(median([4, 1, 3, 2], "randomized"), 2)

    def test_invalid_arguments(self):
        for algo in ALGORITHMS:
            with self.assertRaises(ValueError):
                algo([], 1)
            with self.assertRaises(ValueError):
                algo([1, 2, 3], 0)
            with self.assertRaises(ValueError):
                algo([1, 2, 3], 4)


if __name__ == "__main__":
    unittest.main()
