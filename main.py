# FILE: main.py
import pygame
from pygame.locals import *
from environment.core.environment import Environment
import asyncio  # Necessary for pygbag
import csv
from datetime import datetime

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

        # Model created at https://hyperhuman.deemos.com/rodin

        # List to keep track of all agents and their scores
        self.all_agents = []

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

        # Draw the scoreboard
        self.draw_scoreboard()

        # Update the display once
        pygame.display.flip()

    def draw_scoreboard(self):
        font = pygame.font.Font(None, 36)
        y_offset = 10

        # Draw the header
        header_text = "Top 3 Agent Scores"
        header_surface = font.render(header_text, True, (255, 255, 255))
        screen.blit(header_surface, (10, y_offset))
        y_offset += 40

        # Get the top 3 agents by score
        top_agents = sorted(
            [
                agent
                for agent in self.environment.entities
                if agent.entity_type == "Agent"
            ],
            key=lambda a: a.score,
            reverse=True,
        )[:3]

        for agent in top_agents:
            score_text = f"Agent {agent.position}: {agent.score}"
            text_surface = font.render(score_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 40

    def check_agent_status(self):
        if self.agent and not self.agent.alive:
            self.all_agents.append(self.agent)  # Save the agent before removing
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
        elif key == K_RETURN:
            self.agent.collect()

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

        self.save_scores_to_csv()
        pygame.quit()

    def save_scores_to_csv(self):
        # Add remaining agents to the list
        self.all_agents.extend(
            agent for agent in self.environment.entities if agent.entity_type == "Agent"
        )

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Define the filename for the scoreboard
        filename = "scoreboard.csv"

        # Check if the file exists to determine if we need to write the header
        file_exists = False
        try:
            with open(filename, mode="r") as file:
                file_exists = True
        except FileNotFoundError:
            pass

        # Write the scores to the CSV file
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "Agent Position", "Score"])
            for agent in self.all_agents:
                writer.writerow([timestamp, agent.position, agent.score])


# Run the game
if __name__ == "__main__":
    game = WumpusGame()
    asyncio.run(game.run())
