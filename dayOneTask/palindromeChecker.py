# #### 7. **Palindrome Checker**
# - Check whether a given string is a palindrome (reads the same forwards and backwards).

checkString = "madannm"
reverseString = checkString[::-1]

isPalindrome = reverseString == checkString

print(f"isPalindrome: {isPalindrome}")