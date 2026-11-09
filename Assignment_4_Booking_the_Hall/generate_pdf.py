"""Render current report.md to a four-page A4 report.pdf using matplotlib.
Run with a Python environment containing matplotlib: python generate_pdf.py
"""
import os
import re
import textwrap
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def main():
    source = (ROOT / 'report.md').read_text()
    if 'Assignment 4:' in source:
        markers = ['## 4. Greedy Counterexamples', '## 6. Revenue Ratio Analysis',
                   '## 8. Critical Reflection']
        starts = [0] + [source.index(m) for m in markers] + [len(source)]
        pages = [source[a:b] for a,b in zip(starts,starts[1:])]
    elif 'Assignment 3:' in source:
        markers = ['## 4. Performance Analysis', '## 5. Worst-Case Recurrence Analysis',
                   "## 7. Comparison with Python's sorted()"]
        starts = [0] + [source.index(m) for m in markers] + [len(source)]
        pages = [source[a:b] for a,b in zip(starts,starts[1:])]
    else:
        pages = re.split(r'<div style="page-break-before: always;"></div>', source)
    assert len(pages) == 4, len(pages)
    with PdfPages(ROOT / 'report.pdf') as pdf:
        for number, content in enumerate(pages, 1):
            pictures = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            content = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', content)
            content = re.sub(r'<!--.*?-->', '', content, flags=re.S)
            lines = []
            for raw in content.splitlines():
                raw = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw)
                raw = raw.replace('**', '').replace('`', '')
                if raw.startswith('|') and re.fullmatch(r'[| :\-]+', raw):
                    continue
                is_heading = raw.startswith('#')
                raw = re.sub(r'^#+\s*', '', raw)
                if not raw.strip():
                    if lines and lines[-1][0]:
                        lines.append(('',False))
                    continue
                for part in textwrap.wrap(raw, width=88):
                    lines.append((part, is_heading))
            # Reserve bottom space for figures; text remains 9pt or larger.
            figure_height = .31 if len(pictures) == 1 else .40 if pictures else 0
            text_bottom = .07 + figure_height
            available = .95 - text_bottom
            step = min(.015, available / max(1, len(lines)))
            fontsize = min(10, step * 841.68 / 1.15)
            assert fontsize >= 8.5, (number, fontsize, len(lines))
            fig = plt.figure(figsize=(8.27,11.69))
            y = .955
            for line, heading in lines:
                fig.text(.055,y,line,fontsize=fontsize,
                         weight='bold' if heading else 'normal',
                         family='DejaVu Sans Mono',va='top')
                y -= step
            if pictures:
                if len(pictures) == 1:
                    slots = [[.12,.065,.76,figure_height-.02]]
                elif len(pictures) == 2:
                    slots = [[.07,.065 + k*.20,.86,.19] for k in [1,0]]
                else:
                    slots = [[.04,.265,.45,.18],[.51,.265,.45,.18],[.26,.065,.48,.18]]
                for (caption,path), slot in zip(pictures, slots):
                    ax=fig.add_axes(slot)
                    ax.imshow(plt.imread(ROOT/path))
                    ax.axis('off')
                    ax.set_title(caption,fontsize=6,wrap=True)
            fig.text(.5,.025,f'{number} / 4',ha='center',fontsize=9)
            pdf.savefig(fig)
            plt.close(fig)
            print(f'Page {number}: {len(lines)} lines, {fontsize:.1f}pt, {len(pictures)} figures')
    print('Created', ROOT/'report.pdf')


if __name__ == '__main__':
    main()
