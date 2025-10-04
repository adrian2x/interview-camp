def permutations(values, pos=0, prev=[]):
    # check for solution
    if pos == len(values):
        yield prev
    else:
        for i in range(len(prev) + 1):
            # insert a new item into every position
            newperm = list(prev)
            newperm.insert(i, values[pos])
            yield from permutations(values, pos + 1, newperm)


print("permutations:")
for p in permutations("abc"):
    print(p)


def subsets(choices):
    results = [
        [],  # include empty subset
    ]
    # go through all the items
    for x in choices:
        # check all generated subsets
        size = len(results)
        for i in range(size):
            # add new element to previous subsets
            newset = results[i] + [x]
            results.append(newset)
    return results


print("subsets:")
print(subsets("abc"))


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


def phone_mneumonics(inp, cur=0, output=""):
    if cur == len(inp):
        print(output)
    else:
        digit = inp[cur]
        for letter in phone_letters[digit]:
            phone_mneumonics(inp, cur + 1, output + letter)


print("mneumonics:")
phone_mneumonics("234")
phone_mneumonics("89")
