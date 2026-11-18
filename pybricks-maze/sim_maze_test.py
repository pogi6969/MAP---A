# offline check of the maze logic with fake robot/sensors on a random 6x6 maze
import random, sys, types
src = open(sys.argv[1]).read()
src = src.split('# ---------------- MAIN ----------------')[0]
for mod in ('pybricks', 'pybricks.hubs', 'pybricks.pupdevices', 'pybricks.parameters', 'pybricks.robotics', 'pybricks.tools'):
    sys.modules[mod] = types.ModuleType(mod)
class Any:
    def __init__(self, *a, **k): pass
    def __getattr__(self, n): return Any()
    def __call__(self, *a, **k): return Any()
for mod, names in (('pybricks.hubs', ['PrimeHub']), ('pybricks.pupdevices', ['Motor', 'UltrasonicSensor']), ('pybricks.parameters', ['Port', 'Direction', 'Color', 'Icon']),
                   ('pybricks.robotics', ['DriveBase']), ('pybricks.tools', ['wait'])):
    for n in names: setattr(sys.modules[mod], n, Any())
g = {}; exec(src, g)
W, H = g['MAZE_W'], g['MAZE_H']
# random perfect maze (DFS) + a few loops
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
real = [[15] * H for _ in range(W)]
def carve(x, y, d):
    real[x][y] &= ~(1 << d); real[x + g['DX'][d]][y + g['DY'][d]] &= ~(1 << ((d + 2) % 4))
st = [(0, 0)]; vis = {(0, 0)}
while st:
    x, y = st[-1]; opts = [d for d in range(4) if 0 <= x + g['DX'][d] < W and 0 <= y + g['DY'][d] < H and (x + g['DX'][d], y + g['DY'][d]) not in vis]
    if not opts: st.pop(); continue
    d = random.choice(opts); carve(x, y, d); vis.add((x + g['DX'][d], y + g['DY'][d])); st.append((x + g['DX'][d], y + g['DY'][d]))
state = {'x': 0, 'y': 0, 'h': 0, 'moves': 0}
def wall(d): return real[state['x']][state['y']] & (1 << d)
class Eye:
    def __init__(s, off): s.off = off
    def distance(s): return 50 if wall((state['h'] + s.off) % 4) else 2000
g['left'], g['front'], g['right'] = Eye(3), Eye(0), Eye(1)
def turn_to(h, d): state['h'] = d; return d
def drive_cells(n, speed):
    for _ in range(n):
        assert not wall(state['h']), 'drove into a wall!'
        state['x'] += g['DX'][state['h']]; state['y'] += g['DY'][state['h']]; state['moves'] += 1
g['turn_to'], g['drive_cells'] = turn_to, drive_cells
x, y, h = g['explore'](0, 0, 0, g['GOALS'], None); m1 = state['moves']
x, y, h = g['explore'](x, y, h, [g['START']], None); m2 = state['moves'] - m1
h = turn_to(h, 0); state['moves'] = 0
x, y, h = g['speed_run'](x, y, h)
print('reached goal' if (x, y) in g['GOALS'] else 'FAILED', '| search cells', m1, '+ back', m2, '| speed run cells', state['moves'])
