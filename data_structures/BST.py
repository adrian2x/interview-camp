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
        self.left = None
        self.right = None
        self.parent = None


class BST:
    "Binary Search Tree"

    def __init__(self):
        self.root = None

    def add(self, k, v=None):
        "Add key to the tree"

        # Check for root node
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

    def remove(self, k):
        "Remove a key from the tree"
        if self.root is None:
            raise ValueError("value not in tree")

        node = self.root.search(k)  # find node to delete

        if node is self.root:
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
