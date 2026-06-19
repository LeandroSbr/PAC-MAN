"""Menu class implementation."""
from src.managers.input_manager import InputManager
from src.managers.state_manager import StateManager
from src.managers.resource_manager import ResourceManager
from src.menu.submenus.info import Info
from src.menu.button import Button
from src.menu.text import Text
from src.menu.submenus.highscores import Highscores
from src.utils.enums import AppState
from src.utils.templates import Renderizable

from pygame import Surface, transform
from typing import Callable


class Menu(Renderizable):
    """Menu class implementation.

    Main menu implementation.
    """

    def __init__(self, screen_size: tuple[int, int],
                 resource_manager: ResourceManager,
                 state_manager: StateManager):
        """Initialize the main menu and its submenus.

        Args:
            screen_size: The size of the window surface.
            resource_manager: The resource manager used to load fonts and
                sprites.
            state_manager: The state manager used to change the application
                state.
        """
        self.screen_size = screen_size
        self.font = resource_manager.get_font(50)
        self.button_font = resource_manager.get_font(25)
        self.sm = state_manager
        self.rm = resource_manager
        self.__init_surface()
        self.highscores = Highscores(self.rm, screen_size, self.sm)
        self.info = Info(self.rm, self.sm, screen_size)
        self.__init_frames()
        self.pac_cur_frame = 0
        self.pac_animation_timer = 0
        self.blinky_cur_frame = 0
        self.blinky_animation_timer = 0

    def __init_frames(self) -> None:
        """Load and scale the animated menu frames if they are available."""
        if not self.rm.has_sheet_loaded:
            self.loaded_frames = False
            return
        self.loaded_frames = True
        self.pacman_left = []
        self.blinky_frames = []
        for pac_man, blinky in zip(self.rm.get_frame_resources("pacman_left"),
                                   self.rm.get_frame_resources("blinky")):
            pac_man_scaled_frame = transform.scale(
                    pac_man, (pac_man.get_width() * 6,
                              pac_man.get_height() * 6))
            blinky_scaled_frame = transform.scale(
                    blinky, (blinky.get_width() * 6, blinky.get_height() * 6))
            self.pacman_left.append(pac_man_scaled_frame)
            self.blinky_frames.append(blinky_scaled_frame)
        self.pacman_rect = self.pacman_left[0].get_rect(
            center=(self.screen_size[0] // 4 * 3, self.screen_size[1] // 2))
        self.blinky_rect = self.blinky_frames[0].get_rect(
            center=(self.screen_size[0] // 4, self.screen_size[1] // 2))

    def __init_surface(self) -> None:
        """Create the internal menu surface and its buttons."""
        self.surface = Surface(self.screen_size)
        self.__create_buttons()

    def __draw_surface(self) -> None:
        """Draw the menu surface, buttons, and optional animated sprites."""
        self.surface.fill((5, 10, 15))
        for button in self.renderizables:
            button.render(self.surface)
        if self.loaded_frames:
            self.surface.blit(self.pacman_left[self.pac_cur_frame],
                              self.pacman_rect)
            self.surface.blit(self.blinky_frames[self.blinky_cur_frame],
                              self.blinky_rect)

    def __on_start_game(self) -> None:
        """Switch to the game state when the Play button is pressed."""
        if self.sm.current_state is AppState.MENU:
            self.sm.change_state(AppState.GAME)

    def __on_highscores(self) -> None:
        """Open the highscores submenu when the Scores button is pressed."""
        if self.sm.current_state is AppState.MENU:
            self.sm.change_state(AppState.SCORES)
            self.highscores.draw_scores()
            self.highscores.draw_surface()

    def __on_instructions(self) -> None:
        """Open the info submenu when the Info button is pressed."""
        if self.sm.current_state is AppState.MENU:
            self.sm.change_state(AppState.INFO)

    def __on_exit(self) -> None:
        """Request application shutdown when the Quit button is pressed."""
        if self.sm.current_state is AppState.MENU:
            self.sm.change_state(AppState.QUIT)

    def __create_buttons(self) -> None:
        """Create the menu title and buttons used by the main screen."""
        start_game = self.__on_start_game
        highscores: Callable[[], None] = self.__on_highscores
        instructions = self.__on_instructions
        exit = self.__on_exit

        self.renderizables: list[Renderizable] = []
        center_x = self.screen_size[0] // 2
        pos_y = self.screen_size[1] // 7
        self.renderizables.append(Text("PAC-MAN",
                                       self.font, (center_x, pos_y),
                                       color=(252, 234, 63)))
        self.renderizables.append(Button(
            "Play", (center_x, pos_y * 2 + 50),
            self.button_font, start_game)
        )
        self.renderizables.append(Button(
            "Scores", (center_x, pos_y * 3 + 50),
            self.button_font, highscores)
        )
        self.renderizables.append(Button(
            "Info", (center_x, pos_y * 4 + 50),
            self.button_font, instructions)
        )
        self.renderizables.append(Button(
            "Quit", (center_x, pos_y * 5 + 50),
            self.button_font, exit)
        )
        self.buttons: list[Button] = []
        for renderizable in self.renderizables:
            if isinstance(renderizable, Button):
                self.buttons.append(renderizable)
            renderizable.render(self.surface)

    def update(self, delta_t: int) -> None:
        """Advance animations and redraw the menu surface.

        Args:
            delta_t: The elapsed time since the previous update.
        """
        self.pac_animation_timer += delta_t
        if self.pac_animation_timer >= 50:
            self.pac_cur_frame = (self.pac_cur_frame + 1) % 4
            self.pac_animation_timer = 0
        self.blinky_animation_timer += delta_t
        if self.blinky_animation_timer >= 100:
            self.blinky_cur_frame = (self.blinky_cur_frame + 1) % 4
            self.blinky_animation_timer = 0
        self.__draw_surface()

    def update_highscores(self) -> None:
        """Redraw the highscores submenu surface."""
        self.highscores.draw_surface()

    def update_info(self) -> None:
        """Redraw the information submenu surface."""
        self.info.redraw()

    def register_buttons(self, input_manager: InputManager) -> None:
        """Register all menu and submenu buttons with the input manager.

        Args:
            input_manager: The input manager that dispatches mouse events.
        """
        for button in self.buttons:
            input_manager.register_on_click_observer(button.on_click)
            input_manager.register_on_hover_observer(button.on_hover)
        for button in self.highscores.buttons:
            input_manager.register_on_click_observer(button.on_click)
            input_manager.register_on_hover_observer(button.on_hover)
        for button in self.info.buttons:
            input_manager.register_on_click_observer(button.on_click)
            input_manager.register_on_hover_observer(button.on_hover)

    def unregister_buttons(self, input_manager: InputManager) -> None:
        """Unregister all menu and submenu buttons from the input manager.

        Args:
            input_manager: The input manager that dispatches mouse events.
        """
        for button in self.buttons:
            input_manager.unregister_on_click_observer(button.on_click)
            input_manager.unregister_on_hover_observer(button.on_hover)
        for button in self.highscores.buttons:
            input_manager.unregister_on_click_observer(button.on_click)
            input_manager.unregister_on_hover_observer(button.on_hover)
        for button in self.info.buttons:
            input_manager.unregister_on_click_observer(button.on_click)
            input_manager.unregister_on_hover_observer(button.on_hover)

    @property
    def show_menu(self) -> list[Renderizable]:
        """Return the renderable objects for the main menu view."""
        return [self]

    @property
    def show_highscores(self) -> list[Renderizable]:
        """Return the renderable objects for the highscores view."""
        return self.highscores.representation

    @property
    def show_info(self) -> list[Renderizable]:
        """Return the renderable objects for the information view."""
        return self.info.representation

    def get_buttons(self) -> list[Button]:
        """Return the buttons used by the main menu view."""
        return self.buttons

    def render(self, surface: Surface) -> None:
        """Blit the menu surface onto the target surface.

        Args:
            surface: The surface that receives the menu rendering.
        """
        surface.blit(self.surface, (0, 0))
