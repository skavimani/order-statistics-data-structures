"""
benchmark_structures.py - Part 2 empirical comparison

Measures four scenarios that show the array-vs-linked-list trade-offs:

  1. Stack:   n pushes then n pops        ArrayStack vs LinkedStack
  2. Queue:   n enqueues then n dequeues  ArrayQueue (circular) vs LinkedQueue,
              and (small n) circular ArrayQueue vs a "naive" array queue
              that dequeues from index 0
  3. Insert at the FRONT n times          DynamicArray.insert(0) vs SinglyLinkedList.insert_front
  4. Read n random positions              DynamicArray.get(i) vs SinglyLinkedList.get(i)

Run:  python3 src/benchmark_structures.py   (about 1-2 minutes; each point is the median of 5 runs)
Outputs: results/structures_results.csv and results/structures_comparison.png
"""

import csv
import os
import random
import statistics
import time

from data_structures import (ArrayQueue, ArrayStack, DynamicArray, LinkedQueue,
                             LinkedStack, SinglyLinkedList)

# results/ sits next to src/ in the project folder
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def stack_test(cls, n):
    s = cls()
    for i in range(n):
        s.push(i)
    for _ in range(n):
        s.pop()


def queue_test(cls, n):
    q = cls()
    for i in range(n):
        q.enqueue(i)
    for _ in range(n):
        q.dequeue()


def naive_queue_test(n):
    """Queue on a DynamicArray that dequeues with delete(0): every dequeue shifts."""
    a = DynamicArray()
    for i in range(n):
        a.append(i)
    for _ in range(n):
        a.delete(0)


def front_insert_array(n):
    a = DynamicArray()
    for i in range(n):
        a.insert(0, i)


def front_insert_linked(n):
    ll = SinglyLinkedList()
    for i in range(n):
        ll.insert_front(i)


def random_access(structure, n, rng):
    for _ in range(n):
        structure.get(rng.randrange(n))


def timed(fn, *args, repeats=5):
    """Run fn(*args) several times and return the MEDIAN time (less noisy)."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def run():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    rows = []
    rng = random.Random(1)

    def record(scenario, structure, n, seconds):
        rows.append({"scenario": scenario, "structure": structure, "n": n, "seconds": seconds})
        print(f"{scenario:22} {structure:34} n={n:>7}  {seconds * 1000:9.2f} ms")

    for n in [10_000, 50_000, 100_000, 200_000]:
        record("stack push+pop", "ArrayStack", n, timed(stack_test, ArrayStack, n))
        record("stack push+pop", "LinkedStack", n, timed(stack_test, LinkedStack, n))
        record("queue enq+deq", "ArrayQueue (circular)", n, timed(queue_test, ArrayQueue, n))
        record("queue enq+deq", "LinkedQueue", n, timed(queue_test, LinkedQueue, n))

    for n in [1_000, 2_000, 4_000, 8_000]:
        record("queue: circular vs naive", "ArrayQueue (circular)", n, timed(queue_test, ArrayQueue, n))
        record("queue: circular vs naive", "Naive array queue (delete index 0)", n, timed(naive_queue_test, n))
        record("insert at front", "DynamicArray", n, timed(front_insert_array, n))
        record("insert at front", "SinglyLinkedList", n, timed(front_insert_linked, n))
        arr, ll = DynamicArray(), SinglyLinkedList()
        for i in range(n):
            arr.append(i)
            ll.insert_back(i)
        record("random access", "DynamicArray", n, timed(random_access, arr, n, rng))
        record("random access", "SinglyLinkedList", n, timed(random_access, ll, n, rng))

    with open(os.path.join(RESULTS_DIR, "structures_results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping chart")
        return

    scenarios = ["stack push+pop", "queue enq+deq", "queue: circular vs naive",
                 "insert at front", "random access"]
    palette = ["#1f5aa6", "#d9822b", "#b03a2e"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5))
    axes.flat[-1].axis("off")
    for ax, scen in zip(axes.flat, scenarios):
        names = list(dict.fromkeys(r["structure"] for r in rows if r["scenario"] == scen))
        for color, name in zip(palette, names):
            pts = [r for r in rows if r["scenario"] == scen and r["structure"] == name]
            ax.plot([r["n"] for r in pts], [r["seconds"] * 1000 for r in pts],
                    marker="o", label=name, color=color)
        ax.set_title(scen)
        ax.set_xlabel("n (number of operations)")
        ax.set_ylabel("total time (ms)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Array-based vs linked structures")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "structures_comparison.png"), dpi=150)
    plt.close(fig)
    print(f"Chart saved to {RESULTS_DIR}")


if __name__ == "__main__":
    run()
