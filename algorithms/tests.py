from collections import defaultdict
from functools import cache
import heapq

# 10. Regular Expression Matching
# See https://leetcode.com/problems/regular-expression-matching/solutions/127565/regular-expression-matching/
def isMatch(s: str, p: str) -> bool:
    while "**" in p:
        p = p.replace("**", "*")

    S, P = len(s), len(p)

    @cache
    def solve(si, pi):
        if si >= S and pi >= P:
            return True

        if pi >= P:
            return False

        if si < S and (s[si] == p[pi] or p[pi] == "?"):
            return solve(si + 1, pi + 1)

        if p[pi] == "*":
            return (si < S and solve(si + 1, pi)) or solve(si, pi + 1)

        return False

    return solve(0, 0)


assert isMatch("aa", "a") == False
assert isMatch("aa", "aa") == True
assert isMatch("aa", "*") == True
assert isMatch("cb", "?a") == False


def coinChangeMemo(coins, amount):
    @cache
    def change(amount):
        if amount == 0:
            return 0

        best = amount + 1
        for c in coins:
            if c <= amount:
                res = coinChangeMemo(coins, amount - c)
                if res != -1:
                    best = min(best, 1 + res)
        return best if best <= amount else -1

    return change(amount)


# assert coinChangeMemo([2], 3) == -1
# assert coinChangeMemo([1, 2, 5], 11) == 3
# assert coinChangeMemo([186, 419, 83, 408], 6249) == 20


def coinChange(coins, amount):
    change = [0] * (amount + 1)  # remember sub amounts
    for x in range(1, amount + 1):
        # solve for amount `x`
        best = amount + 1
        for c in coins:
            # use the best change for amount `x - c`.
            if c <= x and change[x - c] + 1 < best:
                best = change[x - c] + 1
        change[x] = best

    return change[amount] if change[amount] <= amount else -1


assert coinChange([2], 3) == -1
assert coinChange([1, 2, 5], 11) == 3
assert coinChange([186, 419, 83, 408], 6249) == 20


def alienOrder(self, words):
    # Get all unique_chars
    unique_chars, graph = set(), {}

    for src, word in enumerate(words):
        unique_chars = unique_chars.union(set(word))

    for word_char in unique_chars:
        graph[word_char] = set()

    # Build graph

    for src in range(len(words) - 1):
        word, other = words[src], words[src + 1]

        if word.startswith(other) and len(word) > len(other):
            return ""

        for word_char, other_char in zip(word, other):
            if word_char != other_char:
                graph[word_char].add(other_char)
                break

    # Topological sort

    degree, stack = defaultdict(int), []

    for src in graph:
        for dest in graph[src]:
            degree[dest] += 1

    stack = [c for c in unique_chars if degree[c] == 0]

    visited, res = set(), []

    while stack:
        node = stack.pop(0)

        visited.add(node)
        res.append(node)

        for neighbor in graph[node]:
            degree[neighbor] -= 1

            if degree[neighbor] == 0:
                stack.append(neighbor)

    return "".join(res) if len(visited) == len(unique_chars) else ""


# Subarray with K Different Integers
class Solution:
    def subarraysWithKDistinct(self, A: "List[int]", K: "int") -> "int":
        return self.subarraysWithAtMostKDistinct(A, K) - self.subarraysWithAtMostKDistinct(A, K - 1)

    def subarraysWithAtMostKDistinct(self, s, k):
        lookup = defaultdict(int)
        l, r, counter, res = 0, 0, 0, 0
        while r < len(s):
            lookup[s[r]] += 1
            if lookup[s[r]] == 1:
                counter += 1
            r += 1
            while l < r and counter > k:
                lookup[s[l]] -= 1
                if lookup[s[l]] == 0:
                    counter -= 1
                l += 1
            res += r - l
        return res


class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        # Init return array in which, we'll store justified lines
        lines = []
        # current line width
        width = 0
        # current line words
        used_words = []

        for word in words:
            # Gather as many words that will fit under maxWidth restrictions.
            # Line length is a sum of:
            # 1) Current word length
            # 2) Sum of words already in the current line
            # 3) Number of spaces (each word needs to be separated by at least one space)
            if (len(word) + width + len(used_words)) <= maxWidth:
                used_words.append(word)
                width += len(word)
                continue

            # If the current line only contains one word, fill the remaining string with spaces.
            if len(used_words) == 1:
                # insert spaces at the end as needed
                line = " ".join(used_words).ljust(maxWidth)
                lines.append(line)
            else:
                # Else calculate how many common spaces and extra spaces are there for the current line.
                # Example:
                #  line = ['a', 'computer.', 'Art', 'is']
                # width left in line equals to: maxWidth - width: 20 - 15 = 5
                # len(line) - 1 because to the last word, we aren't adding any spaces
                # Now divmod will give us how many spaces are for all words and how many extra to distribute.
                # divmod(5, 3) = 1, 2
                # This means there should be one common space for each word, and for the first two, add one extra space.
                spaces, rem = divmod(maxWidth - width, len(used_words) - 1)

                i = 0
                # Distribute extra spaces first
                # There cannot be a case where extra spaces count is greater or equal to number words in the current line.
                while rem > 0:
                    used_words[i] += " "
                    rem -= 1
                    i += 1

                # Join line array into a string by common spaces, and append to justified lines.
                lines.append((" " * spaces).join(used_words))

            # Start the next line with the current word in iteration
            used_words = [word]
            width = len(word)

        # Last but not least format last line to be left-justified with no extra space inserted between words.
        # No matter the input, there always be the last line at the end of for loop, which makes things even easier considering the requirement.
        lines.append(" ".join(used_words).ljust(maxWidth))

        return lines
