"""EXACT gate for the user's RFC (reduced fan-core) / Extra-Hall route to the cutoff Hall lemma.

Blue-closed extra graph (per the user's construction):
  S = completed seed+moat descent switch (R[v]<0).  C=delta_M(S) crossing bad edges; for f in C, Wit_S(f)=exits it
  terminal-witnesses, Pref_S(f,e)=terminal-prefix vertex set (inside S).
  For X subset C:  Y=Wit(X)=union Wit_S(f);  U0=union Pref_S(f,e) over f in X;  U=cl^S_B(U0) (blue-closure inside S:
  union of B[S]-components meeting U0).  B+ = delta_B(U)\Y;  M+ = delta_M(U)\X.
  Door graph: for g in M+ (a_g in U, b_g not in U), D_U(g) = { e=xy in B+ : x in U,y not in U, some shortest geodesic Q of g
  oriented from a_g has Q∩U = initial segment ending at x (exits through e, no re-entry) }.
  Extra-Hall:  forall Z subset B+, |N(Z)| >= |Z|.
  RFC (the falsifier target): NO nonempty REDUCED Z subset B+ (|D_Z(g)|>=2 for all g in N(Z)) with |N(Z)| < |Z|.

This gate searches for an RFC falsifier (reduced deficient Z) over all X subset C, on census R<0 + H?AFBo] blowups.
If 0 falsifiers => RFC holds => route sound (proof then reduces to NL). Exact (counts).  Reuses _pl_gate.witness_structure.
"""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure


def edge(u, v):
    return (u, v) if u < v else (v, u)


def blue_closure_in_S(n, adj, side, Sset, U0):
    """Union of connected components of B[S] (blue edges within S) that meet U0."""
    Sset = set(Sset)
    comp_id = {}; comps = []
    for s in Sset:
        if s in comp_id:
            continue
        stack = [s]; comp = []; comp_id[s] = len(comps)
        while stack:
            u = stack.pop(); comp.append(u)
            for v in adj[u]:
                if v in Sset and v not in comp_id and side[u] != side[v]:  # blue edge within S
                    comp_id[v] = len(comps); stack.append(v)
        comps.append(comp)
    U = set()
    for c in comps:
        if any(x in U0 for x in c):
            U |= set(c)
    return U | set(U0)   # ensure U0 included (isolated U0 vertices)


def delta_B_M(n, adj, side, Uset):
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


def doors_of(n, adj, side, cyc, ell, Uset, g, Bplus):
    """D_U(g): exits in B+ through which a shortest geodesic of g (oriented from its U-endpoint) leaves U as initial segment."""
    a, b = g
    if a in Uset and b not in Uset:
        a_g = a
    elif b in Uset and a not in Uset:
        a_g = b
    else:
        return set()
    out = set()
    for Q0 in cyc.get(g, []):
        Q = list(Q0)
        if Q[0] != a_g:
            Q = Q[::-1]
        if Q[0] != a_g:
            continue
        inU = [1 if x in Uset else 0 for x in Q]
        if inU[0] != 1:
            continue
        r = 0
        while r + 1 < len(inU) and inU[r + 1] == 1:
            r += 1
        if r + 1 >= len(Q):
            continue
        if any(inU[j] for j in range(r + 1, len(inU))):
            continue   # re-enters U: not a clean initial-segment exit
        e = edge(Q[r], Q[r + 1])
        if e in Bplus:
            out.add(e)
    return out


def rfc_falsifier(Bplus, Mplus, door):
    """door: dict g->set(doors in B+). Search for nonempty reduced Z subset B+ with |N(Z)|<|Z| and every g in N(Z) has >=2 Z-doors."""
    Bplus = list(Bplus)
    if len(Bplus) > 16:
        return 'TOOBIG'
    # precompute N(e) = bad edges g with e in door[g]
    Ne = {e: set() for e in Bplus}
    for g, ds in door.items():
        for e in ds:
            if e in Ne:
                Ne[e].add(g)
    for r in range(2, len(Bplus) + 1):   # deficient reduced needs |Z|>=2
        for combo in itertools.combinations(Bplus, r):
            Z = set(combo)
            NZ = set()
            for e in Z:
                NZ |= Ne[e]
            if len(NZ) >= len(Z):
                continue
            # reduced? every g in NZ has >=2 Z-doors
            reduced = all(len(door[g] & Z) >= 2 for g in NZ)
            if reduced:
                return (sorted(Z), sorted(NZ))
    return None


def test_switch(name, n, adj, side, st, Sset, acc):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    if not crossM:
        return
    M, ell, T, mu, cyc = st
    # Wit_S(f), Pref_S(f,e)
    WitS = {f: set() for f in crossM}
    PrefS = {}
    for (f, e), pref in wit.items():
        WitS[f].add(e); PrefS[(f, e)] = pref
    acc['switches'] += 1
    Cl = list(crossM)
    if len(Cl) > 9:
        acc['toobig'] += 1
        return
    for rX in range(1, len(Cl) + 1):
        for X in itertools.combinations(Cl, rX):
            X = set(X)
            Y = set()
            U0 = set()
            for f in X:
                Y |= WitS[f]
                for e in WitS[f]:
                    U0 |= PrefS[(f, e)]
            U = blue_closure_in_S(n, adj, side, Sset, U0)
            dB, dM = delta_B_M(n, adj, side, U)
            Bplus = dB - Y
            Mplus = dM - X
            if not Bplus:
                continue
            door = {g: doors_of(n, adj, side, cyc, ell, U, g, Bplus) for g in Mplus}
            fz = rfc_falsifier(Bplus, Mplus, door)
            acc['XU'] += 1
            if fz == 'TOOBIG':
                acc['XU_toobig'] += 1
            elif fz is not None:
                acc['rfc_fail'] += 1
                if acc['ex'] is None:
                    acc['ex'] = (name, n, ''.join(map(str, side)), sorted(X), fz)
                return


def process(name, n, E, acc, allmax=True):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
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
                continue
            A, moat, drop = sm
            test_switch(name, n, adj, side, st, set(A) | set(moat), acc)


def main():
    acc = dict(switches=0, XU=0, rfc_fail=0, toobig=0, XU_toobig=0, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process("cen%d" % nn, n, E, acc)
        print("census N=%d: switches=%d X,U-instances=%d rfc_fail=%d toobig=%d" % (nn, acc['switches'], acc['XU'], acc['rfc_fail'], acc['toobig']), flush=True)
    hN, hE = dec("H?AFBo]")
    for t in (2,):
        nn, EE = vertex_blowup(hN, hE, t)
        process("Hblow%d" % t, nn, EE, acc)
        print("after Hblow%d N%d: switches=%d X,U=%d rfc_fail=%d toobig=%d %s" % (t, nn, acc['switches'], acc['XU'], acc['rfc_fail'], acc['toobig'], acc['ex'] or ''), flush=True)
    print("=" * 55)
    print("switches:", acc['switches'], " (X,U) instances:", acc['XU'], " too-big switches:", acc['toobig'], " too-big-Z:", acc['XU_toobig'])
    print("RFC FALSIFIERS (reduced deficient Z):", acc['rfc_fail'], acc['ex'] or '')
    print("VERDICT:", "RFC HOLDS (no reduced deficient fan core) -- the user's Extra-Hall route is SOUND on the battery; proof reduces to NL (no-naked-leaf)"
          if acc['rfc_fail'] == 0 else "RFC FALSIFIED -- reduced deficient fan core exists; route needs repair")


if __name__ == "__main__":
    main()
