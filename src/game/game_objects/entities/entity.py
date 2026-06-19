"""Base entity class for game characters.

Provides the abstract Entity class that serves as the base for all game
entities (player and ghosts), handling movement, cell transitions, animation,
and rendering.
"""
from src.utils.enums import GhostState
from src.utils.templates import Renderizable
from src.game.game_objects.cell import Cell

import pygame
from pygame import Surface
from abc import abstractmethod


class Entity(Renderizable):
    """Abstract base class for all game entities (player and ghosts).

    Manages entity state including position, movement,
    animation, and rendering.
    Entities move between maze cells with smooth transitions
    and can be rendered on the game surface.
    """

    def __init__(self, spawn_point: Cell, color: tuple[int, int, int]) -> None:
        """Initialize the base entity state and rendering surface.

        Args:
            spawn_point: The cell where the entity spawns.
            color: The RGB color used to draw the entity.
        """
        self.color = color
        self.spawn_cell: Cell = spawn_point
        self.spawn_coord: tuple[int, int] = self.spawn_cell.coord
        self.current_pos: Cell = spawn_point
        self.target: Cell | None = None
        self.active: bool = True
        self.progress: float = 0.0
        self.movement_elapsed_time: int = 0
        self.total_move_time: int = 200
        self.init_render_components()

    def init_render_components(self) -> None:
        """Create the base rendering surface and entity rect."""
        cell_size = self.current_pos.get_size()
        player_size = (cell_size[0] // 2, cell_size[1] // 2)
        self.surface = Surface(player_size, pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect(
            center=(self.current_pos.rect.centerx,
                    self.current_pos.rect.centery)
        )
        pygame.draw.circle(self.surface, self.color,
                           self.surface.get_rect().center,
                           min(self.rect.size) // 2)

    def get_position(self) -> tuple[int, int]:
        """Return the current maze coordinate of the entity."""
        return self.current_pos.coord

    @abstractmethod
    def move(self, delta_t: int, ghost_state: GhostState) -> None:
        """Advance the entity movement for the current frame.

        Args:
            delta_t: The elapsed time since the previous update.
            ghost_state: The current ghost state used by moving entities.
        """
        pass

    def _update_position_based_on_progress(self) -> None:
        """Interpolate entity position between its current cell and target."""
        if self.target is None:
            return
        start_center = self.current_pos.rect.center
        end_center = self.target.rect.center

        center_offset_x = (end_center[0] - start_center[0])
        center_offset_y = (end_center[1] - start_center[1])
        new_x = int(start_center[0] + center_offset_x * self.progress)
        new_y = int(start_center[1] + center_offset_y * self.progress)

        self.rect.center = (new_x, new_y)

    def get_spawn_coord(self) -> tuple[int, int]:
        """Return the original spawn coordinate of the entity."""
        return self.spawn_coord

    def respawn(self) -> None:
        """Move the entity back to its spawn cell and reset movement state."""
        self.current_pos = self.spawn_cell
        self.rect.center = self.current_pos.rect.center
        self.target = None
        self.progress = 0.0
        self.movement_elapsed_time = 0

    def update_pos(self, dest: Cell) -> None:
        """Update the current cell reference without changing the rect.

        Args:
            dest: The new current cell.
        """
        self.current_pos = dest

    def render(self, surface: Surface) -> None:
        """Blit the entity surface onto the target surface.

        Args:
            surface: The surface that receives the rendered entity.
        """
        surface.blit(self.surface, self.rect)

    def reset_maze(self, cell: Cell) -> None:
        """Reset the entity spawn cell and clear its movement target.

        Args:
            cell: The new spawn cell in the updated maze.
        """
        self.spawn_cell = cell
        self.current_pos = cell
        self.target = None
