#!/usr/bin/env python3
from simple_commander.game.game_controller import GameController

'''
In this game we have two role - invader and hero. Both can bullet.

Invaders are located at the top of game field and always move from the right side to the left and revert.
Also they slowly move to the bottom.

Main hero is located at the centre at the bottom. He can move to the left and to the right.
If he bullet some invader, his bonus is grow.
When invader bullet to main hero, the main hero's life is decrease.
'''
__game = None

def get_game(height=None, width=None, invaders_count=None):
    global __game

    if not __game and height and width and invaders_count is not None:
        __game = GameController(height=height,
                                width=width,
                                invaders_count=invaders_count)
    return __game