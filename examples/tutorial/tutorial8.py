# Import Pyrge
from pyrge import *

# Defina a custom game world, derived from Pyrge's World
# (of course, you can name the class whatever you want)
class TutorialWorld(World):
    
    # The __init__ function is called when we create the world
    def __init__(self):
        
        # We let the parent World create the parts that we don't
        super(TutorialWorld, self).__init__()

        # Create a custom sprite object (described below)
        sprite = TutorialImage()

        # Add our customized sprite to the world
        self.add(sprite)

        # Set the boundaries of the game world's "camera".
        # When this is called without any arguments, like here,
        # the boundaries are set to be the same as the screen.
        self.followBounds()

    # We took out the update() override, because our new strategy
    # no longer needs it. Since the bullets will wrap around the
    # edges of the screen, they'll never really be off-screen, so
    # that way wouldn't work anymore, anyway.

# Define a customized sprite
# Instead of Image alone, we're now making a sprite that is derived
# from both Image and the Wrapper mixin. (Yes, it's multiple
# inheritance. No, it's not as bad as they say.) Inheriting from the
# mixin means that we don't have to write any code to make the
# sprite wrap when it reaches the edge of the screen.
class TutorialImage(Image, mixin.Wrapper):

    # Again, __init__ is called when the object is created
    def __init__(self):
        
        # We'll let the base Image do most of the work
        # (100,100) means that the center of the image is at
        # that position on the screen. The default is (0,0),
        # the upper-left corner. If we use that, then most of
        # the picture will be off the screen!
        super(TutorialImage, self).__init__(100,100)

        # We can use an animation strip to load frames of animation.
        # In this case, the strip contains 8 frames, 2 for each
        # direction of movement.
        self.loadAnimation('animatedsprite.bmp')

        # To add an animation, we need two things: a name (which
        # can be any string you want) and a list of frames. In our
        # animation strip, the frames run from 0 to 7, left to right.
        # These 2-frame animations look too fast on a 60 FPS game,
        # though, so we can use a multiplier to slow them down.
        # Saying that the "walkleft" animation is frames [0,4] with
        # a multiplier of 8 is the same thing as writing the frame list
        # as [0,0,0,0,0,0,0,0,4,4,4,4,4,4,4,4], but much shorter.
        self.addAnimation('walkleft', [0,4], 8)
        self.addAnimation('walkright', [1,5], 8)
        self.addAnimation('walkup', [2,6], 8)
        self.addAnimation('walkdown', [3,7], 8)

        # With animated sprites, we need a starting point. The
        # showFrame method doesn't animate anything; it just moves the
        # animation to a single frame.
        self.showFrame(0)

        # Sprites can request that one of their own methods become
        # an event handler.
        Game.world.addHandler(Game.events.KEYDOWN, self.fire)

    # Every object is updated each frame, and this is where it happens.
    def update(self):
        # This is a temporary variable that we'll use to
        # decide which animation to play
        anim = None

        # Game.keys is a list of all the different keys that
        # Pyrge can use. It's hard to remember the codes for
        # all of them, so each code has a name (thanks to
        # the Pygame and SDL folks). The names are stored in
        # Constants, and they all look like K_(something):
        # K_a, K_4, K_COMMA, K_UP, K_F6, etc.

        # We check for each arrow key, and move our sprite
        # depending on which keys are pressed.
        # X moves to the left and right, Y is up and down.
        # With each keypress, we set our state variable to
        # the appropriate animation
        if Game.keys[Constants.K_LEFT]:
            anim = 'walkleft'
            self.x -= 2
        if Game.keys[Constants.K_RIGHT]:
            anim = 'walkright'
            self.x += 2
        if Game.keys[Constants.K_UP]:
            anim = 'walkup'
            self.y -= 2
        if Game.keys[Constants.K_DOWN]:
            anim = 'walkdown'
            self.y += 2

        # If one of the arrow keys was pressed, then that
        # means that we're moving. When we're moving, we'll
        # play one of the animations we set above, depending
        # on which direction we're going. No keypresses means
        # that we stopped, so we have to stop the animation.
        if anim is not None:
            self.play(anim)
        else:
            self.stop()
        
        # Now let the parent Image do the hard stuff.
        super(TutorialImage, self).update()

    # Fire a bullet whenever the space bar is pressed.
    # (Remember that event handlers always have to accept the
    # event, even if they don't do anything with it.)
    def fire(self, event):
        if event.key == Constants.K_SPACE:
            # All we have to do is create a new bullet, and
            # add it to the world.
            Game.world.add(TutorialBullet(self))

# This is our bullet class. It's an Entity instead of an Image,
# meaning that it has a few extra properties. The main one that's
# important right now is "velocity". Again, we're also using the
# Wrapper mixin.
class TutorialBullet(Entity, mixin.Wrapper):
    def __init__(self, parent):
        # The usual superclass initialization. The idea is that
        # a sprite that wants to fire a bullet will pass itself
        # as the parent argument, so the bullet will appear at
        # the same position.
        super(TutorialBullet, self).__init__(position=parent.position, size=(4,4))

        # The bullet will go in the appropriate direction at
        # 180 pixels per second. In real-world terms, an Entity's
        # velocity can be whatever scale you want.
        v = 180

        # We can use Pygame's drawing functions to make a circle
        # on the sprite's canvas (the "pixels" property). Here,
        # we're making yellow bullets that are circles of radius 2.
        Game.Draw.circle(self.pixels, Game.color('yellow'), (2,2), 2)

        # We'll set the sprite's velocity based on which direction
        # the parent sprite (our player) is pointing. 
        if parent.currentAnimation == 'walkleft' or parent.currentAnimation is None:
            self.velocity = Vector(-v,0)
        elif parent.currentAnimation == 'walkright':
            self.velocity = Vector(v,0)
        elif parent.currentAnimation == 'walkup':
            self.velocity = Vector(0,-v)
        elif parent.currentAnimation == 'walkdown':
            self.velocity = Vector(0,v)

        # Instead of killing the bullet when it goes off the screen
        # (Wrapper prevents that from happening) we give each bullet
        # a "lifetime" property. Here, it's 1200 milliseconds, or
        # 1.2 seconds. Plenty of time for the bullet to cover a bit
        # of ground, without making it easy to hit something across
        # the screen.
        self.lifetime = 1200

    # We're adding game logic (the lifetime property), so now we
    # have to make an update() method.
    def update(self):
        # You should know what this does by now. :p
        super(TutorialBullet, self).update()

        # Game.elapsed holds the number of milliseconds that have
        # passed since the last frame. (That's why we set the
        # lifetime property to be in milliseconds instead of seconds.)
        self.lifetime -= Game.elapsed

        # Now, if the bullet's life has run out, then it must die.
        if self.lifetime <= 0:
            self.kill()
            
# Create the World and start the game loop
theGame = TutorialWorld()
theGame.loop()
