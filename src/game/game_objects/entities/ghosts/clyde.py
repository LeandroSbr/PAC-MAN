"""Clyde ghost AI implementation.

Implements Clyde, the orange ghost with behavior that alternates between
aggressive pursuit and retreat based on proximity to the player.
"""
from src.game.game_objects.game_data import GameData
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.cell import Cell
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState


class Clyde(Ghost):
    """Orange ghost with proximity-based behavioral switching.

    Clyde exhibits dual behavior: pursues the player when distant, but retreats
    to its scatter corner when too close. During scatter mode, targets the
    bottom-right corner of the maze.
    """

    def __init__(self, game: GameData, rm: ResourceManager) -> None:
        """Initialize Clyde and register it in the shared game data.

        Args:
            game: The shared game state used by all ghosts.
            rm: The resource manager used to load sprites.
        """
        self.color = (255, 165, 0)
        super().__init__(self.__get_corner(game), game, self.color, rm)
        self.game.add_ghost("clyde", self)

    @staticmethod
    def __get_corner(game: GameData) -> Cell:
        """Return Clyde's scatter corner cell.

        Args:
            game: The shared game state used to access the maze.

        Returns:
            The bottom-right maze cell used as Clyde's corner target.
        """
        maze_size = game.get_maze_size()
        return game.maze.maze_map[maze_size[1] - 1, maze_size[0] - 1]

    def get_distance_based_target(self) -> Cell:
        """Choose a target based on Clyde's distance from the player.

        Returns:
            The player's cell when Clyde is far enough away, otherwise the
            scatter corner.
        """
        dist_x = abs(self.game.get_player_pos().coord[0]
                     - self.current_pos.coord[0])
        dist_y = abs(self.game.get_player_pos().coord[1]
                     - self.current_pos.coord[1])
        dist = dist_x + dist_y
        if dist >= 8:
            return self.game.get_player_pos()
        else:
            return self.scatter_corner

    def get_target(self, ghost_status: GhostState) -> Cell:
        """Return the target cell based on the current ghost state.

        Args:
            ghost_status: The current state of the ghost AI.

        Returns:
            The cell that Clyde should move toward.
        """
        if ghost_status == GhostState.HUNT:
            return self.get_distance_based_target()
        elif ghost_status == GhostState.SCATTER:
            return self.scatter_corner
        return self.get_distance_based_target()
