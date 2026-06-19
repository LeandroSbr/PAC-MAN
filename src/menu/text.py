"""Text class implementation."""
from src.utils.templates import Renderizable

from pygame.font import Font
from pygame import Surface


class Text(Renderizable):
    """Text class implementation.

    Class used for all base text in the game.
    """

    def __init__(self, text: str, font: Font, center: tuple[int, int],
                 color: tuple[int, int, int] = (255, 255, 255)):
        """Create a rendered text surface centered on the given position.

        Args:
            text: The text string to render.
            font: The font used to render the text.
            center: The center position for the text rectangle.
            color: The text color as an RGB tuple.
        """
        self.text = font.render(text, True, color)
        self.rect = self.text.get_rect(center=center)

    def render(self, surface: Surface) -> None:
        """Draw the text onto the target surface.

        Args:
            surface: The surface where the text should be blitted.
        """
        surface.blit(self.text, self.rect)
