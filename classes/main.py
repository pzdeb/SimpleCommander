#!/usr/bin/env python3

import time

'''

In this game we have two role - invader and hero. Both can bullet.

Invaders are located at the top of game field and always move from the right side to the left and revert.
Also they slowly move to the bottom.

Main hero is located at the centre at the bottom. He can move to the left and to the right.
If he bullet some invader, his bonus is grow.
When invader bullet to main hero, the main hero's life is decrease.

'''


class GameScreen(object):

    def __init__(self, filename, height, width):
        self.image = filename
        self.height = height
        self.width = width


class Unit(object):

    def __init__(self, filename, x, y, bonus=0, speed=5):
        self.image = filename
        self.x = x
        self.y = y
        self.width = 10  # temporary when we don't have real images
        self.height = 10  # must be height of real image
        self.bonus = bonus
        self.speed = speed
        self.is_dead = False
        self.bullet = Bullet(self)
        self.shift = 10

    def check_explosion(self, other_unit):
        pass

    def make_explosion(self, other_unit):
        pass

    def make_bullet(self):
        pass

    def set_bullet_image(self):
        pass


class Invader(Unit):
    moving_speed = 0

    def move_x(self, speed):
        self.x += speed

    def move_y(self, speed):
        self.y += speed or -speed  # positive value

    def check_if_move_y(self):
        if self.x <= self.shift:
            return True
        return False

    def set_speed(self, screen_width):
        # this check for first Invader
        if self.x <= self.shift:
            Invader.moving_speed = self.speed or -self.speed  # positive value
        # this check for last Invader
        if self.x >= screen_width:
            Invader.moving_speed = self.speed < 0 and self.speed or -self.speed  # negative value

    def make_explosion(self, hero):
        hero.is_dead = True

    def make_bullet(self):
        # Invaders will be at the top and must bullet at the bottom
        # so speed must be positive value
        self.bullet.move(self.speed or -self.speed)

    def set_bullet_image(self):
        self.bullet.set_image('images/bullet_invader')


class Hero(Unit):

    def __init__(self, filename, x, y, bonus=0, speed=5, life_count=3):
        super(Hero, self).__init__(filename, x, y, bonus, speed)
        self.life_count = life_count

    def move_right(self):
        self.x += self.speed

    def move_left(self):
        self.x -= self.speed

    def make_explosion(self, invader):
        if self.life_count > 0:
            self.life_count -= 1
            invader.is_dead = True
            self.bonus += invader.bonus
        else:
            self.is_dead = True

    def make_bullet(self):
        # hero will be at the bottom and must bullet at the top
        # so speed must be negative value
        self.bullet.move(-self.speed)

    def check_explosion(self, invader):
        # check if coordinate the bullet and the Invader's is the same
        if (self.bullet.x > invader.x - invader.width) and (self.bullet.x < invader.x + invader.width) and \
                (self.bullet.y > invader.y - invader.height) and (self.bullet.y < invader.y + invader.height):
            self.make_explosion(invader)
            return True
        elif self.bullet.y < 0:
            return True
        else:
            return False

    def set_bullet_image(self):
        self.bullet.set_image('images/bullet_hero')


class Bullet():
    def __init__(self, unit):
        self.x = unit.x
        self.y = unit.y
        self.image = ''

    def move(self, moving_speed):
        self.y += moving_speed

    def set_image(self, filename):
        self.image = filename


class GameObject(object):

    def __init__(self, height, width, Invaders_count):
        self.screen = GameScreen('images/bg.png', height, width)
        self.hero = Hero('images/hero.png', self.screen.height / 2, self.screen.width - 20)
        self.Invaders_count = Invaders_count
        self.Invaders = []
        self.set_invaders()

    def set_invaders(self):
        x = 1
        y = 1
        for count in range(self.Invaders_count):
            if self.hero.shift * x >= self.screen.width:
                x = 1
                y += 1
            pos_x = self.hero.shift * x
            pos_y = self.hero.shift * y
            self.Invaders.append(Invader('images/Invader.png', pos_x, pos_y, 10))
            x += 1

    def get_action(self, action):
        if action == 'bullet':
            make_bullet = True
            while make_bullet:
                self.hero.make_bullet()
                # print 'bullet - ', game_object.hero.bullet.__dict__
                for _invader in self.Invaders:
                    if self.hero.check_explosion(_invader):
                        make_bullet = False
        if action == 'move_right':
            self.hero.move_right()
        if action == 'move_left':
            self.hero.move_left()


if __name__ == "__main__":
    game_object = GameObject(50, 50, 2)

    '''this code for moving invaders. Work as a job.
        We set moving_speed for positive - if reach the left coordinate of our game field
        or negative  - if we reach the right coordinate of our game field '''

    while not game_object.hero.is_dead and len(game_object.Invaders):
        game_object.Invaders[0].set_speed(game_object.screen.width)
        game_object.Invaders[-1].set_speed(game_object.screen.width)
        moving_speed = game_object.Invaders[0].moving_speed

        if game_object.Invaders[0].check_if_move_y():
            for Invader in game_object.Invaders:
                Invader.move_x(moving_speed)
                Invader.move_y(moving_speed)
        else:
            for Invader in game_object.Invaders:
                Invader.move_x(moving_speed)

        # for Invader in game_object.Invaders:
        #     print Invader.__dict__

        time.sleep(3)

    '''This example of calling actions such as 'bullet', 'move_left' for our hero
       Also we can call action 'move_right' '''

    # game_object.get_action('bullet')
    # game_object.get_action('move_left')
    # game_object.get_action('move_left')

    # for invader in game_object.Invaders:
    #     print 'invader - ', invader.__dict__
    # print 'hero - ', game_object.hero.__dict__
