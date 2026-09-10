"""
algorithmlib.searching - binary search and its bound-finding variants.

Binary search is the canonical example of a *divide and conquer* search: each
comparison halves the region still under consideration, which is why it finds
an answer among n sorted items in only O(log n) comparisons - about 20 steps
for a million items.

The functions below form a coherent family, and they are all expressed
against the *same* half-open interval convention [lo, hi) used by Python's
own slicing. Getting comfortable with that convention is half the battle of
writing bug-free binary searches:

    lo = 0, hi = len(items)     # candidate region: items[lo .. hi-1]
    while lo < hi:              # region not yet empty
        mid = (lo + hi) // 2    # integer midpoint, rounds down
        ...

`exponential_search` extends the family to unbounded or unknown-size sorted
sequences (the "search an infinite array" interview problem): it doubles a
probe index until it brackets the target, then runs plain binary search on
the bracket. The same doubling trick - galloping - appears inside timsort's
merge step.

Python's `bisect` module ships lower_bound and upper_bound (as bisect_left /
bisect_right) in optimized C; these versions exist to show the machinery.

Everything here works on any sorted *sequence* (list, tuple, range, ...) of
mutually comparable values. If the collection is not sorted, the results are
meaningless - binary search can only *exploit* order, it cannot create it.

Why several functions instead of one? Interviewers love asking for "first
occurrence" / "last occurrence" / "insertion point" variants of binary search.
`lower_bound` and `upper_bound` answer all of those questions with one piece
of reasoning: they are the C++-style std::lower_bound / std::upper_bound, and
every "search for a value with duplicates" problem reduces to them.
"""

from collections.abc import Sequence
from typing import Optional, TypeVar

T = TypeVar("T")  # a comparable element type


def _lower_bound_range(
    items: Sequence[T], target: T, lo: int, hi: int
) -> int:
    """
    Shared binary-search kernel: in items[lo:hi], return the index of the
    first element >= target, or hi if every element is smaller.

    Invariant: everything in items[:lo] is < target, everything in items[hi:]
    is >= target. The region [lo, hi) shrinks by half each step, and when it
    collapses the two zones meet exactly at the answer.

    Keeping the two bounds as parameters is what lets lower_bound search the
    whole sequence and exponential_search search only its bracket - one loop,
    no duplicated off-by-one risk. (Python's bisect_left takes lo/hi too.)
    """
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < target:
            # items[mid] belongs to the "smaller" zone; the answer is to the
            # right, and we may even advance past mid itself.
            lo = mid + 1
        else:
            # items[mid] >= target, so mid is a *candidate* answer; the real
            # first qualifying element can only be at mid or to its left.
            hi = mid
    return lo


def lower_bound(items: Sequence[T], target: T) -> int:
    """
    Return the index of the first element >= target (i.e. the position where
    target would be *inserted* while keeping items sorted).

    If every element is strictly smaller than target, len(items) is returned.

    This is the workhorse: it finds where a value belongs, so it handles
    duplicates gracefully. Compare with `upper_bound`, which returns the
    first index whose element is strictly *greater* than target - so

        [lower_bound(a, x), upper_bound(a, x))

    is exactly the (possibly empty) range of positions holding x.

    Time: O(log n).  Space: O(1).

    Example:
        >>> lower_bound([1, 3, 3, 3, 5, 7], 3)
        1
        >>> lower_bound([1, 3, 3, 3, 5, 7], 4)
        4
        >>> lower_bound([1, 3, 3, 3, 5, 7], 9)
        6

    (Equivalently: C++ std::lower_bound, Python bisect.bisect_left.)
    """
    return _lower_bound_range(items, target, 0, len(items))


def upper_bound(items: Sequence[T], target: T) -> int:
    """
    Return the index of the first element > target (the insertion point that
    keeps all copies of target to its left).

    Time: O(log n).  Space: O(1).

    Example:
        >>> upper_bound([1, 3, 3, 3, 5, 7], 3)
        4
        >>> upper_bound([1, 3, 3, 3, 5, 7], 2)
        1

    (Equivalently: C++ std::upper_bound, Python bisect.bisect_right.)
    """
    lo, hi = 0, len(items)

    # Same shape as lower_bound, but the invariant zones are reversed:
    # items[:lo] are all <= target and items[hi:] are all > target, so we
    # look for the first strictly-greater element. "<= target" is written
    # as "not (target < items[mid])" so only `<` comparisons are needed -
    # types that define just __lt__ (all Python's sort needs) work here too.
    while lo < hi:
        mid = (lo + hi) // 2
        if not (target < items[mid]):
            lo = mid + 1  # mid is not past target; keep scanning right
        else:
            hi = mid  # mid is a candidate; the answer may sit further left
    return lo


def exponential_search(items: Sequence[T], target: T) -> Optional[int]:
    """
    Return the index of target in the sorted sequence items, or None if it
    is not present - using exponential search: find a range that must contain
    target by *doubling* the upper bound, then binary-search inside it.

    Exponential search is the answer to the classic "search an infinite
    (or unknown-size) sorted array" problem: you cannot take len(items), so
    you probe indices 1, 2, 4, 8, ... until items[bound] >= target (or the
    array ends), which brackets target inside [bound // 2, bound] - every
    index below bound // 2 is then known to be smaller than target (by
    sortedness), so a binary search over the bracket finds the answer. A
    plain binary search on an unbounded array has no place to start; doubling
    gives you one in O(log i) probes, where i is the answer's index.

    For bounded arrays it shines when target sits near the front (a linear
    scan up to index i would be O(i)); the doubling stays logarithmic.

    Time: O(log i) for the probe phase plus O(log i) for the binary search,
    where i is the target's index (worst case O(log n)).
    Space: O(1).

    Example:
        >>> exponential_search([1, 3, 5, 7, 9, 11, 13], 11)
        5
        >>> exponential_search([1, 3, 5], 4) is None
        True
    """
    n = len(items)
    if n == 0:
        return None

    # Probe powers of two until we overshoot the target (or the array ends).
    # Every index below the final bound // 2 is known to be < target, because
    # the probes it shrank past all held smaller values (sortedness carries).
    bound = 1
    while bound < n and items[bound] < target:
        bound *= 2

    # The answer lies in [bound // 2, bound]: the kernel searches the
    # half-open part, and index `bound` itself (if in range) is checked by the
    # equality test below.
    lo = _lower_bound_range(items, target, bound // 2, min(bound, n))

    if lo < n:
        if not (items[lo] < target) and not (target < items[lo]):
            return lo  # found: items[lo] is neither < nor > target
    return None


def binary_search(items: Sequence[T], target: T) -> Optional[int]:
    """
    Return the index of target in the sorted sequence items, or None if it is
    not present. When the sequence holds duplicates, the *first* matching
    position is returned (the last is upper_bound(items, target) - 1) - see
    lower_bound / upper_bound for the full range.

    Time: O(log n).  Space: O(1).

    Example:
        >>> binary_search([1, 3, 5, 7, 9], 7)
        3
        >>> binary_search([1, 3, 5, 7, 9], 8) is None
        True
    """
    # Delegate to lower_bound: the first element >= target either *is* the
    # target (found) or proves the target is absent (everything from here on
    # is strictly larger). Reusing one loop keeps every variant bug-free.
    #
    # The membership test is written as "neither is smaller than the other"
    # instead of ==, so types that implement only __lt__ (no __eq__ beyond
    # identity) are handled correctly: under a strict weak ordering the two
    # formulations agree whenever the elements are truly equal.
    idx = lower_bound(items, target)
    if idx < len(items):
        if not (items[idx] < target) and not (target < items[idx]):
            return idx
    return None
