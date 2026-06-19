"""Blinky ghost AI implementation.

Implements Blinky, the red ghost that pursues the player directly using
aggressive pathfinding behavior.
"""
from src.game.game_objects.game_data import GameData
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.cell import Cell
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState


class Blinky(Ghost):
    """Red ghost with direct pursuit AI behavior.

    Blinky is an aggressive ghost that pursues the player directly. During
    scatter mode, it targets the top-left corner of the maze.
    """

    def __init__(self, game: GameData, rm: ResourceManager) -> None:
        """Initialize Blinky and register it in the shared game data.

        Args:
            game: The shared game state used by all ghosts.
            rm: The resource manager used to load sprites.
        """
        self.color = (255, 0, 0)
        super().__init__(self.__get_corner(game), game, self.color, rm)
        self.game.add_ghost("blinky", self)

    @staticmethod
    def __get_corner(game: GameData) -> Cell:
        """Return Blinky's scatter corner cell.

        Args:
            game: The shared game state used to access the maze.

        Returns:
            The top-left maze cell used as Blinky's corner target.
        """
        return game.maze.maze_map[(0, 0)]

    def get_target(self, ghost_status: GhostState,) -> Cell:
        """Return the target cell based on the current ghost state.

        Args:
            ghost_status: The current state of the ghost AI.

        Returns:
            The cell that Blinky should move toward.
        """
        if ghost_status == GhostState.HUNT:
            return self.game.get_player_pos()
        elif ghost_status == GhostState.SCATTER:
            return self.scatter_corner
        return self.game.get_player_pos()
