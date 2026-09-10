"""
algorithmlib.strings - classical pattern-matching algorithms.

The pattern-matching functions below all answer the same question: *where
does pattern occur inside text?* They return the list of start indices of
every match (possibly overlapping), which is the most useful contract for
callers - an empty list means "not found".

    rabin_karp(text, pattern)          hashing + the sliding window
    kmp_search(text, pattern)          the prefix function, no hashing
    boyer_moore_horspool(text, ...)    skip ahead from the pattern's tail
    z_search(text, pattern)            the Z-array of pattern + sep + text

None of them are restricted to str. Because they only ever need equality of
elements (plus hashability for the hash-based methods: Rabin-Karp's rolling
hash and the Boyer-Moore shift table), they work on any sequence: text and
pattern may be str, bytes, tuples, or lists - matching a tuple of tokens
against a longer tuple works exactly like matching letters in a word. Try it:

    >>> from algorithmlib.strings import kmp_search
    >>> kmp_search((1, 2, 1, 2, 3), (1, 2))
    [0, 2]

Why study several algorithms for one task? The naive scan compares the
pattern against the text at every position: O(n * m) in the worst case. The
algorithms below are different strategies for *not* doing that, and each
strategy is a reusable idea:

* Rabin-Karp turns "do these m characters equal the pattern?" into "do their
  hashes match?" - a constant-time question, with a clever rolling update so
  each new window costs O(1), not O(m). The idea generalizes far beyond
  strings (think: detecting duplicate documents, or plagiarism).
* KMP preprocesses the *pattern* into a prefix function and never re-reads
  text it has already matched - text is scanned exactly once, giving the only
  *guaranteed* linear worst case of the three.
* Boyer-Moore (in its Horspool form here) starts comparing from the *end* of
  the pattern and, on a mismatch, uses a lookup table to skip whole chunks of
  text. It has the best average case in practice - which is why grep and
  modern text editors use its descendants.

Four more classical entries round the module out:

* `z_function` computes, for every position, how long the text matches its
  own prefix there - the linear-time Z-array, KMP's mirror-image cousin.
* `z_search` uses the Z-array for pattern matching by concatenating
  pattern + separator + text: every position whose Z-value reaches the
  pattern length is a match.
* `manacher` finds the longest palindromic substring in linear time, using
  the fact that palindromes nest symmetrically around their center.
* `hamming_distance` counts positions where two equal-length sequences
  differ - the simplest string metric, and the right one for fixed-length
  codes (DNA barcodes, error-correcting codes, binary fingerprints).

Convention: an empty pattern raises ValueError (matching "nothing" everywhere
is almost never what a caller means, and silently returning every index is a
footgun); a non-empty pattern in an empty or shorter text returns [].
"""

from collections.abc import Hashable, Sequence
from typing import Any, List, Tuple, TypeVar

T = TypeVar("T")  # any sequence element type (equality is enough)
H = TypeVar("H", bound=Hashable)  # elements that can be hashed (hash-based methods)


# ---------------------------------------------------------------------------
# Rabin-Karp: rolling hash search
# ---------------------------------------------------------------------------

# Rolling arithmetic is done modulo 2^64 - unsigned machine-word arithmetic,
# the same thing C does implicitly on size_t overflow. The base is odd, so it
# is coprime to the modulus and the polynomial hash stays well distributed.
# (CLRS and Sedgewick use a large - often random - prime modulus instead;
# both choices are fine in an interview, just be ready to say why. A masked
# modulus is only risky for *unverified* hashing: crafted collisions can slow
# it down, but every hit here is verified, so worst case is time, never
# correctness.)
#
# The hash itself is polynomial: h = x[0]*B^(m-1) + x[1]*B^(m-2) + ... + x[m-1],
# built incrementally as h = h*B + x. That shape is what allows the O(1)
# slide below. Note that Python's hash() is salted per process for strings,
# so hash values differ between runs - slightly different collision patterns,
# but identical (always-correct) results, because collisions are verified.
_MOD = 1 << 64
_MASK = _MOD - 1
_BASE = 1_000_003  # odd, so coprime with 2^64; also CPython's hash multiplier


def _hashing(element: H) -> int:
    """Map a hashable element to a 64-bit value for the rolling hash."""
    return hash(element) & _MASK


def _rolling_hash(seq: Sequence[H]) -> int:
    """Hash seq the way the window hash is built: h = h * base + element."""
    h = 0
    for element in seq:
        h = (h * _BASE + _hashing(element)) & _MASK
    return h


def rabin_karp(text: Sequence[H], pattern: Sequence[H]) -> List[int]:
    """
    Return the start indices of every (possibly overlapping) occurrence of
    pattern in text, using the Rabin-Karp rolling-hash algorithm.

    The core trick: instead of comparing m characters at every one of the
    n - m + 1 windows (naive cost O(n*m)), compare a *hash* of the window
    against a hash of the pattern - O(1) per window. When the hashes agree we
    still verify the window element by element, because hashes can collide;
    the verification is what keeps the answer exact.

    The rolling part: the hash of window [i+1, i+1+m) is derived from the
    hash of window [i, i+m) in O(1):
        - subtract the outgoing element weighted by base^(m-1),
        - multiply by base (shifting everything one slot left),
        - add the incoming element.
    This is the same recurrence used to build the hash in the first place,
    just inverted at the left edge.

    Average case O(n + m) (hash compares are cheap and verification rarely
    triggers); worst case O(n*m) when hash collisions are frequent (e.g. all
    elements equal). Space: O(1) beyond the inputs.

    Inputs must be sliceable sequences (str, bytes, list, tuple all are):
    the final verification compares slices, not individual elements.

    Example:
        >>> rabin_karp("doe are hearing me", "ear")
        [9]
        >>> rabin_karp("aaaa", "aa")          # overlapping matches
        [0, 1, 2]
    """
    if not pattern:
        raise ValueError("pattern must not be empty")
    n, m = len(text), len(pattern)
    if n < m:
        return []

    pattern_hash = _rolling_hash(pattern)
    window_hash = _rolling_hash(text[:m])

    # Weight of the character about to leave the window: base^(m-1).
    highest = pow(_BASE, m - 1, _MOD)

    matches: List[int] = []

    # Check the first window, then slide it forward n - m times (once per
    # remaining start position). Verification on every hash hit makes this a
    # Las Vegas algorithm: always exact, expected linear time.
    if window_hash == pattern_hash and text[:m] == pattern:
        matches.append(0)

    for start in range(n - m):
        # Slide the window right by one element. With the window hash
        # H = x[start]*B^(m-1) + ... + x[start+m-1], the next window's hash is
        #   H' = (H - x[start]*B^(m-1)) * B + x[start+m]
        # - drop the leaving element's top-weighted term, shift everything up
        # by one power of B, and append the entering element at weight B^0.
        leaving = _hashing(text[start])
        entering = _hashing(text[start + m])
        window_hash = (
            (window_hash - leaving * highest) * _BASE + entering
        ) & _MASK

        candidate = start + 1
        # Hash equality is necessary but not sufficient: verify to rule out
        # collisions before reporting a match.
        if window_hash == pattern_hash:
            if text[candidate : candidate + m] == pattern:
                matches.append(candidate)
    return matches


# ---------------------------------------------------------------------------
# Knuth-Morris-Pratt: the prefix function and one clean scan
# ---------------------------------------------------------------------------


def prefix_function(pattern: Sequence[T]) -> List[int]:
    """
    Return the prefix function (a.k.a. failure function) pi of pattern.

    pi[i] is the length of the longest proper prefix of pattern[:i+1] that is
    also a suffix of pattern[:i+1]. "Proper" means the whole substring does
    not count: pi is at most i.

    Example: for "aabaaab" the table is
        a  a  b  a  a  a  b
        0  1  0  1  2  2  3
    pi[6] = 3 because "aab" is both a prefix and a suffix of "aabaaab".

    The function is computed incrementally: to extend a match of length j at
    position i, look at pattern[i]. If it continues the match, pi[i] = j + 1.
    If not, *fall back*: j becomes pi[j-1], the longest border of the already
    matched prefix, and we retry. This fallback is what makes the whole
    computation linear - j only ever increases by 1 per step and its
    decreases are paid for by earlier increases.

    Time: O(m).  Space: O(m).
    """
    m = len(pattern)
    pi = [0] * m  # pi[0] is always 0: a one-letter string has no proper border

    j = 0  # length of the longest border of the prefix already processed
    for i in range(1, m):
        # pattern[i] does not continue the current border: fall back to the
        # border of the border, until a character matches or j hits 0.
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1  # the border grew by one character
        pi[i] = j
    return pi


def kmp_search(text: Sequence[T], pattern: Sequence[T]) -> List[int]:
    """
    Return the start indices of every occurrence of pattern in text using the
    Knuth-Morris-Pratt algorithm.

    KMP is the pattern-matching algorithm with the strongest guarantee: the
    text is scanned exactly once, left to right, never re-read, so the worst
    case is O(n + m) regardless of input. It is the right answer whenever the
    input is adversarial or worst-case behaviour matters.

    The scan reuses the *same* fallback logic as prefix_function, which is
    the elegant part: maintain j = length of the longest prefix of pattern
    that is a suffix of the text seen so far. On a mismatch, instead of
    restarting from scratch at the next position (naive), fall back along
    pi[j-1] - the text already consumed proves the border is there, so no
    character is wasted.

    On a full match of length m we record the position and fall back along
    pi[m-1], which is how overlapping matches (e.g. "aa" in "aaa") are found.

    Time: O(n + m) guaranteed.  Space: O(m) for the prefix table.

    Example:
        >>> kmp_search("doe are hearing me", "ear")
        [9]
        >>> kmp_search("aaaa", "aa")
        [0, 1, 2]
    """
    if not pattern:
        raise ValueError("pattern must not be empty")
    n, m = len(text), len(pattern)
    if n < m:
        return []

    pi = prefix_function(pattern)
    matches: List[int] = []
    j = 0  # characters of pattern matched against the text so far
    for i, element in enumerate(text):
        # Same fallback as in prefix_function: element does not extend the
        # current match, so shrink it along the borders of the pattern.
        while j > 0 and element != pattern[j]:
            j = pi[j - 1]
        if element == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)  # the match spans [i-m+1, i]
            j = pi[j - 1]  # look for overlaps starting inside this match
    return matches


# ---------------------------------------------------------------------------
# Boyer-Moore (Horspool variant): skip from the tail
# ---------------------------------------------------------------------------


def boyer_moore_horspool(text: Sequence[H], pattern: Sequence[H]) -> List[int]:
    """
    Return the start indices of every occurrence of pattern in text using the
    Boyer-Moore-Horspool algorithm.

    The radical idea: compare the pattern to the text window *backwards*,
    from the pattern's last character to its first. A mismatch near the end
    of the pattern carries far more information than a mismatch near the
    start, and it lets us skip large chunks of text.

    The bad-character table drives the skips: for each character that occurs
    in pattern[:-1], record how far it is from the pattern's end. When the
    window's last character (text[i + m - 1]) mismatches, we may slide the
    window right by that distance - aligning the character with its last
    occurrence in the pattern. If the character does not occur in the pattern
    at all, we slide the whole pattern past it (shift m).

    Full Boyer-Moore adds a second, "good-suffix" rule that exploits matches
    already confirmed inside the window; Horspool keeps only the bad-character
    rule, which is simpler, still sublinear on typical text, and is the form
    most implementations actually use.

    Time: O(n*m) worst case, but sublinear (~n/m) on typical text.
    Space: O(|alphabet of pattern|) for the shift table.

    Example:
        >>> boyer_moore_horspool("doe are hearing me", "ear")
        [9]
        >>> boyer_moore_horspool("aaaa", "aa")
        [0, 1, 2]
    """
    if not pattern:
        raise ValueError("pattern must not be empty")
    n, m = len(text), len(pattern)
    if n < m:
        return []

    # Bad-character shift table: how far the window may jump when its last
    # character is `ch`. Only pattern[:-1] is indexed - the pattern's own
    # last character occurring again at the very end would give shift 0.
    # The `enumerate` walk stores the *last* occurrence, because later
    # indices overwrite earlier ones. Worked example for pattern "abc":
    # shift['a'] = 2, shift['b'] = 1, and 'c' is absent (it is the last
    # character), so a window ending in 'c' falls back to the default m = 3.
    shift = {}
    for idx, ch in enumerate(pattern[:-1]):
        shift[ch] = m - 1 - idx

    matches: List[int] = []
    i = 0
    while i <= n - m:
        # Compare from the back of the pattern towards its front.
        j = m - 1
        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1

        if j < 0:
            matches.append(i)  # every character matched
            i += 1  # slide by one so overlapping matches are not missed
        else:
            # Mismatch at text[i + j]: jump the window right by the shift
            # stored for the window's *last* character (default: m).
            i += shift.get(text[i + m - 1], m)
    return matches


# ---------------------------------------------------------------------------
# The Z-algorithm: match every position against the sequence's own prefix
# ---------------------------------------------------------------------------


def z_function(seq: Sequence[T]) -> List[int]:
    """
    Return the Z-array of seq: z[i] is the length of the longest prefix of
    seq that also starts at position i (z[0] is conventionally 0 - the whole
    sequence matching itself is not counted).

    The Z-array is the mirror-image cousin of KMP's prefix function: the
    prefix function records, for each position, how far the *suffix* matches
    the prefix; the Z-array records the same for every position's suffix, and
    both enable linear-time pattern matching.

    The algorithm maintains a "Z-box" [left, right]: the rightmost interval
    known to match the prefix. When position i lies inside the box, its first
    z[i] characters are already known to equal the prefix's first z[i]
    characters - because the whole box equals the prefix - so we can copy
    z[i - left] from the mirror position (capped so it cannot leave the box)
    and only extend by brute force past the box edge. Each successful
    extension grows `right`, and right only ever moves forward, which is why
    the total work stays linear.

    Time: O(n).  Space: O(n).

    Example:
        >>> z_function("aaaaa")
        [0, 4, 3, 2, 1]
        >>> z_function("ababab")
        [0, 0, 4, 0, 2, 0]
    """
    n = len(seq)
    z = [0] * n
    left = right = 0  # current Z-box [left, right]: seq[left..right] matches
    #                    the prefix seq[0..right-left] (inclusive on both ends)

    for i in range(1, n):
        if i <= right:
            # i is inside the box: mirror it across `left`. The value cannot
            # exceed the distance to the box edge (right - i + 1).
            z[i] = min(right - i + 1, z[i - left])
        # Extend by brute force: compare past the already-known match.
        while i + z[i] < n and seq[z[i]] == seq[i + z[i]]:
            z[i] += 1
        # Adopt the box if this match reaches further right than before.
        if i + z[i] - 1 > right:
            left, right = i, i + z[i] - 1
    return z


def z_search(text: Sequence[T], pattern: Sequence[T]) -> List[int]:
    """
    Return the start indices of every occurrence of pattern in text, using
    the Z-algorithm on the concatenation pattern + separator + text.

    Why this works: compute the Z-array of the combined sequence. For any
    position i inside the text part, z[i] is how long the text matches the
    pattern *from the start of the combined sequence* - which is exactly how
    long the text at i matches the pattern. The separator guarantees no match
    can run past the pattern's end (it never equals a real element), so
    z[i] == len(pattern) means precisely "the pattern starts at i".

    The separator is a sentinel object that equals nothing but itself - the
    object analogue of the '#' separator used in textbook Z-search. One code
    path covers str and non-str inputs, and text is never re-read more than
    once overall, matching KMP's linear guarantee.

    Time: O(n + m).  Space: O(n + m).

    Example:
        >>> z_search("doe are hearing me", "ear")
        [9]
        >>> z_search("ababab", "aba")       # overlapping matches
        [0, 2]
    """
    if not pattern:
        raise ValueError("pattern must not be empty")
    n, m = len(text), len(pattern)
    if n < m:
        return []

    # The sentinel appears exactly once, so it can never equal a real element
    # and no Z-match can cross from the text into the pattern.
    separator = object()
    combined: List[Any] = list(pattern) + [separator] + list(text)

    z = z_function(combined)
    matches: List[int] = []
    # The text part starts at index m + 1 of the combined sequence.
    for i in range(m + 1, m + 1 + n):
        if z[i] == m:
            matches.append(i - m - 1)
    return matches


# ---------------------------------------------------------------------------
# Manacher: longest palindromic substring in linear time
# ---------------------------------------------------------------------------


def manacher(seq: Sequence[T]) -> Tuple[int, int]:
    """
    Return the (start, end) half-open bounds of one longest palindromic
    contiguous substring of seq; seq[start:end] is a palindrome of maximal
    length. Returns (0, 0) for an empty input.

    The naive approach expands around each of the 2n - 1 possible centers in
    O(n) worst case, giving O(n^2). Manacher's insight is that palindromes
    nest: when a big palindrome spans a center i, the palindrome at i mirrors
    the palindrome at i's mirror point inside the big one - so most of the
    work can be copied instead of recomputed.

    To treat even and odd palindromes uniformly, the sequence is expanded
    with barriers between elements: every palindrome of the original maps to
    an odd-length palindrome centered on a single position of the expanded
    array, and its *radius* equals the original palindrome's length. The
    algorithm keeps the rightmost-reaching palindrome as a "mirror box" and
    initializes each new radius from its mirror (capped at the box edge)
    before extending by brute force - and since the box edge only moves
    right, the total extension work is linear.

    Time: O(n).  Space: O(n).

    Example:
        >>> text = "babad"
        >>> start, end = manacher(text)
        >>> (start, end, text[start:end])
        (0, 3, 'bab')
        >>> manacher("cbbd")
        (1, 3)
    """
    n = len(seq)
    if n == 0:
        return (0, 0)

    # A single sentinel object spliced between every pair of elements (and at
    # both ends): it equals only itself, so sentinel-vs-element comparisons
    # always fail while sentinel-vs-sentinel always succeeds. That makes every
    # palindrome of the original - even or odd length - an odd-length
    # palindrome of `expanded`, centered on an element or a sentinel.
    barrier = object()
    # expanded: barrier, seq[0], barrier, seq[1], ..., barrier (2n + 1 slots)
    expanded: List[Any] = [barrier]
    for element in seq:
        expanded.append(element)
        expanded.append(barrier)

    radii = [0] * len(expanded)  # radii[i] = palindrome radius around i
    center = right = 0  # rightmost-reaching palindrome so far (right exclusive)
    best_radius = 0
    best_center = 0

    for i in range(1, len(expanded)):
        mirror = 2 * center - i
        if i < right:
            # i sits inside the best palindrome: mirror it across `center`,
            # capped so the copy cannot leave the box.
            radii[i] = min(right - i, radii[mirror])
        # Extend by brute force while both sides still match.
        while (
            i - radii[i] - 1 >= 0
            and i + radii[i] + 1 < len(expanded)
            and expanded[i - radii[i] - 1] == expanded[i + radii[i] + 1]
        ):
            radii[i] += 1
        if i + radii[i] > right:
            center, right = i, i + radii[i]  # adopt the new rightmost box
        if radii[i] > best_radius:
            best_radius, best_center = radii[i], i

    # Map the expanded-array palindrome back to original coordinates. The
    # palindrome's real length equals best_radius; start = (center - radius)/2
    # works because center and radius share parity.
    start = (best_center - best_radius) // 2
    return (start, start + best_radius)


# ---------------------------------------------------------------------------
# Hamming distance
# ---------------------------------------------------------------------------


def hamming_distance(a: Sequence[T], b: Sequence[T]) -> int:
    """
    Return the Hamming distance between a and b: the number of positions at
    which they differ. Raises ValueError when the sequences have different
    lengths (the distance is only defined for equal-length sequences).

    This is the simplest string metric - it assumes *alignment is free*,
    which is why it suits fixed-length data (codewords, DNA barcodes of the
    same length, binary fingerprints) but not free-form prose, where edit
    distance (see algorithmlib.dp.edit_distance) is the right tool. The
    elements only need to support equality, so ints, tuples and any sequence
    of comparable values work (hashability is not required).

    Time: O(n).  Space: O(1).

    Example:
        >>> hamming_distance("karolin", "kathrin")
        3
        >>> hamming_distance((1, 0, 1), (1, 1, 1))
        1
    """
    if len(a) != len(b):
        raise ValueError("sequences must have the same length")
    return sum(x != y for x, y in zip(a, b))
