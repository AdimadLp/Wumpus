# FILE: environment/environment.py
import random
from .wumpus import Wumpus

class Environment:
    def __init__(self, size):
        self.size = size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.place_wumpus()
        self.place_pits()
        self.place_gold()

    def place_wumpus(self):
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        self.grid[x][y] = "W"

    def place_pits(self):
        # Logic to place pits in the grid
        pass

    def place_gold(self):
        # Logic to place gold in the grid
        pass