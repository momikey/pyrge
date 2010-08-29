# imports for Pyrge package
__all__ = ['entity', 'gameloop', 'mixin', 'point', 'quadtree', 'spritesheet',
           'text', 'tiledimage', 'tilemap', 'tween', 'tweenfunc', 'util',
           'world']

# convenience imports
from gameloop import Game
Constants = Game.Constants
"""A number of useful constants, such as keycodes, event types, and display flags."""

from point import Point, Vector
