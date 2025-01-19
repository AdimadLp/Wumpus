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
    delta_to_direction,
    get_direction,
    parse_pos_str_to_tuple,
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
    auto_mode: bool = True
    missed_shots_left: int = 2
    memory: dict = field(default_factory=dict)
    last_memories: list = field(
        default_factory=list
    )  # For checking if memory is changing
    targeted_cells: list = field(default_factory=list)
    movement_mode: str = "random"
    vote_admin: bool = False
    vote_state: str = "exit"

    def __post_init__(self):
        """
        Post-initialization to reveal the initial cell.
        """
        super().__post_init__()
        self.memory["target"] = None  # Initialize target
        self.memory["reserved_cells"] = []  # Initialize reserved_cells
        # self.memory["last_target"] = None
        self.memory["arrow_target"] = None

        self.reveal_initial_cell()
        # self.perceive()

    def __str__(self):
        return f"Agent at {self.position}"

    def reveal_initial_cell(self):
        """
        Reveal the initial cell where the agent is located.
        """
        x, y = self.position
        self.environment.grid[x][y].reveal()

    def reveal_wumpus(self):
        """
        Reveal the Wumpus if the probability for the cell with the Wumpus is 1.
        """
        for pos, data in self.memory.items():
            if isinstance(pos, tuple) and data.get("wumpus") == 1.0:
                cell = self.environment.grid[pos[0]][pos[1]]
                if cell.entity and cell.entity.entity_type == "Wumpus":
                    cell.entity.reveal()
                    print(f"{self} revealed a Wumpus at {pos}!")

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
                # "shininess": 0,
                "pit": 0.0,
                "wumpus": 0.0,
                # "gold": 0.0,
            }

        # initialise neighbors in memory
        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
            if (nx, ny) not in self.memory:
                self.memory[(nx, ny)] = {
                    "visited": False,
                    "breeze": 0,
                    "stench": 0,
                    # "shininess": 0,
                    "pit": None,
                    "wumpus": None,
                    # "gold": None,
                }

        if current_cell.perceptions:
            print(f"{self} perceives: {current_cell.perceptions}")

            # reset counts, perceptions can change (shininess)
            self.memory[(x, y)].update(
                {
                    "breeze": 0,
                    "stench": 0,
                    # "shininess": 0,
                }
            )

            for perception in current_cell.perceptions:
                if perception == "shininess":
                    self.memory["shininess"] = True
                    continue

                self.memory[(x, y)][perception] += 1

        # estimate probabilities
        for nx, ny in neumann_neighborhood(x, y, self.environment.size):
            self.estimate_cell((nx, ny))

        self.reveal_wumpus()

        # print(self.memory)
        print(f"------ {self} estimates ------")
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

        if pos in self.memory and self.memory[pos]["visited"]:
            self.memory[pos].update(
                {
                    "pit": 0.0,
                    "wumpus": 0.0,
                    # "gold": 0.0,
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
                            print(f"{self} warning: not possible")
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

        if self.check_memory_stagnation() and not self.vote_admin:
            self.vote_admin = True
            self.vote_state = "exit"
            self.shout("vote")
        elif self.vote_admin:
            if self.vote_state == "exit":
                self.environment.game_over = True
            else:
                self.vote_admin = False

        # check if gold has to be collected (new approach)
        if "shininess" in self.memory and self.memory["shininess"]:
            self.memory["shininess"] = False
            return "collect"

        # check if wumpus is dead and broadcast
        if self.memory["arrow_target"]:
            if self.position == self.memory["arrow_target"]:
                # TODO: maybe shout as own action, but how to transfer data (message)?
                self.shout(f"wumpus killed: {self.position}")
                self.memory["arrow_target"] = None
                self.forget_wumpus(self.position)
            else:
                return (
                    f"move_{get_direction(self.position, self.memory['arrow_target'])}"
                )

        # check if wumpus is clear and shoot
        for cell_pos in neumann_neighborhood(
            self.position[0], self.position[1], self.environment.size
        ):
            if self.memory[cell_pos]["wumpus"] == 1.0:
                required_direction = get_direction(self.position, cell_pos)
                if self.direction == required_direction:
                    self.memory["arrow_target"] = cell_pos
                    return "attack"
                return f"turn_{required_direction}"

        # move (safe and coordinated)
        if not self.memory["target"]:
            safe_cells = []
            for x, y in neumann_neighborhood(
                self.position[0], self.position[1], self.environment.size
            ):
                if (
                    (x, y) in self.memory
                    and self.memory[(x, y)]["pit"] == 0.0
                    and self.memory[(x, y)]["wumpus"] == 0.0
                    and (x, y) not in self.memory["reserved_cells"]
                ):
                    safe_cells.append((x, y))
                # also append externaly visited cells to explore them
                if (
                    (x, y) not in safe_cells
                    and (x, y) not in self.memory["reserved_cells"]
                    and self.environment.grid[x][y].visible
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
                # TODO: do a risky strat, if all are stuck or Agent cant be reached
                print(f"{self} is stuck, needs help")
                self.whisper(f"I am stuck: {self.position}")
                # reserved cells have to be resetted, beacuse the agent does not move
                self.memory["reserved_cells"] = []

        elif self.direction != get_direction(self.position, self.memory["target"]):
            return f"turn_{get_direction(self.position, self.memory['target'])}"
        else:
            action = f"move_{get_direction(self.position, self.memory['target'])}"
            self.memory["reserved_cells"] = []
            # self.memory["last_target"] = self.memory["target"]
            self.memory["target"] = None
            return action

        return "neutral"

    def act(self, decision=None):
        """
        Perform an action based on the decision.

        Parameters:
        -----------
        decision : str, optional
            The decision to act upon. Given decision, if in manual mode and call decide() if in auto mode.
        """
        self.perceive()
        if self.auto_mode:
            decision = self.decide()

        actions = {
            "move_front": lambda: self.move("front"),
            "move_back": lambda: self.move("back"),
            "move_left": lambda: self.move("left"),
            "move_right": lambda: self.move("right"),
            "turn_front": lambda: self.change_direction("front"),
            "turn_back": lambda: self.change_direction("back"),
            "turn_left": lambda: self.change_direction("left"),
            "turn_right": lambda: self.change_direction("right"),
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
            # self.perceive()

    def get_facing_neighbor_cell(self):
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
            print(f"{self} has no more arrows!")
            return

        neighbor_cell = self.get_facing_neighbor_cell()
        if not neighbor_cell.interact(self, interaction_type="attack"):
            print(f"{self} missed the shot!")
            self.missed_shots_left -= 1

    def collect(self):
        """
        Perform a collect action in the direction the agent is facing.
        """
        neighbor_cell = self.get_facing_neighbor_cell()

        if neighbor_cell is None:
            print(f"{self} is facing out of bounds!")
            return
        if not neighbor_cell.interact(self, interaction_type="collect"):
            print(f"{self} cannot collect from this cell!")

    def communicate(self):
        """
        Perform a communication action with other agents in the neighborhood.
        """
        if self.memory["target"]:
            message = f'want to move: {self.position}->{self.memory["target"]}'  # Using single quotes outside

        print(f"{self} communicates: {message}")
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
        neighbors = whisper_neighborhood(x, y, self.environment.size)
        for nx, ny in neighbors:
            cell = self.environment.grid[nx][ny]
            if cell.entity and cell.entity.entity_type == "Agent":
                cell.entity.receive_message(message)

    def get_all_probabilities(self):
        """Get dictionary of all position probabilities from memory"""
        prob_dict = {}
        for key, value in self.memory.items():
            # Skip non-position entries
            if not isinstance(key, tuple):
                continue
            # Get probabilities for this position
            prob_dict[key] = {"pit": value["pit"], "wumpus": value["wumpus"]}
        return prob_dict

    def check_memory_stagnation(self):
        """Check if memory probabilities haven't changed in last 10 steps"""
        current_probs = str(self.get_all_probabilities())
        self.last_memories.append(current_probs)

        if len(self.last_memories) > 20:
            self.last_memories.pop(0)
            if len(set(self.last_memories)) == 1:  # All memories are identical
                return True
        return False

    def vote(self):
        """Cast a vote if memory is stagnant"""
        if self.check_memory_stagnation():
            self.shout("exit")
        else:
            self.shout("stay")

    def shout(self, message):
        """
        Shouts a message to all other agents

        Parameters:
        -----------
        message : str
            The message to shout.
        """
        print(f"{self} shouts: {message}")
        for entity in self.environment.entities:
            if (
                entity.entity_type == "Agent" and entity != self
            ):  # maybe also include self to induce process
                entity.receive_message(message)

    def receive_message(self, message):
        """
        Receive a message from another agent.

        Parameters:
        -----------
        message : str
            The message received.
        """
        print(f"{self} received message: {message}")

        if ":" in message:
            action, data = message.split(":")
            if "->" in message:
                pos = None
                data1, data2 = data.split("->")
                pos1 = parse_pos_str_to_tuple(data1.strip())
                pos2 = parse_pos_str_to_tuple(data2.strip())
            else:
                pos = parse_pos_str_to_tuple(data.strip())
        else:
            data = None
            pos = None
            action = message

        match action.strip():
            case "want to move":
                self.memory["reserved_cells"].append(pos1)
                current_target = self.memory.get("target")
                if current_target and pos2 == current_target:
                    # TODO: auction
                    outcome = random.choice([True, False])
                    if outcome:
                        self.whisper(f"deny: {pos2}")
                    else:
                        self.whisper(f"allow: {pos2}")
                        self.memory["target"] = None
                        self.memory["reserved_cells"].append(pos2)
                else:
                    self.memory["reserved_cells"].append(pos2)
            case "deny":
                self.memory["reserved_cells"].append(pos)
                self.memory["target"] = None
            case "allow":
                pass
                # do not add add pos to reserved neighbors

            case "wumpus killed":
                self.forget_wumpus(pos)

            case "I am stuck":
                # TODO: maybe answer a safe neighbor cell the recieving Agent knows
                self.memory["reserved_cells"].append(pos)
                for cell_pos in neumann_neighborhood(
                    pos[0], pos[1], self.environment.size
                ):
                    if cell_pos in self.memory and (
                        self.memory[cell_pos]["visited"]
                        or (
                            self.memory[cell_pos]["wumpus"] == 0.0
                            and self.memory[cell_pos]["pit"] == 0.0
                        )
                    ):
                        self.whisper(f"safe cell at: {cell_pos}")

            case "safe cell at":
                if pos in self.memory:
                    self.memory[pos]["wumpus"] = 0.0
                    self.memory[pos]["pit"] = 0.0
                else:
                    self.memory[pos] = {
                        "visited": False,
                        "breeze": 0,
                        "stench": 0,
                        # "shininess": 0,
                        "pit": 0.0,
                        "wumpus": 0.0,
                        # "gold": 0.0,
                    }
                print(f"{self} added safe cell at {pos} to memory")

            case "vote":
                if not self.vote_admin:
                    self.vote()

            case "stay":
                if self.vote_admin:
                    self.vote_state = "stay"

    def forget_wumpus(self, pos):
        """
        Removes everything related to the wumpus from memory at given position

        Parameters:
        -----------
        pos: tuple
            where the wumpus was killed
        """

        # prop has to be None and visited to false to reevaluate
        if pos in self.memory:
            self.memory[pos]["visited"] = False
            self.memory[pos]["wumpus"] = None
            self.memory[pos]["stench"] = 0

        for cell_pos in neumann_neighborhood(
            self.position[0], self.position[1], self.environment.size
        ):
            if cell_pos in self.memory:
                self.memory[cell_pos]["visited"] = False
                self.memory[cell_pos]["wumpus"] = None
                self.memory[cell_pos]["stench"] = 0
