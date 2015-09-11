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


class Unit(object):

    def __init__(self, unit_filename, bullet_filename, x, y, bonus=0, speed=5):
        self.image = unit_filename
        self.x = x
        self.y = y
        self.width = 10  # temporary when we don't have real images
        self.height = 10  # must be height of real image
        self.bonus = bonus
        self.speed = speed
        self.is_dead = False
        self.bullet = Bullet(self, bullet_filename)
        self.shift = 5

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def check_fire(self, other_unit):
        raise NotImplementedError

    def fire(self, other_unit):
        raise NotImplementedError

    def make_bullet(self):
        raise NotImplementedError


class Invader(Unit):
    moving_speed = 0

    def __init__(self, hero_filename, bullet_filename, x, y, bonus=0, speed=5):
        super(Invader, self).__init__(hero_filename, bullet_filename, x, y, bonus, speed)
        self.moving_speed = speed

    def check_if_move_y(self):
        return self.x <= self.shift

    def set_speed(self, game_field_width):
        # this check for first Invader
        if self.x <= self.shift:
            self.moving_speed = self.speed or -self.speed  # positive value
        # this check for last Invader
        if self.x >= game_field_width:
            self.moving_speed = self.speed < 0 and self.speed or -self.speed  # negative value

    def check_fire(self, other_unit):
        raise NotImplementedError

    def fire(self, hero):
        hero.is_dead = True

    def make_bullet(self):
        # Invaders will be at the top and must bullet at the bottom
        # so speed must be positive value
        self.bullet.move(self.speed or -self.speed)


class Hero(Unit):

    def __init__(self, unit_filename, bullet_filename, x, y, bonus=0, speed=5, life_count=3):
        super(Hero, self).__init__(unit_filename, bullet_filename, x, y, bonus, speed)
        self.life_count = life_count

    def fire(self, invader):
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

    def check_fire(self, invader):
        # check if coordinate the bullet and the Invader's is the same
        if (self.bullet.x > invader.x - invader.width) and (self.bullet.x < invader.x + invader.width) and \
                (self.bullet.y > invader.y - invader.height) and (self.bullet.y < invader.y + invader.height):
            self.fire(invader)
            return True
        elif self.bullet.y < 0:
            return True
        else:
            return False


class Bullet():
    def __init__(self, unit, image):
        self.x = unit.x
        self.y = unit.y
        self.image = image

    def move(self, moving_speed):
        self.y += moving_speed


class GameController(object):

    def __init__(self, height, width, invaders_count):
        self.game_field = {'image': 'images/bg.png', 'height': height, 'width': width}
        self.hero = Hero('images/hero.png', 'images/bullet_hero',
                         self.game_field['height'] / 2, self.game_field['width'] - 10)
        self.invaders_count = invaders_count
        self.Invaders = []
        self.set_invaders()

    def set_invaders(self):
        x = 1
        y = 1
        for count in range(self.invaders_count):
            if self.hero.shift * x >= self.game_field['width']:
                x = 1
                y += 1
            pos_x = self.hero.shift * x
            pos_y = self.hero.shift * y
            self.Invaders.append(Invader('images/invader.png', 'images/bullet_invader', pos_x, pos_y, 10))
            x += 1

    def get_action(self, action):
        if action == 'bullet':
            make_bullet = True
            while make_bullet:
                self.hero.make_bullet()
                # print 'bullet - ', game_object.hero.bullet.__dict__
                for _invader in self.Invaders:
                    if self.hero.check_fire(_invader):
                        make_bullet = False
        if action == 'move_right':
            self.hero.move_to(self.hero.x + self.hero.speed, self.hero.y)
        if action == 'move_left':
            self.hero.move_to(self.hero.x - self.hero.speed, self.hero.y)


if __name__ == "__main__":
    game_object = GameController(50, 50, 2)

    '''this code for moving invaders. Work as a job.
        We set moving_speed for positive - if reach the left coordinate of our game field
        or negative  - if we reach the right coordinate of our game field '''

    while not game_object.hero.is_dead and len(game_object.Invaders):
        game_object.Invaders[0].set_speed(game_object.game_field['width'])
        game_object.Invaders[-1].set_speed(game_object.game_field['width'])
        check_if_move_y = game_object.Invaders[0].check_if_move_y()
        for invader in game_object.Invaders:
            new_x = invader.x + invader.moving_speed
            new_y = check_if_move_y and invader.y + invader.speed or invader.y
            invader.move_to(new_x, new_y)

        # for invader in game_object.Invaders:
        #     print invader.__dict__

        time.sleep(3)

    '''This example of calling actions such as 'bullet', 'move_left' for our hero
       Also we can call action 'move_right' '''

    # game_object.get_action('bullet')
    # game_object.get_action('move_left')
    # game_object.get_action('move_left')

    # for invader in game_object.Invaders:
    #     print 'invader - ', invader.__dict__
    # print 'hero - ', game_object.hero.__dict__
