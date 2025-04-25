# #### 14. **Word Frequency Counter**
# - Count how many times each word appears in a sentence using a dictionary.

stringOne = "I love coding and I love Python"

newstrin = stringOne.split()

myNewDict = {}

for string in newstrin:

    if string in myNewDict:
        myNewDict[string] += 1
    else:
        myNewDict[string] = 1

print(myNewDict)