"Hash Table implementation"
from typing import Any, List, Optional

from collections.abc import MutableMapping


class HashTable(MutableMapping):
    "A Hash Table implemented using chaining with lists"

    def __init__(self, size: int = 37):
        self._slots = size  # number of buckets
        self._buckets: List[Optional[List[Any]]] = [None] * size
        self._size = 0  # keys inserted

    def hash(self, value):
        return hash(value) % self._slots

    def _rehash(self):
        size = self._slots * 2 + 1
        new_buckets = [None] * size
        self._slots = size
        for bucket in self._buckets:
            if bucket is not None:
                for key, value in bucket:
                    k = self.hash(key)
                    if new_buckets[k] is None:
                        new_buckets[k] = [(key, value)]
                    else:
                        new_buckets[k].append((key, value))
        # Update the buckets
        self._buckets = new_buckets

    # abc.MutableSequence
    def __setitem__(self, key, value) -> None:
        "Add key-value entry"
        k = self.hash(key)
        if self._buckets[k] is None:
            self._buckets[k] = [(key, value)]
            self._size += 1
        else:
            # Find the key if it exists
            for i, entry in enumerate(self._buckets[k]):
                if key == entry[0]:
                    self._buckets[k][i] = (key, value)
                    break
            else:
                self._buckets[k].append((key, value))
                self._size += 1

        # Resize when load is above threshold
        load = float(self._size) / float(self._slots)
        if load > 10: self._rehash()

    # abc.MutableSequence
    def __getitem__(self, key) -> Any:
        "Get the value for a key if it exists"
        k = self.hash(key)
        if self._buckets[k] is not None:
            # Check the bucket for key
            for entry in self._buckets[k]:
                if key == entry[0]:
                    return entry[1]

        # Raise if the key was not found
        raise KeyError("key is not in hash table")

    # abc.MutableSequence
    def __delitem__(self, key) -> None:
        "Delete a key-value pair"
        k = self.hash(key)
        if self._buckets[k] is not None:
            # Pop the key if it exists
            for i, entry in enumerate(self._buckets[k]):
                if key == entry[0]:
                    self._buckets[k].pop(i)
                    self._size -= 1
                    break

    # abc.Collection
    def __contains__(self, key) -> bool:
        k = self.hash(key)
        if self._buckets[k] is not None:
            for entry in self._buckets[k]:
                if key == entry[0]:
                    return True
        return False

    # abc.Collection
    def __len__(self):
        return self._size

    # abc.Collection
    def __iter__(self):
        for bucket in self._buckets:
            if bucket is not None:
                for key, val in bucket:
                    yield key
