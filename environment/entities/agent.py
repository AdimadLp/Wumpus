# FILE: agent/agent.py
from dataclasses import dataclass, field
from .entity import Entity


@dataclass
class Agent(Entity):
    entity_type: str = "Agent"
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/agent/front.png",
            "right": "src/agent/right.png",
            "left": "src/agent/left.png",
            "back": "src/agent/back.png",
        }
    )
    reward: int = 0
    perception_range_multiplier: int = 0
    current_image_key: str = "front"
    score: int = 0
    auto_mode: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.reveal_initial_cell()

    def reveal_initial_cell(self):
        x, y = self.position
        cell = self.environment.grid[x][y]
        cell.reveal()

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

    def interact(self, agent, interaction_type="neutral"):
        if interaction_type == "neutral":
            print("There is already an Agent in this cell!")
            return False
        elif interaction_type == "attack":
            print("Agent attacking another Agent!")
            return False

    def interact_with_entity(self, entity):
        return entity.interact(self)

    def get_new_position_and_check_bounds(self, direction):
        x, y = self.position
        if direction == "right":
            new_x, new_y = x + 1, y
        elif direction == "left":
            new_x, new_y = x - 1, y
        elif direction == "back":
            new_x, new_y = x, y - 1
        elif direction == "front":
            new_x, new_y = x, y + 1
        else:
            raise ValueError("Invalid direction")

        if 0 <= new_x < self.environment.size and 0 <= new_y < self.environment.size:
            return new_x, new_y
        else:
            raise IndexError("Agent would go out of the environment")

    def move(self, direction):
        try:
            new_position = self.get_new_position_and_check_bounds(direction)
        except (IndexError, ValueError) as e:
            print(e)
            return

        new_cell = self.environment.grid[new_position[0]][new_position[1]]

        # Interact with the entity in the new cell
        if new_cell.entity is not None:
            if not self.interact_with_entity(new_cell.entity):
                return  # Stop further actions if interaction returns False

        # Update the grid
        old_cell = self.environment.grid[self.position[0]][self.position[1]]
        old_cell.remove_entity()
        new_cell.set_entity(self)

        # Reveal the new cell if it is not visible
        if not new_cell.visible:
            new_cell.reveal()

        self.position = new_position
        self.perceive()

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
