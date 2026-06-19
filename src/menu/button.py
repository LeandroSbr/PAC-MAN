"""Button class implementation."""
from src.utils.templates import Renderizable

from typing import Callable
from pygame.font import Font
from pygame import Surface, SRCALPHA, draw


class Button(Renderizable):
    """Button class implementation.

    Base class for all button objects in the game.
    """

    def __init__(
        self, caption: str, center: tuple[int, int],
        font: Font, action: Callable[[], None] | None = None,
        color: tuple[int, int, int] = (255, 255, 255),
        bg: tuple[int, int, int, int] | None = None
    ) -> None:
        """Initialize a clickable button with optional background fill.

        Args:
            caption: The label displayed on the button.
            center: The center position of the button on the screen.
            font: The font used to render the caption.
            action: The callback executed when the button is clicked.
            color: The text color as an RGB tuple.
            bg: The optional background color as an RGBA tuple.
        """
        self.original_caption = caption
        self.caption = caption
        self.color = color
        self.bg = bg
        self.text = font.render(caption, True, color, bg)
        self.bg_surface = Surface((self.text.get_width() + 20,
                                   self.text.get_height() + 20), SRCALPHA)
        self.rect = self.bg_surface.get_rect(center=center)
        if bg is not None:
            self.bg_surface.fill(bg)
        else:
            self.bg_surface.fill((0, 0, 0, 0))
        self.text_rect = self.text.get_rect(
            center=(self.rect.width // 2, self.rect.height // 2))
        self.bg_surface.blit(self.text,
                             self.text_rect)
        self.action = action
        self.font = font

    def on_hover(self, hover_coord: tuple[int, int]) -> None:
        """Update the button appearance when the pointer hovers over it.

        Args:
            hover_coord: The current pointer position.
        """
        if self.rect.collidepoint(hover_coord):
            self.__draw_border()
        else:
            self.update_caption(self.original_caption)

    def on_click(self, click_coord: tuple[int, int]) -> None:
        """Trigger the button action if the click occurs inside its bounds.

        Args:
            click_coord: The position of the click event.
        """
        if not self.rect.collidepoint(click_coord):
            return
        if self.action is not None:
            self.action()

    def get_center(self) -> tuple[int, int]:
        """Return the current center position of the button."""
        return self.rect.center

    def __draw_border(self) -> None:
        """Redraw the button surface with a visible border."""
        border_color = (255, 255, 255)
        border_width = 2
        if self.bg is None:
            self.bg_surface.fill((0, 0, 0, 0))
        else:
            self.bg_surface.fill(self.bg)
        self.bg_surface.blit(self.text,
                             self.text_rect)
        draw.rect(self.bg_surface, border_color,
                  self.bg_surface.get_rect(), border_width)

    def update_caption(self, new_caption: str) -> None:
        """Update the button caption and rebuild its rendered surface.

        Args:
            new_caption: The new caption to display on the button.
        """
        self.caption = new_caption
        self.text = self.font.render(new_caption, True,
                                     self.color, self.bg)
        self.bg_surface = Surface((self.text.get_width() + 20,
                                   self.text.get_height() + 20), SRCALPHA)
        self.rect = self.bg_surface.get_rect(center=self.rect.center)
        if self.bg is not None:
            self.bg_surface.fill(self.bg)
        else:
            self.bg_surface.fill((0, 0, 0, 0))
        self.bg_surface.blit(self.text, self.text_rect)

    def render(self, surface: Surface) -> None:
        """Draw the button onto the target surface.

        Args:
            surface: The surface where the button should be rendered.
        """
        surface.blit(self.bg_surface, self.rect)

    def __str__(self) -> str:
        """Return the button caption as its string representation."""
        return self.caption
