"""
benchmark_selection.py - Part 1 empirical analysis

Times deterministic_select (Median of Medians) and randomized_select
(Randomized Quickselect) on four input distributions and several sizes,
always asking for the median (the hardest case for selection).
A small extra run shows first_pivot_select on sorted input to illustrate
the O(n^2) worst case that a fixed pivot rule can hit.

Run:  python3 src/benchmark_selection.py          (full run, about 1-2 minutes)
      python3 src/benchmark_selection.py --quick  (smaller sizes, a few seconds)

Outputs (in the results/ folder):
  selection_results.csv     - every measurement
  selection_by_size.png     - time vs n, one panel per distribution
  selection_per_element.png - time per element (flat line = linear time)
  first_pivot_worst_case.png
"""

import csv
import os
import random
import statistics
import sys
import time

from selection import deterministic_select, first_pivot_select, randomized_select

# results/ sits next to src/ in the project folder
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
QUICK = "--quick" in sys.argv

SIZES = [1_000, 5_000, 10_000, 50_000, 100_000, 200_000] if not QUICK else [1_000, 5_000, 10_000]
REPEATS = 5 if not QUICK else 3
SEED = 2026


def make_input(distribution, n, rng):
    if distribution == "random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if distribution == "sorted":
        return list(range(n))
    if distribution == "reverse-sorted":
        return list(range(n, 0, -1))
    if distribution == "many-duplicates":
        return [rng.randint(0, 9) for _ in range(n)]   # only 10 distinct values
    raise ValueError(distribution)


DISTRIBUTIONS = ["random", "sorted", "reverse-sorted", "many-duplicates"]
ALGORITHMS = {
    "Deterministic (Median of Medians)": deterministic_select,
    "Randomized Quickselect": randomized_select,
    "Built-in sorted() baseline": lambda a, k: sorted(a)[k - 1],
}


def time_call(fn, data, k):
    start = time.perf_counter()
    result = fn(data, k)
    return time.perf_counter() - start, result


def run():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    rng = random.Random(SEED)
    rows = []
    print(f"{'distribution':16} {'n':>8}  " + "  ".join(f"{name[:24]:>24}" for name in ALGORITHMS))
    for dist in DISTRIBUTIONS:
        for n in SIZES:
            data = make_input(dist, n, rng)
            k = (n + 1) // 2
            expected = sorted(data)[k - 1]
            medians = []
            for name, fn in ALGORITHMS.items():
                times = []
                for _ in range(REPEATS):
                    t, result = time_call(fn, data, k)
                    assert result == expected, f"{name} gave a wrong answer"
                    times.append(t)
                med = statistics.median(times)
                medians.append(med)
                rows.append({"distribution": dist, "n": n, "algorithm": name,
                             "median_seconds": med, "min_seconds": min(times),
                             "max_seconds": max(times)})
            print(f"{dist:16} {n:>8}  " + "  ".join(f"{m * 1000:>21.2f} ms" for m in medians))

    # Worst case for a fixed pivot: first-element pivot on sorted input.
    worst_rows = []
    for n in ([500, 1000, 2000, 4000] if not QUICK else [500, 1000]):
        data = list(range(n))
        k = (n + 1) // 2
        t_first, _ = time_call(first_pivot_select, data, k)
        t_rand, _ = time_call(randomized_select, data, k)
        t_det, _ = time_call(deterministic_select, data, k)
        worst_rows.append({"n": n, "first_pivot": t_first,
                           "randomized": t_rand, "deterministic": t_det})
        print(f"sorted n={n:5}: first-pivot {t_first*1000:8.2f} ms | "
              f"randomized {t_rand*1000:6.2f} ms | deterministic {t_det*1000:6.2f} ms")

    with open(os.path.join(RESULTS_DIR, "selection_results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with open(os.path.join(RESULTS_DIR, "first_pivot_worst_case.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(worst_rows[0]))
        writer.writeheader()
        writer.writerows(worst_rows)

    plot(rows, worst_rows)


def plot(rows, worst_rows):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping charts (CSV files were still saved)")
        return

    colors = {"Deterministic (Median of Medians)": "#1f5aa6",
              "Randomized Quickselect": "#d9822b",
              "Built-in sorted() baseline": "#7a7a7a"}

    for kind in ("by_size", "per_element"):
        fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
        for ax, dist in zip(axes.flat, DISTRIBUTIONS):
            for name in ALGORITHMS:
                pts = [r for r in rows if r["distribution"] == dist and r["algorithm"] == name]
                xs = [r["n"] for r in pts]
                if kind == "by_size":
                    ys = [r["median_seconds"] * 1000 for r in pts]
                else:
                    ys = [r["median_seconds"] / r["n"] * 1e9 for r in pts]
                ax.plot(xs, ys, marker="o", label=name, color=colors[name],
                        linestyle="--" if "baseline" in name else "-")
            ax.set_title(dist)
            ax.set_xscale("log")
            ax.grid(alpha=0.3)
            ax.set_ylabel("time (ms)" if kind == "by_size" else "ns per element")
            ax.set_xlabel("n (input size)")
            if kind == "per_element":
                ax.set_ylim(bottom=0)
        axes.flat[0].legend(fontsize=8)
        title = ("Selection time vs input size (k = median)" if kind == "by_size"
                 else "Time per element (a flat line means linear time)")
        fig.suptitle(title)
        fig.tight_layout()
        fig.savefig(os.path.join(RESULTS_DIR, f"selection_{kind}.png"), dpi=150)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    xs = [r["n"] for r in worst_rows]
    ax.plot(xs, [r["first_pivot"] * 1000 for r in worst_rows], marker="o",
            color="#b03a2e", label="First-element pivot (fixed rule)")
    ax.plot(xs, [r["randomized"] * 1000 for r in worst_rows], marker="o",
            color=colors["Randomized Quickselect"], label="Randomized Quickselect")
    ax.plot(xs, [r["deterministic"] * 1000 for r in worst_rows], marker="o",
            color=colors["Deterministic (Median of Medians)"], label="Median of Medians")
    ax.set_xlabel("n (sorted input)")
    ax.set_ylabel("time (ms)")
    ax.set_title("Why the pivot rule matters: sorted input")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "first_pivot_worst_case.png"), dpi=150)
    plt.close(fig)
    print(f"Charts saved to {RESULTS_DIR}")


if __name__ == "__main__":
    run()
