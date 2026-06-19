"""Pinky ghost AI implementation.

Implements Pinky, the pink ghost with behavior that calculate its path
based of player current direction.
"""
from src.game.game_objects.game_data import GameData
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.cell import Cell
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState


class Pinky(Ghost):
    """Pink ghost with player direction based path calculation.

    Pinky calculate its path based on the current player direction.
    During scatter it retreats to bottom-left corner.
    """

    def __init__(self, game: GameData, rm: ResourceManager) -> None:
        """Initialize Pinky and register it in the shared game data.

        Args:
            game: The shared game state used by all ghosts.
            rm: The resource manager used to load sprites.
        """
        self.color = (255, 192, 203)
        super().__init__(self.__get_corner(game), game, self.color, rm)
        self.game.add_ghost("pinky", self)

    @staticmethod
    def __get_corner(game: GameData) -> Cell:
        """Return Pinky's scatter corner cell.

        Args:
            game: The shared game state used to access the maze.

        Returns:
            The bottom-left maze cell used as Pinky's corner target.
        """
        return game.maze.maze_map[game.get_maze_size()[1] - 1, 0]

    def predict_player_pos(self) -> Cell:
        """Predict the player's future position by looking ahead several cells.

        Returns:
            The cell Pinky should target in hunt mode.
        """
        current_cell = self.game.get_player_pos()
        current_dir = self.game.get_player_dir()
        next_dir = self.game.get_player_next_dir()

        if current_dir is None:
            return current_cell

        prediction = current_cell
        for _ in range(4):
            check1 = prediction.get_neighbour_from_dir(current_dir)
            if next_dir is not None:
                check2 = prediction.get_neighbour_from_dir(next_dir)
            else:
                check2 = None
            if check1 is not None:
                prediction = check1
            elif (check2 is not None):
                prediction = check2
            else:
                break
        return prediction

    def get_target(self, ghost_status: GhostState) -> Cell:
        """Return the target cell based on the current ghost state.

        Args:
            ghost_status: The current state of the ghost AI.

        Returns:
            The cell that Pinky should move toward.
        """
        if ghost_status == GhostState.HUNT:
            return self.predict_player_pos()
        elif ghost_status == GhostState.SCATTER:
            return self.scatter_corner
        return self.predict_player_pos()
