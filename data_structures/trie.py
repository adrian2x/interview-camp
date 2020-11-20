" A Trie implementation"

from typing import Any, Mapping


class Node:
    """ The node of a trie represents a single letter and contains
        references to other letters in its `childrens` map.
    """

    def __init__(self, val):
        self.value = val
        self.is_end = False  # indicates end of an entry
        self.children = {}  # map letters -> node


class Trie:
    "A Trie is a tree where the nodes represent letters in a word"

    def __init__(self):
        self.root = Node(None)
        self._size = 0

    def insert(self, key: str):
        "Insert a key in the trie"
        if key is None: return

        self._size += 1
        node = self.root
        for c in key:
            # check if value already exists
            if node.children.get(c) is None:
                # add a new node with the value
                node.children[c] = Node(c)
            # continue with child
            node = node.children[c]
        node.is_end = True  # set entry

    def search(self, key):
        "Returns True if a key is in the trie"
        if key is None:
            return None

        node = self.root
        for c in key:
            # check for a child value
            if node.children.get(c) is None:
                return False
            # continue with child
            node = node.children[c]

        # check if this is an entry
        return node and node.is_end

    def __contains__(self, val):
        return self.search(val)

    def remove(self, key):
        "Remove a key from the trie"
        res = delete(self.root, key, 0, len(key))
        if res: self._size -= 1
        return res

    def __len__(self):
        return self._size

    def __iter__(self):
        return walk(self.root, '')



def delete(node, key, level, length):
    if level == length and node.is_end:
        # check if we found a key's end, and unmark it
        node.is_end = False
        return node

    # check path for key
    for i in range(level, length):
        val = key[i]
        child = node.children.get(val)
        # if there is no child, the key is not in tree
        if child is None:
            return
        # continue deleting from child
        deleted = delete(child, key, level + 1, length)
        if deleted:
            # delete the node if its not part of another entry
            if not deleted.is_end and not deleted.children:
                # remove deleted child value
                del node.children[val]
                return node  # continue with parent
        return deleted


def walk(node, val):
    "yields all the keys starting from node"
    for key in node.children:
        child = node.children[key]
        if child.is_end:
            yield val + key
        yield from walk(child, val + key)
