"""Exact verifier for OBSTRUCTION witnesses (Erdos #23, family F2).

A *pattern* is a triangle-free graph H on h vertices, a 2-colouring col: V(H)->{0,1},
and part sizes n_0..n_{h-1}.  G = H[n_0,..,n_{h-1}] is the blow-up (triangle-free),
with the *blow-up cut* side(v) = col(part(v)).  Because consecutive parts induce
complete bipartite graphs, sigma(S) depends only on the profile s = (s_i), and

    sigma(s) = sum_{ij in E(H)} eps_ij * ( s_i(n_j - s_j) + s_j(n_i - s_i) ),
    eps_ij = +1 if col_i != col_j  (B-edge),  -1 if col_i == col_j  (M-edge).

Everything below is exact integer arithmetic; profiles are enumerated exhaustively.
"""
from itertools import product, combinations


class Pattern:
    def __init__(self, h, edges, col, sizes, name=""):
        self.h, self.edges, self.col, self.n, self.name = h, edges, col, list(sizes), name
        self.eps = {}
        self.adj = [set() for _ in range(h)]
        for (i, j) in edges:
            self.eps[(i, j)] = self.eps[(j, i)] = -1 if col[i] == col[j] else 1
            self.adj[i].add(j)
            self.adj[j].add(i)
        # triangle-freeness of H (hence of the blow-up)
        for (i, j) in edges:
            assert not (self.adj[i] & self.adj[j]), f"H has a triangle at {i},{j}"
        self.N = sum(self.n)
        self.M = sum(self.n[i] * self.n[j] for (i, j) in edges if col[i] == col[j])
        self.E = sum(self.n[i] * self.n[j] for (i, j) in edges)

    def sigma(self, s):
        t = 0
        for (i, j) in self.edges:
            t += self.eps[(i, j)] * (s[i] * (self.n[j] - s[j]) + s[j] * (self.n[i] - s[i]))
        return t

    def sigma_vertex(self, i):
        """sigma(v) for a single vertex v in part i."""
        return sum(self.eps[(i, j)] * self.n[j] for j in self.adj[i])

    # ---------- exhaustive scan over all profiles ----------
    def scan(self):
        best_neg = None                       # (size, profile, sigma)
        minsig = None
        tight = []
        for s in product(*[range(x + 1) for x in self.n]):
            v = self.sigma(s)
            if minsig is None or v < minsig[0]:
                minsig = (v, s)
            if v == 0:
                tight.append(s)
            if v < 0:
                sz = sum(s)
                if best_neg is None or sz < best_neg[0]:
                    best_neg = (sz, s, v)
        return best_neg, minsig, tight

    # ---------- named switch-set families ----------
    def family_profiles(self):
        """Yield (family name, profile) for every set in the classical local families.
        A profile here means: how many vertices are taken from each part."""
        h, n, adj, col = self.h, self.n, self.adj, self.col
        NB = [ {j for j in adj[i] if self.eps[(i, j)] == 1} for i in range(h) ]
        NM = [ {j for j in adj[i] if self.eps[(i, j)] == -1} for i in range(h) ]
        for i in range(h):
            if n[i] == 0:
                continue
            one = [0] * h; one[i] = 1
            yield ("vertex {v}", tuple(one))
            # full star {v} u N_B(v)
            s = list(one)
            for j in NB[i]:
                s[j] = n[j]
            yield ("star {v}uN_B(v)", tuple(s))
            # SHARP star: {v} u A for every A subset N_B(v)  (all profiles)
            for t in product(*[range(n[j] + 1) for j in sorted(NB[i])]):
                s = list(one)
                for idx, j in enumerate(sorted(NB[i])):
                    s[j] = t[idx]
                yield ("sharp star {v}uA, A<=N_B(v)", tuple(s))
            # closed neighbourhood N[v] and open N(v)
            s = list(one)
            for j in adj[i]:
                s[j] = n[j]
            yield ("closed nbhd N[v]", tuple(s))
            s2 = [0] * h
            for j in adj[i]:
                s2[j] = n[j]
            yield ("open nbhd N(v)", tuple(s2))
            # ball of radius 2
            s = list(one)
            for j in adj[i]:
                s[j] = n[j]
                for k in adj[j]:
                    s[k] = n[k]
            yield ("ball B(v,2)", tuple(s))
            # {v} u N_B(v) u N_M(v) variants already covered by N[v]
        # neighbourhood of an edge  N[u] u N[v]
        for (i, j) in self.edges:
            if n[i] == 0 or n[j] == 0:
                continue
            s = [0] * h
            s[i] = 1; s[j] = 1
            for k in adj[i]:
                s[k] = n[k]
            for k in adj[j]:
                s[k] = n[k]
            s[i] = max(s[i], 1); s[j] = max(s[j], 1)
            yield ("edge nbhd N[u]uN[v]", tuple(s))
        # independent sets:  any profile supported on an independent set of H
        for r in range(1, h + 1):
            for T in combinations(range(h), r):
                if any((a in adj[b]) for a in T for b in T):
                    continue
                for t in product(*[range(n[i] + 1) for i in T]):
                    s = [0] * h
                    for idx, i in enumerate(T):
                        s[i] = t[idx]
                    yield ("independent set", tuple(s))
        # C5-shaped sets: one vertex from each part of an induced 5-cycle of H
        for cyc in combinations(range(h), 5):
            for perm in _cycles5(cyc):
                ok = all(perm[(k + 1) % 5] in adj[perm[k]] for k in range(5))
                if ok:
                    s = [0] * h
                    for i in perm:
                        s[i] = 1
                    yield ("C5-shaped", tuple(s))
        # single parts and unions of parts of size <= 1
        for i in range(h):
            s = [0] * h; s[i] = n[i]
            yield ("one whole part", tuple(s))

    def report(self, size_scan=True):
        n, N = self.n, self.N
        print(f"--- {self.name}  parts={n}  N={N}  |E|={self.E}  |M|={self.M}")
        print(f"    N^2/25 = {N*N}/25 = {N*N/25:.4f}   |M| - N^2/25 = {self.M} - {N*N/25:.4f}"
              f" = {self.M - N*N/25:+.4f}   ratio |M|/N^2 = {self.M}/{N*N} = {self.M/N**2:.6f}")
        print(f"    exact rational test 25*|M| > N^2 :  25*{self.M} = {25*self.M}  vs  N^2 = {N*N}"
              f"   ->  {'BEATS N^2/25' if 25*self.M > N*N else 'does not beat N^2/25'}")
        for i in range(self.h):
            if n[i]:
                print(f"    part {i}: size {n[i]}, colour {self.col[i]}, sigma(v) = {self.sigma_vertex(i)}")
        # families
        fails = {}
        tightf = {}
        for name, s in self.family_profiles():
            v = self.sigma(s)
            if v < 0:
                fails.setdefault(name, []).append((s, v))
            elif v == 0:
                tightf[name] = tightf.get(name, 0) + 1
        print("    named switch families:")
        seen = set()
        for name, s in self.family_profiles():
            if name in seen:
                continue
            seen.add(name)
            f = fails.get(name)
            print(f"      {name:32s} : {'VIOLATED ' + str(f[:2]) if f else 'all sigma >= 0'}"
                  f"   (#tight = {tightf.get(name,0)})")
        if size_scan:
            neg, minsig, tight = self.scan()
            if neg is None:
                print("    NO switch set with sigma < 0: the cut is MAXIMUM (this is not a witness)")
            else:
                sz, prof, val = neg
                print(f"    smallest improving switch set: |S| = {sz} = {sz/N:.4f}*N   profile {prof}  sigma = {val}")
                print(f"    => sigma(S) >= 0 for EVERY S with |S| <= {sz-1} = {(sz-1)/N:.4f}*N")
            print(f"    min sigma over all profiles: {minsig[0]} at {minsig[1]};  #tight profiles = {len(tight)}")
        return self


def _cycles5(cyc):
    a = cyc[0]
    rest = list(cyc[1:])
    from itertools import permutations
    out = []
    for p in permutations(rest):
        out.append((a,) + p)
    return out


def P4(b, plus=1):
    """P4[b+plus, b, b, b+plus] with the cut  {P1,P4} | {P2,P3}."""
    return Pattern(4, [(0, 1), (1, 2), (2, 3)], [0, 1, 1, 0],
                   [b + plus, b, b, b + plus], name=f"W1(b={b}) = P4[{b+plus},{b},{b},{b+plus}]")


def C7w(b, d=1, plus=1):
    """C7[b+plus, d,d,d, b+plus, b, b] with colours 0,1,0,1,0,1,1  (M-pair = parts 5,6)."""
    a = b + plus
    edges = [(i, (i + 1) % 7) for i in range(7)]
    edges = [(min(x, y), max(x, y)) for (x, y) in edges]
    return Pattern(7, edges, [0, 1, 0, 1, 0, 1, 1], [a, d, d, d, a, b, b],
                   name=f"W2(b={b},d={d}) = C7[{a},{d},{d},{d},{a},{b},{b}] (connected, non-bipartite)")


if __name__ == "__main__":
    for b in (3, 4, 6, 8):
        P4(b).report()
        print()
    for b in (6, 8, 10):
        C7w(b).report()
        print()
