# FILE: main.py
import pygame
from pygame.locals import *
from environment import Environment
import asyncio  # Necessary for pygbag
import csv
from datetime import datetime
from environment.entities import Wumpus, Gold

# Run pygbag main.py to play the game in the browser

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 900, 900
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World")

# Define colors
GRID_COLOR = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)
CELL_REVEAL_COLOR = (30, 30, 30)


# Define the game class
class WumpusGame:
    """
    A class to represent the Wumpus World game.

    Attributes:
    -----------
    environment : Environment
        The game environment.
    agent : Agent
        The current agent in the game.
    running : bool
        The game running state.
    key_hold_time : int
        The time a key has been held down.
    key_hold_threshold : int
        The threshold time for key hold.
    all_agents : list
        List to keep track of all agents and their scores.
    """

    def __init__(self):
        """
        Initialize the WumpusGame class.
        """
        # Initialize the environment and agent
        self.environment = Environment(size=GRID_SIZE, cell_size=CELL_SIZE)
        # Search the first agent with auto_mode set to False
        self.agent = self.get_next_agent()
        self.game_over = False  # Add a game_over flag
        self.restart_button = pygame.Rect(
            WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 50
        )  # Define the restart button

        self.running = True
        self.key_hold_time = 0  # start time of key hold in milliseconds
        self.key_hold_threshold = 150  # milliseconds

        # Model created at https://hyperhuman.deemos.com/rodin

        # List to keep track of all agents and their scores
        self.all_agents = []

        # Interval for calling the act function (default 1 second)
        self.act_interval = 1000  # 1000  # milliseconds
        self.last_act_time = 0  # last time the act function was called

        self.DEBUG = True
        self.debug_allow_next_step = True

    def get_next_agent(self):
        """
        Get the next agent with auto_mode set to False.

        Returns:
        --------
        Agent or None
            The next agent or None if no agent is found.
        """
        try:
            return next(
                agent
                for agent in self.environment.entities
                if agent.entity_type == "Agent" and not agent.auto_mode and agent.alive
            )
        except StopIteration:
            print("No alive agent with auto_mode set to False found.")
            return None

    def draw_environment(self):
        """
        Draw the game environment including the grid and entities.
        """
        # Clear the screen
        screen.fill(BACKGROUND_COLOR)

        # Draw the grid and entities in one loop
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

                cell = self.environment.grid[x][y]
                if cell.visible:
                    pygame.draw.rect(
                        screen, CELL_REVEAL_COLOR, rect
                    )  # Fill with grey color

                if cell.current_image is not None:
                    image = cell.current_image
                    draw_x = x * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
                    draw_y = y * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2
                    screen.blit(image, (draw_x, draw_y))

        # Draw the scoreboard
        self.draw_scoreboard()

        # Draw the game over label if the game is over
        if self.game_over:
            self.draw_game_over_label()
            self.draw_restart_button()

        # Update the display once
        pygame.display.flip()

    def draw_game_over_label(self):
        """
        Draw the game over label.
        """

        total_score = self.environment.entity_counts[Wumpus] * 1000 + self.environment.entity_counts[Gold] * 100
        agent_score = sum([agent.score for agent in self.environment.entities if agent.entity_type == 'Agent'])
        font = pygame.font.Font(None, 72)
        game_over_text1 = "Agents decided to end the game"
        game_over_text2 = f"Score: {agent_score} / {total_score} points"
        text_surface1 = font.render(game_over_text1, True, (255, 0, 0))
        screen.blit(
            text_surface1,
            (
                WIDTH // 2 - text_surface1.get_width() // 2,
                HEIGHT // 3 - text_surface1.get_height() // 2,
            ),
        )
        text_surface2 = font.render(game_over_text2, True, (255, 0, 0))
        screen.blit(
            text_surface2,
            (
                WIDTH // 2 - text_surface2.get_width() // 2,
                HEIGHT // 2 - text_surface2.get_height() // 2,
            ),
        )

    def draw_restart_button(self):
        """
        Draw the restart button.
        """
        font = pygame.font.Font(None, 36)
        pygame.draw.rect(screen, (255, 255, 255), self.restart_button)
        restart_text = "Restart"
        text_surface = font.render(restart_text, True, (0, 0, 0))
        screen.blit(
            text_surface,
            (
                self.restart_button.x
                + (self.restart_button.width - text_surface.get_width()) // 2,
                self.restart_button.y
                + (self.restart_button.height - text_surface.get_height()) // 2,
            ),
        )

    def draw_scoreboard(self):
        """
        Draw the scoreboard for the top 3 agents alive.
        """
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

        # Draw the scores
        for agent in top_agents:
            score_text = f"Agent {agent.position}: {agent.score}"
            text_surface = font.render(score_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 40

    def check_agent_status(self):
        """
        Check if the agent is alive and if not, remove it, but save it to the list.
        """
        if self.agent and not self.agent.alive:
            # Save the agent before removing
            self.all_agents.append(self.agent)
            self.agent = self.get_next_agent()

        # Check if the game is over
        if self.environment.game_over:
            self.game_over = True  # Set the game_over flag

    def handle_key_event(self, key, no_agent=False):
        """
        Handle key events for user input to move the agent.

        Parameters:
        -----------
        key : int
            The key code of the pressed key.
        """
        if self.game_over:
            return  # Prevent agents from moving after game over

        # Define the possible directions
        direction_map = {
            K_UP: "back",
            K_DOWN: "front",
            K_LEFT: "left",
            K_RIGHT: "right",
        }
        # Check if the key is a valid direction
        if not no_agent:
            if key in direction_map:
                direction = direction_map[key]
                if self.agent.direction == direction:
                    try:
                        self.agent.act(f"move_{direction}")
                    except (IndexError, ValueError) as e:
                        print(e)
                self.agent.change_direction(direction)
            # Check if the key is Space for attacking or Enter for collecting
            elif key == K_SPACE:
                self.agent.act("attack")
            elif key == K_RETURN:
                self.agent.act("collect")
            elif key == K_c:
                self.agent.act("communicate")
        else:

            # game controll
            if key == K_d:
                self.DEBUG = not self.DEBUG
            elif key == K_s and self.DEBUG and not self.debug_allow_next_step:
                self.debug_allow_next_step = True

    async def run(self):
        """
        Run the main game loop.
        """
        # Set up the clock for event handling and frame rate
        clock = pygame.time.Clock()
        # Main game loop
        while self.running:

            # Get the current time and pressed keys
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()

            # Handle events iteratively
            for event in pygame.event.get():
                # Check if the event is a quit event
                if event.type == QUIT:
                    self.running = False
                # Check if the event is a key press event for a selected agent
                elif event.type == KEYDOWN and self.agent:
                    self.handle_key_event(event.key)
                    self.key_hold_time = current_time

                if event.type == KEYDOWN:
                    self.handle_key_event(event.key, no_agent=True)

                if event.type == MOUSEBUTTONDOWN and self.game_over:
                    if self.restart_button.collidepoint(event.pos):
                        self.restart_game()
            # Check if the agent is set and the key is held
            if (
                self.agent
                and current_time - self.key_hold_time > self.key_hold_threshold
            ):
                for key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                    if keys[key]:
                        self.handle_key_event(key)
                        self.key_hold_time = current_time
                        break

            if (self.DEBUG and self.debug_allow_next_step) or not self.DEBUG:
                if self.debug_allow_next_step:
                    self.debug_allow_next_step = False

                # Call act for every agent in auto mode at the specified interval
                if (
                    not self.game_over
                    and current_time - self.last_act_time >= self.act_interval
                ):
                    print(
                        "------------------------------------- SIM STEP --------------------------------------------"
                    )
                    for agent in self.environment.entities:
                        if (
                            agent.entity_type == "Agent"
                            and agent.auto_mode
                            and agent.alive
                        ):
                            agent.act()
                    self.last_act_time = current_time

                self.check_agent_status()
                self.draw_environment()
            clock.tick(30)
            await asyncio.sleep(0)

        self.save_scores_to_csv()
        # pygame.quit()

    def restart_game(self):
        """
        Restart the game by reinitializing the game state.
        """
        self.__init__()  # Reinitialize the game state
        asyncio.create_task(self.run())  # Schedule the game loop

    def save_scores_to_csv(self):
        """
        Save the scores of all agents to a CSV file.
        """
        # Add remaining agents to the list
        self.all_agents.extend(
            agent for agent in self.environment.entities if agent.entity_type == "Agent"
        )

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Define the filename for the scoreboard
        filename = "scoreboard.csv"

        # Check if the file exists to determine if we need to write the header
        try:
            with open(filename, mode="r") as file:
                file_exists = True
        except FileNotFoundError:
            file_exists = False

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
