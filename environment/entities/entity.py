from dataclasses import dataclass, field
from helpers.neighborhood import neumann_neighborhood, moore_neighborhood
from helpers.image_processing import load_and_scale_image, calculate_draw_position

# FILE: environment/entity.py

@dataclass
class Entity:
    environment: object
    position: tuple
    
    entity_type: str
    image_paths: dict
    reward: int

    perception_type: str = field(default=None)
    neighborhood: str = field(default="neumann")
    perception_range_multiplier: int = field(default=0)
    
    alive: bool = field(default=True)
    images:dict = field(default_factory=dict)
    current_image_key: str = field(default=None)
    perception_fields: list = field(default_factory=list)
    direction: str = field(default="front")

    @property
    def die(self):
        self.alive = False
        self.environment.remove_entity(self)
        return self.reward
    
    def __post_init__(self):
        self.calculate_perception_fields()
        self.update_images()

    def update_images(self):
        for key, path in self.image_paths.items():
            self.images[key] = load_and_scale_image(path, self.environment.cell_size)

    def update_image_key(self, new_image_key):
        self.current_image_key = new_image_key
        cell = self.environment.grid[self.position[0]][self.position[1]]
        cell.entity_image_changed()

    def change_direction(self, new_direction):
        self.direction = new_direction
        self.update_image_key(new_direction)

    def calculate_perception_fields(self):
        x, y = self.position
        if self.neighborhood == "neumann":
            self.perception_fields = neumann_neighborhood(x, y, self.environment.size, self.perception_range_multiplier)
        elif self.neighborhood == "moore":
            self.perception_fields = moore_neighborhood(x, y, self.environment.size, self.perception_range_multiplier)

    def die(self):
        print("Agent has been killed by a Wumpus!")
        self.alive = False
        self.environment.remove_entity(self)
        return self.reward