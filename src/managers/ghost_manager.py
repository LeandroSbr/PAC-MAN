"""GhostManager class implementation."""
from src.game.game_objects.entities.ghosts.ghost import Ghost
from src.game.game_objects.entities.ghosts.blinky import Blinky
from src.game.game_objects.entities.ghosts.clyde import Clyde
from src.game.game_objects.entities.ghosts.inky import Inky
from src.game.game_objects.entities.ghosts.pinky import Pinky
from src.game.game_objects.game_data import GameData
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState
from src.utils.enums import PlayerStatus


class GhostManager:
    """GhostManager class implementation.

    Class responsable to manage the ghosts behaviour and logic.
    """

    def __init__(self, game_data: GameData,
                 resource_manager: ResourceManager) -> None:
        """Initialize the ghost manager and create the ghost roster.

        Args:
            game_data: The shared game state used by all ghosts.
            resource_manager: The resource manager used to load sprites.
        """
        self.rm = resource_manager
        self.game_data = game_data
        self.time_since_last_state_change = 0
        self.state_durations: list[dict[str, float]] = [
                                    {"hunt": 20000, "scatter": 7000},
                                    {"hunt": 20000, "scatter": 7000},
                                    {"hunt": 20000, "scatter": 5000},
                                    {"hunt": 20000, "scatter": 1000/60},
                                    {"hunt": float('inf'), "scatter": 0}
                                ]
        self.state_durations_5: list[dict[str, float]] = [
                                    {"hunt": 20000, "scatter": 5000},
                                    {"hunt": 20000, "scatter": 5000},
                                    {"hunt": 20000, "scatter": 5000},
                                    {"hunt": 20000, "scatter": 1000/60},
                                    {"hunt": float('inf'), "scatter": 0}
                                ]
        self.player_invinc: dict[int, int] = {
            1: 6000, 2: 5000, 3: 5000, 4: 5000,
            5: 4000, 6: 4000, 7: 4000, 8: 4000,
            9: 3000, 10: 3000, 11: 2000, 12: 2000,
            13: 1000, 14: 1000, 15: 1000, 16: 1000,
            17: 0, 18: 1000,
        }
        self.phase_counter = 0
        self.frightened_counter = 0
        self.ghost_state = GhostState.HUNT
        self.freeze = False
        self._generate_ghosts()

    def reset_animations(self) -> None:
        """Reset ghosts cur_img."""
        for ghost in self.ghosts:
            ghost.reset_animation()

    def set_freeze(self) -> None:
        """Toggle whether ghosts are allowed to move."""
        self.freeze = not self.freeze

    def _generate_ghosts(self) -> None:
        """Create the four ghost instances managed by the game."""
        self.ghosts: list[Ghost] = [
            Blinky(self.game_data, self.rm),
            Pinky(self.game_data, self.rm),
            Inky(self.game_data, self.rm),
            Clyde(self.game_data, self.rm)
        ]

    def __get_frightened_time(self) -> int:
        """Return how long the frightened state should last.

        Returns:
            The frightened duration in milliseconds for the current level.
        """
        return self.player_invinc.get(self.game_data.get_level(), 0)

    def update(self, delta_t: int) -> None:
        """Advance ghost state and movement logic.

        Args:
            delta_t: The elapsed time since the previous update.
        """
        if self.game_data.get_player_status() == PlayerStatus.SUPER:
            if self.ghost_state is not GhostState.FEAR:
                self.previous_state = self.ghost_state
            self.ghost_state = GhostState.FEAR
            self.frightened_counter = 0
            self.game_data.reset_player_status()

        if self.ghost_state == GhostState.FEAR:
            if self.frightened_counter == 0:
                for ghost in self.ghosts:
                    ghost.total_move_time = ghost.frightened_move_time
                    ghost.movement_elapsed_time = int(ghost.total_move_time *
                                                      ghost.progress)

            self.frightened_counter += delta_t

            if self.frightened_counter > self.__get_frightened_time():
                self.frightened_counter = 0
                self.ghost_state = self.previous_state
                for ghost in self.ghosts:
                    ghost.total_move_time = ghost.original_move_time
                    ghost.movement_elapsed_time = int(ghost.total_move_time *
                                                      ghost.progress)

        self.move_ghosts(delta_t)

    def move_ghosts(self, delta_t: int) -> None:
        """Update the global ghost state machine and move every ghost.

        Args:
            delta_t: The elapsed time since the previous update.
        """
        if self.ghost_state is GhostState.HUNT:
            self.time_since_last_state_change += delta_t

            if (self.time_since_last_state_change >=
                    self.state_durations[self.phase_counter]["hunt"]):
                self.ghost_state = GhostState.SCATTER
                self.time_since_last_state_change = 0

        elif self.ghost_state is GhostState.SCATTER:
            self.time_since_last_state_change += delta_t

            if (self.time_since_last_state_change >=
                    self.state_durations[self.phase_counter]["scatter"]):
                self.ghost_state = GhostState.HUNT
                self.time_since_last_state_change = 0
                self.phase_counter += 1

        if not self.freeze:
            for ghost in self.ghosts:
                ghost.change_animation_frame(self.ghost_state, delta_t)
                ghost.move(delta_t, self.ghost_state)

    def respawn_all_ghosts(self) -> None:
        """Reset ghost state and respawn every ghost at its spawn point."""
        self.phase_counter = 0
        self.ghost_state = GhostState.HUNT
        self.time_since_last_state_change = 0
        self.frightened_counter = 0
        for ghost in self.ghosts:
            ghost.total_move_time = ghost.original_move_time
            ghost.respawn()
