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
