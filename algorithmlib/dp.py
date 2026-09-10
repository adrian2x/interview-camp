"""
algorithmlib.dp - the classical dynamic programming algorithms as pure,
single-shot functions.

Each function here takes the problem's data and returns the answer; none of
them is a data structure you build and then query. What they share is the DP
method: define the answer to the whole problem in terms of answers to smaller
subproblems, compute those in a sensible order, and read off the result.

    fibonacci                     the warm-up: overlapping subproblems
    max_subarray_sum              Kadane's algorithm
    knapsack_01                   0/1 knapsack, bottom-up
    subset_sum                    reachability DP over sums
    coin_change_min               fewest coins, unbounded
    longest_common_subsequence    LCS of two sequences
    longest_common_substring      contiguous cousin of the LCS
    edit_distance                 Levenshtein distance
    longest_increasing_subsequence  O(n log n) patience sorting

The lesson to internalize is the recurrence each one encodes:

* Kadane:      best ending here = max(x, best ending before + x)
* knapsack:    dp[c] = max(dp[c], dp[c - w] + v)      (iterate c downward)
* coin change: dp[a] = min(dp[a], dp[a - coin] + 1)   (iterate a upward)
* LCS:         match ? diagonal + 1 : max(up, left)
* Levenshtein: min(insert, delete, substitute) + 1

The direction of the inner loop is not a detail: *downward* for 0/1 problems
(each item used at most once, so a row must not see its own update), *upward*
for unbounded problems (reusing an item is exactly what we want).

Sequences are generic: the sequence functions accept any comparable
elements. The LCS and longest-common-substring results are always lists;
join at the call site if you want a string (e.g. "".join(result)).
"""

from bisect import bisect_left
from collections.abc import Sequence
from typing import List, TypeVar

T = TypeVar("T")  # element type of the input sequences


def fibonacci(n: int) -> int:
    """
    Return the n-th Fibonacci number, F(n), with F(0) = 0 and F(1) = 1.

    Fibonacci is the canonical DP warm-up because the naive recursion
    fib(n) = fib(n-1) + fib(n-2) recomputes the same values exponentially
    often (try drawing the call tree for fib(5): fib(2) appears three
    times). The fix - the essence of DP - is to notice there are only n + 1
    distinct subproblems and to solve each once, in order.

    The loop keeps only the two most recent values (O(1) space). If you ever
    need F(n) for astronomically large n, the fast-doubling identities
    F(2k) = F(k) * (2*F(k+1) - F(k)) and F(2k+1) = F(k+1)^2 + F(k)^2 compute
    it in O(log n) by repeated squaring.

    Time: O(n).  Space: O(1).

    Example:
        >>> fibonacci(10)
        55
        >>> fibonacci(0)
        0
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1  # F(i) and F(i+1) for the current i
    for _ in range(n):
        a, b = b, a + b
    return a


def max_subarray_sum(nums: Sequence[float]) -> float:
    """
    Return the maximum sum of any contiguous subarray (Kadane's algorithm).

    The insight is a one-line recurrence. Let best_here be the maximum sum
    of a subarray *ending at the current position*. A subarray ending here is
    either just the current element, or the current element appended to the
    best subarray ending at the previous position:

        best_here = max(nums[i], best_here + nums[i])

    The global answer is the largest best_here seen. Because each step needs
    only the previous best_here, the whole scan is O(n) with O(1) space -
    versus O(n^2) for checking every possible subarray.

    Non-empty subarrays only: with an all-negative input the answer is the
    largest single element (each best_here is just nums[i] alone).

    Time: O(n).  Space: O(1).

    Example:
        >>> max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4])   # [4,-1,2,1]
        6
        >>> max_subarray_sum([-3, -1, -2])
        -1
    """
    if not nums:
        raise ValueError("nums must not be empty")
    best_overall = best_ending_here = nums[0]
    for x in nums[1:]:
        # Either start a fresh subarray at x, or extend the best one ending
        # at the previous element. A negative best_ending_here is never worth
        # extending - that is exactly the "fresh start" branch.
        best_ending_here = max(x, best_ending_here + x)
        best_overall = max(best_overall, best_ending_here)
    return best_overall


def knapsack_01(
    weights: Sequence[int], values: Sequence[int], capacity: int
) -> int:
    """
    Return the maximum total value achievable by selecting a subset of items
    (each at most once) whose total weight fits in `capacity` - the 0/1
    knapsack problem, solved bottom-up.

    Recurrence over the capacity axis: dp[c] is the best value achievable
    with capacity c. For each item (w, v),

        dp[c] = max(dp[c], dp[c - w] + v)   for c >= w

    The inner loop runs *downward* over c: dp[c - w] must reflect the items
    seen so far, not the current item - iterating down guarantees a row never
    reuses the item it is currently adding. (Flip the direction and you get
    the unbounded knapsack, where reusing is allowed.)

    Time: O(n * capacity).  Space: O(capacity).

    Raises ValueError if weights and values differ in length, a weight is
    negative, or capacity is negative.

    Example:
        >>> knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], capacity=7)
        9
    """
    if len(weights) != len(values):
        raise ValueError("weights and values must have the same length")
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    if any(w < 0 for w in weights):
        raise ValueError("weights must be non-negative (a negative weight "
                         "would break the descending recurrence)")

    dp = [0] * (capacity + 1)  # dp[c] = best value with capacity c
    for w, v in zip(weights, values):
        # Descending order: each item is considered at most once (see above).
        for c in range(capacity, w - 1, -1):
            take = dp[c - w] + v
            if take > dp[c]:
                dp[c] = take
    return dp[capacity]


def subset_sum(nums: Sequence[int], target: int) -> bool:
    """
    Return True if some subset of nums sums exactly to target (each number
    usable at most once).

    reachable[s] is True once some subset of the numbers seen so far sums to
    s. Each number num extends the reachable set: every already-reachable sum
    s gives a new reachable sum s + num. The inner loop runs downward so a
    number cannot be used twice (same reasoning as knapsack_01).

    This is the decision version of knapsack and shows up in partition
    problems: "can the array be split into two equal-sum halves?" is just
    subset_sum(nums, sum(nums) / 2).

    Time: O(n * target).  Space: O(target).

    Raises ValueError if any number is negative (the decreasing-sums
    recurrence only covers non-negative inputs).

    Example:
        >>> subset_sum([3, 34, 4, 12, 5, 2], 9)
        True
        >>> subset_sum([3, 34, 4, 12, 5, 2], 30)
        False
    """
    if target < 0:
        return False
    if any(num < 0 for num in nums):
        raise ValueError("nums must be non-negative")
    reachable = [False] * (target + 1)
    reachable[0] = True  # the empty subset always sums to 0
    for num in nums:
        for s in range(target, num - 1, -1):
            if reachable[s - num]:
                reachable[s] = True
    return reachable[target]


def coin_change_min(coins: Sequence[int], amount: int) -> int:
    """
    Return the fewest number of coins needed to make `amount`, where each
    coin denomination in `coins` is available in unlimited quantity. Returns
    -1 if the amount cannot be made at all.

    dp[a] = minimum coins for amount a. A coin used last leaves the smaller
    subproblem amount a - coin, so

        dp[a] = 1 + min(dp[a - coin]) over coins <= a

    The inner loop runs *upward* over a: unbounded supply means reusing the
    same coin across subproblems is exactly what we want (contrast with the
    descending loop in knapsack_01 / subset_sum).

    Time: O(amount * len(coins)).  Space: O(amount).

    Raises ValueError if amount is negative or some coin is not positive
    (a non-positive coin would make the subproblem index negative).

    Example:
        >>> coin_change_min([1, 2, 5], 11)   # 5 + 5 + 1
        3
        >>> coin_change_min([2], 3)          # impossible
        -1
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if any(coin <= 0 for coin in coins):
        raise ValueError("coins must be positive")

    infinity = float("inf")
    dp = [infinity] * (amount + 1)
    dp[0] = 0  # zero coins make zero amount
    for coin in coins:
        for a in range(coin, amount + 1):
            if dp[a - coin] + 1 < dp[a]:
                dp[a] = dp[a - coin] + 1
    return -1 if dp[amount] == infinity else dp[amount]


def longest_common_subsequence(
    a: Sequence[T], b: Sequence[T]
) -> List[T]:
    """
    Return one longest common subsequence of a and b - the longest sequence
    of elements obtainable from both inputs by deleting elements (order
    preserved, contiguity not required). Returns the empty list when nothing
    is shared; the result is always a list, so join it for string inputs:
    "".join(longest_common_subsequence(a, b)).

    Classic DP: dp[i][j] = LCS length of a[:i] and b[:j]. The recurrence
    reads off the last elements:

        if a[i-1] == b[j-1]:  dp[i][j] = dp[i-1][j-1] + 1   (match extends)
        else:                 dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    The table is filled row by row; afterwards a backward walk from the
    bottom-right corner reconstructs one actual LCS by retracing the choices
    (diagonal moves are matched elements; up/left moves are deletions).

    Time: O(m * n).  Space: O(m * n). (If only the *length* is needed, two
    rolling rows suffice - see edit_distance below. Reconstructing the
    sequence itself requires keeping the full table: reading the answer back
    costs O(m * n) space.)

    Example:
        >>> "".join(longest_common_subsequence("ABCBDAB", "BDCABA"))
        'BCBA'
    """
    m, n = len(a), len(b)

    # dp[i][j] is the LCS length of a[:i] and b[:j]. Row 0 and column 0 are
    # implicitly 0 (an empty prefix shares nothing).
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct by walking the table backwards from (m, n).
    result: List[T] = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])  # a matched element: part of the LCS
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1  # the optimum came from above: skip a[i-1]
        else:
            j -= 1  # the optimum came from the left: skip b[j-1]
    result.reverse()

    return result


def longest_common_substring(
    a: Sequence[T], b: Sequence[T]
) -> List[T]:
    """
    Return one longest substring (contiguous run of elements) common to a
    and b, as a list; the empty list means no common element at all. Join the
    result for string inputs: "".join(longest_common_substring(a, b)).

    The DP table tracks, for each pair of positions (i, j), the length of
    the common run *ending* at a[i-1] and b[j-1]:

        if a[i-1] == b[j-1]:  dp[i][j] = dp[i-1][j-1] + 1
        else:                 dp[i][j] = 0

    Unlike the LCS, a mismatch resets the run to zero - that is the whole
    difference between "subsequence" (gaps allowed) and "substring"
    (contiguous). Two rolling rows suffice for the DP; the answer is
    recovered from the tracked end position and length, no full table needed.
    The rows are made as short as the *shorter* input (see the swap below),
    which is the standard constant-factor win on this family of DPs.

    Time: O(m * n).  Space: O(min(m, n)) via rolling rows.

    Example:
        >>> "".join(longest_common_substring("abcde", "zbcdf"))
        'bcd'
    """
    if len(b) > len(a):
        # The DP is symmetric, so orient it with the shorter sequence in
        # `b`: the rolling rows then run over the shorter input.
        a, b = b, a
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return []

    best_len = 0
    best_end = 0  # 1-based exclusive end of the best run inside a

    prev = [0] * (n + 1)  # previous row of the DP table
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        ai = a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1  # extend the run ending here
                if cur[j] > best_len:  # strictly greater: keep the *first*
                    best_len = cur[j]  # longest run if several tie
                    best_end = i
        prev = cur

    return list(a[best_end - best_len : best_end])


def edit_distance(a: Sequence[T], b: Sequence[T]) -> int:
    """
    Return the Levenshtein edit distance between a and b: the minimum number
    of single-element insertions, deletions and substitutions needed to turn
    a into b.

    dp[i][j] = distance between a[:i] and b[:j]. The recurrence compares the
    last elements:

        if a[i-1] == b[j-1]:  dp[i][j] = dp[i-1][j-1]          (free match)
        else:                 dp[i][j] = 1 + min(
                                     dp[i-1][j],      # delete from a
                                     dp[i][j-1],      # insert into a
                                     dp[i-1][j-1])    # substitute

    Only the previous row is needed to build the next one, so memory is O(n)
    with two rolling rows. We first swap the inputs so that the rows run over
    the *shorter* sequence - edit distance is symmetric, so this only shrinks
    the constant factor, never the answer. This is the algorithm behind
    spell-check suggestions, diff tools, and DNA sequence alignment (where
    the cost matrix is usually generalized).

    Time: O(m * n).  Space: O(min(m, n)) with rows over the shorter input.

    Example:
        >>> edit_distance("kitten", "sitting")   # k->s, e->i, +g
        3
        >>> edit_distance("", "abc")
        3
    """
    if len(b) > len(a):
        # Symmetric: distance(a, b) == distance(b, a). Put the shorter
        # sequence in `b` so the rolling rows are as narrow as possible.
        a, b = b, a
    m, n = len(a), len(b)

    # Row 0: turning "" into b[:j] costs j insertions.
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n  # turning a[:i] into "" costs i deletions
        ai = a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1]  # last elements already match: no cost
            else:
                cur[j] = 1 + min(
                    prev[j],       # delete a[i-1], then match a[:i-1] to b
                    cur[j - 1],    # insert b[j-1], then match a to b[:j-1]
                    prev[j - 1],   # substitute a[i-1] with b[j-1]
                )
        prev = cur
    return prev[n]


def longest_increasing_subsequence(nums: Sequence[float]) -> int:
    """
    Return the length of the longest strictly increasing subsequence of nums
    (the O(n log n) "patience sorting" version).

    The classic DP - lis[i] = 1 + max(lis[j]) over j < i with nums[j] <
    nums[i] - is O(n^2). The trick that makes it O(n log n) is to keep an
    array `tails` where tails[k] is the smallest possible *last value* of an
    increasing subsequence of length k + 1.

    For each new element x, binary search finds the first tails[k] >= x; x
    can extend a subsequence of length k (whose best ending was tails[k-1])
    and improves that entry, since x <= tails[k]. If x is larger than every
    tail, the longest subsequence grows by one. tails stays sorted, which is
    what makes the binary search legal.

    This is called patience sorting because it mirrors the patience card
    game: piles built by placing each card on the leftmost pile whose top
    beats it. (To also *reconstruct* the subsequence, record a back-pointer
    whenever a tail is updated.)

    Time: O(n log n).  Space: O(n).

    Example:
        >>> longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18])
        4
        >>> longest_increasing_subsequence([7, 7, 7])    # strict: no repeats
        1
    """
    tails: List[float] = []
    for x in nums:
        # First tail entry >= x (strict increase: equal values do not extend,
        # they replace - bisect_left finds the first *>=* position).
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)  # x extends the longest subsequence seen so far
        else:
            tails[k] = x  # x is a better (smaller) ending for length k + 1
    return len(tails)
