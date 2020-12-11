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

    if N < 48: return text.find(search)
    if text.endswith(search): return N - M

    MOD = 1000000007 # prevent overflow (or upcasting)

    def rollhash(seq: str, length):
        "Create a hash by adding all characters in the string"
        value = 0
        for i in range(length):
            value = (value * base + ord(seq[i])) % MOD
        return value

    # hash the first M characters of text
    hash_text = rollhash(text, M)
    hash_search = rollhash(search, M)
    coeff = pow(base, M - 1, MOD) # first coefficient

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
    """ Find the longest common subsequence between two strings:
    """
    if not str1 or not str2:
        return 0

    def helper(str1, p1, str2, p2):
        # use p1 and p2 to walk the strings backwards
        if p1 < 0: return 0
        if p2 < 0: return 0

        # if the characters match, we count the match and continue
        if str1[p1] == str2[p2]:
            return 1 + helper(str1, p1 - 1, str2, p2 - 1)

        # else, we need to find the best between skipping the last character
        # from each string
        return max(helper(str1, p1 - 1, str2, p1), helper(str1, p1, str2, p2 - 1))

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
        curr[0] = i # edit distance from empty string
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
