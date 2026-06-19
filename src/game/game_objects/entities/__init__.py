"""Game entities package.

Provides entity classes for game objects including the player character
and ghost enemies.
"""
from .entity import Entity
from .player import Player
from .ghosts.ghost import Ghost


__all__ = ["Entity", "Player", "Ghost"]
