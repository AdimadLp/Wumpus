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
    missed_shots_left: int = 2

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
        decision = self.decide()
        
        if decision == "move_front":
            self.move("front")
        elif decision == "move_back":
            self.move("back")
        elif decision == "move_left":
            self.move("left")
        elif decision == "move_right":
            self.move("right")
        elif decision == "attack":
            self.attack()
        elif decision == "collect":
            self.collect()
        elif decision == "communicate":
            self.communicate()
        else:
            print("Invalid decision")

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

        # Reveal the new cell if it is not visible
        if not new_cell.visible:
            new_cell.reveal()

        # Interact with the entity in the new cell
        if new_cell.entity is not None:
            if not self.interact_with_entity(new_cell.entity):
                return

        # Update the grid
        old_cell = self.environment.grid[self.position[0]][self.position[1]]
        old_cell.remove_entity()

        if new_cell.entity is None:
            new_cell.set_entity(self)
            self.position = new_position
            self.perceive()

    def attack(self):
        if self.missed_shots_left == 0:
            print("Agent has no more arrows!")
            return
        
        x, y = self.position
        # Check if the field where the agent directly looks at has a Wumpus
        if self.direction == "right" and x + 1 < self.environment.size:
            cell = self.environment.grid[x + 1][y]
        elif self.direction == "left" and x - 1 >= 0:
            cell = self.environment.grid[x - 1][y]
        elif self.direction == "back" and y - 1 >= 0:
            cell = self.environment.grid[x][y - 1]
        elif self.direction == "front" and y + 1 < self.environment.size:
            cell = self.environment.grid[x][y + 1]
        else:
            return

        cell.interact(self, interaction_type="attack")


        if cell.entity and cell.entity.entity_type == "Wumpus":
            self.score += cell.entity.reward
            cell.entity.die()
            print("Agent has killed a Wumpus!")
            return
        else:
            print("Agent missed the shot!")
            self.missed_shots_left -= 1
            return

    def collect(self):
        x, y = self.position
        cell = self.environment.grid[x][y]
        if cell.entity and cell.entity.entity_type == "Gold":
            self.score += cell.entity.reward
            cell.entity.collect()
            print("Agent has collected the Gold!")
            return
        else:
            print("There is no Gold in this cell!")
            return

    def communicate(self):
        pass
