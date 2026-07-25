"""audit_G10_lib.py -- INDEPENDENT re-implementation of the primitives needed to audit
round3/G10.md.  Written from scratch (different data structures from G10_core.py):
graphs are stored as frozenset-of-frozenset edge sets + integer adjacency lists,
cuts are enumerated as subsets of V\\{0} via integer masks, psi/bip are exact
(Fraction / int).  No import of any G10_* module anywhere.
"""
from fractions import Fraction
from itertools import combinations, product


# ---------------------------------------------------------------- graph6 (own decoder)
def g6(s):
    """graph6 string -> (n, edgeset as sorted list of tuples).  Own bit walk."""
    s = s.strip()
    v = [ord(c) - 63 for c in s]
    if v[0] < 63:
        n, body = v[0], v[1:]
    elif v[1] != 63:
        n, body = (v[1] << 12) + (v[2] << 6) + v[3], v[4:]
    else:
        n, body = (v[2] << 30) + (v[3] << 24) + (v[4] << 18) + (v[5] << 12) + (v[6] << 6) + v[7], v[8:]
    # bit stream, column-major upper triangle: pairs (i,j) with i<j ordered by j then i
    need = n * (n - 1) // 2
    bitstr = []
    for byte in body:
        bitstr.extend((byte >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    bitstr = bitstr[:need]
    E = []
    p = 0
    for j in range(n):
        for i in range(j):
            if bitstr[p]:
                E.append((i, j))
            p += 1
    return n, E


def adjlist(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def adjmask(n, E):
    A = [0] * n
    for u, v in E:
        A[u] |= 1 << v
        A[v] |= 1 << u
    return A


# ---------------------------------------------------------------- structure tests
def triangles(n, E):
    """Return a triangle if one exists else None (independent of adjacency-mask tricks)."""
    A = adjlist(n, E)
    for u, v in E:
        common = A[u] & A[v]
        if common:
            return (u, v, min(common))
    return None


def is_tf(n, E):
    return triangles(n, E) is None


def is_maximal_tf(n, E):
    if not is_tf(n, E):
        return False
    A = adjlist(n, E)
    for i in range(n):
        for j in range(i + 1, n):
            if j in A[i]:
                continue
            if not (A[i] & A[j]):
                return False
    return True


def odd_girth(n, E):
    """Length of a shortest odd cycle (BFS from each vertex on the bipartite double
    cover distance argument), or None if bipartite.  Independent implementation."""
    A = adjlist(n, E)
    best = None
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = [s]
        while q:
            nq = []
            for u in q:
                for w in A[u]:
                    if dist[w] < 0:
                        dist[w] = dist[u] + 1
                        nq.append(w)
                    elif dist[w] == dist[u]:      # odd closed walk of length 2d+1
                        c = dist[u] + dist[w] + 1
                        if best is None or c < best:
                            best = c
            q = nq
    return best


def hom_to_C5(n, E):
    """Is there a homomorphism to C5?  Independent method: exhaustive DFS in NATURAL
    vertex order with forward checking over the 5 colours, one component at a time,
    fixing the first vertex of each component to colour 0 (C5 is vertex-transitive)."""
    A = adjlist(n, E)
    nb = [{(c + 1) % 5, (c - 1) % 5} for c in range(5)]
    col = [-1] * n

    comps = []
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        comp, stack = [], [s]
        seen[s] = True
        while stack:
            u = stack.pop()
            comp.append(u)
            for w in A[u]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)
        comps.append(comp)

    def solve(order, k):
        if k == len(order):
            return True
        v = order[k]
        allowed = {0, 1, 2, 3, 4} if k else {0}
        for u in A[v]:
            if col[u] >= 0:
                allowed &= nb[col[u]]
        for c in sorted(allowed):
            col[v] = c
            if solve(order, k + 1):
                return True
            col[v] = -1
        return False

    for comp in comps:
        # BFS order inside the component so every vertex after the first has a coloured nb
        root = comp[0]
        order, seen2 = [root], {root}
        qq = [root]
        while qq:
            u = qq.pop(0)
            for w in sorted(A[u]):
                if w not in seen2:
                    seen2.add(w)
                    order.append(w)
                    qq.append(w)
        if not solve(order, 0):
            return False
    return True


def hom_to_C5_bruteforce(n, E):
    """Total brute force over all 5^n colourings (n <= 8 only) -- third opinion."""
    for col in product(range(5), repeat=n):
        if all((col[u] - col[v]) % 5 in (1, 4) for u, v in E):
            return True
    return False


# ---------------------------------------------------------------- cuts / psi / bip
def cut_mono(n, E):
    """For every one of the 2^(n-1) cuts (vertex 0 pinned to side 0), the list of
    monochromatic edges.  Own enumeration order."""
    out = []
    for m in range(1 << (n - 1)):
        side = [0] + [(m >> (v - 1)) & 1 for v in range(1, n)]
        out.append([(u, v) for (u, v) in E if side[u] == side[v]])
    return out


def bip_int(mono, a):
    """min over cuts of sum of a_u a_v over monochromatic edges -- exact integers."""
    return min(sum(a[u] * a[v] for (u, v) in mo) for mo in mono)


def psi_frac(mono, x):
    return min(sum(x[u] * x[v] for (u, v) in mo) for mo in mono)


def bip_graph(n, E):
    return min(len(mo) for mo in cut_mono(n, E))


# ---------------------------------------------------------------- some named graphs
def C(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def petersen():
    E = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + \
        [(5 + i, 5 + ((i + 2) % 5)) for i in range(5)]
    return 10, sorted((min(u, v), max(u, v)) for u, v in E)


def wagner():
    """V8 = Moebius ladder on 8 vertices = C8(1,4)."""
    E = set()
    for i in range(8):
        for c in (1, 4):
            j = (i + c) % 8
            if i != j:
                E.add((min(i, j), max(i, j)))
    return 8, sorted(E)


def disjoint(g1, g2):
    n1, E1 = g1
    n2, E2 = g2
    return n1 + n2, sorted(E1 + [(u + n1, v + n1) for u, v in E2])


if __name__ == '__main__':
    # self-tests against facts stated in the assignment (accepted facts 1,8)
    n, E = C(5)
    mo = cut_mono(n, E)
    assert psi_frac(mo, [Fraction(1, 5)] * 5) == Fraction(1, 25)
    assert bip_graph(*C(5)) == 1
    assert bip_graph(*petersen()) == 3
    assert is_tf(*petersen()) and is_maximal_tf(*petersen())
    assert is_tf(*wagner()) and is_maximal_tf(*wagner())
    assert odd_girth(*C(7)) == 7 and odd_girth(*petersen()) == 5 and odd_girth(*wagner()) == 5
    assert hom_to_C5(*C(5)) and not hom_to_C5(*wagner())
    assert hom_to_C5_bruteforce(*C(5)) and not hom_to_C5_bruteforce(*wagner())
    assert hom_to_C5(*C(7)) is True   # C7 -> C5 DOES exist (odd cycle, 7 >= 5)
    print('AUDIT LIB OK  bip(C5)=1 bip(Petersen)=3 oddgirth(V8)=5 hom(V8->C5)=False')
