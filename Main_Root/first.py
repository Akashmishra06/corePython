# def get_choices():

#     playerChoice = "rock"
#     computerChoice = "paper"

#     return playerChoice, computerChoice

# choices = get_choices()
# print(choices)
# print(type(get_choices()))


# Function to print full pyramid pattern
def full_pyramid(n):
    for i in range(1, n + 1):
        # Print leading spaces
        for j in range(n - i):
            print(" ", end="")
        
        # Print asterisks for the current row
        for k in range(1, 2*i):
            print("*", end="")
        print()

full_pyramid(5)