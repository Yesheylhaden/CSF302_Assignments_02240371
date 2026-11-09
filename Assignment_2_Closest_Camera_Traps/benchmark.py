"""Measure real runtimes and plot them. Run: .venv/bin/python benchmark.py."""
import csv
import json
import os
import platform
import random
import statistics
import sys
import time
from pathlib import Path

from closest import closest_pair, closest_pair_brute

SIZES = (1000, 2000, 4000, 8000, 16000, 32000, 64000)
ROOT = Path(__file__).resolve().parent


def measure(function, points):
    start = time.perf_counter()
    answer = function(points)
    return time.perf_counter() - start, answer


def main():
    rng = random.Random(302)
    brute_enabled = True
    rows = []
    fields = ['n', 'brute_median_s', 'divide_median_s', 'brute_trials',
              'divide_trials', 'brute_samples_s', 'divide_samples_s', 'brute_status']
    with (ROOT / 'timing_results.csv').open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for n in SIZES:
            points = [(rng.random(), rng.random()) for _ in range(n)]
            fast_samples = []
            for _ in range(3):
                elapsed, fast_answer = measure(closest_pair, points)
                fast_samples.append(elapsed)
            brute_samples = []
            status = 'skipped_after_60s'
            if brute_enabled:
                # Three trials for small sets; one when quadratic cost is high.
                for _ in range(3 if n <= 4000 else 1):
                    elapsed, brute_answer = measure(closest_pair_brute, points)
                    brute_samples.append(elapsed)
                    if brute_answer != fast_answer:
                        raise AssertionError('Algorithms disagree')
                    if elapsed > 60:
                        brute_enabled = False
                        break
                status = 'completed' if brute_enabled else 'exceeded_60s'
            row = dict(n=n,
                       brute_median_s=statistics.median(brute_samples) if brute_samples else '',
                       divide_median_s=statistics.median(fast_samples),
                       brute_trials=len(brute_samples), divide_trials=len(fast_samples),
                       brute_samples_s=json.dumps(brute_samples),
                       divide_samples_s=json.dumps(fast_samples), brute_status=status)
            rows.append(row)
            writer.writerow(row)
            output.flush()
            print(row, flush=True)
    crossover = next((r['n'] for r in rows if r['brute_trials'] and
                      r['divide_median_s'] < r['brute_median_s']), None)
    print('Smallest measured crossover:', crossover)
    print('Python:', sys.version.split()[0], 'Platform:', platform.platform())
    plot_results(rows)


def plot_results(rows):
    # Keep matplotlib's cache inside this writable project directory.
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    measured = [r for r in rows if r['brute_trials']]
    ax.loglog([r['n'] for r in measured], [r['brute_median_s'] for r in measured],
              'o-', label='Brute force')
    ax.loglog([r['n'] for r in rows], [r['divide_median_s'] for r in rows],
              's-', label='Divide and conquer')
    ax.set(xlabel='Number of points n (log scale)',
           ylabel='Median elapsed seconds (log scale)',
           title='Closest camera traps: measured execution time')
    ax.grid(True, which='both', alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / 'performance_graph.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()
