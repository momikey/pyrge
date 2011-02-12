import math, point

__doc__ = """Useful utility classes and functions for working with Pyrge."""

__all__ = ['Struct', 'sign', 'vectorFromAngle']

class Struct(object):
    """A simple struct class that can be initialized by keyword arguments."""
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
        return 'Struct(%s)' % ', '.join(args)

def sign(x):
    """Returns a value based on the sign of a number
       (positive=1, negative=-1, zero=0)."""
    if x == 0.0:
        return x
    elif x > 0.0:
        return 1.0
    else:
        return -1.0

def vectorFromAngle(theta):
    """Returns a vector pointing away from the origin at a specific angle
       (in degrees). This is essentially the same as converting the polar
       coordinates (1,theta) to rectangular.

       @param theta: The angle in degrees.
    """
    rad = math.radians(theta)
    # polar-to-rectangular is (r cos \theta, r sin \theta)
    # pygame's y-coordinate grows downward, hence the minus sign
    return point.Vector(math.cos(rad), -math.sin(rad))

def flatten(seq):
    """Flattens a sequence, changing the elements of any subsequences into
       "top-level" elements. Example: The list [[a,b[,c,[d,e,f]] flattens
       into [a,b,c,d,e,f]

       @param seq: The sequence (list, tuple, etc.) to flatten.
       
       @return: A flattened list as a generator.
    """
    for item in seq:
        try:
            # sublists
            for subitem in item:
                yield subitem
        except TypeError:
            # regular element
            yield item
