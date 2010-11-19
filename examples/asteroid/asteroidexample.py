import pyrge
from pyrge import world, entity, util
import random
from pyrge.point import Vector
from pyrge.world import Game

MAX_X = 640
MAX_Y = 420

class WrapSprite(entity.Entity):
    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
        super(WrapSprite, self).__init__(x,y,w,h)

    def update(self):
        super(WrapSprite, self).update()

        if self.alive:
            if self.x > MAX_X:
                self.x = 0
            elif self.x < 0:
                self.x = MAX_X - 1

            if self.y > MAX_Y:
                self.y = 0
            elif self.y < 0:
                self.y = MAX_Y - 1

class Asteroid(WrapSprite):
    LARGE = 0
    MEDIUM = 1
    SMALL = 2

    def __init__(self, position=Vector(0,0), velocity=Vector(0,0), size=0):
        super(Asteroid, self).__init__()

        self.sizetype = size
        self.reset(position,velocity,size)

    def reset(self, position, velocity, size):
        self.load(['large.png','medium.png','small.png'][size])
        self.visible = True
        self.alive = True
        self.rotating = True

        self.angularVelocity = random.randint(-60,60)
        self.angle = random.randint(0,359)

        if position:
            # making a new one
            self.position = position
            self.velocity = velocity
            return self

        initial_vel = 20

        if random.random() < 0.5:
            # left or right
            if random.random() < 0.5:
                # on the left
                self.x = 0
                self.velocity.x = initial_vel / 2 + random.random() * initial_vel
            else:
                # on the right
                self.x = Game.width
                self.velocity.x = -initial_vel / 2 - random.random() * initial_vel

            self.y = random.randint(20,MAX_Y - 20)
            self.velocity.y = random.random() * initial_vel * 2 - initial_vel
        else:
            # top or bottom
            if random.random() < 0.5:
                # on the top
                self.y = 0
                self.velocity.y = initial_vel / 2 + random.random() * initial_vel
            else:
                # on the bottom
                self.y = Game.height
                self.velocity.y = -initial_vel / 2 - random.random() * initial_vel

            self.x = random.randint(20,MAX_X - 20)
            self.velocity.x = random.random() * initial_vel * 2 - initial_vel

        return self

    def update(self):
        self.hitbox = self.rect.inflate(8,8)
        self.mask = Game.Mask.from_surface(self.image)
        super(Asteroid, self).update()

    def kill(self):
        if self.sizetype != Asteroid.SMALL:

            newsize = self.sizetype + 1
            initial_vel = 20 * (newsize + 1)  # velocity hack

            chunks = random.randint(2,4)

            for i in xrange(chunks):
                ax = self.x + self.width / 2
                ay = self.y + self.height / 2
                avx = random.random() * initial_vel * 2 - initial_vel
                avy = random.random() * initial_vel * 2 - initial_vel
                a = Asteroid.create(Vector(ax, ay), Vector(avx, avy), newsize)
                Game.world.add(a)

        if self.sizetype == Asteroid.LARGE:
            Game.world.score += 10
        elif self.sizetype == Asteroid.MEDIUM:
            Game.world.score += 50
        elif self.sizetype == Asteroid.SMALL:
            Game.world.score += 100

        super(Asteroid, self).kill()

    @staticmethod
    def create(position=Vector(0,0), velocity=Vector(0,0), size=0):
        newa = Game.world.getAvailable(Asteroid)

        if newa is None:
            newa = Asteroid(position, velocity, size)
        else:
            newa.reset(position, velocity, size)

        return newa

class Ship(WrapSprite):
    def __init__(self):
        super(Ship, self).__init__(x=MAX_X/2-8, y=MAX_Y/2-8)

        self.load('ship.png')
        self.angle = 90
        self.maxThrust = 10
        self.maxVelocity = Vector(240,240)
        self.lives = 3
        self.warps = 5

        Game.world.addHandler(Game.event_types.KEYDOWN, self.onSpace)
        Game.world.addHandler(Game.event_types.KEYDOWN, self.onWarp)

    def update(self):

        self.angularVelocity = 0
        if Game.keys[Game.Constants.K_LEFT]:
            self.angularVelocity = 180
        elif Game.keys[Game.Constants.K_RIGHT]:
            self.angularVelocity = -180

        self.thrust = 0
        if Game.keys[Game.Constants.K_UP]:
            self.thrust -= util.vectorFromAngle(self.angle) * self.maxThrust
        self.velocity += self.thrust

##        self.mask = Game.Mask.from_surface(self.image)
        self.hitbox = self.rect.inflate(-10,-10)

        super(Ship, self).update()

    def reset(self):
        oldpos = self.position
        newpos = (random.randint(0,MAX_X), random.randint(0,MAX_Y))
        asts = Game.Sprite.Group([a for a in Game.world.getEntities(Asteroid) if a.visible])
        collided = False
        for a in asts:
            if a.rect.inflate(32,32).collidepoint(newpos):
                collided = True

        if collided:
            newpos = self.reset()
        
        self.position = newpos
        self.velocity = 0.0, 0.0

        return newpos

    def kill(self):
        if self.lives > 0:
            self.reset()
            self.lives -= 1
        else:
            super(Ship, self).kill()
        

    def onSpace(self, evt):
        if evt.key == Game.Constants.K_SPACE and self.alive:
            b = Game.world.getAvailable(Bullet) #self.bullets[self.bulletIndex]
            if b is None:
                b = Bullet()
            else:
                b.lifetime = 2000

            b.alive = True
            b.visible = True
            b.angle = self.angle
            b.position = self.position
            b.velocity = util.vectorFromAngle(self.angle) * 150 + self.velocity
            Game.world.add(b)

    def onWarp(self, evt):
        if evt.key == Game.Constants.K_x:
            if self.warps > 0:
                self.reset()
                self.warps -= 1

                

class Bullet(WrapSprite):
    def __init__(self):
        super(Bullet, self).__init__()

        surf = Game.Surface((4,4), Game.Constants.SRCALPHA)
        Game.Draw.circle(surf, (255,255,255), (2,2), 2)
        self.loadSurface(surf)
        self.alive = False
        self.visible = False

        self.lifetime = 2000

    def update(self):
        if self.alive:
            self.lifetime -= Game.elapsed
            if self.lifetime <= 0:
                self.kill()

        super(Bullet, self).update()

class TheGame(world.World):
    def __init__(self):
        super(TheGame, self).__init__(fps=30)

        self.camera = Vector(self.width/2, self.height/2)
##        self.statusbg.addChild(self.statusline)
        self.lives = 3
        self.reset()

    def reset(self):
        for e in self._entities:
            e.kill()
        self._entities.empty()

        for h in self._evtHandlers[Game.event_types.KEYDOWN]:
            self.removeHandler(Game.event_types.KEYDOWN, h)

        self.addAsteroid()
        self.ship = Ship()

        self.score = 0
        self.statusbg = pyrge.entity.Image(0,0,self.width,self.height - MAX_Y, name="Status")
        self.statusbg.position = self.width/2, MAX_Y + (self.height-MAX_Y)/2
        self.statusbg.pixels.fill((50,50,50))
        self.statusline = pyrge.text.Text(x=0, y=-20, autowidth=True, color=(255,255,255))
        self.add(self.ship)
        self.add(self.statusbg)
        self.statusbg.addChild(self.statusline)
##        self.add(self.statusline)

        self.timer = 0

    def update(self):
        self.timer -= Game.elapsed
        if self.timer <= 0:
            self.addAsteroid()

        collided = lambda f,s: entity.Entity.collide(f,s,kill=True)

        asts = Game.Sprite.Group([a for a in self.getEntities(Asteroid)])
        bullets = Game.Sprite.Group([b for b in self.getEntities(Bullet)])

        Game.Sprite.groupcollide(bullets, asts, False, False, collided)
        Game.Sprite.spritecollide(self.ship, asts, False, collided)

        asts.empty()
        bullets.empty()

##        if not self.ship.alive:
##            if self.lives > 0:
##                self.lives -= 1
##                self.ship.reset()
##            else:
##                self.statusline.text = "Score: %d\tGame Over!" % self.score

        if self.ship.alive:
            self.statusline.text = "Score: %d\tLives: %d" % (self.score,self.ship.lives)
        else:
            self.statusline.text = "Score: %d\tGame Over!" % self.score
##            self.paused = True

        super(TheGame, self).update()

    def addAsteroid(self):
        if len([e for e in self.getEntities(Asteroid) if e.alive]) < 32:
            a = Asteroid.create()
            a.visible = True
            self.add(a)
        self.timer = random.randint(0,10000)

    def getAvailable(self, cls=Asteroid):
        for s in self.getEntities(cls):
            if not s.alive:
                return s

        return None

if __name__ == '__main__':
    TheGame().loop()
