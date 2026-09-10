"""
algorithmlib.numbers - classical number theory and arithmetic algorithms.

Every function is a pure, single-shot computation: you pass numbers in, you
get a number (or a list of numbers) back. No state, no objects to update -
exactly the "functional" contract this package follows.

The algorithms:

    gcd, lcm                 Euclid's algorithm and its trivial cousin
    extended_gcd             Bezout coefficients: a*x + b*y = gcd(a, b)
    modular_inverse          the multiplicative inverse modulo m
    modular_pow              fast modular exponentiation (binary exponentiation)
    sieve_of_eratosthenes    every prime up to a bound, in one shot
    is_prime                 Miller-Rabin primality test
    integer_sqrt             floor(sqrt(n)) by Newton's method, integer exact
    hamming_weight           Brian Kernighan's bit-counting trick

The through-line for interviews: *repeated squaring* appears in modular_pow,
in the Miller-Rabin test (via pow(a, d, n)), and in Newton's method (doubling
the number of correct digits each step). If you recognize those two shapes -
halve the exponent, double the precision - you can reconstruct half of number
theory from first principles.
"""

from typing import List, Tuple


# ---------------------------------------------------------------------------
# Euclid's algorithm family
# ---------------------------------------------------------------------------


def gcd(a: int, b: int) -> int:
    """
    Return the greatest common divisor of a and b (Euclid's algorithm).

    The key observation is that a common divisor of a and b also divides
    a - b, so gcd(a, b) == gcd(b, a % b): the remainder replaces the larger
    number and the pair shrinks until b reaches 0, at which point the answer
    is a. Because the numbers at least halve every two steps, the loop runs
    in O(log min(a, b)) - fast enough for 1000-digit integers.

    Negatives are normalized with abs(); gcd(0, n) == abs(n) and the
    conventional gcd(0, 0) == 0.

    Time: O(log min(a, b)).  Space: O(1).

    Example:
        >>> gcd(48, 18)
        6
        >>> gcd(0, 5)
        5
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """
    Return the least common multiple of a and b.

    Uses the identity lcm(a, b) * gcd(a, b) == |a * b|, dividing *before*
    multiplying so the intermediate product never overflows.

    Time: O(log min(a, b)) - one gcd call.  Space: O(1).

    Example:
        >>> lcm(4, 6)
        12
        >>> lcm(0, 5)
        0
    """
    if a == 0 or b == 0:
        return 0
    return abs(a) // gcd(a, b) * abs(b)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Return (g, x, y) such that a*x + b*y == g == gcd(a, b) (Bezout's
    identity), via the extended Euclidean algorithm.

    The standard Euclid loop tracks not only the running remainder but also
    the coefficients that produce it from the original a and b. Think of a
    small table whose columns are (r, s, t) with the invariant
    r == a*s + b*t, initialised with rows (a, 1, 0) and (b, 0, 1). Each
    step subtracts q = old_r // r times the current row from the previous
    one, applied to all three columns at once, which preserves the invariant
    for the new row. When the remainder hits 0 the row before it holds
    gcd(a, b) together with its Bezout coefficients.

    These coefficients are the engine behind modular_inverse and, further
    afield, the Chinese Remainder Theorem and RSA key generation.

    Time: O(log min(a, b)).  Space: O(1).

    Example (gcd is 2; verify: 240 * -9 + 46 * 47 == 2):
        >>> extended_gcd(240, 46)
        (2, -9, 47)
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    # With a negative input the running remainder can come out negative; gcd
    # is conventionally non-negative, so flip all three signs together (the
    # identity a*x + b*y == g is preserved by the flip).
    if old_r < 0:
        return -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def modular_inverse(a: int, m: int) -> int:
    """
    Return the multiplicative inverse of a modulo m: the value x in [0, m)
    with (a * x) % m == 1. Raises ValueError when a and m are not coprime
    (no inverse exists then).

    Existence argument: a * x ≡ 1 (mod m) means a*x + m*y == 1 for some y,
    and Bezout's identity says that equation is solvable exactly when
    gcd(a, m) == 1. extended_gcd hands us the x; x % m normalizes it into
    the canonical range.

    Time: O(log m).  Space: O(1).

    Raises ValueError if a and m are not coprime (no inverse exists then),
    or if m is not at least 2 (arithmetic mod 1 is degenerate).

    Example:
        >>> modular_inverse(3, 11)     # 3 * 4 == 12 == 1 (mod 11)
        4
        >>> modular_inverse(2, 4)       # gcd(2, 4) == 2, so no inverse
        Traceback (most recent call last):
            ...
        ValueError: a and m are not coprime
    """
    if m <= 1:
        raise ValueError("modulus must be greater than 1")
    g, x, _y = extended_gcd(a, m)
    if g != 1:
        raise ValueError("a and m are not coprime")
    return x % m


# ---------------------------------------------------------------------------
# Modular exponentiation
# ---------------------------------------------------------------------------


def modular_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Return (base ** exponent) % modulus using binary exponentiation -
    O(log exponent) multiplications instead of exponent of them.

    The trick is to rewrite the exponent in binary and to keep *squaring*
    the base: base^13 == base^8 * base^4 * base^1, and each power in that
    list is the square of the previous one. Every set bit of the exponent
    contributes one multiply; every bit contributes one squaring. All
    arithmetic is reduced modulo `modulus` after each step so the numbers
    never grow.

    This is the single most reused algorithm in number theory: RSA, Diffie-
    Hellman, and Miller-Rabin below all build on it. (Python's built-in
    pow(base, exponent, modulus) is the production version.)

    Time: O(log exponent) multiplications.  Space: O(1).

    Example:
        >>> modular_pow(4, 13, 497)     # 4^13 = 67108864 = 445 (mod 497)
        445
        >>> modular_pow(2, 10, 1000)
        24
    """
    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if modulus == 1:
        return 0

    result = 1
    base %= modulus
    while exponent:
        if exponent & 1:  # the current bit of the exponent is set
            result = (result * base) % modulus
        base = (base * base) % modulus  # square for the next bit
        exponent >>= 1
    return result


# ---------------------------------------------------------------------------
# Prime hunting
# ---------------------------------------------------------------------------

# The first twelve primes. As Miller-Rabin bases they are *deterministic* for
# every n < 3.3 * 10^24 (a verified result); beyond that the test is still
# probabilistic with negligible error.
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Return every prime <= limit, in ascending order.

    The sieve starts with a boolean array where every number is "possibly
    prime", then walks upward and crosses out the multiples of each prime it
    finds. Two optimizations matter:

    * Crossing starts at p*p, not 2*p: every smaller multiple of p was
      already crossed out by one of p's own smaller factors.
    * The walk can stop once p*p > limit: any composite <= limit has a prime
      factor <= sqrt(limit), so it has already been crossed out.

    The remaining True entries are exactly the primes. Time is O(n log log n)
    - nearly linear - which is why sieving beats testing each number.

    Note the variants a production sieve adds on top of this reference shape:
    treating 2 as a special case and walking only odd numbers (halves the
    array and about half the marking work), and packing the booleans into a
    bitset (a bytearray or machine words) to shrink memory by 8-64x.

    Time: O(n log log n).  Space: O(n).

    Example:
        >>> sieve_of_eratosthenes(30)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> sieve_of_eratosthenes(1)
        []
    """
    if limit < 2:
        return []

    is_candidate = [True] * (limit + 1)
    is_candidate[0] = is_candidate[1] = False

    p = 2
    while p * p <= limit:
        if is_candidate[p]:
            # Mark multiples of p starting at p*p (see above).
            for multiple in range(p * p, limit + 1, p):
                is_candidate[multiple] = False
        p += 1

    return [n for n, prime in enumerate(is_candidate) if prime]


def is_prime(n: int) -> bool:
    """
    Return True if n is prime, using the Miller-Rabin test.

    The idea: for an odd prime p, p - 1 = d * 2^s with d odd, and Fermat's
    little theorem says a^(p-1) == 1 (mod p). Taking square roots repeatedly
    (which is allowed because p is prime) shows that either a^d == 1 or one
    of a^(d*2), a^(d*4), ..., a^(d*2^(s-1)) == -1 (mod p). A *composite*
    number that still satisfies this for some base a is called a strong
    pseudoprime to that base - but a composite can pass only a small
    fraction of bases, so testing several bases makes the error negligible.

    The bases used here (the first twelve primes) make the test fully
    deterministic for every n < 3.3 * 10^24, which covers all practical
    inputs. A tiny trial division first handles small numbers and even
    inputs cheaply.

    Time: O(k log^3 n) for k bases.  Space: O(1).

    Example:
        >>> is_prime(97)
        True
        >>> is_prime(561)                # Carmichael number: fools Fermat
        False
    """
    if n < 2:
        return False

    # Cheap trial division against the base set: catches small numbers and
    # any composite whose smallest prime factor is in the list.
    for p in _MR_BASES:
        if n % p == 0:
            return n == p

    # Factor n - 1 as d * 2^s with d odd.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for a in _MR_BASES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue  # this base says "probably prime"
        # Square x up to s - 1 times looking for -1 (i.e. n - 1).
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False  # never hit -1: n is composite
    return True


# ---------------------------------------------------------------------------
# Square roots
# ---------------------------------------------------------------------------


def integer_sqrt(n: int) -> int:
    """
    Return floor(sqrt(n)), the largest integer whose square is <= n, using
    Newton's method on integers.

    Newton's iteration for sqrt is x <- (x + n / x) / 2: each step roughly
    doubles the number of correct digits, so from a starting guess of n the
    loop converges in O(log n) steps - and because all arithmetic is integer
    (the floor at each division), the iterates decrease monotonically to
    floor(sqrt(n)) instead of oscillating around it. The loop stops when an
    iteration fails to improve on the previous one.

    This integer version avoids floating-point rounding entirely, which makes
    it exact for arbitrarily large n (try it on a 100-digit number).

    Time: O(log n) iterations of O(log^2 n) arithmetic.
    Space: O(1).

    Example:
        >>> integer_sqrt(50)             # 7^2 == 49 <= 50 < 64 == 8^2
        7
        >>> integer_sqrt(144)
        12
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n

    x = n
    y = (x + n // x) // 2  # first Newton step
    while y < x:
        x = y  # keep the smaller iterate
        y = (x + n // x) // 2
    return x


# ---------------------------------------------------------------------------
# Bit tricks
# ---------------------------------------------------------------------------


def hamming_weight(n: int) -> int:
    """
    Return the number of 1-bits in the binary representation of n, using
    Brian Kernighan's trick: n & (n - 1) clears the *lowest* set bit.

    Why it works: subtracting 1 from n flips the lowest 1-bit to 0 and every
    0-bit below it to 1; ANDing with the original n therefore keeps all the
    higher bits and drops exactly that lowest set bit. One iteration per set
    bit - so the cost is O(popcount), not O(number of bits).

    Time: O(number of set bits).  Space: O(1).

    Example:
        >>> hamming_weight(0b1101)        # 13 == 8 + 4 + 1
        3
        >>> hamming_weight(0)
        0
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    count = 0
    while n:
        n &= n - 1  # clear the lowest set bit
        count += 1
    return count
