import entity
import point
from gameloop import Game, GameLoop
##import pygame

__doc__ = """A simple sprite sheet"""

__all__ = ['SpriteSheet']

class SpriteSheet(object):
    """A simple spritesheet that can be created from an existing surface or
       loaded from an image file. 

       The C{xborder} and C{yborder} arguments default to zero, and the C{colorkey}
       defaults to None. The C{borderleft} and C{bordertop} values default to False.

       @note: All of the keyword arguments are transferred into the object as
           instance variables with the same names

       @ivar sheet: A bitmap of the SpriteSheet.

       @param surface: A filename or pygame Surface object.
       @keyword spritewidth: The width of a single sprite on the sheet.
       @keyword spriteheight: The height of a single sprite on the sheet.
       @keyword xborder: The number of pixels between two sprites in the X direction.
       @keyword yborder: The number of pixels between two sprites in the Y direction.
       @keyword colorkey: A Color object representing the "transparent" color of the sheet.
       @keyword borderleft: Whether the sheet has a border on the left side.
       @keyword bordertop: Whether the sheet has a border on the top.
    """

    def __init__(self, surface, **kwargs):
        if isinstance(surface, basestring):
            # if we got a filename
            self.sheet = Game.Image.load(surface)
        else:
            # if it's not a filename, then it's a surface
            # TODO: error if it's neither
            self.sheet = surface

        # Width and height of the whole sheet
        # Since we're not inheriting from Image, these aren't filled in for us
        self.width, self.height = self.sheet.get_size()

        # Get these before the width and height
        self.xborder = kwargs.get('xborder',0)
        self.yborder = kwargs.get('yborder',0)

        # TODO: allow specifying number of columns/rows instead of sprite width/height
        self.spritewidth = kwargs['spritewidth']
        self.columns = (self.width + self.xborder)/(self.spritewidth + self.xborder)
        self.spriteheight = kwargs['spriteheight']
        self.rows = (self.height + self.yborder)/(self.spriteheight + self.yborder)

        # Use a colorkey if we get one, or use the default (magenta)
        self.colorkey = kwargs.get('colorkey', (255,255,0))
        self.sheet.set_colorkey(self.colorkey)

        # The border on the left and top sides
        # (We don't need to worry about whether there are borders on the right or bottom)
        self.borderleft = kwargs.get('borderleft', False)
        self.bordertop = kwargs.get('bordertop', False)

    def spriteAt(self, xpos, ypos=None):
        """Get the sprite at a given location on the sheet"""

        # Check for a single integer index, and recalculate
        if ypos is None:
            ypos, xpos = divmod(xpos, self.columns)

        if xpos > self.columns or ypos > self.rows or \
           xpos < 0 or ypos < 0:
            raise ValueError, "Invalid spritesheet coordinate"

        spritex = xpos * (self.spritewidth + self.xborder)
        if self.borderleft:
            spritex += self.xborder

        spritey = ypos * (self.spriteheight + self.yborder)
        if self.bordertop:
            spritey += self.yborder

        return self.sheet.subsurface((spritex,spritey,self.spritewidth,self.spriteheight))
