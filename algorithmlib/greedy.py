"""
algorithmlib.greedy - the classical greedy algorithms as single-shot
functions.

A greedy algorithm builds an answer piece by piece, each time taking the
option that looks best *right now*, and never revisits the choice. Greedy
only works when the problem has the right structure (an optimal solution can
be built from optimal solutions to smaller versions - the "greedy-choice
property" plus optimal substructure), which is why these three classics are
the canonical examples: for each of them the greedy rule is provably optimal.

    activity_selection    most non-overlapping intervals: pick earliest end
    fractional_knapsack   take items by value-per-weight, cut the last one
    huffman_codes         minimum-cost prefix codes via the two smallest

The through-line: every greedy proof is an *exchange argument* - take an
optimal solution that disagrees with the greedy choice and show you can swap
in the greedy choice without making it worse. That is the mental template to
reach for whenever someone asks "why is this greedy optimal?":

* activity selection: the greedy pick ends no later than whatever the
  optimal solution picks first, so swapping cannot shrink the rest.
* fractional knapsack: if the optimum is not carrying the densest item,
  replace some of what it carries with that item and the value goes up.
* Huffman: the two least-frequent symbols sit deepest in some optimal tree;
  merging them first is therefore always safe.
"""

import heapq
from collections.abc import Mapping, Sequence
from typing import Dict, Hashable, List, Tuple, TypeVar

T = TypeVar("T", bound=Hashable)  # symbol type for Huffman codes
Number = TypeVar("Number", int, float)  # weights / frequencies / values


class _Leaf:
    """A Huffman tree consisting of a single symbol."""

    __slots__ = ("symbol",)

    def __init__(self, symbol: T):
        self.symbol = symbol


class _Node:
    """An internal Huffman tree node: two subtrees fused by a merge."""

    __slots__ = ("left", "right")

    def __init__(self, left: object, right: object):
        self.left = left
        self.right = right


def activity_selection(
    intervals: Sequence[Tuple[Number, Number]],
) -> int:
    """
    Return the maximum number of non-overlapping intervals selectable from
    intervals (each interval is a (start, end) pair; an interval may start
    exactly when a selected one ends).

    Greedy rule: sort by end time, then take each interval that starts after
    the previously selected one ends.

    Why earliest-finish is optimal (exchange argument): consider the optimal
    selection and its first interval. The greedy choice ends no later than
    that interval, so replacing it with the greedy choice leaves the rest of
    the optimal selection intact and still valid - the greedy choice can
    never block more intervals than it replaces. Repeating the argument for
    the second, third, ... slots shows the greedy selection is at least as
    large as any other.

    This is interval scheduling, the problem behind meeting-room booking and
    CPU/job scheduling.

    Time: O(n log n) - dominated by the sort.  Space: O(1).

    Example:
        >>> activity_selection([(1, 4), (3, 5), (0, 6), (5, 7), (3, 9),
        ...                     (5, 9), (6, 10), (8, 11), (8, 12), (2, 14),
        ...                     (12, 16)])
        4
    """
    count = 0
    last_end = float("-inf")

    # Sorting by end time is the whole algorithm: it guarantees that when we
    # inspect an interval, no unexplored interval could finish earlier.
    for start, end in sorted(intervals, key=lambda pair: pair[1]):
        if start >= last_end:
            count += 1
            last_end = end  # the newly selected interval now bounds the rest
    return count


def fractional_knapsack(
    items: Sequence[Tuple[Number, Number]], capacity: Number
) -> float:
    """
    Return the maximum total value storable in a knapsack of `capacity`, when
    each item in items = [(weight, value), ...] may be taken *partially*.

    Greedy rule: sort by value per unit weight (density) and take items in
    that order, cutting the first item that does not fully fit.

    Why density order is optimal: if an optimal packing contains any amount
    of a less-dense item while a denser item has room left, swapping that
    amount for the denser item only increases the value. Repeated swaps yield
    the greedy packing - the exchange argument again.

    Contrast with knapsack_01 in algorithmlib.dp: when items are indivisible
    the greedy fails (the "last slot" problem) and DP is required; allowing
    fractions is exactly what makes the greedy optimal.

    Time: O(n log n) - dominated by the sort.  Space: O(1).

    Raises ValueError if capacity is negative or an item has non-positive
    weight (density sorting divides by weight).

    Example:
        >>> fractional_knapsack([(10, 60), (20, 100), (30, 120)], 50)
        240.0
    """
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    if any(weight <= 0 for weight, _value in items):
        raise ValueError("item weights must be positive")

    total = 0.0
    remaining = float(capacity)

    # Take items from highest value-per-weight to lowest. When the next item
    # does not fully fit, cut it: fractional items make that optimal.
    for weight, value in sorted(
        items, key=lambda item: item[1] / item[0], reverse=True
    ):
        if remaining <= 0:
            break
        take = min(float(weight), remaining)
        total += take * (value / weight)  # value is proportional to weight
        remaining -= take
    return total


def huffman_codes(
    frequencies: Mapping[T, Number],
) -> Dict[T, str]:
    """
    Return a minimum-cost prefix code for the symbols in frequencies: a dict
    mapping each symbol to a binary string such that no code is a prefix of
    another, minimizing the total cost sum(freq[s] * len(code[s])). This is
    Huffman coding, the algorithm behind ZIP, JPEG and MP3.

    A prefix code is a binary tree with symbols on the leaves; the code of a
    symbol is the path of 0/1 turns from the root, and the "no code is a
    prefix of another" rule is exactly "symbols live on leaves". The cost of
    a tree is the depth of each leaf times its frequency, and Huffman's
    insight is the *bottom-up* merge:

    1. Start with every symbol as a one-node tree weighted by its frequency.
    2. Merge the two trees with the smallest weights into one whose weight is
       their sum - this costs one extra bit for every symbol inside either.
    3. Repeat until a single tree remains.

    Optimality (exchange argument): in some optimal tree the two least
    frequent symbols are siblings at maximum depth; merging them first can
    therefore never preclude an optimal code, and induction on the merged
    problem completes the proof.

    Time: O(n log n) via the heap.  Space: O(n).

    Example:
        >>> huffman_codes({"a": 45, "b": 13, "c": 12, "d": 16, "e": 9,
        ...                "f": 5})   # the classic textbook frequencies
        {'a': '0', 'c': '100', 'b': '101', 'f': '1100', 'e': '1101', 'd': '111'}
    """
    if not frequencies:
        return {}
    for symbol, freq in frequencies.items():
        if freq <= 0:
            raise ValueError(f"frequency of {symbol!r} must be positive")

    # Heap entries are (weight, counter, tree). The counter breaks weight
    # ties so the heap never compares trees against each other.
    counter = 0
    heap: List[Tuple[Number, int, object]] = []
    for symbol, freq in frequencies.items():
        heapq.heappush(heap, (freq, counter, _Leaf(symbol)))
        counter += 1

    # Bottom-up: repeatedly fuse the two lightest trees.
    while len(heap) > 1:
        weight1, _c1, left = heapq.heappop(heap)
        weight2, _c2, right = heapq.heappop(heap)
        heapq.heappush(heap, (weight1 + weight2, counter, _Node(left, right)))
        counter += 1

    root = heap[0][2]
    codes: Dict[T, str] = {}

    # Iterative walk so skewed trees cannot hit the recursion limit (Fibo-
    # nacci-like frequency distributions produce trees thousands deep, and
    # the caller's alphabet size should never be capped by the call stack).
    stack = [(root, "")]
    while stack:
        tree, prefix = stack.pop()
        if isinstance(tree, _Leaf):
            # A single-symbol alphabet would produce the empty code; "0" is
            # the conventional unambiguous choice there.
            codes[tree.symbol] = prefix or "0"
        else:
            # Push right first so left pops first: codes are assigned
            # left-to-right, matching a recursive traversal.
            stack.append((tree.right, prefix + "1"))  # type: ignore[union-attr]
            stack.append((tree.left, prefix + "0"))  # type: ignore[union-attr]
    return codes
