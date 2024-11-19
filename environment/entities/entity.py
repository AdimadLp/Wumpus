from dataclasses import dataclass, field
from helpers.neighborhood import neumann_neighborhood, moore_neighborhood
from helpers.image_processing import load_and_scale_image

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
    perception_range_multiplier: int = field(default=1)

    alive: bool = field(default=True)
    images: dict = field(default_factory=dict)
    current_image_key: str = field(default=None)
    perception_fields: list = field(default_factory=list)
    direction: str = field(default="front")

    # Class-level cache for images
    _image_cache = {}

    def die(self):
        self.alive = False
        self.environment.remove_entity(self)
        return self.reward

    def revial(self):
        x, y = self.position
        cell = self.environment.grid[x][y]
        cell.reveal()

    def __post_init__(self):
        self.calculate_perception_fields()
        self.update_images()

    def update_images(self):
        if self.entity_type not in Entity._image_cache:
            Entity._image_cache[self.entity_type] = {}
            for key, path in self.image_paths.items():
                Entity._image_cache[self.entity_type][key] = load_and_scale_image(
                    path, self.environment.cell_size
                )

        self.images = Entity._image_cache[self.entity_type]

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
            fields = neumann_neighborhood(
                x, y, self.environment.size, self.perception_range_multiplier
            )
        elif self.neighborhood == "moore":
            fields = moore_neighborhood(
                x, y, self.environment.size, self.perception_range_multiplier
            )
        else:
            fields = None

        if fields is not None:
            self.perception_fields = fields

    def interact(self, agent, interaction_type="neutral"):
        pass
