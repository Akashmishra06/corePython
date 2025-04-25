# #### 13. **Remove Duplicates from a List**
# - Remove duplicate items from a list using a loop.

listuse = [2323, 23, 23, 23,34, 344]

newList = []
for i in listuse:

    if i not in newList:
        newList.append(i)
    
print(newList)