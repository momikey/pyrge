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

# Define a customized sprite
# In this case, we're making an Image, Pyrge's most basic sprite class.
# The more advanced classes include Entity, which has simple physics, and
# Tweener, which can use tweens for motion or animation.
class TutorialImage(Image):

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
        
# Create the World and start the game loop
theGame = TutorialWorld()
theGame.loop()
