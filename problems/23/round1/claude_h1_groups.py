"""H1: build Cayley tables for ALL groups of the target orders, dedupe up to isomorphism.

Representation: a group is (name, n, table) where table[i][j] = i*j, element 0 = identity.

Construction toolkit
  cyclic(n), direct(A,B), semidirect(A,B,phi), dihedral(m), dicyclic(m),
  from_perms(gens)  [closure of a permutation set -> regular Cayley table]

Completeness strategy (justified per order in claude_h1_cayley.md):
  * all abelian groups of order n  (partitions of prime exponents)      -- complete
  * A |x| B  for every hom phi: B -> Aut(A), A,B previously built       -- covers every split extension
  * dicyclic / generalized quaternion (the non-split cyclic-by-Z2 ones)
  * explicit exceptional groups (S4, A4, SL(2,3), GL(2,3), 2O, ...)
Counts are checked against the known number of groups of each order.

Usage:  python claude_h1_groups.py OUTDIR n1 n2 ...
Writes  OUTDIR/groups_<n>.txt :  first line "<count> <n>", then per group a name line and n lines of n ints.
"""
import sys, os, itertools
from functools import lru_cache

# ---------------------------------------------------------------- basic constructions

def cyclic(n):
    return ("Z%d" % n, n, [[(i + j) % n for j in range(n)] for i in range(n)])


def direct(A, B):
    (na, ta), (nb, tb) = (A[1], A[2]), (B[1], B[2])
    n = na * nb
    idx = lambda a, b: a * nb + b
    T = [[0] * n for _ in range(n)]
    for a1 in range(na):
        for b1 in range(nb):
            for a2 in range(na):
                for b2 in range(nb):
                    T[idx(a1, b1)][idx(a2, b2)] = idx(ta[a1][a2], tb[b1][b2])
    return ("(%s x %s)" % (A[0], B[0]), n, T)


def semidirect(A, B, phi, name=None):
    """A |x|_phi B ; phi[b] is an automorphism of A given as a list (image of each elt).
    Element (a,b) -> a*nb+b.  (a1,b1)(a2,b2) = (a1 * phi[b1](a2), b1 b2)."""
    na, ta = A[1], A[2]
    nb, tb = B[1], B[2]
    n = na * nb
    idx = lambda a, b: a * nb + b
    T = [[0] * n for _ in range(n)]
    for b1 in range(nb):
        p = phi[b1]
        for a1 in range(na):
            r = T[idx(a1, b1)]
            for a2 in range(na):
                x = ta[a1][p[a2]]
                for b2 in range(nb):
                    r[idx(a2, b2)] = idx(x, tb[b1][b2])
    return (name or ("%s:%s" % (A[0], B[0])), n, T)


def dihedral(m):
    """order 2m: (i,e) with (i,0)=r^i, (i,1)=r^i s."""
    n = 2 * m
    idx = lambda i, e: i * 2 + e
    T = [[0] * n for _ in range(n)]
    for i in range(m):
        for e in range(2):
            for j in range(m):
                for f in range(2):
                    if e == 0:
                        T[idx(i, e)][idx(j, f)] = idx((i + j) % m, f)
                    else:
                        T[idx(i, e)][idx(j, f)] = idx((i - j) % m, (1 + f) % 2)
    return ("D%d" % n, n, T)


def dicyclic(m):
    """Dic_m, order 4m: a^{2m}=1, b^2=a^m, b a b^-1 = a^-1.  elt a^i b^e."""
    n = 4 * m
    M = 2 * m
    idx = lambda i, e: i * 2 + e
    T = [[0] * n for _ in range(n)]
    for i in range(M):
        for e in range(2):
            for j in range(M):
                for f in range(2):
                    if e == 0:
                        T[idx(i, e)][idx(j, f)] = idx((i + j) % M, f)
                    else:
                        if f == 0:
                            T[idx(i, e)][idx(j, f)] = idx((i - j) % M, 1)
                        else:
                            T[idx(i, e)][idx(j, f)] = idx((i - j + m) % M, 0)
    return ("Dic%d" % m, n, T)


def from_perms(gens, name):
    """Close a set of permutations (tuples) under composition; return Cayley table."""
    deg = len(gens[0])
    ident = tuple(range(deg))
    elems = {ident: 0}
    order = [ident]
    frontier = [ident]
    comp = lambda p, q: tuple(p[q[i]] for i in range(deg))   # (p*q)(i) = p(q(i))
    while frontier:
        nf = []
        for p in frontier:
            for g in gens:
                r = comp(p, g)
                if r not in elems:
                    elems[r] = len(order)
                    order.append(r)
                    nf.append(r)
        frontier = nf
    n = len(order)
    T = [[elems[comp(order[i], order[j])] for j in range(n)] for i in range(n)]
    return (name, n, T)


# ---------------------------------------------------------------- group utilities

def inverses(G):
    n, T = G[1], G[2]
    inv = [0] * n
    for i in range(n):
        for j in range(n):
            if T[i][j] == 0:
                inv[i] = j
                break
    return inv


def elem_orders(G):
    n, T = G[1], G[2]
    o = [0] * n
    for i in range(n):
        x, k = i, 1
        while x != 0:
            x = T[x][i]
            k += 1
        o[i] = k
    o[0] = 1
    return o


def subgroup_gen(G, gens):
    n, T = G[1], G[2]
    S = {0}
    fr = [0]
    while fr:
        nf = []
        for a in fr:
            for g in gens:
                b = T[a][g]
                if b not in S:
                    S.add(b)
                    nf.append(b)
        fr = nf
    return S


def gen_sequence(G):
    """greedy minimal-ish generating sequence"""
    n = G[1]
    seq, cur = [], {0}
    while len(cur) < n:
        best, bestsz = None, -1
        for g in range(n):
            if g in cur:
                continue
            sz = len(subgroup_gen(G, seq + [g]))
            if sz > bestsz:
                best, bestsz = g, sz
        seq.append(best)
        cur = subgroup_gen(G, seq)
    return seq


def _word_table(G, seq):
    """BFS: for each element, a word (list of generator indices) evaluating to it."""
    n, T = G[1], G[2]
    word = [None] * n
    word[0] = []
    fr = [0]
    while fr:
        nf = []
        for a in fr:
            for k, g in enumerate(seq):
                b = T[a][g]
                if word[b] is None:
                    word[b] = word[a] + [k]
                    nf.append(b)
        fr = nf
    return word


def _map_from_images(G, H, seq, imgs, words):
    """build phi: G->H with phi(seq[k]) = imgs[k]; return list or None if not a homomorphism."""
    nG, TG = G[1], G[2]
    nH, TH = H[1], H[2]
    if nG != nH:
        return None
    f = [0] * nG
    for a in range(nG):
        x = 0
        for k in words[a]:
            x = TH[x][imgs[k]]
        f[a] = x
    if len(set(f)) != nG:
        return None
    for a in range(nG):
        fa, Ta, TH_fa = f[a], TG[a], TH[f[a]]
        for b in range(nG):
            if f[Ta[b]] != TH_fa[f[b]]:
                return None
    return f


def automorphisms(G):
    """all automorphisms of G as permutation lists"""
    n = G[1]
    seq = gen_sequence(G)
    words = _word_table(G, seq)
    ords = elem_orders(G)
    res = []
    k = len(seq)
    # precompute subgroup closure sizes for pruning
    def rec(i, imgs, cursub):
        if i == k:
            f = _map_from_images(G, G, seq, imgs, words)
            if f is not None:
                res.append(f)
            return
        target_ord = ords[seq[i]]
        prev_size = len(subgroup_gen(G, seq[:i]))
        for h in range(n):
            if ords[h] != target_ord:
                continue
            if h in cursub:
                # seq[i] must not be in <seq[:i]> (greedy sequence is strictly increasing)
                continue
            ns = subgroup_gen(G, imgs + [h])
            if len(ns) != len(subgroup_gen(G, seq[:i + 1])):
                continue
            rec(i + 1, imgs + [h], ns)
    rec(0, [], {0})
    return res


def isomorphic(G, H):
    if G[1] != H[1]:
        return False
    if sorted(elem_orders(G)) != sorted(elem_orders(H)):
        return False
    n = G[1]
    seq = gen_sequence(G)
    words = _word_table(G, seq)
    ordsG, ordsH = elem_orders(G), elem_orders(H)
    k = len(seq)

    def rec(i, imgs):
        if i == k:
            return _map_from_images(G, H, seq, imgs, words) is not None
        tg = ordsG[seq[i]]
        want = len(subgroup_gen(G, seq[:i + 1]))
        for h in range(n):
            if ordsH[h] != tg:
                continue
            ns = subgroup_gen(H, imgs + [h])
            if len(ns) != want:
                continue
            if rec(i + 1, imgs + [h]):
                return True
        return False
    return rec(0, [])


def homs_to_aut(B, A, autA):
    """all homomorphisms B -> Aut(A); returns list of phi (phi[b] = automorphism list)."""
    nB, TB = B[1], B[2]
    seqB = gen_sequence(B)
    wordsB = _word_table(B, seqB)
    nA = A[1]
    ident = list(range(nA))
    autset = {tuple(a): i for i, a in enumerate(autA)}
    ordsB = elem_orders(B)
    # order of an automorphism
    def aut_order(p):
        x, k = p, 1
        while x != ident:
            x = [p[x[i]] for i in range(nA)]
            k += 1
        return k
    aord = [aut_order(a) for a in autA]
    res = []
    k = len(seqB)

    def compose(p, q):
        return [p[q[i]] for i in range(nA)]

    def rec(i, imgs):
        if i == k:
            phi = []
            ok = True
            for b in range(nB):
                x = ident
                for t in wordsB[b]:
                    x = compose(x, imgs[t])
                phi.append(x)
            # verify homomorphism
            for a in range(nB):
                for b in range(nB):
                    if phi[TB[a][b]] != compose(phi[a], phi[b]):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                res.append(phi)
            return
        for j, a in enumerate(autA):
            if ordsB[seqB[i]] % aord[j] != 0:
                continue
            rec(i + 1, imgs + [a])
    rec(0, [])
    return res


# ---------------------------------------------------------------- abelian groups

def abelian_groups(n):
    """all abelian groups of order n"""
    if n == 1:
        return [("Z1", 1, [[0]])]
    # factor
    f, m = {}, n
    d = 2
    while d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1:
        f[m] = f.get(m, 0) + 1

    def partitions(k):
        if k == 0:
            yield []
            return
        for first in range(k, 0, -1):
            for rest in partitions(k - first):
                if not rest or rest[0] <= first:
                    yield [first] + rest

    per_prime = []
    for p, e in sorted(f.items()):
        per_prime.append([[p ** a for a in part] for part in partitions(e)])
    out = []
    for combo in itertools.product(*per_prime):
        cycs = [c for grp in combo for c in grp]
        G = cyclic(cycs[0])
        for c in cycs[1:]:
            G = direct(G, cyclic(c))
        G = (("Z" + " x Z".join(str(c) for c in cycs)), G[1], G[2])
        out.append(G)
    return out


# ---------------------------------------------------------------- exceptional groups

def perm(*cycles_deg):
    deg = cycles_deg[-1]
    cycles = cycles_deg[:-1]
    p = list(range(deg))
    for cyc in cycles:
        for i in range(len(cyc)):
            p[cyc[i]] = cyc[(i + 1) % len(cyc)]
    return tuple(p)


def S4():
    return from_perms([perm((0, 1), 4), perm((0, 1, 2, 3), 4)], "S4")


def A4():
    return from_perms([perm((0, 1, 2), 4), perm((0, 1), (2, 3), 4)], "A4")


def _matgroup(mats, mod, name):
    """closure of 2x2 matrices mod m under multiplication -> Cayley table"""
    def mul(a, b):
        return ((a[0] * b[0] + a[1] * b[2]) % mod, (a[0] * b[1] + a[1] * b[3]) % mod,
                (a[2] * b[0] + a[3] * b[2]) % mod, (a[2] * b[1] + a[3] * b[3]) % mod)
    ident = (1, 0, 0, 1)
    elems = {ident: 0}
    order = [ident]
    fr = [ident]
    while fr:
        nf = []
        for x in fr:
            for g in mats:
                y = mul(x, g)
                if y not in elems:
                    elems[y] = len(order)
                    order.append(y)
                    nf.append(y)
        fr = nf
    n = len(order)
    T = [[elems[mul(order[i], order[j])] for j in range(n)] for i in range(n)]
    return (name, n, T)


def SL23():
    return _matgroup([(1, 1, 0, 1), (0, 1, 2, 0)], 3, "SL(2,3)")


def GL23():
    return _matgroup([(1, 1, 0, 1), (0, 1, 2, 0), (2, 0, 0, 1)], 3, "GL(2,3)")


def binary_octahedral():
    """2O, order 48: SL(2,3) extended -- use the 48-elt subgroup of SL(2,9)?  Use quaternions."""
    # 2O = <SL(2,3), w> inside unit quaternions.  Build as permutation group on 48 points
    # via the regular action generated by SL(2,3) and the extra element; easier: use
    # SL(2,3) semidirect nothing.  Instead realise 2O as the group generated by the
    # matrices of SL(2,3) plus the 'octahedral' element in SL(2,9).
    mod = 9
    def mul(a, b):
        return ((a[0] * b[0] + a[1] * b[2]) % mod, (a[0] * b[1] + a[1] * b[3]) % mod,
                (a[2] * b[0] + a[3] * b[2]) % mod, (a[2] * b[1] + a[3] * b[3]) % mod)
    # generators of a 2O inside SL(2,9): standard 48-element subgroup
    gens = [(1, 1, 0, 1), (0, 1, 8, 0), (2, 0, 0, 5)]
    ident = (1, 0, 0, 1)
    elems = {ident: 0}
    order = [ident]
    fr = [ident]
    while fr:
        nf = []
        for x in fr:
            for g in gens:
                y = mul(x, g)
                if y not in elems:
                    elems[y] = len(order)
                    order.append(y)
                    nf.append(y)
        fr = nf
    n = len(order)
    T = [[elems[mul(order[i], order[j])] for j in range(n)] for i in range(n)]
    return ("2O?", n, T)


# ---------------------------------------------------------------- pool builder

KNOWN_COUNT = {1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 6: 2, 7: 1, 8: 5, 9: 2, 10: 2, 11: 1, 12: 5,
               13: 1, 14: 2, 15: 1, 16: 14, 17: 1, 18: 5, 19: 1, 20: 5, 21: 2, 22: 2,
               23: 1, 24: 15, 25: 2, 26: 2, 27: 5, 28: 4, 29: 1, 30: 4, 32: 51,
               36: 14, 48: 52, 49: 2, 50: 5, 51: 1, 52: 5, 54: 15, 74: 2, 76: 4,
               99: 2, 101: 1, 124: 4, 126: 16, 149: 1, 151: 1, 174: 4, 176: 42, 199: 1}


def invariant(G):
    """cheap isomorphism invariant: element orders, conjugacy class sizes,
    centre, derived subgroup (order + element orders)."""
    n, T = G[1], G[2]
    inv = inverses(G)
    ords = elem_orders(G)
    # conjugacy classes
    seen = [False] * n
    csizes = []
    for x in range(n):
        if seen[x]:
            continue
        cls = set()
        for g in range(n):
            cls.add(T[T[g][x]][inv[g]])
        for y in cls:
            seen[y] = True
        csizes.append(len(cls))
    centre = [x for x in range(n) if all(T[x][y] == T[y][x] for y in range(n))]
    comms = set()
    for a in range(n):
        for b in range(n):
            comms.add(T[T[inv[a]][inv[b]]][T[a][b]])
    D = subgroup_gen(G, sorted(comms))
    return (tuple(sorted(ords)), tuple(sorted(csizes)), len(centre),
            tuple(sorted(ords[x] for x in centre)), len(D),
            tuple(sorted(ords[x] for x in D)))


def dedupe(groups):
    buckets = {}
    for G in groups:
        buckets.setdefault(invariant(G), []).append(G)
    out = []
    for key, gs in buckets.items():
        reps = []
        for G in gs:
            if not any(isomorphic(G, H) for H in reps):
                reps.append(G)
        out += reps
    return out


def build_pool(orders, verbose=True):
    """build all groups of every order in `orders` plus every divisor needed."""
    need = set()
    for n in orders:
        for d in range(1, n + 1):
            if n % d == 0:
                need.add(d)
    pool = {}
    for n in sorted(need):
        cands = list(abelian_groups(n))
        if n % 2 == 0 and n >= 6:
            cands.append(dihedral(n // 2))
        if n % 4 == 0 and n >= 8:
            cands.append(dicyclic(n // 4))
        # split extensions A |x| B with |A||B| = n, A,B already built, |A|>1,|B|>1
        for a in sorted(need):
            if a <= 1 or n % a or a == n:
                continue
            b = n // a
            if a not in pool or b not in pool:
                continue
            if a * b != n:
                continue
            for A in pool[a]:
                if A[1] > 20:
                    continue
                autA = automorphisms(A)
                for B in pool[b]:
                    if B[1] > 16:
                        continue
                    for phi in homs_to_aut(B, A, autA):
                        cands.append(semidirect(A, B, phi, "%s:%s" % (A[0], B[0])))
        if n == 24:
            cands += [S4(), SL23()]
        if n == 48:
            cands += [direct(S4(), cyclic(2)), direct(SL23(), cyclic(2)), GL23(),
                      direct(A4(), cyclic(4)), direct(A4(), cyclic(2)) if False else GL23(),
                      binary_octahedral()]
            cands = [c for c in cands if c[1] == 48]
        if n == 12:
            cands += [A4()]
        cands = [c for c in cands if c[1] == n]
        pool[n] = dedupe(cands)
        if verbose:
            k = KNOWN_COUNT.get(n)
            flag = "" if k is None else (" OK" if len(pool[n]) == k else "  <-- have %d / known %d" % (len(pool[n]), k))
            print("order %3d : %3d groups%s   %s" % (n, len(pool[n]), flag,
                  ", ".join(g[0] for g in pool[n])[:110]), flush=True)
    return pool


def write_groups(path, n, groups):
    with open(path, "w") as f:
        f.write("%d %d\n" % (len(groups), n))
        for name, m, T in groups:
            f.write(name.replace(" ", "") + "\n")
            for row in T:
                f.write(" ".join(map(str, row)) + "\n")


if __name__ == "__main__":
    outdir = sys.argv[1]
    orders = [int(x) for x in sys.argv[2:]]
    os.makedirs(outdir, exist_ok=True)
    pool = build_pool(orders)
    for n in orders:
        write_groups(os.path.join(outdir, "groups_%d.txt" % n), n, pool[n])
        print("wrote %s : %d groups of order %d" % (os.path.join(outdir, "groups_%d.txt" % n), len(pool[n]), n))


def binary_octahedral_exact():
    """2O (order 48): the 48 unit quaternions  +-1,+-i,+-j,+-k ; (+-1+-i+-j+-k)/2 ;
    (+-a+-b)/sqrt(2) for distinct a,b in {1,i,j,k}.  Built numerically and then verified
    exactly (Latin square + associativity) before use."""
    import math, itertools
    r = 1.0 / math.sqrt(2.0)
    els = []
    for k in range(4):
        for s in (1.0, -1.0):
            v = [0.0] * 4; v[k] = s; els.append(tuple(v))
    for s in itertools.product((0.5, -0.5), repeat=4):
        els.append(tuple(s))
    for a in range(4):
        for b in range(a + 1, 4):
            for sa in (r, -r):
                for sb in (r, -r):
                    v = [0.0] * 4; v[a] = sa; v[b] = sb; els.append(tuple(v))
    assert len(els) == 48, len(els)

    def qmul(x, y):
        a1, b1, c1, d1 = x; a2, b2, c2, d2 = y
        return (a1*a2 - b1*b2 - c1*c2 - d1*d2,
                a1*b2 + b1*a2 + c1*d2 - d1*c2,
                a1*c2 - b1*d2 + c1*a2 + d1*b2,
                a1*d2 + b1*c2 - c1*b2 + d1*a2)

    def find(v):
        for i, e in enumerate(els):
            if max(abs(v[t] - e[t]) for t in range(4)) < 1e-9:
                return i
        raise ValueError("product left the set")

    idx1 = find((1.0, 0.0, 0.0, 0.0))
    order = [els[idx1]] + [e for i, e in enumerate(els) if i != idx1]
    pos = {e: i for i, e in enumerate(order)}
    def find2(v):
        for i, e in enumerate(order):
            if max(abs(v[t] - e[t]) for t in range(4)) < 1e-9:
                return i
        raise ValueError("product left the set")
    T = [[find2(qmul(order[i], order[j])) for j in range(48)] for i in range(48)]
    # exact verification: identity, Latin square, associativity
    assert all(T[0][j] == j and T[j][0] == j for j in range(48))
    for i in range(48):
        assert sorted(T[i]) == list(range(48))
        assert sorted(T[j][i] for j in range(48)) == list(range(48))
    for a in range(48):
        for b in range(48):
            for c in range(48):
                assert T[T[a][b]][c] == T[a][T[b][c]]
    return ("2O", 48, T)
