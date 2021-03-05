def rabin_karp(text: str, search: str, base=127):
    """
    A Rabin-Karp implementation to find occurrences of search in text, in O(N + M)
    text: the text where we should search for pattern
    search: the pattern to search for in text
    base: the alphabet size (eg. 127 for ascii)
    """
    N, M = len(text), len(search)

    if N < 1 or M < 1 or M > N:
        return -1

    if N < 48:
        return text.find(search)
    if text.endswith(search):
        return N - M

    MOD = 1000000007  # prevent overflow (or upcasting)

    def rollhash(seq: str, length):
        "Create a hash by adding all characters in the string"
        value = 0
        for i in range(length):
            value = (value * base + ord(seq[i])) % MOD
        return value

    # hash the first M characters of text
    hash_text = rollhash(text, M)
    hash_search = rollhash(search, M)
    coeff = pow(base, M - 1, MOD)  # first coefficient

    # check for all sequences of M characters in text
    for i in range(N - M):
        if hash_search == hash_text:
            # check if we found the pattern
            for p in range(M):
                if search[p] != text[i + p]:
                    break
            else:
                return i

        # update rolling hash of the text window
        # by subtracting the first letter and adding the new one to the end
        hash_text = (hash_text - ord(text[i]) * coeff) % MOD
        hash_text = (hash_text * base + ord(text[i + M])) % MOD

    return -1


assert rabin_karp("doe are hearing me", "ear") == 9
assert rabin_karp("doe are hearing me", " me") == 15


def lcs(str1, str2):
    """Find the longest common subsequence between two strings:"""
    if not str1 or not str2:
        return 0

    def helper(str1, cur1, str2, cur2):
        # use p1 and p2 to walk the strings backwards
        if cur1 < 0:
            return 0
        if cur2 < 0:
            return 0

        # if the characters match, we count the match and continue
        if str1[cur1] == str2[cur2]:
            return 1 + helper(str1, cur1 - 1, str2, cur2 - 1)

        # else, we need to find the best between skipping the last character
        # from each string
        return max(
            helper(str1, cur1 - 1, str2, cur1), helper(str1, cur1, str2, cur2 - 1)
        )

    return helper(str1, len(str1) - 1, str2, len(str2) - 1)


assert lcs("abcdgh", "aedfhr") == 3


def levenshtein(str1, str2):
    """
    Levenshtein Edit Distance is defined as the minimum numbers of operations to make two given strings match.
    The possible operations are replacing, inserting or removing a character.
    The result should be the number of operations needed to match the two strings, which can be used as a measure of similarity.
    """

    N, M = len(str1), len(str2)
    """
    We need a table to store subproblems for matching substrings, like so:
        ''   x   y   z   …
    ''  0,   1,  2,  3,  4
    a   1,
    b   2,
    c   3,
    …   4,

    The first row of the table represents the distance between the empty string ('') and the substrings of the given string ("xyz"), which requires N insertions.
    Similarly the first column of the table represents the distance from '' to "abc" which also requires N insertions.
    """
    # initialize distance from empty string to given strings
    # Note that instead of a full matrix, we could just use two arrays (one being the last computed row and the other being the current row)
    prev = [0] * (N + 1)
    curr = list(range(N + 1))

    # check the distance between the two strings
    for i in range(1, M + 1):
        # swap the arrays with previous calculations
        curr, prev = prev, curr
        curr[0] = i  # edit distance from empty string
        for j in range(1, N + 1):
            # when the characters match, the result is the same as excluding the characters
            if str2[i - 1] == str1[j - 1]:
                curr[j] = prev[j - 1]
            else:
                # we need at least one operation for this pair, plus the least operations for all the previous characters
                curr[j] = 1 + min(curr[j - 1], prev[j], prev[j - 1])
                # Note curr[j - 1] means deleting from first string (or inserting in second)
                # prev[j] means deleting from second string (or inserting in first)
                # prev[j - 1] means replacing either character from the strings to match the other

    return curr[N]


assert levenshtein("benyam", "ephrem") == 5


def atoi(s: str) -> int:
    "Convert a string to integer ignore any leading spaces"
    max_val = 2147483647
    min_val = -2147483648
    ans = 0
    sign = 1
    start = 0
    length = len(s)
    for i in range(length):
        if s[i] != " ":
            break
        start += 1

    if start < length:
        if s[start] == "+":
            sign = 1
            start += 1
        elif s[start] == "-":
            sign = -1
            start += 1
    s = s[start:]

    for pos in range(length):
        ch = s[pos]
        if not (ch >= "0" and ch <= "9"):
            break

        ans *= 10
        ans += ord(ch) - ord("0")

    if ans > max_val and sign == 1:
        return max_val

    if -ans < min_val and sign == -1:
        return min_val

    return ans * sign


def itoen(num: int):
    "Return english numerals for a given integer"
    if num < 0:
        return ""
    if num == 0:
        return "Zero"

    nums = {
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine",
        10: "Ten",
        11: "Eleven",
        12: "Twelve",
        13: "Thirteen",
        14: "Fourteen",
        15: "Fifteen",
        16: "Sixteen",
        17: "Seventeen",
        18: "Eighteen",
        19: "Nineteen",
        20: "Twenty",
        30: "Thirty",
        40: "Fourty",
        50: "Fifty",
        60: "Sixty",
        70: "Seventy",
        80: "Eighty",
        90: "Ninety",
        100: "Hundred",
        1000: "Thousand",
        1000000: "Million",
        1000000000: "Billion",
        1000000000000: "Trillion",
        1000000000000000: "Quadrillion",
        1000000000000000000: "Sextillion",
        1000000000000000000000: "Septillion",
        1000000000000000000000000: "Octillion",
    }

    str1 = str(num)

    def groups(str1):
        "Split the string in groups of three right to left"
        size = len(str1) - 3
        while size >= 0:
            yield str1[size : size + 3]
            size -= 3
        if size + 3 > 0:
            yield str1[: size + 3]

    power = 1
    result = ""
    for part in groups(str1):
        # convert each 3-digit group and append
        res = ""
        if len(part) == 1:
            res += nums[int(part)]
        elif len(part) == 2:
            if int(part) in nums:
                res += nums[int(part)]
            else:
                sign = int(part[0])
                rem = int(part[1])
                if sign > 0:
                    res += nums[sign * 10]
                if rem in nums:
                    res += " " + nums[rem]
        else:
            sign = int(part[0])
            rem = int(part[1:])
            if sign > 0:
                res += nums[sign] + " Hundred"
            if rem in nums:
                res += " " + nums[rem]
            elif rem > 0:
                res += nums[(rem // 10) * 10]
                if rem % 10 > 0:
                    res += " " + nums[rem % 10]
        # append the current unit
        if power > 10 and int(part) > 0:
            res += " " + nums[power]
        power *= 1000
        result = res.strip() + " " + result.strip()
    return result.strip()


print(itoen(1111))
