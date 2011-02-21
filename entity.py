##import pygame
import point, world, util, tween, tweenfunc

from world import Game
from util import Struct

__doc__ = """Classes that can be used to create game objects

The L{Image} class is the base class for any displayable game object. It holds a
number of properties such as position and size, and contains methods to control
updating, collisions (detection and response), and loading images or pygame Surfaces.

The L{Entity} class is intended to represent "moving" game objects. It is derived
from Image, but also adds functionality to control velocity and acceleration
(both linear and angular).

Finally, the L{Tweener} class is a subclass of Entity that adds support for
interpolations, or tweens, which are defined in the tween module."""

__all__ = ['Image', 'Entity', 'Tweener']

class Image(Game.Sprite.DirtySprite):
    """A class representing any drawable object.

       The L{Image} class is the base class for any drawable object. It can be
       used directly for objects that don't require the use of velocity,
       acceleration, in-game rotation, or L{Tween}s.

       The keyword arguments C{x}, C{y}, C{width}, and C{height} can be used to
       specify an Image's position and size, as can the arguments C{position}
       and C{size}. Also, if an Image is created using two non-keyword arguments,
       those are treated as its x-y position. Four non-keyword arguments are
       understood to be the object's position and size, as the basic four
       parameters C{x}, C{y}, C{width}, and C{height}. Finally, C{w} and C{h},
       as keyword arguments, are synonyms for C{width} and C{height}, respectively.

       @ivar rect: The rectangle representing the object's on-screen drawing area.
           This is also used as the bounding box in collision detection if the
           C{hitbox} property is not present.
       @ivar pixels: A Surface object containing the object's bitmap,
           unaffected by rotations. If the object is animated, this holds the
           bitmap of the current animation frame.
       @ivar angle: The angle, in degrees, that this object is rotated from its
           original heading.
       @ivar collidable: Whether this object should have its collision response
           handlers called on a collision.
       @ivar alive: A living object updates every frame, changes frames if
           animated, and can have collision response.
       @ivar animated: An animated object changes its appearance every frame.
       @ivar currentAnimation: A string containing the name of the currently playing
           animation, or None if the object has only a single, unnamed animation.
       @ivar currentFrame: The number of the frame this object is currently showing.
           If a specific animation is being played, this is the index of the current
           frame in that animation's list.
       @ivar scroll: A L{Point} representing the "scroll factor" of this object.
       @ivar name: A string identifying this image, if needed.
       @ivar filename: The name of an image file to load. (This is equivalent
           to calling the C{load} method after creating this Image.)

       @keyword x: The x position of the object, in pixels.
       @keyword y: The y position of the object, in pixels.
       @keyword width: The width of the object, in pixels.
       @keyword height: The height of the object, in pixels.
       @keyword w: A synonym for C{width}.
       @keyword h: A synonym for C{height}.
       @keyword name: An identifying name for this object.
       """
##    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
    def __init__(self, *args, **kwargs):
        super(Image, self).__init__()

        # handle positional and keyword arguments
        # (position arguments take precedence)
        x = kwargs.get('x',0.0)
        y = kwargs.get('y',0.0)
        w = kwargs.get('w', kwargs.get('width',0.0))
        h = kwargs.get('h', kwargs.get('height',0.0))

        x,y = kwargs.get('position', (x,y))
        w,h = kwargs.get('size', (w,h))

        if len(args) == 2:
            x,y = args
        elif len(args) == 4:
            x,y,w,h = args

        # set up the "pygame sprite" properties
        self._x, self._y, self._w, self._h = x,y,w,h
        self.rect = Game.Rect(x,y,w,h)
        self.rect.center = (self._x, self._y)

        # instead of using self.image directly,
        # we use this, and generate self.image as needed
        self.pixels = Game.Surface((w,h))

        # the angle of rotation of this sprite
        self.angle = 0.0

        # does this sprite participate in collision checks?
        self.collidable = True

        # do we draw this sprite?
        # we don't actually need this, since DirtySprite declares it for us
        # self.visible = True

        # do we need to update this sprite?
        self.alive = True

        # is this sprite animated?
        self.animated = False

        # a list of all the animation frames
        self._frames = []

        # an animation control structure
        # the values will be lists of frames
        self._animations = {}

        # the currently playing animation and frame
        self.currentAnimation = None
        self.currentFrame = 0

        # camera scrolling factors
        self.scroll = point.Point(1.0,1.0)

        # internal state for the image property
        self._imagecache = None

        # Parent/child relationships
        self._children = []
        self._parent = None

        # name of this object
        self.name = kwargs.get('name', '')

        # load an image
        if 'filename' in kwargs:
            self.load(kwargs['filename'])

    ###
    # Image property, holding the surface currently active for this sprite
    ###
    @property
    def image(self):
        """The currently displayed image, as changed by rotation."""
        # use a "cached" image if we can, because rotating is expensive
        if self.dirty > 0:
            img = Game.Transform.rotate(self.pixels, self.angle)
            self._imagecache = img
        else:
            img = self._imagecache
        return img


    ###
    # General update control methods
    ###
    def kill(self):
        """Kills this object by setting its alive property to False
        and removing it from the display."""
        self.alive = False
        self.visible = False
        # pygame Sprites have a kill method that removes them from groups
        super(Image, self).kill()

    def update(self):
        """Updates this sprite's position for each frame."""
        if self.alive and self.animated:
            self.currentFrame += 1

            # animations loop from end back to beginning
            if self.currentAnimation is not None:
                self.currentFrame %= len(self._animations[self.currentAnimation])
                nextframe = self._animations[self.currentAnimation][self.currentFrame]
            else:
                self.currentFrame %= len(self._frames)
                nextframe = self.currentFrame

            self.pixels = self._frames[nextframe]
            self._w, self._h = self.rect.size = self.image.get_size()

            self._recenter()

        # pygame Sprites' update() methods don't do anything by default,
        # but we have this here to allow for mixins
        super(Image, self).update()

    def redraw(self):
        """Force a redraw of this sprite next frame."""
        self.dirty = 1
        self._recenter()

    ###
    # Child methods
    ###
    def addChild(self, child):
        """Adds a child sprite (entity whose position, etc. are relative to parent's).

           @param child: The object that is to be attached to this one.
        """
        self._children.append(child)
        child._parent = self
        child.add(*self.groups())
        child._recenter()

    def removeChild(self, child):
        """Removes a child from this sprite.

           Calling this method with an object that is not one of this object's
           children is the same as calling C{child.kill()}.

           @param child: The child object that is to be removed.
        """
        while child in self._children:
            self._children.remove(child)
        child._parent = None
        child.remove(*self.groups())
        child._recenter()

    @property
    def children(self):
        """A list of this sprite's children."""
        return self._children

    @property
    def parent(self):
        """This sprite's parent entity, or None if it doesn't have one."""
        return self._parent


    ###
    # Image loading methods
    ###

    # load an image
    def load(self, fname):
        """Loads a sprite image into this entity.

           @param fname: The filename of a bitmap to load into this object.
           @return: This object, to allow for chained methods.
        """
        self.pixels = Game.Image.load(fname)
        self.rect.size = self.image.get_size()
        self._w, self._h = self.rect.size
        self._recenter()
        self.dirty = 1          # force a redraw
        return self

    # load an image and rotate it
    def loadRotatedImage(self, fname, angle):
        """Loads a sprite image and rotates it.

           @param fname: The filename of a bitmap to load into this object.
           @param angle: The angle that the bitmap will be rotated before
               it is loaded into this object.
           @return: This object, to allow for chained methods.
        """
        self.pixels = Game.Image.load(fname)
        self.angle = angle
        self.rect.size = self.image.get_size()
        self._w, self._h = self.rect.size
        self._recenter()
        self.dirty = 1          # force a redraw
        return self

    # load an animation frame
    def loadFrame(self, fname, frameid=None):
        """Loads an image into a specific frame.

           @param fname: The filename of a bitmap to load into this object.
           @param frameid: The point in this object's frame list where the
               new frame should be placed. If this is None or out of range
               then it will simply be placed at the end of the list.
           @return: This object, to allow for chained methods.
        """
        frame = Game.Image.load(fname)

        if frameid is None or frameid >= len(self._frames):
            # no frame # or out of range means that we just add it to the end
            self._frames.append(frame)
        else:
            # if the frame # is in range, _replace_ a frame
            self._frames[frameid] = frame

        return self

    # load an animation strip
    def loadAnimation(self, fname, frames=None, horizontal=True):
        """Loads a number of animation frames from a single image.

           This method loads bitmaps from an animation strip. This means
           that the file should contain a sequence of animation frames,
           each the same size, either from left to right or from top to
           bottom, with no intervening gaps.

           @param fname: The filename of an animation strip.
           @param frames: The number of frames in the strip. If not given,
               the method will attempt to guess based on the strip's
               dimensions.
           @param horizontal: The layout of the animation strip. If True
               (the default), frames in the strip are laid out from left
               to right. If False, they run from top to bottom.
           @return: This object, for chaining.
           """
        astrip = Game.Image.load(fname)

        # if we got a specific number of frames, use that,
        # otherwise calculate how many frames we need,
        # assuming that they're all in a row or column
        if frames is not None:
            numFrames = frames
        else:
            if horizontal:
                numFrames = astrip.get_width() / astrip.get_height()
            else:
                numFrames = astrip.get_height() / astrip.get_width()

        if horizontal:
            # frames go from left to right
            framewidth = astrip.get_width() / numFrames
            frameheight = astrip.get_height()
            self._frames += [astrip.subsurface((framewidth*i,0,framewidth,frameheight))\
                             for i in xrange(numFrames)]
        else:
            # frames go from top to bottom
            framewidth = astrip.get_width()
            frameheight = astrip.get_height() / numFrames
            self._frames += [astrip.subsurface((0,frameheight*i,framewidth,frameheight))\
                             for i in xrange(numFrames)]

        return self

    # load a pygame surface
    def loadSurface(self, surf):
        """Loads a pygame surface into the sprite.

           @param surf: A pygame Surface object (including another L{Image}'s
               C{pixels}) that is to be loaded into the C{pixels} field of this
               object.
           @return: This object, for chaining.
        """
        self.pixels = surf
        self.rect = self.image.get_rect()
        self.rect.center = (self._x, self._y)
        self._w, self._h = self.rect.size
        self._recenter()
        self.dirty = 1          # force a redraw
        return self

    ###
    # Animation control
    ###

    def addAnimation(self, name, frames, multiplier=None):
        """Adds an animation using a list of frames.

           An animation can be specified by a list of the image's frames
           that have been loaded by the L{loadFrame} method. If the
           C{multiplier} argument is present, then each entry in the
           animation's frame list will occur that many times. Example:
           C{image.addAnimation('name', [0,1,2], 2)} has the same result
           as calling C{image.addAnimation('name', [0,0,1,1,2,2])}.

           @param name: The name to be used to refer to this animation.
           @param frames: A list of frame numbers that make up this
               animation.
           @param multiplier: Each entry in the list of frames will be
               multiplied by this amount, slowing down the animation.
           @return: This object, for chaining.
        """
        if multiplier is None:
            framelist = frames
        else:
            framelist = [f for f in frames for _ in xrange(int(multiplier))]
            
        if not self._animations.has_key(name):
            self._animations[name] = framelist
        else:
            self._animations[name] += framelist

        return self

    def removeAnimation(self, name):
        """Removes an animation. If the object has no animation by the given
           name, then this method is harmless.

           @param name: The name of the animation to remove.
           @return: This object, for chaining.
        """
        if self._animations.has_key(name):
            del self._animations[name]

        return self

    def play(self, name=None, startFrame=None):
        """Starts an animation (if given a name) or all animation frames.

           If the requested animation is currently playing, it will only be
           restarted if the C{startframe} argument is given. Otherwise,
           there is no effect.

           @param name: The name of the animation to play, or None if all
               the object's animation frames should be used.
           @param startFrame: The index of the frame where animation should start.
           @return: This object, for chaining.
        """
        self.animated = True
        if name == self.currentAnimation:
            # calling an already playing animtion does nothing,
            # unless a specific start frame is requested
            if startFrame is not None:
                self.currentFrame = startFrame
                
        else:
            if name is not None:
                self.currentAnimation = name

            self.currentFrame = startFrame if startFrame is not None else 0

        return self

    def stop(self):
        """Stops animation of this object. This does not remove any animations."""
        self.animated = False
        self.currentAnimation = None
        self.redraw()
        return self

    def showFrame(self, frameid):
        """Shows a specific frame, without animation."""
        
        self.pixels = self._frames[frameid]
        self.currentFrame = frameid
        self._w, self._h = self.rect.size = self.image.get_size()
        self._recenter()
        self.dirty = 1

        return self

    def addFrame(self, frame, frameid=None):
        """Adds a frame to the sprite.

           @note: This method does not update animation frame lists.
           @param frame: A Pygame Surface (such as an L{Image}'s C{pixels}
               property) to use as the animation frame.
           @param frameid: The index number of the frame. If None, then the
               frame will be added to the end of the list.
           @return: The index number of the frame.
        """
        if frameid is None:
            self._frames.append(frame)
        else:
            self._frames.insert(frameid, frame)
        return frameid if frameid is not None else len(self._frames)

    def removeFrame(self, frame):
        """Removes a frame from the sprite.

           @note: This method does not update the frame lists of
               the sprite's animations.
           @param frame: The index number of the frame to remove.
        """
        while frame in self._frames:
            del self._frames[self._frames.index(frame)]

    ###
    # Layer (foreground/background) control
    ###
    def foreground(self):
        """Moves this object to the foreground."""
        for g in self.groups():
            g.move_to_front(self)

    def background(self, scrolling=None):
        """Moves this sprite to the background, optionally setting it to scroll.

           @param scrolling: The new scroll factor for this object.
        """
        for g in self.groups():
            g.move_to_back(self)

        if scrolling:
            self.scroll = point.Point(scrolling)
        else:
            self.scroll = point.Point()

    def getSpritesInLayer(self):
        """Gets a list of all the objects in the same layer as this one."""
        sprites = []
        for g in self.groups():
            sprites += g.get_sprites_from_layer(g.get_layer_of_sprite(self))
        return sprites

    ###
    # Transformations
    ###

    # rotate the sprite outside of updating
    # this method destroys the original sprite image, and resets the angle to 0
    # (this can cause graphical degradation)
    def rotate(self, deg, rotateAnimations=False):
        """Rotates an object without updating it.

           @note: This method sets the entity's angle to 0.
           @param deg: The amount that this object should be rotated, in degrees.
           @param rotateAnimations: Whether to rotate all of the object's
               animation frames.
           @return: This object.
        """
        self.angle = 0.0
        self.pixels = Game.Transform.rotate(self.pixels, deg)
        self.dirty = 1
        self.rect.size = self.image.get_size()
        self.rect.center = (self._x, self._y)
        self._w, self._h = self.rect.size

        if rotateAnimations:
            for idx,f in enumerate(self._frames):
                f = Game.Transform.rotate(f, deg)
                self._frames[idx] = f
        return self

    # scale the sprite
    # this method destroys the original sprite image
    # (this can cause graphical degradation)
    def scale(self, xscl, yscl=None, smooth=True, scaleAnimations=False):
        """Scales an object using either a simple algorithm or a better-looking,
           but more expensive, smooth scale.

           If the C{xscl} parameter is a sequence, then it will be unpacked to
           (xscl, yscl).

           @note: Smooth scaling only works on 24- and 32-bit images. This is a
               limitation of the underlying platform.

           @param xscl: The scale factor in the X direction.
           @param yscl: The scale factor in the Y direction.
           @param smooth: Whether a smooth scale should be used. (Default True)
           @param scaleAnimations: Whether all animation frames should be scaled.
           @return: This object.
        """
        if yscl is None:
            # we got a point or tuple or something
            # TODO: make this so a single number means a uniform scale
            xscl, yscl = xscl[0:2]

        self.dirty = 1

        # use smoothscale if we're asked, or scale2x if we can
        if smooth and self.pixels.get_bitsize() >= 24:
            scalefunc = Game.Transform.smoothscale
        elif xscl == 2.0 and yscl == 2.0:
            # scale2x doesn't use the width and height (since it only scales by 2)
            # so we just use this to throw away the size argument
            scalefunc = lambda surf,size: Game.Transform.scale2x(surf)
        else:
            scalefunc = Game.Transform.scale

        # save the old values, so we can use them below
        oldw, oldh = self.width, self.height
        neww = int((oldw * xscl)+0.5)
        newh = int((oldh * yscl)+0.5)

        self.pixels = scalefunc(self.pixels, (neww, newh))

        self.rect.size = (neww, newh)
        self._w, self._h = self.rect.size

        if scaleAnimations:
            for idx,f in enumerate(self._frames):
                w,h = f.get_size()
                f = scalefunc(f, (int(w*xscl), int(h*yscl)))
                self._frames[idx] = f

        return self

    ###
    # Collision detection
    ###
    def overlap(self, other, checkAlive=False):
        """Tests whether this object and another overlap.

           This method uses a series of collision detection tests. First,
           a bounding-box collision is tested (optionally using user-defined
           C{hitbox} attributes). If the two objects' bounding boxes collide,
           then, if both objects have a C{mask} attribute, a pixel-level
           detection is performed, and its result returned. Otherwise, the
           result of the bounding-box collision is returned.

           @note: An object is not considered to overlap itself.

           @param other: The object to check against this one.
           @param checkAlive: If True, only check for overlap if the other
               object is alive (C{other.alive == True)}.
           @return: Whether the two objects overlap.
        """
        if checkAlive and (not self.alive or not other.alive):
            # if one sprite isn't alive, there's no overlap
            return False
        elif self is other or other is None:
            # test for collision against itself or nothing
            return False

        if isinstance(other, Game.Rect):
            # pygame Rect objects don't have any sprite-like attributes,
            # so we treat them separately
            return self.rect.colliderect(other)
        else:
            # First check a hitbox collision
            if hasattr(self, "hitbox"):
                sbox = self.hitbox
            else:
                sbox = self.rect

            if hasattr(other, "hitbox"):
                obox = other.hitbox
            else:
                obox = other.rect

            boxcollision = sbox.colliderect(obox)

            if not (hasattr(self, "mask") and hasattr(other, "mask")):
                # there's no masks, so bounding boxes are the best we can get
                return boxcollision
            else:
                # we have masks, so we can do pixel-perfect collision,
                # but only if the bounding boxes actually overlap
                if boxcollision:
                    return Game.Sprite.collide_mask(self, other)
                else:
                    return False
                    
    def collide(self, other, kill=False, checkAlive=True):
        """Performs collision detection and calls response methods.

           @param other: The object to check against this one.
           @param kill: If True, calls the kill() method of both objects
               if they collide.
           @param checkAlive: If True, this object is only considered
               to be colliding if the other object is alive.
           @return: The result of calling this object's response methods.
        """
        if self.overlap(other, checkAlive):
            # direction(s) of collision
            _l, _r, _t, _b = False, False, False, False

            # figure out which sides of the sprite are colliding
##            _lrect = Game.Rect(self.rect.left, self.rect.top, 1, self.rect.height-1)
##            _rrect = Game.Rect(self.rect.right-2, self.rect.top, 1, self.rect.height-1)
##            _trect = Game.Rect(self.rect.left, self.rect.top, self.rect.width-1, 1)
##            _brect = Game.Rect(self.rect.left, self.rect.bottom-2, self.rect.width-1, 1)
##
##            _l = _lrect.colliderect(other)
##            _r = _rrect.colliderect(other)
##            _t = _trect.colliderect(other)
##            _b = _brect.colliderect(other)

            # figure out which sides of this object are colliding,
            # based on velocity/position data
            selfvx,selfvy = self.velocity if hasattr(self, 'velocity') else 0,0
            othervx,othervy = other.velocity if hasattr(other, 'velocity') else 0,0
            orect = other.rect if not isinstance(other,Game.Rect) else other

            if selfvx > othervx or (self.x < other.x and self.rect.right > orect.left):
                # this object is approaching from the left
                # so its right edge will be colliding
                _r = True
                
            if selfvx < othervx or (self.x > other.x and self.rect.left < orect.right):
                # this object is approaching from the right
                # so its left edge will be colliding
                _l = True

            if selfvy > othervy or (self.y < other.y and self.rect.bottom > orect.top):
                # this object is approaching from the top
                # so its bottom will be colliding
                _b = True

            if selfvy < othervy or (self.y > other.y and self.rect.top < orect.bottom):
                # this object is approaching from the bottom
                # so its top will be colliding
                _t = True
            

            if kill:
                self.kill()
                other.kill()

            # call this sprite's specific collision response method
            return self.onCollision(other, Struct(left=_l, right=_r, top=_t, bottom=_b))

    def collideRect(self, otherrect):
        """Checks for collision against a rectangle.

           @param otherrect: A pygame Rect to test against this object.
           @return: The result of this object colliding with the given Rect
        """
        return self.collide(otherrect, checkAlive=False)

    def collideList(self, otherlist):
        """Checks for collision against a list of rectangles.

           @note: This is a small wrapper for a pygame method, hence the
               strange return value.

           @param otherlist: A list of pygame Rects that this object may be
               overlapping.
           @return: The indices of each rectangle overlapping this object,
               or -1 if there is no overlap.
        """
        return self.rect.collidelist(otherlist)

    ###
    # Collision response
    # These methods do nothing as they stand, because they are intended to be
    # overridden in derived classes. However, they still call super methods so
    # that we can make mixins that have specific collision responses.
    # We wrap the super calls in a try/except, because pygame's Sprites don't
    # have these methods.
    ###

    def onCollision(self, other, directions=None):
        """Override this method for customized collision response.

           @param other: The object that collided with this object.
           @param directions: A L{Struct} containing the directions where
               collisions were detected (left, right, top, bottom).
           @return: Whether any collision response happened. This can be
               overriden in subclasses.
        """
        # don't do anything unless this sprite participates in collisions
        if self.collidable and self.alive:
            if directions.left: self.hitLeft(other)
            if directions.right: self.hitRight(other)
            if directions.top: self.hitTop(other)
            if directions.bottom: self.hitBottom(other)

            try:
                super(Image, self).onCollision(other, directions)
            except AttributeError:
                pass

            return True
        else:
            return False

    def hitLeft(self, other):
        """Collision response for a hit on the left side of the sprite.

           @param other: The object colliding with this object.
        """
        try:
            super(Image, self).hitLeft(other)
        except AttributeError:
            pass

    def hitRight(self, other):
        """Collision response for a hit on the right side of the sprite.

           @param other: The object colliding with this object.
        """
        try:
            super(Image, self).hitRight(other)
        except AttributeError:
            pass

    def hitTop(self, other):
        """Collision response for a hit on the top of the sprite.

           @param other: The object colliding with this object.
        """
        try:
            super(Image, self).hitTop(other)
        except AttributeError:
            pass

    def hitBottom(self, other):
        """Collision response for a hit on the bottom of the sprite.

           @param other: The object colliding with this object.
        """
        try:
            super(Image, self).hitBottom(other)
        except AttributeError:
            pass

    ###
    # Getters and setters
    # These probably shouldn't be overridden unless you have a really good reason.
    ###

    # any on-screen object will have a position
    def _get_pos(self):
        return point.Vector(self.x, self.y)

    def _set_pos(self, val):
        self._x = val[0]
        self._y = val[1]
        self._recenter()
        self.dirty = 1

    position = property(_get_pos, _set_pos, doc="The X-Y position of this object.")

    # positional properties
    def __get_x(self):
        return self._x

    def __set_x(self, val):
        self._x = val
        self._recenter()
        self.dirty = 1
        return self

    def __get_y(self):
        return self._y

    def __set_y(self, val):
        self._y = val
        self._recenter()
        self.dirty = 1
        return self

    @property
    def left(self):
        return self.x - self.width/2.

    @property
    def right(self):
        return self.x + self.width/2.

    @property
    def top(self):
        return self.y - self.height/2.

    @property
    def bottom(self):
        return self.y + self.height/2.

    # size properties

    def __get_width(self):
        return self._w

    def __set_width(self, val):
        self._w = val
        self.rect.width = val
        self.dirty = 1
        return self

    def __get_height(self):
        return self._h

    def __set_height(self, val):
        self._h = val
        self.rect.height = val
        self.dirty = 1
        return self

    def __get_size(self):
        return point.Vector(self._w, self._h)

    def __set_size(self, val):
        self.width, self.height = val
        self.dirty = 1
        return self

    x = property(__get_x, __set_x, doc="The X coordinate of this object.")
    y = property(__get_y, __set_y, doc="The Y coordinate of this object.")
    width = property(__get_width, __set_width, doc="The width of this object.")
    height = property(__get_height, __set_height, doc="The height of this object.")
    size = property(__get_size, __set_size, doc="The size of this object.")

    @property
    def screenX(self):
        """The on-screen X coordinate of this sprite."""
        x = self.x - Game.scroll.x * self.scroll.x
        if self._parent is not None:
            x += self._parent.x
        return x

    @property
    def screenY(self):
        """The on-screen Y coordinate of this sprite."""
        y = self.y - Game.scroll.y * self.scroll.y
        if self._parent is not None:
            y += self._parent.y
        return y

    def __str__(self):
        """Returns a useful string value for this image."""

        s = "Image %s @ %s %.2f deg." % (self.name,self.position,self.angle)

        return s

    ###
    # Helper methods
    ###
    def _recenter(self):
        """Moves a sprite into its proper screen-based position."""
        self.rect.center = (self.screenX, self.screenY)

class Entity(Image):
    """A movable game sprite.

       An L{Entity} is considered to be an L{Image} that can be affected by
       physical forces. What this means in code terms is that Entities have
       a few extra properties to control their speed and acceleration, both
       in linear and rotational terms. They are computationally more expensive,
       due to the increased logic. Also, although the properties of an Entity
       are described using physical terms, they are not perfectly physically
       accurate, just close enough for a game.

       The Entity class has a total of five physical properties, three of them
       linear and two angular. They are:

           - velocity: The speed of the object in the X and Y directions. This is
               a L{Vector}, and the units are pixels per second (pixels/s).
           - acceleration: The acceleration (change in velocity over time)
               of the object in the X and Y directions. This is a Vector, and the
               units are M{pixels/s**2}.
           - drag: This is a deceleration factor that only affects an object that
               is not accelerating. It is a Vector in pixels per second per frame.
               It is not the same as true physical drag, and the choice of units
               reflects this.
           - angular velocity: The speed of this object's rotation, in degrees per
               second (M{deg/s}).
           - angular acceleration: The accleration of this object's angular velocity,
               in degrees per second per second (M{deg/s**2}).

       Entities also have a couple of extra attributes. First, "fixed" can be set
       to create an Entity that is immune to velocity and acceleration effects.
       Second, the "rotating" flag, as its name suggests, indicates whether an object
       is (or will be) rotating. This flag can be enabled to allow rotating images,
       or disabled (the default) to speed up the rendering of Entities that do not
       rotate.

       Subclasses of Entity can override the L{onMove}, L{onMoveX}, and L{onMoveY}
       "hooks" to create fine-grained motion control and collision detection/response.
 
       The constructor arguments for L{Image} are all usable here.

       @ivar maxVelocity: The maximum velocity of this object, in pixels/second.
           This should be a L{Vector} object containing the maximum velocities
           in the X and Y directions.
       @ivar maxAngularVelocity: The maximum rotational speed of this object,
           in degrees per second.
       @ivar angularAcceleration: The current angular acceleration of the object,
           in degrees per second per second (M{deg/s**2}).
       @ivar rotating: Whether this object will be rotating. Since rotation is
           fairly expensive in terms of CPU, setting this to False is a minor
           optimization.
       @ivar fixed: Whether this object is affected by velocity and acceleration.
    """
##    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
    def __init__(self, *args, **kwargs):
##        super(Entity, self).__init__(x,y,w,h)
        super(Entity, self).__init__(*args, **kwargs)
        
        # The maximum velocity of this object (as a vector) in pixels/second
        self.maxVelocity = None

        # The maximum angular speed of this object in degrees/second
        self.maxAngularVelocity = None

        # motion properties
        # (Be careful setting these directly, since they're used as if they
        # were Vector objects!)
        self._velocity = point.Vector(0,0)
        self._accel = point.Vector(0,0)
        self._drag = point.Vector(0,0)

        # We define angular velocity as a scalar, not a vector, but we still
        # need a getter and setter, so that we can clamp to maxAngularVelocity.
        self._angular = 0.0

        # The angular acceleration of this object in degrees/second^2
        # (we don't really need a property for this, since it's a scalar)
        self.angularAcceleration = 0.0

        # rotating sprites use more CPU, so leave this cleared if this sprite
        # isn't rotating, leaving more time for other rendering
        self.rotating = False

        # does this sprite move?
        self.fixed = False

    # general methods
    def update(self):
        """Updates this sprite for the next frame."""
        if self.alive and not self.fixed:
            # Game.elapsed is in ms, but all our calculations are in seconds
            dt = world.Game.elapsed/1000.0

            if dt > 0.001:
                # linear motion
                if self.drag.x and not self.acceleration.x:
                    # drag is just deceleration when there's no acceleration
                    if abs(self.velocity.x) > abs(self.drag.x):
                        self.velocity.x -= (self.drag.x * util.sign(self.velocity.x))
                    else:
                        self.velocity.x = 0.0
                if self.drag.y and not self.acceleration.y:
                    if abs(self.velocity.y) > abs(self.drag.y):
                        self.velocity.y -= (self.drag.y * util.sign(self.velocity.y))
                    else:
                        self.velocity.y = 0.0

                self.velocity += self.acceleration * dt
                if self.maxVelocity is not None:
                    if self.velocity.x > self.maxVelocity.x:
                        self.velocity.x = self.maxVelocity.x
                    if self.velocity.y > self.maxVelocity.y:
                        self.velocity.y = self.maxVelocity.y

                # move the entity, with hooks after moving by x and y
                self.x += self.velocity.x * dt
                self.onMoveX()
                self.y += self.velocity.y * dt
                self.onMoveY()
                # hook for post-movement code (e.g., collision detection)
                self.onMove()

                # rotation
                # Setting angular velocity or acceleration overrides the
                # 'rotating' property since it is assumed that, by applying
                # angular velocity, you really want an object to rotate.
                if (self.angle and self.rotating) or \
                   self.angularVelocity or self.angularAcceleration:
                    self.angularVelocity += self.angularAcceleration * dt
                    if self.maxAngularVelocity and self.angularVelocity > \
                       self.maxAngularVelocity:
                        self.angularVelocity = self.maxAngularVelocity
                    self.angle += self.angularVelocity * dt
                    self.rect = self.image.get_rect()

        self._recenter()
        super(Entity, self).update()

    # per-frame update hooks
    def onMove(self):
        """A hook for an Entity's post-movement actions."""
        try:
            super(Entity, self).onMove()
        except AttributeError:
            pass

    def onMoveX(self):
        """A hook for actions taken after movement along the x axis."""
        try:
            super(Entity, self).onMoveX()
        except AttributeError:
            pass

    def onMoveY(self):
        """A hook for actions taken after movement along the y axis."""
        try:
            super(Entity, self).onMoveY()
        except AttributeError:
            pass

    # defining motion properties
    def _get_velocity(self):
        return self._velocity

    def _set_velocity(self, val):
        if self.maxVelocity:
            _vx, _vy = val

            if abs(self.maxVelocity.x) < abs(_vx):
                _vx = self.maxVelocity.x * util.sign(_vx)
            if abs(self.maxVelocity.y) < abs(_vy):
                _vy = self.maxVelocity.y * util.sign(_vy)

            self._velocity = point.Vector(_vx, _vy)
        else:
            self._velocity = point.Vector(val)
        self.dirty = 1

    velocity = property(_get_velocity, _set_velocity,
                             doc='The velocity L{Vector} of this object.')

    def _get_accel(self):
        return self._accel

    def _set_accel(self, val):
        self._accel = point.Vector(val)
        self.dirty = 1

    acceleration = property(_get_accel, _set_accel,
                             doc='The acceleration L{Vector} of this object.')

    def _get_drag(self):
        return self._drag

    def _set_drag(self, val):
        self._drag = point.Vector(val)

    drag = property(_get_drag, _set_drag, doc='The drag L{Vector} of this object.')

    def _get_angularvelocity(self):
        return self._angular

    def _set_angularvelocity(self, val):
        if self.maxAngularVelocity and abs(self.maxAngularVelocity) < abs(val):
            self._angular = self.maxAngularVelocity * util.sign(val)
        else:
            self._angular = val
        self.dirty = 1

    angularVelocity = property(_get_angularvelocity, _set_angularvelocity,
                             doc='The angular velocity of this object')

    # angular acceleration doesn't need a property

    def __str__(self):
        """Returns a string representation of this object"""
        s = "Entity %s @ %s, %d deg., V=%s, A=%s, aV=%s, aA=%d" % \
            (self.name, self.position, self.angle, self.velocity, self.acceleration, \
             self.angularVelocity, self.angularAcceleration)

        return s

class Tweener(Entity):
    """An object that can use interpolations.

       A L{Tweener} is a special type of L{Entity} that is made to hold
       and use a number of L{Tween} objects. These can be used, for example,
       to give the appearance of natural motion or transformation.

       When a L{Tween} is added to an object, it is given a type. This type
       determines what happens when the Tween's interpolator is complete. The
       different types given using the following class constants:

           - ONESHOT: The Tween should be deleted after it is complete.
           - LOOP: The Tween should be restarted on completion.
           - PERSIST: After the Tween completes, it is stopped, but not deleted.

       A Tweener is created with the same arguments as its superclasses.

       @ivar tweens: A list of tuples, each of the form (tw, ty), where C{tw}
           is a L{Tween} object, and C{ty} is the type of completion action,
           as above.
    """

    # tween control types
    ONESHOT = 0
    LOOP = 1
    PERSIST = 2

##    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
##        super(Tweener, self).__init__(x,y,w,h)
    def __init__(self, *args, **kwargs):
        super(Tweener, self).__init__(*args, **kwargs)

        # this will contain a sequence of tuples (tween,type),
        # where "type" can be ONESHOT (where the tween is removed after running),,
        # LOOP (where the tween starts over after completion),
        # or PERSIST (the tween can stop, but is not removed)
        self.tweens = []

    def addTween(self, tw, t=0, startnow=False):
        """Adds a tween to this object's update list.

           @param tw: The Tween that will be added.
           @param t: The type of Tween (Tweener.ONESHOT, LOOP, or PERSIST).
           @param startnow: Whether this Tween should be started immediately.
           @return: This object.
        """
        self.tweens.append((tw, t))
        if startnow: tw.start()

        return self
    
    def removeTween(self, tw):
        """Removes a tween from this object's update list. Removing a tween
           that this object doesn't have is harmless.

           @param tw: The Tween that should be removed.
           @return: This object.
        """
        self.tweens = [t for t in self.tweens if t[0] != tw]
        return self

    def update(self):
        """Updates the objects's position, motion, and any tweens that it contains
           for the next frame."""
        for tt in self.tweens[:]:
            tw, tp = tt     # 'tween' and 'type'

            if tw.percent == 1.0 and tw.running == False:
                # this tween is done, so do whatever we need to do
                if tp == self.ONESHOT:
                    self.removeTween(tw)
                elif tp == self.LOOP:
                    tw.reset()
                    tw.start()

            else:
                tw.update()

        super(Tweener, self).update()
