# Import Pyrge
from pyrge import *

# Defina a custom game world, derived from Pyrge's World
# (of course, you can name the class whatever you want)
class TutorialWorld(World):
    
    # The __init__ function is called when we create the world
    def __init__(self):
        
        # We let the parent World create the parts that we don't
        super(TutorialWorld, self).__init__()
        
        # Add some informative text to the screen
        self.add(text.Text('Hello, Pyrge!'))

# Create the World and start the game loop
theGame = TutorialWorld()
theGame.loop()
