def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


class MinHeap:
    def __init__(self) -> None:
        self.heap = []

    def add(self, val):
        self.heap.append(val)
        self._move_up(len(self.heap) - 1)

    def __len__(self):
        return len(self.heap)

    def _move_up(self, cur):
        if cur <= 0:
            return
        parent = cur // 2
        if self.heap[cur] < self.heap[parent]:
            swap(self.heap, cur, parent)
            return self._move_up(parent)

    def remove(self):
        top = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self._heapify(0)
        return top

    def _heapify(self, cur):
        size = len(self.heap)
        left = cur * 2 + 1
        right = cur * 2 + 2
        _min = cur
        if left < size and self.heap[left] < self.heap[_min]:
            _min = left
        if right < size and self.heap[right] < self.heap[_min]:
            _min = right
        if _min != cur:
            swap(self.heap, cur, _min)
            return self._heapify(_min)


class ListItem:
    def __init__(self, key, lst) -> None:
        self.key = key
        self.container = lst

    def __lt__(self, other):
        return self.key < other.key


def merge_k(blocks):
    # Merge k sorted blocks
    k_heap = MinHeap()

    # note we need to keep track of where we are on each list, so iterators play well
    iters = [iter(block) for block in blocks]
    values = []
    for lst in iters:
        nxt = next(lst)
        k_heap.add(ListItem(nxt, lst))

    while len(k_heap) > 0:
        # Get the min element from the heap and store it in the array
        _min = k_heap.remove()
        values.append(_min.key)
        lst = _min.container
        try:
            nxt = next(lst)
            k_heap.add(ListItem(nxt, lst))
        except StopIteration:
            pass
    return values


sorted_lists = [[1, 2], [3, 4], [0, 1]]
assert merge_k(sorted_lists) == [0, 1, 1, 2, 3, 4]


from heapq import heappop, heappush


def kth_smallest(nums, k):
    """Find k-th smallest elements in a list"""
    maxheap = []
    for n in nums:
        # put the first k elements in max heap
        if len(maxheap) < k:
            heappush(maxheap, -n)
        # check if the value is less than heap root (max)
        # and push into heap
        elif n < -maxheap[0]:
            heappop(maxheap)
            heappush(maxheap, n)
    return -maxheap[0]


def sort_character_by_frequency(str1):
    "Return the string sorted with the most repeated characters first, in lexicographical order"
    freq = {}
    for char in str1:
        if char not in freq:
            freq[char] = 0
        freq[char] += 1

    maxheap = []
    for char, count in freq.items():
        heappush(maxheap, (-count, char))

    result = []
    while len(maxheap):
        entry = heappop(maxheap)
        result.append(entry)

    ret = ""
    for count, letter in result:
        repeat = [letter] * (-count)
        ret += "".join(repeat)

    return ret


print(
    "String after sorting characters by frequency: "
    + sort_character_by_frequency("Programming")
)
print(
    "String after sorting characters by frequency: "
    + sort_character_by_frequency("abcbab")
)
