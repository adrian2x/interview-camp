from collections import *


def permutations_recursive(items, cur=0, temp=[]):
    "O(N!) permutations with O(N) memory each = O(N*N!)"
    if cur == len(items):  # check if solution
        yield temp
    else:
        # create a new permutation by adding an item at every position
        for index in range(len(temp) + 1):
            permutation = list(temp)
            permutation.insert(index, items[cur])
            yield from permutations_recursive(items, cur + 1, permutation)
            # note this is tail recursive!


def permutations_iterative(items):
    "O(N!) permutations with O(N) memory each = O(N*N!)"
    queue = deque([[]])
    total_len = len(items)
    for current in items:
        # combine with permutations in queue
        current_len = len(queue)
        for _ in range(current_len):
            temp = queue.popleft()
            # create a new permutation by adding the item at every position
            for index in range(len(temp) + 1):
                permutation = list(temp)
                permutation.insert(index, current)
                if len(permutation) == total_len:
                    yield permutation
                else:
                    queue.append(permutation)


def subsets_recursive(items, subset=[], i=0):
    "O(2^N) subsets and stack frames"
    if i == len(items):  # base case
        yield subset
    else:
        # skip the i-th element
        yield from subsets_recursive(items, subset, i + 1)
        # add the i-th element to the subset
        newset = subset + [items[i]]
        yield from subsets_recursive(items, newset, i + 1)


def subsets_iterative(items):
    "O(2^N) subsets with O(N) memory each = O(N*2^N)"
    subsets = [[]]  # empty set (base case)
    for current in items:
        # go through the previous subsets
        current_len = len(subsets)
        for i in range(current_len):
            # create a new subset by adding a new element
            subset = subsets[i] + [current]
            subsets.append(subset)
    return subsets


# http://tiny.cc/fixed-queries
def fixed_len_queries(arr, queries):
    output = []
    for size in queries:
        result = 1e6  # global min
        window = deque([], size)
        for (i, n) in enumerate(arr):
            # discard previous max in the window
            while window and window[-1][0] < n:
                window.pop()

            # index for checking if item is out of the window
            window.append((n, i))

            # update elements leaving the window
            while window and window[0][1] <= i - size:
                window.popleft()

            # update global min if window is full
            if i >= size - 1:
                result = min(result, window[0][0])

        output.append(result)
    return output


print(fixed_len_queries([2, 3, 4, 5, 6], [2, 3]))
