import entity, util
from gameloop import Game, GameLoop

__doc__ = """A text object

L{text} is a module contaning a single class, L{Text}, that can
be used to create text objects. It supports varying fonts, font sizes, colors,
antialiasing, and word wrapping. The L{Text} class inherits from L{Image}, so
it is completely compatible with the rest of Pyrge, but it is also almost totally
self-contained, and can be used in other pygame-based applications with little
effort."""

__all__ = ['Text']

class Text(entity.Image):
    """A text display class.

       L{Text} can be used to create text display objects that have all the
       properties of a Pyrge L{Image}. Objects of this class have a number of
       different attributes that can be manipulated to produce bold text, italics,
       different fonts and font sizes, different colors (for both text and
       background), antialiasing, word-wrapping, and more.

       The constructor for L{Text} takes all of the usual L{Image} arguments,
       plus a number of specialized keyword arguments detailed below.

       @note: A Text object uses colorkey transparency, unless the text color
           is black (C{Color(0,0,0)}), in which case it will use per-pixel
           alpha values.

       @param text: The text that this object will render.

       @keyword font: A pygame Font object that contains all of the rendering
           information, such as font face, size, and bold/italics. If this is
           None, then Pyrge's default font will be used.
       @keyword antialias: Whether to render smooth text by using antialiasing.
       @keyword color: The color to use to render text, either as a pygame
           C{Color} object or as a tuple of RGB or RGBA.
       @keyword background: The color of the background, in the same format as
           the C{color} argument. If this is None, then a transparent background
           will be used.
       @keyword autowidth: If this argument is True (default is False), then
           the Text object will be resized so that the text will fit on a
           single line.
    """
    def __init__(self, text='', *args, **kwargs):
        # do these first, so we can use them for positioning

        # the actual text to render
        self._text = self._replace_escaped(kwargs.get('text', text))

        # the font to use for rendering
        self._font = kwargs.get('font', Game.defaultFont)

        # whether to use antialiasing
        self._aa = kwargs.get('antialias', False)

        # the text and background colors (respectively)
        self._color = kwargs.get('color', (255,255,255))
        self._bgcolor = kwargs.get('background', None)

        # whether the text should all be on one line, and the sprite resized
        # TODO: I don't really like the name "autowidth". What else can we call it?
        self._autowidth = kwargs.get('autowidth', False)

        # position and size
##        x = kwargs.get('x', 0.0)
##        y = kwargs.get('y', 0.0)
        kwargs['w'] = kwargs.get('w', kwargs.get('width', self._font.size(self._text)[0]))
        kwargs['h'] = kwargs.get('h', kwargs.get('height', self._font.get_linesize()))

##        super(Text, self).__init__(x,y,w,h)
        super(Text, self).__init__(*args, **kwargs)

        # change position semantics from center to top-left
        self.x += self.width/2
        self.y += self.height/2

        if len(self._text):
            self._render_text()

    def _render_text(self):
        """This is a helper method to render text to a surface with wrapping."""
        if self._autowidth:
            # "autowidth" means one line, no wrapping, and the left edge
            # stays in the same place
            textlines = [self.text]
            textheight = self.font.get_linesize()
            oldleft = self.left
            self.width = self.font.size(self.text)[0]
            self.x = oldleft + self.width/2.
        else:
            textlines = self._wrap(self.text)
            textheight = len(textlines) * self.font.get_linesize()

        textwidth = self.width
        self.height = textheight

        # fix in case we're drawing black text
        if self.background is None and self.color == Game.rgb(0,0,0):
            ALPHA = Game.Constants.SRCALPHA
        else:
            ALPHA = 0

        surf = Game.Surface((textwidth, textheight), ALPHA)

        for lineno,line in enumerate(textlines):
            if self.background is not None:
                r = self.font.render(line, self.antialias, self.color, self.background)
            else:
                r = self.font.render(line, self.antialias, self.color)
            surf.blit(r, (0,lineno*self.font.get_linesize()))

        self.pixels = surf

        if self.background is None:
            # per-pixel alphas override colorkeys, so this line won't do anything
            # if the text is black
            self.pixels.set_colorkey((0,0,0), Game.Constants.RLEACCEL)

        self.redraw()

    def _wrap(self, text):
        """This is a helper method to calculate where a line should break when wrapping."""
        if '\n' in text:
            return list(util.flatten([self._wrap(l) for l in text.split('\n')]))
        else:
            lines = []
            linelength = self._font.size(text)[0]
            if linelength <= self.width:
                # line is short enough, we don't need to do anything
                lines.append(text)
                return lines
            else:
                breakpoint = text.rfind(' ',0,len(text)*self.width/linelength)
                if breakpoint != -1:
                    # we found a word break
                    lines.append(text[:breakpoint])
                    lines.extend(self._wrap(text[breakpoint+1:]))
                else:
                    # there's no word break, so nothing we can do
                    lines.append(text)
                return lines

    def _replace_escaped(self, text):
        """Helper method to replace non-newline special characters with printable equivalents"""
        # TODO: handle other escaped characters
        # TODO: better cross-platform EOL support
        return text.replace('\t', '    ').replace('\r', '\n')

    def _get_text(self):
        return self._text

    def _set_text(self, txt):
        self._text = self._replace_escaped(txt)
        self._render_text()

    text = property(_get_text, _set_text, doc="The text of this object.")

    def _get_font(self):
        return self._font

    def _set_font(self, font):
        self._font = font
        self._render_text()

    font = property(_get_font, _set_font, doc="The font used to render this text object.")

    def _get_aa(self):
        return self._aa

    def _set_aa(self, aa):
        self._aa = aa
        self._render_text()

    antialias = property(_get_aa, _set_aa, doc=\
            """Whether this text object should be rendered with antialiasing.""")

    def _get_color(self):
        return self._color

    def _set_color(self, col):
        self._color = col
        self._render_text()

    color = property(_get_color, _set_color, doc="The color this text should appear.")

    def _get_bg(self):
        return self._bgcolor

    def _set_bg(self, bg):
        self._bgcolor = bg
        self._render_text()

    background = property(_get_bg, _set_bg, doc=\
            """The background color for this text object,
               or None if it should be transparent.""")
