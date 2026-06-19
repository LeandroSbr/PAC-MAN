"""Base HUD object for displaying images on the screen.

Provides a renderizable HUD component for displaying fixed-position
images such as lives, score display, and other UI elements.
"""
from src.utils.templates import Renderizable

from pygame import Surface


class HudObject(Renderizable):
    """HudObject implementation.

    Class for UI static object during the game.
    """

    def __init__(self, image: Surface, coord: tuple[int, int]):
        """Create a HUD object from an image positioned at a coordinate.

        Args:
            image: The surface to display in the HUD.
            coord: The top-left position of the HUD object.
        """
        self.image = image
        self.rect = self.image.get_rect(top=coord[1], left=coord[0])

    def render(self, screen: Surface) -> None:
        """Draw the HUD object onto the target screen.

        Args:
            screen: The surface where the HUD object should be rendered.
        """
        screen.blit(self.image, self.rect)
