# FILE: environment/field.py


class Field:
    def __init__(self, entity=None):
        self.entity = entity
        self.visible = False
        self.perceptions = []

    def reveal(self):
        self.visible = True
