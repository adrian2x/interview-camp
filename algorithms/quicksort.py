"""
QuickSort(A[], start, end)
    if start >= end return
    pivotIndex = Partition(A, start, end)
    QuickSort(A, start, pivotIndex)
    QuickSort(A, pivotIndex + 1, end)
"""
from random import randint

SMALL_ARRAY_SIZE = 47


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


def partition(A, start, end):
    """
    Hoare's partition scheme uses two indices: one at the start and end of the array and they move towards each other looking for elements that should be swapped because they are on the wrong side of the pivot.
    This scheme does three fewer swaps on average than Lomuto's.
    With the middle element as the pivot, sorted data results in almost no swaps in equally sized partitions, leading to best-case behavior.
    Here we use a randomized pivot to minimize swaps in case of sorted (or reverse-sorted) input.
    This makes the number of comparisons needed to sort n elements = 1.386 n log n.
    """
    pivot = A[randint(start, end)]

    while True:
        # move right while elements are < pivot
        while A[start] < pivot:
            start += 1
        # move left while elements are > pivot
        while A[end] > pivot:
            end -= 1

        # if whe checked both sides return end
        if start >= end:
            return end

        # swap elements in wrong sides of the pivot
        swap(A, start, end)
        start += 1
        end -= 1


def qsort(A):
    _qsort(A, 0, len(A) - 1)
    return A


def _qsort(A, start, end):
    if start >= end:
        # (opt) sort smaller arrays with insertion sort
        return

    # partition the array around a random pivot
    pivot = A[randint(start, end)]
    left, right = start, end
    while left <= right:
        # move right while elements are < pivot
        while A[left] < pivot:
            left += 1
        # move left while elements are > pivot
        while A[right] > pivot:
            right -= 1
        if left > right:
            break
        # swap elements in wrong sides of the pivot
        swap(A, left, right)
        left += 1
        right -= 1

    # (opt) call the smaller side first
    _qsort(A, start, right)
    _qsort(A, left, end)
