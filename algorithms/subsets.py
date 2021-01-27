from collections import deque


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
