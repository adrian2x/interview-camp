import random
from insertionsort import insertion_sort

SMALL_ARRAY_LENGTH = 47

def qsort(xs):
    return _qsort(xs, 0, len(xs) - 1)

def pivot(xs, start, end):
    """
    Hoare's partition scheme uses two indices: one at the start and end of the array and they move towards each other looking for elements that should be swapped because they are on the wrong side of the pivot.
    This scheme does three fewer swaps on average than Lomuto's.
    With the middle element as the pivot, sorted data results in almost no swaps in equally sized partitions, leading to best-case behavior.
    Here we use a randomized pivot to minimize swaps in case of sorted (or reverse-sorted) input.
    This makes the number of comparisons needed to sort n elements = 1.386 n log n.
    """
    piv = random.choice(xs)
    while True:
        # move right while elements are < pivot
        while xs[start] < piv:
            start += 1
        # move left while elements are > pivot
        while xs[end] > piv:
            end -= 1
        if start >= end:
            return end

        xs[start], xs[end] = xs[end], xs[start]
        start += 1
        end -= 1

def _qsort(xs, start, end):
    if start >= end:
        return
    if end - start + 1 < SMALL_ARRAY_LENGTH:
        insertion_sort(xs, start, end + 1)
    else:
        pidx = pivot(xs, start, end)
        _qsort(xs, start, pidx)
        _qsort(xs, pidx + 1, end)


arr = [3, 7, 8, 5, 2, 1, 9, 5, 4]
qsort(arr)
assert arr == [1, 2, 3, 4, 5, 5, 7, 8, 9]
