from linkedlist import DoublyLinkedList


class LRUCache:
    "A Least-Recently Used Cache"

    def __init__(self, size=100) -> None:
        self._items = DoublyLinkedList()
        self._map = {}
        self.maxsize = size
        self._capacity = size

    def __len__(self):
        return len(self._items)

    def put(self, value):
        # add the element to the front of the cache
        self._items.append_head(value)
        self._capacity -= 1
        # set a reference to the node
        self._map[value] = self._items.head
        # if over capacity, evict from the back of the cache
        if self._capacity < 0:
            evicted = self._items.popright()
            del self._map[evicted]
            self._capacity += 1

    def get(self, value):
        # check if value is in the cache
        node = self._map.get(value)
        if node is None:
            return False

        # move value to the front of the cache
        if node is not self._items.head:
            self._items._remove(node)
            self._items.append_head(value)
        return True


# Tests:
cache = LRUCache(size=3)
cache.put(1)
cache.put(2)
cache.put(3)
print(cache._items)
cache.put(4)
print(cache._items)
