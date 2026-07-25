"""audit_Q3_named.py -- independent construction of the calibration graphs, own graph6 encoder.
Emits "<g6>\t<label>" lines.  Pure integer arithmetic.
"""
import sys

def g6enc(n, E):
    adj = [[0]*n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = 1
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(adj[i][j])
    while len(bits) % 6:
        bits.append(0)
    out = chr(n+63)
    for k in range(0, len(bits), 6):
        x = 0
        for b in bits[k:k+6]:
            x = (x << 1) | b
        out += chr(x+63)
    return out

def g6dec(s):
    s = s.strip()
    b = [ord(c)-63 for c in s]
    n = b[0]; p = 1
    if n == 63:
        n = (b[1] << 12) | (b[2] << 6) | b[3]; p = 4
    E = []; idx = 0
    for j in range(1, n):
        for i in range(j):
            byte, bit = divmod(idx, 6)
            if p+byte < len(b) and (b[p+byte] >> (5-bit)) & 1:
                E.append((i, j))
            idx += 1
    return n, E

def c5blowup(sizes):
    n = sum(sizes)
    off = []; a = 0
    for s in sizes:
        off.append(a); a += s
    E = []
    for i in range(5):
        j = (i+1) % 5
        for x in range(sizes[i]):
            for y in range(sizes[j]):
                E.append((off[i]+x, off[j]+y))
    return n, E

def prism():
    E = []
    for j in range(5):
        E.append((j, (j+1) % 5))
        E.append((5+j, 5+(j+1) % 5))
        E.append((j, 5+j))
    return 10, E

def petersen():
    E = []
    for j in range(5):
        E.append((j, (j+1) % 5))
        E.append((5+j, 5+(j+2) % 5))
        E.append((j, 5+j))
    return 10, E

def circulant(n, S):
    E = []
    for u in range(n):
        for s in S:
            v = (u+s) % n
            if u < v:
                E.append((u, v))
            elif v < u:
                E.append((v, u))
    return n, sorted(set(E))

def circle_graph(m):
    """Gamma_m: u~v iff circular distance*3 > m  (accepted base (8) convention)."""
    E = []
    for u in range(m):
        for v in range(u+1, m):
            d = min((u-v) % m, (v-u) % m)
            if 3*d > m:
                E.append((u, v))
    return m, E

def grotzsch():
    # Mycielski of C5: 0..4 cycle, 5..9 shadows, 10 apex
    E = []
    for j in range(5):
        E.append((j, (j+1) % 5))
    for j in range(5):
        E.append((5+j, (j+1) % 5))
        E.append((5+j, (j-1) % 5))
        E.append((5+j, 10))
    return 11, sorted((min(a, b), max(a, b)) for a, b in E)

def clebsch():
    # halved 5-cube: vertices = even-weight subsets of {0..4}, adjacent iff Hamming distance 4
    verts = [v for v in range(32) if bin(v).count('1') % 2 == 0]
    idx = {v: i for i, v in enumerate(verts)}
    E = []
    for a in verts:
        for b in verts:
            if a < b and bin(a ^ b).count('1') == 4:
                E.append((idx[a], idx[b]))
    return 16, E

def prism_blowup(t):
    n, E = prism()
    return blowup(n, E, t)

def blowup(n, E, t):
    N = n*t
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                x, y = u*t+a, v*t+b
                EE.append((min(x, y), max(x, y)))
    return N, sorted(set(EE))

NAMED = {}
NAMED['C5'] = c5blowup([1]*5)
NAMED['C5[2]'] = c5blowup([2]*5)
NAMED['C5[3]'] = c5blowup([3]*5)
NAMED['C5[4]'] = c5blowup([4]*5)
NAMED['prism'] = prism()
NAMED['petersen'] = petersen()
NAMED['petersen[2]'] = blowup(*petersen(), 2)
NAMED['grotzsch'] = grotzsch()
NAMED['clebsch'] = clebsch()
NAMED['C13(1,5)'] = circulant(13, [1, 5])
NAMED['C13(2,3)'] = circulant(13, [2, 3])
for m in (8, 10, 11, 12, 13, 14, 15, 16, 17):
    NAMED['Gamma%d' % m] = circle_graph(m)

if __name__ == '__main__':
    for k, (n, E) in NAMED.items():
        print("%s\t%s\t%d\t%d" % (g6enc(n, E), k, n, len(E)))
