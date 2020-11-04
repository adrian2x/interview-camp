from BST import BST


tree = BST()
tree.add(2)
tree.add(1)
tree.add(3)
tree.add(6)
tree.add(4)
tree.add(7)
assert 3 in tree
tree.remove(3)
assert 3 not in tree

tree = BST()
tree.add(6)
tree.add(4)
tree.add(2)
tree.add(5)
tree.add(9)
tree.add(8)
tree.add(12)
tree.add(10)
tree.add(14)
assert 9 in tree
tree.remove(9)
assert 9 not in tree

tree.remove(6)
assert 6 not in tree
assert tree.root.key == 8


tree = BST()
tree.add(1)
tree.add(0)
tree.remove(1)
assert tree.root.key == 0
tree.remove(0)
assert tree.root is None
