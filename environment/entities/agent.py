# FILE: agent/agent.py
from dataclasses import dataclass, field
from .entity import Entity


@dataclass
class Agent(Entity):
    """
    A class to represent an agent in the game environment.

    Attributes:
    -----------
    entity_type : str
        Specifies the type of the entity to "Agent".
    image_paths : dict
        Specifies the image file paths.
    reward : int
        Specifies the reward value to 0.
    perception_range_multiplier : int
        Specifies the multiplier for the perception range to 0.
    current_image_key : str
        The key for the current image (default is "front").
    score : int
        The score of the agent.
    auto_mode : bool
        The auto mode status of the agent.
    missed_shots_left : int
        The number of missed shots left for the agent.
    """

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
        """
        Post-initialization to reveal the initial cell.
        """
        super().__post_init__()
        self.reveal_initial_cell()
        self.perceive()

    def reveal_initial_cell(self):
        """
        Reveal the initial cell where the agent is located.
        """
        x, y = self.position
        self.environment.grid[x][y].reveal()

    def perceive(self):
        """
        Logic for the agent to perceive its surroundings.

        Returns:
        --------
        list
            A list of perceptions in the current field.
        """
        x, y = self.position
        field = self.environment.grid[x][y]
        if field.perceptions:
            print("Agent perceives:", field.perceptions)
            return field.perceptions
        return []

    def decide(self):
        """
        Decide the next action for the agent.

        Returns:
        --------
        str
            The decision made by the agent (default is "neutral").
        """
        # TODO: Implement the decision-making logic
        return "neutral"

    def act(self, decision=None):
        """
        Perform an action based on the decision.

        Parameters:
        -----------
        decision : str, optional
            The decision to act upon. Given decision, if in manual mode and call decide() if in auto mode.
        """
        if self.auto_mode:
            decision = self.decide()

        actions = {
            "move_front": lambda: self.move("front"),
            "move_back": lambda: self.move("back"),
            "move_left": lambda: self.move("left"),
            "move_right": lambda: self.move("right"),
            "attack": self.attack,
            "collect": self.collect,
            "communicate": self.communicate,
            "neutral": lambda: None,
        }
        actions.get(decision, lambda: print("Invalid decision"))()

    def get_new_position_and_check_bounds(self, direction):
        """
        Get the new position based on the direction and check if it is within bounds.

        Parameters:
        -----------
        direction : str
            The direction to move.

        Returns:
        --------
        tuple
            The new (x, y) position.

        Raises:
        -------
        ValueError
            If the direction is invalid.
        IndexError
            If the new position is out of bounds.
        """
        x, y = self.position
        directions = {
            "right": (x + 1, y),
            "left": (x - 1, y),
            "back": (x, y - 1),
            "front": (x, y + 1),
        }
        new_x, new_y = directions.get(direction, (None, None))
        if new_x is None or new_y is None:
            raise ValueError("Invalid direction")

        if 0 <= new_x < self.environment.size and 0 <= new_y < self.environment.size:
            return new_x, new_y
        else:
            raise IndexError("Agent would go out of the environment")

    def move(self, direction):
        """
        Move the agent in the specified direction.

        Parameters:
        -----------
        direction : str
            The direction to move.
        """
        try:
            new_position = self.get_new_position_and_check_bounds(direction)
        except (IndexError, ValueError) as e:
            print(e)
            return

        new_cell = self.environment.grid[new_position[0]][new_position[1]]

        # Reveal the new cell if it is not visible
        if not new_cell.visible:
            new_cell.reveal()

        # Check if the new cell is occupied by another agent
        if new_cell.entity and new_cell.entity.entity_type == "Agent":
            return

        new_cell.interact(self)

        if new_cell.entity is None:
            # Update the grid
            old_cell = self.environment.grid[self.position[0]][self.position[1]]
            old_cell.remove_entity()
            new_cell.set_entity(self)
            self.position = new_position
            self.perceive()

    def get_facing_neighbour_cell(self):
        """
        Get the cell that the agent is facing.

        Returns:
        --------
        Cell or None
            The cell the agent is facing or None if out of bounds.
        """
        x, y = self.position
        directions = {
            "right": (x + 1, y),
            "left": (x - 1, y),
            "back": (x, y - 1),
            "front": (x, y + 1),
        }
        new_x, new_y = directions.get(self.direction, (None, None))
        if (
            new_x is None
            or new_y is None
            or not (
                0 <= new_x < self.environment.size
                and 0 <= new_y < self.environment.size
            )
        ):
            return None
        return self.environment.grid[new_x][new_y]

    def attack(self):
        """
        Perform an attack action in the direction the agent is facing.
        """
        if self.missed_shots_left == 0:
            print("Agent has no more arrows!")
            return

        neighbour_cell = self.get_facing_neighbour_cell()
        if not neighbour_cell.interact(self, interaction_type="attack"):
            print("Agent missed the shot!")
            self.missed_shots_left -= 1

    def collect(self):
        """
        Perform a collect action in the direction the agent is facing.
        """
        neighbour_cell = self.get_facing_neighbour_cell()

        if not neighbour_cell.interact(self, interaction_type="collect"):
            print("Agent cannot collect from this cell!")

    def communicate(self):
        """
        Perform a communicate action.
        """
        # TODO: Implement the communication logic
        pass
