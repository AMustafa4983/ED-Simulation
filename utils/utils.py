import random

priority_order = ["Very High", "High", "Medium", "Low", "Very Low"]

def generate_id(count: int):
    start_number = int("1"+("0" * count))
    end_number = int("9" * (count+1))

    random_number = random.randint(start_number, end_number)

    return random_number

def generate_random_between_two(start, end):

    random_number = random.randint(start, end)

    return random_number

def sort_by_priority(objects):
    priority_dict = {value: index for index, value in enumerate(priority_order)}
    sorted_objects = sorted(objects, key=lambda obj: priority_dict[obj.getPriorityLevel()])

    return sorted_objects