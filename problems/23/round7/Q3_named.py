"""Q3 (round 7): emit graph6 strings for the named calibration graphs, plus weighted lines.

Usage:  python Q3_named.py            -> writes Q3_named.g6 and Q3_named_weighted.txt
All graphs here are triangle-free; the script checks that before writing.
"""
import sys
from itertools import combinations


def g6(n, edges):
    E = set()
    for (u, v) in edges:
        E.add((min(u, v), max(u, v)))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in E else 0)
    while len(bits) % 6:
        bits.append(0)
    s = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        s += chr(v + 63)
    return s


def is_tf(n, edges):
    E = set()
    for (u, v) in edges:
        E.add((min(u, v), max(u, v)))
    for (a, b, c) in combinations(range(n), 3):
        if (a, b) in E and (a, c) in E and (b, c) in E:
            return False
    return True


def cycle(n):
    return [(i, (i + 1) % n) for i in range(n)]


def circle_graph(m):
    """Gamma_m : m equally spaced points on R/Z, i ~ j iff circular distance > 1/3."""
    E = []
    for i in range(m):
        for j in range(i + 1, m):
            d = min((j - i) % m, (i - j) % m)
            if 3 * d > m:
                E.append((i, j))
    return m, E


def blowup(n, edges, parts):
    """C5[a] style blow-up of a pattern"""
    idx = []
    c = 0
    for p in parts:
        idx.append(list(range(c, c + p)))
        c += p
    E = []
    for (u, v) in edges:
        for a in idx[u]:
            for b in idx[v]:
                E.append((a, b))
    return c, E


def petersen():
    E = [(i, (i + 1) % 5) for i in range(5)]
    E += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    E += [(i, 5 + i) for i in range(5)]
    return 10, E


def grotzsch():
    # Mycielskian of C5: outer c0..c4, copies u0..u4, apex z
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((5 + i, 10))
    return 11, E


def clebsch():
    # halved 5-cube: vertices = even-weight subsets of {0..4}, adjacent iff symmetric difference size 4
    V = [s for s in range(32) if bin(s).count('1') % 2 == 0]
    idx = {v: i for i, v in enumerate(V)}
    E = []
    for a in V:
        for b in V:
            if a < b and bin(a ^ b).count('1') == 4:
                E.append((idx[a], idx[b]))
    return len(V), E


NAMED = {}
NAMED['C5'] = (5, cycle(5))
NAMED['C5[2]'] = blowup(5, cycle(5), [2, 2, 2, 2, 2])
NAMED['C5[3]'] = blowup(5, cycle(5), [3, 3, 3, 3, 3])
NAMED['C7'] = (7, cycle(7))
NAMED['Petersen'] = petersen()
NAMED['Grotzsch'] = grotzsch()
NAMED['Clebsch'] = clebsch()
for m in range(6, 18):
    NAMED['Gamma%d' % m] = circle_graph(m)

if __name__ == '__main__':
    out = []
    for name, (n, E) in NAMED.items():
        if n > 17:
            continue
        assert is_tf(n, E), name
        out.append('%s\t%s\t%d\t%d' % (g6(n, E), name, n, len(set((min(a, b), max(a, b)) for a, b in E))))
    with open('Q3_named.g6', 'w') as f:
        for line in out:
            f.write(line.split('\t')[0] + '\n')
    with open('Q3_named_index.txt', 'w') as f:
        for line in out:
            f.write(line + '\n')
    for line in out:
        print(line)
