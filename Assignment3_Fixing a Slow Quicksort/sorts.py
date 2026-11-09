"""Two in-place quicksorts; both return None, like list.sort()."""
import random


def quicksort_basic(a):
    """Last-pivot Lomuto: Θ(n log n) balanced/average, Θ(n²) worst case."""
    def sort(lo, hi):
        if lo >= hi:
            return
        pivot = a[hi]
        boundary = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[boundary], a[j] = a[j], a[boundary]
                boundary += 1
        a[boundary], a[hi] = a[hi], a[boundary]
        sort(lo, boundary - 1)
        sort(boundary + 1, hi)

    sort(0, len(a) - 1)


def quicksort_improved(a, cutoff=16):
    """Randomized three-way quicksort with O(log n) recursive stack depth.

    Expected time is O(n log n), worst-case time O(n²) for fixed cutoff.
    Equal keys are removed from further sorting in a single partition pass.
    """
    if not isinstance(cutoff, int) or isinstance(cutoff, bool) or cutoff < 1:
        raise ValueError('cutoff must be a positive integer')

    def insertion(lo, hi):
        for i in range(lo + 1, hi + 1):
            value = a[i]
            j = i - 1
            while j >= lo and a[j] > value:
                a[j + 1] = a[j]
                j -= 1
            a[j + 1] = value

    def sort(lo, hi):
        while lo < hi:
            if hi - lo + 1 <= cutoff:
                insertion(lo, hi)
                return
            pivot = a[random.randrange(lo, hi + 1)]
            lt, i, gt = lo, lo, hi
            # [lo, lt) < pivot; [lt, i) == pivot; (gt, hi] > pivot.
            while i <= gt:
                if a[i] < pivot:
                    a[lt], a[i] = a[i], a[lt]
                    lt += 1
                    i += 1
                elif a[i] > pivot:
                    a[i], a[gt] = a[gt], a[i]
                    gt -= 1  # Inspect the incoming element before advancing i.
                else:
                    i += 1
            # Every recursive child is at most half the parent's size.
            # The larger side uses this stack frame again through the loop.
            if lt - lo < hi - gt:
                sort(lo, lt - 1)
                lo = gt + 1
            else:
                sort(gt + 1, hi)
                hi = lt - 1

    sort(0, len(a) - 1)
