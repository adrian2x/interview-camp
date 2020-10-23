"LinkedList is a collection of nodes"


class LinkedListNode():
    "Represents a single node in a LinkedList"
    def __init__(self, data):
        self.data = data
        self.next = None

    def detach(self):
        del self.data
        del self.next


class LinkedList():
    "A linked list is formed by nodes which are linked together like a chain."
    def __init__(self):
        self.head = None

    def __str__(self, end=" -> "):
        "Print the list"
        value = ""
        if self.is_empty:
            return "head" + end + "nil"
        temp = self.head
        while temp.next is not None:
            value += str(temp.data) + end
            temp = temp.next
        value += str(temp.data) + end + "nil"
        return value

    def append_tail(self, value):
        "Add element to the end of the list"

        # Base case: empty list
        if self.head is None:
            self.head = LinkedListNode(value)
            return self

        # Find the last element
        slot = self.head
        while slot.next is not None:
            slot = slot.next
        # Append node to the last element
        slot.next = LinkedListNode(value)
        return self

    def append_head(self, value):
        "Add element to the beginning of the list"
        # Update the head reference
        node = self.head
        self.head = LinkedListNode(value)
        self.head.next = node
        return self

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
            # Clear any references to other nodes
            current.next = None
            return self

        previous = current
        while current is not None:
            # Check the node value
            if current.data == value:
                # Set previous node pointer to next node
                previous.next = current.next
                # Clear any references to other nodes
                current.next = None
                return self
            # Continue down the list
            previous = current
            current = current.next

    def insert(self, value, index):
        "Insert a value in a given index"

        if index == 0:
            return self.append_head(value)
        elif index > 0 and self.is_empty:
            raise IndexError('Inserting on an empty list')

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
            raise IndexError('Specified index is out of bounds')

    @property
    def is_empty(self):
        return self.head is None

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
                current.detach()
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
        current = self.head
        while current.next:
            current = current.next

        # Link the last element to the head of other list
        current.next = list2.head
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


class DoublyLinkedList(LinkedList):
    class Node():
        def __init__(self, value):
            self.data = value
            self.next = None
            self.previous = None

        def detach(self):
            del self.data
            del self.previous
            del self.next
            return self

    def __init__(self):
        self.head: DoublyLinkedList.Node = None
        self.tail: DoublyLinkedList.Node = None

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
            current.detach()
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
                current.detach()
                return self
            # Continue down the list
            current = current.next

    def __len__(self):
        count = 0
        head = self.head
        while head is not None:
            count += 1
            head = head.next
        return count

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
            raise IndexError(f'Invalid index {index} on an empty list.')

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
            raise IndexError(f'Index {index} out of bounds (size {current_idx + 1})')



##########################################
###  LinkedList Tests
##########################################
lst = LinkedList()
print(lst)

print("Inserting values in list")
for i in range(1, 10):
    lst.append_head(i)
print(lst)


lst = LinkedList()
print(lst)
lst.append_tail(0)
print(lst)
lst.append_tail(1)
print(lst)
lst.append_tail(2)
print(lst)
lst.append_tail(3)
print(lst)

print(">>> Inserting 4 at index 3")
lst.insert(4, 3)
print(lst)
assert 4 in lst

print(">>> List with duplicates")
# Test duplicates
lst = LinkedList()
lst.append_head(7)
lst.append_head(7)
lst.append_head(7)
lst.append_head(22)
lst.append_head(14)
lst.append_head(21)
lst.append_head(14)
lst.append_head(7)

print(lst)
lst = lst.distinct()
print(lst)


print(">>> Union & Intersection")
ulist1 = LinkedList()
ulist2 = LinkedList()
ulist1.append_head(8)
ulist1.append_head(22)
ulist1.append_head(15)

print(">>> List 1")
print(ulist1)

ulist2.append_head(21)
ulist2.append_head(14)
ulist2.append_head(7)

print(">>> List 2")
print(ulist2)

new_list = ulist1 + ulist2

print(">>> Union of list 1 and 2")
print(new_list)

ilist1 = LinkedList()
ilist2 = LinkedList()

ilist1.append_head(14)
ilist1.append_head(22)
ilist1.append_head(15)

ilist2.append_head(21)
ilist2.append_head(14)
ilist2.append_head(15)

lst = ilist1 & ilist2
print(">>> Intersect list1 & list2")
print(lst)


##########################################
###  DoublyLinkedList Tests
##########################################
print(">>> Doubly Linked Lists")
lst = DoublyLinkedList()
lst.append_tail(1)
lst.append_tail(2)
lst.append_tail(3)
lst.append_tail(4)
lst.append_tail(5)
print(lst)
print("Deleting 4")
lst.remove(4)
assert 4 not in lst
print(lst)
print("List size:", len(lst))

print("Reverse list")
tail = lst.tail
lst.reverse(inplace=True)
assert lst.head == tail
assert lst.tail.data == 1
assert len(lst) > 0
assert 5 in lst
assert 3 in lst
assert 2 in lst
assert 1 in lst
print(lst)
