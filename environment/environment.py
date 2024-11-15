# FILE: environment/environment.py
import random
from .field import Field
from .wumpus import Wumpus
from .pit import Pit
from .gold import Gold


def moore_neighborhood(x, y, size, multiplier):
    neighbors = []
    for dx in range(-multiplier, multiplier + 1):
        for dy in range(-multiplier, multiplier + 1):
            if dx == 0 and dy == 0:
                continue
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < size and 0 <= new_y < size:
                neighbors.append((new_x, new_y))
    return neighbors


def neumann_neighborhood(x, y, size, multiplier):
    neighbors = []
    for dx in range(-multiplier, multiplier + 1):
        for dy in range(-multiplier, multiplier + 1):
            if (dx == 0 and dy == 0) or (dx != 0 and dy != 0):
                continue
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < size and 0 <= new_y < size:
                neighbors.append((new_x, new_y))
    return neighbors


class Environment:
    def __init__(self, size):
        self.size = size
        self.grid = [[Field() for _ in range(size)] for _ in range(size)]
        self.number_of_wumpus = 1
        self.number_of_pits = 0
        self.number_of_gold = 0
        self.place_entities()

    def generate_random_position(self):
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        return x, y

    def place_entities(self):
        for _ in range(self.number_of_wumpus):
            self.place_wumpus(*self.generate_random_position())
        for _ in range(self.number_of_gold):
            self.place_gold(*self.generate_random_position())
        for _ in range(self.number_of_pits):
            self.place_pits(*self.generate_random_position())

    def place_wumpus(self, x, y):
        field = self.grid[x][y]
        if field.entity is None:
            field.entity = Wumpus()
            field.entity.position = (x, y)
            perception_fields = neumann_neighborhood(
                x, y, self.size, field.entity.perception_multiplier
            )
            field.entity.assign_perception_fields(perception_fields)
            for px, py in perception_fields:
                self.grid[px][py].perceptions.append(field.entity.percept)

    def place_pits(self, x, y):
        if self.grid[x][y].entity is None:
            self.grid[x][y].entity = Pit()
            self.grid[x][y].entity.perceive(x, y, self.size)

    def place_gold(self, x, y):
        if self.grid[x][y].entity is None:
            self.grid[x][y].entity = Gold()

    def remove_entity(self, entity):
        x, y = entity.position
        for px, py in self.grid[x][y].entity.perception_fields:
            self.grid[px][py].perceptions.remove(self.grid[x][y].entity.percept)
        self.grid[x][y].entity = None
