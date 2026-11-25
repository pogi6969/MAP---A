#!/usr/bin/env python3
"""Builds the Husky Maze Coder app: tools/husky_coder.src.html + a program template made from
maze_mouse_husky.py (the tested robot program, with {{FIELDS}} the app fills in and the uploaded map built in).
Writes ../husky_maze_coder.html (open it in Chrome/Edge) and, with --artifact PATH, the page body for publishing."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
src = open(os.path.join(ROOT, 'maze_mouse_husky.py')).read()


def sub(old, new):
    global src
    assert src.count(old) == 1, 'not found once: ' + old
    src = src.replace(old, new)


sub('#  SPIKE Prime MICROMOUSE + HuskyLens camera - Pybricks        (black walls, HuskyLens on port F)',
    '#  SPIKE Prime MICROMOUSE + HuskyLens camera - Pybricks   made with Husky Maze Coder (your maze map is built in)')
sub('#  Wiring: HuskyLens T -> port F pin 6,', '#  Wiring: HuskyLens T -> port {{HP}} pin 6,')
sub('print("HuskyLens OK on port F at"', 'print("HuskyLens OK on port {{HP}} at"')
for old, key in (('LEFT_MOTOR = Port.B', 'LM'), ('RIGHT_MOTOR = Port.E', 'RM'), ('FRONT_EYE = Port.C', 'FE'),
                 ('RIGHT_EYE = Port.A', 'RE'), ('LEFT_EYE = Port.D', 'LE')):
    sub(old + '\n', old.split('Port.')[0] + 'Port.{{' + key + '}}\n')
sub('HUSKY_PORT = Port.F ', 'HUSKY_PORT = Port.{{HP}} ')
sub('MAZE_W, MAZE_H = 6, 6        # cells across, cells forward', 'MAZE_W, MAZE_H = {{W}}, {{H}}        # cells across, cells up the picture')
sub('START = (0, 0)               # bottom-left corner, robot facing north (up)',
    'START = ({{SX}}, {{SY}})               # start cell: x from the left, y from the bottom of the picture\n'
    'START_H = {{SH}}                  # start heading: 0 = up the picture, 1 = right, 2 = down, 3 = left')
sub('GOALS = [(2, 2), (2, 3), (3, 2), (3, 3)]', 'GOALS = {{GOALS}}')
sub('CELL = 250                   #', 'CELL = {{CELL}}                   #')
sub('WALL_T = 12                  # wall thickness, mm\n',
    'WALL_T = {{WALLT}}                  # wall thickness, mm\n\n'
    '# ---------------- MAP FROM THE APP (your uploaded maze) ----------------\n'
    'USE_APP_MAP = {{USEMAP}}           # True = use this map straight away, False = search the maze first\n'
    'RUN_STYLE = "{{STYLE}}"            # "cells" = cell by cell, checks every wall (safest)   "arcs" = smooth arcs (fastest)\n'
    'APP_PATH = "{{PATH}}"              # route found by the app (N E S W = up right down left in the picture)\n'
    'APP_MAP = [                        # walls per cell, rows from the TOP of the picture; hex digit = N1 + E2 + S4 + W8\n'
    '{{MAPROWS}}\n'
    ']\n')
sub('WHEEL = 56                   #', 'WHEEL = {{WHEEL}}                   #')
sub('AXLE = 112                   #', 'AXLE = {{AXLE}}                   #')
sub('SIDE_OFS = 40                #', 'SIDE_OFS = {{SOFS}}                #')
sub('FRONT_OFS = 40               #', 'FRONT_OFS = {{FOFS}}               #')
sub('SEARCH_SPEED = 350           #', 'SEARCH_SPEED = {{VS}}           #')
sub('RUN_SPEED = 700              #', 'RUN_SPEED = {{VR}}              #')
sub('SMOOTH_SPEED = 600           #', 'SMOOTH_SPEED = {{VM}}           #')
sub('USE_CARDS = True             #', 'USE_CARDS = {{CARDS}}             #')
sub('H_REF = 180                  #', 'H_REF = {{HREF}}                  #')
sub('OBST_NEAR_Y = 185            #', 'OBST_NEAR_Y = {{OBSTY}}            #')
sub('''def flood(targets, known_only=False):''', '''def load_app_map():
    """walls of the uploaded maze -> the robot's map (every cell known)"""
    for r, row in enumerate(APP_MAP):
        y = MAZE_H - 1 - r
        for x, ch in enumerate(row):
            m = int(ch, 16)
            for d in range(4):
                if m & (1 << d):
                    add_wall(x, y, d)
            seen[x][y] = True


def flood(targets, known_only=False):''')
sub('''    remembered = load_map()
    if remembered and inner_walls() == 0:''', '''    if USE_APP_MAP:
        load_app_map()
        print("map from the app:", APP_PATH)
    remembered = USE_APP_MAP or load_map()
    if remembered and not USE_APP_MAP and inner_walls() == 0:''')
sub('''    x, y, h = START[0], START[1], 0
    if remembered and path_dirs(x, y, flood(GOALS, known_only=True)):''', '''    x, y, h = START[0], START[1], START_H
    if USE_APP_MAP and RUN_STYLE == "cells":
        print_map()
        hub.light.on(Color.CYAN)
        x, y, h = speed_run(x, y, h)                       # checks every wall on the way, re-plans if blocked
        if (x, y) in GOALS:
            save_map()
            hub.light.on(Color.BLUE)
            hub.display.icon(Icon.HAPPY)
            print("done at", x, y)
            wait(5000)
            return
        print("path blocked - searching from", x, y)
    elif remembered and path_dirs(x, y, flood(GOALS, known_only=True)):''')
sub('    h = turn_to(h, 0)\n', '    h = turn_to(h, START_H)\n')
assert '</script' not in src.lower()
page = open(os.path.join(HERE, 'husky_coder.src.html')).read()
assert page.count('@@TEMPLATE@@') == 1
page = page.replace('@@TEMPLATE@@', src)
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>\n')
open(os.path.join(ROOT, 'husky_maze_coder.html'), 'w').write(head + page + '\n</body></html>\n')
if '--artifact' in sys.argv:
    open(sys.argv[sys.argv.index('--artifact') + 1], 'w').write(page)
print('template fields:', sorted(set(__import__('re').findall(r'\{\{(\w+)\}\}', src))))
