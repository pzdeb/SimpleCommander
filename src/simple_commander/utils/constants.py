""" This module contains list of constant variables. """


ANGLE = 2
ACTION_INTERVAL = 0.05
DEFAULT_LIFE_COUNT = 5
DEFAULT_SPEED = 35
DEFAULT_SPEED_BULLETS = 120
MAX_ANGLE = 360
MAX_SPEED = 220
ROTATION_ANGLE = 0.015
SPEED = 8
STEP_INTERVAL = 1  # 1 second, can be changed to 0.5
UNIT_PROPERTIES = ['x', 'y', 'x1', 'y1', 'angle', 'hits', 'speed', 'id', 'life_count', 'type', 'width', 'height', 'name']

UNITS = {'invader': [{'type': 'invader1', 'dimension': 28},
                     {'type': 'invader2', 'dimension': 28},
                     {'type': 'invader3', 'dimension': 28}],
         'hero': [{'type': 'hero_1_black', 'dimension': 28},
                  {'type': 'hero_1_green', 'dimension': 28},
                  {'type': 'hero_1_blue', 'dimension': 28},
                  {'type': 'hero_1_pink', 'dimension': 28},
                  {'type': 'hero_1_white', 'dimension': 28},
                  {'type': 'hero_1_red', 'dimension': 28},
                  {'type': 'hero_2_black', 'dimension': 28},
                  {'type': 'hero_2_green', 'dimension': 28},
                  {'type': 'hero_2_blue', 'dimension': 28},
                  {'type': 'hero_2_pink', 'dimension': 28},
                  {'type': 'hero_2_white', 'dimension': 28},
                  {'type': 'hero_2_red', 'dimension': 28}],
         'bullet_hero': {'type': 'bullet_hero', 'dimension': 5},
         'bullet_invader': {'type': 'bullet_invader', 'dimension': 10}}
