from quicksort import swap
from random import randint
from os import cpu_count
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import threading
import math
import random
from collections import deque



from quicksort import qsort, _qsort


array = [3, 7, 8, 5, 2, 1, 9, 5, 4]
qsort(array)
assert sorted(array) == array

for i in range(0, 100):
    array = [randint(0, 1000) for i in range(100)]
    qsort(array)
    assert sorted(array) == array


def paralell_qsort(A):
    size = len(A)
    cpus = cpu_count()
    threshold = max(100, (1 + size) / (cpus * 4))
    with ThreadPoolExecutor(cpus * 2) as pool:
        queue = deque()
        pqsort(A, 0, size - 1, pool, queue, threshold=threshold)
        while len(queue) > 0:
            fut = queue.pop()
            fut.result()



def pqsort(A, low, high, pool, queue, threshold=47):
    if high - low < threshold:
        # Sort directly
        return _qsort(A, low, high)

    i, j = low, high
    pivot = A[random.randint(i, j)]

    # Pivot the array
    while i <= j:
        while A[i] < pivot:
            i += 1

        while A[j] > pivot:
            j -= 1

        if i <= j:
            swap(A, i, j)
            i += 1
            j -= 1

    if low < j:
        # submit the subproblems to a thread pool
        fut = pool.submit(pqsort, A, low, j, pool, queue, threshold=threshold)
        queue.append(fut)
    if i < high:
        # submit the subproblems to a thread pool
        fut = pool.submit(pqsort, A, i, high, pool, queue, threshold=threshold)
        queue.append(fut)


for i in range(0, 100):
    lst = [randint(0, 1000) for i in range(1000)]
    qsort(lst)
    # paralell_qsort(lst)
    assert sorted(lst) == lst
