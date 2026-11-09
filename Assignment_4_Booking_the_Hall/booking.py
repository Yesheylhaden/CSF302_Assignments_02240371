"""Hall booking algorithms. Inputs: valid start < finish, nonnegative fees.

Output indices are chronological (finish, start, original index). Greedy ties
use original indices. DP excludes the later finish-sorted booking on a tie;
brute force uses the smallest finish-order subset mask on a tie. These rules
are equivalent, but callers should compare optimal revenue and validity.
"""
from bisect import bisect_right


def _ordered(requests):
    return sorted(((s, f, fee, i) for i, (s, f, fee) in enumerate(requests)),
                  key=lambda r: (r[1], r[0], r[3]))


def _compatible(a, b):
    return a[1] <= b[0] or b[1] <= a[0]


def greedy_earliest_finish(requests):
    """O(n log n) sorting and linear selection; input is unchanged."""
    chosen, total, last_finish = [], 0, float('-inf')
    for start, finish, fee, index in _ordered(requests):
        if start >= last_finish:
            chosen.append(index)
            total += fee
            last_finish = finish
    return total, chosen


def greedy_highest_fee(requests):
    """O(n²): compare each candidate with every accepted booking."""
    candidates = sorted(((s, f, fee, i) for i, (s, f, fee) in enumerate(requests)),
                        key=lambda r: (-r[2], r[3]))
    accepted = []
    for candidate in candidates:
        if all(_compatible(candidate, old) for old in accepted):
            accepted.append(candidate)
    accepted.sort(key=lambda r: (r[1], r[0], r[3]))
    return sum(r[2] for r in accepted), [r[3] for r in accepted]


def best_schedule(requests):
    """O(n log n) time, O(n) space; 1-based DP, OPT(0)=0."""
    ordered = _ordered(requests)
    finishes = [r[1] for r in ordered]
    optimum = [0] * (len(ordered) + 1)
    predecessors = [0] * len(ordered)
    take = [False] * len(ordered)
    for k, (start, finish, fee, index) in enumerate(ordered):
        # Search only preceding bookings. Count = predecessor's DP index.
        p = bisect_right(finishes, start, 0, k)
        predecessors[k] = p
        include = fee + optimum[p]
        take[k] = include > optimum[k]
        optimum[k + 1] = max(optimum[k], include)
    chosen, j = [], len(ordered)
    while j:
        if take[j - 1]:
            chosen.append(ordered[j - 1][3])
            j = predecessors[j - 1]
        else:
            j -= 1
    chosen.reverse()
    return optimum[-1], chosen


def brute_force(requests):
    """Independent O(n * 2**n) exhaustive checker, restricted to n <= 15."""
    if len(requests) > 15:
        raise ValueError('Brute force supports at most 15 requests')
    ordered = _ordered(requests)
    best_fee, best_indices = 0, []
    for mask in range(1 << len(ordered)):
        total, indices, last_finish = 0, [], float('-inf')
        valid = True
        for k, (start, finish, fee, index) in enumerate(ordered):
            if mask & (1 << k):
                if start < last_finish:
                    valid = False
                    break
                last_finish = finish
                total += fee
                indices.append(index)
        if valid and total > best_fee:
            best_fee, best_indices = total, indices
    return best_fee, best_indices
