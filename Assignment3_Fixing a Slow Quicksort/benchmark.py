"""Reproduce evidence: .venv/bin/python benchmark.py

Three trials; each runs in a fresh process with a 5-second wall timeout.
Only sorting is timed (copying, startup and correctness checks are excluded).
A crash/timeout stops that case; larger sizes are still attempted independently.
"""
import csv
import multiprocessing as mp
import platform
import random
import statistics
import sys
import time
from pathlib import Path

from sorts import quicksort_basic, quicksort_improved

SIZES = (1000, 2000, 4000, 8000, 16000, 32000, 64000)
CUTOFFS = (1, 4, 8, 16, 32, 64)
TRIALS = 3
TIMEOUT = 5
SEED = 302


def worker(connection, values, algorithm, cutoff, seed):
    random.seed(seed)
    data = values.copy()
    try:
        start = time.perf_counter()
        if algorithm == 'basic':
            quicksort_basic(data)
        elif algorithm == 'improved':
            quicksort_improved(data, cutoff)
        else:
            data = sorted(data)
        elapsed = time.perf_counter() - start
        if data != sorted(values):
            raise AssertionError('Incorrect output')
        connection.send(('ok', elapsed))
    except RecursionError:
        connection.send(('crash', None))
    except Exception as error:
        connection.send(('error: ' + repr(error), None))
    finally:
        connection.close()


def measure(values, algorithm, cutoff=16):
    times = []
    context = mp.get_context('spawn')
    for trial in range(TRIALS):
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(target=worker, args=(
            sender, values, algorithm, cutoff, SEED + trial))
        process.start()
        sender.close()
        process.join(TIMEOUT)
        if process.is_alive():
            process.terminate()
            process.join()
            status, elapsed = 'timeout', None
        elif receiver.poll():
            status, elapsed = receiver.recv()
        else:
            status, elapsed = 'process_error', None
        receiver.close()
        if status != 'ok':
            return dict(status=status, median_seconds='', completed_trials=len(times),
                        trial_seconds=';'.join(map(str, times)))
        times.append(elapsed)
    return dict(status='ok', median_seconds=statistics.median(times),
                completed_trials=len(times), trial_seconds=';'.join(map(str, times)))


def save(name, rows):
    with open(name, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def graphs(timings, cutoffs):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for kind in ('random', 'sorted', 'duplicates'):
        fig, ax = plt.subplots(figsize=(5.6, 2.5), layout='constrained')
        for algorithm, color in [('basic', 'tab:blue'), ('improved', 'tab:orange')]:
            rows = [r for r in timings if r['input_type'] == kind and r['algorithm'] == algorithm]
            ax.plot([r['n'] for r in rows],
                    [r['median_seconds'] if r['status'] == 'ok' else float('nan') for r in rows],
                    'o-', label=algorithm, color=color, markersize=3)
            for status, marker in [('crash', 'x'), ('timeout', 's')]:
                failed = [r['n'] for r in rows if r['status'] == status]
                if failed:
                    ax.scatter(failed, [0.94] * len(failed), transform=ax.get_xaxis_transform(),
                               marker=marker, color=color, label=f'{algorithm}: {status}')
        ax.set(xscale='log', yscale='log', xlabel='Input size (n)',
               ylabel='Execution time (seconds)', title=f'Quicksort: {kind} data')
        ax.legend(fontsize=7)
        ax.grid(alpha=.25)
        fig.savefig(f'{kind}_performance.png', dpi=180)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.6, 2.5), layout='constrained')
    ax.plot([r['cutoff'] for r in cutoffs], [r['median_seconds'] for r in cutoffs], 'o-')
    ax.set(xlabel='Insertion-sort cutoff', ylabel='Execution time (seconds)',
           title='Cutoff comparison: 100,000 random integers', xticks=CUTOFFS)
    ax.grid(alpha=.25)
    fig.savefig('cutoff_performance.png', dpi=180)
    plt.close(fig)


def main():
    timings = []
    for kind in ('random', 'sorted', 'duplicates'):
        for n in SIZES:
            rng = random.Random(SEED + n)
            values = (list(range(n)) if kind == 'sorted' else
                      [rng.randrange(10 if kind == 'duplicates' else 1000000) for _ in range(n)])
            for algorithm in ('basic', 'improved'):
                row = dict(input_type=kind, n=n, algorithm=algorithm, cutoff=16)
                row.update(measure(values, algorithm))
                timings.append(row)
                print(kind, n, algorithm, row['status'], row['median_seconds'], flush=True)
    save('timing_results.csv', timings)
    rng = random.Random(SEED)
    values = [rng.randrange(1000000) for _ in range(100000)]
    cutoffs = []
    for cutoff in CUTOFFS:
        row = dict(n=len(values), cutoff=cutoff)
        row.update(measure(values, 'improved', cutoff))
        cutoffs.append(row)
    save('cutoff_results.csv', cutoffs)
    if any(row['status'] != 'ok' for row in cutoffs):
        raise RuntimeError('Cutoff experiment incomplete; inspect cutoff_results.csv')
    best = min(cutoffs, key=lambda row: row['median_seconds'])['cutoff']
    comparisons = []
    for algorithm in ('improved', 'sorted'):
        row = dict(n=len(values), algorithm=algorithm, cutoff=best if algorithm == 'improved' else '')
        row.update(measure(values, algorithm, best))
        comparisons.append(row)
    if any(row['status'] != 'ok' for row in comparisons):
        raise RuntimeError('Python comparison failed')
    ratio = comparisons[0]['median_seconds'] / comparisons[1]['median_seconds']
    for row in comparisons:
        row['improved_over_sorted_ratio'] = ratio
    save('python_comparison.csv', comparisons)
    graphs(timings, cutoffs)
    Path('environment.txt').write_text(
        f'Python: {sys.version}\nPlatform: {platform.platform()}\n'
        f'Recursion limit: {sys.getrecursionlimit()}\nTrials: {TRIALS}\n'
        f'Seed: {SEED}; pivot seeds: 302, 303, 304\n'
        f'Timeout: {TIMEOUT}s per worker including startup and verification\n')
    print('Best cutoff:', best, 'Improved/sorted ratio:', ratio)


if __name__ == '__main__':
    main()
