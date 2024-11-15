# FILE: main.py
import pygame
from pygame.locals import *
from environment import Environment
from agent import Agent
import asyncio # Necessary for pygbag

# Run pygbag main.py to play the game in the browser

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World")


def load_and_scale_image(image_path, cell_size):
    image = pygame.image.load(image_path)
    original_width, original_height = image.get_size()
    scaling_factor = min(cell_size / original_width, cell_size / original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    return pygame.transform.smoothscale(image, (new_width, new_height))


def calculate_draw_position(x, y, image):
    image_width, image_height = image.get_size()
    draw_x = x * CELL_SIZE + (CELL_SIZE - image_width) // 2
    draw_y = y * CELL_SIZE + (CELL_SIZE - image_height) // 2
    return draw_x, draw_y


# Define the game class
class WumpusGame:
    def __init__(self):
        # Load all images
        self.agent_image = load_and_scale_image("src/agent.png", CELL_SIZE)
        self.wumpus_image = load_and_scale_image("src/wumpus_discord.png", CELL_SIZE)
        # self.pit_image = load_and_scale_image('src/pit.png', CELL_SIZE)
        # self.gold_image = load_and_scale_image('src/gold.png', CELL_SIZE)

        # Initialize the environment and agent
        self.environment = Environment(size=GRID_SIZE)
        self.agent = Agent(self.environment)
        self.running = True
        self.key_hold_time = 0
        self.key_hold_threshold = 500  # milliseconds

    def draw_grid(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    def draw_agent(self):
        x, y = self.agent.position
        draw_x, draw_y = calculate_draw_position(x, y, self.agent_image)
        screen.blit(self.agent_image, (draw_x, draw_y))

    def draw_environment(self):
        for x in range(self.environment.size):
            for y in range(self.environment.size):
                cell_content = self.environment.grid[x][y]
                if cell_content.entity is None:
                    continue
                if cell_content.entity.type == "Wumpus":
                    image = self.wumpus_image
                elif cell_content == "P":
                    image = self.pit_image
                elif cell_content == "G":
                    image = self.gold_image
                else:
                    continue

                draw_x, draw_y = calculate_draw_position(x, y, image)
                screen.blit(image, (draw_x, draw_y))

    async def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if not self.agent.auto_mode:
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
                    self.key_hold_time = pygame.time.get_ticks()

            keys = pygame.key.get_pressed()
            if not self.agent.auto_mode:
                current_time = pygame.time.get_ticks()
                if current_time - self.key_hold_time > self.key_hold_threshold:
                    try:
                        if keys[K_UP]:
                            self.agent.move("up")
                        if keys[K_DOWN]:
                            self.agent.move("down")
                        if keys[K_LEFT]:
                            self.agent.move("left")
                        if keys[K_RIGHT]:
                            self.agent.move("right")
                    except IndexError as e:
                        print(e)
                    except ValueError as e:
                        print(e)

            screen.fill((0, 0, 0))
            self.draw_grid()
            self.draw_environment()
            self.draw_agent()
            pygame.display.flip()
            clock.tick(30)
            await asyncio.sleep(0)

        pygame.quit()


# Run the game
if __name__ == "__main__":
    game = WumpusGame()
    asyncio.run(game.run())
