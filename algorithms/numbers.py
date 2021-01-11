import random

# from nzmath.ecpp import ecpp


def primenums(_max=None):
    primes = [2, 3, 5]
    # primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for num in primes:
        yield num
    num = primes[-1] + 2
    while True:
        if isprime(num):
            primes.append(num)
            yield num
        num += 2


def isprime(n: int, trials=8):
    """
    Miller-Rabin primality test.

    A return value of False means n is certainly not prime. A return value of
    True means n is very likely a prime.
    """
    for p in (2, 3, 5, 7, 11, 13, 17):
        if n == p:
            return True
        if n % p == 0:
            return False

    s = 0
    d = n - 1
    while d % 2 == 0:
        d >>= 1
        s += 1
    assert 2 ** s * d == n - 1

    def trial_composite(k):
        if pow(k, d, n) == 1:
            return False
        for i in range(s):
            if pow(k, 2 ** i * d, n) == n - 1:
                return False
        return True  # k is definitely composite

    for i in range(trials):
        a = random.randrange(2, n)
        if trial_composite(a):
            return False

    return True


def try_divisor(n: int):
    "Primality test using 6k + 1 optimization"
    if n <= 3:
        return n > 1

    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


for p in primenums():
    print(p)