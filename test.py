#! /usr/bin/python3

def twoSum(nums, target):
    
    for index, item in enumerate(nums):
        for index_2 in range(index + 1, len(nums)):
            if nums[index] + nums[index_2] == target:
                return [index, index_2]
    
    
nums = [2,7,11,15]
target = 3

indices = twoSum(nums, target)
print('aaa', indices)