from .entity import Entity
from dataclasses import dataclass, field
# FILE: environment/pit.py

@dataclass
class Pit(Entity):
    entity_type: str = "Pit"
    perception_type: str = "breeze"
    reward: int = 0
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/pit/front.png",
        }
    )
    current_image_key: str = "front"
    neighborhood: str = "neumann"
    perception_range_multiplier: int = 1

    def interaction_beaviour(self, agent, interaction_type):
        if interaction_type == "neutral":
            print("Agent has fallen into a pit!")
            agent.die()
            self.revial()
