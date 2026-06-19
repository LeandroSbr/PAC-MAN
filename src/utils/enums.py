"""Game state and action enumerations.

Defines enumeration types for application states, game states, player actions,
and input priority.
"""
from enum import Enum, auto


class AppState(Enum):
    """Define the high-level application states."""

    MENU = auto()
    SCORES = auto()
    INFO = auto()
    GAME = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    QUIT = auto()


class GameState(Enum):
    """Define the internal states of the game world."""

    READY = auto()
    ONGOING = auto()
    PAUSED = auto()
    DEATH_ANIMATION = auto()
    WON = auto()
    LOST = auto()
    QUIT = auto()


class Action(Enum):
    """Define the actions that can be triggered during gameplay."""

    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SKIP_ANIMATION = auto()
    PAUSE = auto()
    RESUME = auto()
    SELECT = auto()
    BACK = auto()
    QUIT = auto()
    TIMERDOWN = auto()
    CHANGE_LEVEL = auto()
    FREEZE_GHOSTS = auto()
    LIVES_UP = auto()
    INCREASE_SPEED = auto()
    DECREASE_SPEED = auto()
    RESET_SPEED = auto()


class ClickPriority(Enum):
    """Define the priority order for resolving input clicks."""

    MOUSE = auto()
    KEYBOARD = auto()


class View(Enum):
    """Define the available menu views."""

    PAUSE = auto()
    EXTRA = auto()


class Dir(Enum):
    """Define the four cardinal movement directions."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


class GhostState(Enum):
    """Define the possible states for ghosts."""

    HUNT = auto()
    SCATTER = auto()
    FEAR = auto()


class PlayerStatus(Enum):
    """Define the possible player statuses."""

    NORMAL = auto()
    SUPER = auto()
    DEAD = auto()
