
'''
How many ways are there to decode an encoded string using this alphabet:
a: 1
b: 2
c: 3
...
z: 26
input: a string such as "33"
output: 2
'''
def decode_ways(data, k, cache):
    if k == 0:
        return 1

    N = len(data)
    start = N - k
    if data[start] == "0":
        return 0

    if cache[k] != None:
        return cache[k]

    # try next letter
    ways = decode_ways(data, k - 1, cache)
    # try next two letters
    if int(data[start:start + 1]) <= 26 and k >= 2:
        ways += decode_ways(data, k - 2, cache)

    cache[k] = ways
    return ways


test = "33"
print(decode_ways(test, len(test), [None] * (len(test) + 1)))


def permutations(search, val="", cache={}):
    length = len(search)
    if len(val) == length:
        return print(val)
    for char in search:
        if not cache.get(char):
            cache[char] = True
            permutations(search, val + char, cache)
            cache[char] = False


s = "abc"
permutations(s)


def n_matched_parens(n):
    "Generate all possible n-matched parenthesis"
    def helper(cur, opened=0, closed=0):
        if len(cur) == n * 2:
            if opened == n and closed == n:
                print(cur)
        else:
            not_closed = opened - closed
            if opened < n:
                helper(cur + "(", opened + 1, closed)
            if closed < n and not_closed > 0:
                helper(cur + ')', opened, closed + 1)

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
