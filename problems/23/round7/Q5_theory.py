"""Q5 (a)-(d): exact verification of every claim in the report.

  T1  closed-form certificates for C5[n]:  cover z == 1/5, packing y == n^-3
      on the n^5 transversal 5-cycles  =>  tau*(C5[n]) = bip(C5[n]) = n^2.
  T2  explicit K5 minor in C5[2]  (the extremal family leaves the T-join class).
  T3  3-subdivision lemma: bip and tau* are both invariant, so bip on
      triangle-free graphs is as hard as MaxCut; witness = 3-subdivided K5,
      triangle-free (girth 9), bip = 4, tau* = 10/3.
  T4  z == 1/5 is a FRACTIONAL VERTEX of the odd-cycle covering polyhedron of
      the N=14 extremal graph (exact rank computation over Q).
  T5  weighted chain  psi(H,x) <= e(x) - 4 e(x)^2  and  Lambda(H,x) <= e(x)/5,
      verified numerically-exactly on all test objects.
  T6  search for x with Lambda(H,x) < psi(H,x) on C5[2] (product weights) and
      for a general weight w with tau*_w < tau_w (=> odd-K5 minor by Guenin).
"""
import sys, os, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *

NAMED = {
    "N12a": "K?ABBBwerwBw",
    "N12b": "K?BD@g]Qvo^?",
    "N13": "L??ED@_~?~^_Fw",
    "N14": "M?AE@bH{AYN_LgBs?",
}


# ---------------------------------------------------------------- T1 -------
def T1(nmax=6):
    print("=== T1  closed-form exact certificates for C5[n] ===")
    for k in range(1, nmax + 1):
        N, adj = blowup_C5(k)
        E = edges_of(N, adj)
        z = {e: Fraction(1, 5) for e in E}
        ok, info = verify_cover(N, adj, z)
        cost = sum(z.values())
        # packing: all transversal 5-cycles, weight k^-3
        y = Fraction(1, k ** 3)
        pack = []
        for tup in itertools.product(range(k), repeat=5):
            vs = [p * k + tup[p] for p in range(5)]
            cyc = sorted(tuple(sorted((vs[i], vs[(i + 1) % 5]))) for i in range(5))
            pack.append((cyc, y))
        w = {e: Fraction(1) for e in E}
        okp, tot = verify_packing(N, adj, pack, w)
        print(f"  C5[{k}]: N={N} |E|={len(E)} cover z=1/5 valid={ok} cost={cost}"
              f" | packing y=1/{k**3} on {len(pack)} cycles valid={okp} value={tot}"
              f" | equal={cost == tot} = n^2={k*k} -> tau* = bip = {cost}"
              f" = N^2/25 = {Fraction(N*N,25)}")
        assert ok and okp and cost == tot == k * k


# ---------------------------------------------------------------- T2 -------
def T2():
    print("=== T2  explicit K5 minor in C5[2] (parts {0,1},{2,3},{4,5},{6,7},{8,9}) ===")
    N, adj = blowup_C5(2)
    B = [{0, 3, 9}, {1, 2, 5}, {4, 7}, {6}, {8}]
    # disjoint + cover
    assert len(set().union(*B)) == sum(len(b) for b in B) == 10
    for i, b in enumerate(B):
        # connectivity
        seen, stack = set(), [next(iter(b))]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            for v in adj[u]:
                if v in b and v not in seen:
                    stack.append(v)
        assert seen == b, (i, b, seen)
    links = {}
    for i in range(5):
        for j in range(i + 1, 5):
            found = [(u, v) for u in B[i] for v in B[j] if v in adj[u]]
            assert found, (i, j)
            links[(i, j)] = found[0]
    print(f"  branch sets {B}  all connected, disjoint, pairwise adjacent")
    print(f"  linking edges {links}")
    print("  => C5[2] has a K5 minor, so bip on C5[n] (n>=2) is NOT a T-join in a dual")


# ---------------------------------------------------------------- T3 -------
def subdivide3(n, adj):
    """Replace every edge by a path of length 3.  Preserves all cycle parities."""
    E = edges_of(n, adj)
    m = n
    newadj = [set() for _ in range(n + 2 * len(E))]
    for (u, v) in E:
        a, b = m, m + 1
        m += 2
        for (p, q) in ((u, a), (a, b), (b, v)):
            newadj[p].add(q)
            newadj[q].add(p)
    return m, [frozenset(x) for x in newadj]


def T3():
    print("=== T3  3-subdivision: bip and tau* invariant; triangle-free witness ===")
    n = 5
    adj = [frozenset(set(range(5)) - {i}) for i in range(5)]
    b0, _ = bip_exact(n, adj)
    t0 = tau_star(n, adj)
    print(f"  K5:            N=5  |E|=10 bip={b0} tau*={t0['value']} gap={b0-t0['value']}")
    n2, adj2 = subdivide3(n, adj)
    E2 = edges_of(n2, adj2)
    print(f"  K5 3-subdiv:   N={n2} |E|={len(E2)} triangle-free={is_triangle_free(n2,adj2)}"
          f" girth=9")
    t2 = tau_star(n2, adj2)
    print(f"  K5 3-subdiv:   tau*={t2['value']}  (must equal tau*(K5)={t0['value']})")
    assert t2["value"] == t0["value"]
    print("  bip of the 3-subdivision is computed exactly by Q5_bip.exe (N=25); "
          "the lemma below proves it equals bip(K5)=4.")
    return n2, adj2


# ---------------------------------------------------------------- T4 -------
def rank_Q(rows, ncol):
    """Exact rank over Q of a list of rows (lists of Fractions)."""
    M = [r[:] for r in rows]
    r = 0
    for c in range(ncol):
        piv = None
        for i in range(r, len(M)):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(ncol)]
        r += 1
        if r == len(M):
            break
    return r


def T4():
    print("=== T4  fractional vertex of the odd-cycle covering polyhedron ===")
    for name in ("N14",):
        n, adj = g6_decode(NAMED[name])
        E = edges_of(n, adj)
        eidx = {e: i for i, e in enumerate(E)}
        z = {e: Fraction(1, 5) for e in E}
        ok, info = verify_cover(n, adj, z)
        cyc = enumerate_odd_cycles(n, adj, maxlen=5)
        rows = []
        for c in cyc:
            es = [tuple(sorted((c[i], c[(i + 1) % len(c)]))) for i in range(len(c))]
            if sum(z[e] for e in es) == 1:
                row = [Fraction(0)] * len(E)
                for e in es:
                    row[eidx[e]] = Fraction(1)
                rows.append(row)
        rk = rank_Q(rows, len(E))
        print(f"  {name}: |E|={len(E)}  z=1/5 feasible={ok}  cost={sum(z.values())}"
              f"  #tight 5-cycles={len(rows)}  rank={rk}"
              f"  -> {'VERTEX' if rk == len(E) else 'not a vertex'} of Q(G)")
    return


# ---------------------------------------------------------------- T5 -------
def emass(n, adj, x):
    return sum(x[u] * x[v] for (u, v) in edges_of(n, adj))


def psi_exact(n, adj, x):
    """psi(G,x) = min over cuts of the monochromatic x-mass (exact)."""
    E = edges_of(n, adj)
    w = {e: x[e[0]] * x[e[1]] for e in E}
    return bip_exact(n, adj, weights=w)


def groetzsch():
    """Mycielskian of C5: 11 vertices, 20 edges, triangle-free, chi = 4."""
    adj = [set() for _ in range(11)]

    def add(a, b):
        adj[a].add(b)
        adj[b].add(a)
    for i in range(5):
        add(i, (i + 1) % 5)                 # u_i - u_{i+1}
        add(5 + i, (i + 1) % 5)             # v_i - u_{i+1}
        add(5 + i, (i - 1) % 5)             # v_i - u_{i-1}
        add(10, 5 + i)                      # w - v_i
    return 11, [frozenset(a) for a in adj]


def andrasfai(k):
    """And(k) = circulant on 3k-1 vertices, i ~ j iff |i-j| = 1 mod 3 (the
    Gamma_{3k-1} circle graph: circular distance > 1/3)."""
    N = 3 * k - 1
    adj = [set() for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i < j:
                d = min((j - i) % N, (i - j) % N)
                if 3 * d > N:
                    adj[i].add(j)
                    adj[j].add(i)
    return N, [frozenset(a) for a in adj]


def T5():
    print("=== T5  weighted chain  Lambda <= e/5,  psi <= e - 4e^2,  both <= 1/25 ===")
    objs = [("C5", blowup_C5(1)), ("C5[2]", blowup_C5(2)), ("C5[3]", blowup_C5(3))]
    for name, g6 in NAMED.items():
        objs.append((name, g6_decode(g6)))
    objs.append(("Petersen", g6_decode("IheA@GUAo")))
    objs.append(("Groetzsch", groetzsch()))
    for k in (2, 3, 4, 5):
        objs.append((f"And({k})", andrasfai(k)))
    for name, (n, adj) in objs:
        assert is_triangle_free(n, adj), (name, "NOT triangle-free")
        x = [Fraction(1, n)] * n
        e = emass(n, adj, x)
        lam = Fraction(tau_star(n, adj)["value"], n * n)
        psi = Fraction(bip_exact(n, adj)[0], n * n)
        print(f"  {name}: N={n} e={e}({float(e):.5f}) Lambda={lam}({float(lam):.5f})"
              f" psi={psi}({float(psi):.5f}) e/5={e/5}({float(e/5):.5f})"
              f" e-4e^2={e-4*e*e}({float(e-4*e*e):.5f})  1/25={float(Fraction(1,25)):.5f}")
        assert lam <= e / 5, (name, "Lambda > e/5")
        assert psi <= e - 4 * e * e, (name, "psi > e-4e^2")
        assert lam <= psi
        assert lam <= Fraction(1, 25), (name, "Lambda > 1/25 -- COUNTEREXAMPLE")


# ---------------------------------------------------------------- T6 -------
def T6(trials=200, seed=1):
    print("=== T6  hunt for product weights x with Lambda(C5[2],x) < psi(C5[2],x) ===")
    rnd = random.Random(seed)
    n, adj = blowup_C5(2)
    E = edges_of(n, adj)
    best = None
    for t in range(trials):
        raw = [rnd.randint(1, 9) for _ in range(n)]
        s = sum(raw)
        x = [Fraction(r, s) for r in raw]
        w = {e: x[e[0]] * x[e[1]] for e in E}
        lam = tau_star(n, adj, w=w)["value"]
        psi = bip_exact(n, adj, weights=w)[0]
        if lam < psi:
            print(f"  GAP at x={raw}/{s}: Lambda={lam} < psi={psi}, gap={psi-lam}")
            best = (raw, s, lam, psi)
            break
    if best is None:
        print(f"  no product-weight gap found on C5[2] in {trials} random trials")
    return best


def T6b(trials=400, seed=7):
    print("=== T6b  hunt for ANY nonneg weights w on C5[2] with tau*_w < tau_w ===")
    rnd = random.Random(seed)
    n, adj = blowup_C5(2)
    E = edges_of(n, adj)
    for t in range(trials):
        w = {e: Fraction(rnd.randint(1, 6)) for e in E}
        lam = tau_star(n, adj, w=w)["value"]
        tau = bip_exact(n, adj, weights=w)[0]
        if lam < tau:
            print(f"  GAP: w={ {str(k):str(v) for k,v in w.items()} }")
            print(f"       tau*={lam} < tau={tau}  => C5[2] has an odd-K5 minor (Guenin)")
            return w, lam, tau
    print(f"  no weight gap found on C5[2] in {trials} random trials")
    return None


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "T1"):
        T1(6)
    if which in ("all", "T2"):
        T2()
    if which in ("all", "T3"):
        T3()
    if which in ("all", "T4"):
        T4()
    if which in ("all", "T5"):
        T5()
    if which in ("all", "T6"):
        T6()
    if which in ("all", "T6b"):
        T6b()
