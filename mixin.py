from gameloop import Game

__doc__ = """Mixin classes for game objects

The L{mixin} module defines a few commonly used traits that many
sprites share, but are not common enough to warrant inclusion in the basic
sprite classes of the L{entity} module. These mixin classes can be used with
multiple inheritance to add these effects to a sprite."""

__all__ = ['SpriteMixin', 'Bouncer', 'Wrapper', 'Clickable']

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
        if (hasattr(self, "hitbox") and self.hitbox.collidepoint(event.pos)) or \
           self.rect.collidepoint(event.pos) and self.alive:
            self.click(event)

    def click(self, event):
        """Handler for mouse clicks. Your subclass must override this method
           if you want it to do anything.

           @param event: The pygame Event object that prompted this action.
        """
        pass
