"""Game constants and mapping tables.

Defines timer events, wall codes, and direction mappings used throughout
the game engine.
"""
from src.utils.enums import Dir

from pygame import USEREVENT


TIMEREVENT: int = USEREVENT + 1


WALL_MAP: dict[int, list[Dir]] = {
    0: [],
    1: [Dir.NORTH],
    2: [Dir.EAST],
    3: [Dir.NORTH, Dir.EAST],
    4: [Dir.SOUTH],
    5: [Dir.NORTH, Dir.SOUTH],
    6: [Dir.EAST, Dir.SOUTH],
    7: [Dir.NORTH, Dir.EAST, Dir.SOUTH],
    8: [Dir.WEST],
    9: [Dir.NORTH, Dir.WEST],
    10: [Dir.EAST, Dir.WEST],
    11: [Dir.NORTH, Dir.EAST, Dir.WEST],
    12: [Dir.SOUTH, Dir.WEST],
    13: [Dir.NORTH, Dir.SOUTH, Dir.WEST],
    14: [Dir.EAST, Dir.SOUTH, Dir.WEST],
    15: [Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]
}

MOVE_DIR_MAP: dict[Dir, tuple[int, int]] = {
    Dir.NORTH: (0, -1),
    Dir.EAST: (1, 0),
    Dir.SOUTH: (0, 1),
    Dir.WEST: (-1, 0),
}
