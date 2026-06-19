"""Game Pause menu implementation."""
from src.managers.input_manager import InputManager
from src.managers.resource_manager import ResourceManager
from src.menu.button import Button
from src.menu.text import Text
from src.managers.state_manager import StateManager
from src.utils.enums import AppState, View
from src.utils.templates import Renderizable

from typing import Callable
from pygame import Surface, SRCALPHA, transform


class GamePause(Renderizable):
    """Game Pause Implementation.

    Implement Game Pause menu, that switch between pause menu and
    extra menu, where cheat mode can be enabled/disabled.
    """

    def __init__(self, screen_size: tuple[int, int],
                 unpause: Callable[[], None],
                 back_to_menu: Callable[[], None],
                 cheat: Callable[[], None],
                 sm: StateManager, rm: ResourceManager):
        """Initialize the pause overlay and its subviews.

        Args:
            screen_size: The size of the window surface.
            unpause: Callback used to resume the game.
            back_to_menu: Callback used to return to the main menu.
            cheat: Callback used to toggle cheat mode.
            sm: The state manager used to check the active app state.
            rm: The resource manager used to load fonts and sprites.
        """
        self.screen_size = screen_size
        self.sm = sm
        self.rm = rm
        self.unpause = unpause
        self.back_to_menu = back_to_menu
        self.cheat_func = cheat
        self.cheating = False
        self.bg_pause = Surface(screen_size, SRCALPHA)
        self.bg_pause.fill((0, 0, 0, 128))
        self.current_view = View.PAUSE
        self.__init_menu()
        self.__init_extra()

    def update_view(self) -> None:
        """Redraw the active pause submenu on the overlay surface."""
        if self.current_view is View.EXTRA:
            self.bg_pause.fill((0, 0, 0, 128))
            self.bg_pause.blit(self.extra_surface, self.extra_rect)
            for button in self.extra_buttons:
                button.render(self.bg_pause)

        elif self.current_view is View.PAUSE:
            self.bg_pause.fill((0, 0, 0, 128))
            self.bg_pause.blit(self.menu_surface, self.menu_rect)
            for button in self.buttons:
                button.render(self.bg_pause)

    def change_view(self) -> None:
        """Toggle between the main pause menu and the extra menu."""
        if self.current_view is View.PAUSE:
            self.current_view = View.EXTRA
            self.update_view()

        elif self.current_view is View.EXTRA:
            self.current_view = View.PAUSE
            self.update_view()

    def reset_view(self) -> None:
        """Return to the default pause menu view."""
        self.current_view = View.PAUSE
        self.update_view()

    def __init_menu(self) -> None:
        """Build the main pause menu surface and its buttons."""
        menu_size = (self.screen_size[0] // 3, self.screen_size[1] // 3 * 2)
        self.menu_surface = Surface(menu_size)
        screen_center = (self.screen_size[0] // 2, self.screen_size[1] // 2)
        self.menu_rect = self.menu_surface.get_rect(center=screen_center)
        self.menu_surface.fill((10, 15, 20))

        x_local = self.menu_rect.width // 2
        y_local = self.menu_rect.height // 6
        center_x = self.menu_rect.x + x_local
        pos_y = self.menu_rect.y + y_local

        Text("PAUSE", self.rm.get_font(40),
             (x_local, y_local),
             (252, 234, 63)).render(self.menu_surface)
        self.buttons: list[Button] = []
        self.buttons.append(Button(
            "Resume game",
            (center_x, pos_y + (y_local)),
            self.rm.get_font(25), (
                lambda: self.unpause()
                if (self.sm.current_state is AppState.GAME and
                    self.current_view is View.PAUSE) else None)
            ))

        self.buttons.append(Button(
            "Extra",
            (center_x, pos_y + (y_local * 2)),
            self.rm.get_font(25), (
                lambda: self.change_view()
                if (self.sm.current_state is AppState.GAME and
                    self.current_view is View.PAUSE) else None)
            ))

        self.buttons.append(Button(
            "Back to menu", (center_x, pos_y + (y_local * 3)),
            self.rm.get_font(25),
            lambda: self.back_to_menu()
            if (self.sm.current_state is AppState.GAME and
                self.current_view is View.PAUSE) else None
        ))
        self.buttons.append(Button(
            "Quit", (center_x, pos_y + (y_local * 4)),
            self.rm.get_font(25),
            lambda: self.sm.change_state(AppState.QUIT)
            if (self.sm.current_state is AppState.GAME and
                self.current_view is View.PAUSE) else None
        ))

        self.bg_pause.blit(self.menu_surface, self.menu_rect)
        for button in self.buttons:
            button.render(self.bg_pause)

    def cheat(self) -> None:
        """Toggle cheat mode and update the extra menu label."""
        self.cheating = not self.cheating
        self.cheat_func()
        text = "Disable cheat" if self.cheating else "Enable cheat"
        self.extra_buttons[0].original_caption = text
        self.extra_buttons[0].update_caption(
            self.extra_buttons[0].original_caption)
        self.update_view()

    def __init_extra(self) -> None:
        """Build the extra pause menu surface and its buttons."""
        extra_size = (self.screen_size[0] // 2,
                      self.screen_size[1] // 3 * 2 + 100)
        self.extra_surface = Surface(extra_size)
        screen_center = (self.screen_size[0] // 2, self.screen_size[1] // 2)
        self.extra_rect = self.extra_surface.get_rect(center=screen_center)
        self.extra_surface.fill((10, 15, 20))

        x_local = self.extra_rect.width // 2
        offset_x = 100
        y_local = self.extra_rect.height // 10
        center_x = self.extra_rect.width // 2
        pos_y = self.extra_rect.y + y_local
        width_third = self.extra_rect.width // 3

        Text("EXTRA", self.rm.get_font(40),
             (x_local, y_local),
             (252, 234, 63)).render(self.extra_surface)

        self.__draw_inputs()

        self.extra_buttons: list[Button] = []
        cheat_text = "Disable cheat" if self.cheating else "Enable cheat"
        self.extra_buttons.append(Button(
            cheat_text,
            (self.extra_rect.x + width_third, pos_y + (y_local * 8)),
            self.rm.get_font(25),
            lambda: self.cheat()
            if (self.sm.current_state is AppState.GAME and
                self.current_view is View.EXTRA) else None
        ))
        self.extra_buttons.append(Button(
            "Back", (self.extra_rect.x + width_third * 2,
                     pos_y + (y_local * 8)),
            self.rm.get_font(25),
            lambda: self.change_view()
            if (self.sm.current_state is AppState.GAME and
                self.current_view is View.EXTRA) else None
        ))
        for i, (key, string) in enumerate(self.key_images):
            pos_x = center_x - offset_x
            self.extra_surface.blit(key, key.get_rect(
                center=(pos_x - 30, pos_y + (y_local * i))
            ))
            pos_x = center_x + offset_x
            Text(string, self.rm.get_font(20),
                 (pos_x - 30,
                  pos_y + (y_local * i))).render(self.extra_surface)

    def __draw_inputs(self) -> None:
        """Create the key icons used by the extra menu instructions."""
        info_font = self.rm.get_font(25)

        if self.rm.has_keyb_sheet_loaded:
            n_surf = transform.scale(self.rm.get_resource("n"), (30, 30))
            f_surf = transform.scale(self.rm.get_resource("f"), (30, 30))
            one_surf = transform.scale(self.rm.get_resource("1"), (30, 30))
            x_surf = transform.scale(self.rm.get_resource("x"), (30, 30))
            c_surf = transform.scale(self.rm.get_resource("c"), (30, 30))
            z_surf = transform.scale(self.rm.get_resource("z"), (30, 30))

        else:
            n_surf = Surface((30, 30))
            f_surf = Surface((30, 30))
            one_surf = Surface((30, 30))
            x_surf = Surface((30, 30))
            c_surf = Surface((30, 30))
            z_surf = Surface((30, 30))
            Text("N", info_font, (0, 0)).render(n_surf)
            Text("F", info_font, (0, 0)).render(f_surf)
            Text("1", info_font, (0, 0)).render(one_surf)
            Text("X", info_font, (0, 0)).render(x_surf)
            Text("C", info_font, (0, 0)).render(c_surf)
            Text("Z", info_font, (0, 0)).render(z_surf)

        self.key_images = [
            (n_surf, "change level"),
            (f_surf, "freeze ghost"),
            (one_surf, "lives up"),
            (z_surf, "decrease speed"),
            (c_surf, "reset speed"),
            (x_surf, "increase speed"),
        ]

    def register_buttons(self, im: InputManager) -> None:
        """Register all pause menu buttons with the input manager.

        Args:
            im: The input manager used to dispatch button events.
        """
        for button in self.buttons:
            im.register_on_click_observer(button.on_click)
            im.register_on_hover_observer(button.on_hover)
        for button in self.extra_buttons:
            im.register_on_click_observer(button.on_click)
            im.register_on_hover_observer(button.on_hover)

    def render(self, surface: Surface) -> None:
        """Blit the pause overlay onto the target surface.

        Args:
            surface: The surface that receives the pause overlay.
        """
        surface.blit(self.bg_pause, (0, 0))
