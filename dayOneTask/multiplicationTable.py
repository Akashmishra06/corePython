### 8. **Multiplication Table**
# - Print the multiplication table (1 to 10) of a number entered by the user.

number1 = int(input("Please Enter the value of number1: "))

for i in range(1, 11):
    print(f"{number1} * {i} = {number1 * i}")