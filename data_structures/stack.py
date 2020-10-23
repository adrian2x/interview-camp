""" A stack implementation using a list
"""

class Stack():
    "A Stack collection implemented with a list"

    def __init__(self):
        "Make a new stack"
        self.stack_list = []

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


#######################################################
###  Stack tests
#######################################################
stack = Stack()
for i in range(5):  # Pushing values in
    stack.push(i)

print("top(): " + str(stack.top()))

for x in range(5):  # Removing values
    print(stack.pop())

print("is_empty(): " + str(stack.is_empty))
