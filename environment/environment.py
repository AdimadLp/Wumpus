# FILE: environment/environment.py
import random
from environment.cell import Cell
from environment.entities import Wumpus, Pit, Gold, Agent


class Environment:
    """
    A class to represent the game environment.

    Attributes:
    -----------
    size : int
        The size of the environment grid passed from the main file.
    cell_size : int
        The size of each cell in the grid passed from the main file.
    grid : list
        A 2D list representing the grid of cells.
    entities : list
        A list to keep track of all entities in the environment.
    entity_counts : dict
        A dictionary to specify the number of each type of entity.
    """

    def __init__(self, size, cell_size):
        """
        Initialize the Environment class and place entities in the grid.

        Parameters:
        -----------
        size : int
            The size of the environment grid.
        cell_size : int
            The size of each cell in the grid.
        """
        self.size = size
        self.cell_size = cell_size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.entities = []
        # Entities defined first will be placed first
        self.entity_counts = {Wumpus: 3, Gold: 10, Pit: 10, Agent: 5}

        self.place_entities()

        # pre-determined test field:
        # self.place_entity(Agent, 0, 0)
        # self.place_entity(Agent, 3, 0)
        # self.place_entity(Wumpus, 1, 0)
        # self.place_entity(Wumpus, 0, 3)
        # self.place_entity(Pit, 2, 0)
        # self.place_entity(Pit, 4, 0)
        # self.place_entity(Gold, 0, 3)

    def generate_random_position(self):
        """
        Generate a random position within the grid.

        Returns:
        --------
        tuple
            A tuple representing the (x, y) position.
        """
        x = random.randint(0, self.size - 1)
        y = random.randint(0, self.size - 1)
        return x, y

    def place_entities(self):
        """
        Place entities randomly in the grid.
        """
        # Check if the total number of entities is greater than the total number of cells
        total_cells = self.size * self.size
        total_entities = sum(self.entity_counts.values())
        if total_entities > total_cells:
            raise ValueError("Too many entities for the environment size")

        # Place number of entities in the grid
        for entity_type, count in self.entity_counts.items():
            placed = 0
            while placed < count:
                x, y = self.generate_random_position()
                if self.grid[x][y].entity is None:
                    self.place_entity(entity_type, x, y)
                    placed += 1

    def place_entity(self, entity_type, x, y):
        """
        Place a single entity in the grid.

        Parameters:
        -----------
        entity_type : type
            The type of the entity to place.
        x : int
            The x-coordinate of the position.
        y : int
            The y-coordinate of the position.
        """
        cell = self.grid[x][y]
        # Check if the cell is empty
        if cell.entity is None:
            entity = entity_type(self, (x, y))
            cell.set_entity(entity)
            self.entities.append(entity)
            self.update_perceptions(entity)

    def update_perceptions(self, entity):
        """
        Update the perception fields of an entity.

        Parameters:
        -----------
        entity : Entity
            The entity whose perception fields need to be updated.
        """
        entity.calculate_perception_fields()
        for px, py in entity.perception_fields:
            self.grid[px][py].perceptions.append(entity.perception_type)

    def remove_entity(self, entity):
        """
        Remove an entity from the grid.

        Parameters:
        -----------
        entity : Entity
            The entity to remove.
        """
        x, y = entity.position
        cell = self.grid[x][y]
        for px, py in cell.entity.perception_fields:
            self.grid[px][py].perceptions.remove(cell.entity.perception_type)
        self.entities.remove(entity)
        cell.remove_entity()

    def get_all_agents_in_range(self, position, range=None):
        """
        Get all agents within a specified range of a position.

        Parameters:
        -----------
        position : tuple
            The (x, y) position to check around.
        range : int, optional
            The range to check within. If None, the range is the whole environment.

        Returns:
        --------
        list
            A list of agents within the specified range.
        """
        if range is None:
            range = self.size

        x, y = position
        agents = []
        # Iterate over all cells in the range
        for dx in range(-range, range + 1):
            for dy in range(-range, range + 1):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.size and 0 <= new_y < self.size:
                    cell = self.grid[new_x][new_y]
                    if cell.entity and cell.entity.entity_type == "Agent":
                        agents.append(cell.entity)
        return agents

    def vote(self):
        # Count how many agents are alive
        # Mehrheit gewinnt
        pass
