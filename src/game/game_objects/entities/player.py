"""Player character entity for the Pac-Man game.

Implements the controllable player character with movement, animation,
collectible collection, life management, and special power-up states.
"""
from src.game.game_objects.entities.entity import Entity
from src.game.game_objects.cell import Cell
from src.managers.resource_manager import ResourceManager
from src.utils.enums import Dir, GhostState
from src.utils.enums import PlayerStatus

from pygame import Surface, transform


class Player(Entity):
    """Player character with lives, score, and power-up management.

    Extends Entity to implement player-specific behavior including directional
    input handling, collectible tracking, life management, death animation,
    and special states like invincibility after eating power pellets.
    """

    def __init__(self, spawn_point: Cell,
                 collectibles:  int,
                 rm: ResourceManager,
                 lives: int = 3) -> None:
        """Initialize the player entity and its animation state.

        Args:
            spawn_point: The cell where the player spawns.
            collectibles: The number of collectibles available in the maze.
            rm: The resource manager used to load sprites and config values.
            lives: The initial number of lives.
        """
        self.color = (255, 255, 0)
        super().__init__(spawn_point, self.color)
        self.points = 0
        self.rm = rm
        self.__total_collectibles = collectibles
        self.__remaining_collectibles = collectibles
        self.__lives = lives
        self.__remaining_lives = self.__lives
        self.status: PlayerStatus = PlayerStatus.NORMAL
        self.__current_dir: Dir | None = None
        self.__ghosts_eaten = 0
        self.__next_dir: Dir | None = None
        self.cur_frame = 1
        self.death_frame = 0
        self.__init_frames()
        self.original_speed = self.total_move_time
        self.is_cheating = False
        self.animation_timer = 0
        self.__ghost_points = self.rm.config.get("points_per_ghost", 200)

    def death_animation(self, delta_t: int) -> bool:
        """Advance the death animation and report when it finishes.

        Args:
            delta_t: The elapsed time since the previous update.

        Returns:
            ``True`` when the death animation has completed, otherwise
            ``False``.
        """
        if not self.loaded:
            return True
        if self.cur_frame == len(self.death_frames):
            return True
        self.animation_timer += delta_t
        if self.animation_timer >= 150:
            self.cur_frame = (self.cur_frame + 1)
            self.animation_timer = 0
            if self.cur_frame <= len(self.death_frames) - 1:
                self.cur_img = self.death_frames[self.cur_frame]
        return False

    def cheat_mode(self) -> None:
        """Toggle cheat mode for the player."""
        self.is_cheating = not self.is_cheating

    def reset_speed(self) -> None:
        """Restore the player's movement speed to the original value."""
        self.total_move_time = self.original_speed

    def decrease_speed(self) -> None:
        """Decrease the player's movement speed if the limit allows it."""
        if self.total_move_time >= 500:
            return
        self.total_move_time += self.original_speed // 25

    def increase_speed(self) -> None:
        """Increase the player's movement speed if the limit allows it."""
        if self.total_move_time <= 100:
            return
        self.total_move_time -= self.original_speed // 25

    def add_life(self) -> None:
        """Increase the player's remaining lives by one."""
        self.__remaining_lives += 1

    def __init_frames(self) -> None:
        """Load the directional and death animation frames."""
        if not self.rm.has_sheet_loaded:
            self.loaded = False
            return
        self.loaded = True
        north = self.rm.get_frame_resources("pacman_up")
        south = self.rm.get_frame_resources("pacman_down")
        west = self.rm.get_frame_resources("pacman_left")
        east = self.rm.get_frame_resources("pacman_right")
        scale_n: list[Surface] = []
        scale_s: list[Surface] = []
        scale_w: list[Surface] = []
        scale_e: list[Surface] = []
        for n, s, w, e in zip(north, south, west, east):
            scale_n.append(
                transform.scale(n, (self.current_pos.dim[0] * 2 / 3,
                                    self.current_pos.dim[1] * 2 / 3))
            )
            scale_s.append(
                transform.scale(s, (self.current_pos.dim[0] * 2 / 3,
                                    self.current_pos.dim[1] * 2 / 3))
            )
            scale_w.append(
                transform.scale(w, (self.current_pos.dim[0] * 2 / 3,
                                    self.current_pos.dim[1] * 2 / 3))
            )
            scale_e.append(
                transform.scale(e, (self.current_pos.dim[0] * 2 / 3,
                                    self.current_pos.dim[1] * 2 / 3))
            )
        self.dir_frames = {
            Dir.NORTH: scale_n,
            Dir.SOUTH: scale_s,
            Dir.WEST: scale_w,
            Dir.EAST: scale_e
        }
        death_frames = self.rm.get_frame_resources("pacman_death")
        self.death_frames: list[Surface] = []
        for frame in death_frames:
            self.death_frames.append(
                transform.scale(frame, (self.current_pos.dim[0] * 2 / 3,
                                        self.current_pos.dim[1] * 2 / 3))
            )
        self.frames = self.dir_frames[Dir.WEST]
        self.cur_img = self.frames[self.cur_frame]
        self.rect = self.cur_img.get_rect(center=self.rect.center)
        self.animation_timer = 0

    def get_lives(self) -> int:
        """Return the number of remaining lives."""
        return self.__remaining_lives

    def reset_lives(self) -> None:
        """Reset the remaining lives to the initial value."""
        self.__remaining_lives = self.__lives

    def set_next_dir(self, dir: Dir | None) -> None:
        """Queue the next movement direction for the player.

        Args:
            dir: The next direction to try to move toward.
        """
        self.__next_dir = dir

    def __set_dir(self, dir: Dir | None) -> None:
        """Set the current movement direction.

        Args:
            dir: The direction to activate.
        """
        self.__current_dir = dir

    def get_dir(self) -> Dir | None:
        """Return the current movement direction."""
        return self.__current_dir

    def get_next_dir(self) -> Dir | None:
        """Return the queued next movement direction."""
        return self.__next_dir

    def win(self) -> bool:
        """Return whether all collectibles have been consumed."""
        return self.__remaining_collectibles == 0

    def _set_move_values(self) -> None:
        """Compute the next movement target and reset progress values."""
        if self.__current_dir is None:
            return
        if self.is_cheating:
            self.target = self.current_pos.get_cheat_from_dir(
                                                self.__current_dir
                                            )
        else:
            self.target = self.current_pos.get_neighbour_from_dir(
                                                self.__current_dir
                                            )
        if self.target is None:
            self.__current_dir = None
            return

        self.movement_elapsed_time = 0
        self.progress = 0.0

    def reset_animation(self) -> None:
        """Reset the animation to the starting point."""
        self.cur_frame = 1
        self.cur_img = self.frames[self.cur_frame]
        self.animation_timer = 0

    def __change_animation_frame(self, delta_t: int) -> None:
        """Advance the running animation frame if sprites are loaded.

        Args:
            delta_t: The elapsed time since the previous update.
        """
        if not self.loaded:
            return
        self.animation_timer += delta_t
        if self.animation_timer >= 100:
            self.cur_frame = (self.cur_frame + 1) % 4
            self.animation_timer = 0
            self.cur_img = self.frames[self.cur_frame]

    def set_new_frames(self) -> None:
        """Update the animation frames to match the current direction."""
        if not self.loaded:
            return
        if self.__current_dir is None:
            self.frames = self.dir_frames[Dir.WEST]
        else:
            self.frames = self.dir_frames[self.__current_dir]

    def move(self, delta_t: int,
             ghost_state: GhostState = GhostState.HUNT) -> None:
        """Advance the player movement and animation state.

        Args:
            delta_t: The elapsed time since the previous update.
            ghost_state: The current ghost state, kept for interface parity.
        """
        ghost_state
        self.__change_animation_frame(delta_t)
        if (self.target is None):
            if (self.__next_dir is not None and
                    (self.current_pos.is_open(self.__next_dir)
                     or self.is_cheating)):
                self.__set_dir(self.__next_dir)
                self.__next_dir = None
                self.set_new_frames()

            if (self.__current_dir is not None):
                self._set_move_values()

        if self.target is not None:
            self.movement_elapsed_time += delta_t
            prog = self.movement_elapsed_time / self.total_move_time
            self.progress = min(1.0, prog)
            self._update_position_based_on_progress()

        if self.progress == 1:
            self._complete_movement()

    def _complete_movement(self) -> None:
        """Finalize the current movement and process collected pellets."""
        if self.target is None:
            return
        self.current_pos = self.target
        self.rect.center = self.target.rect.center
        self.target = None
        self.progress = 0.0
        self.movement_elapsed_time = 0
        self.eat_pellet()

    def eat_pellet(self) -> None:
        """Collect the pellet on the current cell, if present."""
        if (self.current_pos.pellet is not None and
                not self.current_pos.collected):
            self.__remaining_collectibles -= 1
            self.points += self.current_pos.collect()
            if self.current_pos.pellet.is_power_pellet:
                self.status = PlayerStatus.SUPER
                self.__ghosts_eaten = 0
            self.current_pos.redraw()

    def eat_ghost(self) -> None:
        """Award points for eating a ghost and update the combo counter."""
        self.points += self.__ghost_points * (2 ** self.__ghosts_eaten)
        self.__ghosts_eaten += 1

    def respawn(self) -> None:
        """Respawn the player and clear directional input."""
        super().respawn()
        self.__current_dir = None
        self.set_next_dir(None)

    def is_alive(self) -> bool:
        """Return whether the player still has at least one life left."""
        return self.__remaining_lives > 0

    def lose_life(self) -> None:
        """Consume one life and switch to the death animation frame."""
        self.animation_timer = 0
        self.__remaining_lives -= 1
        if not self.loaded:
            return
        self.death_frame = 0
        self.cur_img = self.death_frames[self.death_frame]

    def reset_collectible_count(self, to_collect: int = -1) -> None:
        """Reset the number of remaining collectibles.

        Args:
            to_collect: The new collectible count.
        """
        if to_collect == -1:
            self.__remaining_collectibles = self.__total_collectibles
        else:
            self.__remaining_collectibles = to_collect

    def render(self, surface: Surface) -> None:
        """Render the player using the loaded sprite or base entity drawing.

        Args:
            surface: The surface that receives the rendered player.
        """
        if self.loaded:
            surface.blit(self.cur_img, self.rect)
        else:
            super().render(surface)
