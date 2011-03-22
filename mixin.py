from gameloop import Game
from entity import Image

__doc__ = """Mixin classes for game objects

The L{mixin} module defines a few commonly used traits that many
sprites share, but are not common enough to warrant inclusion in the basic
sprite classes of the L{entity} module. These mixin classes can be used with
multiple inheritance to add these effects to a sprite.

When using mixins, they should be listed first in an object's superclasses.
"""

__all__ = ['SpriteMixin', 'Bouncer', 'Wrapper', 'Clickable',
           'Fader', 'YOrdered', 'ArrowKeys']

class SpriteMixin(Game.Sprite.DirtySprite):
    """The base class for all mixins. You shouldn't make instances of this class;
       you should use a subclass instead."""

    def update(self):
        """SpriteMixin is intended to be an abstract class, so its update method
           does nothing."""
        # don't do anything, just delegate to super
        super(SpriteMixin, self).update()

class Bouncer(SpriteMixin):
    """A mixin that makes a sprite "bounce" off the boundaries of the world."""

    def update(self):
        """Update this sprite for the next frame of animation. If the sprite
           is overlapping any edge of the screen, then its velocity in that direction
           (x for left and right, y for top and bottom) is reversed."""
        # get the "out of bounds" areas of the world, out to a suitable length
        oob = Game.world.getOutOfBounds(self.velocity.length())

        # "bounce" by reversing the x and/or y components of the velocity
        if self.overlap(oob.left) or self.overlap(oob.right):
            self.velocity.x *= -1
        if self.overlap(oob.top) or self.overlap(oob.bottom):
            self.velocity.y *= -1

        super(Bouncer, self).update()

class Wrapper(SpriteMixin):
    """A mixin that makes a sprite "wrap" when it reaches the edge of the world."""

    def update(self):
        """Update the sprite for the next frame of animation. If the sprite is
           positioned off the screen, it will "wrap around" to the opposite side."""
        # All we do here is get the extents of the world. If we're beyond one
        # of the four edges, we move to the opposite edge.
        # However, this doesn't compensate for _how far_ we're past the edge.

        bounds = Game.world.getBounds()
        if self.x < bounds.left:
            self.x = bounds.right
        elif self.x > bounds.right:
            self.x = bounds.left

        if self.y < bounds.top:
            self.y = bounds.bottom
        elif self.y > bounds.bottom:
            self.y = bounds.top

        super(Wrapper, self).update()

class Stopper(SpriteMixin):
    """A mixin that makes a sprite stop moving when it reaches the edge of the
       game world."""

    def update(self):
        bounds = Game.world.getBounds()
        if self.left < bounds.left:
            self.x = bounds.left + self.width/2.
            if hasattr(self, "velocity"):
                self.velocity.x = self.acceleration.x = 0
        elif self.right > bounds.right:
            self.x = bounds.right - self.width/2.
            if hasattr(self, "velocity"):
                self.velocity.x = self.acceleration.x = 0

        if self.top < bounds.top:
            self.y = bounds.top + self.height/2.
            if hasattr(self, "velocity"):
                self.velocity.y = self.acceleration.y = 0
        elif self.bottom > bounds.bottom:
            self.y = bounds.bottom - self.height/2.
            if hasattr(self, "velocity"):
                self.velocity.y = self.acceleration.y = 0

        super(Stopper, self).update()
            
class Clickable(SpriteMixin):
    """A mixin that detects when a sprite is clicked and responds accordingly.

       @note: When subclassing L{Clickable}, you must override the C{click}
           method with your own sprite's behavior.
    """
    def __init__(self, *args, **kwargs):
        super(Clickable, self).__init__(*args, **kwargs)

        # register a "click" handler
        # we use the MOUSEBUTTONDOWN event, since pygame has no MOUSECLICK event
        Game.world.addHandler(Game.events.MOUSEBUTTONDOWN, self.__isClicked)

    def __isClicked(self, event):
        """Helper method to determine whether this object was clicked.

        @todo: This should take into account layers, and whether there is
               another object on top of this one.
        """
        pos = (event.pos[0] / Game.world.scale, event.pos[1] / Game.world.scale)
        if (hasattr(self, "hitbox") and self.hitbox.collidepoint(pos)) or \
           self.rect.collidepoint(pos) and self.alive:
            self.click(event)

    def click(self, event):
        """Handler for mouse clicks. Your subclass must override this method
           if you want it to do anything.

           @param event: The pygame Event object that prompted this action.
        """
        pass

    def kill(self):
        """Kills the sprite, removing it from the display and setting its
           C{alive} property to False."""
        # Clean up after ourselves
        Game.world.removeHandler(Game.events.MOUSEBUTTONDOWN, self.__isClicked)
        super(Clickable, self).kill()

class ArrowKeys(SpriteMixin):
    """A mixin that does user-defined actions when arrow keys are held down.

       @note: ArrowKeys should come before Image (or any of its subclasses) in
           a sprite's base class list.

       @keyword keys: A sequence containing the keycodes to use for up, left,
           down, and right, in order, or a string of 4 letters, such as "WASD".
    """
    def __init__(self, *args, **kwargs):
        self.__arrowkeys = kwargs.get('keys',
                                      (Game.Constants.K_UP, Game.Constants.K_LEFT,
                                       Game.Constants.K_DOWN, Game.Constants.K_RIGHT))

        if isinstance(self.__arrowkeys, basestring):
            self.__arrowkeys = [getattr(Game.Constants, "K_" + l)
                                for l in self.__arrowkeys]

        super(ArrowKeys, self).__init__(*args, **kwargs)
        
    def update(self):
        if Game.keys[self.__arrowkeys[0]]:
            self.upArrow()
        elif Game.keys[self.__arrowkeys[2]]:
            self.downArrow()

        if Game.keys[self.__arrowkeys[1]]:
            self.leftArrow()
        elif Game.keys[self.__arrowkeys[3]]:
            self.rightArrow()

        super(ArrowKeys, self).update()

    def upArrow(self):
        """Override this to control behavior when the "up" key is held"""
        pass

    def downArrow(self):
        """Override this to control behavior when the "down" key is held"""
        pass

    def leftArrow(self):
        """Override this to control behavior when the "left" key is held"""
        pass

    def rightArrow(self):
        """Override this to control behavior when the "right" key is held"""
        pass

class Fader(SpriteMixin):
    """A mixin that makes a sprite fade in brightness over a set period of time.

       @note: Fader should come before Image (or any of its subclasses) in
           a sprite's base class list.
       
       @todo: Add a Fader mixin that can be used with particle emitters, because
           the duration property in this class clashes with the one that
           Emitter adds to its children.

       @keyword duration: The time the sprite should take to fade from full
           brightness to zero, in seconds. At the end of this time, the sprite
           will be destroyed by calling its C{kill} method.
    """
    def __init__(self, *args, **kwargs):
        super(Fader, self).__init__(*args, **kwargs)

        self.duration = kwargs.get('duration', 0)
        self._fullDuration = self.duration
        self.pixels.set_colorkey((0,0,0))

    def update(self):
        """Update the sprite for the next frame. If the C{duration} property is
           0 or less, then the sprite's "lifetime" is up, and it will be killed."""
        self.duration -= pyrge.Game.elapsed / 1000.
        
        if self.duration <= 0:
            self.kill()
        else:
            alpha = int((self.duration / self._fullDuration) * 256) - 1
            self.pixels.set_alpha(alpha)
            super(Fader, self).update()

class YOrdered(SpriteMixin):
    """A mixin that changes a sprite's render layer based on its vertical
       screen position.

       A Y-ordered sprite changes its layer (i.e., drawing order) when it
       changes its Y-coordinate. This can be used to create a perspective
       effect like that seen in old RPGs.
    """
    def update(self):
        for g in self.groups():
            if isinstance(g, Game.Sprite.LayeredDirty) and \
               abs(g.get_layer_of_sprite(self) - self.y) > 1:
                # Only the "LayeredDirty" type groups, like Stages and
                # the World's display list, need to be affected. Also,
                # we only change the sprite's layer if it's actually
                # different enough to be noticed.
                g.change_layer(self, self.y)
                
        super(YOrdered, self).update()
