import random

from stack import Stack


stack = Stack()
for i in range(5):  # Pushing values in
    stack.push(i)

print("top(): " + str(stack.top()))

for x in range(5):  # Removing values
    print(stack.pop())

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
def evaluate_postfix(exp: str):
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
print(">>>", evaluate_postfix(operation))
print(">>>", evaluate_postfix("921*-8--4+"))
