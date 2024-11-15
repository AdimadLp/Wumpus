# FILE: agent/agent.py

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.position = (0, 0)
        self.score = 0
        self.auto_mode = False
        self.alive = True  # Add an attribute to track if the agent is alive
        self.direction = "down"  # Add agent direction attribute

    def perceive(self):
        # Logic for the agent to perceive its surroundings
        x, y = self.position
        field = self.environment.grid[x][y]
        if field.perceptions:
            print("Agent perceives:", field.perceptions)
            return field.perceptions

        return []

    def decide(self):
        # Logic for the agent to make decisions based on perceptions
        pass

    def act(self):
        # Logic for the agent to act based on decisions
        pass

    def can_move(self, direction):
        x, y = self.position
        if direction == "right":
            return x < self.environment.size - 1
        elif direction == "left":
            return x > 0
        elif direction == "up":
            return y > 0
        elif direction == "down":
            return y < self.environment.size - 1
        else:
            raise ValueError("Invalid direction")

    def check_for_wumpus(self, position):
        x, y = position
        field = self.environment.grid[x][y]
        if field.entity:
            if field.entity.type == "Wumpus":
                print("Agent has been killed by a Wumpus!")
                self.alive = False
                return True
        return False
    
    def attack(self):
        x, y = self.position
        field = self.environment.grid[x][y]
        # Check if the field where the agent directly looks at has a Wumpus
        if self.direction == "right" and x + 1 < self.environment.size:
            field = self.environment.grid[x + 1][y]
        elif self.direction == "left" and x - 1 >= 0:
            field = self.environment.grid[x - 1][y]
        elif self.direction == "up" and y - 1 >= 0:
            field = self.environment.grid[x][y - 1]
        elif self.direction == "down" and y + 1 < self.environment.size:
            field = self.environment.grid[x][y + 1]
        else:
            return
        
        if field.entity.type == "Wumpus":
            field.entity.die()
            self.score += field.entity.reward
            self.environment.remove_entity(field.entity)
            print("Agent has killed a Wumpus!")
            return


    def move(self, direction):
        if not self.can_move(direction):
            raise IndexError("Agent would go out of the environment")

        x, y = self.position
        if direction == "right":
            new_position = (x + 1, y)
        elif direction == "left":
            new_position = (x - 1, y)
        elif direction == "up":
            new_position = (x, y - 1)
        elif direction == "down":
            new_position = (x, y + 1)

        # Check if the new position has a Wumpus
        if self.check_for_wumpus(new_position):
            self.alive = False

        self.position = new_position
        self.perceive()