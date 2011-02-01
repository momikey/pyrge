import math

__doc__ = """Interpolation functions

The L{tweenfunc} module is a helper module to L{tween},
containing a set of predefined interpolation functions (tweens).These functions
can be used as interpolators for the Tween class. They all use the same basic
interface, taking three arguments (start, end, percent) representing the starting point,
the ending point, and the distance "through" the function, from 0.0 to 1.0.

In addition, this module also defines a few "adapter" classes. These are intended
to allow the use of interpolation with sequences, colors, and arbitrary objects."""

__all__ = ['Linear', 'Smoothstep', 'QuadraticEaseIn', 'QuadraticEaseOut',
           'Sine', 'Cosine', 'TweenFunction', 'ListTween', 'ColorTween']

def Linear(start, end, percent):
    """A linear interpolator (lerp)."""
    # most functions will eventually call this, since it is
    # the basic parametric equation common to any form of interpolation
    return start + (end - start) * percent

# just a synonym
Lerp = Linear
"""A linear interpolator (lerp)."""

def Smoothstep(start, end, percent):
    """A smooth interpolation following the equation M{y=3x^2-2x^2}."""
    v = 3*percent**2 - 2*percent**3
    return Linear(start, end, v)

def QuadraticEaseIn(start, end, percent):
    """A quadratic interpolation accelerating from 0."""
    v = percent*percent
    return Linear(start, end, v)

def QuadraticEaseOut(start, end, percent):
    """A quadratic interpolation decelerating to 0."""
    v = 2*percent - percent**2
    return Linear(start, end, v)

def Sine(start, end, percent):
    """An interpolation following a sine curve."""
    v = math.sin(percent*math.pi/2)
    return Linear(start, end, v)

def Cosine(start, end, percent):
    """An interpolation following a cosine curve."""
    v = math.cos(percent*math.pi/2)
    return Linear(start, end, v)

# Adapters for non-tweenable types
class TweenFunction(object):
    """A base class for adapters for types (such as colors)
       that don't support tweening operations.

       @param function: The interpolation function that this object will use.
    """
    def __init__(self, function):
        self.function = function

    def __call__(self, start, end, percent):
        return self.function(start, end, percent)

class ListTween(TweenFunction):
    """An adapter that can use tweening functions with lists or other
       Python sequences.

       @param function: The interpolation function that this object will use.
    """
    def __init__(self, function):
        super(ListTween, self).__init__(function)

    def __call__(self, start, end, percent):
        values = []
        for s,e in zip(start, end):
            values.append(self.function(s,e,percent))
        return values

class ColorTween(ListTween):
    """An adapter to allow the use of tweening functions with pygame
       Color objects.

       @param function: The interpolation function that this object will use.
       @param useAlpha: If True, the alpha value of the Color will be interpolated.
           Otherwise, it will be set to 255 (fully opaque).
    """
    from pygame import color
    def __init__(self, function, useAlpha=False):
        super(ColorTween, self).__init__(function)
        self.useAlpha = useAlpha

    def __call__(self, start, end, percent):
        r = int(self.function(start.r, end.r, percent))
        g = int(self.function(start.g, end.g, percent))
        b = int(self.function(start.b, end.b, percent))
        if self.useAlpha:
            a = int(self.function(start.a, end.a, percent))
        else:
            a = 255

        return color.Color(r,g,b,a)
