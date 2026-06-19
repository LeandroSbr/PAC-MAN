"""Inky ghost AI implementation.

Implements Inky, the cyan ghost with complex AI behavior influenced by both
the player position and Blinky's position for unpredictable movement.
"""
from src.game.game_objects.game_data import GameData
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.cell import Cell
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState


class Inky(Ghost):
    """Cyan ghost with player and Blinky-dependent AI behavior.

    Inky exhibits unpredictable movement influenced by both the player's
    position and Blinky's position, making it harder to predict. During
    scatter mode, targets the top-right corner of the maze.
    """

    def __init__(self, game: GameData, rm: ResourceManager) -> None:
        """Initialize Inky and register it in the shared game data.

        Args:
            game: The shared game state used by all ghosts.
            rm: The resource manager used to load sprites.
        """
        self.color = (0, 255, 255)
        super().__init__(self.__get_corner(game), game, self.color, rm)
        self.game.add_ghost("inky", self)

    @staticmethod
    def __get_corner(game: GameData) -> Cell:
        """Return Inky's scatter corner cell.

        Args:
            game: The shared game state used to access the maze.

        Returns:
            The top-right maze cell used as Inky's corner target.
        """
        return game.maze.maze_map[0, game.get_maze_size()[0] - 1]

    def triangulate_target(self) -> Cell:
        """Compute Inky's hunt target using the player and Blinky positions.

        Returns:
            The maze cell Inky should target in hunt mode.
        """
        dist_x = (self.game.get_player_pos().coord[0] -
                  self.game.get_ghost_pos("blinky").coord[0])

        dist_y = (self.game.get_player_pos().coord[1] -
                  self.game.get_ghost_pos("blinky").coord[1])

        target_x = min(self.game.get_player_pos().coord[0] + dist_x,
                       self.game.get_maze_size()[0] - 1)

        target_y = min(self.game.get_player_pos().coord[1] + dist_y,
                       self.game.get_maze_size()[1] - 1)

        if target_x < 0:
            target_x = 0
        elif target_x >= self.game.get_maze_size()[1]:
            target_x = self.game.get_maze_size()[1] - 1

        if target_y < 0:
            target_y = 0
        elif target_y >= self.game.get_maze_size()[0]:
            target_y = self.game.get_maze_size()[0] - 1

        return self.game.maze.maze_map[(target_x, target_y)]

    def get_target(self, ghost_status: GhostState) -> Cell:
        """Return the target cell based on the current ghost state.

        Args:
            ghost_status: The current state of the ghost AI.

        Returns:
            The cell that Inky should move toward.
        """
        if ghost_status == GhostState.HUNT:
            return self.triangulate_target()

        elif ghost_status == GhostState.SCATTER:
            return self.scatter_corner

        return self.triangulate_target()
