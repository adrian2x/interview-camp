import array

# type code, type, min bytes
# 'c', char, 1
"""  Type code, Type, Min bytes
     'c'        char              1
     'b'        int (signed)      1
     'B'        int (unsigned)    1
     'u'        unicode char      2
     'h'        short (signed)    2
     'H'        short (unsigned)  2
     'i'        int (signed)      2
     'I'        int (unsigned)    4
     'l'        long (signed)     4
     'L'        long (unsigned)   4
     'f'        float             4
     'd'        double            8
"""
new_array = array.array("d", [1, 2, 3])
print(new_array[0])

integers = array.array("i", [1, 2, 3, 5, 7, 10])

# changing first element
integers[0] = 0
print(integers)  # array('i', [0, 2, 3, 5, 7, 10])

# changing 3rd to 5th element
integers[2:5] = array.array("i", [4, 6, 8])
print(integers)

" Just as with lists, we can add one item to the end of an array using the append() method or add several items using the extend() method."

numbers = array.array("i", [1, 2, 3])

numbers.append(4)
print(numbers)  # array('i', [1, 2, 3, 4])

# extend() appends iterable to the end of the array
numbers.extend([5, 6, 7])
print(numbers)  # array('i', [1, 2, 3, 4, 5, 6, 7])

odd = array.array("i", [1, 3, 5])
even = array.array("i", [2, 4, 6])

integers = array.array("i")  # creating empty array of integer
integers = odd + even

print(integers)


" To delete one or more items from an array, use the `del` statement as with lists."
integer_array = array.array("i", [1, 2, 3, 3, 4])

del integer_array[2]  # removing third element
print(integer_array)  # Output: array('i', [1, 2, 3, 4])

del integer_array  # deleting entire array

" We can use the remove(val) method to remove the given item or pop(index) to remove an item at the given index. The remove(val) method removes the first element that is equal to val in the array."

integer_array = array.array("i", [10, 11, 12, 12, 13])

integer_array.remove(12)
print(integer_array)  # array('i', [10, 11, 12, 13])

print(integer_array.pop(2))  # Output: 12
print(integer_array)  # array('i', [10, 11, 13])
