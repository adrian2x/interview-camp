"""
algorithmlib.sorting - reference implementations of the classical sorts,
plus quickselect, the selection algorithm that shares quicksort's machinery.

Reading order (each builds on ideas from the previous ones):

1. insertion_sort - the "online" sort: cheap for small inputs, O(1) extra
   space, stable. Every hybrid sort below secretly uses it for small slices.
2. merge_sort     - the canonical divide-and-conquer sort: guaranteed
   O(n log n), stable, but pays O(n) auxiliary space for the merge buffer.
3. quicksort      - the other divide-and-conquer sort: in-place partitioning,
   no auxiliary buffer, average O(n log n). Unstable, worst case O(n^2).
4. heapsort       - selection-sort done right: an implicit binary heap inside
   the array gives guaranteed O(n log n) with O(1) extra space.
5. timsort        - what Python's sorted() actually runs: a hybrid of natural
   run detection, binary insertion sort, and merge sort. Stable, adaptive.
6. quickselect    - quicksort's partition applied to *one* side only: find the
   k-th smallest element in O(n) expected time without sorting everything.

Convention (matching the rest of this repo, e.g. algorithms/quicksort.py):
every sort mutates the list it is given and *returns it*, so callers may write
    data = merge_sort(data)
or chain the call. Pass a copy (data[:]) if the original must be preserved.

Elements only need to support < (comparison). Sorting is not stable unless the
docstring says so; stability means equal elements keep their relative order.
"""

from collections.abc import MutableSequence
from typing import TypeVar

T = TypeVar("T")  # a comparable element type


def _swap(items: MutableSequence[T], i: int, j: int) -> None:
    """Swap two positions. Kept as a helper so the algorithms read cleanly."""
    items[i], items[j] = items[j], items[i]


# Sorting a very short slice is faster with insertion sort than with more
# divide-and-conquer: the recursion/partition overhead dominates below ~16
# elements, and insertion sort touches the elements in a cache-friendly
# linear sweep. This is the classic quicksort/mergesort "hybrid" cutoff -
# values anywhere in the 8-32 range behave similarly (CPython uses 64 for
# timsort's binary-insertion runs; the classic literature uses 5-20).
_INSERTION_CUTOFF = 16


def _insertion_sort_range(
    items: MutableSequence[T], lo: int, hi: int
) -> None:
    """
    Sort items[lo:hi] in place using insertion sort - the shared small-slice
    workhorse called by merge_sort, quicksort and (in spirit) timsort.

    Invariant: after iteration i, items[lo:i+1] is sorted. The element at i
    is the "card being placed" and slides left over everything strictly
    larger than it (a strict `<`, never `<=`, which keeps equal elements in
    their original order - stability).

    (timsort uses the binary-search variant `_binary_insert` for its runs:
    the same shifting scheme, but locating the insertion point in O(log n)
    instead of scanning.)
    """
    for i in range(lo + 1, hi):
        current = items[i]  # the card being placed
        j = i - 1
        while j >= lo and current < items[j]:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = current


# ---------------------------------------------------------------------------
# 1. Insertion sort
# ---------------------------------------------------------------------------


def insertion_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """
    Sort items in place using insertion sort, and return items.

    Imagine sorting a hand of cards: you keep a growing *sorted prefix*
    items[:i] and, at each step, slide the next card left until it lands
    between its two neighbours.

    Why it matters:
    * O(1) extra space - it sorts by shifting, never by copying to a buffer.
    * Adaptive: on an already-sorted (or nearly sorted) input the inner loop
      exits almost immediately, giving O(n) best case. That is why the hybrid
      sorts - timsort, and quicksort variants with a small-slice cutoff -
      fall back to insertion sort for their short runs.
    * Stable: we only shift an element left while it is *strictly smaller*
      than its neighbours (a strict `<`, never `<=`): equal elements never
      jump over each other.
    * Worst case O(n^2) when the input is reverse-sorted - every new element
      travels all the way to the front.

    Time: O(n^2) worst / O(n) best.  Space: O(1).

    Example:
        >>> insertion_sort([5, 2, 9, 1, 7])
        [1, 2, 5, 7, 9]
    """
    # The loop lives in _insertion_sort_range because the hybrid sorts below
    # reuse it for their small slices.
    _insertion_sort_range(items, 0, len(items))
    return items


# ---------------------------------------------------------------------------
# 2. Merge sort
# ---------------------------------------------------------------------------


def _merge_into(
    items: MutableSequence[T],
    lo: int,
    mid: int,
    hi: int,
    buffer: MutableSequence[T],
) -> None:
    """
    Merge the two sorted halves items[lo:mid] and items[mid:hi] into one
    sorted run items[lo:hi], using buffer as scratch space.

    The merge itself is the heart of merge sort - and of timsort below, which
    reuses this exact helper. Two fingers walk the two sorted halves; the
    smaller head is copied out each time. Copying the result back into items
    is what keeps the sort in-place from the caller's point of view.

    Stability: when the halves offer equal values we take from the *left*
    half first (the `<` on the right side), so relative order is preserved.
    """
    i, j = lo, mid  # fingers into the left and right halves
    k = lo  # write position in the buffer

    # Walk both halves at once, always emitting the smaller head.
    while i < mid and j < hi:
        if items[j] < items[i]:
            buffer[k] = items[j]  # right head is strictly smaller
            j += 1
        else:
            buffer[k] = items[i]  # left head wins ties -> stability
            i += 1
        k += 1

    # One half is exhausted; drain the other (it is already sorted).
    while i < mid:
        buffer[k] = items[i]
        i += 1
        k += 1
    while j < hi:
        buffer[k] = items[j]
        j += 1
        k += 1

    # Copy the merged run back over the original region.
    items[lo:hi] = buffer[lo:hi]


def _msort(
    items: MutableSequence[T],
    lo: int,
    hi: int,
    buffer: MutableSequence[T],
) -> None:
    """
    Sort items[lo:hi] (half-open) with the classic top-down recursion.

    The recursion tree explains the complexity: each level of the tree merges
    every element exactly once (O(n) work per level) and the tree is log n
    levels tall, so the total is O(n log n) - guaranteed, no bad inputs.
    """
    if hi - lo <= 1:
        return  # zero or one element: nothing to sort

    # Optimization - the small-slice cutoff: below _INSERTION_CUTOFF elements,
    # insertion sort finishes the slice faster than more recursive splitting
    # (no recursion overhead, one linear pass). It changes no asymptotics,
    # only the constants, and it keeps the sort stable.
    if hi - lo <= _INSERTION_CUTOFF:
        _insertion_sort_range(items, lo, hi)
        return

    mid = (lo + hi) // 2
    _msort(items, lo, mid, buffer)
    _msort(items, mid, hi, buffer)

    # Optimization: if the largest of the left half already sits before the
    # smallest of the right half, the two halves are globally sorted and the
    # merge can be skipped. This is what gives merge sort its O(n) best case
    # on already-sorted input.
    if items[mid - 1] > items[mid]:
        _merge_into(items, lo, mid, hi, buffer)


def merge_sort(items: MutableSequence[T]) -> MutableSequence[T]:
    """
    Sort items in place with top-down merge sort, and return items.

    Divide: split the list in half. Conquer: sort each half recursively.
    Combine: merge the two sorted halves into one sorted run.

    Merge sort is the sort to name when the question is "stable and
    guaranteed O(n log n)": it has no bad inputs and never rearranges equal
    elements. Its one weakness is the O(n) auxiliary buffer used by the
    merge step - that is the price of combining two sorted lists.

    One buffer is allocated up front and reused by every merge in the
    recursion (each level also copies back), so the auxiliary space stays
    O(n) rather than O(n log n). Recursion stops at slices of
    _INSERTION_CUTOFF elements or fewer, which are finished by insertion
    sort - the standard hybrid trick that removes most of the recursion's
    constant-factor cost.

    Time: O(n log n) always.  Space: O(n).

    Example:
        >>> merge_sort([5, 2, 9, 1, 7])
        [1, 2, 5, 7, 9]
    """
    if len(items) > 1:
        buffer = items[:]  # reusable scratch, same size as the input
        _msort(items, 0, len(items), buffer)
    return items


# ---------------------------------------------------------------------------
# 3. Quicksort
# ---------------------------------------------------------------------------


def _median3_pivot(items: MutableSequence[T], lo: int, hi: int) -> T:
    """
    Pick a pivot for the [lo, hi) region: the median of the first, middle and
    last elements. The median is moved to position hi - 1 and returned.

    Why bother? If the pivot is the region's smallest or largest element the
    partition is lopsided and quicksort degrades toward O(n^2). Taking the
    median of three is a cheap heuristic that tames sorted and reverse-sorted
    inputs (the classic worst cases when the pivot is simply one end).
    """
    mid = lo + (hi - lo - 1) // 2  # the middle index of the region

    # A 3-element sorting network: three compare-and-swap steps order the
    # values at lo, mid and hi - 1 so that items[lo] <= items[mid] <=
    # items[hi-1], using only `<` comparisons (all the element type must
    # provide - never `<=`).
    if items[mid] < items[lo]:
        _swap(items, lo, mid)
    if items[hi - 1] < items[lo]:
        _swap(items, lo, hi - 1)
    if items[hi - 1] < items[mid]:
        _swap(items, mid, hi - 1)

    # items[mid] now holds the median value. Park it at hi - 1 (the slot
    # Lomuto's partition expects its pivot in) and return it. The swap is a
    # no-op when the region is tiny and mid == hi - 1.
    _swap(items, mid, hi - 1)
    return items[hi - 1]


def _partition(items: MutableSequence[T], lo: int, hi: int) -> int:
    """
    Lomuto partition of items[lo:hi] around a pivot chosen by _median3_pivot.

    Returns the pivot's final index p, with the region rearranged so that

        items[lo:p]   <= pivot
        items[p]       == pivot
        items[p+1:hi]  >= pivot

    The loop invariant: after processing position j, everything in
    items[lo:i] is <= pivot (the "small zone") and everything in
    items[i:j] is > pivot (the "large zone", already inspected). Position j
    itself is the frontier being inspected. When an element <= pivot is
    found it is swapped into the small zone and the zone grows by one.

    Lomuto is easier to reason about and to get right than Hoare's scheme
    (which the repo's algorithms/quicksort.py implements); Hoare does fewer
    swaps on average but has subtler boundary conditions.
    """
    pivot = _median3_pivot(items, lo, hi)  # pivot now lives at hi - 1

    i = lo  # right edge of the "small zone"
    # Inspect everything except the pivot's parking spot (hi - 1).
    for j in range(lo, hi - 1):
        # Belong in the small zone: not *greater* than the pivot. Written
        # with only `<` (no `<=`) so any __lt__-only type can be sorted.
        if not (pivot < items[j]):
            _swap(items, i, j)
            i += 1

    # Drop the pivot between the two zones: everything left of i is <= pivot,
    # everything from i onward (including the pivot's old spot) is > pivot.
    _swap(items, i, hi - 1)
    return i


def _qsort(items: MutableSequence[T], lo: int, hi: int) -> None:
    """
    Sort items[lo:hi] with quicksort.

    Two standard optimizations are at work here:

    * Small-slice cutoff: once a region shrinks to _INSERTION_CUTOFF elements
      or fewer, insertion sort finishes it (partition overhead no longer pays
      for itself at that size). This is what makes quicksort "hybrid" and is
      part of why real implementations beat the textbook version.
    * Recurse on the *smaller* side and loop on the larger one: the recursion
      depth is then bounded by O(log n) even in the worst case, because each
      recursive call works on at most half of the current region.
    """
    while hi - lo > _INSERTION_CUTOFF:
        p = _partition(items, lo, hi)  # pivot now at its final position
        left_size = p - lo
        right_size = hi - p - 1
        if left_size < right_size:
            _qsort(items, lo, p)  # small side: recurse
            lo = p + 1  # large side: continue the loop
        else:
            _qsort(items, p + 1, hi)
            hi = p

    # Whatever region remains is short: finish it with one insertion pass.
    _insertion_sort_range(items, lo, hi)


def quicksort(items: MutableSequence[T]) -> MutableSequence[T]:
    """
    Sort items in place with quicksort, and return items.

    Quicksort is the workhorse of the real world (C's qsort, and the
    partition step inside many libraries) because it sorts *in place* with no
    auxiliary buffer and, on average, fewer comparisons than merge sort.

    How it works: pick a pivot, partition the region so everything smaller
    than the pivot sits left of it and everything larger sits right (the
    pivot itself lands at its final sorted position), then sort each side
    independently.

    Caveats to know for interviews:
    * Unstable - partitioning can swap equal elements past each other.
    * Average O(n log n), worst case O(n^2). The worst case happens when the
      pivot is always an extreme value; the median-of-three pivot above
      defends against the common triggers (sorted / reverse-sorted input).
      A randomized pivot (like the repo's own quicksort) defends against
      adversarial inputs at the price of non-determinism.
    * Degenerates to O(n^2) when almost all elements are *equal*: the pivot
      equals everything, so each partition peels off one element. The fix is
      a 3-way (Dutch National Flag) partition that groups equal values in
      the middle - see the notebooks' "sort 0s, 1s and 2s" problem.
    * Not adaptive in the pure form, but the small-slice insertion cutoff in
      _qsort above (and timsort below) take care of the common "almost
      sorted" cases cheaply.

    Time: O(n log n) average, O(n^2) worst.  Space: O(log n) stack.

    Example:
        >>> quicksort([5, 2, 9, 1, 7])
        [1, 2, 5, 7, 9]
    """
    if len(items) > 1:
        _qsort(items, 0, len(items))
    return items


# ---------------------------------------------------------------------------
# 4. Heapsort
# ---------------------------------------------------------------------------


def _sift_down(items: MutableSequence[T], start: int, end: int) -> None:
    """
    Restore the max-heap property in items[start:end] assuming every node
    except possibly items[start] already satisfies it.

    A binary heap stored in an array places node i's children at 2i+1 and
    2i+2. "Sifting down" means: while the current node has a child larger
    than itself, swap it with the *larger* child and continue there. Swapping
    with the larger child matters - swapping with the smaller one could leave
    the other child violating the heap property.
    """
    root = start
    while True:
        child = 2 * root + 1
        if child >= end:
            break  # no children left: heap property holds

        # Pick the larger of the two children, if a right child exists.
        # `items[child] < items[child + 1]` reads as "<" only, matching the
        # convention used across this module.
        if child + 1 < end and items[child] < items[child + 1]:
            child += 1

        # Stop when the root is not smaller than its larger child, i.e. the
        # heap property already holds (again expressed via < only).
        if not (items[root] < items[child]):
            break
        _swap(items, root, child)
        root = child


def heapsort(items: MutableSequence[T]) -> MutableSequence[T]:
    """
    Sort items in place with heapsort, and return items.

    Heapsort is "selection sort with a better data structure": selection sort
    scans the whole array to find each next maximum (O(n) per pick, O(n^2)
    total); heapsort organizes the array as an implicit max-heap so each
    maximum is retrieved in O(log n).

    Phase 1 - build the heap in O(n): the leaves (indices >= n // 2) are
    already valid heaps of size 1, so sift down every internal node from the
    bottom up. The classic "why is heapify O(n) not O(n log n)?" argument:
    most nodes sit near the leaves and sift only a few levels.

    Phase 2 - extract maxima: repeatedly swap the heap's maximum (at index 0)
    with the last element, shrink the heap by one, and sift the new root
    down. The sorted suffix grows from the right end of the array.

    Trade-offs: guaranteed O(n log n) with only O(1) extra space (the best
    of both merge and quick sort on paper). In practice it is beaten by
    quicksort's cache behaviour and merge sort's stability - and heapsort is
    *unstable*, like quicksort.

    Time: O(n log n) always.  Space: O(1).

    Example:
        >>> heapsort([5, 2, 9, 1, 7])
        [1, 2, 5, 7, 9]
    """
    n = len(items)

    # Phase 1: heapify. Internal nodes are indices n//2 - 1 down to 0.
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(items, start, n)

    # Phase 2: pop the max into the growing sorted suffix.
    for end in range(n - 1, 0, -1):
        _swap(items, 0, end)  # max -> its final position
        _sift_down(items, 0, end)  # repair the heap on items[:end]
    return items


# ---------------------------------------------------------------------------
# 5. Timsort - the adaptive hybrid behind Python's sorted()
# ---------------------------------------------------------------------------


def _minrun(n: int) -> int:
    """
    Choose a minimum run length for timsort.

    CPython's heuristic: pick minrun so that n / minrun is a power of two
    (or just under one), which makes the later pairwise merges as balanced
    as possible. The bit trick computes this in one pass: shift n right
    until it is below 64, keeping the discarded low bits in r.
    """
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


def _binary_insert(items: MutableSequence[T], lo: int, hi: int) -> None:
    """
    Insertion-sort items[lo:hi] assuming items[lo] starts an already-sorted
    run. Each element is located with a binary search over the sorted prefix
    instead of a linear scan (the trick that gives timsort its edge over
    plain insertion sort on long runs).
    """
    for i in range(lo + 1, hi):
        value = items[i]

        # Binary search for the first index p in [lo, i) with items[p] > value
        # (i.e. the insertion point). "items[p] <= value" is written as
        # "not (value < items[p])" so only `<` comparisons are needed, and
        # equal values stay put to the left of the insertion point, which is
        # what keeps this insertion sort stable.
        p, q = lo, i
        while p < q:
            m = (p + q) // 2
            if not (value < items[m]):
                p = m + 1
            else:
                q = m

        # Shift items[p:i] one slot right and drop value into the gap.
        # (When p == i the slice is empty and this is just a no-op store.)
        items[p + 1 : i + 1] = items[p:i]
        items[p] = value


def timsort(items: MutableSequence[T]) -> MutableSequence[T]:
    """
    Sort items in place with a simplified Timsort, and return items.

    This is the algorithm Python's sorted() and list.sort() actually run, and
    it is the reason sorting a mostly-sorted list in Python is nearly free.
    Timsort is a *hybrid* that combines three ideas:

    1. Natural runs - scan the input once and keep whatever order is already
       there. A descending run is simply reversed (one pass, still O(1)
       extra space) so it becomes an ascending run.
    2. Binary insertion sort - any run shorter than minrun (about 32-64) is
       extended by inserting the following elements into it with binary
       search, which is cheap for small slices.
    3. Merge sort - the runs are then merged pairwise in passes, reusing the
       same _merge_into helper as merge_sort. Every element participates in
       one merge per pass and the number of runs at least halves per pass,
       so the total stays O(n log n) even on adversarial input.

    Two real-Timsort optimizations are omitted here for clarity:
    * the pending-run stack with strict merge invariants (we merge in simple
      passes instead - same worst case, slightly less adaptive),
    * galloping mode, which uses binary search to skip over large stretches
      when one run is winning a merge decisively.

    Stability: inherited from the merge helper and the insertion sorts.

    Time: O(n log n) worst, O(n) best (already sorted).
    Space: O(n) for the merge buffer.

    Example:
        >>> timsort([5, 2, 9, 1, 7])
        [1, 2, 5, 7, 9]
    """
    n = len(items)
    if n < 2:
        return items

    minrun = _minrun(n)
    buffer = items[:]  # one reusable merge buffer, as in merge_sort

    # Pass 1: split the input into runs of at least minrun elements.
    # boundaries holds the start index of each run, plus n as a sentinel, so
    # run i occupies items[boundaries[i] : boundaries[i + 1]].
    boundaries = [0]
    start = 0
    while start < n:
        # (a) Detect one natural run starting at `start`.
        if start + 1 >= n:
            end = n
        elif items[start + 1] < items[start]:
            # Strictly descending run: count it, then reverse it in place so
            # the run becomes ascending. Equal neighbours stop the descent
            # (reversing equals is unnecessary and would be unstable).
            end = start + 1
            while end < n and items[end] < items[end - 1]:
                end += 1
            items[start:end] = reversed(items[start:end])
        else:
            # Ascending or flat run. ">= " is written as "not smaller than"
            # so only `<` comparisons are needed; equals stay inside the run.
            end = start + 1
            while end < n and not (items[end] < items[end - 1]):
                end += 1

        # (b) Pad short runs up to minrun with binary insertion sort.
        if end - start < minrun:
            end = min(start + minrun, n)
            _binary_insert(items, start, end)

        boundaries.append(end)
        start = end

    # Pass 2: merge adjacent runs pairwise until a single run remains.
    # Each pass at least halves the number of runs -> O(n log n) total.
    while len(boundaries) > 2:
        merged = [boundaries[0]]  # first run always starts at index 0
        i = 0
        while i + 2 < len(boundaries):
            lo, mid, hi = boundaries[i], boundaries[i + 1], boundaries[i + 2]
            _merge_into(items, lo, mid, hi, buffer)
            merged.append(hi)  # runs i and i+1 are now one run ending at hi
            i += 2
        if i + 1 == len(boundaries) - 1:
            merged.append(boundaries[-1])  # odd run out: carry it over
        boundaries = merged

    return items


# ---------------------------------------------------------------------------
# 6. Quickselect - find the k-th smallest without sorting everything
# ---------------------------------------------------------------------------


def quickselect(items: MutableSequence[T], k: int) -> T:
    """
    Return the element that would sit at index k of the fully sorted items,
    using quickselect (a.k.a. Hoare's selection algorithm). k is 0-based, so
    k=0 asks for the minimum and k=len(items)-1 for the maximum.

    The insight is that quicksort's partition places the pivot at its *final*
    sorted position. That single fact is enough to search: after partitioning
    a region we know the answer lies in exactly one of the two sides (or is
    the pivot itself), so we recurse into that side only - never sorting the
    other one. The expected cost is n + n/2 + n/4 + ... = O(n), compared to
    O(n log n) for sorting the whole list.

    Like quicksort, items is partially reordered as a side effect (that is
    inherent to partitioning); the original data is not recoverable, so pass
    a copy if you need it intact. The same duplicate-heavy inputs that slow
    quicksort to O(n^2) slow this down too (see quicksort's caveats).

    Time: O(n) expected, O(n^2) worst (median-of-three pivoting mitigates
    the usual triggers; a randomized pivot removes the adversarial case).
    Space: O(1) - the recursion is tail-loop shaped, as in _qsort.

    Guaranteed-linear alternative: the median-of-medians pivot selection
    ("BFPRT") chooses a pivot provably good enough to force O(n) even in the
    worst case, at a large constant-factor cost - which is why practical
    implementations stick with the randomized/median-of-three versions.

    Example:
        >>> quickselect([5, 2, 9, 1, 7], k=2)   # the 3rd smallest value
        5
    """
    n = len(items)
    if not 0 <= k < n:
        raise ValueError(f"k={k} out of range for a list of length {n}")

    lo, hi = 0, n
    while hi - lo > 1:
        p = _partition(items, lo, hi)  # pivot now at its final position p
        if p == k:
            break  # the pivot itself is the answer
        if k < p:
            hi = p  # answer is in the left side
        else:
            lo = p + 1  # answer is in the right side
    return items[k]
