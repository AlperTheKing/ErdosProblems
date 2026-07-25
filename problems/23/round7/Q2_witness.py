"""Q2_witness.py -- exact dissection of any blow-up witness.

usage:  python Q2_witness.py PATFILE G6 COLSTR a0,a1,...   [--fam]
        python Q2_witness.py PATFILE G6 COLSTR a0,... --scale k1,k2,k3

Reports in exact integers: N,|E|,|M|,sigma, 25|M|-N^2, every improving
part-subset, which structured families catch one, and the exact minimum
improving switch size.
"""
import sys
from itertools import product, combinations
from fractions import Fraction as Fr


def load(patfile):
    pats = {}
    lines = open(patfile).read().split("\n")
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1; continue
        h, g6 = lines[i].split()
        h = int(h)
        adj = [[int(c) for c in lines[i + 1 + r].strip()] for r in range(h)]
        pats[g6] = (h, adj)
        i += 1 + h
    return pats


class Cfg:
    def __init__(self, h, adjm, col, a):
        self.h, self.col, self.a = h, list(col), list(a)
        self.adj = [set(j for j in range(h) if adjm[i][j]) for i in range(h)]
        self.edges = [(i, j) for i in range(h) for j in range(i + 1, h) if adjm[i][j]]

    def sigma(self):
        return [sum(self.a[j] if self.col[j] != self.col[i] else -self.a[j]
                    for j in self.adj[i]) for i in range(self.h)]

    def mono(self):
        return sum(self.a[i] * self.a[j] for i, j in self.edges if self.col[i] == self.col[j])

    def nedges(self):
        return sum(self.a[i] * self.a[j] for i, j in self.edges)

    def delta(self, s):
        sg = self.sigma()
        v = -sum(s[i] * sg[i] for i in range(self.h))
        for i, j in self.edges:
            v += (-2 if self.col[i] == self.col[j] else 2) * s[i] * s[j]
        return v

    def switchstar(self):
        sg = self.sigma()
        out = []
        for i in range(self.h):
            if self.a[i] == 0:
                continue
            rhs = sum(self.a[j] * (2 - sg[j]) for j in self.adj[i]
                      if self.col[j] != self.col[i] and self.a[j] > 0 and sg[j] <= 1)
            out.append((i, sg[i], rhs, sg[i] - rhs))
        return out

    def indep(self, allowed):
        res = []
        for r in range(len(allowed) + 1):
            for J in combinations(sorted(allowed), r):
                if all(y not in self.adj[x] for x, y in combinations(J, 2)):
                    res.append(frozenset(J))
        return res

    def families(self):
        h = self.h
        star, sup, nbru, pair = set(), set(), set(), set()
        for i in range(h):
            Nv = frozenset(self.adj[i])
            rest = [j for j in range(h) if j not in Nv]
            for J in self.indep(rest):
                S = Nv | J
                if 0 < len(S) < h:
                    star.add(S)
            for r in range(len(rest) + 1):
                for J in combinations(rest, r):
                    S = Nv | frozenset(J)
                    if 0 < len(S) < h:
                        sup.add(S)
        for r in range(1, h + 1):
            for vs in combinations(range(h), r):
                S = frozenset().union(*[self.adj[v] for v in vs])
                if 0 < len(S) < h:
                    nbru.add(S)
        for i, j in self.edges:
            S = frozenset(self.adj[i]) | frozenset(self.adj[j])
            if 0 < len(S) < h:
                pair.add(S)
        return dict(STAR=star, SUP=sup, NBRU=nbru, PAIRNBR=pair)


def report(cfg, tag):
    h = cfg.h
    N, E, M, sg = sum(cfg.a), cfg.nedges(), cfg.mono(), cfg.sigma()
    print(f"\n### {tag}: a={cfg.a} col={''.join(map(str,cfg.col))} N={N} |E|={E} |M|={M} sigma={sg}")
    print(f"    25|M|={25*M}  N^2={N*N}  25|M|-N^2={25*M-N*N}  |M|/N^2={Fr(M,N*N)}"
          f" = {float(Fr(M,N*N)):.6f} = 1/{float(N*N)/M:.4f}")
    neg = [i for i in range(h) if cfg.a[i] > 0 and sg[i] < 0]
    print(f"    sigma>=0 on the support: {'YES' if not neg else 'NO at parts '+str(neg)}")
    for i, s, rhs, sl in cfg.switchstar():
        print(f"      part{i}: sigma={s:5d} >= {rhs:5d}  slack {sl:5d}  {'TIGHT' if sl == 0 else ('VIOLATED' if sl < 0 else '')}")
    imp = []
    for m in range(1, (1 << h) - 1):
        S = frozenset(i for i in range(h) if (m >> i) & 1)
        s = [cfg.a[i] if i in S else 0 for i in range(h)]
        d = cfg.delta(s)
        if d > 0:
            imp.append((d, S, sum(s)))
    imp.sort(key=lambda t: -t[0])
    print(f"    improving part-subsets: {len(imp)}")
    for d, S, sz in imp[:14]:
        print(f"      S={sorted(S)} |S|={sz}={Fr(sz,N)}N Delta={d}")
    impS = set(S for _, S, _ in imp)
    for name, fam in cfg.families().items():
        hit = sorted(sorted(S) for S in impS & fam)
        print(f"    family {name}: catches {len(hit)} improving set(s) {hit[:6]}")
    best = None
    if all(x <= 30 for x in cfg.a):
        for s in product(*[range(x + 1) for x in cfg.a]):
            d = cfg.delta(list(s))
            if d > 0 and (best is None or sum(s) < best[0]):
                best = (sum(s), s, d)
        if best:
            print(f"    MIN improving switch |S|={best[0]}={Fr(best[0],N)}N"
                  f" ({float(Fr(best[0],N)):.4f}) s={best[1]} Delta={best[2]}")


if __name__ == "__main__":
    pats = load(sys.argv[1])
    g6 = sys.argv[2]
    h, adjm = pats[g6]
    col = [int(c) for c in sys.argv[3][:h]]
    a = [int(x) for x in sys.argv[4].split(",")][:h]
    report(Cfg(h, adjm, col, a), f"{g6} col={sys.argv[3][:h]}")
    if len(sys.argv) > 5 and sys.argv[5] == "--scale":
        base = a
        g = 0
        for k in [int(x) for x in sys.argv[6].split(",")]:
            report(Cfg(h, adjm, col, [x * k for x in base]), f"{g6} scaled x{k}")
