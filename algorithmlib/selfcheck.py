"""
algorithmlib.selfcheck - property tests for every algorithm in the package.

Run from the repository root:

    python3 -m algorithmlib.selfcheck

Each test compares an implementation against a trivial reference (built-in
sorted, naive pattern matching, brute-force shortest paths, exhaustive
search over small inputs) on hand-picked edge cases AND on seeded random
inputs, so the same test covers empty input, singletons, duplicates,
already-sorted data and adversarial shapes.

Exit code is 0 only if every assertion passed.
"""

import itertools
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from algorithmlib.dp import (
    coin_change_min,
    edit_distance,
    fibonacci,
    knapsack_01,
    longest_common_subsequence,
    longest_common_substring,
    longest_increasing_subsequence,
    max_subarray_sum,
    subset_sum,
)
from algorithmlib.graphs import (
    bellman_ford,
    dijkstra,
    edmonds_karp,
    floyd_warshall,
    is_bipartite,
    kruskal_mst,
    prim_mst,
    strongly_connected_components,
    topological_sort,
)
from algorithmlib.greedy import activity_selection, fractional_knapsack, huffman_codes
from algorithmlib.numbers import (
    extended_gcd,
    gcd,
    hamming_weight,
    integer_sqrt,
    is_prime,
    lcm,
    modular_inverse,
    modular_pow,
    sieve_of_eratosthenes,
)
from algorithmlib.randomized import fisher_yates, reservoir_sample
from algorithmlib.searching import binary_search, exponential_search, lower_bound, upper_bound
from algorithmlib.sorting import (
    heapsort,
    insertion_sort,
    merge_sort,
    quickselect,
    quicksort,
    timsort,
)
from algorithmlib.strings import (
    boyer_moore_horspool,
    hamming_distance,
    kmp_search,
    manacher,
    prefix_function,
    rabin_karp,
    z_function,
    z_search,
)

ALL_SORTERS = [insertion_sort, merge_sort, quicksort, heapsort, timsort]


# ---------------------------------------------------------------------------
# sorting
# ---------------------------------------------------------------------------


class Tagged:
    """Element whose ordering ignores a payload - used to test stability."""

    __slots__ = ("key", "tag")

    def __init__(self, key: int, tag: int):
        self.key, self.tag = key, tag

    def __lt__(self, other: "Tagged") -> bool:
        return self.key < other.key

    def __repr__(self) -> str:
        return f"Tagged({self.key}, {self.tag})"


def is_sorted(values) -> bool:
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def test_sorter(sorter, values: List[int]) -> None:
    work = values[:]
    result = sorter(work)
    assert result is work, f"{sorter.__name__} must return the list it sorted"
    assert result == sorted(values), f"{sorter.__name__} wrong on {values}"


def test_sorting() -> None:
    rng = random.Random(20260909)

    shapes: List[List[int]] = [
        [],
        [7],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [1, 1, 1, 1],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [0] * 5,
        [1, 2, 2, 1, 2, 1],
    ]
    for shape in shapes:
        for sorter in ALL_SORTERS:
            test_sorter(sorter, shape)

    for _ in range(300):
        size = rng.randrange(0, 40)
        values = [rng.randrange(0, 6) for _ in range(size)]
        for sorter in ALL_SORTERS:
            test_sorter(sorter, values)
        floats = [rng.random() for _ in range(size)]
        for sorter in ALL_SORTERS:
            test_sorter(sorter, floats)

    words = ["pear", "apple", "fig", "date", "apple"]
    for sorter in ALL_SORTERS:
        assert sorter(words[:]) == sorted(words)

    # Stability for the stable sorts only.
    for sorter in (insertion_sort, merge_sort, timsort):
        items = [Tagged(key, tag) for tag, key in enumerate([1, 0, 1, 0, 2, 1])]
        sorter(items)
        assert is_sorted([t.key for t in items])
        seen: dict = {}
        for item in items:
            group = seen.setdefault(item.key, -1)
            assert item.tag > group, f"{sorter.__name__} was not stable: {items}"
            seen[item.key] = item.tag


def test_quickselect() -> None:
    rng = random.Random(7)
    for _ in range(200):
        values = [rng.randrange(0, 20) for _ in range(rng.randrange(1, 30))]
        reference = sorted(values)
        for k in range(len(values)):
            got = quickselect(values[:], k)
            assert got == reference[k], f"quickselect k={k} wrong on {values}"
    assert quickselect([9, 1, 8, 2, 7], 0) == 1
    assert quickselect([9, 1, 8, 2, 7], 4) == 9
    try:
        quickselect([1, 2], 5)
        raise AssertionError("quickselect must reject an out-of-range k")
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# searching
# ---------------------------------------------------------------------------


def test_searching() -> None:
    rng = random.Random(11)
    for _ in range(300):
        size = rng.randrange(0, 50)
        values = sorted(rng.randrange(0, 10) for _ in range(size))
        probe = rng.randrange(-2, 12)

        expected_lo = next(
            (i for i, v in enumerate(values) if v >= probe), len(values)
        )
        assert lower_bound(values, probe) == expected_lo
        expected_hi = next(
            (i for i, v in enumerate(values) if v > probe), len(values)
        )
        assert upper_bound(values, probe) == expected_hi

        # binary_search and exponential_search must both agree with Python,
        # and both return the FIRST occurrence under duplicates.
        for fn in (binary_search, exponential_search):
            got = fn(values, probe)
            if probe in values:
                assert got is not None and values[got] == probe
                assert got == expected_lo
            else:
                assert got is None

    assert binary_search((1, 3, 5, 7), 5) == 2
    assert binary_search("aceg", "g") == 3
    assert lower_bound(range(10), 5) == 5
    assert upper_bound([], 1) == 0
    assert exponential_search([], 1) is None
    assert exponential_search([5], 5) == 0
    assert exponential_search([5], 3) is None


# ---------------------------------------------------------------------------
# strings
# ---------------------------------------------------------------------------


def naive_matches(text, pattern):
    return [
        i
        for i in range(len(text) - len(pattern) + 1)
        if text[i : i + len(pattern)] == pattern
    ]


MATCHERS = [rabin_karp, kmp_search, boyer_moore_horspool, z_search]


def brute_z(seq) -> List[int]:
    """Reference Z-array by definition: LCP of seq with seq[i:]."""
    n = len(seq)
    z = [0] * n
    for i in range(1, n):
        k = 0
        while i + k < n and seq[k] == seq[i + k]:
            k += 1
        z[i] = k
    return z


def test_strings() -> None:
    rng = random.Random(13)

    fixed_cases = [
        ("doe are hearing me", "ear", [9]),
        ("aaaa", "aa", [0, 1, 2]),
        ("abc", "z", []),
        ("abc", "abc", [0]),
        ("abc", "bc", [1]),
        ("abababa", "aba", [0, 2, 4]),
        ("caf\u00e9 au lait", "au", [5]),
    ]
    for text, pattern, expected in fixed_cases:
        for matcher in MATCHERS:
            assert matcher(text, pattern) == expected, (
                f"{matcher.__name__}({text!r}, {pattern!r})"
            )

    for _ in range(400):
        text = "".join(rng.choice("aab") for _ in range(rng.randrange(0, 25)))
        pattern = "".join(rng.choice("aab") for _ in range(rng.randrange(1, 6)))
        expected = naive_matches(text, pattern)
        for matcher in MATCHERS:
            assert matcher(text, pattern) == expected, (
                f"{matcher.__name__} mismatch on {text!r} vs {pattern!r}"
            )

    # Z-function against the by-definition reference.
    for _ in range(200):
        seq = "".join(rng.choice("ab") for _ in range(rng.randrange(1, 30)))
        assert z_function(seq) == brute_z(seq), f"z_function wrong on {seq!r}"
    assert z_function("aaaaa") == [0, 4, 3, 2, 1]
    assert z_function("aabcaabxaaaz") == [0, 1, 0, 0, 3, 1, 0, 0, 2, 2, 1, 0]

    # Genericity: the matchers work on tuples of ints too.
    token_text = (3, 1, 4, 1, 5, 9, 1, 4)
    token_pattern = (1, 4)
    expected_tokens = [1, 6]
    assert naive_matches(token_text, token_pattern) == expected_tokens
    for matcher in MATCHERS:
        assert matcher(token_text, token_pattern) == expected_tokens
    assert prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]

    # Manacher: bounds must be a palindrome of maximal length.
    def brute_longest_palindrome(s):
        best = 0
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                chunk = s[i:j]
                if chunk == chunk[::-1]:
                    best = max(best, j - i)
        return best

    assert manacher("") == (0, 0)
    for text, expected in [("babad", 3), ("cbbd", 2), ("a", 1), ("aa", 2)]:
        lo, hi = manacher(text)
        assert hi - lo == expected, f"manacher on {text!r}"
        chunk = text[lo:hi]
        assert chunk == chunk[::-1]
    for _ in range(150):
        text = "".join(rng.choice("abc") for _ in range(rng.randrange(1, 16)))
        lo, hi = manacher(text)
        chunk = text[lo:hi]
        assert chunk == chunk[::-1], f"manacher non-palindrome on {text!r}"
        assert hi - lo == brute_longest_palindrome(text), (
            f"manacher not longest on {text!r}"
        )

    # Hamming distance: fixed cases + random cross-check.
    assert hamming_distance("karolin", "kathrin") == 3
    assert hamming_distance((1, 0, 1), (1, 1, 1)) == 1
    assert hamming_distance("abc", "abc") == 0
    try:
        hamming_distance("abc", "ab")
        raise AssertionError("hamming_distance accepted unequal lengths")
    except ValueError:
        pass
    for _ in range(100):
        n = rng.randrange(0, 12)
        a = [rng.randrange(2) for _ in range(n)]
        b = [rng.randrange(2) for _ in range(n)]
        assert hamming_distance(a, b) == sum(x != y for x, y in zip(a, b))

    for matcher in MATCHERS:
        try:
            matcher("anything", "")
            raise AssertionError(f"{matcher.__name__} accepted an empty pattern")
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------


def trial_prime(n: int) -> bool:
    """Reference primality by trial division (small n only)."""
    if n < 2:
        return False
    for d in range(2, int(math.isqrt(n)) + 1):
        if n % d == 0:
            return False
    return True


def test_numbers() -> None:
    rng = random.Random(23)

    # gcd / lcm against math.gcd / the definition.
    for _ in range(300):
        a, b = rng.randrange(-10**6, 10**6), rng.randrange(-10**6, 10**6)
        assert gcd(a, b) == math.gcd(a, b)
        if a and b:
            assert lcm(a, b) == abs(a * b) // math.gcd(a, b)
    assert gcd(0, 0) == 0
    assert lcm(0, 5) == 0
    assert gcd(48, 18) == 6
    assert lcm(4, 6) == 12

    # extended_gcd: Bezout identity a*x + b*y == g == gcd(a, b).
    for _ in range(300):
        a, b = rng.randrange(-1000, 1000), rng.randrange(-1000, 1000)
        g, x, y = extended_gcd(a, b)
        assert g == math.gcd(a, b)
        assert a * x + b * y == g

    # modular_inverse: definition + refusal when not coprime.
    for _ in range(200):
        m = rng.randrange(2, 10**6)
        a = rng.randrange(1, m)
        if math.gcd(a, m) == 1:
            inv = modular_inverse(a, m)
            assert 0 <= inv < m and (a * inv) % m == 1
        else:
            try:
                modular_inverse(a, m)
                raise AssertionError(f"inverse of non-coprime {a} mod {m}")
            except ValueError:
                pass
    assert modular_inverse(3, 11) == 4
    for bad_m in (1, 0, -5):
        try:
            modular_inverse(5, bad_m)
            raise AssertionError(f"modular_inverse accepted modulus {bad_m}")
        except ValueError:
            pass

    # modular_pow against pow(..., mod).
    for _ in range(200):
        base = rng.randrange(0, 10**6)
        exp = rng.randrange(0, 10**5)
        mod = rng.randrange(1, 10**6)
        assert modular_pow(base, exp, mod) == pow(base, exp, mod)
    assert modular_pow(4, 13, 497) == 445

    # Sieve against trial division, plus is_prime cross-checks.
    for limit in [0, 1, 2, 3, 10, 30, 100, 500, 2000]:
        primes = sieve_of_eratosthenes(limit)
        assert primes == [n for n in range(limit + 1) if trial_prime(n)]
    for n in range(2, 3000):
        assert is_prime(n) == trial_prime(n), f"is_prime({n})"
    # Carmichael / strong pseudoprime numbers must all be rejected.
    for n in [341, 561, 1105, 1729, 2465, 2821, 6601, 8911]:
        assert not is_prime(n), f"{n} is not prime"
    for _ in range(200):
        n = rng.randrange(2, 10**6)
        assert is_prime(n) == trial_prime(n), f"is_prime({n})"
    # Large known primes / composites (deterministic base set).
    assert is_prime(2**31 - 1)  # Mersenne prime
    assert is_prime(2305843009213693951)  # 2**61 - 1, Mersenne prime
    assert not is_prime(147573952589676412927)  # 2**67 - 1, composite
    # Smallest strong pseudoprime to the first twelve primes: caught once
    # base 41 joins the set (the bound would otherwise be ~3.2e23, not 3.3e24).
    assert not is_prime(318665857834031151167461)

    # integer_sqrt against math.isqrt.
    for _ in range(300):
        n = rng.randrange(0, 10**12)
        assert integer_sqrt(n) == math.isqrt(n)
    assert integer_sqrt(50) == 7
    assert integer_sqrt(0) == 0

    # hamming_weight against bin().count().
    for _ in range(200):
        n = rng.randrange(0, 10**12)
        assert hamming_weight(n) == bin(n).count("1")
    assert hamming_weight(0b1101) == 3


# ---------------------------------------------------------------------------
# dp
# ---------------------------------------------------------------------------


def brute_max_subarray(nums) -> float:
    best = nums[0]
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            best = max(best, s)
    return best


def brute_lcs_len(a, b) -> int:
    def subsequences(s):
        out = set()
        for r in range(len(s) + 1):
            for combo in itertools.combinations(range(len(s)), r):
                out.add("".join(s[i] for i in combo))
        return out

    return max(len(x) for x in subsequences(a) & subsequences(b))


def test_dp() -> None:
    rng = random.Random(29)

    # Fibonacci.
    assert fibonacci(0) == 0 and fibonacci(1) == 1 and fibonacci(10) == 55
    f = [fibonacci(i) for i in range(20)]
    for i in range(2, 20):
        assert f[i] == f[i - 1] + f[i - 2]
    assert fibonacci(90) == 2880067194370816120  # fits Python ints fine

    # Kadane against brute force on every slice of random arrays.
    for _ in range(120):
        nums = [rng.randrange(-10, 10) for _ in range(rng.randrange(1, 12))]
        assert max_subarray_sum(nums) == brute_max_subarray(nums)
    assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_subarray_sum([-3, -1, -2]) == -1

    # 0/1 knapsack against exhaustive subsets.
    def brute_knapsack(weights, values, capacity):
        best = 0
        n = len(weights)
        for mask in range(1 << n):
            w = v = 0
            for i in range(n):
                if mask >> i & 1:
                    w += weights[i]
                    v += values[i]
            if w <= capacity:
                best = max(best, v)
        return best

    for _ in range(120):
        n = rng.randrange(1, 9)
        weights = [rng.randrange(1, 12) for _ in range(n)]
        values = [rng.randrange(1, 20) for _ in range(n)]
        cap = rng.randrange(0, 25)
        got = knapsack_01(weights, values, cap)
        assert got == brute_knapsack(weights, values, cap), (
            f"knapsack_01 wrong: {weights} {values} cap {cap}"
        )
    assert knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9

    # Subset sum against exhaustive reachability.
    for _ in range(120):
        nums = [rng.randrange(1, 15) for _ in range(rng.randrange(0, 9))]
        target = rng.randrange(0, 40)
        reachable = {
            sum(combo)
            for r in range(len(nums) + 1)
            for combo in itertools.combinations(nums, r)
        }
        assert subset_sum(nums, target) == (target in reachable)
    assert subset_sum([3, 34, 4, 12, 5, 2], 9)
    assert not subset_sum([3, 34, 4, 12, 5, 2], 30)
    assert subset_sum([], 0)

    # Input validation: bad data must raise, never crash or mislead.
    for bad_call in (
        lambda: knapsack_01([-2], [1], 5),          # negative weight
        lambda: knapsack_01([1, 2], [1], 5),        # length mismatch
        lambda: knapsack_01([1], [1], -1),          # negative capacity
        lambda: subset_sum([-2], 6),                # negative number
        lambda: coin_change_min([-1, 2], 5),        # non-positive coin
        lambda: coin_change_min([1, 2], -3),        # negative amount
        lambda: max_subarray_sum([]),               # empty input
    ):
        try:
            bad_call()
            raise AssertionError("invalid input accepted")
        except ValueError:
            pass

    # Coin change against a memoized recursive reference.
    def ref_coin(coins, amount):
        memo = {}

        def rec(rest):
            if rest == 0:
                return 0
            if rest < 0:
                return float("inf")
            if rest in memo:
                return memo[rest]
            memo[rest] = 1 + min((rec(rest - c) for c in coins), default=float("inf") - 1)
            return memo[rest]

        ans = rec(amount)
        return -1 if ans == float("inf") else ans

    for _ in range(120):
        coins = [rng.randrange(1, 10) for _ in range(rng.randrange(1, 4))]
        amount = rng.randrange(0, 40)
        assert coin_change_min(coins, amount) == ref_coin(coins, amount)
    assert coin_change_min([1, 2, 5], 11) == 3
    assert coin_change_min([2], 3) == -1

    # LCS length against brute force over all subsequences.
    def is_subseq(needle, haystack):
        it = iter(haystack)
        return all(x in it for x in needle)

    for _ in range(80):
        a = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 8)))
        b = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 8)))
        got = longest_common_subsequence(a, b)
        assert len(got) == brute_lcs_len(a, b)
        assert is_subseq(got, a) and is_subseq(got, b)
    assert longest_common_subsequence("ABCBDAB", "BDCABA") == list("BCBA")
    assert longest_common_subsequence("abc", "def") == []
    # The result is always a list, whatever containers came in.
    out = longest_common_subsequence((1, 2, 3, 4), (2, 4, 6))
    assert isinstance(out, list) and out == [2, 4]
    assert longest_common_subsequence((2, 4, 6), (1, 2, 3, 4)) == [2, 4]

    # Longest common substring against brute force over all substrings.
    def brute_lcsubstring(a, b):
        best = 0
        for i in range(len(a)):
            for j in range(i + 1, len(a) + 1):
                if a[i:j] in b:
                    best = max(best, j - i)
        return best

    for _ in range(100):
        a = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 9)))
        b = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 9)))
        got = longest_common_substring(a, b)
        assert len(got) == brute_lcsubstring(a, b), (a, b, got)
        joined = "".join(got)
        assert joined in a and joined in b
    assert longest_common_substring("abcde", "zbcdf") == list("bcd")
    assert longest_common_substring("abc", "def") == []
    # Shorter first argument exercises the swap path; result is still a list.
    assert longest_common_substring("bcd", "abcdbef") == list("bcd")
    assert longest_common_substring((1, 2, 3), (0, 1, 2, 3, 4)) == [1, 2, 3]

    # Edit distance against a memoized recursive reference.
    def ref_edit(a, b):
        memo = {}

        def rec(i, j):
            if i == 0:
                return j
            if j == 0:
                return i
            key = (i, j)
            if key not in memo:
                cost = 0 if a[i - 1] == b[j - 1] else 1
                memo[key] = min(
                    rec(i - 1, j) + 1,
                    rec(i, j - 1) + 1,
                    rec(i - 1, j - 1) + cost,
                )
            return memo[key]

        return rec(len(a), len(b))

    for _ in range(100):
        a = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 8)))
        b = "".join(rng.choice("abc") for _ in range(rng.randrange(0, 8)))
        assert edit_distance(a, b) == ref_edit(a, b), (a, b)
    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("", "abc") == 3
    assert edit_distance("flaw", "lawn") == 2

    # LIS length against O(n^2) reference.
    def ref_lis(nums):
        if not nums:
            return 0
        dp = [1] * len(nums)
        for i in range(len(nums)):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    for _ in range(150):
        nums = [rng.randrange(0, 12) for _ in range(rng.randrange(0, 15))]
        assert longest_increasing_subsequence(nums) == ref_lis(nums), nums
    assert longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert longest_increasing_subsequence([7, 7, 7]) == 1
    assert longest_increasing_subsequence([]) == 0


# ---------------------------------------------------------------------------
# greedy
# ---------------------------------------------------------------------------


def test_greedy() -> None:
    rng = random.Random(31)

    # Activity selection against brute force over subsets.
    def brute_activities(intervals):
        best = 0
        n = len(intervals)
        for mask in range(1 << n):
            chosen = [intervals[i] for i in range(n) if mask >> i & 1]
            chosen.sort()
            ok = all(
                chosen[i][1] <= chosen[i + 1][0]
                for i in range(len(chosen) - 1)
            )
            if ok:
                best = max(best, len(chosen))
        return best

    for _ in range(100):
        intervals = []
        for _ in range(rng.randrange(0, 8)):
            s = rng.randrange(0, 10)
            e = s + rng.randrange(1, 6)
            intervals.append((s, e))
        assert activity_selection(intervals) == brute_activities(intervals)
    assert activity_selection([]) == 0
    assert activity_selection([(1, 2)]) == 1
    # Textbook 11-interval example has answer 4.
    textbook = [
        (1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
        (6, 10), (8, 11), (8, 12), (2, 14), (12, 16),
    ]
    assert activity_selection(textbook) == 4

    # Fractional knapsack: greedy value must be >= every integral packing and
    # <= taking everything; for tiny cases, cross-check with brute over all
    # fractions via linear programming is overkill - instead verify against
    # the closed-form: sort by density and take greedily.
    def reference_fractional(items, capacity):
        items = sorted(items, key=lambda it: it[1] / it[0], reverse=True)
        total = 0.0
        for w, v in items:
            take = min(w, capacity)
            total += take * (v / w)
            capacity -= take
        return total

    for _ in range(100):
        items = [
            (rng.randrange(1, 10), rng.randrange(1, 30))
            for _ in range(rng.randrange(0, 8))
        ]
        cap = rng.randrange(0, 30)
        assert abs(fractional_knapsack(items, cap) - reference_fractional(items, cap)) < 1e-9
    assert fractional_knapsack([(10, 60), (20, 100), (30, 120)], 50) == 240.0
    for bad_call in (
        lambda: fractional_knapsack([(0, 5)], 10),   # zero weight
        lambda: fractional_knapsack([(-2, 5)], 10),  # negative weight
        lambda: fractional_knapsack([(2, 5)], -3),   # negative capacity
    ):
        try:
            bad_call()
            raise AssertionError("fractional_knapsack accepted bad input")
        except ValueError:
            pass

    # Huffman codes: prefix-free, complete coverage, and minimal cost against
    # an independent implementation of the same merge rule.
    def reference_cost(freqs):
        import heapq

        values = list(freqs.values())
        if len(values) == 1:
            return values[0]  # a single symbol pays one bit (code "0")
        heap = list(freqs.values())
        heapq.heapify(heap)
        total = 0
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            total += a + b
            heapq.heappush(heap, a + b)
        return total

    def cost_of(codes, freqs):
        return sum(len(code) * freqs[sym] for sym, code in codes.items())

    for _ in range(150):
        symbols = rng.sample(range(20), rng.randrange(1, 8))
        freqs = {sym: rng.randrange(1, 50) for sym in symbols}
        codes = huffman_codes(freqs)
        assert set(codes) == set(freqs)  # every symbol got a code
        code_list = sorted(codes.values(), key=len, reverse=True)
        # Prefix-free: no code is a prefix of another.
        for i in range(len(code_list)):
            for j in range(len(code_list)):
                if i != j and code_list[j].startswith(code_list[i]):
                    raise AssertionError(f"prefix collision: {codes}")
        assert cost_of(codes, freqs) == reference_cost(freqs), freqs
    codes = huffman_codes({"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5})
    assert cost_of(codes, {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}) == 224
    assert huffman_codes({"only": 7}) == {"only": "0"}
    assert huffman_codes({}) == {}

    # Skewed trees: Fibonacci-like frequencies produce very deep Huffman
    # trees; the (iterative) walk must handle thousands of symbols.
    fib = {}
    a, b = 1, 1
    for i in range(3000):
        fib[i] = a
        a, b = b, a + b
    deep_codes = huffman_codes(fib)
    assert set(deep_codes) == set(fib)
    assert cost_of(deep_codes, fib) == reference_cost(fib)


# ---------------------------------------------------------------------------
# randomized
# ---------------------------------------------------------------------------


def test_randomized() -> None:
    rng = random.Random(37)

    # Fisher-Yates: identity, multiset preservation, reproducibility.
    for _ in range(100):
        data = [rng.randrange(10) for _ in range(20)]
        expected = sorted(data)
        out = fisher_yates(data[:], rng)
        assert sorted(out) == expected
    original = list(range(100))
    a = fisher_yates(original[:], random.Random(1))
    b = fisher_yates(original[:], random.Random(1))
    assert a == b and a != original  # same seed, same shuffle, really shuffled
    single = [42]
    assert fisher_yates(single, rng) == [42]

    # Reservoir sampling: size, subset property, all-items-when-k-large.
    for _ in range(100):
        stream = list(range(rng.randrange(0, 60)))
        k = rng.randrange(0, 12)
        sample = reservoir_sample(stream, k, rng)
        assert len(sample) == min(k, len(stream))
        assert set(sample) <= set(stream)
    assert reservoir_sample([1, 2, 3], 10, rng) == [1, 2, 3]
    assert reservoir_sample([1, 2, 3], 0, rng) == []
    # Uniformity smoke test: each element should appear roughly k/n of the
    # time over many runs (loose bounds to avoid flakiness).
    counts = {i: 0 for i in range(10)}
    trials = 4000
    for _ in range(trials):
        for x in reservoir_sample(range(10), 3, rng):
            counts[x] += 1
    for i in range(10):
        assert 0.2 < counts[i] / trials < 0.45, counts  # expect ~0.3


# ---------------------------------------------------------------------------
# graphs
# ---------------------------------------------------------------------------


def random_graph(rng: random.Random, node_count: int, negative: bool):
    """Small weighted digraph as an adjacency mapping over int labels."""
    graph = {u: [] for u in range(node_count)}
    for u in range(node_count):
        for v in range(node_count):
            if u != v and rng.random() < 0.25:
                weight = rng.randrange(-3 if negative else 0, 6)
                if weight != 0:
                    graph[u].append((v, weight))
    return graph


def to_matrix(graph, nodes):
    index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)
    matrix = [[float("inf")] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 0
    for u, edges in graph.items():
        for v, w in edges:
            matrix[index[u]][index[v]] = min(matrix[index[u]][index[v]], w)
    return matrix


def test_graphs() -> None:
    example = {"A": [("B", 4)], "B": [("C", -2)]}
    assert bellman_ford(example, "A") == {"A": 0, "B": 4, "C": 2}
    assert dijkstra({"A": [("B", 4), ("C", 2)], "B": [("C", 1)]}, "A") == {
        "A": 0,
        "B": 4,
        "C": 2,
    }
    m = floyd_warshall(
        [[0, 3, float("inf")], [float("inf"), 0, 1], [float("inf"), float("inf"), 0]]
    )
    assert m[0][2] == 4 and m[1][2] == 1 and m[0][1] == 3

    rng = random.Random(17)
    for _ in range(150):
        graph = random_graph(rng, rng.randrange(1, 8), negative=False)
        nodes = sorted(graph)
        source = rng.choice(nodes)
        source_idx = nodes.index(source)
        bf = bellman_ford(graph, source)
        dj = dijkstra(graph, source)
        fw = floyd_warshall(to_matrix(graph, nodes))
        assert bf == dj, f"bellman_ford and dijkstra disagree on {graph}"
        for i, u in enumerate(nodes):
            assert bf[u] == fw[source_idx][i], (
                f"single-source vs all-pairs disagree on {graph}"
            )
        assert bf[source] == 0

    for _ in range(300):
        graph = random_graph(rng, rng.randrange(1, 7), negative=True)
        nodes = sorted(graph)
        source = rng.choice(nodes)
        source_idx = nodes.index(source)
        try:
            bf = bellman_ford(graph, source)
        except ValueError:
            continue
        try:
            fw = floyd_warshall(to_matrix(graph, nodes))
        except ValueError:
            continue
        for i, u in enumerate(nodes):
            if bf[u] != float("inf"):
                assert bf[u] == fw[source_idx][i]
        try:
            dj = dijkstra(graph, source)
            assert dj == bf
        except ValueError:
            pass

    neg_cycle = {0: [(1, 5)], 1: [(2, -3)], 2: [(1, -3)]}
    for fn in (
        lambda: bellman_ford(neg_cycle, 0),
        lambda: floyd_warshall(to_matrix(neg_cycle, [0, 1, 2])),
    ):
        try:
            fn()
            raise AssertionError("negative cycle not detected")
        except ValueError:
            pass

    tail_only = {"s": [("mid", 2)], "mid": [("t", 3)]}
    assert bellman_ford(tail_only, "s") == {"s": 0, "mid": 2, "t": 5}
    assert dijkstra(tail_only, "s") == {"s": 0, "mid": 2, "t": 5}

    dag = {"a": ["b", "c"], "b": ["d"], "c": ["d"]}
    order = topological_sort(dag)
    position = {node: i for i, node in enumerate(order)}
    for u, neighbours in dag.items():
        for v in neighbours:
            assert position[u] < position[v], f"bad order {order}"
    cyclic = {"a": ["b"], "b": ["c"], "c": ["a"]}
    try:
        topological_sort(cyclic)
        raise AssertionError("topological_sort accepted a cyclic graph")
    except ValueError:
        pass
    dag2 = {"boot": ["wheel"], "frame": ["wheel"]}
    order2 = topological_sort(dag2)
    assert order2.index("boot") < order2.index("wheel")
    assert order2.index("frame") < order2.index("wheel")

    # ---- MST: prim and kruskal must agree, produce a spanning tree ----
    def connected_undirected(rng, n):
        """Random connected undirected weighted graph (both directions)."""
        graph = {i: [] for i in range(n)}
        # Random spanning tree first (guarantees connectivity).
        for v in range(1, n):
            u = rng.randrange(v)
            w = rng.randrange(1, 21)
            graph[u].append((v, w))
            graph[v].append((u, w))
        # Extra random edges.
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.3:
                    w = rng.randrange(1, 21)
                    graph[u].append((v, w))
                    graph[v].append((u, w))
        return graph

    def total(edges):
        return sum(w for _u, _v, w in edges)

    def spans_all(edges, node_count):
        parent = list(range(node_count))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v, _w in edges:
            a, b = find(u), find(v)
            if a == b:
                return False  # cycle: not a tree
            parent[a] = b
        roots = {find(i) for i in range(node_count)}
        return len(roots) == 1 and len(edges) == node_count - 1

    for _ in range(100):
        n = rng.randrange(1, 8)
        graph = connected_undirected(rng, n)
        k = kruskal_mst(graph)
        p = prim_mst(graph)
        assert total(k) == total(p), f"MST totals differ on {graph}"
        if n > 0:
            assert spans_all(k, n) and spans_all(p, n)
    # Disconnected graphs must raise.
    disc = {0: [(1, 2)], 1: [(0, 2)], 2: []}
    for fn in (kruskal_mst, prim_mst):
        try:
            fn(disc)
            raise AssertionError(f"{fn.__name__} accepted a disconnected graph")
        except ValueError:
            pass
    assert kruskal_mst({0: []}) == []
    assert prim_mst({0: []}) == []

    # ---- Bipartite: coloring must be valid; odd cycles must be refused ----
    def brute_bipartite(adj_undirected, node_count):
        for mask in range(1 << node_count):
            colors = [(mask >> i) & 1 for i in range(node_count)]
            good = True
            for u in range(node_count):
                for v in adj_undirected[u]:
                    if colors[u] == colors[v]:
                        good = False
            if good:
                return True
        return False

    for _ in range(120):
        n = rng.randrange(1, 8)
        adj = {i: [] for i in range(n)}
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.3:
                    adj[u].append(v)
                    adj[v].append(u)
        coloring = is_bipartite(adj)
        expected = brute_bipartite(adj, n)
        if coloring is None:
            assert not expected, f"missed bipartition on {adj}"
        else:
            assert expected, f"claimed bipartition on {adj}"
            for u in range(n):
                for v in adj[u]:
                    assert coloring[u] != coloring[v]
    triangle = {0: [1], 1: [0, 2], 2: [1, 0]}
    assert is_bipartite(triangle) is None
    assert is_bipartite({0: [1], 1: [0, 2], 2: [1]}) == {0: 0, 1: 1, 2: 0}

    # ---- SCC: equality iff mutual reachability (brute-force reach) ----
    def brute_reach(adj, n):
        reach = [[False] * n for _ in range(n)]
        for s in range(n):
            stack = [s]
            reach[s][s] = True
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if not reach[s][v]:
                        reach[s][v] = True
                        stack.append(v)
        return reach

    for _ in range(120):
        n = rng.randrange(1, 7)
        adj = {i: [] for i in range(n)}
        for u in range(n):
            for v in range(n):
                if u != v and rng.random() < 0.3:
                    adj[u].append(v)
        comps = strongly_connected_components(adj)
        owner = {}
        for comp_id, comp in enumerate(comps):
            for node in comp:
                owner[node] = comp_id
        assert sorted(owner) == list(range(n)), "every node must be owned"
        reach = brute_reach(adj, n)
        for u in range(n):
            for v in range(n):
                mutual = reach[u][v] and reach[v][u]
                assert (owner[u] == owner[v]) == mutual, (
                    f"SCC partition wrong on {adj}"
                )
    comps = strongly_connected_components({0: [1], 1: [2], 2: [0, 3], 3: [4], 4: []})
    assert {frozenset(c) for c in comps} == {frozenset({0, 1, 2}), frozenset({3}), frozenset({4})}

    # ---- Max flow: equals min cut (max-flow min-cut theorem) ----
    def brute_min_cut(caps, n, source, sink):
        best = float("inf")
        for mask in range(1 << n):
            if not (mask >> source & 1) or (mask >> sink & 1):
                continue
            cut = 0
            for u in range(n):
                if not (mask >> u & 1):
                    continue
                for v in range(n):
                    if not (mask >> v & 1):
                        cut += caps[u][v]
            best = min(best, cut)
        return best

    for _ in range(100):
        n = rng.randrange(2, 6)
        caps = [[0] * n for _ in range(n)]
        graph = {i: [] for i in range(n)}
        for u in range(n):
            for v in range(n):
                if u != v and rng.random() < 0.35:
                    c = rng.randrange(1, 10)
                    caps[u][v] += c
                    graph[u].append((v, c))
        s, t = 0, n - 1
        flow = edmonds_karp(graph, s, t)
        expected = brute_min_cut(caps, n, s, t)
        assert flow == expected, f"flow {flow} != min cut {expected} on {caps}"
    demo = {0: [(1, 3), (2, 2)], 1: [(2, 1), (3, 2)], 2: [(3, 3)], 3: []}
    assert edmonds_karp(demo, 0, 3) == 5
    assert edmonds_karp({0: [], 1: []}, 0, 0) == 0  # source == sink

    # String labels built at runtime (equal by value, distinct objects), an
    # edge pointing back into the source, and a missing source/sink.
    s = "".join(["sou", "rce"])
    t = "".join(["si", "nk"])
    assert edmonds_karp({s: [(t, 3)], t: []}, s, t) == 3
    back_edge = {0: [(1, 2)], 1: [(2, 1), (0, 5)], 2: []}
    assert edmonds_karp(back_edge, 0, 2) == 1
    for fn in (
        lambda: edmonds_karp({0: [(1, 2)]}, 0, 9),
        lambda: edmonds_karp({0: [(1, 2)]}, 9, 1),
    ):
        try:
            fn()
            raise AssertionError("edmonds_karp accepted an absent endpoint")
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------


def main() -> None:
    tests = [
        ("sorting", test_sorting),
        ("quickselect", test_quickselect),
        ("searching", test_searching),
        ("strings", test_strings),
        ("numbers", test_numbers),
        ("dp", test_dp),
        ("greedy", test_greedy),
        ("randomized", test_randomized),
        ("graphs", test_graphs),
    ]
    for name, test in tests:
        test()
        print(f"  ok  {name}")
    print("All algorithmlib self-tests passed.")


if __name__ == "__main__":
    main()
