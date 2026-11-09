"""Run 1,000 revenue experiments and build the report: python analysis.py."""
import csv
import os
import platform
import random
import statistics
import sys
import textwrap
from pathlib import Path
from booking import greedy_earliest_finish, greedy_highest_fee, best_schedule, brute_force
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    examples = []
    for name, fn, requests, explanation in [
        ('Earliest finish', greedy_earliest_finish, [(0, 2, 3), (0, 3, 8)],
         'The early booking blocks the overlapping booking worth 8.'),
        ('Highest fee', greedy_highest_fee, [(0, 4, 7), (0, 2, 4), (2, 4, 4)],
         'The fee of 7 blocks two compatible bookings worth 8 together.')]:
        g, d = fn(requests), best_schedule(requests)
        assert d[0] == brute_force(requests)[0] and g[0] < d[0]
        examples.append(f'{name}: requests {requests}. Greedy {g}; optimal {d}; '
                        f'loss {d[0]-g[0]}. {explanation}')
        print(examples[-1])
    rng = random.Random(302)
    rows = []
    for trial in range(1, 1001):
        requests = []
        for _ in range(50):
            s = rng.randint(0, 99)
            requests.append((s, s + rng.randint(1, 20), rng.randint(0, 10000)))
        a, b, d = [fn(requests)[0] for fn in
                   (greedy_earliest_finish, greedy_highest_fee, best_schedule)]
        assert 0 <= a <= d and 0 <= b <= d
        rows.append(dict(trial=trial, earliest_fee=a, highest_fee=b, optimal_fee=d,
                         earliest_ratio=a/d if d else 1., highest_ratio=b/d if d else 1.))
    with (ROOT/'revenue_results.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    means = [statistics.mean(r[k] for r in rows) for k in ('earliest_ratio', 'highest_ratio')]
    worst = [min(r[k] for r in rows) for k in ('earliest_ratio', 'highest_ratio')]
    fig, ax = plt.subplots(figsize=(6.5, 2.8))
    ax.bar([-.18, .82], means, .36, label='Average')
    ax.bar([.18, 1.18], worst, .36, label='Worst observed')
    ax.set(xticks=[0, 1], xticklabels=['Earliest finish', 'Highest fee'],
           xlabel='Greedy algorithm', ylabel='Revenue / optimal revenue', ylim=(0, 1.15),
           title='Hall bookings: 1,000 seeded sets of 50 requests')
    for x, value in zip([-.18, .82, .18, 1.18], means + worst):
        ax.text(x, value+.02, f'{value:.4f}', ha='center', fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT/'revenue_comparison.png', dpi=180)
    plt.close(fig)
    declaration = ('AI Use Declaration: OpenAI ChatGPT/Codex was used to assist with Python implementation, '
                   'test development, experimental analysis, and explanation of greedy and dynamic programming '
                   'algorithms. All generated code and experimental results will be reviewed and verified by the student before submission.')
    sections = [
    ('1. Introduction', 'The Paro community hall receives requests (start, finish, fee). Only one event can '
     'occupy the hall at a time; a finish equal to the next start is compatible. The objective is maximum '
     'revenue. Two greedy rules are compared with weighted interval dynamic programming (DP) and exhaustive search.'),
    ('2. Algorithm Implementation',
     'Earliest finish sorts by (finish, start, original index) and accepts each compatible request. With '
     'equal positive fees, it maximizes activity count: exchange the first activity in an optimal schedule '
     'for the earliest-finishing one. This leaves at least as much room for later bookings; repeat on '
     'the remaining activities. Unequal fees invalidate the revenue conclusion.\n\n'
     'Highest fee sorts by descending fee, breaking ties by original index, and checks each candidate '
     'against every accepted booking. One large fee can block a more valuable combination.\n\n'
     'DP uses finish sorting, binary-searched predecessors, a revenue table and backwards reconstruction. '
     'On equal include/exclude revenue it excludes the later finish-sorted booking. Brute force independently '
     'enumerates every finish-order subset bitmask, keeping the first maximum. Both have deterministic ties. '
     'Output indices are original indices in chronological order; input lists are unchanged. The assumed '
     'domain is start < finish with nonnegative fees. Brute force rejects n > 15.'),
    ('3. Testing Results',
     'Five unittest methods passed on 9 November 2026. They include 500 random inputs of size 0-10 '
     '(seed 302), comparing DP with independent brute force, and 200 random equal-positive-fee inputs '
     '(seed 304), confirming earliest finish equals optimal revenue. Tests cover empty and singleton '
     'inputs, all-overlapping and nonoverlapping requests, back-to-back bookings, unequal/equal/zero '
     'fees, shared start/finish times, duplicate requests, multiple optima and both greedy failures. '
     'Every algorithm is checked for valid original indices, no duplicate selections, compatibility, '
     'fee sums, repeatability and unchanged input. The brute-force limit is tested at 15 and above it. '
     'Tests supply evidence, not a proof for every possible input.'),
    ('4. Greedy Counterexamples', '\n\n'.join(examples) + '\n\nOutputs are (total fee, original indices). '
     'Both optimal revenues were verified by exhaustive enumeration.'),
    ('5. Dynamic Programming Analysis',
     'Number finish-sorted requests 1 through n. OPT(j) is maximum revenue among the first j requests, '
     'with OPT(0)=0. fee_j is booking j\'s fee. p(j) is the last preceding booking finishing no later '
     'than j starts, or 0 if none. In code, bisect_right returns the count of such preceding bookings: '
     'this count is exactly their prefix index in the 1-based DP table. Search excludes j itself.\n\n'
     'OPT(j) = max(OPT(j-1), fee_j + OPT(p(j))).\n\n'
     'An optimal schedule either excludes j, giving OPT(j-1), or includes j, leaving only its compatible '
     'prefix available. The prefix schedule must be optimal: replacing it by a better prefix schedule '
     'would improve the whole solution. Therefore inclusion gives fee_j + OPT(p(j)), and the maximum '
     'is optimal by induction. This is optimal substructure. Storing each prefix once avoids repeated '
     'calculations. Reconstruction follows an inclusion to p(j), otherwise to j-1.\n\n'
     'Example in finish order: (0,2,4), (0,4,7), (2,4,4). Here p=[0,0,1] and '
     'OPT=[0,4,7,8]. Including the last booking yields 4+OPT(1)=8 rather than 7.'),
    ('6. Revenue Ratio Analysis',
     'Exactly 1,000 sets of 50 requests use random.Random(302). Independent inclusive integer draws '
     'give start 0-99, duration 1-20 and fee Nu. 0-10,000; finish=start+duration. Time uses synthetic '
     'units, not a daily opening-hours model. Each trial gives identical inputs to both greedy rules '
     'and DP; brute force is excluded. Ratio=greedy/optimal; zero optimum is assigned ratio 1 because '
     'both revenues are zero. No greedy revenue exceeded optimal revenue. Every trial is saved in CSV.\n\n'
     '| Algorithm | Average ratio | Worst observed ratio |\n|---|---:|---:|\n'
     f'| Earliest finish | {means[0]:.6f} | {worst[0]:.6f} |\n'
     f'| Highest fee | {means[1]:.6f} | {worst[1]:.6f} |\n\n'
     'Figure 1 uses decimal ratios; 1 means optimal revenue. The minimum observed ratio is a sample '
     'statistic, not a theoretical worst-case guarantee.'),
    ('7. Time Complexity Comparison',
     '| Algorithm | Time | Auxiliary space |\n|---|---|---|\n'
     '| Earliest finish | O(n log n) | O(n) |\n| Highest fee | O(n²) | O(n) |\n'
     '| DP | O(n log n) | O(n) |\n| Brute force | O(n × 2ⁿ) | O(n) |\n\n'
     'Earliest finish sorts then scans once. Highest fee sorts and can perform O(n) compatibility '
     'checks for each candidate; final output sorting is dominated by O(n²). DP sorting and n '
     'binary searches cost O(n log n); filling and reconstructing each cost O(n). Brute force sorts '
     'once and scans at most n bookings per subset in finish order. Adjacent checks suffice for '
     'compatibility. It stores one subset at a time. Exponential growth prevents large-input use.'),
    ('8. Critical Reflection',
     '**Question 1: What do passing tests establish?** Passing tests cannot prove a greedy rule '
     'correct on every input. The earliest-finish example loses 5, while highest fee loses 1. A '
     'single counterexample disproves universal optimality. Brute-force comparisons on 500 small '
     'random inputs help find DP errors; the include/exclude proof supplies general justification.\n\n'
     '**Question 2: Should the manager keep the simple rule?** '
     f'Earliest finish averaged {means[0]:.6f} of optimal revenue, with minimum {worst[0]:.6f}; '
     f'highest fee averaged {means[1]:.6f}, with minimum {worst[1]:.6f}. '
     'These losses favor DP for revenue. Earliest finish remains appropriate for maximizing booking '
     'count with equal positive fees. Greedy rules are simple, but neither guarantees weighted '
     'optimality. DP has the same asymptotic time bound as earliest finish here. Real demand may '
     'produce different ratios from synthetic requests.\n\n'
     '**Question 4: How was AI assistance checked?** AI helped with implementation, tests and '
     'explanation. No claim is made that AI previously called a greedy rule optimal. Both small '
     'counterexamples were exhaustively checked, DP was compared against brute force, and the '
     '1,000 experiments checked greedy revenues against DP. Student review remains necessary: '
     'run the commands, inspect the code and CSV, understand the recurrence and confirm the '
     'declaration accurately reflects actual AI use.'),
    ('9. Conclusion',
     'Weighted interval DP maximizes revenue for this model. Earliest finish optimizes activity '
     'count with equal positive fees; highest fee can miss valuable combinations. The manager '
     'should use DP for revenue and check whether real operating constraints require an expanded model.')]
    environment = f'Verified environment: Python {sys.version.split()[0]}, {platform.platform()}; matplotlib {matplotlib.__version__}.'
    md = '# Assignment 4: Booking the Hall\n\n**AI Use Declaration:** ' + declaration.split(': ',1)[1] + '\n\n'
    md += '**Student:** Yeshey Lhaden (02240371)\n\n'
    md += '## Table of Contents\n\n'
    for heading, _ in sections:
        number, label = heading.split('. ', 1)
        anchor = heading.lower().replace('.', '').replace(' ', '-')
        md += f'{number}. [{label}](#{anchor})\n'
    md += '\n'
    for heading, body in sections:
        md += f'## {heading}\n\n{body}\n\n'
        if heading.startswith('6.'):
            md += '![Figure 1. Average and worst observed revenue ratios.](revenue_comparison.png)\n\n'
    (ROOT/'report.md').write_text(md + environment + '\n')
    # Fixed layout using matplotlib's PDF backend; no additional PDF dependency.
    with PdfPages(ROOT/'report.pdf') as pdf:
        for page, group in enumerate([sections[:3], sections[3:5], sections[5:7], sections[7:]],1):
            fig = plt.figure(figsize=(8.27,11.69))
            y = .95
            def paragraph(text, size=9):
                nonlocal y
                for line in text.replace('**','').splitlines():
                    for part in textwrap.wrap(line, width=94) or ['']:
                        fig.text(.065,y,part,fontsize=size,family='DejaVu Sans Mono',va='top')
                        y -= .014
                y -= .004
            if page==1:
                paragraph('Assignment 4: Booking the Hall',13)
                paragraph('Yeshey Lhaden (02240371)')
                paragraph(declaration)
                paragraph('Table of Contents', 11)
                for heading, _ in sections:
                    paragraph(heading, 8)
            for heading, body in group:
                paragraph(heading,11)
                paragraph(body)
            if page==3:
                assert y > .32, y
                ax = fig.add_axes([.12,.075,.76,.24])
                ax.imshow(plt.imread(ROOT/'revenue_comparison.png'))
                ax.axis('off')
            if page==4:
                paragraph(environment,8)
                paragraph('Student action: review code, results, reflection and declaration; submit booking.py, test_booking.py and report.pdf.')
            assert y > .055, (page,y)
            fig.text(.5,.035,f'{page} / 4',ha='center',fontsize=9)
            pdf.savefig(fig)
            plt.close(fig)
    print('Average ratios:',means,'Worst ratios:',worst)
    print('Saved 1,000 trials, graph, report.md and four-page report.pdf.')

if __name__ == '__main__':
    main()
