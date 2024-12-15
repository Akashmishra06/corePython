nums = [2, 4, 6, 8, 9, 0, 1]
target = 10

for i in range(len(nums) - 1):
    if nums[i] + nums[i + 1] == target:
        print(i, i + 1)