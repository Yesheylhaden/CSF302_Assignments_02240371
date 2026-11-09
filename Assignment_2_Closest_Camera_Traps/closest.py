"""Closest pairs, breaking ties by the smallest original index pair.

Inputs contain at least two finite, real coordinate pairs. Results are (d, i, j).
"""

from math import hypot, isfinite


def _prepare(points):
    points = list(points)
    if len(points) < 2:
        raise ValueError("At least two points are required")
    for point in points:
        if len(point) != 2 or not all(isfinite(value) for value in point):
            raise ValueError("Each point must have two finite coordinates")
    return [(x, y, i) for i, (x, y) in enumerate(points)]


def _brute(points):
    best = (float("inf"), float("inf"), float("inf"))
    for a in range(len(points) - 1):
        x1, y1, i = points[a]
        for b in range(a + 1, len(points)):
            x2, y2, j = points[b]
            candidate = (hypot(x1 - x2, y1 - y2), min(i, j), max(i, j))
            if candidate < best:
                best = candidate
    return best


def closest_pair_brute(points):
    """Compare all n(n-1)/2 pairs: Theta(n squared) time."""
    return _brute(_prepare(points))


def closest_pair(points):
    """Return the closest pair in O(n log n) time and O(n) extra space.

    Equal distances are resolved by lexicographic order of (i, j).
    """
    by_x = sorted(_prepare(points), key=lambda p: (p[0], p[1], p[2]))

    # Consider a zero distance first: a dense replica strip violates packing limits.
    duplicate = None
    for a, b in zip(by_x, by_x[1:]):
        if a[:2] == b[:2]:
            candidate = (0.0, min(a[2], b[2]), max(a[2], b[2]))
            if duplicate is None or candidate < duplicate:
                duplicate = candidate
    if duplicate is not None:
        return duplicate

    rank = {point[2]: position for position, point in enumerate(by_x)}
    by_y = sorted(by_x, key=lambda p: (p[1], p[0], p[2]))

    def solve(lo, hi, ordered_y):
        if hi - lo <= 3:
            return _brute(by_x[lo:hi])
        mid = (lo + hi) // 2
        dividing_x = by_x[mid][0]
        left_y, right_y = [], []
        for point in ordered_y:
            if rank[point[2]] < mid:
                left_y.append(point)
            else:
                right_y.append(point)
        best = min(solve(lo, mid, left_y), solve(mid, hi, right_y))
        delta = best[0]
        strip = [p for p in ordered_y if abs(p[0] - dividing_x) <= delta]
        for a, (x1, y1, i) in enumerate(strip):
            # Packings provide a fixed number of neighbors. Instead of 15, use
            # more than the standard 7 to safely incorporate distance ties.
            for b in range(a + 1, min(a + 16, len(strip))):
                x2, y2, j = strip[b]
                if y2 - y1 > best[0]:
                    break
                candidate = (hypot(x1 - x2, y1 - y2), min(i, j), max(i, j))
                if candidate < best:
                    best = candidate
        return best

    return solve(0, len(by_x), by_y)
