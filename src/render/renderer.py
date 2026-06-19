"""Game rendering and display management."""
from src.utils.templates import Renderizable

from pygame import display, NOFRAME


class Renderer:
    """Game rendering and display management.

    Handles rendering of all game objects to the screen and manages the
    display surface.
    """

    def __init__(self) -> None:
        """Initialize the rendering surface in fullscreen windowed mode."""
        self.screen = display.set_mode((0, 0), NOFRAME)

    def render(self, objs: list[Renderizable]) -> None:
        """Render all objects onto the screen and present the frame.

        Args:
            objs: The renderable objects to draw on the screen.
        """
        self.screen.fill((5, 10, 15))
        for obj in objs:
            obj.render(self.screen)
        display.flip()
