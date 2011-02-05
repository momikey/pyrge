import world, entity, point
from gameloop import Game

import random

__doc__ = """Special effects

This module contains special effects, camera tricks, and anything else that
doesn't really have a place in the rest of Pyrge."""

__all__ = ['Quake']

class Quake(object):
    """A camera effect that simulates a shaking screen by randomly moving the
       World camera.

       Quake objects are persistent: they are not destroyed after they expire.
       This means that, except for special cases, you often only need a single
       object.
    """
    def __init__(self):
        super(Quake, self).__init__()
        self.intensity = self.duration = 0
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
        self.__origscroll = Game.scroll
        self.intensity = intensity
        self.duration = duration
        Game.world.addUpdater(self.update)

    def stop(self):
        """Stop the shaking effect early."""
        self.duration = 0
        Game.scroll = self.__origscroll
        Game.world.removeUpdater(self.update)
        for e in Game.world.getEntities():
            if e.scroll:
                e._recenter()
                e.dirty = 1

##        self.kill()

    def update(self):
        """Update the effect by moving sprites around. Non-scrolling sprites
           (such as overlays) are unaffected, since it is assumed that those
           sprites are meant to be stationary.
        """
        if self.running:
            self.duration -= Game.elapsed / 1000.0

            if self.duration > 0:
                rx = random.uniform(-self.intensity*Game.width,self.intensity*Game.width)
                ry = random.uniform(-self.intensity*Game.height,self.intensity*Game.height)
                Game.scroll = self.__origscroll + point.Vector(rx,ry)
            else:
                self.stop()

            for e in Game.world.getEntities():
                if e.scroll:
                    e._recenter()
                    e.dirty = 1

    @property
    def running(self):
        return (self.duration > 0)

