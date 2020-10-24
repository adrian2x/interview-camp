from collections.abc import Sequence, Iterable

from linked_list import DoublyLinkedList


class Queue():
    "A Queue is a First-In-First-Out sequence of items."
    def __init__(self, items: Iterable = None, **kwargs):
        self.queue_list = DoublyLinkedList(items)

    @property
    def is_empty(self):
        return self.queue_list.is_empty

    def front(self):
        if self.is_empty:
            return None
        return self.queue_list.head.data

    def back(self):
        if self.is_empty:
            return None
        return self.queue_list.tail.data

    def size(self):
        return len(self.queue_list)

    def enqueue(self, item):
        self.queue_list.append_tail(item)

    def dequeue(self):
        if self.is_empty:
            raise ValueError("Cannot remove element from empty queue")
        front = self.front()
        self.queue_list.remove(front)
        return front



if __name__ == "__main__":
    ######################################################################
    ###  Queue tests
    ######################################################################
    queue = Queue()

    queue.enqueue(2)
    queue.enqueue(4)
    queue.enqueue(6)
    queue.enqueue(8)
    queue.enqueue(10)

    print("Dequeue(): " + str(queue.dequeue()))
    print("Dequeue(): " + str(queue.dequeue()))

    print("front(): " + str(queue.front()))
    print("back(): " + str(queue.back()))

    queue.enqueue(12)
    queue.enqueue(14)

    while queue.is_empty is False:
        print("Dequeue(): " + str(queue.dequeue()))

    print("is_empty: " + str(queue.is_empty))
