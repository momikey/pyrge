import math

__doc__ = """2D points and vectors

The Point class is made to be lightweight, while the Vector class supports
the full range of typical vector operations."""

__all__ = ['Point', 'Vector', 'length', 'distance', 'rotate']

class Point(object):
    """A lightweight 2D point.

       A L{Point} is a 2D point of the form (x,y). It can be initialized
       by two coordinates, another Point object, or any sequence.
    """
    def __init__(self, x=0.0, y=0.0):
        # This way is about 3x faster than the exception version below,
        # according to timeit(). It's not as flexible, though.
        if isinstance(x, (tuple,list)):
            # Try converting a tuple
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

##        try:
##            self.x = x.x
##            self.y = x.y
##        except AttributeError:
##            try:
##                self.x = x[0]
##                self.y = x[1]
##            except TypeError:
##                self.x = x
##                self.y = y
##            except IndexError:
##                try:
##                    self.x = self.y = x[0]
##                except IndexError:
##                    raise ValueError, "Invalid sequence argument"
##            except:
##                raise ValueError, "Invalid argument"

##        self.x = float(self.x)
##        self.y = float(self.y)

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

class Vector(Point):
    """A full-featured 2D vector.

       A L{Vector} is much the same as a L{Point}, but it adds a full range
       of mathematical operations (addition, subtraction, etc.), as well as
       the usual vector operations such as length, dot product, etc.
    """
    def __init__(self, x=0.0, y=0.0):
        super(Vector, self).__init__(x, y)

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

# Testing starts here
if __name__ == '__main__':
    p1 = Point()
    p2 = Point(1)
    p3 = Point(2.0)
    p4 = Point(-1.5, 3.5)
    p5 = p4
    p6 = tuple(p3)
    p7 = Point((1,2))
    p8 = Point(p6)

    assert p1.x == 0 and p1.y == 0, "Zero-arg constructor: Point() != (0,0)"
    assert p2.x == 1 and p2.y == 0, "One-arg constructor: Point(1) != (1,0)"
    assert p3.x == 2 and p3.y == 0, "Floating-point argument: Point(2.0) != (2,0)"
    assert p4.x == -1.5 and p4.y == 3.5, "Two-arg constructor: Point(-1.5, 3.5) != (-1.5, 3.5)"
    assert p5.x == -1.5 and p5.y == 3.5 and p4 == p5, \
        "Equality test: Point(-1.5, 3.5) != Point(-1.5, 3.5)"
    assert p6 == (2,0), "Conversion to tuple: Point(2,0) != (2,0)"
    assert p7.x == 1 and p7.y == 2, "Initialization from tuple: Point((1,2)) != (1,2)"
    assert p8.x == p3.x and p8.y == p3.y, \
        "Initialization from tuple: Point((2,0)) != (2,0)"

    v1 = Vector(2,3)
    v2 = Vector(-1,-1.5)
    v3 = (1,2)
    v4 = Vector((0,))

    assert v1.x == 2 and v1.y == 3, "Simple constructor failed"
    assert v2.x == -1 and v2.y == -1.5, "Floating-point constructor failed"
    assert v4.x == 0 and v4.y == 0, "Tuple constructor failed"

    assert v1 + v2 == Vector(1,1.5), "Addition operation failed"
    assert v2 + v3 == Vector(0,0.5), "Addition of tuple failed"
    assert v1 - v2 == Vector(3,4.5), "Subtraction operation failed"
    assert v2 - v3 == Vector(-2,-3.5), "Subtraction of tuple failed"

    v4 += v3
    assert v4 == (1,2), "In-place addition failed"
    assert (10,10) + v4 == (11,12), "Reverse addition failed"

    assert v1 * 5 == (10,15), "Multiplication operation failed"
    assert v2 * -3.3 == (-1 * -3.3, -1.5 * -3.3), "Float multiplication failed"
    assert v3 * v4 == (1,4), "Vector scaling failed"

    assert v1.length() == math.sqrt(2**2+3**2), "Length method failed"
    assert v1.dot(v2) == v1.x*v2.x + v1.y*v2.y == -6.5, "Dot product failed"
    assert v1.perpendicular() == (-3,2), "Perpendicular method failed"

    assert length(v1) == v1.length(), "Global length function failed"
    assert distance(v1, Vector(1,1)) == math.sqrt(5), "Global distance function failed"
    assert Vector(1,1).angle() == 45, "Angle method failed"
    assert abs(Vector(1,1).rotate(-45).length() - Vector(1,1).length()) < 1e-10, \
        "Rotate method failed"
    assert abs(Vector(1,0).rotate(45).normalized().length() - 1) < 1e-10, \
        "Normalized method failed"

    assert bool(Vector(1,0)) and bool(Vector(3.1,4.5)) \
        and not bool(Vector(0.0, -0.0)), "Nonzero method failed"

##    # speed test (this is no longer needed)
##    import timeit
##    print "Point speed test:", timeit.Timer('p = Point()',
##        'from __main__ import Point').timeit()
##    print "Vector speed test:", timeit.Timer('p = Vector()',
##                       'from __main__ import Vector').timeit()
##    print "Trig test 1:", timeit.Timer('a = Vector().angle()',
##        'from __main__ import Vector').timeit()
##    print "Trig test 2:", timeit.Timer('v = v.rotate(5)',
##        'from __main__ import Vector\nv = Vector(1,0)').timeit()
