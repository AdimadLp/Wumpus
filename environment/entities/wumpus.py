# FILE: environment/wumpus.py
from .entity import Entity
from dataclasses import dataclass, field


@dataclass
class Wumpus(Entity):
    """
    A class to represent a Wumpus entity in the game environment.

    Attributes:
    -----------
    entity_type : str
        Specifies the type of the entity to "Wumpus".
    image_paths : dict
        A dictionary mapping directions to image file paths.
    reward : int
        The reward value associated with the Wumpus (default is 1000).
    perception_type : str
        The type of perception the Wumpus has (default is "stench").
    neighborhood : str
        The type of neighborhood for perception (default is "neumann").
    perception_range_multiplier : int
        Specifies the multiplier for the perception range to 1.
    current_image_key : str
        The key for the current image (default is "front").
    """

    entity_type: str = "Wumpus"
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/wumpus/front.png",
        }
    )
    reward: int = 1000
    perception_type: str = "stench"
    neighborhood: str = "neumann"
    perception_range_multiplier: int = 1
    current_image_key: str = "front"

    def interaction_beaviour(self, agent, interaction_type):
        """
        Define the interaction behavior with an agent.

        Parameters:
        -----------
        agent : Agent
            The agent interacting with the Wumpus.
        interaction_type : str
            The type of interaction (e.g., "neutral", "attack").
        """
        if interaction_type == "neutral":
            print("Agent has been killed by a Wumpus!")
            agent.die()
            self.revial()

        elif interaction_type == "attack":
            print("Agent killed a Wumpus!")
            agent.score += self.reward
            self.revial()
            self.die()
