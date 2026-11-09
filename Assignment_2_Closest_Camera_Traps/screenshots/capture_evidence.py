"""Render authentic output transcripts as PNGs; these are not desktop captures.

Run with .venv/bin/python screenshots/capture_evidence.py.
Benchmarks are read from the saved CSV, not rerun or estimated.
"""
import csv
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
import matplotlib

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'screenshots'
FONT = Path(matplotlib.get_data_path()) / 'fonts/ttf/DejaVuSansMono.ttf'


def render(name, title, transcript):
    font = ImageFont.truetype(str(FONT), 18)
    lines = [title, ''] + transcript.rstrip().splitlines()
    width = max(1000, int(max(font.getlength(line) for line in lines)) + 48)
    image = Image.new('RGB', (width, 48 + 26 * len(lines)), '#f8fafc')
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((24, 20 + 26 * i), line, font=font, fill='#172033')
    image.save(OUT / (name + '.png'))
    (OUT / (name + '.txt')).write_text(transcript)


result = subprocess.run([sys.executable, '-m', 'unittest', '-v'], cwd=ROOT,
                        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
transcript = '$ python3 -m unittest -v\n' + result.stdout
render('test_results', 'Executed unittest output (rendered transcript)', transcript)
if result.returncode:
    raise SystemExit(result.returncode)

rows = list(csv.DictReader((ROOT / 'timing_results.csv').open()))
lines = ['Source: timing_results.csv (saved measurements; no rerun)', '',
         '       n    brute (s)   divide (s)   trials B/D   brute status']
for row in rows:
    brute = f"{float(row['brute_median_s']):.6f}" if row['brute_median_s'] else 'skipped'
    lines.append(f"{int(row['n']):8,d}  {brute:>11}  {float(row['divide_median_s']):11.6f}"
                 f"       {row['brute_trials']}/{row['divide_trials']}     {row['brute_status']}")
crossover = next((row['n'] for row in rows if row['brute_median_s'] and
                  float(row['divide_median_s']) < float(row['brute_median_s'])), None)
lines += ['', f'Smallest tested n where divide-and-conquer is faster: {crossover}',
          'Times are medians; skipped values are not estimated.']
render('benchmark_summary', 'Saved benchmark results (rendered CSV summary)', '\n'.join(lines) + '\n')
print('Tests passed. Created two PNGs and their source transcripts in screenshots/.')
