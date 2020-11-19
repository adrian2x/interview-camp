"""
QuickSort(A[], start, end)
    if start >= end return
    Get the pivot element index
    pivotIndex = Partition(A, start, end)
    QuickSort(A, start, pivotIndex)
    QuickSort(A, pivotIndex + 1, end)
"""
import random
from random import randint

SMALL_ARRAY_SIZE = 47


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

def partition(A, start, end):
    pivot = A[random.randint(start, end)]

    while True:
        # partition the remaining elements
        while A[start] < pivot:
            start += 1

        while A[end] > pivot:
            end -= 1

        if start >= end:
            return end

        swap(A, start, end)
        start += 1
        end -= 1


def qsort(A):
    _qsort(A, 0, len(A) - 1)
    return A


def _qsort(A, start, end):
    if start >= end:
        return

    # optimize smaller arrays with insertion sort
    if end - start + 1 < SMALL_ARRAY_SIZE:
        i = start + 1
        while i <= end:
            x = A[i]
            j = i - 1
            while A[j] > x and j >= start:
                A[j + 1] = A[j]
                j -= 1
            A[j + 1] = x
            i += 1
        return

    pividx = partition(A, start, end)

    # optimize the recursive call with the smaller side first
    if start - pividx < end - pividx - 1:
        _qsort(A, start, pividx)
        _qsort(A, pividx + 1, end)
    else:
        _qsort(A, pividx + 1, end)
        _qsort(A, start, pividx)


def is_sorted(arr):
    for i in range(1, len(arr)):
        assert arr[i] >= arr[i - 1]


array = [3, 7, 8, 5, 2, 1, 9, 5, 4]
qsort(array)
is_sorted(array)

for i in range(0, 100):
    array = [randint(0, 1000) for i in range(100)]
    qsort(array)
    is_sorted(array)
