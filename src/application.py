"""Main application controller and game loop.

Manages initialization of all game subsystems, coordinates state transitions,
and runs the main game loop that processes input and renders frames.
"""
from src.game_over.game_over import GameOver
from src.menu.menu import Menu
from src.render.renderer import Renderer
from src.managers.resource_manager import ResourceManager
from src.managers.state_manager import StateManager
from src.managers.input_manager import InputManager
from src.utils.enums import AppState
from src.utils.enums import Action
from src.game.game import World

import pygame


class Application:
    """Main game application controller.

    Manages the game loop, coordinates all subsystems (rendering, input,
    state management), and handles transitions between game states.
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the application and wire all major subsystems.

        Args:
            config_path: Path to the configuration file used by the resource
                manager.
        """
        self.running = True
        pygame.init()
        self.clock = pygame.time.Clock()
        self.renderer = Renderer()
        self.state_manager = StateManager()
        self.input_manager = InputManager(self.state_manager)
        self.resource_manager = ResourceManager(config_path)
        self.screen_info = pygame.display.Info()
        self.screen_size = (self.screen_info.current_w,
                            self.screen_info.current_h)
        self.menu = Menu(self.screen_size, self.resource_manager,
                         self.state_manager)
        self.world = World(self.screen_size, self.resource_manager,
                           self.state_manager)
        self.gg = GameOver(self.state_manager, self.input_manager,
                           self.resource_manager, self.screen_size)
        self.game_state = AppState.MENU

        self.state_manager.register_observer(self.__change_state)
        self.state_manager.register_observer(self.input_manager.set_app_state)
        self.input_manager.register_observer(self.__handle_actions)
        self.input_manager.register_observer(self.world.handle_actions)
        self.input_manager.register_event_observer(self.gg.handle_events)
        self.world.register_buttons(self.input_manager)
        self.menu.register_buttons(self.input_manager)
        self.gg.register_buttons(self.input_manager)

    def __change_state(self, new_state: AppState) -> None:
        """Update the current application state.

        Args:
            new_state: The new application state to activate.
        """
        self.game_state = new_state

    def __handle_actions(self, action: Action) -> None:
        """Handle application-level actions from the input manager.

        Args:
            action: The action produced by the input manager.
        """
        if action is Action.QUIT:
            self.state_manager.change_state(AppState.QUIT)

    def run(self) -> None:
        """Run the main application loop until the program exits."""
        delta_t = 0
        while self.running:

            self.input_manager.update()
            self.input_manager.send_actions()

            if self.game_state is AppState.MENU:
                self.menu.update(delta_t)
                self.renderer.render(self.menu.show_menu)

            elif self.game_state is AppState.SCORES:
                self.menu.update_highscores()
                self.renderer.render(self.menu.show_highscores)

            elif self.game_state is AppState.INFO:
                self.menu.update_info()
                self.renderer.render(self.menu.show_info)

            elif self.game_state is AppState.GAME:
                self.world.update(delta_t)
                self.renderer.render(self.world.representation)

            elif self.game_state is AppState.GAME_OVER:
                self.gg.update(self.world.get_score())
                self.renderer.render(self.gg.representation)

            elif self.game_state is AppState.QUIT:
                self.running = False

            delta_t = self.clock.tick(120)
        self.resource_manager.serialize_scores()
        pygame.quit()
