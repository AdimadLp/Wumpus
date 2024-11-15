# FILE: environment/wumpus.py


class Wumpus:
    def __init__(self):
        self.type = "Wumpus"
        self.percept = "stench"
        self.position = None
        self.neighborhood = "neumann"
        self.perception_multiplier = 1
        self.perception_fields = []
        self.reward = 1000
        self.alive = True

    def __repr__(self):
        return "W"

    def assign_perception_fields(self, fields):
        self.perception_fields = fields

    def die(self):
        return self.reward
