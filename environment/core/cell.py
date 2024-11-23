class Cell:
    """
    A class to represent a cell in the game environment.

    Attributes:
    -----------
    entity : Entity or None
        The entity present in the cell (default is None).
    visible : bool
        The visibility status of the cell (default is False).
    perceptions : list
        A list of perceptions in the cell (default is an empty list).
    current_image : pygame.Surface or None
        The current image to display for the cell (default is None).
    """

    def __init__(self, entity=None):
        """
        Initialize the Cell class.

        Parameters:
        -----------
        entity : Entity or None, optional
            The entity present in the cell (default is None).
        """
        self.entity = entity
        self.visible = (
            False  # TODO: Create images for visible and invisible cells without entity
        )
        self.perceptions = []
        self.current_image = None
        self.update_image()

    def reveal(self):
        """
        Reveal the cell and update its image.
        """
        self.visible = True
        self.update_image()

    def update_image(self):
        """
        Update the current image of the cell based on its visibility and entity.
        """
        if self.entity and self.visible:
            self.current_image = self.entity.images[self.entity.current_image_key]
        else:
            self.current_image = None

    def set_entity(self, entity):
        """
        Set an entity in the cell and update its image.

        Parameters:
        -----------
        entity : Entity
            The entity to set in the cell.
        """
        self.entity = entity
        self.update_image()

    def remove_entity(self):
        """
        Remove the entity from the cell and update its image.
        """
        self.entity = None
        self.update_image()

    def interact(self, entity, interaction_type="neutral"):
        """
        Interact with the entity in the cell.

        Parameters:
        -----------
        entity : Entity
            The entity interacting with the cell.
        interaction_type : str, optional
            The type of interaction (default is "neutral").

        Returns:
        --------
        bool
            True if there is an entity to interact with, False otherwise.
        """
        if self.entity:
            self.entity.interaction_beaviour(entity, interaction_type)
            return True
        else:
            # No entity to interact with
            return False
