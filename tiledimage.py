import entity, gameloop, point

__doc__ = """A tiled image, as used for backgrounds and terrain

The L{tiledimage} module's single class, L{TiledImage}, is a
specialized subclass of L{Image} that repetitively blits a small bitmap across
its surface, creating a textured or "tiled" appearance. This is often used in
2D games to make blocky terrain or backgrounds."""

__all__ = ['TiledImage']

class TiledImage(entity.Image):
    """An image filled with tiles of a smaller image.

       The L{TiledImage} class is used to make large images that are composed
       of many copies of a single "tile" image. This is commonly used to make
       background images and terrain in 2D games, but it can be used anywhere
       that a "textured" image is needed.

       @note: TiledImage is a subclass of L{Image}, and can take all of its
           constructor arguments. However, the position of a  TiledImage is
           that of its top-left corner, not its center.

       @param img: A pygame Surface object containing the bitmap to be used
           as the "tile".
    """
    def __init__(self, img, *args, **kwargs):
        self._tileimage = img       # img must be a Surface

##        # position and size properties
##        x = kwargs.get('x', 0.0)
##        y = kwargs.get('y', 0.0)
##        w = kwargs.get('w', kwargs.get('width', img.get_width()))
##        h = kwargs.get('h', kwargs.get('height', img.get_height()))

        super(TiledImage, self).__init__(*args, **kwargs)

        # in case we didn't get passed a width or height
        if self.width == 0.0:
            self.width = img.get_width()
        if self.height == 0.0:
            self.height = img.get_height()

        # change position semantics from center to top-left
        self.x += self.width/2
        self.y += self.height/2

        self._doTile()

    def _doTile(self):
        """Helper method to actually tile the image."""
        imgwidth, imgheight = self._tileimage.get_size()

        for xtile in xrange(0, self.width, imgwidth):
            for ytile in xrange(0, self.height, imgheight):
                self.pixels.blit(self._tileimage, (xtile,ytile))

    @property
    def tile(self):
        """The tile bitmap"""
        return self._tileimage


# Testing starts here
if __name__ == '__main__':
    from spritesheet import SpriteSheet

    loop = gameloop.GameLoop()
    sheet = SpriteSheet('blocks1.bmp', spritewidth=32, spriteheight=32, \
                        xborder=2, yborder=2, borderleft=True, bordertop=True, colorkey=(0,0,0))

    ti = TiledImage(sheet.spriteAt(90), x=100, y=100, w=160, h=128)
    ti2 = TiledImage(sheet.spriteAt(180), w=640, h=480)

    loop.add((ti,ti2))
    ti.foreground()
    loop.loop()
