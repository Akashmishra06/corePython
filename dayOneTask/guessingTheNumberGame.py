# #### 10. **Guess the Number Game**
# - Generate a random number between 1 to 100 and let the user guess until they get it right.

import random

computerChoice = random.randint(1, 100)

while True:
    youGuess = int(input("Enter the number: "))
    
    if youGuess == computerChoice:
        print("🎉 You won! 🎉")
        break
    elif youGuess < computerChoice:
        print(f"Your choice is: {youGuess} — Too low, try again.")
    else:
        print(f"Your choice is: {youGuess} — Too high, try again.")