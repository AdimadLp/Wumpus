# FILE: agent/agent.py
import pygame


class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.position = (0, 0)
        self.has_gold = False
        self.enabled = False  # Flag to determine if the agent is enabled
        self.image = pygame.Surface((environment.cell_size, environment.cell_size))
        self.image.fill((0, 255, 0))  # Green square for the agent

    def perceive(self):
        # Logic for the agent to perceive its surroundings
        pass

    def decide(self):
        # Logic for the agent to make decisions based on perceptions
        pass

    def act(self):
        # Logic for the agent to act based on decisions
        pass

    def move(self, direction):
        x, y = self.position
        if direction == "right":
            self.position = (x + 1, y)
        elif direction == "left":
            self.position = (x - 1, y)
        elif direction == "up":
            self.position = (x, y - 1)
        elif direction == "down":
            self.position = (x, y + 1)
        else:
            raise ValueError("Invalid direction")
