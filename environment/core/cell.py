class Cell:
    def __init__(self, entity=None):
        self.entity = entity
        self.visible = True
        self.perceptions = []
        self.current_image = None
        self.update_image()

    def reveal(self):
        self.visible = True
        self.update_image()

    def update_image(self):
        if self.entity and self.visible:
            self.current_image = self.entity.images[self.entity.current_image_key]
        else:
            self.current_image = None

    def set_entity(self, entity):
        self.entity = entity
        self.update_image()

    def remove_entity(self):
        self.entity = None
        self.update_image()

    def entity_image_changed(self):
        self.update_image()