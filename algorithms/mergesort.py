"""
MergeSort(A[], start, end):
    if start >= end: return
    middle = (start + end) // 2
    MergeSort(A, start, middle)
    MergeSort(A, middle + 1, end)
    Merge(A, start, middle, end)
"""


def mergesort(arr):
    "MergeSort"
    tmp = list(arr)
    _msort(tmp, arr, 0, len(arr) - 1)
    return arr


def _msort(A, tmp, start, end):
    # OPT: use insertion sort for small slices
    if start >= end:
        return
    mid = (start + end) // 2
    # OPT: alternate between tmp and A to avoid copying one to the other
    _msort(tmp, A, start, mid)
    _msort(tmp, A, mid + 1, end)
    # OPT: only run merge if lists not sorted, best case O(N)
    if A[mid] > A[mid + 1]:
        _merge(A, tmp, start, mid, end)


def _merge(arr, tmp, i, mid, end):
    lside, rside = i, mid + 1
    swaps = 0
    # merge the two sorted lists into tmp
    while lside <= mid and rside <= end:
        if arr[lside] <= arr[rside]:
            tmp[i] = arr[lside]
            lside += 1
            i += 1
            swaps += rside - (mid + 1)
        else:
            # this element would have to swap places with the remaining from the left side
            tmp[i] = arr[rside]
            rside += 1
            i += 1
    # take the reminder of the lists
    while lside <= mid:
        tmp[i] = arr[lside]
        lside += 1
        i += 1
    while rside <= end:
        tmp[i] = arr[rside]
        rside += 1
        i += 1
    # copy the sorted elements to the original array
    # for i in range(lstart, tmpos):
    #     arr[i] = tmp[i]
    return swaps
