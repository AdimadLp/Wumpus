# FILE: environment/wumpus.py
from .entity import Entity
from dataclasses import dataclass, field


@dataclass
class Wumpus(Entity):
    entity_type: str = "Wumpus"
    perception_type: str = "stench"
    reward: int = 1000
    image_paths: dict = field(
        default_factory=lambda: {
            "front": "src/wumpus/front.png",
        }
    )
    current_image_key: str = "front"
    neighborhood: str = "neumann"
    perception_range_multiplier: int = 1

    def interaction_beaviour(self, agent, interaction_type):
        if interaction_type == "neutral":
            print("Agent has been killed by a Wumpus!")
            agent.die()
            self.revial()

        elif interaction_type == "attack":
            print("Agent killed a Wumpus!")
            agent.score += self.reward
            self.die()
