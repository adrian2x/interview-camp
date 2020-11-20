from trie import Trie


# Tests
# Input keys (use only 'a' through 'z')
keys = ["the", "a", "there", "answer", "any", "by", "bye", "their", "abc"]
output = ["Not present in trie", "Present in trie"]

t = Trie()
print("Keys to insert: ")
print(keys)

# Construct Trie
for key in keys:
    t.insert(key)
    assert t.search(key) is True

for key in t:
    print('>', key)

# it should remove the key
t.remove("the")
print('>>> Deleted key "the"')
assert not t.search("the")

# it shouldnt remove other keys
assert t.search("there")
assert t.search("their")


t = Trie()
t.insert("the")
t.remove("the")
assert not "the" in t
