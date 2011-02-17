import random
from pyrge import *
from pyrge.quadtree import QuadTree

class Ship(Entity):
    def __init__(self):
        super(Ship, self).__init__(x=Game.width/2, y=Game.height-30)
        self.load("ship.png")
        self.scale(2,2,smooth=False)
        self.lives = 3
        Game.world.addHandler(Game.events.KEYDOWN, self.onSpace)

    def update(self):
        self.velocity.x = 0

        if Game.keys[Game.Constants.K_LEFT]:
            self.velocity.x -= 150
        elif Game.keys[Game.Constants.K_RIGHT]:
            self.velocity.x += 150

        super(Ship, self).update()

        self.x = min(self.x, Game.width - self.width - 8)
        self.x = max(self.x, 8)

    def onSpace(self, evt):
        if evt.key == Game.Constants.K_SPACE:
            b = Game.world.getAvailableBullet(self)
            if b is not None:
                b.reset(fired=self, position=self.position, vy=-160)

    def kill(self):
        self.lives -= 1
        if self.lives < 1:
            Game.world.lives.text = "Game Over"
        else:
            Game.world.lives.text = "Lives: %d" % self.lives
            
        Game.world.removeHandler(Game.events.KEYDOWN, self.onSpace)
        self.alive = self.visible = False

    def reset(self):
        self.position = Game.width/2, Game.height-30
        Game.world.addHandler(Game.events.KEYDOWN, self.onSpace)
        self.alive = True
        self.visible = True        

class Bullet(Entity):
    def __init__(self, pos):
        super(Bullet, self).__init__(x=pos.x, y=pos.y, w=2, h=8)
        self.pixels.fill((255,255,255))
        self.alive = False
        self.visible = False
        self.fired = None

    def update(self):
        if self.alive and (self.y < 0 or self.y > Game.height):
            self.kill()

        super(Bullet, self).update()

    def reset(self, fired, position, vy):
        self.alive = True
        self.visible = True
        self.fired = fired
        self.position = position
        self.velocity.y = vy

    def kill(self):
        self.alive = False
        self.visible = False

class Alien(Entity):
    def __init__(self, x, y, color):
        super(Alien, self).__init__(x=x, y=y)

        self.loadAnimation('alien.png', 3)
        self.scale(2,2,smooth=False,scaleAnimations=True)

        self.origx = x
        self.color = color
        self.shotclock = random.randint(4,15)*1000

##        frames = [0,0,0,1,1,1,0,0,0,2,2,2]
        self.addAnimation('default', [0,1,0,2], 3)
        self.play('default', startFrame=random.choice(self._animations['default']))
        self.velocity.x = 10

        for f in self._frames:
            f.convert(8)
            f.set_palette_at(0, color)

    def update(self):
        if self.x < self.origx - 16:
            self.x = self.origx - 16
            self.velocity.x = 10
            self.y += 2

        if self.x > self.origx + 16:
            self.x = self.origx + 16
            self.velocity.x = -10

        if self.y > Game.height / 3:
            self.shotclock -= Game.elapsed

        if self.shotclock <= 0:
            self.shotclock = random.randint(4,15)*1000
            b = Game.world.getAvailableBullet(self)
            if b is not None:
                b.reset(fired = self, position=self.position, vy=65)

        super(Alien, self).update()

class Shield(Image):
    def __init__(self, x,y):
        super(Shield, self).__init__(x,y,4,4)
        self.fixed = True
        self.pixels.fill((255,255,255))

    def collide(self, other):
        if other.y > self.y: return False
        if self.alive and self.overlap(other):
            return self.onCollision(other)

    def onCollision(self, other, directions=None):
        if self.alive:
            self.kill()
            if isinstance(other, Bullet):
                other.kill()
            return True

class FPS(text.Text):
    def __init__(self, **kwargs):
        super(FPS, self).__init__(**kwargs)
        self._autowidth = True
        self.background = Game.color('black')
        self.update()

    def update(self):
        self.text = "FPS: %.2f" % Game.clock.get_fps()
        self.rect.bottomright = (Game.world.width, Game.world.height)
        self._x, self._y = self.rect.center

class TheGame(World):
    def __init__(self):
        super(TheGame, self).__init__(fps=30)

        self.player = Ship()
        self.add(self.player)

        self.aliens = []
        colors = ['blue', 'cyan', 'green', 'yellow', 'red']
        for i in xrange(50):
            a = Alien(32 + (i%10)*64, 48 + (i/10)*64, Game.color(colors[i/10]))
            self.aliens.append(a)
        self.add(self.aliens)

        self.shields = Game.Sprite.Group()
        for i in xrange(256):
            s = Shield(x=64+160*(i/64)+(i%8)*4, y=Game.height-100+(i%64)/8*4)
            self.shields.add(s)
            
        self.add(self.shields)

        self.quadtree = QuadTree(self.shields.sprites())

        self.playerbullets = [Bullet(Vector(0,0)) for _ in xrange(8)]
        self.alienbullets = [Bullet(Vector(0,0)) for _ in xrange(24)]
        self.bullets = self.playerbullets + self.alienbullets
        self.add(self.bullets)

        self.fpsdisplay = FPS(font=Game.defaultFont)
        self.add(self.fpsdisplay)

        self.lives = text.Text(x=50, y=Game.world.height-20, autowidth=True)
        self.lives.text = "Lives: %d" % self.player.lives
        self.add(self.lives)

        self.killTimer = 2000

    def update(self):
        collided = lambda f,s: f.collide(s,kill=True)
        shieldcollision = lambda f,s: f.collide(s)

        livingbullets = [b for b in self.bullets if b.alive]

        vsshields = [_ for _ in livingbullets + self.aliens \
            if _.y > 360 and _.x > 60 and _.x < 580]

        for b in vsshields:
            hit = self.quadtree.hit(b.rect)
            if hit:
                for h in hit:
                    if h.alive:
                        h.collide(b)

        Game.Sprite.groupcollide(Game.Sprite.Group(self.playerbullets), \
            self.aliens, False, False, collided)
        Game.Sprite.spritecollide(self.player, Game.Sprite.Group(self.alienbullets), \
            False, collided)

        if not self.player.alive:
            self.killTimer -= Game.elapsed
            if self.killTimer <= 0:
                self.killTimer = 2000
                self.player.reset()

        super(TheGame, self).update()

    def getAvailableBullet(self, who):
        if who == self.player:
            bulletslist = self.playerbullets
        else:
            bulletslist = self.alienbullets

        for e in bulletslist:
            if not e.alive:
                e.alive = True
                e.visible = True
                return e
        return None

if __name__ == '__main__':
    TheGame().loop()
