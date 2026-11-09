"""Build report.md and a four-page report.pdf from measured CSV evidence."""
import csv
import re
from pathlib import Path
from xml.sax.saxutils import escape


def read(name):
    with open(name, newline='') as handle:
        return list(csv.DictReader(handle))


def seconds(row):
    return f"{float(row['median_seconds']):.6f}" if row['status'] == 'ok' else row['status'].upper()


def main():
    timings = read('timing_results.csv')
    cutoffs = read('cutoff_results.csv')
    comparison = read('python_comparison.csv')
    best = min(cutoffs, key=lambda row: float(row['median_seconds']))
    ratio = float(comparison[0]['improved_over_sorted_ratio'])
    table = '| n | Random B / I | Sorted B / I | Duplicates B / I |\n|---:|---|---|---|\n'
    for n in (1000, 2000, 4000, 8000, 16000, 32000, 64000):
        cells = []
        for kind in ('random', 'sorted', 'duplicates'):
            cells.append(' / '.join(seconds(r) for r in timings
                                    if r['input_type'] == kind and int(r['n']) == n))
        table += f"| {n:,} | " + ' | '.join(cells) + ' |\n'
    cutoff_table = '| Cutoff | 1 | 4 | 8 | 16 | 32 | 64 |\n|---|---|---|---|---|---|---|\n| Median seconds | ' + ' | '.join(seconds(r) for r in cutoffs) + ' |'
    crash_count = sum(r['status'] == 'crash' for r in timings)
    def timing(kind, n, algorithm):
        return seconds(next(r for r in timings if r['input_type'] == kind and int(r['n']) == n and r['algorithm'] == algorithm))
    reflection = f'''**Question 1: Why did the basic algorithm fail?** On ascending transaction amounts, the final pivot is always the maximum. Lomuto therefore leaves an almost unchanged subproblem and creates linear recursion depth. In these experiments, {crash_count} basic input-size cases raised RecursionError, including {sum(r['status'] == 'crash' and r['input_type'] == 'sorted' for r in timings)} ascending cases; the largest ascending case had status {next(r['status'] for r in timings if r['input_type'] == 'sorted' and r['n'] == '64000' and r['algorithm'] == 'basic')}. The average-case analysis assumes random relative input order, or an equivalent source of pivot randomness; the bank's already ordered records break that assumption. Repeated top-ups also concentrate equal keys on one side in the basic version. Random pivots help with order, while three-way partitioning directly addresses duplicates.

**Question 2: Why use insertion sort?** A quadratic algorithm can still be useful on a short partition because it avoids further partitioning, pivot selection and function calls. For fixed cutoff k, insertion work across the small partitions is O(nk). The measured fastest cutoff was {best['cutoff']}, with a median of {seconds(best)} seconds for 100,000 random integers. This is a result for this implementation and machine, not a universal optimum. A bank should remeasure with representative transaction data before selecting its cutoff.

**Question 4: How was AI assistance checked?** ChatGPT/Codex assisted with the implementation, tests, benchmark and explanation. Automated checks compared both algorithms with Python's sorted() on 500 reproducible random inputs and explicit edge cases. The benchmark independently verified every successful output and preserved crashes as missing times. This checks correctness and measured behavior, but cannot replace understanding the partition invariants or reviewing experimental design. Student review required: personally rerun the commands, inspect the code and CSV evidence, and confirm this declaration accurately describes your use of AI before submission.'''
    assert len(reflection.split()) <= 400
    document = f'''# Assignment 3: Fixing a Slow Quicksort

**AI Use Declaration:** OpenAI ChatGPT/Codex was used to assist with Python implementation, test development, performance benchmarking, and explanation of algorithmic concepts. All generated code and experimental results will be reviewed and verified by the student before submission.

## 1. Introduction

A bank in Thimphu sorts mobile-payment amounts. Already ordered records and repeated Nu. 100 and Nu. 500 top-ups expose basic quicksort's worst case. This experiment compares a last-pivot implementation with a randomized, duplicate-aware version, measuring correctness, speed and practical limits.

## 2. Implementation

**Basic:** sorts.py uses Lomuto partitioning. A boundary separates amounts no greater than the last-element pivot from larger amounts. After scanning, the pivot moves to its final position, and both sides are recursively sorted. Balanced partitions give T(n) = 2T(n/2) + Θ(n) = Θ(n log n). For random distinct-key permutations, averaging pivot ranks also gives Θ(n log n). This average does not cover every repeated-key distribution. Extremely unbalanced partitions give Θ(n²) time and Θ(n) stack space.

**Improved:** select a random pivot and partition into less-than, equal-to and greater-than regions. The equal region needs no further sorting; all-equal data takes Θ(n) time. Use insertion sort for partitions at most cutoff elements long. Recurse only on the smaller unequal region, then loop over the larger. Each recursive child is at most half its parent's size, giving O(log n) stack depth regardless of pivot quality. Expected time for fixed cutoff is O(n log n); worst-case time remains O(n²). Both versions modify the supplied list and return None, without built-in sorting or array slices inside the algorithms.

## 3. Testing Results

The executed unittest suite passed all four test methods. It checks 500 seeded random lists of lengths 0–200 against sorted(), using basic quicksort and six improved cutoffs (1, 4, 8, 16, 32, 64): 3,500 random algorithm/cutoff checks. Additional cases cover empty, singleton, all-equal, ascending, descending, negative, repeated and mixed-sign inputs. Tests check alias-visible mutation, unchanged list identity, None returns and agreement between algorithms. The improved version also passed three 10,000-element ordered/equal cases; invalid cutoffs raise ValueError. Small basic test inputs avoid intentional stack failure.

**Environment and reproduction:** CPython 3.14.4, macOS 26.5, ARM64; default recursion limit 1,000. Run `.venv/bin/python -m unittest -v`, then `MPLCONFIGDIR=/tmp/quicksort-mpl .venv/bin/python benchmark.py`. Full metadata is in environment.txt. Timings are machine-specific wall-clock measurements, not theoretical operation counts.

<!-- pagebreak -->

## 4. Performance Analysis

**Table 1. Median seconds, three trials where successful.** B = basic, I = improved (cutoff 16). CRASH means actual RecursionError; it is not a zero timing.

{table}

Inputs are shared between algorithms, with fresh copies per run. Random values span 0–999,999; duplicate values span 0–9. Input seeds are 302 + n; pivot seeds are 302–304. Only sorting is timed with perf_counter(); copying, process startup and sorted() verification are excluded. Each case runs independently in fresh processes. A five-second worker timeout includes startup/verification; first crash or timeout ends that case. Successful medians require three completed trials. CSVs retain status, completed counts and trial times. Basic was faster on random data ({timing('random', 64000, 'basic')} s versus {timing('random', 64000, 'improved')} s at n = 64,000). With 8,000 duplicate-heavy values, improved took {timing('duplicates', 8000, 'improved')} s versus basic's {timing('duplicates', 8000, 'basic')} s. There were {crash_count} crashes, {sum(r['status'] == 'timeout' for r in timings)} timeouts and no skipped cases. Failures have blank CSV timing cells.

![Figure 1. Random data; median seconds.](random_performance.png)

![Figure 2. Ascending data; crosses = crashes, square = timeout (no time values).](sorted_performance.png)

![Figure 3. Duplicate-heavy data; crosses mark crashes, with no time value.](duplicates_performance.png)

<!-- pagebreak -->

## 5. Worst-Case Recurrence Analysis

On ascending input, the last pivot is the maximum. All n − 1 preceding values pass Lomuto's <= test, leaving partitions of sizes n − 1 and zero. Scanning the partition costs Θ(n), even though the data is already ordered. Thus T(n) = T(n − 1) + Θ(n), with a constant-size base case. Expanding gives Θ(n + (n − 1) + ... + 1) = Θ(n(n + 1)/2) = Θ(n²). There are Θ(n) nested calls, so Python's finite recursion limit causes RecursionError. With all equal amounts, the <= test again puts every other element on one side; randomizing the pivot alone cannot fix this. Three-way partitioning removes all copies of a pivot value together, making repeated bank top-ups inexpensive.

## 6. Cutoff Optimization

**Table 2. Three-trial medians on the same 100,000 random integers.**

{cutoff_table}

![Figure 4. Insertion-sort cutoff experiment.](cutoff_performance.png)

The measured best cutoff is **{best['cutoff']}**, at **{seconds(best)} seconds**. Small insertion sorts avoid recursive partitioning overhead and have simple loops. Their quadratic cost is bounded by the small partition size: across leaves the cost is O(nk) for cutoff k. Very large cutoffs increase shifting work. This small experiment does not establish statistical significance or a universal best cutoff.

## 7. Comparison with Python's sorted()

On the same seeded 100,000-element input, a separate three-trial comparison measured improved quicksort (cutoff {best['cutoff']}) at **{seconds(comparison[0])} s** and sorted() at **{seconds(comparison[1])} s**. The ratio improved / sorted is **{ratio:.2f}**, so sorted() was {ratio:.2f} times faster. sorted() includes allocating its result; both exclude input copying. CPython's adaptive Timsort exploits existing runs and executes optimized C code; our swaps, comparisons, loops and calls execute through Python. This experiment cannot numerically separate algorithmic effects from language overhead. sorted() produces a new list and is stable; our quicksorts are in place and unstable.

<!-- pagebreak -->

## 8. Critical Reflection

{reflection}

## 9. Conclusion

Random pivot selection reduces sensitivity to input order, three-way partitioning handles repeated amounts, and smaller-side recursion bounds stack growth. The basic version's observed failures explain why a method that works on random payments may fail on routine bank data. The measured cutoff {best['cutoff']} performed best in the cutoff sweep; Python's sorted() was faster in the direct comparison. The evidence supports the improved implementation for this assignment, while a bank using Python should also consider the built-in stable sorter.

**Student action before submission:** review the AI declaration and reflection, rerun tests and benchmarks if required by the course, add your name/student number, and submit sorts.py, test_sorts.py and report.pdf. The scripts, CSVs and four PNGs remain supporting evidence. Submission timing and final approval belong to the student.
'''
    Path('report.md').write_text(document)
    render_pdf(document)
    print('Reflection words:', len(reflection.split()))


def render_pdf(document):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 9
    styles['Normal'].leading = 12
    styles['Normal'].spaceAfter = 7
    styles['Heading1'].fontSize = 15
    styles['Heading2'].fontSize = 11
    styles['Heading2'].spaceBefore = 8
    def markup(text):
        text = escape(text)
        # Standard built-in PDF fonts lack these mathematical glyphs.
        for old, new in [('Θ', 'Theta'), ('²', '^2'), ('−', '-'), ('–', '-'), ('≤', '&lt;=')]:
            text = text.replace(old, new)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text.replace('`', '')
    story = []
    for block in document.strip().split('\n\n'):
        if block == '<!-- pagebreak -->':
            story.append(PageBreak())
        elif block.startswith('# '):
            story.append(Paragraph(markup(block[2:]), styles['Heading1']))
        elif block.startswith('## '):
            story.append(Paragraph(markup(block[3:]), styles['Heading2']))
        elif block.startswith('|'):
            rows = [[Paragraph(markup(cell.strip()), styles['Normal']) for cell in line.strip('|').split('|')]
                    for line in block.splitlines() if not re.match(r'^\|[-:| ]+\|$', line)]
            table = Table(rows, hAlign='LEFT')
            table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .35, colors.lightgrey),
                                       ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 5),
                                       ('RIGHTPADDING', (0, 0), (-1, -1), 5)]))
            story.extend([table, Spacer(1, 6)])
        elif block.startswith('!['):
            caption, path = re.match(r'!\[(.*?)\]\((.*?)\)', block).groups()
            width = 270 if 'cutoff' not in path else 340
            story.extend([Image(path, width=width, height=width * 2.5 / 5.6),
                          Paragraph(markup(caption), styles['Normal'])])
        else:
            story.append(Paragraph(markup(block), styles['Normal']))
    pages = []
    def footer(canvas, doc):
        pages.append(doc.page)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 42, 23, str(doc.page))
    doc = SimpleDocTemplate('report.pdf', pagesize=A4, rightMargin=42, leftMargin=42,
                            topMargin=32, bottomMargin=32)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    assert len(pages) == 4, f'Expected four pages, got {len(pages)}; adjust layout'
    print('Verified PDF page count:', len(pages))


if __name__ == '__main__':
    main()
