"""
QuickSort(A[], start, end)
    if start >= end return
    pivotIndex = Partition(A, start, end)
    QuickSort(A, start, pivotIndex)
    QuickSort(A, pivotIndex + 1, end)
"""
from random import randint
from multiprocessing.pool import ThreadPool
from os import cpu_count
import math

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
        return

    # OPT: sort smaller arrays with insertion sort

    # partition the array around a random pivot
    pivot = A[randint(start, end)]
    i, j = start, end
    while i <= j:
        # move right while elements are < pivot
        while A[i] < pivot:
            i += 1
        # move left while elements are > pivot
        while A[j] > pivot:
            j -= 1

        if i <= j:
            # swap elements in wrong sides of the pivot
            swap(A, i, j)
            i += 1
            j -= 1

    # fat partition: include elements == pivot
    while i < end and A[i] == pivot:
        i += 1
    while j > start and A[j] == pivot:
        j -= 1

    # OPT: call the smaller side first
    if start < j:
        # sort elements < pivot
        _qsort(A, start, j)
    if i < end:
        # sort elements > pivot
        _qsort(A, i, end)
