# Import Pyrge
from pyrge import *

# Defina a custom game world, derived from Pyrge's World
# (of course, you can name the class whatever you want)
class TutorialWorld(World):
    
    # The __init__ function is called when we create the world
    def __init__(self):
        
        # We let the parent World create the parts that we don't
        super(TutorialWorld, self).__init__()

        # Add our customized object to the world
        self.add(TutorialImage())

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
        
# Create the World and start the game loop
theGame = TutorialWorld()
theGame.loop()
