# #### 3. **Even or Odd**
# - Take a number as input and check whether it is even or odd.

number = int(input("Please Enter a Number: "))

if number == 0:
    print("number is zero")

elif (number % 2) == 0:
    print(f"{number} is Even Number")

else:
    print(f"{number} is Odd Number")