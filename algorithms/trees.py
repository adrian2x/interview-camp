def level_order_traversal(root):
    "O(N) nodes with O(N) memory for the queue"
    result = []
    if root is None:
        return result
    queue = deque()
    queue.append(root)
    while queue:
        currentLevel = []
        levelSize = len(queue)
        for _ in range(levelSize):
            currentNode = queue.popleft()
            # add the node to the current level
            currentLevel.append(currentNode.val)
            # insert the children of current node in the queue
            if currentNode.left:
                queue.append(currentNode.left)
            if currentNode.right:
                queue.append(currentNode.right)
        result.append(currentLevel)

    return result


def all_paths_wsum(root, given_sum):
    allPaths = []

    def check_path_sum(node, sum, path):
        if not node:
            return
        if not node.left and not node.right:
            if sum == node.val:
                allPaths.append(path + [node.val])
        if node.left:
            check_path_sum(node.left, sum - node.val, path + [node.val])
        if node.right:
            check_path_sum(node.right, sum - node.val, path + [node.val])

    check_path_sum(root, given_sum, [])
    return allPaths


def count_subpaths_wsum(root, given_sum):
    def helper(node, sum, path):
        if node is None:
            return 0

        path.append(node.val)
        # check if any subpath == sum
        pathSum, counter = 0, 0
        for i in range(len(path) - 1, -1, -1):
            pathSum += path[i]
            if pathSum == sum:
                counter += 1

        counter += helper(node.left, sum, path)
        counter += helper(node.right, sum, path)
        # remove current node
        del path[-1]
        return counter

    return helper(root, given_sum, [])
