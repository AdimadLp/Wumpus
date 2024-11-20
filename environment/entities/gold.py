# FILE: environment/wumpus.py
from .entity import Entity
from dataclasses import dataclass, field


@dataclass
class Gold(Entity):
    entity_type: str = "Gold"
    perception_range_multiplier: int = 0
    reward: int = 100
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/gold/front.png",
        }
    )
    current_image_key: str = "front"

    def interaction_beaviour(self, agent, interaction_type):
        if interaction_type == "collect":
            print("Agent collected a gold!")
            agent.score += self.reward
            self.die()
