# #### 15. **Simple Contact Book**
# - Create a mini contact book where the user can add, view, and delete contacts using a dictionary.

# contact = int(input("Please Enter the contact Number: "))
# EnterTheKey = input("Enter the Key if want to add else pass 0: ")
# myDict = {}

# myDict[contact] = contact

# print(myDict[contact])
# myDict.pop(contact)
# print(myDict)

# if EnterTheKey != "0":
#     newKey = input("value of key: ")
#     newValue = input("value of key: ")
#     myDict[newKey] = newValue
#     print(myDict)


# Simple Contact Book using match-case (Python 3.10+)

myDict = {}

while True:
    print("\nContact Book Menu:")
    print("1. Add Contact")
    print("2. View Contacts")
    print("3. Delete Contact")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    match choice:
        case "1":
            name = input("Enter contact name: ")
            number = input("Enter contact number: ")
            myDict[name] = number
            print(f"✅ Contact '{name}' added successfully.")

        case "2":
            if myDict:
                print("\n📒 Contact List:")
                for name, number in myDict.items():
                    print(f"{name}: {number}")
            else:
                print("⚠️ No contacts to display.")

        case "3":
            name = input("Enter contact name to delete: ")
            if name in myDict:
                del myDict[name]
                print(f"🗑️ Contact '{name}' deleted.")
            else:
                print(f"❌ Contact '{name}' not found.")

        case "4":
            print("👋 Exiting Contact Book. Bye!")
            break

        case _:
            print("❗ Invalid choice. Please select 1, 2, 3, or 4.")
