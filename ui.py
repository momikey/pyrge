import mixin, text
from entity import Image
from gameloop import Game

__doc__ = """Non-game user interface elements.

This module contains objects that can be used as user interface elements in
a game.
"""

__all__ = ['Button', 'ToggleButton', 'Console']

class Button(Image, mixin.Clickable):
    """A simple button class that can call a function when it is clicked.
       The button can contain text and/or graphics. It is also used as a
       base class for other button-like interface elements.

       @keyword click: The funtion to call when the button is clicked.
       @keyword label: The text label to display on the button.
       @keyword graphic: A graphic (or filename of a graphic) to display
           on the button.
       @keyword bgColor: The background color of the button.
       @keyword border: The width of the border, in pixels.
       @keyword labelColor: The color of the button's label text.
       @keyword borderColor: The color of the button's border.

       @ivar text: A L{Text} object containing the button's label.
       @ivar graphic: An L{Image} to be used as a button's label or icon.
       @ivar bgColor: The color of the button's background (read-only).
       @ivar border: The amount of border space between the edge of the
           button and the text/graphic.
       @ivar borderColor: The color of the border, if the button has one.
    """
    def __init__(self, *args, **kwargs):
        # set a click handler, if we get one
        if 'click' in kwargs:
            self.click = kwargs['click']

        # text label
        # TODO: add more options?
        self.text = text.Text(kwargs.get('label',''),
                              color=kwargs.get('labelColor',Game.color('black')),
                              )

        # graphics
        self.graphic = kwargs.get('graphic',None)
        if isinstance(self.graphic, basestring):
            self.graphic = Image().load(self.graphic)

        # background
        self.bgColor = kwargs.get('bgColor', 'gray70')
        if isinstance(self.bgColor, basestring):
            self.bgColor = Game.color(self.bgColor)

        # border
        self.border = kwargs.get('border',8)

        # border color
        self.borderColor = kwargs.get('borderColor', None)

        # if we don't get a size, figure one out
        # TODO: if we get a graphic and text, make it the bigger of the two
        if 'size' not in kwargs:
            if self.graphic is not None:
                kwargs['size'] = self.graphic.size
            elif self.text is not None:
                kwargs['size'] = self.text.size
            else:
                kwargs['size'] = (0,0)

        kwargs['size'] += (self.border,self.border)

        super(Button, self).__init__(*args, **kwargs)

        self.pixels = Game.Surface((self.width,self.height),Game.Constants.SRCALPHA)
        self.pixels.fill(self.bgColor)
        self._drawBorder()


    def _drawBorder(self):
        # We don't want the whole border drawn in, because it might make
        # the text hard to read, so we'll only use about half of it for the
        # colored border.
        if self.borderColor is not None and self.border > 0:
            Game.Draw.rect(self.pixels, self.borderColor,
                           self.pixels.get_rect(), max(1,self.border/2-1))

    def update(self):
        # addChild has to wait until the game loop starts, because the groups
        # aren't set up until then
        if self.text.text != '' and self.text not in self._children:
            self.addChild(self.text)
            self.text.position = (0,0)
        if self.graphic is not None and self.graphic not in self._children:
            self.addChild(self.graphic)

class ToggleButton(Button):
    """A toggle button that changes color when clicked.

       @ivar toggled: Whether this button is on (True) or off (False, default).

       @keyword off: The background color of the button when it is not active.
       @keyword on: The background color of the button when it is active.
    """
    def __init__(self, *args, **kwargs):
        super(ToggleButton, self).__init__(*args, **kwargs)

        self.toggled = False
        
        # if we don't get off/on arguments, use the background color for off,
        # and "half" of it for on
        self._off = kwargs.get('off',self.bgColor)
        self._on = kwargs.get('on',(self._off[0]/2,self._off[1]/2,
                                    self._off[2]/2,self._off[3]))

        self.pixels.fill(self._off)
        self._drawBorder()

    def click(self, event):
        # TODO: allow custom click behavior?
        self.toggled = not self.toggled
        self.pixels.fill(self._on if self.toggled else self._off)
        self._drawBorder()
        self.redraw()

class Console(Image):
    """A simple on-screen console window."""
    def __init__(self, *args, **kwargs):
        super(Console, self).__init__(*args, **kwargs)

        self.x += self.width/2
        self.y += self.height/2
        
        self.textbox = text.Text('', size=self.size)
        self.textbox.background = Game.color('black')

    def update(self):
        """Update the console."""
        if self.textbox.dirty > 0:
            rect = Game.Rect(0,max(0,self.textbox.height - self.height),
                             self.width,min(self.rect.height,self.textbox.rect.height))
            self.pixels = self.textbox.pixels.subsurface(rect)
            self.redraw()
            self.textbox.dirty = 0

    def write(self, txt, newline=False):
        """Add text to the console window.

           @param txt: The text to display.
           @param newline: If True, add a newline after the text (default False).
        """
        self.textbox.text += str(txt) + ('\n' if newline else '')

    def show(self):
        """Show the console."""
        self.visible = 1
        self.redraw()

    def hide(self):
        """Hide the console."""
        self.visible = 0
        self.redraw()
