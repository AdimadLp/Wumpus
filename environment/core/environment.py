# FILE: environment/environment.py
import random
from environment.core.cell import Cell
from environment.entities import Wumpus, Pit, Gold, Agent


class Environment:
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.entities = []
        self.entity_counts = {Agent: 2, Wumpus: 2, Gold: 0, Pit: 0}
        self.place_entities()

    def generate_random_position(self):
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        return x, y

    def place_entities(self):
        total_cells = self.size * self.size
        total_entities = sum(self.entity_counts.values())
        if total_entities > total_cells:
            raise ValueError("Too many entities for the environment size")

        for entity_type, count in self.entity_counts.items():
            placed = 0
            while placed < count:
                x, y = self.generate_random_position()
                if self.grid[x][y].entity is None:
                    self.place_entity(entity_type, x, y)
                    placed += 1

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
