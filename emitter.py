import pyrge, random

__doc__="""A simple particle emitter

An L{Emitter} can be used to create particle emission effects like explosions,
eruptions, fountains, and so on. It works by creating a number of particles of
a particular class, with random (but constrained) velocities. Each particle has
its own lifetime, and is killed when that time expires.
"""

__all__ = ['Emitter']

class Emitter(pyrge.entity.Image):
    """A particle emitter.

       Emitters create explosion-like effects by releasing multiple small
       sprites (particles) at varying speeds and in varying directions. The
       speed, direction, and duration, and their ranges can all be controlled by
       using the Emitter's properties.

       @param particleType: A class (note: not an instance of that class) to be
       used as the base type of particle. Multiple instances of this class will
       be created and emitted when L{emit} is called.
    """
    def __init__(self, particleType, x=0.0, y=0.0):
        super(Emitter, self).__init__(x,y,0,0)

        self.particleType = particleType
        self._duration = 1.0        # seconds
        self._durationrange = 1.0   # seconds
        self._velocity = 100.0      # pixels/sec
        self._velocityrange = 100.0 # pixels/sec
        self._emitAngle = 0.0       # degrees
        self._spread = 0.0          # degrees

    def emit(self, number):
        """Emit a given number of particles, using the speed, direction, etc.
           given by this object's properties.

           @param number: The number of particles to emit. The Emitter will
           release exactly this many particles. If this value is too high,
           slowdown will occur, but "too high" varies on different systems.
        """
        for i in xrange(number):
            self._doEmit()

    def _doEmit(self, x=0.0, y=0.0):
        p = self.particleType(position=(x,y))
        p.duration = random.gauss(self.duration, self.durationRange/4.)
        a = pyrge.util.vectorFromAngle(random.gauss(self.emitAngle, self.spread/4.))
        p.velocity = random.gauss(self.velocity,self.velocity/4.) * a
        self.addChild(p)

    def update(self):
        """Update the Emitter for each frame, particularly to control the
           lifetimes of the child particles."""
        super(Emitter, self).update()
        for c in self.children:
            c.duration -= pyrge.Game.elapsed / 1000.0
            if c.duration <= 0.0:
                self.removeChild(c)

    # Emitter properties (these are used to control the particles themselves)
    def __get_duration(self):
        return self._duration

    def __set_duration(self, seconds):
        self._duration = seconds

    duration = property(__get_duration, __set_duration, \
                        doc = "The average lifetime of a particle, in seconds.")

    def __get_durationRange(self):
        return self._durationRange

    def __set_durationRange(self, seconds):
        self._durationRange = seconds

    durationRange = property(__get_durationRange, __set_durationRange, \
                             doc = """The amount that a particle's lifetime can differ
                             from the average, in seconds.""")

    # Note that Emitter velocity is not the same as Entity velocity!
    def __get_velocity(self):
        return self._velocity

    def __set_velocity(self, pixps):
        self._velocity = pixps

    velocity = property(__get_velocity, __set_velocity, \
                        doc = "The average speed of a particle (in pixels/sec)")

    def __get_velocityRange(self):
        return self._velocityRange

    def __set_velocityRange(self, pixps):
        self._velocityRange = pixps

    velocityRange = property(__get_velocityRange, __set_velocityRange, \
                             doc = """The amount that a particle's speed can differ
                             from the average (in pixels/sec).""")

    # This can't be called "angle" because Images already have that property
    def __get_emitAngle(self):
        return self._emitAngle

    def __set_emitAngle(self, degrees):
        self._emitAngle = degrees

    emitAngle = property(__get_emitAngle, __set_emitAngle, \
                     doc="The angle (in degrees) that the emission will be aimed")

    def __get_spread(self):
        return self._spread

    def __set_spread(self, degrees):
        self._spread = degrees

    spread = property(__get_spread, __set_spread, \
                      doc="The amount of variation in the emitter's angle (in degrees)")

if __name__ == '__main__':
    from gameloop import Game
    
    class Box(pyrge.entity.Entity):
        def __init__(self, *args, **kwargs):
            kwargs['size'] = (2,2)
            super (Box, self).__init__(*args, **kwargs)

            self.pixels.fill(Game.randomcolor())
            self.dirty = 1

    w = pyrge.world.World(fps=30)
    e = Emitter(Box,320,240)
    e.duration = 1.0
    e.durationRange = 0.3
    e.velocity = 80.0
    e.velocityRange = 30.0
    e.emitAngle = 0
    e.spread = 180.0
    w.add(e)
    w.addHandler(pyrge.Game.event_types.KEYDOWN, \
        lambda evt: e.emit(12) if evt.key == pyrge.Constants.K_SPACE else None)
    w.loop()
