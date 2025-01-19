from dataclasses import dataclass, field
from helpers.neighborhood import neumann_neighborhood, moore_neighborhood
from helpers.image_processing import load_and_scale_image

# FILE: environment/entity.py


@dataclass
class Entity:
    """
    A class to represent an entity in the game environment.

    Attributes:
    -----------
    environment : object
        The environment in which the entity exists.
    position : tuple
        The (x, y) position of the entity in the grid.
    entity_type : str
        The type of the entity (e.g., "Agent", "Wumpus").
    image_paths : dict
        A dictionary mapping directions to image file paths.
    reward : int
        The reward value associated with the entity.
    perception_type : str, optional
        The type of perception the entity has (default is None).
    perception_neighborhood : str, optional
        The type of neighborhood for perception (default is "neumann").
    perception_range_multiplier : int, optional
        The multiplier for the perception range (default is 1).
    alive : bool, optional
        The alive status of the entity (default is True).
    images : dict, optional
        A dictionary to store loaded images (default is an empty dict).
    current_image_key : str, optional
        The key for the current image (default is None).
    perception_fields : list, optional
        A list of perception fields (default is an empty list).
    direction : str, optional
        The current direction the entity is facing (default is "front").
    """

    environment: object
    position: tuple
    entity_type: str
    image_paths: dict
    reward: int
    perception_type: str = field(default=None)
    perception_neighborhood: str = field(default="neumann")
    perception_range_multiplier: int = field(default=1)
    alive: bool = field(default=True)
    images: dict = field(default_factory=dict)
    current_image_key: str = field(default=None)
    perception_fields: list = field(default_factory=list)
    direction: str = field(default="front")

    # Class-level cache for images
    _image_cache = {}

    def die(self):
        """
        Mark the entity as dead and remove it from the environment.
        """
        self.alive = False
        self.environment.remove_entity(self)

    def reveal(self):
        """
        Reveal the cell where the entity is located.
        """
        x, y = self.position
        cell = self.environment.grid[x][y]
        cell.reveal()

    def __post_init__(self):
        """
        Post-initialization to calculate perception fields and update images.
        """
        self.calculate_perception_fields()
        self.update_images()

    def update_images(self):
        """
        Load and cache images for the entity based on its type and image paths.
        """
        if self.entity_type not in Entity._image_cache:
            Entity._image_cache[self.entity_type] = {}
            for key, path in self.image_paths.items():
                Entity._image_cache[self.entity_type][key] = load_and_scale_image(
                    path, self.environment.cell_size
                )

        self.images = Entity._image_cache[self.entity_type]

    def update_image_key(self, new_image_key):
        """
        Update the current image key and notify the cell of the change.

        Parameters:
        -----------
        new_image_key : str
            The new image key to update.
        """
        self.current_image_key = new_image_key
        cell = self.environment.grid[self.position[0]][self.position[1]]
        cell.update_image()

    def change_direction(self, new_direction):
        """
        Change the direction the entity is facing and update the image.

        Parameters:
        -----------
        new_direction : str
            The new direction to face.
        """
        self.direction = new_direction
        self.update_image_key(new_direction)

    def calculate_perception_fields(self):
        """
        Calculate the perception fields based on the entity's position and neighborhood type.
        """
        x, y = self.position
        if self.perception_neighborhood == "neumann":
            fields = neumann_neighborhood(
                x, y, self.environment.size, self.perception_range_multiplier
            )
        elif self.perception_neighborhood == "moore":
            fields = moore_neighborhood(
                x, y, self.environment.size, self.perception_range_multiplier
            )
        else:
            fields = None

        if fields is not None:
            self.perception_fields = fields

    def interaction_beaviour(self, entity, interaction_type):
        """
        Define the interaction behavior with another entity.

        Parameters:
        -----------
        entity : Entity
            The entity to interact with.
        interaction_type : str
            The type of interaction (e.g., "attack", "collect").
        """
        pass
