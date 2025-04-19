# #### 9. **Fibonacci Series**
# - Generate the first N numbers of the Fibonacci series.

getNumber = int(input("Please Enter the number: "))
list1 = []
for i in range((getNumber)):
    if len(list1) == 0:
        list1.append(0)
    elif len(list1) == 1:
        list1.append(1)
    elif len(list1) >= 2:
        list1.append((list1[-1]+list1[-2]))

print(list1)