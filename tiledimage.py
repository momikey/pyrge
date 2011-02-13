import entity, gameloop, point
from gameloop import Game

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
           constructor arguments. However, the position of a TiledImage is
           that of its top-left corner, not its center.

       @param img: An object with the bitmap to be used as the "tile". This
           can be a Pyrge L{Image}, a Pygame Surface, or a string containing
           a filename.
    """
    def __init__(self, img, *args, **kwargs):
        super(TiledImage, self).__init__(*args, **kwargs)

        if isinstance(img, Game.Surface):
            # if we got a Surface
            self._tileimage = img
        elif isinstance(img, entity.Image):
            # if we got a Pyrge Image
            self._tileimage = img.pixels
        elif isinstance(img, basestring):
            # if we got a filename
            self._tileimage = entity.Image().load(img).pixels
        else:
            # don't know what to do
            raise TypeError, "Unable to find tile image"

        # in case we didn't get passed a width or height
        if self.width == 0.0:
            self.width = self._tileimage.get_width()
        if self.height == 0.0:
            self.height = self._tileimage.get_height()

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
