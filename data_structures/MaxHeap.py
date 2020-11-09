" A Max Heap implementation. "

from typing import Any, List


class MaxHeap:
    " A MaxHeap is a tree where the root node is always the max value in the tree"

    def __init__(self, items: List[Any] = []):
        self.heap = items
        # create a new heap from list
        for i in range(len(items) // 2, -1, -1):
            self._max_heapify(i)

    def _max_heapify(self, index):
        "Ensure heap property moving down the tree"
        size = len(self)
        left = index * 2 + 1
        right = left + 1
        _max = index
        # check if either child > parent
        if left < size and self[left] > self[_max]:
            _max = left
        if right < size and self[right] > self[_max]:
            _max = right
        if _max != index:
            # swap with max(child) and move down the tree
            swap(self.heap, index, _max)
            self._max_heapify(_max)

    def insert(self, value):
        "Insert a value in the heap"
        # insert value and bubble up
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        "Ensure heap property moving up the tree"
        if index <= 0:
            return
        # swap when value > parent's
        parent = (index - 1) // 2
        if self[parent] < self[index]:
            swap(self.heap, index, parent)
            self._heapify_up(parent)

    def __len__(self):
        return len(self.heap)

    def remove(self):
        "Remove and return max value from the tree"
        size = len(self)
        if size == 0:
            raise ValueError("remove from empty heap")

        if size == 1:
            return self.heap.pop()

        # replace top with last child
        top = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heap.pop()  # remove last child

        # restore heap property top-down
        self._max_heapify(0)

        return top

    def __contains__(self, key):
        return key in self.heap

    def __getitem__(self, i):
        return self.heap[i]

    def __setitem__(self, i, val):
        return self.update(i, val)

    def update(self, index, key):
        "Increase value of a key in the heap"
        if index >= len(self):
            raise IndexError('index out of range')
        if key < self[index]:
            raise ValueError('value should be greater than current')
        self.heap[index] = key
        self._heapify_up(index)


def swap(A, i, j):
    A[i], A[j] = A[j], A[i]
