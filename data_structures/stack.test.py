import random

from stack import Stack


stack = Stack()
for i in range(5):  # Pushing values in
    stack.push(i)
    assert i in stack

print(stack)
print("top(): " + str(stack.top()))

for x in range(5):  # Removing values
    stack.pop()

print("is_empty(): " + str(stack.is_empty))

###################################################
##  Queue using two Stacks
###################################################
temp_stack = Stack()
main_stack = Stack()


def enqueue(item):
    main_stack.push(item)
    print(str(item) + " enqueued")


def dequeue():
    if temp_stack.is_empty:
        # Transfer all elements to temp stack
        if main_stack.is_empty:
            return None
        while not main_stack.is_empty:
            temp_stack.push(main_stack.pop())
    # Pop from temp stack
    last = temp_stack.pop()
    print(str(last) + " dequeued")
    return last


for i in range(5):
    enqueue(i + 1)

print("----------")

for i in range(5):
    assert dequeue() == i + 1


#################################################
##  Sort values in a stack
#################################################
def sort_stack(stack: Stack):
    # Use a temp stack that will hold values in descending order
    tmp = Stack()  # temp stack

    while not stack.is_empty:
        value = stack.pop()

        # if value is larger than tmp, push it
        if tmp.is_empty or value >= tmp.top():
            tmp.push(value)
        else:
            while not tmp.is_empty and tmp.top() > value:
                stack.push(tmp.pop())
            tmp.push(value)

    # Note all elements are now in tmp (desc order)
    # to sort ascending, just move to the other stack
    while not tmp.is_empty:
        stack.push(tmp.pop())

    return stack


def _sort_stack(stack: Stack):
    # Recursive version
    if not stack.is_empty:
        value = stack.pop()
        _sort_stack(stack)
        insert(stack, value)
    return stack


def insert(stack, value):
    if stack.is_empty or value < stack.top():
        stack.push(value)
    else:
        top = stack.pop()
        insert(stack, value)
        stack.push(top)


stack = Stack()
for i in range(5):  # Pushing values in
    stack.push(random.randint(1, 100))

print("Sorting:", stack)
print(sort_stack(stack))
print(_sort_stack(stack))


################################################
##  Evaluate post-fix expr
################################################
def eval_postfix(exp: str):
    stack = Stack()
    try:
        for c in exp:
            if c.isdigit():
                stack.push(c)
            else:
                # some operand, use top two numbers
                right = stack.pop()
                left = stack.pop()
                stack.push(str(eval(f"{left} {c} {right}")))
        # final answer
        return float(stack.pop())
    except:
        return "Invalid sequence"


operation = "921*-8-4+"
print("Sequence:", operation)
print(">>>", eval_postfix(operation))
print(">>>", eval_postfix("921*-8--4+"))


################################################
##  Next Greater Element
################################################
def next_greater(items):
    stack = Stack()
    result = [-1] * len(items)
    # Iterate the list in reverse
    for i in range(len(items) - 1, -1, -1):
        value = items[i]
        # Pop all elements from the stack < current value
        while not stack.is_empty and stack.top() <= value:
            stack.pop()
        # The top element will be > ith value
        if not stack.is_empty:
            result[i] = stack.top()
        # Push current value in stack
        stack.push(value)

    return result


lst = next_greater([4, 6, 3, 2, 8, 1, 9, 9, 9])
print(lst)


################################################
##  Stack.min()
################################################
class MinStack:
    def __init__(self, iterable=()):
        self.main_stack = []
        self.min_stack = Stack()
        for value in iterable:
            self.push(value)

    def pop(self):
        top = self.main_stack[-1]
        # Check if we're removing the min
        if top == self.min_stack.top():
            self.min_stack.pop()
        return self.main_stack.pop()

    def push(self, value):
        # If there is a new min, push to min_stack
        if self.min_stack.is_empty or value < self.min_stack.top():
            self.min_stack.push(value)
        self.main_stack.append(value)

    def min(self):
        "Return the minimum in O(1)"
        return self.min_stack.top()


min_stack = MinStack([9, 3, 1, 4])
assert min_stack.min() == 1
min_stack.pop()
min_stack.pop()
assert min_stack.min() == 3
min_stack.pop()
assert min_stack.min() == 9

min_stack = MinStack([5, 10, 6, 23, 2])
assert min_stack.min() == 2
min_stack.pop()
assert min_stack.min() == 5

min_stack = MinStack([5, 0, 2, 4, 1, 3, 0])
assert min_stack.min() == 0
