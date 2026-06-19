"""Info class implementation."""
from src.menu.text import Text
from src.menu.button import Button
from src.managers.resource_manager import ResourceManager
from src.managers.state_manager import StateManager
from src.utils.templates import Renderizable
from src.utils.enums import AppState

from pygame import Surface, transform


class Info(Renderizable):
    """Info class implementation.

    Info class that displays commands info.
    """

    def __init__(self, rm: ResourceManager,
                 sm: StateManager,
                 screen_size: tuple[int, int]) -> None:
        """Initialize the information submenu and its rendered content.

        Args:
            rm: The resource manager used to load fonts and images.
            sm: The state manager used to return to the menu.
            screen_size: The size of the window surface.
        """
        self.rm = rm
        self.sm = sm
        self.screen_size = screen_size
        self.__init_surface()
        self.__init_components()
        self.__draw_surface()

    def __init_surface(self) -> None:
        """Create the submenu surface and load the required fonts."""
        self.main_surface = Surface(self.screen_size)
        self.subtitle_font = self.rm.get_font(40)
        self.info_font = self.rm.get_font(20)
        self.button_font = self.rm.get_font(25)

    def __init_components(self) -> None:
        """Create the static text and button components for the submenu."""
        center_x = self.screen_size[0] // 2
        pos_y = self.screen_size[1] // 5
        self.renderizables: list[Renderizable] = []
        self.renderizables.append(Text("INFO", self.subtitle_font,
                                       (center_x, pos_y * 5 // 6),
                                       color=(252, 234, 63)
                                       ))
        self.renderizables.append(Button(
            "back to menu", (center_x, (pos_y * 4)),
            self.button_font, lambda: (
                self.sm.change_state(AppState.MENU)
                if self.sm.current_state is AppState.INFO
                else None
            ),
            color=(255, 255, 255),
            bg=(10, 15, 20, 255)
        ))

        self.buttons: list[Button] = []
        for rend in self.renderizables:
            if isinstance(rend, Button):
                self.buttons.append(rend)

    def _draw_inputs(self) -> None:
        """Draw the input guide images used by the info screen."""
        wasd_surf = Surface((45, 30))
        arrow_surf = Surface((45, 30))
        esc_surf = Surface((30, 30))
        enter_surf = Surface((120, 30))
        wasd_surf.fill((10, 15, 20))
        arrow_surf.fill((10, 15, 20))
        esc_surf.fill((10, 15, 20))
        enter_surf.fill((10, 15, 20))
        if self.rm.has_keyb_sheet_loaded:

            self.wasd_list = [
                (self.rm.get_resource("w"), (15, 0)),
                (self.rm.get_resource("a"), (0, 15)),
                (self.rm.get_resource("s"), (15, 15)),
                (self.rm.get_resource("d"), (30, 15))
            ]
            self.arrow_list = [
                (self.rm.get_resource("up"), (15, 0)),
                (self.rm.get_resource("left"), (0, 15)),
                (self.rm.get_resource("down"), (15, 15)),
                (self.rm.get_resource("right"), (30, 15))
            ]
            esc_surf = self.rm.get_resource("esc")
            enter_surf = self.rm.get_resource("enter")
            wasd_surf.blits(self.wasd_list)
            arrow_surf.blits(self.arrow_list)
            wasd_surf = transform.scale(wasd_surf, (90, 60))
            arrow_surf = transform.scale(arrow_surf, (90, 60))
            esc_surf = transform.scale(esc_surf, (30, 30))
            enter_surf = transform.scale(enter_surf, (120, 30))
        else:
            Text("WASD", self.button_font, (0, 0)).render(wasd_surf)
            Text("ARROWS", self.button_font, (0, 0)).render(arrow_surf)
            Text("ESC", self.button_font, (0, 0)).render(esc_surf)
            Text("ENTER", self.button_font, (0, 0)).render(enter_surf)

        self.key_images = [([wasd_surf, arrow_surf], "movement"),
                           ([esc_surf], "exit"),
                           ([enter_surf], "pause")]

    def __draw_surface(self) -> None:
        """Compose the full info screen surface."""
        self.main_surface.fill((10, 15, 20))
        self._draw_inputs()

        for renderizable in self.renderizables:
            renderizable.render(self.main_surface)
        center_x = self.screen_size[0] // 2
        offset_x = 200
        step_x = 0
        step_y = 100
        pos_y = 200 + self.screen_size[1] // 5

        for key in self.key_images:
            for elem in key[0]:
                pos_x = center_x - offset_x + step_x
                self.main_surface.blit(elem, elem.get_rect(
                                                center=(pos_x, pos_y)))
                if elem is not key[0][-1]:
                    Text("/", self.button_font,
                         (pos_x + 90, pos_y)).render(self.main_surface)
                step_x += 160
            step_x = 0
            pos_x = center_x + offset_x
            Text(key[1], self.info_font,
                 (pos_x, pos_y)).render(self.main_surface)
            pos_y += step_y

    def redraw(self) -> None:
        """Redraw the submenu content on the internal surface."""
        for renderizable in self.renderizables:
            renderizable.render(self.main_surface)

    @property
    def representation(self) -> list[Renderizable]:
        """Return the renderable objects for the info submenu."""
        return [self]

    def render(self, surface: Surface) -> None:
        """Blit the info submenu onto the target surface.

        Args:
            surface: The surface that receives the rendered submenu.
        """
        surface.blit(self.main_surface, (0, 0))
