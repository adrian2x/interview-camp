"""
How many ways are there to decode an encoded string using this alphabet:
a: 1
b: 2
c: 3
...
z: 26
input: a string such as "33"
output: 2
"""


def decode_ways(data, remain, memo):
    if remain == 0:
        return 1

    N = len(data)
    start = N - remain
    if data[start] == "0":
        return 0

    if memo[remain] != None:
        return memo[remain]

    # try next letter
    ways = decode_ways(data, remain - 1, memo)
    # try next two letters if valid
    if int(data[start : start + 1]) <= 26 and remain >= 2:
        ways += decode_ways(data, remain - 2, memo)

    memo[remain] = ways
    return ways


test = "33"
print(decode_ways(test, len(test), [None] * (len(test) + 1)))


def permutations(search, part=[], curr=0, cast=None):
    # check for a solution
    if curr == len(search):
        return part if cast is None else cast(part)
    # or insert a new element at each position in curent perm
    for i in range(len(part) + 1):
        newperm = list(part)
        newperm.insert(i, search[curr])
        permutations(search, newperm, curr + 1, cast)


s = "abc"
permutations(list(s), [], 0, cast=print)


def n_matched_parens(n):
    "Generate all possible n-matched parenthesis"

    def helper(cur, opened=0, closed=0):
        if len(cur) == n * 2:
            # check if we have a valid solution
            if opened == n and closed == n:
                print(cur)
        else:
            # get remaining parens to match
            not_closed = opened - closed
            if opened < n:  # try opening a new one
                helper(cur + "(", opened + 1, closed)
            if closed < n and not_closed > 0:
                # try closing a previous one
                helper(cur + ")", opened, closed + 1)

    helper("")


n_matched_parens(3)


def max_subarray_sum(arr):
    max_sum = 0
    agg = [0] * len(arr)
    for r in range(0, len(arr)):
        agg[r] = max(arr[r], arr[r] + agg[r - 1])
        if agg[r] > max_sum:
            max_sum = agg[r]
    return max_sum


max_subarray_sum([13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7])


def second_largest_value(arr):
    _max = float("-inf")
    _max2 = float("-inf")
    for i in arr:
        if i > _max:
            _max2 = _max
            _max = i
        elif i != _max and i > _max2:
            _max2 = i
    return _max2


second_largest_value([-1, 10, 8, 9, 10, 9, -8, 11])


phone_letters = {
    "2": "ABC",
    "3": "DEF",
    "4": "GHI",
    "5": "JKL",
    "6": "MNO",
    "7": "PQRS",
    "8": "TUV",
    "9": "WXYZ",
}


def phone_mneumonics(inp, cur=0, seq="", marked={}):
    if cur == len(inp):
        print(seq)
    else:
        digit = inp[cur]
        for c in phone_letters[digit]:
            if not marked.get(c):
                marked[c] = True
                phone_mneumonics(inp, cur + 1, seq + c, marked)
                marked[c] = False


phone_mneumonics("23")
phone_mneumonics("89")


def knapsack(weights, profits, capacity):
    nitems = len(profits)

    def helper(curItem, curCapacity):
        # stop when no more capacity or items
        if curCapacity < 0 or curItem >= nitems:
            return 0

        takecur = 0
        # check if we can take this current item and add it to solution
        if weights[curItem] <= curCapacity:
            takecur = profits[curItem] + helper(
                curItem + 1, curCapacity - weights[curItem]
            )

        # check solution for skipping this item
        skipcur = helper(curItem + 1, curCapacity)
        # return max solution
        return max(takecur, skipcur)

    return helper(0, capacity)


def bottomup_knapsack(weights, profits, capacity):
    # since the solution depends on smaller subproblems,
    # we can use a bottom-up approach solving the smaller problems first
    nitems = len(profits)
    # This table represents the solution to the first i items with capacity j
    # which will be stored in the table in [i][j]
    solved = [[0] * (capacity + 1) for i in range(nitems)]

    # consider the first item and the best we can do at each capacity
    for c in range(capacity + 1):
        if weights[0] <= c:
            solved[0][c] = profits[0]

    for i in range(1, nitems):
        # consider remaining items
        for c in range(1, capacity + 1):
            # check each capacity
            takeProfit, skipProfit = 0, 0
            if weights[i] <= c:
                # if the item can fit in this capacity
                # consider the result of taking it with the result of remainig capacity
                takeProfit = profits[i] + solved[i - 1][c - weights[i]]
            # consider the result of skipping the item and keeping the capacity
            skipProfit = solved[i - 1][c]
            solved[i][c] = max(takeProfit, skipProfit)
    return solved[nitems - 1][capacity]


assert knapsack([1, 2, 3, 5], [1, 6, 10, 16], 5) == 16
assert knapsack([1, 2, 3, 5], [1, 6, 10, 16], 6) == 17
assert knapsack([1, 2, 3, 5], [1, 6, 10, 16], 7) == 22

assert bottomup_knapsack([1, 2, 3, 5], [1, 6, 10, 16], 5) == 16
assert bottomup_knapsack([1, 2, 3, 5], [1, 6, 10, 16], 6) == 17
assert bottomup_knapsack([1, 2, 3, 5], [1, 6, 10, 16], 7) == 22


def equal_sum_partition(nums):
    "Given a set of positive numbers, find if we can partition it into two subsets such that the sum of elements in both subsets is equal"
    total = sum(nums)
    target = total / 2

    def helper(i, curSum):
        if curSum == target:
            return True

        if i >= len(nums):
            return False

        if nums[i] + curSum <= target and helper(i + 1, curSum + nums[i]):
            return True

        return helper(i + 1, curSum)

    return helper(0, 0)


assert equal_sum_partition([1, 2, 3, 4]) == True
assert equal_sum_partition([1, 1, 3, 4, 7]) == True
assert equal_sum_partition([2, 3, 4, 6]) == False


def contains_sum(nums, S):
    "Given a set of positive numbers, determine if a subset exists whose sum is equal to a given number S"
    n = len(nums)
    # table is subset up to ith by sum up to s
    sol = [[False] * (S + 1) for i in range(n)]

    # we can always find a solution for sum 0: the empty set {}
    for i in range(n):
        sol[i][0] = True

    # we can also find a solution if any single item has the desired sum
    for s in range(1, S + 1):
        sol[0][s] = nums[0] == s

    # now check every item and every possible sum
    for i in range(1, len(nums)):
        N = nums[i]
        for s in range(1, S + 1):
            # check if we should sip the item from the sum
            # or include it if it's less than desired sum
            if sol[i - 1][s]:
                sol[i][s] = True
            elif N <= s:
                sol[i][s] = sol[i - 1][s - N]
    return sol[n - 1][S]


def minimum_subset_sum(nums):
    "Given a set of positive numbers, partition the set into two subsets with minimum difference between their subset sums"
    total = sum(nums) + 1
    # initialize the memoized table
    sol = [[-1] * total for i in range(len(nums))]

    def helper(sum1, sum2, cur):
        # base case: all numbers either in sum1 or sum2
        if cur >= len(nums):
            return abs(sum1 - sum2)

        if sol[cur][sum1] == -1:
            # check the solution from adding to the left subset or right subset
            # and take the minimal difference
            res1 = helper(sum1 + nums[cur], sum2, cur + 1)
            res2 = helper(sum1, sum2 + nums[cur], cur + 1)
            sol[cur][sum1] = min(res1, res2)

        return sol[cur][sum1]

    return helper(0, 0, 0)
