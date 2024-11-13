# FILE: main.py
import pygame
from pygame.locals import *
from environment import Environment
from agent import Agent

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World")


# Define the game class
class WumpusGame:
    def __init__(self):
        self.environment = Environment(size=GRID_SIZE, cell_size=CELL_SIZE)
        self.agent = Agent(self.environment)
        self.running = True

    def draw_grid(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    def draw_agent(self):
        x, y = self.agent.position
        screen.blit(self.agent.image, (x * CELL_SIZE, y * CELL_SIZE))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if not self.agent.enabled:
                        try:
                            if event.key == K_UP:
                                self.agent.move("up")
                            elif event.key == K_DOWN:
                                self.agent.move("down")
                            elif event.key == K_LEFT:
                                self.agent.move("left")
                            elif event.key == K_RIGHT:
                                self.agent.move("right")
                        except IndexError as e:
                            print(e)
                        except ValueError as e:
                            print(e)

            screen.fill((0, 0, 0))
            self.draw_grid()
            self.draw_agent()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


# Run the game
if __name__ == "__main__":
    game = WumpusGame()
    game.run()
