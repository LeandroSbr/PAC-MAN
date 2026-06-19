"""Maze cell representation and rendering.

Defines the Cell class which represents individual maze cells with encoded
wall information, optional pellets, and rendering capabilities.
"""
from __future__ import annotations

from src.game.game_objects.entities.collect.collectible import Collectible
from src.utils.macros import WALL_MAP
from src.utils.enums import Dir
from src.utils.templates import Renderizable

from pygame import Surface, draw


class Cell(Renderizable):
    """Represent a single maze cell, including walls and pellets."""

    def __init__(self, coord: tuple[int, int], walls: int,
                 dim: tuple[int, int], pellet: Collectible | None) -> None:
        """Initialize a maze cell with walls, dimensions, and a pellet.

        Args:
            coord: The cell coordinate in maze row/column space.
            walls: The encoded wall bitmask for the cell.
            dim: The pixel dimensions of the cell surface.
            pellet: The collectible associated with the cell, if any.
        """
        self.pellet = pellet
        self.coord: tuple[int, int] = coord
        self.walls: int = walls
        self.dim: tuple[int, int] = dim
        self.__create_surface()
        self.rect = self.surface.get_rect(topleft=(coord[1] * dim[0],
                                                   coord[0] * dim[1]))

    def is_open(self, dir: Dir) -> bool:
        """Return whether the cell is open in the given direction.

        Args:
            dir: The direction to inspect.

        Returns:
            ``True`` if movement is allowed in that direction, otherwise
            ``False``.
        """
        return not (self.walls & dir.value)

    def is_closed(self, dir: Dir) -> bool:
        """Return whether the cell is closed in the given direction.

        Args:
            dir: The direction to inspect.

        Returns:
            ``True`` if movement is blocked in that direction, otherwise
            ``False``.
        """
        if self.walls & dir.value:
            return True
        return False

    def _get_walls(self) -> list[Dir]:
        """Return the list of wall directions encoded in the cell."""
        return WALL_MAP[self.walls]

    def __create_surface(self) -> None:
        """Create the initial cell surface with walls and collectibles."""
        self.wall_color = (70, 75, 80)
        self.closed_color = (0, 0, 0)
        self.open_color = (0, 0, 40)
        self.surface = Surface(self.dim)
        if self.walls == 15:
            self.surface.fill(self.closed_color)
        else:
            self.surface.fill(self.open_color)
        for wall in self._get_walls():
            if wall == Dir.NORTH:
                draw.line(self.surface, self.wall_color, (0, 0),
                          (self.dim[0], 0), self.dim[0] // 10)
            elif wall == Dir.EAST:
                draw.line(self.surface, self.wall_color, (self.dim[0], 0),
                          (self.dim[0], self.dim[1]), self.dim[0] // 10 + 2)
            elif wall == Dir.SOUTH:
                draw.line(self.surface, self.wall_color, (0, self.dim[1]),
                          (self.dim[0], self.dim[1]), self.dim[0] // 10 + 2)
            elif wall == Dir.WEST:
                draw.line(self.surface, self.wall_color, (0, 0),
                          (0, self.dim[1]), self.dim[0] // 10)
        if self.pellet is not None:
            self.pellet.render(self.surface)

    def redraw(self) -> None:
        """Rebuild the cell surface without drawing the pellet."""
        self.surface.fill(self.open_color)
        for wall in self._get_walls():
            if wall == Dir.NORTH:
                draw.line(self.surface, self.wall_color, (0, 0),
                          (self.dim[0], 0), self.dim[0] // 10)
            elif wall == Dir.EAST:
                draw.line(self.surface, self.wall_color, (self.dim[0], 0),
                          (self.dim[0], self.dim[1]), self.dim[0] // 10 + 2)
            elif wall == Dir.SOUTH:
                draw.line(self.surface, self.wall_color, (0, self.dim[1]),
                          (self.dim[0], self.dim[1]), self.dim[0] // 10 + 2)
            elif wall == Dir.WEST:
                draw.line(self.surface, self.wall_color, (0, 0),
                          (0, self.dim[1]), self.dim[0] // 10)

    def get_size(self) -> tuple[int, int]:
        """Return the pixel size of the cell surface."""
        return self.dim

    def render(self, surface: Surface) -> None:
        """Blit the cell surface onto the target surface.

        Args:
            surface: The surface that receives the rendered cell.
        """
        surface.blit(self.surface, self.rect)

    def set_neighbours(self, neighbours: dict[Dir, "Cell" | None]) -> None:
        """Store the standard neighbours for each direction.

        Args:
            neighbours: A mapping from direction to adjacent cell.
        """
        self.neighbours = neighbours

    def set_cheat(self, neighbours: dict[Dir, "Cell" | None]) -> None:
        """Store the wraparound neighbours for each direction.

        Args:
            neighbours: A mapping from direction to wraparound cell.
        """
        self.cheat = neighbours

    def get_neighbour_from_dir(self, dir: Dir) -> Cell | None:
        """Return the standard neighbour in the given direction.

        Args:
            dir: The direction to inspect.

        Returns:
            The adjacent cell, or ``None`` if no neighbour exists.
        """
        return self.neighbours.get(dir)

    def get_cheat_from_dir(self, dir: Dir) -> Cell | None:
        """Return the wraparound neighbour in the given direction.

        Args:
            dir: The direction to inspect.

        Returns:
            The wraparound neighbour cell, if available.
        """
        return self.cheat[dir]

    @property
    def collected(self) -> bool:
        """Return whether the cell's pellet has already been collected."""
        return self.pellet.collected if self.pellet else False

    def collect(self) -> int:
        """Collect the pellet in the cell and return its score value.

        Returns:
            The points awarded by the collectible, or ``0`` if absent.
        """
        if self.pellet:
            return self.pellet.collect()
        return 0

    def __lt__(self, other: Cell) -> bool:
        """Compare cells using their coordinates for ordering."""
        return self.coord > other.coord

    def __repr__(self) -> str:
        """Return the string representation of the cell coordinate."""
        return str(self.coord)
