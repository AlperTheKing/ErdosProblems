"""INDEPENDENT exact gate for GPT-Pro's hereditary paid-leakage inequality (PL) -- the candidate proof of the Hall
lemma (PL_HEREDITARY_HALL_GPTPRO.md). Reimplemented from scratch (witness graph, U_D, leaks); reuses only struct_for_side.

For an R<0 vertex v on a connected-B max cut, take the descent switch S (length-bundle L_max seed through v, + <=1 moat),
neutral + B-conn + Gamma-decreasing. Build the witness graph W:
  L = crossM = bad edges with exactly one endpoint in S;  R = bdyB = blue edges with exactly one endpoint in S;
  f witnesses e iff some shortest geodesic of f, oriented from f's endpoint INSIDE S, has S as a terminal prefix and
  exits S through e.  For each (f,e) record the terminal-prefix vertex set pref(f,e) = path[0..r] (inside S).
(PL): for every CONNECTED subdiagram D of W,  beta(D)=|delta_B(U_D)\R_D| >= mu(D)=|delta_M(U_D)\L_D|,
  U_D = union of pref(f,e) over witness-edges (f,e) in D.
Enumerate ALL connected subdiagrams (feasible only for small W: census R<0 + H?AFBo] base). Exact, no Fractions needed (counts).
"""
import subprocess, itertools
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from fractions import Fraction as F
from _construction_gate import lenbundle_switches, gamma_of, boundary_delta, flip
from _seedmoat_gate import find_seedmoat


def edge(u, v):
    return (u, v) if u < v else (v, u)


def witness_structure(n, adj, side, st, Sset):
    """Return (crossM, bdyB, wit_edges) where wit_edges[(f,e)] = frozenset(terminal prefix verts) ; or None if invalid."""
    M, ell, T, mu, cyc = st
    inS = [1 if u in Sset else 0 for u in range(n)]
    crossM = []; bdyB = set()
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if inS[u] == inS[v]:
                continue
            if side[u] == side[v]:
                crossM.append(edge(u, v))   # bad edge crossing S
            else:
                bdyB.add(edge(u, v))        # blue edge crossing S
    wit = {}
    for f in crossM:
        u, v = f
        tau = u if inS[u] else v   # endpoint of f inside S
        ok_any = False
        for path0 in cyc[f]:
            path = list(path0)
            if path[0] != tau:
                path = list(reversed(path))
            if path[0] != tau:
                continue
            bits = [inS[x] for x in path]
            if bits[0] != 1 or bits[-1] != 0:
                continue
            r = 0
            while r + 1 < len(bits) and bits[r + 1] == 1:
                r += 1
            if any(bits[j] for j in range(r + 1, len(bits))):
                continue   # not a terminal prefix (re-enters S)
            e = edge(path[r], path[r + 1])
            if e not in bdyB:
                continue
            pref = frozenset(path[:r + 1])
            key = (f, e)
            wit[key] = wit.get(key, frozenset()) | pref
            ok_any = True
        # f must witness at least one e (terminal validity)
    return crossM, bdyB, wit


def deltas_of(n, adj, side, Uset):
    """(delta_B(U), delta_M(U)) = (blue edges, bad edges) with exactly one endpoint in U."""
    dB = set(); dM = set()
    for u in Uset:
        for v in adj[u]:
            if v in Uset:
                continue
            if side[u] != side[v]:
                dB.add(edge(u, v))
            else:
                dM.add(edge(u, v))
    return dB, dM


def connected_subdiagrams(crossM, bdyB, wit):
    """Yield connected vertex subsets of the bipartite witness graph W (vertices = crossM + bdyB).
       Edges: (f,e) for each witness key. Enumerate all connected induced subgraphs (small W only)."""
    Lv = list(crossM); Rv = list(bdyB)
    nodes = Lv + Rv
    idx = {x: i for i, x in enumerate(nodes)}
    adjW = {x: set() for x in nodes}
    for (f, e) in wit:
        adjW[f].add(e); adjW[e].add(f)
    # enumerate connected induced subgraphs via growing from each node (bounded for small W)
    seen = set()
    nn = len(nodes)
    if nn > 22:
        return  # too big to enumerate; caller handles
    for r in range(1, nn + 1):
        for combo in itertools.combinations(nodes, r):
            cs = frozenset(combo)
            if cs in seen:
                continue
            # connected?
            start = next(iter(cs)); stack = [start]; vis = {start}
            while stack:
                x = stack.pop()
                for y in adjW[x]:
                    if y in cs and y not in vis:
                        vis.add(y); stack.append(y)
            if len(vis) == len(cs):
                seen.add(cs)
                yield cs


def test_switch(name, n, adj, side, st, Sset, acc):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    if not bdyB or not wit:
        return
    acc['switches'] += 1
    if len(crossM) + len(bdyB) > 22:
        acc['too_big'] += 1
        return
    for D in connected_subdiagrams(crossM, bdyB, wit):
        L_D = [f for f in crossM if f in D]
        R_D = [e for e in bdyB if e in D]
        # U_D = union of prefixes of witness-edges (f,e) with both f,e in D
        U = set()
        for (f, e), pref in wit.items():
            if f in D and e in D:
                U |= pref
        if not U:
            continue
        dB, dM = deltas_of(n, adj, side, U)
        beta = len(dB - set(R_D))
        mu = len(dM - set(L_D))
        acc['D_checked'] += 1
        if beta < mu:
            acc['fail'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), sorted(L_D), sorted(R_D), beta, mu)


def process(name, n, E, acc, allmax=True):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj) if allmax else []
    for side in cuts:
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        if not M:
            continue
        N = F(n)
        K2 = build_K2(n, M, cyc)
        R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v in range(n):
            if R[v] >= 0:
                continue
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                acc['nodescent'] += 1
                continue
            A, moat, drop = sm
            Sset = set(A) | set(moat)
            test_switch(name, n, adj, side, st, Sset, acc)


def main():
    acc = dict(switches=0, D_checked=0, fail=0, too_big=0, nodescent=0, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process("cen%d" % nn, n, E, acc)
        print("census N=%d: switches=%d D_checked=%d fail=%d too_big=%d" % (nn, acc['switches'], acc['D_checked'], acc['fail'], acc['too_big']), flush=True)
    print("=" * 55)
    print("switches tested:", acc['switches'], " connected subdiagrams checked:", acc['D_checked'])
    print("too-big switches skipped (W>22):", acc['too_big'], " nodescent:", acc['nodescent'])
    print("(PL) beta(D)>=mu(D) FAILURES:", acc['fail'], acc['ex'] or '')
    print("VERDICT:", "(PL) HOLDS exact on all enumerable connected witness subdiagrams (census R<0) -- GPT-Pro's hereditary inequality VALIDATED on small cases"
          if acc['fail'] == 0 else "(PL) FALSE -- GPT-Pro's proof mechanism is WRONG")


if __name__ == "__main__":
    main()
