"""Game world management and state control for Pac-Man game.

Implements the main game loop, entity management, collision detection,
and game state transitions.
"""
from src.game.game_objects.entities.entity import Entity
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.entities.player import Player
from src.game.game_objects.maze import Maze
from src.game.game_objects.cell import Cell
from src.game.game_objects.game_data import GameData
from src.game.game_pause.game_pause import GamePause
from src.managers.state_manager import StateManager
from src.managers.ghost_manager import GhostManager
from src.managers.input_manager import InputManager
from src.managers.resource_manager import ResourceManager
from src.menu.text import Text
from src.hud.hud_object import HudObject
from src.hud.dynamic_score import DynamicScore
from src.utils.enums import Action, Dir, GhostState, AppState, GameState
from src.utils.macros import TIMEREVENT
from src.utils.templates import Renderizable

from mazegenerator import MazeGenerator
from sys import exit
from pygame import Surface, SRCALPHA, draw, quit
from pygame.time import set_timer


def format_time(seconds: int) -> str:
    """Convert seconds to formatted time string in MM:SS format.

    Args:
        seconds (int): Total seconds to convert.

    Returns:
        str: Time formatted as 'MM:SS' with zero-padding.
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


class World:
    """Manage the game world, entities, and game state transitions.

    Coordinates the player and ghost entities, handles collision detection,
    manages level progression, updates game state, and provides rendering data
    for the current game frame.
    """

    def __init__(self, screen_size: tuple[int, int],
                 rm: ResourceManager,
                 sm: StateManager) -> None:
        """Initialize the game.

        Args:
            screen_size (tuple[int, int]): size of the screen surface.
            rm (ResourceManager): resources manager to get sprites.
            sm (StateManager): manager that changes AppState.
        """
        self.screen_size = screen_size
        self.sm = sm
        self.rm = rm
        self.config = rm.config
        self.pause_screen = GamePause(screen_size, self.__unpause,
                                      self.__back_to_menu, self.cheat,
                                      sm, rm)
        self.font = self.rm.get_font(36)
        self.level_font = self.rm.get_font(30)
        self.animating = False
        self.animation_timer = 2000
        self.level = 1
        self.final_score: int
        self.__score: DynamicScore
        self.__seeds = self.config.get("level", [])
        self.__generate_maze()
        self.__generate_player()
        self.game_data = GameData(self.maze, self.player, self.level)
        self.ghost_manager = GhostManager(self.game_data, rm)
        self.__init_maze_entities()
        self.__set_up_timer()
        self.__init_hud_objects()
        self.maze.draw_entities(self.__maze_entities)
        self.running = True
        self.state = GameState.READY
        self.prev_state: GameState = GameState.READY

    def get_score(self) -> int:
        """Return the final score of the game.

        Returns:
            int: the final score
        """
        return self.final_score

    def __reset_game(self) -> None:
        """Reset the game to initial state and generate a new maze.

        Recreates the maze, resets player and ghost positions, reinitializes
        timers and HUD, and preserves score.
        """
        self.__generate_maze()
        for entity in self.__maze_entities:
            entity.reset_maze(self.maze.maze_map[entity.get_spawn_coord()])
        self.game_data.change_maze(self.maze)
        self.game_data.change_level(self.level)
        self.__reset_positions()
        self.final_score = self.player.points
        self.__set_up_timer()
        self.__timer_update()
        self.__init_hud_objects()

    def cheat(self) -> None:
        """Enable/Disable cheat mode."""
        self.player.is_cheating = not self.player.is_cheating

    def loss(self) -> None:
        """Reset game after loss and return to initial state.

        Resets the maze, player lives, level, and score, then reinitializes
        the HUD.
        """
        self.__reset_game()
        self.player.reset_lives()
        self.level = 1
        self.player.points = 0
        self.player.reset_collectible_count()
        self.__score.update_score(0)
        self.__init_hud_objects()
        self.__reset_animations()

    def register_buttons(self, im: InputManager) -> None:
        """Register all buttons in the input manager to recieve inputs.

        Args:
            im (InputManager): the manager that manages inputs.
        """
        self.pause_screen.register_buttons(im)

    def __set_up_timer(self) -> None:
        """Set up the timer."""
        self.sec_time = self.config.get("level_max_time", 90)
        set_timer(TIMEREVENT, 1000)

    def __init_hud_objects(self) -> None:
        """Create the game hud."""
        if self.rm.has_sheet_loaded:
            pacman_image = self.rm.get_resource("pacman_hud")
        else:
            pacman_image = Surface((30, 30), SRCALPHA)
            pacman_image.fill((0, 0, 0, 0))
            draw.circle(pacman_image, (255, 255, 0), (15, 15), 15)

        pac_x = ((self.screen_size[0] - self.maze.size[0]) / 4
                 - pacman_image.get_width() * 3 / 2)
        pac_x = int(pac_x)
        start_pac_x = pac_x
        pac_y = self.screen_size[1] - pacman_image.get_rect().height - 50

        pac_y = int(pac_y)
        self.__score = DynamicScore(self.font, (pac_x, 10), self.player.points)
        self.__level = Text(
            f"Level: {self.level}", self.level_font,
            (self.screen_size[0] - pac_x, self.screen_size[1] // 2))
        self.__timer = Text(format_time(self.sec_time), self.font,
                            (self.screen_size[0] - pac_x, 25))

        self.lives_list: list[HudObject] = []
        i = 0
        for _ in range(self.player.get_lives()):
            self.lives_list.append(HudObject(pacman_image,
                                             (pac_x, pac_y)))
            pac_x += int(pacman_image.get_rect().width * 1.5)
            i += 1
            if i == 5:
                pac_x = start_pac_x
                pac_y -= int(pacman_image.get_rect().height * 1.5)
                i = 0

    def update(self, delta_t: int) -> None:
        """Update the world state based on delta_t.

        Args:
            delta_t (int): the time passed since last call.
        """
        match self.state:

            case GameState.READY:
                if self.animation_timer > 0:
                    self.animation_timer -= delta_t
                    self.animating = True
                    self.maze.draw_entities(self.__maze_entities)
                    return
                self.state = GameState.ONGOING

            case GameState.ONGOING:
                self.player.move(delta_t)
                self.ghost_manager.update(delta_t)
                self.maze.draw_entities(self.__maze_entities)
                self.__handle_collisions()
                if self.game_data.has_score_changed():
                    self.__score.update_score(self.game_data.get_score())
                if self.player.win():
                    self.animation_timer = 2000
                    self.state = GameState.WON

            case GameState.DEATH_ANIMATION:
                if self.player.death_animation(delta_t):
                    self.state = GameState.ONGOING
                    if self.player.is_alive():
                        if len(self.lives_list) > 0:
                            self.lives_list.pop()
                        self.__reset_positions()
                        self.maze.draw_maze_surface()
                        self.maze.draw_entities(self.__maze_entities)
                    else:
                        self.animation_timer = 2000
                        self.state = GameState.LOST
                else:
                    self.maze.draw_entities(self.__maze_entities)

            case GameState.PAUSED:
                self.pause_screen.update_view()

            case GameState.WON:
                if self.animation_timer > 0:
                    self.animation_timer -= delta_t
                else:
                    self.__generate_new_level()
                    self.state = GameState.READY

            case GameState.LOST:
                if self.animation_timer > 0:
                    self.animation_timer -= delta_t
                else:
                    self.state = GameState.QUIT

            case GameState.QUIT:
                self.loss()
                self.state = GameState.READY
                self.sm.change_state(AppState.GAME_OVER)

    def __timer_update(self) -> None:
        """Update the timer."""
        if self.sec_time <= 0:
            self.animation_timer = 2000
            self.state = GameState.LOST
        else:
            self.__timer = Text(
                format_time(self.sec_time), self.font,
                self.__timer.rect.center
            )

    def __init_maze_entities(self) -> None:
        """Create the list of entities."""
        self.__maze_entities: list[Entity] = [self.player]
        self.__maze_entities.extend(self.ghost_manager.ghosts)

    def __generate_maze(self) -> None:
        """Generate the maze layout and instantiate the maze object."""
        size = self.config.get("size", (15, 15))

        self.size = (size[0], size[1])
        try:
            if self.level < len(self.__seeds):
                seed = self.__seeds[self.level - 1]
            else:
                seed = -1
            gen = MazeGenerator(self.size, seed=seed)
        except Exception:
            print("\033[31mMaze generation error\033[0m")
            quit()
            exit(1)

        self.layout = gen.maze
        self.maze = Maze(self.layout, self.screen_size, self.rm, self.size)

    def __generate_player(self) -> None:
        """Create the player at the maze spawn position."""
        start_cell: Cell = self.maze.maze_map[((self.size[1] - 1) // 2),
                                              (self.size[0] - 1) // 2]
        self.player = Player(start_cell, self.maze.get_pellet_amount(),
                             self.rm, self.config.get("lives", 3))

    def handle_actions(self, action: Action) -> None:
        """Handle a single input action for the current game state."""
        if self.sm.current_state is not AppState.GAME:
            return
        if self.state is GameState.ONGOING:
            if action is Action.MOVE_UP:
                self.player.set_next_dir(Dir.NORTH)
            elif action is Action.MOVE_DOWN:
                self.player.set_next_dir(Dir.SOUTH)
            elif action is Action.MOVE_LEFT:
                self.player.set_next_dir(Dir.WEST)
            elif action is Action.MOVE_RIGHT:
                self.player.set_next_dir(Dir.EAST)
            elif action is Action.TIMERDOWN:
                self.sec_time -= 1
                self.__timer_update()
            if self.player.is_cheating:
                if action is Action.CHANGE_LEVEL:
                    self.animation_timer = 2000
                    self.state = GameState.WON
                elif action is Action.FREEZE_GHOSTS:
                    self.ghost_manager.set_freeze()
                elif action is Action.LIVES_UP:
                    self.player.add_life()
                    self.__init_hud_objects()
                elif action is Action.INCREASE_SPEED:
                    self.player.increase_speed()
                elif action is Action.DECREASE_SPEED:
                    self.player.decrease_speed()
                elif action is Action.RESET_SPEED:
                    self.player.reset_speed()
        if action is Action.PAUSE:
            self.__pause_unpause()
        elif action is Action.SKIP_ANIMATION:
            self.animation_timer = 0

    def __pause_unpause(self) -> None:
        """Toggle between paused and running states."""
        if self.state is not GameState.PAUSED:
            self.__pause()
        elif self.state is GameState.PAUSED:
            self.pause_screen.reset_view()
            self.__unpause()

    def __pause(self) -> None:
        """Store the current state and switch to paused."""
        self.prev_state = self.state
        self.state = GameState.PAUSED

    def __unpause(self) -> None:
        """Restore the state that was active before pausing."""
        self.state = self.prev_state

    def __back_to_menu(self) -> None:
        """Mark the world for a transition back to the main menu."""
        self.state = GameState.QUIT

    @property
    def representation(self) -> list[Renderizable]:
        """Return the renderable objects for the current frame."""
        rep = self.lives_list + [self.__score, self.maze, self.__timer,
                                 self.__level]
        if self.state is GameState.ONGOING:
            return rep
        elif self.state is GameState.PAUSED:
            rep.append(self.pause_screen)
            return rep
        elif self.state is GameState.READY:
            rep.append(Text("READY!", self.font,
                       (self.screen_size[0] // 2,
                        self.screen_size[1] // 2 - 100),
                       (255, 255, 0)))
            return rep
        elif self.state is GameState.WON:
            rep.append(Text("Level Completed!", self.font,
                       (self.screen_size[0] // 2, self.screen_size[1] // 2),
                       (0, 255, 0)))
            return rep
        elif self.state is GameState.LOST:
            rep.append(Text("Game Over!", self.font,
                       (self.screen_size[0] // 2, self.screen_size[1] // 2),
                       (255, 0, 0)))
            return rep
        elif self.state is GameState.QUIT:
            return rep
        return rep

    def __handle_collisions(self) -> None:
        """Manage collision between ghost and player."""
        ghosts = self.ghost_manager.ghosts
        if any((ghost.died for ghost in ghosts)):
            self.maze.draw_maze_surface()
            self.maze.draw_entities(self.__maze_entities)
        collisions = self.player.rect.collideobjectsall(ghosts)
        if not any(collisions):
            return

        if self.ghost_manager.ghost_state is GhostState.FEAR:
            self.__handle_ghosts_eaten(collisions)
        else:
            self.__handle_player_hit()

    def __handle_ghosts_eaten(self, ghosts: list[Ghost]) -> None:
        """Process ghosts eaten by player during fear state.

        Args:
            ghosts (list[Ghost]): List of ghosts colliding with player.
        """
        for ghost in ghosts:

            if not ghost.died:
                self.player.eat_ghost()
                ghost.die()

    def __handle_player_hit(self) -> None:
        """Process player collision with ghost.

        Deducts life from player (unless in cheat mode) and triggers
        death animation state.
        """
        if self.player.is_cheating:
            return
        self.player.lose_life()

        self.state = GameState.DEATH_ANIMATION

    def __reset_positions(self) -> None:
        """Reset player and all ghosts to their spawn positions.

        Triggers respawn animations and redraws the maze surface.
        """
        self.animation_timer = 2000
        self.player.respawn()
        self.ghost_manager.respawn_all_ghosts()

    def __generate_new_level(self) -> None:
        """Advance to the next level with an updated maze.

        Increments level counter, resets collectibles, and reinitializes
        the game state.
        """
        self.level += 1
        self.animation_timer = 1000
        self.player.reset_collectible_count(self.maze.get_pellet_amount())
        self.__reset_game()

    def __reset_animations(self) -> None:
        """Reset animation states for player and all ghosts.

        Clears any active animations from death, eating, or movement.
        """
        self.player.reset_animation()
        self.ghost_manager.reset_animations()
