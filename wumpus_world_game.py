# FILE: wumpus_world_game.py

from environment import Environment
from agent import Agent


class WumpusWorldGame:
    def __init__(self, size):
        self.environment = Environment(size)
        self.agent = Agent(self.environment)

    def play(self):
        while not self.agent.has_gold:
            self.agent.perceive()
            self.agent.decide()
            self.agent.act()
            self.environment.display()


if __name__ == "__main__":
    game = WumpusWorldGame(size=4)
    game.play()
