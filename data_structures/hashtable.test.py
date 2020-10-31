from hashtable import HashTable

table = HashTable()
table["This"] = 1
table["is"] = 2
table["a"] = 3
table["Test"] = 4
table["Driver"] = 5
print("Table size: ", len(table))
assert 'is' in table
print("map['is']: ", table['is'])
del table['is']
del table['a']
assert 'is' not in table
assert 'a' not in table
print("Table size: ", len(table))
print(table._buckets)
print(list(table.keys()))
print(list(table.values()))
print(list(table.items()))
assert True
