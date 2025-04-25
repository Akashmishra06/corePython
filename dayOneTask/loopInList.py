# #### 12. **Find the Largest Number in a List**
# - Without using `max()`, find the largest number in a list.

list1 = [11, 12, 19, 2, 858585, 0, 555, 855]

itere = list1[0]

for value in list1:
    if itere < value:
        itere = value

print(itere) 