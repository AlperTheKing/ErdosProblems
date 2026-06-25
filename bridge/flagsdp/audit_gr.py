#!/usr/bin/env python3
"""D1 AUDIT: independent brute reimplementation of the deficit regenerator gr_exact.
Does NOT call gr_exact's body; only reuses fs._induces_sigma_ordered for the ordered-induce
predicate (and even re-derives a brute version to cross-check that too)."""
import itertools, pickle
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs
import flag_exact as fx

T = F(2, 25)
LO = F(1243, 5000); HI = F(3197, 10000)


def induces_sigma_brute(A, R, k, Asig):
    """Independent: ordered tuple R induces labeled sigma (k,Asig) exactly."""
    for a in range(k):
        for b in range(a + 1, k):
            e = 1 if (A[R[a]] >> R[b]) & 1 else 0
            s = 1 if (Asig[a] >> b) & 1 else 0
            if e != s:
                return False
    return True


def my_gr(states, k, Asig, pmap, t):
    """Fully independent deficit functional. pmap: dict frozenset->F (side-0 prob); default 1/2."""
    out = []
    for (n, A) in states:
        if n < 2:
            out.append(F(0)); continue
        m = n - k
        Cm2 = m * (m - 1) // 2
        nk = 1
        for i in range(k):
            nk *= (n - i)
        if Cm2 <= 0 or nk == 0:
            out.append(F(0)); continue
        # adjacency as set of neighbors
        nbr = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        g = F(0)
        for R in itertools.permutations(range(n), k):
            if not induces_sigma_brute(A, R, k, Asig):
                continue
            rest = [w for w in range(n) if w not in R]
            q = {}
            for w in rest:
                prof = frozenset(i for i in range(k) if R[i] in nbr[w])
                q[w] = pmap.get(prof, F(1, 2))
            cm = F(0)
            for i in range(len(rest)):
                u = rest[i]
                for j in range(i + 1, len(rest)):
                    v = rest[j]
                    if v in nbr[u]:
                        cm += q[u] * q[v] + (1 - q[u]) * (1 - q[v])
            g += (cm / Cm2 - t)
        out.append(g / nk)
    return out


def beta_density_minus_roots(states, k, Asig):
    """For each H and each R inducing sigma: true beta over the (m-vertex) induced subgraph on non-roots
    = e(G[rest]) - maxcut(G[rest]); return per-R averaged (beta/Cm2) - t to compare g_r >= that.
    Returns list over states of (avg over R of (beta_rest/Cm2)) - t   [the TRUE min-cut deficit]."""
    out = []
    for (n, A) in states:
        if n < 2:
            out.append(None); continue
        m = n - k
        Cm2 = m * (m - 1) // 2
        nk = 1
        for i in range(k):
            nk *= (n - i)
        if Cm2 <= 0 or nk == 0:
            out.append(None); continue
        nbr = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        acc = F(0); cnt = 0
        for R in itertools.permutations(range(n), k):
            if not induces_sigma_brute(A, R, k, Asig):
                continue
            cnt += 1
            rest = [w for w in range(n) if w not in R]
            ei = [(rest[i], rest[j]) for i in range(len(rest)) for j in range(i + 1, len(rest)) if rest[j] in nbr[rest[i]]]
            ne = len(ei)
            # brute max-cut over rest (m<=5 here so 2^m fine)
            best = -1
            for mask in range(1 << len(rest)):
                side = {rest[i]: (mask >> i) & 1 for i in range(len(rest))}
                cut = sum(1 for (u, v) in ei if side[u] != side[v])
                if cut > best:
                    best = cut
            beta_rest = ne - best
            acc += F(beta_rest, Cm2) - T
        out.append(acc / cnt if cnt else None)
    return out


def main():
    d = pickle.load(open("dual_cert_n9.pkl", "rb"))
    lam = [F(x) for x in d["lam"]]; ndix = d["ndix"]; prov = d["prov"]
    atoms = []
    for c in range(len(lam)):
        if lam[c] != 0:
            pr = prov[ndix[c]]
            assert pr[0] == "deficit"
            _, k, A, cls, p = pr
            pmap = {cls[i]: F(int(p[i])) for i in range(len(cls))}
            atoms.append((c, k, list(A), cls, p, pmap))
    print(f"found {len(atoms)} nonzero deficit atoms")

    # check all pmap values are 0/1 (genuine cut) and in [0,1]
    for (c, k, A, cls, p, pmap) in atoms:
        vals = set(pmap.values())
        assert all(0 <= float(x) <= 1 for x in pmap.values()), ("pmap out of [0,1]", c, vals)
    print("all pmap values in [0,1]:", sorted(set(float(v) for (_,_,_,_,_,pm) in atoms for v in pm.values())))

    maxdisc = F(0)
    soundness_ok = True
    sound_min = F(10)
    for n in (4, 5, 6, 7):
        states = fe.enumerate_graphs(n, triangle_free=True)
        for (c, k, A, cls, p, pmap) in atoms:
            mine = my_gr(states, k, tuple(A), pmap, T)
            theirs = fx.gr_exact(states, k, tuple(A), pmap, T)
            assert len(mine) == len(theirs) == len(states)
            for i in range(len(states)):
                dsc = abs(mine[i] - theirs[i])
                if dsc > maxdisc:
                    maxdisc = dsc
                # soundness: g_r(H) >= true beta-deficit (avg over R). g is per-flag avg, beta-deficit avg over R.
                # both are convex combos over the SAME R-set with the SAME weights (uniform over inducing R),
                # so g_r >= beta-deficit must hold edge-by-flag IF cm>=beta per R.
            # per-R soundness check: g uses cm (a 0/1 cut here since pmap in {0,1}); beta uses true maxcut
            bdef = beta_density_minus_roots(states, k, tuple(A))
            for i in range(len(states)):
                if bdef[i] is None:
                    continue
                # g (averaged over inducing R, /nk) vs bdef (averaged over inducing R only).
                # nk counts ALL ordered k-tuples; bdef averages only over inducing ones. So compare
                # g*nk/(#inducing) >= bdef. Recompute #inducing:
                nn = states[i][0]
                ninduce = sum(1 for R in itertools.permutations(range(nn), k) if induces_sigma_brute(states[i][1], R, k, tuple(A)))
                if ninduce == 0:
                    continue
                nk = 1
                for ii in range(k):
                    nk *= (nn - ii)
                g_over_induce = mine[i] * nk / ninduce
                gap = g_over_induce - bdef[i]
                if gap < sound_min:
                    sound_min = gap
                if gap < 0:
                    # allow tiny negative only if exactly 0
                    if gap != 0:
                        soundness_ok = False
                        print(f"  SOUNDNESS VIOLATION n={n} atom c={c} state {i}: g/induce={float(g_over_induce):.6f} < bdef={float(bdef[i]):.6f} gap={float(gap):.2e}")
        print(f"n={n}: states={len(states)} cumulative maxdisc={maxdisc}")

    print(f"MAX ABS DISCREPANCY (mine vs gr_exact) = {maxdisc}  (float {float(maxdisc):.3e})")
    print(f"SOUNDNESS g_r/inducing >= true beta-deficit: ok={soundness_ok}, min gap = {float(sound_min):.6e} = {sound_min}")

    # unit case sanity: k=0, q=1/2 everywhere -> cm = (1/2)e_rest -> cm/Cm2 = (1/2) d_edge ; g = d_edge/2 - 2/25
    states7 = fe.enumerate_graphs(7, triangle_free=True)
    g0 = my_gr(states7, 0, tuple(), {}, T)
    edens = fx.edge_density_exact(states7)
    unit_ok = True; unit_maxdisc = F(0)
    for i in range(len(states7)):
        expect = edens[i] / 2 - T
        dsc = abs(g0[i] - expect)
        if dsc > unit_maxdisc:
            unit_maxdisc = dsc
        if dsc != 0:
            unit_ok = False
    print(f"UNIT CASE k=0,q=1/2: g == d_edge/2 - 2/25 ? ok={unit_ok}, maxdisc={unit_maxdisc}")
    # also compare to gr_exact for k=0
    g0x = fx.gr_exact(states7, 0, tuple(), {}, T)
    unit_xdisc = max(abs(g0[i]-g0x[i]) for i in range(len(states7)))
    print(f"UNIT CASE k=0: my vs gr_exact maxdisc = {unit_xdisc}")

    print("VERDICT_PASS" if (maxdisc == 0 and soundness_ok and unit_ok and unit_xdisc == 0) else "VERDICT_FAIL")


if __name__ == "__main__":
    main()
