"""Standard pellet collectible for the Pac-Man game.

Implements the basic pellet item that the player collects throughout the maze
to earn points and progress through levels.
"""
from src.game.game_objects.entities.collect.collectible import Collectible

from pygame import Surface, draw


class Pellet(Collectible):
    """Standard pellet collectible item.

    Extends Collectible to represent a basic pellet that appears throughout
    the maze. Players collect pellets to earn points
    and fill the game objective.
    """

    def __init__(self, points: int) -> None:
        """Initialize a standard pellet collectible.

        Args:
            points: The score awarded when the pellet is collected.
        """
        super().__init__(points, None)

    def render(self, surface: Surface) -> None:
        """Draw the pellet onto the target surface.

        Args:
            surface: The surface where the pellet should be rendered.
        """
        draw.rect(surface, (255, 250, 150),
                  surface.get_rect().scale_by(0.1, 0.1))
