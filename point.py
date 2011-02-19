import math

__doc__ = """2D points and vectors

The Point class is made to be lightweight, while the Vector class supports
the full range of typical vector operations. This module also includes
functions for common 2D geometric operations."""

__all__ = ['Point', 'Vector', 'length', 'distance', 'rotate']

class Point(object):
    """A lightweight 2D point.

       A L{Point} is a 2D point of the form (x,y). It can be initialized
       by two coordinates, another Point object, or any sequence.
    """
    def __init__(self, x=0.0, y=0.0):
##        if isinstance(x, (tuple,list)):
        if hasattr(x, '__getitem__'):
            # Try converting a sequence
            if len(x) == 2:
                self.x, self.y = x
            elif len(x) == 1:
                self.x = x[0]
                self.y = y
            else:
                raise ValueError, "Invalid sequence argument"
        elif isinstance(x, Point):
            # Try converting a Point or Vector
            self.x = x.x
            self.y = x.y
        else:
            # Use numbers directly
            self.x = x
            self.y = y

    def __str__(self):
        return str((self.x, self.y))

    def __repr__(self):
        return "Point(%f,%f)" % (self.x, self.y)

    def __len__(self):
        # TODO: implement 3D points/vectors?
        return 2

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __nonzero__(self):
        return (self.x != 0.0 or self.y != 0.0)

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __ne__(self, other):
        return not self == other

# An origin point, so we don't have to create an extra one all the time.
ZeroPoint = Point()

class Vector(Point):
    """A full-featured 2D vector.

       A L{Vector} is much the same as a L{Point}, but it adds a full range
       of mathematical operations (addition, subtraction, etc.), as well as
       the usual vector operations such as length, dot product, etc.
    """
    def __init__(self, x=0.0, y=0.0):
        super(Vector, self).__init__(x, y)
        self.x = float(self.x)
        self.y = float(self.y)

    def length(self):
        """Vector length.

           @return: The length of this Vector, M{sqrt(x^2+y^2)}.
        """
        # libm already has a 2D vector length function
        return math.hypot(self.x, self.y)

    def normalized(self):
        """Normalized (unit length) vector.

           @return: A Vector pointing the same direction as this Vector,
               but whose length is 1.
        """
        l = self.length()
        return Vector(self.x/l, self.y/l)

    def dot(self, other):
        """Dot product of two vectors.

           @return: The 2D dot product (sum of componentwise multiplication).
        """
        return (self.x * other.x) + (self.y * other.y)

    def perpendicular(self):
        """2D perpendicular vector.

           @return: The Vector perpendicular to this one, i.e., this vector
           rotated 90 deg. counterclockwise.
        """
        return Vector(-self.y, self.x)

    def angle(self):
        """The angle in which this vector is pointing, in degrees."""
        return math.degrees(math.atan2(self.y, self.x))

    def rotate(self, deg=0):
        """Rotates this vector around the origin.

           @param deg: The number of degrees to rotate this Vector
               (counterclockwise).
           @return: A new Vector representing this Vector rotated around the origin.
        """
        r = math.radians(deg)
        v = Vector()
        v.x = self.x * math.cos(r) - self.y * math.sin(r)
        v.y = self.x * math.sin(r) + self.y * math.cos(r)
        return v

##    def closestPoint(self, pt, start=ZeroPoint):
##        """Finds the closest point along this vector to the given point.
##
##           The vector is treated as a line segment with a starting point
##           equal to the C{start} parameter.
##
##           @param pt: The Point that will be tested.
##           @param start: The starting Point of this Vector.
##           @return: The nearest point to the given point that is along
##               this Vector.
##        """
##        w = Vector(pt.x-start.x,pt.y-start.y)
##        proj = w.dot(self)
##        if proj <= 0:
##            return start
##        else:
##            vsq = self.dot(self)
##            if proj >= vsq:
##                return self + start
##            else:
##                return start + (proj/vsq)*self
##
##    def distanceToPoint(self, pt, start=ZeroPoint):
##        return distance(pt, self.closestPoint(pt,Vector(start)))

    def __add__(self, other):
        try:
            o = Point(other)
            v = Vector(self.x + o.x, self.y + o.y)
        except:
            return NotImplemented
        return v

    def __sub__(self, other):
        try:
            o = Point(other)
            v = Vector(self.x - o.x, self.y - o.y)
        except:
            return NotImplemented
        return v

    def __mul__(self, other):
        v = Vector()
        try:
            # uniform scaling
            v.x = self.x * float(other)
            v.y = self.y * float(other)
        except TypeError:
            # non-uniform scaling
            v.x = self.x * other[0]
            v.y = self.y * other[1]
        return v

    def __div__(self, other):
        # we can only divide by numbers, not other vectors
        return Vector(self.x/float(other), self.y/float(other))

    def __iadd__(self, other):
        try:
            o = Point(other)
            self.x += o.x
            self.y += o.y
        except:
            return NotImplemented
        return self

    def __isub__(self, other):
        try:
            o = Point(other)
            self.x -= o.x
            self.y -= o.y
        except:
            return NotImplemented
        return self

    def __imul__(self, other):
        try:
            # uniform scaling
            self.x *= float(other)
            self.y *= float(other)
        except TypeError:
            # non-uniform scaling
            self.x *= other[0]
            self.y *= other[1]
        return self

    def __idiv__(self, other):
        self.x /= float(other)
        self.y /= float(other)
        return self

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):
        return self * other

    def __rdiv__(self, other):
        return self / other

    def __neg__(self):
        return Vector(-self.x, -self.y)

# Vector functions
def length(v):
    """The length of a vector.

       This is the same as C{v.length()}, but it can also be used with any
       object that can be converted to a Vector, such as a L{Point} or tuple.
       
       @param v: A Vector.
       @return: The length of Vector C{v}.
    """
    return Vector(v).length()

def distance(p1, p2):
    """The distance between two points.

       @return: The distance between Vectors C{p1} and C{p2}.
    """
    return length(p2-p1)

def rotate(v, theta):
    """Rotates a vector counterclockwise around the origin.

       This is the same as calling C{v.rotate(theta)}, but it can be used with
       any object that can be converted to a Vector.
       
       @param v: The Vector to rotate.
       @param theta: The number of degrees to rotate this Vector.
       @return: A new Vector representing C{vec} rotated around the origin
        by C{theta} degrees.
    """
    return Vector(v).rotate(theta)
