"""Module that contains generic abstract classes."""
from abc import ABC, abstractmethod
from pygame import Surface


class Renderizable(ABC):
    """Define the interface for objects that can be rendered on a surface."""

    @abstractmethod
    def render(self, surface: Surface) -> None:
        """Draw the object onto the given surface.

        Args:
            surface: The target surface where the object should be rendered.
        """
        pass
