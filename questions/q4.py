# Simple Calculator

# Write a program that takes two numbers and performs addition, subtraction, multiplication, and division on them.

num1 = int(input("Enter the value of num1: "))
num2 = int(input("Enter the valuue of num2: "))

def PerformingTasks(num1, num2):
    addition = num1 + num2
    subtraction = num1 - num2
    multiplication = num1 * num2
    division = num1 // num2

    outputString = f"addition of num1 and num2 is: {addition}\nsubtraction os num1 and num2 is: {subtraction}\nmultiplication of num1 and num2 is: {multiplication}\ndivision of num1 and num2 is: {division}"

    return outputString

results = PerformingTasks(num1, num2)
print(results)