from gameloop import Game

__doc__ = """A simple, static quadtree

The L{quadtree} module contains a single class, L{QuadTree},
which represents a simple quadtree structure that can be used to hold static
sprites for uses such as collision detection."""

# copied (with some modifications) from the pygame cookbook
class QuadTree(object):
    """A static quadtree class.

       @param items: A sequence of items to place in the tree.
       @param depth: The maximum depth of any one quadrant.
       @param bounds: A bounding rectangle covering all the objects. The top level
           of the tree can calculate its own bounds from its items, while the
           subtrees' bounds will be calculated based on their parents' bounds,
           so specifying this parameter is rarely necessary.
    """
    def __init__(self, items, depth=8, bounds=None):
        # the four sub trees
        self.nw = self.ne = self.se = self.sw = None

        # change a Group to a list
        # this can be useful when using World.getEntities()
        if isinstance(items, Game.Sprite.Group):
            items = items.sprites()

        depth -= 1
        if depth == 0 or not items:
            self.items = items
            return

        if bounds:
            bounds = Game.Rect(bounds)
        else:
            bounds = items[0].rect
            bounds = bounds.unionall([i.rect for i in items[1:]])

        cx = self.cx = bounds.centerx
        cy = self.cy = bounds.centery

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.rect.left <= cx and item.rect.top <= cy
            in_sw = item.rect.left <= cx and item.rect.bottom >= cy
            in_ne = item.rect.right >= cx and item.rect.top <= cy
            in_se = item.rect.right >= cx and item.rect.bottom >= cy

            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)

        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (bounds.left, bounds.top, cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, bounds.top, bounds.right, cy))
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, cy, bounds.right, bounds.bottom))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (bounds.left, cy, cx, bounds.bottom))

    def hit(self, rect):
        """Gets all the objects that intersect the given rectangle."""
        # Find the hits at the current level.
        hits = set( [ self.items[n] for n in rect.collidelistall( self.items ) ] )

        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)

        return hits
