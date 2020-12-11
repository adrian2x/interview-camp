from BST import BST, Node


tree = BST()
tree.add(2)
tree.add(1)
tree.add(3)
tree.add(6)
tree.add(4)
tree.add(7)

print(">>> in-order:")
for i in tree.inorder():
    print(i)

print(">>> post-order:")
for i in tree.postorder():
    print(i)

print("min()", min(tree))
print("max()", max(tree))
assert max(tree) == 7

# k-th max value (order statistics)
assert tree.max(2) == 6
assert tree.max(3) == 4

assert 3 in tree
tree.remove(3)
assert 3 not in tree


#############################
##  Delete node test
#############################
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


#################################
##  Root node tests
#################################
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


#################################
##  Validate BST
#################################
n1 = Node(1)
root = Node(2)
root.left = n1

def is_bst(root):
    if root is None:
        return True
    if root.left and root.left.key > root.key:
        return False
    if root.right and root.right.key < root.key:
        return False
    return is_bst(root.left) and is_bst(root.right)

assert is_bst(root) == True


fake_tree = Node(0, right=n1)
n1.left = root
assert is_bst(fake_tree) == False


def lca(root, node, other):
    """ The idea here is to first try to find the nodes in the tree,
        and then backtrack from the leafs until the first root node where a path for
        both given nodes was found. That node is the lowest common ancestor.
    """
    if root is None: return None

    # check if we found either child
    if root == node or root == other:
        return root

    # find the child nodes from left and right
    leftSearch = lca(root.left, node, other)
    rightSearch = lca(root.right, node, other)

    # check if we found both nodes
    if not leftSearch: return rightSearch
    if not rightSearch: return leftSearch

    # we found both nodes from here, so root is LCA
    return root
