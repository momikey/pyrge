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

__all__ = ['GameLoop', 'Game']

class Globals(object):
    """Useful game-specific values.

    This class holds a number of useful values, such as the time taken
    in the current frame, the currently-pressed keys, and a pointer to the game world.
    It also imports many of the most important pygame objects, so you can create,
    for example, a Rect object by using Game.Rect instead of pygame.Rect, meaning that
    you don't need to use "import pygame" in your own game.

    @cvar Rect: The pygame Rect object.
    @cvar Surface: The pygame Surface object.
    @cvar Draw: The pygame draw module.
    @cvar Sprite: The pygame sprite module.
    @cvar PixelArray: The pygame PixelArray object.
    @cvar Font: The pygame font module.
    @cvar Mask: The pygame mask module.
    @cvar Image: The pygame image module.
    @cvar Transform: The pygame transform module.
    @cvar Constants: The pygame locals module, holding named constants
        representing key codes, event types, display flags, etc.
    @cvar events: A Struct whose attributes point to the pygame events
        of the same name. (Example: event_types.KEYUP == pygame.KEYUP)
    """

    @staticmethod
    def color(name):
        """Create a Pygame Color object from a color name.

           @param name: The name of a color. The valid color names can be found in
           pygame.color.THECOLORS.
        """
        return pygame.Color(name)

    @staticmethod
    def rgb(r, g, b, a=255):
        """Create a Pygame Color object from RGB or RGBA values.

           @param r: The red value of the desired color.
           @param g: The green value of the color.
           @param b: The blue value of the color.
           @param a: The alpha value (transparency) of the color. Default is 255,
               or fully opaque.
        """
        return pygame.Color(r,g,b,a)

    @staticmethod
    def randomcolor():
        """Get a random named color."""
        from random import choice
        from pygame import color
        return choice(color.THECOLORS.values())

    @staticmethod
    def timer(evttype, milliseconds=0):
        """Set an event timer.

           This method will post recurring events of the given type after a
           specified amount of time. This is a repeating timer, so events will
           be posted until the timer is disabled (by calling this method with
           C{milliseconds} set to 0) or the program ends.

           @param evttype: The type of event to post. Event types are listed in
           the L{events} structure.
           @param milliseconds: The time between each event, or 0 to disable
           this timer.
        """
        pygame.time.set_timer(evttype, milliseconds)
           
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

    # Functions for transforming (scaling, rotating, etc.) surfaces
    Transform = pygame.transform

    # Constants is just a synonym for "pygame.locals", which keeps all of the
    # various constants like keycodes, event types, and surface flags
    Constants = pygame.locals

    # helpful structs

    # Event types
    # Right now, we simply copy pygame's events into a Struct.
    # Later, we might use the USEREVENTs to do something.
    events = Struct(
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
    """An event-aware wrapper around the basic pygame loop.

       The GameLoop is the heart of any Pyrge game. It controls and updates
       all the various entities (sprites, text, UI elements, etc.) and does
       everything necessary to link the entities to the underlying Pygame
       system.

       @cvar screen: The main game window, as a Pygame L{Surface}. (If the
           game graphics are scaled, then this is the "pre-scaled" screen.)
       @cvar clock: The game clock, which can also be used to get the
           game's actual framerate.
       @cvar width: The width of the game window or the screen.
       @cvar height: The height of the game window or the screen.
       @cvar scale: The scale factor of the game's graphics.
       @cvar fps: The target (not actual) framerate of the game.
       @cvar paused: While this property is set to True, all game updates
           are stopped.
       @cvar frameTime: The time taken in the last frame, in milliseconds.
           (This is an absolute measure of time, unaffected by the C{timeScale}
           property.)
       @cvar timeScale: A factor that will be multiplief by the C{frameTime}
           value to obtain "game time". The default is 1, meaning that game
           time will pass at the same speed as normal "wall time". Lower numbers
           cause a slowdown or slow-motion effect (e.g., 0.5 is half speed),
           while numbers greater than 1 will cause a speed-up effect (e.g.,
           2 is double speed).
    """

    def __init__(self, width=640, height=480, fps=30, scale=1, initmixer=True):
        """Create a basic game structure.

            @param width: The width of the game window (default 640).
            @param height: The height of the game window (default 480).
            @param fps: The framerate of the game in frames per second
                (default 30).
            @param initmixer: Whether to set up the mixer module for
                high-quality sounds (default True).
        """

        # pre-initialize the mixer module to use 44.1kHz sampling
        # the defaults are:
        # frequency = 22050 (22.050 kHz)
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

        # this is the scale factor from "real time" to "game time"
        self.timeScale = 1

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

        # The current position of the mouse, updated each frame
        Game.mousepos = (0,0)

        # The current state of the mouse buttons, updated each frame
        # Note: This only covers the three main mouse buttons, not the
        # scroll wheel or other buttons.
        Game.mousebuttons = (0,0,0)

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
            if isinstance(etype, basestring):
                es = [_e for _e in self._entities if _e.name == etype]
            else:
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
            raise ValueError, "Invalid event type"

        self._evtHandlers[evttype].append(func)
        return self

    def removeHandler(self, evttype, func):
        """Remove an existing event handler"""
        if not isinstance(evttype, int) or evttype > pygame.NUMEVENTS:
            raise ValueError, "Invalid event type"

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

    def showCursor(self):
        """Shows the system mouse cursor."""
        return pygame.mouse.set_visible(1)

    def hideCursor(self):
        """Hides the system mouse cursor."""
        return pygame.mouse.set_visible(0)

    def __get_bgcolor(self):
        return self.background.get_at((0,0))
    
    def __set_bgcolor(self, color):
        self.background.fill(color)

    backgroundColor = property(__get_bgcolor, __set_bgcolor, \
                               doc="The background color of the game screen.")

    def __get_title(self):
        return pygame.display.get_caption[0]

    def __set_title(self, title):
        pygame.display.set_caption(title)

    title = property(__get_title, __set_title,
                     doc="""The caption that will be shown in the game window's
                     title bar.""")

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
                self.frameTime = self.clock.tick(self.fps)
                Game.elapsed = self.frameTime * self.timeScale
                Game.keys = pygame.key.get_pressed()
                Game.keymods = pygame.key.get_mods()
                Game.mousepos = pygame.mouse.get_pos()
                Game.mousebuttons = pygame.mouse.get_pressed()
        finally:
            pygame.quit()
