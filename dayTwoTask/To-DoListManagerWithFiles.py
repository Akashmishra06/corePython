# #### 1. **To-Do List Manager (With File Save)**
# - Add, delete, and view tasks.
# - Save/load tasks from a text file.

filePlace = "/workspaces/corePython/dayTwoTask"

# 1-view
# 2-save
# 3-load 
# 4-delete

chooseOne = int(input("Please Enter your choice(1, 2, 3, 4): "))
with open(filePlace, 'w') as file:
    file.write(f"")