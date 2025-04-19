# #### 6. **Count Vowels**
# - Write a program to count the number of vowels in a string.

stringOfVowels = "enqsiiiicplisreou"
vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']

numberOfVowels = 0
listUd = []

for i in stringOfVowels:
    if i in vowels and i not in listUd:
        numberOfVowels += 1
        listUd.append(i)

print(numberOfVowels)
del(listUd)