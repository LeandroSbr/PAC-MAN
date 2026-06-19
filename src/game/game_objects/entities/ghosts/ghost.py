"""Base ghost class for Pac-Man AI enemies.

Provides the abstract Ghost class that serves as the base for all specific
ghost implementations (Blinky, Pinky, Inky, Clyde), handling ghost behavior,
states, pathfinding, and animations.
"""
from src.managers.resource_manager import ResourceManager
from src.utils.enums import GhostState
from src.utils.enums import Dir
from src.game.game_objects.cell import Cell
from src.game.game_objects.game_data import GameData
from src.game.game_objects.entities.entity import Entity
from src.game.game_objects.entities.ghosts.pathfinder import Pathfinder

from abc import abstractmethod
from random import shuffle
from pygame import Surface, transform


class Ghost(Entity):
    """Abstract base class for all ghost enemies.

    Implements shared ghost behavior including hunting/scattering modes,
    pathfinding, fear state handling, animation, and collision detection.
    Concrete subclasses implement specific AI strategies for individual ghosts.
    """

    def __init__(self, cell: Cell, game: GameData,
                 color: tuple[int, int, int], rm: ResourceManager) -> None:
        """Initialize the base ghost state and shared resources.

        Args:
            cell: The spawn cell of the ghost.
            game: The shared game state used by the ghost AI.
            color: The RGB color used to draw the ghost.
            rm: The resource manager used to load sprites.
        """
        super().__init__(cell, color)
        self.frightened_move_time = 400
        self.original_move_time = 300
        self.total_move_time = 300
        self.pathfinder = Pathfinder
        self.rm = rm
        self.scatter_corner = cell
        self.game = game
        self.directions = [Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]
        self.died = False
        self.path: list[Cell | None]
        self.__is_target_switched = False
        self.speed = 400
        self.distance: int | None = None
        self.__init__frames()

    def __init__frames(self) -> None:
        """Load the ghost animation frames from the resource manager."""
        if not self.rm.has_sheet_loaded:
            self.loaded = False
            return
        self.loaded = True
        self.__fear_anim = 0
        frames = self.rm.get_frame_resources(
            self.__class__.__name__.lower())
        self.direction_frames = {
            Dir.NORTH: transform.scale(
                frames[0],
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)),
            Dir.SOUTH: transform.scale(
                frames[1],
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)),
            Dir.WEST: transform.scale(
                frames[2],
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)),
            Dir.EAST: transform.scale(
                frames[3],
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)),
        }
        if self.scatter_corner.coord[1] == 0:
            self.cur_img = self.direction_frames[Dir.EAST]
        else:
            self.cur_img = self.direction_frames[Dir.WEST]
        d_frames = self.rm.get_frame_resources(
            "ghost_dead"
        )
        self.d_frames: list[Surface] = []
        for frame in d_frames:
            self.d_frames.append(transform.scale(
                frame,
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)))
        fear_frames = self.rm.get_frame_resources(
                                        "ghost_frightened")
        self.fear_frames: list[Surface] = []
        for frame in fear_frames:
            self.fear_frames.append(transform.scale(
                frame,
                (self.current_pos.dim[0] * 2 / 3,
                 self.current_pos.dim[1] * 2 / 3)))
        if self.scatter_corner.coord[1] == 0:
            self.death_frame = self.d_frames[2]
        else:
            self.death_frame = self.d_frames[3]
        self.rect = self.cur_img.get_rect(center=self.rect.center)

    def reset_animation(self) -> None:
        """Reset animation starting point."""
        if self.scatter_corner.coord[1] == 0:
            self.cur_img = self.direction_frames[Dir.EAST]
        else:
            self.cur_img = self.direction_frames[Dir.WEST]
        self.__fear_anim = 0

    def change_animation_frame(self, ghost_state: GhostState,
                               delta_t: int) -> None:
        """Update the current sprite according to state and direction.

        Args:
            ghost_state: The current ghost AI state.
            delta_t: The elapsed time since the previous update.
        """
        if not self.loaded:
            return
        if self.died:
            self.__fear_anim += delta_t
            self.cur_img = self.death_frame
            return
        if ghost_state == GhostState.FEAR:
            self.__fear_anim += delta_t
            if self.__fear_anim < 600:
                self.cur_img = self.fear_frames[0]
            elif self.__fear_anim >= 600 and self.__fear_anim < 1200:
                self.cur_img = self.fear_frames[1]
            else:
                self.__fear_anim = 0
            return
        current_dir = Dir.WEST
        if (self.current_pos is not None and
                self.target is not None):
            for k, v in self.current_pos.neighbours.items():
                if v is None:
                    continue
                if v is self.target:
                    current_dir = k
        self.cur_img = self.direction_frames[current_dir]

    @abstractmethod
    def get_target(self, ghost_status: GhostState) -> Cell:
        """Return the cell this ghost should target.

        Args:
            ghost_status: The current ghost AI state.

        Returns:
            The target cell for the current state.
        """
        pass

    def get_path(self, state: GhostState, counter: int) -> list[Cell | None]:
        """Return the next cells to follow for the requested state.

        Args:
            state: The current ghost AI state.
            counter: A frightened-state counter used for target selection.

        Returns:
            A short list containing the next path cells and a ``None``
            sentinel.
        """
        if state is GhostState.FEAR:
            return [self.get_frightened_target(counter), None]
        return self.pathfinder.get_path(self.current_pos,
                                        self.get_target(state))

    def _set_move_values(self, ghost_state: GhostState) -> None:
        """Finalize the current movement step and prepare the next target.

        Args:
            ghost_state: The current ghost AI state.
            delta_t: The elapsed time since the previous update.
        """
        if self.target is None:
            return
        self.current_pos = self.target
        if self.died:
            self.target = None
            self.__is_target_switched = False
            self.died = False
        else:
            self.target = self.path.pop(0)
        if self.target is None:
            self.path = self.get_path(ghost_state, 1)
            self.target = self.path.pop(0)
        self.progress = 0
        self.movement_elapsed_time = 0

    def __set_target(self, ghost_state: GhostState,
                     counter: int) -> None:
        """Assign a new movement target when the ghost is ready.

        Args:
            ghost_state: The current ghost AI state.
            counter: A frightened-state counter used for target selection.
            delta_t: The elapsed time since the previous update.
        """
        if self.died:
            if not self.__is_target_switched:
                self.target = self.scatter_corner
                self.death_pos = self.rect
                self.movement_elapsed_time = 0
                self.progress = 0
                self.__is_target_switched = True

        if self.target is None:
            self.path = self.get_path(ghost_state, counter)
            self.target = self.path.pop(0)

    def __update_progress(self, delta_t: int) -> None:
        """Advance the movement progress for either chase or death motion.

        Args:
            delta_t: The elapsed time since the previous update.
        """
        if self.died:
            if self.target is not None:
                if self.distance is None:
                    start_center = self.death_pos.center
                    end_center = self.target.rect.center
                    self.distance = ((end_center[0] - start_center[0])**2 +
                                     (end_center[1] - start_center[1])**2)**0.5

                if self.distance is not None:
                    if self.distance > 0:
                        distance_moved = self.speed * delta_t / 1000
                        self.progress += distance_moved / self.distance
                        self.progress = min(1.0, self.progress)
                    else:
                        self.progress = 1.0

        else:
            self.movement_elapsed_time += delta_t
            prog = self.movement_elapsed_time / self.total_move_time
            self.progress = min(1.0, prog)

    def move(self, delta_t: int, ghost_state: GhostState, counter: int = 1
             ) -> None:
        """Advance the ghost movement toward its current target.

        Args:
            delta_t: The elapsed time since the previous update.
            ghost_state: The current ghost AI state.
            counter: A frightened-state counter used for target selection.
        """
        self.__set_target(ghost_state, counter)
        if self.target is None:
            return
        self.__update_progress(delta_t)
        self._update_position_based_on_progress()

        if self.progress == 1:
            self._set_move_values(ghost_state)

        if self.target is self.current_pos:
            self.target = self.path.pop(0)

    def get_frightened_target(self, counter: int) -> Cell | None:
        """Return the frightened-mode target for the ghost.

        Args:
            counter: The frightened-state counter used to vary movement.

        Returns:
            The cell selected for frightened movement, or ``None``.
        """
        if counter == 0:
            target = self.get_furthest()
        else:
            shuffle(self.directions)
            for direction in self.directions:
                target = self.get_dir_target(direction)
                if target is not None:
                    target = target
                    break
        return target

    def get_furthest(self) -> Cell | None:
        """Return the direction that maximizes distance from the player.

        Returns:
            The cell that leads away from the player, or ``None``.
        """
        distances: dict[int, Dir] = {}
        for direction in self.directions:

            next_cell = self.get_dir_target(direction)
            if next_cell is not None:
                distances[self.pathfinder.heuristic(
                    next_cell,
                    self.game.get_player_pos()
                )] = direction
        if not distances:
            return None
        min_heuristic = min(distances.keys())
        return self.get_dir_target(distances[min_heuristic])

    def get_dir_target(self, direction: Dir) -> Cell | None:
        """Return the adjacent cell in the requested direction.

        Args:
            direction: The direction to inspect.

        Returns:
            The adjacent cell, or ``None`` if no cell exists there.
        """
        return self.current_pos.get_neighbour_from_dir(direction)

    def die(self) -> None:
        """Mark the ghost as dead."""
        self.died = True

    def respawn(self) -> None:
        """Respawn the ghost and clear its dead state."""
        super().respawn()
        self.died = False

    def reset_maze(self, cell: Cell) -> None:
        """Reset the ghost spawn cell and scatter corner.

        Args:
            cell: The new spawn cell in the updated maze.
        """
        super().reset_maze(cell)
        self.scatter_corner = cell

    def render(self, surface: Surface) -> None:
        """Render the ghost using the loaded sprite or base entity drawing.

        Args:
            surface: The surface that receives the rendered ghost.
        """
        if self.loaded:
            surface.blit(self.cur_img, self.rect)
        else:
            super().render(surface)
