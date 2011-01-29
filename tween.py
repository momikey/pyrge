import world
import tweenfunc

__doc__ = """Controllable interpolations

The L{tween} module contains the L{Tween} class, which allows
time-based interpolation (tweening) of values such as coordinates, vectors,
and colors. An interpolation function can be given, or one of a number of stock
interpolators (contained in the "tweenfunc" module) can be used.

One or more L{Tween} objects can be attached to the L{Tweener} type of sprite
to create a wider variety of effects than possible with only properties defined
in the L{entity} classes."""

__all__ = ['Tween']

class Tween(object):
    """A customizable tween.

       @ivar startval: The starting value.
       @ivar endval: The ending value.
       @ivar duration: The number of seconds this Tween should run.
       @ivar function: The interpolation function used by the Tween.
       @ivar complete: The function that will be run on completion.
       @ivar value: The current value.
       @ivar percent: The distance "through" the Tween so far, from 0 to 1.
       @ivar running: Whether this Tween is currently active.

       @keyword start: The starting value.
       @keyword end: The ending value.
       @keyword duration: The length of time this Tween should run, in seconds.
       @keyword function: An interpolation function. This can be any function
           that takes three arguments (start, end, percent) and returns an object
           of the same type as C{start} and C{end}.
       @keyword complete: A function that will be called on completion.
    """
    def __init__(self, start=0.0, end=1.0, duration=1.0, function=None, complete=None):
        # the starting value for this tween
        self.startval = start

        # the ending value for this tween
        self.endval = end

        # how long this tween should run, in seconds
        self.duration = duration

        if function is not None:
            # the interpolation function that this tween should use
            self.function = function
        else:
            # if no function, just use a basic lerp
            self.function = lambda s,e,d: s + (e-s)*d

        # an optional function to call when this tween is complete
        if complete is not None:
            self.doOnComplete = complete
        else:
            self.doOnComplete = None

        # the current value of the tween
        self.value = self.startval

        # how far through the interpolation we are, from 0 to 1
        self.percent = 0.0

        # whether this tween is currently running
        self.running = False

    def start(self):
        """Starts the tween's internal timer."""
        if not self.running and self.percent < 1.0:
            self.running = True

    def stop(self):
        """Stops the tween from updating."""
        if self.running:
            self.running = False

    def reset(self):
        """Resets the tween to its initial state."""
        self.running = False
        self.percent = 0.0
        self.value = self.startval

    def update(self):
        """Updates the Tween's values.

           @note: This should be called once per frame.

           @return: The value of the Tween.
        """
        timeThisFrame = world.Game.elapsed
        if self.running:
            self.percent += float(timeThisFrame) / (self.duration*1000.0)

            self.value = self.function(self.startval, self.endval, self.percent)

            if self.percent >= 1.0:
                self.value = self.endval
                self.percent = 1.0
                self.running = False
                self.onComplete()

        return self.value

    def onComplete(self):
        """Override this method to handle tasks after the tween is complete."""
        if self.doOnComplete is not None:
            self.doOnComplete(self.value)

    def __str__(self):
        if isinstance(self.startval, float) and isinstance(self.endval, float):
            return "%.3f:%.3f@%.3f=%.3f" % (self.startval,self.endval,self.percent,self.value)
        else:
            return "%s:%s@%.3f=%s" % (self.startval, self.endval,self.percent,self.value)

# Testing
if __name__ == '__main__':
    w = world.World(fps=30)

    from point import Vector
    tween = Tween(start=Vector(0,0), end=Vector(3,4), duration=1.0)
    w.addUpdater(tween.start)
    w.addUpdater(tween.update)

    def printTween():
        print tween, "\t", tween.value.length()

    w.addUpdater(printTween)

    w.loop()
    print tween, "\t", tween.value.length()
