"""Maze layout, rendering, and cell management.

Provides the Maze class for representing the game maze structure, rendering
maze cells, managing collectibles (pellets and power pellets), and tracking
navigation data for entities.
"""
from src.game.game_objects.entities.collect.pellet import Pellet
from src.game.game_objects.entities.collect.power_pellet import PowerPellet
from src.game.game_objects.entities.collect.collectible import Collectible
from src.game.game_objects.entities.entity import Entity
from src.managers.resource_manager import ResourceManager
from src.utils.enums import Dir
from src.game.game_objects.cell import Cell
from src.utils.templates import Renderizable

from pygame import Surface


class Maze(Renderizable):
    """Represent the maze surface, cells, and navigation helpers."""

    def __init__(self, layout: list[list[int]],
                 screen_size: tuple[int, int],
                 rm: ResourceManager,
                 size: tuple[int, int] = (15, 15)) -> None:
        """Create a maze from a layout and prepare its rendering data.

        Args:
            layout: The integer layout describing walls and paths.
            screen_size: The size of the window surface.
            rm: The resource manager used to fetch configuration values.
            size: The maze dimensions in cells.
        """
        self.layout = layout
        self.maze_size = size
        self.power_pellets_pos = {
            (0, 0), (0, self.maze_size[0] - 1), (self.maze_size[1] - 1, 0),
            (self.maze_size[1] - 1, self.maze_size[0] - 1)
        }
        self.__pellet_count = self.maze_size[0] * self.maze_size[1] - 99
        self.rm = rm
        self.init_render_components(screen_size)
        self._init_maze(layout)
        self.draw_maze_surface()

    def get_pellet_amount(self) -> int:
        """Return the total number of pellets available in the maze."""
        return self.__pellet_count

    def init_render_components(self, screen_size: tuple[int, int]) -> None:
        """Initialize the maze surface and its screen placement.

        Args:
            screen_size: The size of the window surface.
        """
        self.screen_size = screen_size
        cell_px = int(
            min(
                (self.screen_size[0] * 0.9) / self.maze_size[0],
                (self.screen_size[1] * 0.9) / self.maze_size[1],
            )
        )

        self.cell_size = (cell_px, cell_px)
        self.size = (self.cell_size[0] * self.maze_size[0],
                     self.cell_size[1] * self.maze_size[1])
        self.surface = Surface(self.size)
        self.rect = self.surface.get_rect(center=(self.screen_size[0] // 2,
                                                  self.screen_size[1] // 2))

    def draw_maze_surface(self) -> None:
        """Render every maze cell onto the internal maze surface."""
        for cell in self.maze_map.values():
            cell.render(self.surface)

    def draw_entities(self, entities: list[Entity]) -> None:
        """Render entities, targets, and current positions on the maze.

        Args:
            entities: The entities to draw on top of the maze.
        """
        for entity in entities:
            entity.current_pos.render(self.surface)
            if entity.target:
                entity.target.render(self.surface)
        for entity in entities:
            entity.render(self.surface)

    def __check_logo_area(self, pos: tuple[int, int]) -> bool:
        """Return whether a cell lies outside the central logo area.

        Args:
            pos: The cell coordinate to check.

        Returns:
            ``True`` if the cell is outside the logo area, otherwise ``False``.
        """
        horizontal_check: bool = not (
            ((self.maze_size[0] - 1) // 2) - 5 <= pos[1] and
            ((self.maze_size[0] - 1) // 2) + 5 >= pos[1]
        )

        vertical_check: bool = not (
            ((self.maze_size[1] - 1) // 2) - 4 <= pos[0] and
            ((self.maze_size[1] - 1) // 2) + 4 >= pos[0]
        )

        return horizontal_check or vertical_check

    def __init_cell_pellet(self, cell_pos: tuple[int, int]
                           ) -> Collectible | None:
        """Create the collectible assigned to a maze cell, if any.

        Args:
            cell_pos: The coordinate of the cell being initialized.

        Returns:
            A pellet, a power pellet, or ``None``.
        """
        if cell_pos in self.power_pellets_pos:
            return PowerPellet(self.rm.config.get("points_per_super_pacgum",
                                                  100))
        elif self.__check_logo_area(cell_pos):
            return Pellet(self.rm.config.get("points_per_pacgum", 10))
        else:
            return None

    def _init_maze(self, layout: list[list[int]]) -> None:
        """Build the maze cell map from the provided layout."""
        self.maze_map: dict[tuple[int, int], Cell] = {}
        for i, row in enumerate(layout):
            for j, wall_value in enumerate(row):
                cell = Cell((i, j), wall_value, self.cell_size,
                            self.__init_cell_pellet((i, j)))
                self.maze_map[(i, j)] = cell
        self._set_cells_neighbours()

    def _set_cells_neighbours(self) -> None:
        """Compute standard and wraparound neighbours for every cell."""
        for cell in self.maze_map.values():
            neighbours: dict[Dir, Cell | None] = {}
            cheat: dict[Dir, Cell | None] = {}
            for d in Dir:
                neighbours[d] = self._get_neighbour_from_direction(cell, d)
                cheat[d] = self._get_cheat_from_direction(cell, d)
            cell.set_neighbours(neighbours)
            cell.set_cheat(cheat)

    def _get_cheat_from_direction(
                    self, cell: Cell, dir: Dir
                ) -> Cell | None:
        """Return the wraparound neighbour for a direction, if any.

        Args:
            cell: The source cell.
            dir: The direction to inspect.

        Returns:
            The wraparound neighbour cell, or ``None`` at the border.
        """
        if dir == Dir.NORTH:
            return self.maze_map.get((cell.coord[0] - 1, cell.coord[1]), None)
        if dir == Dir.EAST:
            return self.maze_map.get((cell.coord[0], cell.coord[1] + 1), None)
        if dir == Dir.SOUTH:
            return self.maze_map.get((cell.coord[0] + 1, cell.coord[1]), None)
        if dir == Dir.WEST:
            return self.maze_map.get((cell.coord[0], cell.coord[1] - 1), None)

    def _get_neighbour_from_direction(
                    self, cell: Cell, dir: Dir
                ) -> Cell | None:
        """Return the adjacent walkable neighbour for a direction.

        Args:
            cell: The source cell.
            dir: The direction to inspect.

        Returns:
            The adjacent cell if the path is open, otherwise ``None``.
        """
        if cell.is_closed(dir):
            return None
        if dir == Dir.NORTH:
            return self.maze_map.get((cell.coord[0] - 1, cell.coord[1]), None)
        if dir == Dir.EAST:
            return self.maze_map.get((cell.coord[0], cell.coord[1] + 1), None)
        if dir == Dir.SOUTH:
            return self.maze_map.get((cell.coord[0] + 1, cell.coord[1]), None)
        if dir == Dir.WEST:
            return self.maze_map.get((cell.coord[0], cell.coord[1] - 1), None)

    def render(self, surface: Surface) -> None:
        """Blit the maze surface onto the target surface.

        Args:
            surface: The surface that receives the rendered maze.
        """
        surface.blit(self.surface, self.rect)
