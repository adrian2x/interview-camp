class TrieNode():
    """ The node of a trie represents a single letter and contains
        references to other letters in its `childrens` map.
    """
    def __init__(self, char=''):
        self.char = char
        self.is_last = False # indicates the end of a word
        self.children = {} # map letters -> node


class Trie():
    "A Tree where the nodes represent letters in a word."
    def __init__(self):
        "Make a new Trie with a root node"
        self.root = TrieNode(None)

    def insert(self, word: str):
        "Insert a key in the Trie"
        if word is None: return
        # Start searching at the root
        node = self.root
        # Look for each character in the trie
        for i in word:
            # If not already there, create a new Node for this letter
            if node.children.get(i) is None:
                node.children[i] = TrieNode(i)
            # Start from this letter
            node = node.children[i]

        # Finally, mark the end character as a leaf node
        node.is_last = True

    def search(self, word: str):
        "Returns True if the key is found in the Trie"
        if word is None: return False
        node = self.root
        for i in word:
            child = node.children.get(i)
            if child is None:
                return False
            node = child
        # If we ended up at a leaf node, the key is in the Trie
        return node.is_last if node else False

    def _del_deep(self, key, node, index=0):
        if index == len(key) and node.is_last:
            # Unmark the key end
            node.is_last = False
            return node
        for i in range(index, len(key)):
            ch = key[i]
            child = node.children.get(ch)
            if child is None:
                return None
            deleted = self._del_deep(key, child, i + 1)
            if deleted is not None:
                # Delete the node if it's not an end and has no children
                if not deleted.is_last and not deleted.children:
                    # remove from children and return this too
                    del node.children[ch]
                    return node
            return deleted

    def delete(self, key):
        """Search for and delete a given key"""
        if key is None:
            return False
        self._del_deep(key, self.root, 0)

# TESTS
# Tests
# Input keys (use only 'a' through 'z')
keys = ["the", "a", "there", "answer", "any",
        "by", "bye", "their", "abc"]
output = ["Not present in trie", "Present in trie"]

t = Trie()
print("Keys to insert: ")
print(keys)

# Construct Trie
for key in keys:
    t.insert(key)

# Search for different keys
if t.search("the") is True:
    print("the --- " + output[1])
else:
    print("the --- " + output[0])

if t.search("these") is True:
    print("these --- " + output[1])
else:
    print("these --- " + output[0])

if t.search("abc") is True:
    print("abc --- " + output[1])
else:
    print("abc --- " + output[0])

t.delete("abc")
print("Deleted key \"abc\"")

if t.search("abc") is True:
    print("abc --- " + output[1])
else:
    print("abc --- " + output[0])
