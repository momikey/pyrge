import gameloop, point
from gameloop import Game
from util import Struct

__doc__ = """A scrollable game world with camera control

The L{world} module defines a single class. L{World} is a subclass
of L{GameLoop}, which creates a simple, single-screen game. L{World} adds
scrolling (including parallax scrolling) and camera control (i.e., an object,
usually the player, can be designated as the "focus", so the game engine always
tries to center the display on that object)."""

class World(gameloop.GameLoop):
    """A game world that can be larger than the screen size.

       @ivar camera: The current position in the game world of the camera.
       @ivar focus: The object currently being followed by the camera.

       @keyword width: The width of the screen.
       @keyword height: The height of the screen.
       @keyword fps: The speed (frames per second) that the game should run.
    """
    def __init__(self, width=640, height=480, fps=60, scale=1):
        super(World, self).__init__(width, height, fps, scale)

        # camera position (this is a basis position for all drawing)
        self.camera = point.Point(0, 0)
        Game.scroll = Game.camera = self.camera

        # which object is the focus of the camera
        self.focus = None

        # how far away the camera (center of the screen) should be from the focus
        self._focusLead = None

        # how fast the camera should "catch up" to the focus
        self._followSpeed = 1.0

        # the boundaries of camera movement
        self._followMin, self._followMax = None, None

        # SDL uses 16-bit coordinates for drawing, so these are the maximum bounds
        # Range of a 16-bit integer = -32,678 to +32,767 (or -2**15 to 2**15 - 1)
        self._bounds = Game.Rect(-(1 << 15), (1 << 15)-1, (1 << 16)-1, (1 << 16)-1)

    # set a specific object as the camera's focus
    def follow(self, o, lead=None):
        """Sets the camera to follow a specific object.

           @param o: The object to follow.
           @param lead: How far the camera should be ahead of the focus.
           @type lead: L{Point}
        """
        self.focus = o
        if lead:
            self.focusLead = point.Point(lead)
        self._doCameraFollow()

    def followBounds(self, followMin=None, followMax=None):
        """Sets the range in which the camera is allowed to move.

           If both parameters, C{followMin} and C{followMax}, are None,
           then the game world's extents are set to be the same as the screen.
           
           @param followMin: The top-left corner of the game world.
           @param followMax: The bottom-right corner of the game world.
        """
        if followMin is None:
            followMin = point.Vector(0,0)
        if followMax is None:
            followMax = point.Vector(self.width, self.height)

        # The minimum follow value is the top-left corner of the game world,
        # and the maximum is the bottom-right. We can just use followMin as is,
        # but we have to adjust followMax to take into account the size of the
        # screen. We do this _after_ setting the world boundaries, though,
        # because it saves typing and it might be slightly faster.
        self._followMin = point.Vector(followMin)
        self._followMax = point.Vector(followMax)
        self._bounds = Game.Rect(followMin, self._followMax - self._followMin)
        self._followMax -= (self.width, self.height)
        self._doCameraFollow()

    def followSpeed(self, spd=1.0):
        """Sets the camera's "catch-up" speed."""
        self._followSpeed = spd

    def getScreenRect(self):
        """Returns a Rect object containing the bounds of the screen."""
        if self.screen is not None:
            return self.screen.get_rect()
        else:
            return Game.Rect(0,0,self.width, self.height)

    def getScreenCenter(self):
        """Returns a Point object representing the center of the screen."""
        return point.Point(self.getScreenRect().center)

    def getBounds(self):
        """Gets a Rect object containing the camera boundaries."""
        return self._bounds

    def getOutOfBounds(self, border=10):
        """Gets a Struct containing Rects that are just outside the camera boundaries."""
        bounds = self.getBounds()
        oobleft = Game.Rect(bounds.left-border, bounds.top-border,\
                              border,bounds.height+border*2)
        oobright = Game.Rect(bounds.right, bounds.top-border,\
                              border,bounds.height+border*2)
        oobtop = Game.Rect(bounds.left-border, bounds.top-border,\
                              bounds.width+border*2, border)
        oobbottom = Game.Rect(bounds.left-border, bounds.bottom,\
                              bounds.width+border*2, border)
        l = [r.move(-Game.scroll.x, -Game.scroll.y) for r in \
             oobleft, oobright, oobtop, oobbottom]

        return Struct(left=l[0], right=l[1], top=l[2], bottom=l[3])

    def update(self):
        """Updates the world for each frame."""
        if self.focus:
            Game.camera = self.camera = self.focus.position
            self._doCameraFollow()
        super(World, self).update()

    def _doCameraFollow(self):
        """Helper function to move the camera to follow an object."""
        if self.focus is not None:
            _target = point.Vector(self.focus.position - self.getScreenCenter())

            if self._focusLead:
                _target += self.velocity * self._focusLead

            Game.scroll += (_target - Game.scroll) * self._followSpeed * Game.elapsed / 1000.0

            # _followMin/_followMax are the camera boundaries
            if self._followMin is not None:
                if Game.scroll.x < self._followMin.x:
                    Game.scroll.x = self._followMin.x
                if Game.scroll.y < self._followMin.y:
                    Game.scroll.y = self._followMin.y
            if self._followMax is not None:
                if Game.scroll.x > self._followMax.x:
                    Game.scroll.x = self._followMax.x
                if Game.scroll.y > self._followMax.y:
                    Game.scroll.y = self._followMax.y

if __name__ == '__main__':
    w = World()

    assert w.getScreenRect() == Game.Rect(0,0,w.width,w.height), "Screen rect"
    assert w.getScreenCenter() == (w.width/2, w.height/2), "Screen center"
    w.followBounds()
    assert w.getBounds() == Game.Rect(0,0,w.width,w.height), "Bounds rect"
