"""Highscore class implementation."""
from src.menu.button import Button
from src.managers.resource_manager import ResourceManager
from src.managers.state_manager import StateManager
from src.menu.text import Text
from src.utils.enums import AppState
from src.utils.templates import Renderizable

from pygame import Surface


class Highscores(Renderizable):
    """Highscore class implementation.

    Initialize the highscores submenu and its surfaces.
    """

    def __init__(self, rm: ResourceManager, screen_size: tuple[int, int],
                 sm: StateManager) -> None:
        """Initialize the highscores submenu and its surfaces.

        Args:
            rm: The resource manager used to load fonts and scores.
            screen_size: The size of the window surface.
            sm: The state manager used to return to the menu.
        """
        self.rm = rm
        self.screen_size = screen_size
        self.sm = sm
        self.__init_surface()
        self.__init_components()
        self.draw_scores()
        self.draw_surface()

    def __init_surface(self) -> None:
        """Create the submenu surfaces and load the required fonts."""
        self.main_surface = Surface(self.screen_size)
        self.main_surface.fill((5, 10, 15))
        self.subtitle_font = self.rm.get_font(40)
        self.score_font = self.rm.get_font(20)
        self.button_font = self.rm.get_font(25)
        scores_x = self.screen_size[0] // 3
        scores_y = self.screen_size[1] // 5 * 3
        self.scores_surface = Surface((scores_x, scores_y))
        self.scores_rect = self.scores_surface.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 2)
        )

    def __init_components(self) -> None:
        """Create the static text and button components for the submenu."""
        center_x = self.screen_size[0] // 2
        pos_y = self.screen_size[1] // 5
        self.renderizables: list[Renderizable] = []
        self.renderizables.append(Text("SCORES", self.subtitle_font,
                                  (center_x, pos_y * 5 // 6),
                                  color=(252, 234, 63)))
        self.renderizables.append(Button(
            "back to menu", (center_x, (pos_y * 4)),
            self.button_font, lambda: (
                self.sm.change_state(AppState.MENU)
                if self.sm.current_state is AppState.SCORES
                else None
            ),
            color=(255, 255, 255),
            bg=(10, 15, 20, 255)
        ))
        self.buttons: list[Button] = []
        for rend in self.renderizables:
            if isinstance(rend, Button):
                self.buttons.append(rend)

    def draw_scores(self) -> None:
        """Render the highscores list onto the dedicated scores surface."""
        self.scores_surface.fill((5, 10, 15))
        score_surf_size = self.scores_surface.get_size()
        step = self.score_font.get_height() + 20
        center_x = score_surf_size[0] // 2
        score_list = [f"{k}: {v}" for k, v in self.rm.get_highscores()]
        center_y = step // 2 + 100
        for score in score_list:
            Text(score, self.score_font, (center_x, center_y)).render(
                                                        self.scores_surface)
            center_y += step

    def draw_surface(self) -> None:
        """Compose the full highscores screen surface."""
        self.main_surface.blit(self.scores_surface, self.scores_rect)
        for renderizable in self.renderizables:
            renderizable.render(self.main_surface)

    def redraw(self) -> None:
        """Redraw the interactive button components on the main surface."""
        for button in self.buttons:
            button.render(self.main_surface)

    @property
    def representation(self) -> list[Renderizable]:
        """Return the renderable objects for the highscores submenu."""
        return [self]

    def render(self, surface: Surface) -> None:
        """Blit the highscores submenu onto the target surface.

        Args:
            surface: The surface that receives the rendered submenu.
        """
        surface.blit(self.main_surface, (0, 0))
