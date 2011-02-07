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

        # We want our sprite's moving function to run whenever
        # a mouse button is pressed, so we use an event handler.
        # All we have to do is tell Pyrge which event we want
        # to handle (here, the "mouse button down" event), and
        # what we want to do when that event happens.
        self.addHandler(Game.events.MOUSEBUTTONDOWN, sprite.onClick)

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

        # Pyrge is based on Pygame; hopefully they won't mind
        # if we use their logo until we get one of our own!
        self.load('pygame_icon.bmp')

    # Every object is updated each frame, and this is where it happens.
    def update(self):
        # Game.keys is a list of all the different keys that
        # Pyrge can use. It's hard to remember the codes for
        # all of them, so each code has a name (thanks to
        # the Pygame and SDL folks). The names are stored in
        # Constants, and they all look like K_(something):
        # K_a, K_4, K_COMMA, K_UP, K_F6, etc.

        # We check for each arrow key, and move our sprite
        # depending on which keys are pressed.
        # X moves to the left and right, Y is up and down.
        if Game.keys[Constants.K_LEFT]:
            self.x -= 2
        if Game.keys[Constants.K_RIGHT]:
            self.x += 2
        if Game.keys[Constants.K_UP]:
            self.y -= 2
        if Game.keys[Constants.K_DOWN]:
            self.y += 2

        # Now let the parent Image do the hard stuff.
        super(TutorialImage, self).update()

    # This is an event handling function. You can tell because it
    # takes two parameters: self, which is the object itself, and
    # event, an object that Pyrge (really, Pygame) sends out when
    # something happens, like a mouse button being clicked.
    def onClick(self, event):
        
        # Set our sprite's position to wherever the mouse
        # button was clicked.
        self.position = event.pos

        
# Create the World and start the game loop
theGame = TutorialWorld()
theGame.loop()
