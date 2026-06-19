"""Dynamic score display HUD component.

Provides a HUD object that renders and updates the player's score during
gameplay.
"""
from src.hud.hud_object import HudObject

from pygame import Surface
from pygame.font import Font


class DynamicScore(HudObject):
    """Dynamic Score implementation.

    HUD object used to show game time during the game.
    """

    def __init__(self, font: Font, top_left: tuple[int, int],
                 initial_score: int = 0) -> None:
        """Create a score HUD object that can be updated dynamically.

        Args:
            font: The font used to render the score.
            top_left: The top-left position of the score HUD.
            initial_score: The score displayed at initialization.
        """
        self.font = font
        text = self.font.render(str(initial_score), True, (255, 255, 255))
        text_rect = text.get_rect()
        self.image = Surface((text_rect.width, text_rect.height))
        self.bg = (0, 0, 0)
        self.image.fill(self.bg)
        self.image.blit(text, text_rect)
        super().__init__(self.image, top_left)

    def update_score(self, score: int) -> None:
        """Update the rendered score text.

        Args:
            score: The new score value to display.
        """
        text = self.font.render(f"{score}", True, (255, 255, 255))
        self.image = Surface((text.get_width(), text.get_height()))
        self.image.fill(self.bg)
        self.image.blit(text, (0, 0))
