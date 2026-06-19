"""Shared game state container.

Provides a centralized data structure for storing and managing game state
shared between the player, ghosts, and other game systems including the maze,
current level, score, and entity references.
"""
from __future__ import annotations
from src.game.game_objects.cell import Cell
from src.game.game_objects.maze import Maze

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from src.utils.enums import Dir, PlayerStatus
if TYPE_CHECKING:
    from src.game.game_objects.entities.player import Player
    from src.game.game_objects.entities.ghosts.ghost import Ghost
    from pygame import Rect


@dataclass
class GameData:
    """Store the shared game state used by the player and ghosts."""

    maze: Maze
    player: Player
    level: int
    ghosts: dict[str, Ghost] = field(default_factory=dict)
    score: int = 0

    def get_ghosts_rect(self) -> list[Rect]:
        """Return the rectangles for all registered ghosts."""
        return [ghost.rect for ghost in self.ghosts.values()]

    def get_level(self) -> int:
        """Return the current level number."""
        return self.level

    def get_ghost(self, ghost_name: str) -> Ghost:
        """Return a ghost by name.

        Args:
            ghost_name: The identifier of the ghost to retrieve.

        Returns:
            The requested ghost instance.
        """
        return self.ghosts[ghost_name]

    def get_player_pos(self) -> Cell:
        """Return the player's current cell."""
        return self.player.current_pos

    def get_ghost_pos(self, ghost_name: str) -> Cell:
        """Return the current cell of a named ghost.

        Args:
            ghost_name: The identifier of the ghost to retrieve.

        Returns:
            The current cell occupied by the ghost.
        """
        return self.ghosts[ghost_name].current_pos

    def get_maze_size(self) -> tuple[int, int]:
        """Return the maze dimensions in cells."""
        return self.maze.maze_size

    def get_player_dir(self) -> Dir | None:
        """Return the player's current movement direction."""
        return self.player.get_dir()

    def has_score_changed(self) -> bool:
        """Return whether the player's score changed since the last check."""
        if self.score != self.get_score():
            self.score = self.get_score()
            return True
        return False

    def get_player_status(self) -> PlayerStatus:
        """Return the current player status."""
        return self.player.status

    def reset_player_status(self) -> None:
        """Reset the player status to normal."""
        self.player.status = PlayerStatus.NORMAL

    def get_score(self) -> int:
        """Return the player's current score."""
        return self.player.points

    def get_player_next_dir(self) -> Dir | None:
        """Return the player's queued movement direction."""
        return self.player.get_next_dir()

    def add_ghost(self, ghost_name: str, ghost: Ghost) -> None:
        """Register a ghost in the shared game state.

        Args:
            ghost_name: The identifier to associate with the ghost.
            ghost: The ghost instance to store.
        """
        self.ghosts[ghost_name] = ghost

    def change_maze(self, maze: Maze) -> None:
        """Replace the current maze with a new one.

        Args:
            maze: The new maze instance.
        """
        self.maze = maze

    def change_level(self, level: int) -> None:
        """Update the current level number.

        Args:
            level: The new level number.
        """
        self.level = level
