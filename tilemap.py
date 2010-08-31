from gameloop import Game, GameLoop
from spritesheet import SpriteSheet
from entity import Image
from util import Struct
import point

__doc__ = """A spritesheet-based tilemap

             L{tilemap} has a single class, L{TileMap} (note the capitalization!)
             that defines a simple tilemap based on a spritesheet (specifially,
             a L{SpriteSheet} object).
             """

class TileMap(Image):
    """A simple tilemap created from a SpriteSheet object.

    A L{TileMap} is an L{Image} created by combining a number of smaller images
    (tiles) taken from a L{SpriteSheet}. The tiles that should be used are
    determined by a number of integers that give the position of a tile on the
    SpriteSheet. The tile indices are given in the "tile map", a list of lists:
    each sub-list contains the indices for one row of the map, in order from
    left to right, with the sub-lists ordered from top to bottom. The special
    tile index C{-1} can be used to show that a tile is blank.

    @note: The position of a TileMap object is that of its top-left corner,
        not its center.

    @ivar sheet: The SpriteSheet that this TileMap uses.
    @ivar themap: A list of lists used to map tile indices to SpriteSheet tiles.
    @ivar rows: The number of rows in the final mapped image.
    @ivar columns: The number of columns in the final mapped image.
    @ivar tiles: A dictionary containing all the mapped tiles, whose keys
        are tuples (X,Y), where X and Y are the column and row position of
        each tile.
    
    @param sheet: A SpriteSheet object representing the tiles that can be used
        by this TileMap.
    @param themap: A list of map rows (each itself a list of tile indices).
    """
    def __init__(self, sheet, themap, *args, **kwargs):
        # sheet must be a pre-existing SpriteSheet
        # TODO: make this unnecessary
        if not isinstance(sheet, SpriteSheet):
            raise ValueError, "TileMap requires a SpriteSheet"

        super(TileMap, self).__init__(*args, **kwargs)

        # the spritesheet that we'll use
        self.sheet = sheet

        # the tilemap: a list of lists, with each sublist being one row of tile ids
        self.themap = themap

        # the size of the map in tiles
        self.rows = len(self.themap)
        self.columns = max([len(_) for _ in self.themap])

        # the size of the map in pixels
        self.height = self.rows * self.sheet.spriteheight
        self.width = self.columns * self.sheet.spritewidth

        # a dictionary of all the tiles in the map
        # the keys are tuples (x,y), values are the tiles themselves
        self.tiles = {}

        borderx, bordery = self.sheet.spritewidth/2, self.sheet.spriteheight/2
        
        for rowid,row in enumerate(self.themap):
            for colid,col in enumerate(row):
                tile = Image(x=colid*self.sheet.spritewidth+self.x+borderx, \
                             y=rowid*self.sheet.spriteheight+self.y+bordery, \
                             w=self.sheet.spritewidth, \
                             h=self.sheet.spriteheight)
                tile.fixed = True
                if col != -1:
                    # -1 is a blank tile, we just leave it empty
                    tile.loadSurface(self.sheet.spriteAt(col))
                    tile.pixels.set_colorkey(self.sheet.colorkey)
                    self.tiles[(colid,rowid)] = tile

    def update(self):
        """Updates the tilemap. This only does something the first time it is
        called, because of a small quirk in the way Pyrge handles pygame's
        drawing system."""
        super(TileMap, self).update()

        # On the first update, we need to add the tiles to the display list.
        # This is because a pygame sprite's add() method only works on groups,
        # and the tilemap itself is not in a group when it is first created.
        if not self._children:
            for tile in self.tiles.values():
                self.addChild(tile)

    def overlap(self, other, checkAlive=False):
        """Tests whether an object intersects any tile in the map.

           @param other: The object that will be tested for collision.
           @return: A list of tiles that overlap the given object.
        """
        return [t for t in self.tiles.values() if other.overlap(t)]

    def collide(self, other, kill=False, checkAlive=True):
        """Performs collision detection and calls collision response methods.

           Specifically, this method tests for overlapping of solid tiles, and
           calls the "other" object's collision function against each tile. 

           @param other: The object that will be tested for collision.
           @return: A list of overlapping tiles.
        """
        overlapping = self.overlap(other)

        for tile in overlapping:
            if tile.collidable:
                other.collide(tile)

        return overlapping

    def at(self, xpos, ypos=None):
        """Gets the tile at a given coordinate.

           @return: A L{Struct} with two attributes:
                - tile : A copy of the tile at a specific location on the map,
                    or None if the given position is outside the boundaries of the map.
                - index : The tile's index on the tilemap's spritesheet, or -1
                    for a blank tile.
        """
        if ypos is None:
            ypos, xpos = divmod(xpos, self.columns)

        if xpos < 0 or ypos < 0 or xpos > self.columns or ypos > self.rows:
            _tileid = None
        else:
            _tileid = self.themap[int(ypos)][int(xpos)]

        _tile = self.tiles.get((xpos,ypos),None)
        return Struct(index=_tileid, tile=_tile)

    def atWorldPosition(self, xpos, ypos):
        """Gets the tile at a specific world-based coordinate.

           @return: A L{Struct} with two attributes:
                - tile : A copy of the tile at a specific location on the map,
                    or None if the given position is outside the map.
                - index : The tile's index on the tilemap's spritesheet, or -1
                    for a blank tile.
        """
        left = self.x
        top = self.y

        # Note integer division here
        tx = (xpos - left) // self.sheet.spritewidth
        ty = (ypos - top) // self.sheet.spriteheight
        return self.at(tx,ty)

    def setSolidTiles(self, indices):
        """Sets a list of tiles to be solid.

           A solid tile can be the target of a collision.

           @param indices: A list of spritesheet indices to be made solid.
        """
        for tile in self.tiles:
            if self.at(*tile).index in indices:
                self.tiles[tile].collidable = True

    def setClearTiles(self, indices):
        """Sets a list of tiles to be "clear" (i.e., not solid).

           @param indices: A list of spritesheet indices to be made clear.
        """

        for tile in self.tiles:
            if self.at(*tile).index in indices:
                self.tiles[tile].collidable = False
            

    @staticmethod
    def fromString(sheet, mapstring, *args, **kwargs):
        """Creates a new tilemap from a string.

           @param sheet: The SpriteSheet to use when creating the TileMap.
           @param mapstring: A multi-line string specifying the tile indices.
               Each line of the string is one row of tiles, and individual tiles
               in a row are given by comma-separated tile indices.
           @return: A new TileMap object.
        """
        rows = []
        lines = mapstring.split('\n')
        for l in lines:
            rows.append([int(i) for i in l.split(',') if i != ''])

        return TileMap(sheet, rows, *args, **kwargs)

    @staticmethod
    def fromImage(sheet, image, colors, *args, **kwargs):
        """Creates a new tilemap from an image.

           @param sheet: The SpriteSheet to use when creating the TileMap.
           @param image: The image to use as the basis for the TileMap.
           @param colors: A dictionary mapping color values to tile indices.
               Any color that is not in the colors dictionary is treated as
               a blank tile (index -1). The keys in the colors dict should
               be RGB or RGBA tuples.
        """
        if isinstance(image, basestring):
            image = Game.Image.load(image)

        rows = []
        pxarray = Game.PixelArray(image)

        for y in xrange(image.get_height()):
            thisRow = []
            for x in xrange(image.get_width()):
                r,g,b,a = image.unmap_rgb(pxarray[x][y])
                idx = colors.get((r,g,b,a),None)
                if idx is None:
                    idx = colors.get((r,g,b),-1)
                thisRow.append(idx)
            rows.append(thisRow)

        return TileMap(sheet, rows, *args, **kwargs)

if __name__ == '__main__':
    loop = GameLoop()

    bg = Game.Surface((loop.width, loop.height))
    bg.fill(Game.NamedColors['lightskyblue'])
    loop.background = bg
    sheet = SpriteSheet('blocks1.bmp', spritewidth=32, spriteheight=32, \
                        xborder=2, yborder=2, borderleft=True, bordertop=True, colorkey=(0,0,0))

    tiles = """93,94,95,-1,-1,-1,96,97,
-1,-1,1,0,1,-1,90,90"""

    tileDict = {(255,0,0): 93, (0,255,0): 94, (0,0,255): 95, (255,255,0): 96, (255,0,255): 97,
                (0,255,255): 90, (128,128,128): 0, (204,204,204): 1}

    tilemap = TileMap.fromImage(sheet, "testmap.png", tileDict)

    tilemap.setClearTiles(range(93,98))

    for t in tilemap.tiles:
        print tilemap.tiles[t].mask.outline()
    loop.add(tilemap)

    loop.loop()
