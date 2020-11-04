"Linked Lists implementation"
from typing import Iterator

from collections.abc import Sequence, Iterable


class LinkedListNode:
    "Represents a single node in a LinkedList"

    def __init__(self, data):
        self.data = data
        self.next = None

    def clear(self):
        del self.data
        del self.next

    def pop(self):
        "Unwrap and return node value and clear the pointers"
        data = self.data
        self.clear()
        return data


class LinkedList(Sequence):
    "A linked list is formed by nodes which are linked together like a chain."

    def __init__(self, items: Iterable = None):
        self.head = None
        self.tail = None
        if isinstance(items, Iterable):
            self.extend(items)

    def __str__(self, end=" -> "):
        "Print the list"
        value = ""
        if self.is_empty:
            return "head" + end + "None"
        temp = self.head
        while temp.next is not None:
            value += str(temp.data) + end
            temp = temp.next
        value += str(temp.data) + end + "None"
        return value

    @property
    def is_empty(self):
        return self.head is None

    def append_head(self, value):
        "Add element to the beginning of the list"
        new_node = LinkedListNode(value)
        new_node.next = self.head
        self.head = new_node
        # Update tail
        if self.tail is None:
            self.tail = self.head

    # abc.Collection
    def __len__(self):
        count = 0
        node = self.head
        while node:
            count += 1
            node = node.next
        return count

    # abc.Collection
    def __contains__(self, value):
        "Check if the list contains a given value"
        node = self.head
        # Traverse the nodes till the end
        while node:
            # Check the node value
            if node.data is value:
                return True
            node = node.next
        return False

    # abc.Collection
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def append_tail(self, value):
        "Add element to the end of the list"
        new_node = LinkedListNode(value)
        # Check if tail exists
        if self.tail:
            self.tail.next = new_node
        else:
            self.head = new_node
        self.tail = new_node
        return self

    def extend(self, seq: Iterable):
        "Extend list by appending elements from a sequence"
        for item in seq:
            self.append_tail(item)
        return self

    def remove(self, value):
        """
        Remove a value from the list
        """

        if self.is_empty:
            # List is empty, do nothing
            return None

        # Deleting the head
        current = self.head
        if current.data == value:
            # Set next node as new head
            self.head = current.next
            # Clear any references to other nodes
            current.next = None
            # Check if we deleted the tail
            if current == self.tail:
                self.tail = None
            return self

        previous = current
        while current is not None:
            # Check the node value
            if current.data == value:
                # Set previous node pointer to next node
                previous.next = current.next
                # Clear any references to other nodes
                current.next = None
                # Check if we deleted the tail
                if current == self.tail:
                    self.tail = previous
                return self
            # Continue down the list
            previous = current
            current = current.next

        raise ValueError("value is not in list")

    # abc.Sequence
    def __getitem__(self, index):
        "Return the value in a given index"
        if self.is_empty:
            raise ValueError("Cannot access element from empty list")

        pos = 0
        node = self.head
        while node:
            if pos == index:
                return node.data
            node = node.next
            pos += 1

        if pos < index:
            raise IndexError("Cannot access index out of range")

    def insert(self, value, index: int):
        "Insert a value in a given index"

        if index == 0:
            return self.append_head(value)
        elif index > 0 and self.is_empty:
            raise IndexError("Inserting on an empty list")

        current = self.head
        current_idx = 0
        while current:
            current_idx += 1
            next_node = current.next
            if current_idx == index:
                new_node = LinkedListNode(value)
                new_node.next = next_node
                current.next = new_node
                if current == self.tail:
                    self.tail = new_node
                return self
            current = next_node

        if current_idx < index:
            raise IndexError("Specified index out of range")

    def pop(self, index: int):
        "Remove the element at index"
        if self.is_empty:
            return None

        current = self.head
        previous = current
        while current:
            if index == 0:
                # Rewrite links
                previous.next = current.next
                # Reset head and tail
                if current is self.tail:
                    self.tail = previous
                if current is self.head:
                    self.head = current.next
                # Detach the node and return value
                return current.pop()
            previous = current
            current = current.next
            index -= 1

        raise IndexError("pop index out of range")

    def distinct(self):
        if self.is_empty:
            return self

        results = set()
        current = self.head
        prev = current
        while current:
            if current.data in results:
                # Remove this node
                next_node = current.next
                current.clear()
                prev.next = next_node
                current = next_node
            else:
                results.add(current.data)
                prev = current
                current = current.next
        return self

    def union(self, list2):
        "Return a list containing elements from both lists"
        # Return other list if one is empty
        if self.is_empty:
            return list2
        if list2.is_empty:
            return self

        # Traverse the list to the tail
        # current = self.head
        # while current.next:
        #     current = current.next

        # Link the last element to the head of other list
        self.tail.next = list2.head
        return self

    def __add__(self, list2):
        return self.union(list2)

    def intersection(self, list2):
        "Return a list containing only elements included in both lists"

        result = LinkedList()
        # Check if either one is empty
        if self.is_empty:
            return result
        if list2.is_empty:
            return result

        # Traverse the list and search in the other
        current = self.head
        while current:
            if current.data in list2:
                result.append_head(current.data)
            current = current.next

        return result.distinct()

    def __and__(self, list2):
        return self.intersection(list2)

    def clear(self):
        self.head = self.tail = None
        return self


class DoublyLinkedList(LinkedList):
    class Node:
        def __init__(self, value):
            self.data = value
            self.next = None
            self.previous = None

        def clear(self):
            del self.data
            del self.previous
            del self.next

        def pop(self):
            "Unwrap and return node value and clear the pointers"
            data = self.data
            self.clear()
            return data

    def __init__(self, items: Iterable = None):
        self.head: DoublyLinkedList.Node = None
        self.tail: DoublyLinkedList.Node = None
        if isinstance(items, Iterable):
            self.extend(items)

    @property
    def is_empty(self):
        return self.head is None

    def append_tail(self, value):
        "Add element to the end of the list"
        new_node = DoublyLinkedList.Node(value)

        # Base case: empty list
        if self.head is None:
            self.head = self.tail = new_node
            return self

        # Append node to the last element
        self.tail.next = new_node
        new_node.previous = self.tail
        # Update tail pointer
        self.tail = new_node
        return self

    def append_head(self, value):
        "Add element to the beginning of the list"
        # Update the head reference
        new_node = DoublyLinkedList.Node(value)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        # Set pointer of next node to new head
        if new_node.next:
            new_node.next.previous = new_node
        return self

    def remove(self, value):
        """
        Remove a value from the list
        """

        if self.is_empty:
            # List is empty, do nothing
            return None

        # Base case: deleting the head node
        current = self.head

        if current.data == value:
            # Set next node as new head
            self.head = current.next
            if self.head:
                self.head.previous = None
            # Check if we deleted the tail
            if current == self.tail:
                self.tail = None
            current.clear()
            return self

        while current is not None:
            # Check the node value
            if current.data == value:
                previous = current.previous
                nxt = current.next
                if nxt:
                    nxt.previous = previous
                previous.next = nxt
                # Check tail
                if current is self.tail:
                    self.tail = previous
                current.clear()
                return self
            # Continue down the list
            current = current.next

    def pop(self, index: int):
        "Remove the element at index"
        if self.is_empty:
            return None

        current = self.head
        while current:
            if index == 0:
                # Rewrite the links
                if current.previous:
                    current.previous.next = current.next
                if current.next:
                    current.next.previous = current.previous
                # Reset head and tail
                if current is self.tail:
                    self.tail = current.previous
                if current is self.head:
                    self.head = current.next
                return current.pop()
            current = current.next
            index -= 1

        raise IndexError("pop index out of range")

    def popright(self):
        if self.tail is None:
            return None

        node = self.tail
        if node.previous:
            node.previous.next = None
        else:
            self.head = None
        self.tail = node.previous
        data = node.data
        node.clear()
        return data

    def popleft(self):
        if self.head is None:
            return None

        node = self.head
        if node.next:
            node.next.previous = None
        else:
            self.tail = None
        self.head = node.next
        data = node.data
        node.clear()
        return data

    def find(self, value):
        # Search from both ends
        tail = self.tail
        head = self.head
        while head and tail:
            # Single node
            if head == tail:
                return tail.data == value
            # Check both ends
            if value == head.data:
                return head
            if value == tail.data:
                return tail
            # Check if the pointers close!
            if head.next == tail:
                return None
            # Move the pointers up
            head, tail = head.next, tail.previous
        return None

    def __contains__(self, value):
        "Check if the list contains a given value"
        return self.find(value) is not None

    # abc.Reversible
    def __reversed__(self) -> Iterator:
        current = self.tail
        while current:
            yield current.data
            current = current.previous

    def reverse(self, inplace=False):
        """Reverse the order of the elements in the list

        inplace: bool
            Set to True to avoid creating a new list and perform in-place reversing instead.
        """
        if not inplace:
            # Create a new linked list and append tails
            other = DoublyLinkedList()
            current = self.head
            while current:
                other.append_head(current.data)
                current = current.next
            return other

        previous = None
        current = self.head
        self.tail = current
        # Iterate through the list and swap the pointers
        while current:
            nxt = current.next
            current.next = current.previous
            current.previous = nxt
            previous = current
            current = nxt
            # Update head
            self.head = previous

        return self

    def insert(self, value, index):
        "Insert a value in a given index"

        if index == 0:
            return self.append_head(value)
        elif index > 0 and self.is_empty:
            raise IndexError("index out of range")

        current = self.head
        current_idx = 0
        while current:
            current_idx += 1
            next_node = current.next
            if current_idx == index:
                new_node = LinkedListNode(value)
                new_node.next = next_node
                current.next = new_node
                return self
            current = next_node

        if current_idx < index:
            raise IndexError("index out of range")
