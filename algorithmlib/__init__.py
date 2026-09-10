"""
algorithmlib - reference implementations of classical algorithms.

Every function in this package is *functional* in the interview sense of the
word: it takes one (or a few) inputs, computes, and hands back an output.
None of them are data structures - you do not construct them and then issue a
sequence of queries and updates. You import, you call, you get a result.

The package is organized by theme, and each submodule reads like a lesson:

    algorithmlib.searching    binary search, bounds, exponential search
    algorithmlib.sorting      insertion / merge / quick / heap / tim sort
                              (+ quickselect, the selection cousin of quicksort)
    algorithmlib.strings      pattern matching: Rabin-Karp, KMP,
                              Boyer-Moore-Horspool, Z-algorithm, Manacher
    algorithmlib.graphs       shortest paths (Bellman-Ford, Dijkstra,
                              Floyd-Warshall), MST (Kruskal, Prim), Kahn's
                              topological sort, bipartite check, Kosaraju SCC,
                              Edmonds-Karp max flow
    algorithmlib.numbers      Euclid's gcd + extended gcd, modular inverse,
                              binary exponentiation, sieve of Eratosthenes,
                              Miller-Rabin primality, Newton sqrt,
                              Kernighan bit count
    algorithmlib.dp           Fibonacci, Kadane's max subarray, 0/1 knapsack,
                              subset sum, coin change, LCS, longest common
                              substring, edit distance, LIS (patience)
    algorithmlib.greedy       activity selection, fractional knapsack,
                              Huffman codes
    algorithmlib.randomized   Fisher-Yates shuffle, reservoir sampling

Design notes (why the APIs look the way they do):

* Sorting functions sort the list you hand them *in place* and return it,
  mirroring the convention already used by this repo (see algorithms/mergesort.py
  and algorithms/quicksort.py). If you want to keep your original data intact,
  pass a copy:  sorted_data = quicksort(data[:]).

* Everything is written against duck-typed sequences and hashable node labels,
  so the functions work on any comparable data - ints, floats, strings, tuples,
  or your own classes that implement __lt__ - not just on the toy examples in
  the docstrings. Only the `<` comparison is ever required of elements.

* Every public function carries type annotations and a docstring that explains
  the *why*: the loop invariant, the edge cases, and the complexity.

Quick tour:

    >>> from algorithmlib.searching import binary_search
    >>> binary_search([1, 3, 5, 7, 9], 7)
    3

    >>> from algorithmlib.sorting import timsort, quickselect
    >>> timsort([5, 2, 9, 1, 7])
    [1, 2, 5, 7, 9]
    >>> quickselect([5, 2, 9, 1, 7], k=2)   # 0-based: the 3rd smallest
    5

    >>> from algorithmlib.strings import rabin_karp
    >>> rabin_karp("doe are hearing me", "ear")
    [9]

    >>> from algorithmlib.graphs import bellman_ford
    >>> bellman_ford({"A": [("B", 4)], "B": [("C", -2)]}, source="A")
    {'A': 0, 'B': 4, 'C': 2}

    >>> from algorithmlib.numbers import gcd, sieve_of_eratosthenes
    >>> gcd(48, 18), sieve_of_eratosthenes(10)
    (6, [2, 3, 5, 7])

Run the self-tests from the repo root with:

    python3 -m algorithmlib.selfcheck
"""

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

__version__ = "0.2.0"

__all__ = [
    # dp
    "coin_change_min",
    "edit_distance",
    "fibonacci",
    "knapsack_01",
    "longest_common_subsequence",
    "longest_common_substring",
    "longest_increasing_subsequence",
    "max_subarray_sum",
    "subset_sum",
    # graphs
    "bellman_ford",
    "dijkstra",
    "edmonds_karp",
    "floyd_warshall",
    "is_bipartite",
    "kruskal_mst",
    "prim_mst",
    "strongly_connected_components",
    "topological_sort",
    # greedy
    "activity_selection",
    "fractional_knapsack",
    "huffman_codes",
    # numbers
    "extended_gcd",
    "gcd",
    "hamming_weight",
    "integer_sqrt",
    "is_prime",
    "lcm",
    "modular_inverse",
    "modular_pow",
    "sieve_of_eratosthenes",
    # randomized
    "fisher_yates",
    "reservoir_sample",
    # searching
    "binary_search",
    "exponential_search",
    "lower_bound",
    "upper_bound",
    # sorting / selection
    "heapsort",
    "insertion_sort",
    "merge_sort",
    "quickselect",
    "quicksort",
    "timsort",
    # strings
    "boyer_moore_horspool",
    "hamming_distance",
    "kmp_search",
    "manacher",
    "prefix_function",
    "rabin_karp",
    "z_function",
    "z_search",
]
