import world, entity, point
from gameloop import Game

import random

__doc__ = """Special effects

This module contains special effects, camera tricks, and anything else that
doesn't really have a place in the rest of Pyrge."""

__all__ = ['Effect','Quake']

class Effect(object):
    """A generic camera effect. This does nothing by itself, but gives the
       developer a framework for creating effects that fit into Pyrge's
       display system.

       In most subclasses, you should override the C{__init__}, C{start},
       C{stop}, and C{effect} methods, with a C{super} call in all but C{effect}.

       @ivar duration: The time that this effect will run. This is updated
           each frame, and the effect is automatically stopped when it reaches
           zero.
       @ivar running: Whether the effect is currently active. Subclasses must
           update this on their own, but the most common definition is
           C{self.duration > 0}.
    """
    def __init__(self):
        super(Effect, self).__init__()
        self.duration = 0

    def start(self):
        """Start the effect. Subclasses can (and should) override this method,
           with their own code before the C{super} call."""
        Game.world.addUpdater(self.update)

    def stop(self):
        """Stop the effect. This method is used to clean up anything done by
           the effect, such as resetting the camera. It also forces a redraw
           for any game objects that are set to scroll. (Non-scrolling objects
           are considered immune to effects.) Subclasses should override this
           method with their own code before C{super}."""
        self.duration = 0
        Game.world.removeUpdater(self.update)
        for e in Game.world.getEntities():
            if e.scroll:
                # force a recenter and redraw
                e._recenter()
                e.dirty = 1

    def update(self):
        """Update the effect for the next frame. This is essentially the same
           type of method as used by game objects, but without the code to
           update the object's appearance."""
        if self.running:
            # duration is in seconds, Game.elapsed is milliseconds
            self.duration -= Game.elapsed / 1000.

            if self.duration > 0:
                self.effect()
            else:
                self.stop()

            for e in Game.world.getEntities():
                if e.scroll:
                    # force a recenter and redraw
                    e._recenter()
                    e.dirty = 1

    def effect(self):
        """The code for the actual effect. Subclasses must override this method
           if they want to do anything. (Note that there is no C{super} call.)"""
        pass

    @property
    def running(self):
        """Whether this effect is active and being updated. Subclasses can
           override this property to customize the definition of "running"."""
        return (self.duration > 0)

class Quake(Effect):
    """A camera effect that simulates a shaking screen by randomly moving the
       World camera.

       Quake objects are persistent: they are not destroyed after they expire.
       This means that, except for special cases, you often only need a single
       object.
    """
    def __init__(self):
        super(Quake, self).__init__()
        self.intensity = 0
        self.__origscroll = Game.scroll
        
    def start(self, intensity=0.05, duration=1.0):
        """Start the camera shaking effect

           @param intensity: The amount of shaking, or the maximum amount of
               camera displacement, relative to the screen size. Higher values
               cause a more jarring effect, and values less than about 0.002 will
               have no effect. The best values are between 0.005 and 0.1.
           @param duration: The length of time (in seconds) that the shaking
               effect will last.
        """
        # save the original scroll value, so that we can reset the camera
        # back to the way it was
        self.__origscroll = Game.scroll
        self.intensity = intensity
        self.duration = duration
        super(Quake, self).start()

    def stop(self):
        """Stop the shaking effect."""
        # reset the camera to its pre-effect position
        Game.scroll = self.__origscroll
        super(Quake, self).stop()

    def effect(self):
        """Update the effect by moving sprites around. Non-scrolling sprites
           (such as overlays) are unaffected, since it is assumed that those
           sprites are meant to be stationary.
        """
        # the "quake" effect is simply moving the camera by a random amount
        # each frame, the intensity value is just how big the random numbers
        # are relative to the screen size
        rx = random.uniform(-self.intensity*Game.width,self.intensity*Game.width)
        ry = random.uniform(-self.intensity*Game.height,self.intensity*Game.height)
        Game.scroll = self.__origscroll + point.Vector(rx,ry)
