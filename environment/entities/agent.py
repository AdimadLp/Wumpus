# FILE: agent/agent.py
from dataclasses import dataclass, field
from .entity import Entity


@dataclass
class Agent(Entity):
    entity_type: str = "Agent"
    image_paths: dict = field(default_factory=lambda: {
        "front": "src/agent/front.png",
        "right": "src/agent/right.png",
        "left": "src/agent/left.png",
        "back": "src/agent/back.png",
    })
    reward: int = 0
    perception_range_multiplier: int = 1
    current_image_key: str = "front"
    score: int = 0
    auto_mode: bool = False

    def perceive(self):
        # Logic for the agent to perceive its surroundings
        x, y = self.position
        field = self.environment.grid[x][y]
        if field.perceptions:
            print("Agent perceives:", field.perceptions)
            return field.perceptions

        return []

    def decide(self):
        # Logic for the agent to make decisions based on perceptions
        pass

    def act(self):
        # Logic for the agent to act based on decisions
        pass

    def can_move(self, direction):
        x, y = self.position
        if direction == "right":
            return x < self.environment.size - 1
        elif direction == "left":
            return x > 0
        elif direction == "back":
            return y > 0
        elif direction == "front":
            return y < self.environment.size - 1
        else:
            raise ValueError("Invalid direction")

    def check_for_wumpus(self, position):
        x, y = position
        cell = self.environment.grid[x][y]
        if cell.entity:
            if cell.entity.entity_type == "Wumpus":
                self.die()
                return True
        return False
    
    def attack(self):
        x, y = self.position
        field = self.environment.grid[x][y]
        # Check if the field where the agent directly looks at has a Wumpus
        if self.direction == "right" and x + 1 < self.environment.size:
            field = self.environment.grid[x + 1][y]
        elif self.direction == "left" and x - 1 >= 0:
            field = self.environment.grid[x - 1][y]
        elif self.direction == "back" and y - 1 >= 0:
            field = self.environment.grid[x][y - 1]
        elif self.direction == "front" and y + 1 < self.environment.size:
            field = self.environment.grid[x][y + 1]
        else:
            return
        
        if field.entity and field.entity.entity_type == "Wumpus":
            self.score += field.entity.die()
            print("Agent has killed a Wumpus!")
            return

    def move(self, direction):
        if not self.can_move(direction):
            raise IndexError("Agent would go out of the environment")

        x, y = self.position
        if direction == "right":
            new_position = (x + 1, y)
        elif direction == "left":
            new_position = (x - 1, y)
        elif direction == "back":
            new_position = (x, y - 1)
        elif direction == "front":
            new_position = (x, y + 1)

        # Check if the new position has a Wumpus
        if self.check_for_wumpus(new_position):
            self.alive = False
            return

        # Update the grid
        self.environment.grid[x][y].remove_entity()
        self.environment.grid[new_position[0]][new_position[1]].entity = self

        self.position = new_position
        self.perceive()