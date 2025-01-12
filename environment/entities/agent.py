# FILE: agent/agent.py
from dataclasses import dataclass, field
from .entity import Entity
from helpers.neighborhood import (
    neumann_neighborhood,
    whisper_neighborhood,
)
import random

from helpers.essentials import (
    perception_to_target,
    targets,
    parse_pos_str_to_tuple
)



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
    memory : dict
        Count of perceptions assigned to each cell (default is a grid of the same size as the cell grid of dictionaries with None values for each perception that exists on the cells).
    targeted_cells : list
        A list of targeted cells for the agent.
    strategy : str
        The movement strategy of the agent (default is "random").
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
    memory: dict = field(default_factory=dict)
    targeted_cells: list = field(default_factory=list)
    movement_mode: str = "random"

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
        # was_visited = False
        x, y = self.position

        current_cell = self.environment.grid[x][y]
        if (x, y) in self.memory:
            # was_visited = self.memory[(x, y)]["visited"]
            self.memory[(x, y)]["visited"] = True
        else:
            # using numbers, same perception multiple times is possible
            # also save probabilities of entities
            self.memory[(x, y)] = {
                "visited": True,
                "breeze": 0,
                "stench": 0,
                "shininess": 0,
                "pit": 0.0,
                "wumpus": 0.0,
                "gold": 0.0,
            }

        # initialise neighbors in memory
        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
            if (nx, ny) not in self.memory:
                self.memory[(nx, ny)] = {
                    "visited": False,
                    "breeze": 0,
                    "stench": 0,
                    "shininess": 0,
                    "pit": None,
                    "wumpus": None,
                    "gold": None,
                }

        if current_cell.perceptions:
            print("Agent perceives:", current_cell.perceptions)

            # reset counts, perceptions can change (shininess)
            self.memory[(x, y)].update(
                {
                    "breeze": 0,
                    "stench": 0,
                    "shininess": 0,
                }
            )

            for perception in current_cell.perceptions:
                self.memory[(x, y)][perception] += 1

        # estimate probabilities
        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
            self.estimate_cell((nx, ny))

        # print(self.memory)
        print("------------")
        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
            self.print_probs((nx, ny))
        print("------------")

    def estimate_cell(self, pos):
        """
        Estimates entity probabilities of corresponding cell based on data in memory

        Parameters:
        -----------
            pos: tuple (int, int)
        """

        # todo: remove shininess after gold was collected
        # todo: get shininess perception to work some how or remove it completely

        if pos in self.memory and self.memory[pos]["visited"]:
            self.memory[pos].update(
                {
                    "pit": 0.0,
                    "wumpus": 0.0,
                    "gold": 0.0,
                }
            )
            return None

        # check neighbors for perceptions
        for x, y in neumann_neighborhood(pos[0], pos[1], self.environment.size):
            # only visited cells can have perceptions in memory
            if (x, y) in self.memory and self.memory[(x, y)]["visited"]:

                for perception, amount in self.memory[(x, y)].items():
                    if perception in ["visited"] + targets:
                        continue
                    target = perception_to_target[perception]

                    if not amount:
                        self.memory[pos][target] = 0.0
                        continue

                    # only use max prob (but dont overwrite a 0 or 1)
                    if (
                        self.memory[pos][target] != 0
                        and self.memory[pos][target] != 1.0
                    ):

                        # get possible neighbors for target (of this neighbor)
                        # reduce amount by already determined neighbor cells
                        possible_neighbors = 0
                        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
                            if (nx, ny) not in self.memory or (
                                not self.memory[(nx, ny)]["visited"]
                                and self.memory[(nx, ny)][target] != 0
                                and self.memory[(nx, ny)][target] != 1
                            ):
                                possible_neighbors += 1
                            if (nx, ny) in self.memory and self.memory[(nx, ny)][
                                target
                            ] == 1.0:
                                amount -= 1

                        if amount and possible_neighbors == 0:
                            print("warning: not possible")
                            continue

                        prob = amount / possible_neighbors

                        if (
                            not self.memory[pos][target]
                            or self.memory[pos][target] < prob
                            or prob == 0
                        ):
                            self.memory[pos][target] = prob

    def print_probs(self, pos):
        if pos in self.memory:
            d = dict(filter(lambda item: item[0] in targets, self.memory[pos].items()))
            print(f"{pos}: {d}")
        else:
            print("unknown")

    def decide(self):
        """
        Decide the next action for the agent.

        Returns:
        --------
        str
            The decision made by the agent (default is "neutral").
        """
        # TODO: Implement the decision-making logic 
        #   - if wumpus is clear shoot and broadcast
        #   - decide to end game
        #   - if gold is clear: collect

        delta_to_direction = {
            (1, 0): "right",
            (-1, 0): "left",
            (0, 1): "front",
            (0, -1): "back",
        }

        if "target" not in self.memory:
            self.memory["target"] = None

        if not self.memory["target"]:
            # TODO: exclude conflicting cells (determined by auction in same sim step)
            safe_cells = []
            for x, y in neumann_neighborhood(
                self.position[0], self.position[1], self.environment.size
            ):
                if (
                    (x, y) in self.memory
                    and self.memory[(x, y)]["pit"] == 0.0
                    and self.memory[(x, y)]["wumpus"] == 0.0
                ):
                    safe_cells.append((x, y))

            if safe_cells:
                # explore
                unvisited_cells = []
                for cell in safe_cells:
                    if not self.memory[cell]["visited"]:
                        unvisited_cells.append(cell)
                if unvisited_cells:
                    self.memory["target"] = random.choice(unvisited_cells)
                    return "communicate"

                # go back
                self.memory["target"] = random.choice(safe_cells)
                return "communicate"
            else:
                # TODO: broadcast for help (or do a risky strat)
                pass
        else:
            dx = self.memory["target"][0] - self.position[0]
            dy = self.memory["target"][1] - self.position[1]
            self.memory["target"] = None
            return f"move_{delta_to_direction[(dx, dy)]}"

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

        if neighbour_cell is None:
            print("Agent is facing out of bounds!")
            return
        if not neighbour_cell.interact(self, interaction_type="collect"):
            print("Agent cannot collect from this cell!")

    def communicate(self):
        """
        Perform a communication action with other agents in the neighborhood.
        """
        # message = f"cfp:{self.position}"  # Example message

        if self.memory["target"]:
            message = f"going to: {self.memory["target"]}"

        print(f"Agent at {self.position} communicates: {message}")
        self.whisper(message)

    def whisper(self, message):
        """
        Whisper a message to other agents in the defined neighborhood.

        Parameters:
        -----------
        message : str
            The message to whisper.
        """
        x, y = self.position
        neighbours = whisper_neighborhood(x, y, self.environment.size)
        for nx, ny in neighbours:
            cell = self.environment.grid[nx][ny]
            if cell.entity and cell.entity.entity_type == "Agent":
                cell.entity.receive_whisper(message)

    def receive_whisper(self, message):
        """
        Receive a whispered message from another agent.

        Parameters:
        -----------
        message : str
            The message received.
        """
        print(f"Agent at {self.position} received whisper: {message}")

        action, data = message.split(':')
        pos = parse_pos_str_to_tuple(data.strip())
        match action.strip():
            case "going to":
                # TODO: add pos to conflicting neighbors

                if pos == self.memory["target"]:
                    # TODO: auction
                    outcome = random.choice([True, False])
                    if outcome:
                        self.whisper(f"deny: {pos}")
                    else:
                        self.whisper(f"allow: {pos}")
                        self.memory["target"] = None
            case "deny":
                # TODO: add pos to conflicting neighbors
                self.memory["target"] = None
            case "allow":
                pass
                # do not add add pos to conflicting neighbors

        # TODO: Implement response to the whisper
        # TODO: Implement negotiation logic based on the message
