from .entity import Entity
from dataclasses import dataclass, field

# FILE: environment/pit.py


@dataclass
class Pit(Entity):
    """
    A class to represent a pit entity in the game environment.

    Attributes:
    -----------
    entity_type : str
        Specifies the type of the entity to "Pit".
    image_paths : dict
        Specifies the image file paths.
    reward : int
        Specifies the reward value to 100.
    perception_type : str
        Specifies the perception to "breeze".
    neighborhood : str
        Specifies the type of neighborhood for perception to "neumann".
    perception_range_multiplier : int
        Specifies the multiplier for the perception range to 0.
    current_image_key : str
        The key for the current image (default is "front").
    """

    entity_type: str = "Pit"
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/pit/front.png",
        }
    )
    reward: int = 0
    perception_type: str = "breeze"
    neighborhood: str = "neumann"
    perception_range_multiplier: int = 1
    current_image_key: str = "front"

    def interaction_beaviour(self, agent, interaction_type):
        """
        Define the interaction behavior with an agent.

        Parameters:
        -----------
        agent : Agent
            The agent interacting with the pit.
        interaction_type : str
            The type of interaction (e.g., "neutral").
        """
        if interaction_type == "neutral":
            print("Agent has fallen into a pit!")
            agent.die()
            self.reveal()
