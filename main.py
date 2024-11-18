# FILE: main.py
import pygame
from pygame.locals import *
from environment.core.environment import Environment
import asyncio  # Necessary for pygbag

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

        # Model created at https://hyperhuman.deemos.com/rodin

        # Dictionary to keep track of loaded images
        self.loaded_images = {}

    def get_next_agent(self):
        try:
            return next(
                agent
                for agent in self.environment.entities
                if agent.entity_type == "Agent" and not agent.auto_mode and agent.alive
            )
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

        # Draw the grid and entities in one loop
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

                cell = self.environment.grid[x][y]
                if cell.current_image is not None:
                    image = cell.current_image
                    draw_x = x * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
                    draw_y = y * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2
                    screen.blit(image, (draw_x, draw_y))

        # Update the display once
        pygame.display.flip()

    def check_agent_status(self):
        if self.agent and not self.agent.alive:
            self.agent = self.get_next_agent()

    def handle_key_event(self, key):
        direction_map = {
            K_UP: "back",
            K_DOWN: "front",
            K_LEFT: "left",
            K_RIGHT: "right",
        }
        if key in direction_map:
            direction = direction_map[key]
            if self.agent.direction == direction:
                try:
                    self.agent.move(direction)
                except (IndexError, ValueError) as e:
                    print(e)
            self.agent.change_direction(direction)
        elif key == K_SPACE:
            self.agent.attack()

    async def run(self):
        clock = pygame.time.Clock()
        while self.running:
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN and self.agent and not self.agent.auto_mode:
                    self.handle_key_event(event.key)
                    self.key_hold_time = current_time

            if (
                self.agent
                and current_time - self.key_hold_time > self.key_hold_threshold
            ):
                for key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                    if keys[key]:
                        self.handle_key_event(key)
                        self.key_hold_time = current_time
                        break

            self.check_agent_status()
            self.draw_environment()
            clock.tick(30)
            await asyncio.sleep(0)

        pygame.quit()


# Run the game
if __name__ == "__main__":
    game = WumpusGame()
    asyncio.run(game.run())
