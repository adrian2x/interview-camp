"""
algorithmlib.randomized - classical randomized algorithms as single calls.

Both algorithms consume one input and produce one output, with the twist
that the output is random: a uniformly shuffled permutation of the input, or
a uniformly random k-subset drawn from a possibly endless stream.

    fisher_yates       the unbiased in-place shuffle (a.k.a. Knuth shuffle)
    reservoir_sample   draw k items uniformly from a stream of unknown size

The shared lesson: to sample uniformly you must decide each element's fate
with the *right probability at the right time*, and both algorithms get that
probability from a single randrange. Fisher-Yates proves unbiasedness by a
backward argument (each position ends up holding each element with
probability exactly 1/n); reservoir sampling proves it by induction (after i
elements, every element seen is in the sample with probability k/i).

Both accept an optional random.Random instance (e.g. random.Random(42)) so
results are reproducible; by default they use the global random module (a
module also exposes randrange, so `rng or random` makes either work).

Related stdlib note: for an already-materialized sequence, random.sample is
essentially the *partial* Fisher-Yates - only the k positions that matter are
shuffled, giving O(k) instead of O(n). reservoir_sample below is what you use
when the input is a stream of unknown length.
"""

import random
from collections.abc import Iterable, MutableSequence
from typing import List, Optional, TypeVar

T = TypeVar("T")


def fisher_yates(
    items: MutableSequence[T], rng: Optional[random.Random] = None
) -> MutableSequence[T]:
    """
    Shuffle items in place into a uniformly random permutation (Fisher-Yates,
    a.k.a. the Knuth shuffle), and return items.

    The naive shuffle - swap every element with a uniformly chosen position -
    produces some permutations more often than others (it makes n^n equally
    likely *choice sequences* map unevenly onto n! permutations). Fisher-Yates
    fixes this by restricting each step's choice to the *unshuffled* suffix:

        for i from n-1 down to 1:
            j = randrange(i + 1)      # j uniform in [0, i]
            swap(items[i], items[j])

    Unbiasedness: when position i is decided, it is equally likely to receive
    any of the i + 1 elements still in the prefix - and because every later
    step only touches earlier positions, that decision is never revisited.
    A quick count shows every permutation is produced by exactly one choice
    sequence (n * (n-1) * ... * 2 possibilities = n!), so all are equal.

    Time: O(n).  Space: O(1).

    Example:
        >>> rng = random.Random(2026)
        >>> deck = [1, 2, 3, 4, 5]
        >>> fisher_yates(deck, rng) is deck   # shuffled in place
        True
    """
    rng = rng or random
    for i in range(len(items) - 1, 0, -1):
        j = rng.randrange(i + 1)  # any position in the still-unshuffled part
        items[i], items[j] = items[j], items[i]
    return items


def reservoir_sample(
    items: Iterable[T], k: int, rng: Optional[random.Random] = None
) -> List[T]:
    """
    Return a uniformly random sample of k elements drawn from items, without
    knowing how many elements items has (reservoir sampling, Vitter's
    Algorithm R). Raises ValueError if k is negative.

    The algorithm keeps a "reservoir" of the first k elements, then streams
    through the rest. When element number i (0-based) arrives and i >= k, it
    joins the reservoir with probability k / (i + 1), replacing a uniformly
    chosen resident:

        j = randrange(i + 1)
        if j < k: reservoir[j] = element

    Why uniform? Inductively, after element number i is processed every
    element seen is in the reservoir with probability k / (i + 1). A newcomer
    gets in with exactly that probability; an old resident survives because
    the newcomer misses it (prob 1 - k/(i+1)) or replaces a different slot
    (prob (k-1)/k of the k/(i+1) cases) - and the arithmetic works out to
    k/(i+2) for the next round. Only O(k) memory is ever used, no matter how
    long the stream is.

    If items has fewer than k elements, the whole stream is returned in order.

    Time: O(n) with O(1) work per element.
    Space: O(k).

    Example:
        >>> rng = random.Random(2026)
        >>> sample = reservoir_sample(range(100), 5, rng)
        >>> len(sample) == 5 and all(0 <= x < 100 for x in sample)
        True
        >>> reservoir_sample([1, 2, 3], 10)   # fewer elements than k: all
        [1, 2, 3]
        >>> reservoir_sample([1, 2, 3], 0)
        []
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    rng = rng or random

    reservoir: List[T] = []
    # Phase 1: the first k elements always enter (nothing decided yet).
    for i, element in enumerate(items):
        if i < k:
            reservoir.append(element)
            continue
        # Phase 2: element i (>= k) enters with probability k / (i + 1).
        j = rng.randrange(i + 1)
        if j < k:
            reservoir[j] = element
    return reservoir
