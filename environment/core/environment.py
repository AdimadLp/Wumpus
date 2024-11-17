# FILE: environment/environment.py
import random
from environment.core.cell import Cell
from environment.entities import Entity, Wumpus, Pit, Gold, Agent

class Environment:
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.entities = []
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
            self.place_entity(Wumpus, *self.generate_random_position())
        for _ in range(self.number_of_gold):
            self.place_entity(Gold, *self.generate_random_position())
        for _ in range(self.number_of_pits):
            self.place_entity(Pit, *self.generate_random_position())
        self.place_entity(Agent, *self.generate_random_position())

    def place_entity(self, entity_type, x, y):
        cell = self.grid[x][y]
        if cell.entity is None:
            entity = entity_type(self, (x, y))
            cell.set_entity(entity)
            self.entities.append(entity)
            self.update_perceptions(entity)

    def update_perceptions(self, entity):
        entity.calculate_perception_fields()
        for px, py in entity.perception_fields:
            self.grid[px][py].perceptions.append(entity.perception_type)

    def remove_entity(self, entity):
        x, y = entity.position
        cell = self.grid[x][y]
        for px, py in cell.entity.perception_fields:
            self.grid[px][py].perceptions.remove(cell.entity.perception_type)
        self.entities.remove(entity)
        cell.remove_entity()