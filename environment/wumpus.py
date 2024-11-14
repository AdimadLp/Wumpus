# FILE: environment/wumpus.py


class Wumpus:
    def __init__(self):
        self.type = "Wumpus"
        self.percept = "stench"
        self.perception_multiplier = 2
        self.perception_fields = []
        self.alive = True
        self.reward = 1000

    def __repr__(self):
        return "W"

    def assign_perception_fields(self, fields):
        self.perception_fields = fields

    def die(self):
        self.alive = False
        return self.reward
