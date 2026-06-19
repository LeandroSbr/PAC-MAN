"""Resource Manager implementation."""
from src.managers.parser import Parser

import pygame
from pygame import Surface
from pygame.font import Font


BASETILEWIDTH = 16
BASETILEHEIGHT = 16
TILEWIDTH = 16
TILEHEIGHT = 16


class ResourceManager:
    """Resource Manager implementation.

    It manage all the data given by the parser.
    """

    def __init__(self, config_path: str):
        """Load configuration, resources, fonts, and animations.

        Args:
            config_path: Path to the configuration file used by the parser.
        """
        self.resources: dict[str, Surface] = {}
        self.parser = Parser(config_path)
        self.config = self.parser.get_config()
        self.scores = self.parser.get_highscores()
        self.__elaborate_highscores()
        self.__load_spritesheets()
        self.__init_fonts()
        self.__init_resources()
        self.frames_sources: dict[str, list[Surface]] = {}
        self.__init_frames_resources()

    def __init_fonts(self) -> None:
        """Load the game fonts, falling back to a system font if needed."""
        try:
            font_path = "resources/PressStart2P-Regular.ttf"
            self.fonts = {
                14: pygame.font.Font(font_path, 14),
                20: pygame.font.Font(font_path, 20),
                22: pygame.font.Font(font_path, 22),
                24: pygame.font.Font(font_path, 24),
                25: pygame.font.Font(font_path, 25),
                30: pygame.font.Font(font_path, 30),
                36: pygame.font.Font(font_path, 36),
                40: pygame.font.Font(font_path, 40),
                50: pygame.font.Font(font_path, 50),
            }
        except (FileNotFoundError, pygame.error, PermissionError):
            new_font_path: str | None = None
            self.fonts = {
                14: pygame.font.SysFont(new_font_path, 14),
                20: pygame.font.SysFont(new_font_path, 20),
                22: pygame.font.SysFont(new_font_path, 22),
                24: pygame.font.SysFont(new_font_path, 24),
                25: pygame.font.SysFont(new_font_path, 25),
                30: pygame.font.SysFont(new_font_path, 30),
                36: pygame.font.SysFont(new_font_path, 36),
                40: pygame.font.SysFont(new_font_path, 40),
                50: pygame.font.SysFont(new_font_path, 50),
            }

    def __load_spritesheets(self) -> None:
        """Load sprite sheets and record whether they are available."""
        try:
            self.sheet = pygame.image.load(
                "resources/spritesheet.png").convert()
            transcolor = self.sheet.get_at((0, 0))
            self.sheet.set_colorkey(transcolor)
            self.has_sheet_loaded = True
        except (FileNotFoundError, pygame.error, PermissionError):
            self.has_sheet_loaded = False
        try:
            self.keyb_sheet = pygame.image.load(
                "resources/horizontal_normal.png").convert()
            transcolor = self.keyb_sheet.get_at((0, 0))
            self.keyb_sheet.set_colorkey(transcolor)
            self.has_keyb_sheet_loaded = True
        except (FileNotFoundError, pygame.error, PermissionError):
            self.has_keyb_sheet_loaded = False

    def set_scores(self, scores: list[tuple[str, int]]) -> None:
        """Replace the stored highscores list.

        Args:
            scores: The new highscores list.
        """
        self.scores = scores

    def __elaborate_highscores(self) -> None:
        """Sort highscores in descending order by score."""
        self.scores.sort(key=lambda item: item[1], reverse=True)

    def serialize_scores(self) -> None:
        """Persist the highscores to disk."""
        self.__elaborate_highscores()
        self.parser.serialize_scores(self.scores)

    def get_highscores(self) -> list[tuple[str, int]]:
        """Return the current highscores list."""
        return self.scores

    def get_Image(self, x: int, y: int, width: int, height: int) -> Surface:
        """Return a subsurface from the main sprite sheet.

        Args:
            x: The tile column in the sprite sheet.
            y: The tile row in the sprite sheet.
            width: The width of the extracted image in pixels.
            height: The height of the extracted image in pixels.

        Returns:
            The extracted sprite image.
        """
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())

    def get_key_Image(self, x: int, y: int,
                      width: int, height: int) -> Surface:
        """Return a subsurface from the keyboard sprite sheet.

        Args:
            x: The tile column in the keyboard sheet.
            y: The tile row in the keyboard sheet.
            width: The width of the extracted image in pixels.
            height: The height of the extracted image in pixels.

        Returns:
            The extracted keyboard sprite image.
        """
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.keyb_sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.keyb_sheet.subsurface(self.keyb_sheet.get_clip())

    def __init_resources(self) -> None:
        """Populate the named resources dictionary from the sprite sheets."""
        if not self.has_sheet_loaded:
            return
        self.resources["pacman_hud"] = self.get_Image(
                                    0, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT)
        self.resources["cherry"] = self.get_Image(
                                    16, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT)
        self.resources["strawberry"] = self.get_Image(
                                    16, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT)
        self.resources["orange"] = self.get_Image(
                                    18, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT)
        self.resources["w"] = self.get_key_Image(
                                    1, 10, 15, 15)
        self.resources["a"] = self.get_key_Image(
                                    0, 0, 15, 15)
        self.resources["s"] = self.get_key_Image(
                                    1, 6, 15, 15)
        self.resources["d"] = self.get_key_Image(
                                    0, 3, 15, 15)
        self.resources["up"] = self.get_key_Image(
                                    4, 0, 15, 15)
        self.resources["down"] = self.get_key_Image(
                                    4, 1, 15, 15)
        self.resources["left"] = self.get_key_Image(
                                    4, 2, 15, 15)
        self.resources["right"] = self.get_key_Image(
                                    4, 3, 15, 15)
        self.resources["esc"] = self.get_key_Image(
                                    5, 4, 15, 15)
        self.resources["enter"] = self.get_key_Image(
                                    10, 3, 60, 15)
        self.resources["n"] = self.get_key_Image(
                                    1, 1, 15, 15)
        self.resources["f"] = self.get_key_Image(
                                    0, 5, 15, 15)
        self.resources["z"] = self.get_key_Image(
                                    2, 1, 15, 15)
        self.resources["c"] = self.get_key_Image(
                                    0, 2, 15, 15)
        self.resources["x"] = self.get_key_Image(
                                    1, 11, 15, 15)
        self.resources["n"] = self.get_key_Image(
                                    1, 1, 15, 15)
        self.resources["1"] = self.get_key_Image(
                                    2, 2, 15, 15)

    def __init_frames_resources(self) -> None:
        """Populate the animation frame resources for characters."""
        if not self.has_sheet_loaded:
            return

        self.frames_sources["pacman_left"] = [
            self.get_Image(10, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 2, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["pacman_right"] = [
            self.get_Image(10, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 2, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["pacman_up"] = [
            self.get_Image(10, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 2, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["pacman_down"] = [
            self.get_Image(10, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 2, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 0, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["pacman_death"] = [
            self.get_Image(0, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(8, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(10, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(12, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(14, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(16, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(18, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(20, 12, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["blinky"] = [
            self.get_Image(0, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(0, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]

        self.frames_sources["inky"] = [
            self.get_Image(4, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(4, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["pinky"] = [
            self.get_Image(2, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(2, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["clyde"] = [
            self.get_Image(6, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(6, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["ghost_dead"] = [
            self.get_Image(8, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(8, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(8, 8, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(8, 10, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]
        self.frames_sources["ghost_frightened"] = [
            self.get_Image(10, 4, 2 * TILEWIDTH, 2 * TILEHEIGHT),
            self.get_Image(10, 6, 2 * TILEWIDTH, 2 * TILEHEIGHT),
        ]

    def get_resource(self, name: str) -> Surface:
        """Return a named resource from the loaded sprite dictionary.

        Args:
            name: The resource identifier.

        Returns:
            The requested surface resource.

        Raises:
            ValueError: If the resource is not available.
        """
        resource = self.resources.get(name)
        if resource is None:
            raise ValueError(f"Resource '{name}' not found")
        return resource

    def get_frame_resources(self, name: str) -> list[Surface]:
        """Return the animation frames associated with a resource name."""
        return self.frames_sources.get(name, [])

    def get_font(self, font_size: int) -> Font:
        """Return a loaded font by its size.

        Args:
            font_size: The requested font size.

        Returns:
            The loaded font matching the requested size.
        """
        return self.fonts[font_size]
