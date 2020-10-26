""" A stack implementation using a list
"""


class Stack:
    "A Stack collection implemented with a list"

    def __init__(self, items=()):
        "Make a new stack"
        self.stack_list = []
        for item in items:
            self.push(item)

    def push(self, item):
        "Add an element to the top of the stack"
        self.stack_list.append(item)

    def pop(self):
        "Remove and return the top element in the stack"
        if self.is_empty:
            return None
        return self.stack_list.pop()

    @property
    def is_empty(self):
        "Check if the stack is empty"
        return len(self.stack_list) == 0

    def top(self):
        "Return the top element in the stack"
        if self.is_empty:
            return None
        return self.stack_list[-1]

    def __len__(self):
        return len(self.stack_list)

    def pop_each(self):
        "Returns an iterator that pops each item from the stack"
        while not self.is_empty:
            value = self.pop()
            yield value

    def __iter__(self):
        "Iterate the stack top to bottom"
        return reversed(self.stack_list)

    def __str__(self):
        return str([x for x in self])
