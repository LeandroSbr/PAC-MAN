"""Power pellet collectible for temporary invincibility.

Implements the special power-up pellet that grants the player temporary
invincibility and the ability to eat ghosts for bonus points.
"""
from src.game.game_objects.entities.collect.collectible import Collectible

from pygame import Surface, draw


class PowerPellet(Collectible):
    """Special power-up pellet granting temporary invincibility.

    Extends Collectible to represent a power pellet that activates a special
    game state allowing the player to become invincible and eat ghosts for
    bonus points.
    """

    def __init__(self, points: int) -> None:
        """Initialize a power pellet collectible.

        Args:
            points: The score awarded when the pellet is collected.
        """
        super().__init__(points, None)
        self.is_power_pellet = True

    def render(self, surface: Surface) -> None:
        """Draw the power pellet onto the target surface.

        Args:
            surface: The surface where the power pellet should be rendered.
        """
        draw.rect(surface, (255, 250, 150),
                  surface.get_rect().scale_by(0.25, 0.25))
