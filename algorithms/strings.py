

def find_permutation(str1, pattern):
    freq = {}
    patlen = len(pattern)
    for c in pattern:
        if not c in freq:
            freq[c] = 0
        freq[c] += 1

    start = 0
    end = 0
    matched = 0
    while end < len(str1):
        char = str1[end]
        if char in freq:
            freq[char] -= 1
            if freq[char] == 0:
                matched += 1

        if matched == patlen:
            return True

        if end - start >= patlen:
            # shrink the window from the start
            leftchar = pattern[start]
                if leftchar in 

        end += 1

    return False


def is_perm(str1, other):
  chars1 = {}
  chars2 = {}
  for c in str1:
    if c not in chars1:
      chars1[c] = 0
    chars1[c] += 1

  for c in other:
    if c not in chars1:
      return False
    if c not in chars2:
      chars2[c] = 0
    chars2[c] += 1

  for k in chars1:
    if chars1[k] != chars2[k]:
      return False

  return True


find_permutation("aaacb", "abc")


def rabin_karp(text: str, search: str):
    """
    A Rabin-Karp implementation to find occurrences of search in text, in O(N + M)
    text: the text where we should search for pattern
    search: the pattern to search for in text
    mod: a prime number
    """
    if text is None or search is None:
        return -1
    if text == "" or search == "":
        return -1
    if len(search) > len(text):
        return -1


    def rollhash(seq: str, length):
        "Create a hash by adding all characters in the string"
        value = 0
        for i in range(length):
            value += ord(seq[i])
        return value

    # hash the first M characters of text
    N, M = len(text), len(search)
    hash_text = rollhash(text, M)
    hash_search = rollhash(search, M)

    # check for all sequences of M characters in text
    for i in range(N - M + 1):
        if hash_search == hash_text:
            for p in range(M):
                print("submatch at", i + p)
                if search[p] != text[i + p]:
                    break
            else:
                return i

        # update rolling hash of the text window
        hash_text -= ord(text[i])
        hash_text += ord(text[i + M])

    return -1


rabin_karp("doe are hearing me", "ear")
