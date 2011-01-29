import math, pygame, pygame.locals
from util import Struct
##from pygame.locals import *
from pygame import fastevent as pgevent

import point

__doc__ = """A game object that contains a main loop

On creation, the GameLoop object initializes pygame, creates a screen,
and sets up a clock and a system of "event handlers". Any function can
be registered to handle different pygame events, or as a per-frame "updater"
that can be used to perform the game logic. For scrolling games, use L{World}.

@var Game: An instance of the Globals class that is extended by having various
    important and useful values inserted into it. These are documented as
    instance variables of L{Globals}, with the understanding that Globals is a
    singleton, and Game is the sole instance of the class.
"""

class Globals(object):
    """Useful game-specific values.

    This class holds a number of useful values, such as the time taken
    in the current frame, the currently-pressed keys, and a pointer to the game world.
    It also imports many of the most important pygame objects, so you can create,
    for example, a Rect object by using Game.Rect instead of pygame.Rect, meaning that
    you don't need to use "import pygame" in your own game.

    @cvar Color: The pygame Color object.
    @cvar NamedColors: A dictionary mapping common color names to Color objects.
    @cvar Rect: The pygame Rect object.
    @cvar Surface: The pygame Surface object.
    @cvar Draw: The pygame draw module.
    @cvar Sprite: The pygame sprite module.
    @cvar PixelArray: The pygame PixelArray object.
    @cvar Font: The pygame font module.
    @cvar Mask: The pygame mask module.
    @cvar Image: The pygame image module.
    @cvar Timer: The pygame time module.
    @cvar Transform: The pygame transform module.
    @cvar Constants: The pygame locals module, holding named constants
        representing key codes, event types, display flags, etc.
    @cvar event_types: A Struct whose attributes point to the pygame events
        of the same name. (Example: event_types.KEYUP == pygame.KEYUP)
    """

    # A color object, holding RGBA values
    Color = pygame.Color

    # A dictionary of named colors
    NamedColors = pygame.color.THECOLORS

    # A rectangle object (NOTE: pygame Rects only support integer coordinates)
    Rect = pygame.Rect

    # A surface/image object
    Surface = pygame.Surface

    # Drawing functions
    # TODO: options for regular draw vs. gfxdraw
    Draw = pygame.draw

    # The pygame sprite library
    Sprite = pygame.sprite

    # An array interface to the individual pixels of a surface
    # TODO: maybe detect if NumPy is installed and use SurfArray instead?
    PixelArray = pygame.PixelArray

    # The font module (access to font objects, system fonts, etc.)
    Font = pygame.font

    # A 2D bitmask that can be used for pixel-level collision detection
    Mask = pygame.mask

    # Functions for loading/saving images
    Image = pygame.image

    # Functions for controlling timers
    Timer = pygame.time

    # Functions for transforming (scaling, rotating, etc.) surfaces
    Transform = pygame.transform

    # Constants is just a synonym for "pygame.locals", which keeps all of the
    # various constants like keycodes, event types, and surface flags
    Constants = pygame.locals

    # helpful structs

    # Event types
    # Right now, we simply copy pygame's events into a Struct.
    # Later, we might use the USEREVENTs to do something.
    event_types = Struct(
        QUIT = pygame.QUIT,
        ACTIVEEVENT = pygame.ACTIVEEVENT,
        KEYDOWN = pygame.KEYDOWN,
        KEYUP = pygame.KEYUP,
        MOUSEMOTION = pygame.MOUSEMOTION,
        MOUSEBUTTONUP = pygame.MOUSEBUTTONUP,
        MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN,
        JOYAXISMOTION = pygame.JOYAXISMOTION,
        JOYBALLMOTION = pygame.JOYBALLMOTION,
        JOYHATMOTION = pygame.JOYHATMOTION,
        JOYBUTTONUP = pygame.JOYBUTTONUP,
        JOYBUTTONDOWN = pygame.JOYBUTTONDOWN,
        VIDEORESIZE = pygame.VIDEORESIZE,
        VIDEOEXPOSE = pygame.VIDEOEXPOSE,
        USEREVENT = pygame.USEREVENT)


# Use the Game object to access "global" properties
Game = Globals()

class GameLoop(object):
    """An event-aware wrapper around the basic pygame loop"""

    def __init__(self, width=640, height=480, fps=30, scale=1, initmixer=True):
        """Create a basic game structure. The parameters are:
            width: the width of the game window (default 640)
            height: the height of the game window (default 480)
            fps: the framerate of the game in frames per second (default 30)
            initmixer: whether to set up the mixer module for high-quality samples (default True)"""

        # pre-initialize the mixer module to use 44.1kHz sampling
        # the defaults are:
        # frequency = 22050 (22,050 kHz)
        # size = -16 (16-bit signed integers)
        # channels = 2 (stereo sound)
        # buffer = 4096
        # TODO: make a way to support arbitary mixing values
        if initmixer:
            pygame.mixer.pre_init(frequency=44100)

        # initialize pygame and the fastevent module
        pygame.init()
        pgevent.init()

        # create the main screen (we'll fill this in once the game starts)
        self.screen = None

        # initialize event handlers
        self._evtHandlers = []
        for etype in xrange(pygame.NUMEVENTS):
            self._evtHandlers.append([])

        # initialize "update" list
        self._updates = []

        # this will hold a list of "dirty" rectangles to repaint
        self._rectList = None

        # make a clock to limit CPU usage
        self.clock = pygame.time.Clock()

        # this is the time elapsed in the current frame
        self.frameTime = 0.0

        # copy constructor arguments into properties
        self.width = width
        self.height = height
        self.fps = fps

        # the scale factor of graphics
        # (all graphics will be scaled by this amount in both x and y directions)
        self.scale = scale

        # copy some useful properties into the global structure

        # A pointer to the game world
        Game.world = self

        # A pointer to the game clock (a Clock object)
        Game.clock = self.clock

        # The time spent in the previous frame (used for e.g., velocity)
        Game.elapsed = self.frameTime

        # The game's frames per second setting (not necessarily the _actual_ FPS)
        Game.fps = self.fps

        # The current state of the keyboard, updated each frame
        Game.keys = pygame.key.get_pressed()

        # The current key modifiers (SHIFT, CTRL, etc.), updated each frame
        Game.keymods = pygame.key.get_mods()

        # The default Pyrge font (you can change this in your own classes)
        Game.defaultFont = pygame.font.SysFont('arial', 16)

        # The total "scroll factor", which is applied to every Image to move
        # the screen around. On single-screen games (i.e., those inheriting from
        # GameLoop instead of World), we still have a scroll factor, but it
        # is always set to (0,0).
        Game.scroll = point.Point()

        # The width and height of the game window
        Game.width, Game.height = self.width, self.height

        # A surface representing the background
        self.background = pygame.Surface((self.width, self.height))

        # This is the "display list": all the drawable objects
        self._entities = pygame.sprite.LayeredDirty()
        self.addUpdater(self.update)

        # the game can set this to pause the game logic,
        # while still handling events
        self.paused = False

    def add(self, e):
        """Add an entity (or sequence of entities) to the display list"""
        self._entities.add(e)
        return self

    def remove(self, e):
        """Remove an entity (or sequence of entities) from the display list"""
        self._entities.remove(e)
        return self

    def getEntities(self, etype=None):
        """Get all the entities in the display list, or those of a specific type"""
        if etype is not None:
            es = [_e for _e in self._entities if isinstance(_e, etype)]
        else:
            es = self._entities.sprites()

        return es

    def update(self):
        self._entities.update()
        self._entities.clear(self.screen, self.background)
        self._rectList = self._entities.draw(self.screen)

        if self.scale != 1:
            if self.scale == 2:
                pygame.transform.scale2x(self.screen, self._realscreen)
            else:
                pygame.transform.scale(self.screen, (self.width, self.height), self._realscreen)
            for r in self._rectList:
                r.x *= self.scale
                r.y *= self.scale
                r.w *= self.scale
                r.h *= self.scale

    def addHandler(self, evttype, func):
        """Add a handler for a specific type of event"""
        if not isinstance(evttype, int) or evttype > pygame.NUMEVENTS:
            raise ValueError, "Invalid event type"""

        self._evtHandlers[evttype].append(func)
        return self

    def removeHandler(self, evttype, func):
        """Remove an existing event handler"""
        if not isinstance(evttype, int) or evttype > pygame.NUMEVENTS:
            raise ValueError, "Invalid event type"""

        hl = self._evtHandlers[evttype]

        while func in hl:
            del hl[hl.index(func)]

        return self

    def addUpdater(self, func):
        """Add a per-frame update function (as if we had a "frame" event"""
        self._updates.append(func)
        return self

    def removeUpdater(self, func):
        """Remove an existing per-frame updater"""
        uds = self._updates

        while func in uds:
            del uds[uds.index(func)]

        return self

    def clearBackground(self):
        """Clears the background so that future frames will be drawn on black"""
        self.background = pygame.Surface((self.width, self.height))
        return self

    def loop(self, flags=0):
        """Start the game"""

        # fix scaling
        if self.scale != 1:
            self.screen = pygame.Surface((self.width/self.scale, self.height/self.scale), flags)
            self._realscreen = pygame.display.set_mode((self.width, self.height), flags)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), flags)

        try:
            while True:
                for evt in pgevent.get():
                    for handler in self._evtHandlers[evt.type]:
                        handler(evt)

                    # this goes after the "main" handlers to give them
                    # a chance to clean up
                    if evt.type == pygame.QUIT:
                        raise SystemExit

                if not self.paused:
                    for ud in self._updates:
                        ud()

                pygame.display.update(self._rectList)

                # set game-global values
                Game.elapsed = self.frameTime = self.clock.tick(self.fps)
                Game.keys = pygame.key.get_pressed()
                Game.keymods = pygame.key.get_mods()
        finally:
            pygame.quit()


# Testing starts here

if __name__ == '__main__':
    game = GameLoop()
    game.loop()
