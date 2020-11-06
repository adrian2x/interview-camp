""" Binary Search Tree (BST)

    A BST is a collection of Nodes composed of key-value pairs and in which each node key is inserted following this rule:
        Node.left <= Node < Node.right

    The keys must be comparable, while the value can be any arbitrary data.
    A notable property of the BST is that it is iterable, producing the keys in ascending order, and also supports reverse iteration for descending order.
"""
from typing import Iterator
from collections.abc import Collection


class Node:
    "A Node value in the BST"

    def __init__(self, key, value=None, left=None, right=None, parent=None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

    def __repr__(self):
        return str(self.key)

    def insert(self, k, v):
        if k <= self.key:
            if self.left:
                self.left.insert(k, v)
            else:
                self.left = Node(k, v, parent=self)
        else:
            if self.right:
                self.right.insert(k, v)
            else:
                self.right = Node(k, v, parent=self)

    def search(self, key):
        if key == self.key:
            return self
        if key < self.key:
            if self.left:
                return self.left.search(key)
        else:
            if self.right:
                return self.right.search(key)

    def succesor(self):
        node = self.right
        if node:
            while node.left:
                node = node.left
        return node

    def remove(self):
        if self.left is None:
            self.replace(self.right)
        elif self.right is None:
            self.replace(self.left)
        else:
            nxt = self.succesor()
            (self.key, self.value) = nxt.key, nxt.value
            nxt.replace(None)

    def replace(self, other):
        parent = self.parent
        if parent:
            if self is parent.left:
                parent.left = other
            else:
                parent.right = other
        if other:
            other.parent = parent
        self.dispose()

    def dispose(self):
        "Clean up references to other nodes"
        del self.value
        del self.left
        del self.right
        del self.parent

    def __min__(self):
        while self.left:
            self = self.left
        return self

    def __max__(self):
        while self.right:
            self = self.right
        return self


class BST(Collection):
    "Binary Search Tree"

    def __init__(self):
        self.root = None
        self.size = 0

    def add(self, k, v=None):
        "Add key to the tree"

        # Check for root node
        self.size += 1
        if self.root is None:
            self.root = Node(k, v)
        else:
            self.root.insert(k, v)

    def __contains__(self, k):
        if self.root is None:
            return False
        # Search from root
        node = self.root.search(k)
        return node is not None

    def __len__(self):
        return self.size

    def remove(self, k):
        "Remove a key from the tree"
        if self.root is None:
            raise ValueError("value not in tree")

        node = self.root.search(k)  # find node to delete
        if node is None:
            raise ValueError("value not in tree")

        self.size -= 1
        if node is self.root:
            # Remove the root and replace
            if node.left is None:
                node = node.right
            elif node.right is None:
                node = node.left
            else:
                nxt = node.succesor()
                node.key, node.value = nxt.key, nxt.value
                nxt.remove()

            # Set the new left node as tree root
            if node: node.parent = None
            self.root = node
        else:
            node.remove()

    def preorder(self):
        return preorder(self.root)

    def inorder(self):
        return inorder(self.root)

    def postorder(self):
        return postorder(self.root)

    def __iter__(self):
        "Default to in-order traversal"
        return inorder(self.root)

    def __reversed__(self) -> Iterator:
        return reverse_inorder(self.root)

    def max(self, k=0):
        "Return the max or k-th max value in the tree"
        if self.root is None:
            return None
        if not k:
            return max(self)

        if k > self.size:
            # check if k is out of bounds
            raise IndexError('index out of range')
        else:
            # create a reverse in-order iterator
            _iter = reverse_inorder(self.root)
            # take the first k values
            while k > 0:
                value = next(_iter)
                k -= 1
            return value

    def __min__(self):
        if self.root:
            return min(self.root).key

    def __max__(self):
        if self.root:
            return max(self.root).key


def preorder(root):
    if root is None:
        return ()
    yield root.key
    yield from preorder(root.left)
    yield from preorder(root.right)


def inorder(root):
    if root is None:
        return ()
    yield from inorder(root.left)
    yield root.key
    yield from inorder(root.right)


def reverse_inorder(root):
    "Traverse the tree in a reverse in-order sequence, which results in descending order"
    if root is None:
        return ()
    yield from reverse_inorder(root.right)
    yield root.key
    yield from reverse_inorder(root.left)

def postorder(root):
    if root is None:
        return ()
    yield from postorder(root.left)
    yield from postorder(root.right)
    yield root.key

