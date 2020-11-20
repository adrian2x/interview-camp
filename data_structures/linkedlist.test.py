from linkedlist import LinkedList, DoublyLinkedList


lst = LinkedList()
print(lst)

print("Inserting values in list")
for i in range(1, 10):
    lst.append_head(i)
print(lst)

lst = LinkedList()
print(lst)
lst.append_tail(0)
assert lst.tail == lst.head
assert 0 in lst
print(lst)
lst.append_tail(1)
assert 1 in lst
print(lst)
lst.append_tail(2)
assert 2 in lst
print(lst)
lst.append_tail(3)
assert lst.tail.data == 3
print(lst)

print(">>> Inserting 4 at index 3")
lst.insert(4, 3)
print(lst)
assert 4 in lst

##########################################
##  Remove duplicates
##########################################

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

##########################################
##  Union & Intersection
##########################################

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
assert len(new_list) == 6

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
assert len(lst) == 2
print(">>> Intersect list1 & list2")
print(lst)

##########################################
##  DoublyLinkedList Tests
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

##########################################
##  Reverse LinkedList
##########################################
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

print("Pop elements")
assert lst.popleft() == 5
print(lst)
assert lst.popright() == 1
print(lst)
assert lst.popleft() == 3
print(lst)

lst.append_tail(3)
lst.insert(1, 0)
print(lst)
assert lst.pop(2) == 3
assert lst.tail.data == 2
assert lst.pop(1) == 2
assert lst.tail == lst.head
assert lst.pop(0) == 1
assert lst.tail is None
assert lst.is_empty
