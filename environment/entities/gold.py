# FILE: environment/gold.py
from .entity import Entity
from dataclasses import dataclass, field


@dataclass
class Gold(Entity):
    """
    A class to represent a gold entity in the game environment.

    Attributes:
    -----------
    entity_type : str
        Specifies the type of the entity to "Gold".
    image_paths : dict
        Specifies the image file paths.
    reward : int
        Specifies the reward value to 100.
    perception_type : str, optional
        The type of perception the gold has (default is "shininess").
    perception_neighborhood : str, optional
        The type of neighborhood for perception (default is "neumann").
    perception_range_multiplier : int
        Specifies the multiplier for the perception range to 0.
    current_image_key : str
        The key for the current image (default is "front").
    """

    entity_type: str = "Gold"
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/gold/front.png",
        }
    )
    reward: int = 100
    perception_type: str = "shininess"
    perception_range_multiplier: int = 0
    current_image_key: str = "front"

    revealed: bool = False

    def interaction_beaviour(self, agent, interaction_type):
        """
        Define the interaction behavior with an agent.

        Parameters:
        -----------
        agent : Agent
            The agent interacting with the gold.
        interaction_type : str
            The type of interaction (e.g., "collect").
        """
        if interaction_type == "neutral":
            if self.revealed:
                return

            self.revealed = True
            self.perception_range_multiplier = 1
            self.environment.update_perceptions(self)
            agent.perceive()

        if interaction_type == "collect":
            print(f"{agent} collected a gold!")
            agent.score += self.reward
            self.die()
