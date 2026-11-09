# Assignment 3 evidence and reproduction

Submit `sorts.py`, `test_sorts.py`, and `report.pdf`. The PDF has an explicitly checked four-page layout; arbitrary Markdown converters may paginate `report.md` differently. Review the declaration/reflection and add your student details before submitting.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest -v
MPLCONFIGDIR=/tmp/quicksort-mpl .venv/bin/python benchmark.py
.venv/bin/python build_report.py
```

`benchmark.py` overwrites the CSVs and graphs with fresh measurements. `build_report.py` reads the CSVs and updates the report and PDF. Preserve the original evidence if comparing machines. Values in the report are rounded to six decimal places; CSVs retain full precision. Trial order is fixed, not randomized, and three trials provide only a small sample. Remeasure close cutoff results before claiming a general optimum.

The original benchmark saved all CSVs before its graph import failed because dependency installation was still running. After installation, the four graphs were generated directly from those saved CSVs. No timing values were replaced or invented. `benchmark.log` preserves the first run, including that error; `environment.txt` documents recovery.

## Viva notes

- Basic Lomuto: before index j, values before boundary are <= pivot and the inspected values after boundary are > pivot. Swapping in the last pivot puts it between those regions. Both recursive subproblems are smaller.
- Improved partition: lt marks the start of equal keys, i the first unexamined key, and gt the last unexamined key. Swapping a large value with gt does not advance i because the incoming value is unexamined. Equal keys are finished together.
- Insertion sort: the prefix within a small partition is already ordered. Shift larger prefix values right and insert the saved value into the gap.
- Smaller-side recursion: at most half the unequal keys enter a recursive child. The larger side is processed by updating lo/hi in the current call. Depth is logarithmic even if runtime becomes quadratic.
- Random pivots reduce order sensitivity; they do not guarantee balanced partitions. Three-way partitioning supplies the separate benefit for repeated amounts. The improved version was slower on the measured random inputs, but faster and more robust on the bank's problematic data.
- CRASH is an observed RecursionError. TIMEOUT means the worker was stopped at five seconds; it does not prove a later crash. Blank timing cells represent failures, never zero seconds.

## Rubric review

- Analysis/problem-solving (5): all 42 size/distribution/algorithm cases recorded; recurrence derived; six cutoffs measured; built-in comparison measured; exactly questions 1, 2 and 4 reflected on in under 400 words.
- Application (5): two in-place algorithms, required pivot rules, insertion cutoff, three-way partitioning, smaller-side recursion; 500 random cases plus edge, large improved and cutoff checks passed.
- Presentation (3): commented code; timing tables, four labelled graphs; measured environment; four-page PDF and Markdown source; AI declaration.
- Submission/correctness (2): all requested files generated and code executed. Student must review, add identity details, and submit by the course deadline; no submission or grade is claimed here.
