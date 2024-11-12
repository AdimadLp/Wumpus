# FILE: agent.py


class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.position = (0, 0)
        self.has_gold = False

    def perceive(self):
        # Logic for the agent to perceive its surroundings
        pass

    def decide(self):
        # Logic for the agent to make decisions based on perceptions
        pass

    def act(self):
        # Logic for the agent to act based on decisions
        pass
