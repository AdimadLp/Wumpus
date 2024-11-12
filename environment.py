# FILE: environment.py


class Environment:
    def __init__(self, size):
        self.size = size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.place_wumpus()
        self.place_pits()
        self.place_gold()

    def place_wumpus(self):
        # Logic to place Wumpus in the grid
        pass

    def place_pits(self):
        # Logic to place pits in the grid
        pass

    def place_gold(self):
        # Logic to place gold in the grid
        pass

    def display(self):
        for row in self.grid:
            print(" ".join(row))


class Wumpus:
    pass


class Pit:
    pass


class Gold:
    pass
