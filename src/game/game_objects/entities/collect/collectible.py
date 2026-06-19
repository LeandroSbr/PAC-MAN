"""Base collectible item class for game objects.

Provides the abstract Collectible class representing items that can be
collected by the player to earn points, such as pellets and power pellets.
"""
from src.utils.templates import Renderizable

from pygame import Surface


class Collectible(Renderizable):
    """Base class for collectible items with point values.

    Represents an item that can be collected by the player to earn points.
    Tracks collection state and prevents double-counting of points for the
    same collectible instance.
    """

    def __init__(self, points: int, symbol: Surface | None = None) -> None:
        """Initialize a collectible item and its score value.

        Args:
            points: The score awarded when the item is collected.
            symbol: An optional surface used to represent the item.
        """
        self.points = points
        self.is_power_pellet = False
        self.symbol: Surface | None = symbol
        self.collected = False

    def collect(self) -> int:
        """Mark the collectible as collected and return its score value.

        Returns:
            The points awarded by this collectible, or ``0`` if already
            collected.
        """
        if not self.collected:
            self.collected = True
            return self.points
        return 0
