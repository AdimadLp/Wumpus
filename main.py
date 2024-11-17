# FILE: main.py
import pygame
from pygame.locals import *
from environment.core.environment import Environment
import asyncio # Necessary for pygbag
from helpers.image_processing import calculate_draw_position
# Run pygbag main.py to play the game in the browser

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1200, 1200
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World")

# Define the game class
class WumpusGame:
    def __init__(self):
        # Initialize the environment and agent
        self.environment = Environment(size=GRID_SIZE, cell_size=CELL_SIZE)
        # Search the first agent with auto_mode set to False
        self.agent = self.get_next_agent()
        
        self.running = True
        self.key_hold_time = 0
        self.key_hold_threshold = 100  # milliseconds

        # Dictionary to keep track of loaded images
        self.loaded_images = {}

    def get_next_agent(self):
        try:
            return next(agent for agent in self.environment.entities if agent.entity_type == 'Agent' and not agent.auto_mode and agent.alive)
        except StopIteration:
            print("No alive agent with auto_mode set to False found.")
            return None

    def draw_grid(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    def draw_environment(self):
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the grid
        self.draw_grid()
        
        # Draw the entities in the environment
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell = self.environment.grid[x][y]
                if cell.current_image is not None:
                    image = cell.current_image
                    draw_x, draw_y = calculate_draw_position(x, y, image, CELL_SIZE)
                    screen.blit(image, (draw_x, draw_y))
        
        # Update the display
        pygame.display.flip()

    def check_agent_status(self):
        if self.agent and not self.agent.alive:
            self.agent = self.get_next_agent()

    async def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN and self.agent:
                    if not self.agent.auto_mode:
                        if event.key == K_UP:
                            if self.agent.direction == "back":
                                try:
                                    self.agent.move("back")
                                except (IndexError, ValueError) as e:
                                    print(e)
                            self.agent.change_direction("back") # Change to up
                        elif event.key == K_DOWN:
                            if self.agent.direction == "front":
                                try:
                                    self.agent.move("front")
                                except (IndexError, ValueError) as e:
                                    print(e)
                            self.agent.change_direction("front")
                        elif event.key == K_LEFT:
                            if self.agent.direction == "left":
                                try:
                                    self.agent.move("left")
                                except (IndexError, ValueError) as e:
                                    print(e)
                            self.agent.change_direction("left")
                        elif event.key == K_RIGHT:
                            if self.agent.direction == "right":
                                try:
                                    self.agent.move("right")
                                except (IndexError, ValueError) as e:
                                    print(e)
                            self.agent.change_direction("right")
                        elif event.key == K_SPACE:
                            self.agent.attack()
                    self.key_hold_time = pygame.time.get_ticks()

            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            if self.agent and current_time - self.key_hold_time > self.key_hold_threshold:
                if keys[K_UP]:
                    if self.agent.direction == "back":
                        try:
                            self.agent.move("up")
                        except (IndexError, ValueError) as e:
                            print(e)
                    self.agent.change_direction("back")
                    self.key_hold_time = current_time
                elif keys[K_DOWN]:
                    if self.agent.direction == "front":
                        try:
                            self.agent.move("down")
                        except (IndexError, ValueError) as e:
                            print(e)
                    self.agent.change_direction("front")
                    self.key_hold_time = current_time
                elif keys[K_LEFT]:
                    if self.agent.direction == "left":
                        try:
                            self.agent.move("left")
                        except (IndexError, ValueError) as e:
                            print(e)
                    self.agent.change_direction("left")
                    self.key_hold_time = current_time
                elif keys[K_RIGHT]:
                    if self.agent.direction == "right":
                        try:
                            self.agent.move("right")
                        except (IndexError, ValueError) as e:
                            print(e)
                    self.agent.change_direction("right")
                    self.key_hold_time = current_time

            self.check_agent_status()
            self.draw_environment()
            clock.tick(30)
            await asyncio.sleep(0)

        pygame.quit()


# Run the game
if __name__ == "__main__":
    game = WumpusGame()
    asyncio.run(game.run())