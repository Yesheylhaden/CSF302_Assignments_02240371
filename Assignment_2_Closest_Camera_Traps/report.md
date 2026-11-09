# CSF302 — Assignment 2: Closest Camera Traps

**Student:** Yeshey Lhaden (02240371)  
**Experiment date:** 2 November 2026

## Table of Contents

1. [Implementation and correctness](#implementation-and-correctness)
2. [Recurrence analysis](#recurrence-analysis)
3. [Validation and measured performance](#validation-and-measured-performance)
4. [Critical reflection](#critical-reflection-three-questions-under-400-words)
5. [Reproduce and prepare submission](#reproduce-and-prepare-submission)
6. [Execution evidence](#execution-evidence)
   - [Test results](#test-results)
   - [Benchmark evidence](#benchmark-evidence)
7. [Conclusion](#conclusion)

## Implementation and correctness

In both cases, `closest.py` will output `(d, i, j)` where the values are zero-based indexing such that `i < j`. In case of ties for distances, then the choice will be made on the lexicographically smaller `(i, j)`, for example, `(0, 3)` over `(1, 2)`. If less than two points are given, an error message is raised, `ValueError`.

For the function `closest_pair_brute`, all pairs are iterated through, their distances are found, and then the smallest `(distance, i, j)` is returned. The comparison works from left to right in tuples in Python.

The `closest_pair` algorithm adds a prefix to each input index while sorting. `closest_pair` sorts twice, once by x and once by y. The x-rank dictionary is used to decide which half the point is on, even in the case when there are many equal x-coordinates. Brute force is used for solving problems with three points or less.

This recursive computation gives a bound on the distance, delta. If a pair crosses the boundary and is close to each other, then that pair must be situated in the strip of width delta near this line. This strip is already sorted by the y coordinate. Using packing arguments, we get the number of such points, because for each half, all points are separated by at least delta. Partitioning the rectangle of size delta by delta into four squares with side delta/2 makes sure that there will be at most one point per square, because the diagonal of each square has a length less than delta. It shows that only a constant number of successors needs to be considered in both halves. The algorithm considers no more than 15 successors and terminates if the difference between y coordinates becomes larger than the distance bound.

Co-linear points are found using the first x-sorted list. Since the indices of elements within the same duplicate set are in increasing order, the smallest indices will occur at the first consecutive pair. The optimum duplicate pair among all groups yields the right result for the distance of zero, without producing the heavy zero-width strip. Working space is O(n).

## Recurrence analysis

Besides the first O(n log n) sorting algorithm, the remaining recursion satisfies all the requirements:

**T(n) = 2T(n/2) + Θ(n)** with a base case of constant size.

Two subproblems of size n/2 each exist. Separation of the points by y-coordinate and the creation/scanning of the strip takes O(n) time per function call. From the Master Theorem, **a = 2**, **b = 2**, and **f(n) = Θ(n)**. So, **n^(log_b a) = n^(log₂ 2) = n**. Since f(n) = Θ(n^(log_b a)), **Case 2** will be used and the answer is **T(n) = Θ(n log n)**. Subproblems that are of odd sizes and unbalanced are included in this solution. The initial sort itself has the same complexity, making the overall runtime Θ(n log n).

The brute-force solution requires the comparison of all possible pairs of points: n(n−1)/2 pairs. Comparisons have a constant time complexity. The solution runtime is thus **Θ(n²)**.

<div style="page-break-before: always;"></div>

## Validation and measured performance

`python3 -m unittest -v` successfully ran all **8 test Tests** are conducted, from which **500 randomly created** sets of 2 to 50 points with seed 302. Half of the random tests are performed on points having integer coordinates, while the other half is done on points having continuous coordinates. These tests help to check the validity of distances and index pairs of the points. The mentioned tests include two points, duplicates, vertical points, pair of points passing through the split point, ties, invalid input size, and non-finite coordinate points. An additional exhaustive test has been performed as well.

The `benchmark.py` employs seed 302 and uniformly distributed points in [0, 1)². The two algorithms receive the same points at each n. Input generation is not timed using `time.perf_counter()`, however the validation and sorting done within the algorithms are considered in their time. The divide-and-conquer algorithm is run three times at each point. The brute-force algorithm is run three times when n ≤ 4,000, while once at any other point. The numbers presented in the following are medians; while the median calculated based on one trial is not reproduced. The sample values and number of repeats are saved in the `timing_results.csv` file. When a trial with the brute-force algorithm takes more than 60 seconds, all other trials with greater n are skipped.

| n | Brute force (s) | Divide and conquer (s) |
|---:|---:|---:|
| 1,000 | 0.164118 | 0.004930 |
| 2,000 | 0.701349 | 0.010345 |
| 4,000 | 2.529376 | 0.022432 |
| 8,000 | 10.208314 | 0.046608 |
| 16,000 | 41.862539 | 0.103003 |
| 32,000 | 166.107199 | 0.209437 |
| 64,000 | Skipped | 0.455163 |

Environment: Python 3.14.4, Darwin 25.5.0, arm64. Brute-force approach took **166.107 seconds at 32,000** and led to the activation of the stop condition; 64,000 was not calculated. The lowest n, at which the divide-and-conquer approach worked faster than the brute force one, was **1,000** (0.004930 s compared to 0.164118 s). The exact number is unknown under 1,000.

![Measured median runtimes on logarithmic axes](performance_graph.png)

<div style="page-break-before: always;"></div>

## Critical reflection (three questions; under 400 words)

**1. Did growth match the recurrence?** The obtained values are in line with the predicted rates of growth for the specified ranges. Brute force rose from 0.164118 s to 166.107199 s when the number of points was changed from 1,000 to 32,000 – that is an increase by 1,012 times with 32 times more points; the predicted value using quadratic growth is 1,024 times. Divide and conquer rose from 0.004930 s to 0.455163 s when the number of points changed from 1,000 to 64,000 points – an increase by 92.3 times.

**3. Which edge case required most care, and how did testing help?** Here, the use of equidistant pairs together with original index based tie breaking required additional consideration. Actually, distance alone would yield another pair of indices. Equidistant x values must be divided according to x ranking and not just their coordinate values. Such considerations were considered in tuple comparisons, strip bounding, and duplicate prechecks. Duplicate group, grid tie, vertical line, and random integers test cases were tested using brute force.

**4. How was AI assistance verified?** Implementation, testing, benchmarking, and explanation have been done with the help of ChatGPT/Codex. The code has been tested using 8 methods of tests, which include 500 random seed-based test methods and 502 grid subset exhaustive tests. The benchmark confirmed equality of all sizes used by both test methods. This is an evidence for the correctness of code, but it is not a substitute for the review of the strip argument and ties. The student's personal review is pending.

## Reproduce and prepare submission

Run from the project directory:

```sh
python3 -m unittest -v
python3 -m venv .venv
.venv/bin/python -m pip install matplotlib
.venv/bin/python benchmark.py
```

The local virtual environment `.venv` contains the package matplotlib installed. It is necessary only for plotting the graph, as the algorithms work with standard libraries. The benchmarking will overwrite the CSV file and the plot; update this report if you receive other results.

**AI-use acknowledgement:** OpenAI’s ChatGPT/Codex AI was used in helping to implement, test, benchmark, and explain the project.

**Student completion:** Enter your name/ID, check the code and measurements, and make sure that the reflection reflects your understanding. Practise explaining original-index tracking, y-order partitioning, strip packing, and the Master Method. Generate this report as a PDF file and check that the PDF is no longer than four pages, including the reflection. Recommendation for layout: A4 size, 11pt text, 18 mm margins, graph resized to fit the text width, with the supplied page breaks intact. There is no PDF generator available in this environment.

<div style="page-break-before: always;"></div>

## Execution evidence

These images render authentic output as readable transcripts; they are not desktop screenshots. The test output was captured on 9 November 2026. The benchmark summary reads the existing `timing_results.csv` from the 7 November experiment; no benchmark timings were regenerated or estimated.

### Test results

![Captured unittest output: eight test methods passed, including 500 seeded random cases](screenshots/test_results.png)

**Figure 2.** Actual output from a fresh `python3 -m unittest -v` run. The test named `test_500_random_inputs` performs the 500 comparisons.

### Benchmark evidence

![Summary of saved benchmark medians, trial counts, and stop-rule status](screenshots/benchmark_summary.png)

**Figure 3.** Saved CSV measurements, including the 60-second stop rule and smallest tested winning size. B/D means brute-force/divide-and-conquer trial counts. The labelled log-log graph appears in the performance section.

Source text and a reproducible capture script are included in `screenshots/`.

## Conclusion

Both closest-pair algorithms were developed and verified through 500 random seed trials, edge cases tests, and 502 exhaustive grid subset trials. This data provides evidence of the expected Θ(n²) time complexity for brute force algorithm and Θ(n log n) time complexity for divide and conquer algorithm. Brute force takes 166.107 seconds for 32,000 points, whereas divide and conquer takes only 0.209 seconds. Divide and conquer is faster at all sizes tested and took 0.455 seconds to finish 64,000 points. This result proves that divide and conquer is more efficient for camera trap data.