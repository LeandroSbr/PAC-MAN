"""Game over screen display and high score management.

Handles rendering the game over screen, displaying high scores, and
capturing player name input for score recording.
"""
from src.managers.state_manager import StateManager
from src.managers.input_manager import InputManager
from src.managers.resource_manager import ResourceManager
from src.menu.button import Button
from src.menu.text import Text
from src.utils.enums import AppState
from src.utils.templates import Renderizable

from pygame import K_BACKSPACE, K_RETURN, Surface, event


class GameOver(Renderizable):
    """Game over screen implementation.

    Game over menu, where you can insert your nickname to save
    the game points in the Json file.
    """

    def __init__(
                self, state_manager: StateManager,
                input_manager: InputManager,
                rm: ResourceManager,
                screen_size: tuple[int, int]
            ) -> None:
        """Initialize the game over screen and its rendering state.

        Args:
            state_manager: The state manager used to change application state.
            input_manager: The input manager used to register buttons.
            rm: The resource manager used to load fonts and scores.
            screen_size: The size of the window surface.
        """
        self.state_manager = state_manager
        self.input_manager = input_manager
        self.rm = rm
        self.screen_size = screen_size
        self.highscores: list[tuple[str, int]] = self.rm.get_highscores()
        self.title_font = rm.get_font(50)
        self.button_font = rm.get_font(25)
        self.score_font = self.rm.get_font(20)
        self.old_scores: list[Renderizable] = []
        self.input: str = ""
        self.init_scores = False
        self.to_update = True
        self.text_to_render: Text
        self.input_center: tuple[int, int]

        self.__init_surface()

    def register_buttons(self, input_manager: InputManager) -> None:
        """Register the game over buttons with the input manager.

        Args:
            input_manager: The input manager used to handle button events.
        """
        for button in self.buttons:
            input_manager.register_on_click_observer(button.on_click)
            input_manager.register_on_hover_observer(button.on_hover)

    def __draw_surface(self) -> None:
        """Draw the game over surface content."""
        self.surface.fill((5, 10, 15))
        for score in self.old_scores:
            score.render(self.surface)
        self.text_to_render.render(self.surface)

    def update(self, score: int) -> None:
        """Update the game over screen with the current score.

        Args:
            score: The score earned in the finished game.
        """
        if (all(score < s[1] for s in self.highscores) and
                len(self.highscores) == 10):
            self.state_manager.change_state(AppState.MENU)
            return
        if not self.init_scores:
            self.__draw_scores(score)
            self.score = score
            self.init_scores = True
        if self.to_update:
            self.text_to_render = Text(f"{self.input}: {score}",
                                       self.score_font, self.input_center)
            self.__draw_surface()

    def __init_buttons(self) -> None:
        """Create the game over action buttons."""
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 5 * 4
        self.buttons: list[Button] = [
            Button("Save and exit", (center_x, center_y), self.button_font,
                   self.__save_score_and_quit, (255, 255, 255))
        ]

    def __draw_scores(self, score: int) -> None:
        """Prepare the highscores and score input layout.

        Args:
            score: The score earned in the finished game.
        """
        new_score_rendered = False
        self.old_scores.clear()
        step = self.score_font.get_height() + 25
        center_x = self.surface.get_width() // 2
        center_y = 150 + (self.title_font.get_height() + 20) // 2
        self.old_scores.append(Text("Highscores:", self.title_font,
                                    (center_x, center_y), (252, 234, 63)))
        center_y += self.title_font.get_height() + 80
        i = 0
        for k, v in self.highscores:
            if i == 10:
                break
            if (v < score or i == 9) and not new_score_rendered:
                self.input_center = (center_x, center_y)
                new_score_rendered = True
            else:
                self.old_scores.append(Text(
                    f"{k}: {v}", self.score_font,
                    (center_x, center_y)
                ))
            center_y += step
            i += 1
        if not new_score_rendered:
            self.input_center = (center_x, center_y)

    def __init_surface(self) -> None:
        """Create the main game over surface and pre-render buttons."""
        size_x = self.screen_size[0] // 3
        self.surface = Surface((size_x, self.screen_size[1]))
        self.surf_rect = self.surface.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
        self.surface.fill((5, 10, 15))
        self.__init_buttons()
        for button in self.buttons:
            button.render(self.surface)

    def __save_score_and_quit(self) -> None:
        """Save the current score, then return to the menu if valid."""
        if len(self.input) > 2 and len(self.input) < 10:
            inserted = False
            for i, (_, v) in enumerate(self.highscores):
                if self.score > v:
                    inserted = True
                    self.highscores.insert(i, (self.input, self.score))
                    break
            if not inserted:
                self.highscores.append((self.input, self.score))
            if len(self.highscores) > 10:
                self.highscores.pop()
            self.rm.serialize_scores()
            self.input = ""
            self.init_scores = False
            self.state_manager.change_state(AppState.MENU)

    def handle_events(self, kd_event: event.Event) -> None:
        """Handle keyboard events for name entry and score saving.

        Args:
            kd_event: The pygame keyboard event to process.
        """
        if self.state_manager.current_state is not AppState.GAME_OVER:
            return
        elif kd_event.key == K_RETURN:
            return self.__save_score_and_quit()
        elif kd_event.key == K_BACKSPACE:
            self.input = self.input[:-1]
        key = kd_event.unicode
        if not key:
            return
        elif (ord(key) < 32 or
              ord(key) > 127 or len(self.input) > 10):
            return
        else:
            self.input += key
        self.to_update = True

    @property
    def representation(self) -> list[Renderizable]:
        """Return the renderable objects for the game over screen."""
        repres: list[Renderizable] = [self]
        repres.extend(self.buttons)
        return repres

    def render(self, surface: Surface) -> None:
        """Blit the game over surface onto the target surface.

        Args:
            surface: The surface that receives the rendered content.
        """
        surface.blit(self.surface, self.surf_rect)
