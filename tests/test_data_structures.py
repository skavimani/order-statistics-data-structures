"""Unit tests for data_structures.py. Run with:  python3 -m unittest discover -s tests -v"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from data_structures import (ArrayQueue, ArrayStack, DynamicArray, LinkedQueue,
                             LinkedStack, Matrix, RootedTree, SinglyLinkedList)


class TestDynamicArray(unittest.TestCase):

    def test_append_get_set(self):
        a = DynamicArray()
        for i in range(100):
            a.append(i)
        self.assertEqual(len(a), 100)
        self.assertEqual(a.get(57), 57)
        a.set(57, -1)
        self.assertEqual(a.get(57), -1)

    def test_insert_delete_matches_python_list(self):
        rng = random.Random(0)
        a, ref = DynamicArray(), []
        for step in range(500):
            if ref and rng.random() < 0.4:
                i = rng.randrange(len(ref))
                self.assertEqual(a.delete(i), ref.pop(i))
            else:
                i = rng.randint(0, len(ref))
                a.insert(i, step)
                ref.insert(i, step)
            self.assertEqual(a.to_list(), ref)

    def test_find_and_errors(self):
        a = DynamicArray()
        a.append("x")
        self.assertEqual(a.find("x"), 0)
        self.assertEqual(a.find("y"), -1)
        with self.assertRaises(IndexError):
            a.get(1)
        with self.assertRaises(IndexError):
            a.insert(5, "z")
        with self.assertRaises(IndexError):
            DynamicArray().delete(0)


class TestMatrix(unittest.TestCase):

    def test_access_and_shape_changes(self):
        m = Matrix.from_lists([[1, 2, 3], [4, 5, 6]])
        self.assertEqual(m.get(1, 2), 6)
        m.insert_row(1, [7, 8, 9])
        self.assertEqual(m.to_lists(), [[1, 2, 3], [7, 8, 9], [4, 5, 6]])
        self.assertEqual(m.delete_row(0), [1, 2, 3])
        m.insert_column(0, [0, 0])
        self.assertEqual(m.to_lists(), [[0, 7, 8, 9], [0, 4, 5, 6]])
        self.assertEqual(m.delete_column(3), [9, 6])
        self.assertEqual(m.to_lists(), [[0, 7, 8], [0, 4, 5]])

    def test_math(self):
        a = Matrix.from_lists([[1, 2], [3, 4]])
        b = Matrix.from_lists([[5, 6], [7, 8]])
        self.assertEqual(a.add(b).to_lists(), [[6, 8], [10, 12]])
        self.assertEqual(a.multiply(b).to_lists(), [[19, 22], [43, 50]])
        self.assertEqual(Matrix.from_lists([[1, 2, 3]]).transpose().to_lists(),
                         [[1], [2], [3]])

    def test_errors(self):
        m = Matrix(2, 2)
        with self.assertRaises(IndexError):
            m.get(2, 0)
        with self.assertRaises(ValueError):
            m.insert_row(0, [1])
        with self.assertRaises(ValueError):
            m.multiply(Matrix(3, 1))


class TestStacksAndQueues(unittest.TestCase):

    def test_stacks_are_lifo(self):
        for stack in (ArrayStack(), LinkedStack()):
            for i in range(1000):
                stack.push(i)
            self.assertEqual(stack.peek(), 999)
            self.assertEqual([stack.pop() for _ in range(1000)],
                             list(range(999, -1, -1)))
            self.assertTrue(stack.is_empty())
            with self.assertRaises(IndexError):
                stack.pop()

    def test_queues_are_fifo_with_wraparound(self):
        for queue in (ArrayQueue(), LinkedQueue()):
            expected, nxt = [], 0
            rng = random.Random(5)
            for _ in range(2000):          # mixed ops force wrap-around and resizing
                if expected and rng.random() < 0.45:
                    self.assertEqual(queue.dequeue(), expected.pop(0))
                else:
                    queue.enqueue(nxt)
                    expected.append(nxt)
                    nxt += 1
                self.assertEqual(len(queue), len(expected))
            while expected:
                self.assertEqual(queue.peek(), expected[0])
                self.assertEqual(queue.dequeue(), expected.pop(0))
            with self.assertRaises(IndexError):
                queue.dequeue()


class TestSinglyLinkedList(unittest.TestCase):

    def test_insertions(self):
        ll = SinglyLinkedList()
        ll.insert_back(2)
        ll.insert_front(1)
        ll.insert_back(4)
        ll.insert_at(2, 3)
        ll.insert_at(0, 0)
        self.assertEqual(ll.to_list(), [0, 1, 2, 3, 4])
        self.assertEqual(ll.tail.value, 4)

    def test_deletions_keep_tail_correct(self):
        ll = SinglyLinkedList([1, 2, 3, 4])
        self.assertTrue(ll.delete_value(4))        # delete the tail
        self.assertEqual(ll.tail.value, 3)
        ll.insert_back(5)
        self.assertEqual(ll.to_list(), [1, 2, 3, 5])
        self.assertFalse(ll.delete_value(42))
        self.assertEqual(ll.delete_at(1), 2)
        self.assertEqual(ll.delete_front(), 1)
        self.assertEqual(ll.to_list(), [3, 5])
        ll.delete_at(1)
        ll.delete_at(0)
        self.assertTrue(ll.is_empty())
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)

    def test_search_get_traverse_reverse(self):
        ll = SinglyLinkedList("abcde")
        self.assertEqual(ll.search("c"), 2)
        self.assertEqual(ll.search("z"), -1)
        self.assertEqual(ll.get(4), "e")
        ll.reverse()
        self.assertEqual("".join(ll.traverse()), "edcba")
        ll.insert_back("!")                        # tail must be right after reverse
        self.assertEqual(ll.to_list()[-1], "!")


class TestRootedTree(unittest.TestCase):

    def test_tree(self):
        t = RootedTree("A")
        b = t.add_child(t.root, "B")
        c = t.add_child(t.root, "C")
        d = t.add_child(b, "D")
        t.add_child(d, "E")
        self.assertEqual(len(t), 5)
        self.assertEqual([n.key for n in t.children(t.root)], ["C", "B"])
        self.assertEqual(list(t.preorder()), ["A", "C", "B", "D", "E"])
        self.assertEqual(t.height(), 3)
        self.assertEqual(t.depth(t.find("E")), 3)
        self.assertIs(t.find("C"), c)
        self.assertIsNone(t.find("Z"))


if __name__ == "__main__":
    unittest.main()
