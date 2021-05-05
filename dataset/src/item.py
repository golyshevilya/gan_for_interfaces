import random


class Item:
    """
    A class that is intended for setting parameters for class objects in a future dataset
    """
    def __init__(self, name_, count_):
        self.name = name_
        self.count = count_
        if 'button' in name_:
            self.size_start = 60, 60
            self.current_size = [60, 60]
            self.size_finish = 120, 120
            self.count_of_position = 5
            random.seed()
            self.current_position = random.randrange(1, self.count_of_position, 1)
            self.orientation = 0  # random.randrange(0, 2, 1)
            self.step_change_size = 20
