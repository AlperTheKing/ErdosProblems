#!/usr/bin/env python3
"""
Order-5 TWO-color core SDP (GPT Q17 pivot): drop the 4-color margin lift; use 2 side colors (A=0,B=1),
add the order-5 monochromatic-P3 bipartite-block-recoloring (BR) cut that excludes the bad Clebsch cut.
Tiny vs the 45,130-var order-6 4-color monolith. Does moments+band+SW0+BR break d_mono below 0.10
toward 0.08?

BR cut (rooted at a mono-P3 e1-c-e2; U = vertices adjacent to exactly one of e1,e2):
   functional = 2*m(U) + m(U,Ubar) - cut(U,Ubar) <= 0   (mono = same side).
Sound for any global max cut (per-root density recovers the full-graph BR 2m(U)+m(U,Ubar)<=cut(U,Ubar)).
"""
import sys, itertools, time
import numpy as np
import flag_engine as fe
import flag_engine_col as fc
import flag_sdp_col as fs


def br_coef(states):
    out = []
    for (n, A, col) in states:
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        tot = 0.0
        for c in range(n):
            nb = [w for w in range(n) if adj[c][w]]
            for e1, e2 in itertools.combinations(nb, 2):
                if adj[e1][e2]:                         # need e1 !~ e2
                    continue
                if not (col[e1] == col[e2] == col[c]):  # all same side (mono P3)
                    continue
                U = [z for z in range(n) if z not in (e1, e2, c) and (adj[e1][z] ^ adj[e2][z])]
                Uset = set(U)
                mU = sum(1 for x, y in itertools.combinations(U, 2) if adj[x][y] and col[x] == col[y])
                mUb = cutUb = 0
                for x in U:
                    for y in range(n):
                        if y in Uset or y == x:
                            continue
                        if adj[x][y]:
                            if col[x] == col[y]:
                                mUb += 1
                            else:
                                cutUb += 1
                tot += 2 * mU + mUb - cutUb
        out.append(tot)
    return np.array(out)


def sw1_2col(states):
    """2-color side 1-root switch: rooted at v, P=same-side nbrs, Q=other nbrs, R=same non-nbrs,
    T=other non-nbrs; e(P,R)+e(Q,T) <= e(R,T). Returns g with g@x <= 0 (sum over roots)."""
    out = []
    for (n, A, col) in states:
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        tot = 0.0
        for v in range(n):
            P = [u for u in range(n) if u != v and col[u] == col[v] and adj[v][u]]
            Q = [u for u in range(n) if u != v and col[u] != col[v] and adj[v][u]]
            R = [u for u in range(n) if u != v and col[u] == col[v] and not adj[v][u]]
            T = [u for u in range(n) if u != v and col[u] != col[v] and not adj[v][u]]
            def eb(X, Y): return sum(1 for a in X for b in Y if adj[a][b])
            tot += eb(P, R) + eb(Q, T) - eb(R, T)
        out.append(float(tot))
    return np.array(out)


def sw2_explicit(states):
    """GPT Q18 Section 2: EXACT 2-root switch. For each 2-root (a,b) with ab in E and same side,
    P=N(a)\\N(b), Q=N(b)\\N(a) (disjoint, triangle-free); orientations t=1,2:
      t=1: p=1 on (P & same-side-as-a) or (Q & other-side);  t=2: swap.
    Functional sum_edges chi*(p_u+p_v-2 p_u p_v) <= 0 (chi=+1 mono,-1 cut). Sum over anchors and t."""
    out = []
    for (n, A, col) in states:
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        tot = 0.0
        for a in range(n):
            for b in range(a + 1, n):
                if not adj[a][b] or col[a] != col[b]:
                    continue
                sa = col[a]
                for t in (1, 2):
                    p = [0.0] * n
                    for z in range(n):
                        if z == a or z == b:
                            continue
                        inP = adj[a][z] and not adj[b][z]
                        inQ = adj[b][z] and not adj[a][z]
                        if t == 1:
                            p[z] = 1.0 if (inP and col[z] == sa) or (inQ and col[z] != sa) else 0.0
                        else:
                            p[z] = 1.0 if (inP and col[z] != sa) or (inQ and col[z] == sa) else 0.0
                    for u in range(n):
                        if u == a or u == b:
                            continue
                        for v in range(u + 1, n):
                            if v == a or v == b or not adj[u][v]:
                                continue
                            w = p[u] + p[v] - 2 * p[u] * p[v]
                            if w:
                                tot += w if col[u] == col[v] else -w
        out.append(float(tot))
    return np.array(out)


def br_profiles(states):
    """Full bipartite-block recoloring family: for each 2-root pair (a,b) with a !~ b, and each profile
    bit-choice on the 'mixed' neighbors, U = chosen subset of N(a) u N(b) inducing a bipartite block
    (we use U = (N(a)\\N(b)) u (N(b)\\N(a)) = symmetric difference, always bipartite). Generalize the
    mono-P3 cut to ALL same-side 2-root anchors (a,b same side, a!~b). Returns ONE aggregated vector
    (sum of 2*m(U)+m(U,Ubar)-cut(U,Ubar) over all such anchors). Sound for max cuts."""
    out = []
    for (n, A, col) in states:
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        tot = 0.0
        for a in range(n):
            for b in range(a + 1, n):
                if adj[a][b] or col[a] != col[b]:    # need a!~b, same side
                    continue
                U = [z for z in range(n) if z not in (a, b) and (adj[a][z] ^ adj[b][z])]
                if not U:
                    continue
                Uset = set(U)
                mU = sum(1 for x, y in itertools.combinations(U, 2) if adj[x][y] and col[x] == col[y])
                mUb = cutUb = 0
                for x in U:
                    for y in range(n):
                        if y in Uset or y == x:
                            continue
                        if adj[x][y]:
                            if col[x] == col[y]:
                                mUb += 1
                            else:
                                cutUb += 1
                tot += 2 * mU + mUb - cutUb
        out.append(float(tot))
    return np.array(out)


def ex_neighborhood(states):
    """Minimal-counterexample neighborhood EX (Section 8): per root v, 25 T(v) - 4 D(v) + 2 D(v)^2 >= 0,
    with unbiased finite-n density estimators. Returns g = -(sum over roots) so constraint g@x <= 0."""
    out = []
    for (n, A, col) in states:
        if n < 3:
            out.append(0.0); continue
        deg = [bin(A[v]).count('1') for v in range(n)]
        tot = 0.0
        for v in range(n):
            D = deg[v] / (n - 1)
            D2 = deg[v] * (deg[v] - 1) / ((n - 1) * (n - 2))         # unbiased E[1(v~z)1(v~w)]
            Tsum = 0
            for z in range(n):
                if (A[v] >> z) & 1:
                    Tsum += deg[z] - 1                                # z's nbrs excluding v
            T = Tsum / ((n - 1) * (n - 2))                            # unbiased E[1(v~z)1(z~w)]
            tot += 25 * T - 4 * D + 2 * D2
        out.append(-tot)     # constraint  -(sum) <= 0  i.e. sum of EX >= 0
    return np.array(out)


def deg_cyl(states, thr=4.0/25):
    """Linear degree cylinders <[[F(D-thr)]]> >= 0 for a few rooted F (one fresh vertex carries D).
    Returns a LIST of vectors g with g@x <= 0 (i.e. <[[F(D-thr)]]> >= 0). F in {1, same-side-nbr, other-nbr}."""
    vecs = {'F=1': [], 'F=sameNbr': [], 'F=othNbr': []}
    for (n, A, col) in states:
        if n < 2:
            for k in vecs: vecs[k].append(0.0)
            continue
        deg = [bin(A[v]).count('1') for v in range(n)]
        g1 = gs = go = 0.0
        for v in range(n):
            D = deg[v] / (n - 1)
            ex = D - thr
            g1 += ex
            # F = "root has a same-side neighbor" indicator (density), times (D - thr) via a 2nd fresh vtx
            sames = sum(1 for u in range(n) if u != v and (A[v] >> u) & 1 and col[u] == col[v])
            oths = sum(1 for u in range(n) if u != v and (A[v] >> u) & 1 and col[u] != col[v])
            gs += (sames / (n - 1)) * ex
            go += (oths / (n - 1)) * ex
        vecs['F=1'].append(-g1); vecs['F=sameNbr'].append(-gs); vecs['F=othNbr'].append(-go)
    return [np.array(vecs[k]) for k in vecs]


def deg_localizer(states, thr=4.0/25):
    """Minimal-counterexample degree core, linear F=1 form: <D> >= thr, i.e. thr - <D> <= 0.
    D = degree density = d_edge here; returns (thr - d_edge_per_state) so constraint <=0 means <D> >= thr."""
    out = []
    for (n, A, col) in states:
        deg = 2.0 * fe.num_edges(n, A) / (n * (n - 1)) if n > 1 else 0.0
        out.append(thr - deg)
    return np.array(out)


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    BAND = (0.2486, 0.3197)
    t0 = time.time()
    states = fc.enumerate_colored(N, triangle_free=True)
    print(f"=== order-{N} 2-color core (band={BAND}) ===  states={len(states)} [{time.time()-t0:.0f}s]", flush=True)
    dmono = fs.d_mono_vec(states); dedge = fs.d_edge_vec(states)
    sw0 = 2.0 * dmono - dedge
    br = br_coef(states)
    print(f"  BR coef: nonzero on {int(np.count_nonzero(np.abs(br)>1e-9))}/{len(states)} states, range [{br.min():.0f},{br.max():.0f}]", flush=True)
    tf = fs.colored_types(N, kmax=2)
    print(f"  types={len(tf)} [{time.time()-t0:.0f}s]", flush=True)

    def run(tag, extra):
        val, st, _, _ = fs.solve_primal(N, tf, band=BAND, extra_lin=extra, verbose=False)
        print(f"  [{tag}] max d_mono = {val:.6f}  (beta/N^2 <= {val/2:.5f})  status={st} [{time.time()-t0:.0f}s]", flush=True)
        return val

    sw1 = sw1_2col(states)
    brp = br_profiles(states)
    print(f"  SW1 nonzero {int(np.count_nonzero(np.abs(sw1)>1e-9))}/{len(states)}; BRprofiles nonzero {int(np.count_nonzero(np.abs(brp)>1e-9))}/{len(states)}", flush=True)
    run("moments+band only", None)
    run("+SW0", [sw0])
    run("+SW0+SW1", [sw0, sw1])
    run("+SW0+SW1+BR(monoP3)", [sw0, sw1, br])
    run("+SW0+SW1+BRprofiles", [sw0, sw1, brp])
    ex = ex_neighborhood(states)
    dcyl = deg_cyl(states)
    print(f"  EX nonzero {int(np.count_nonzero(np.abs(ex)>1e-9))}/{len(states)} range[{ex.min():.2f},{ex.max():.2f}]; degcyl[0] range[{dcyl[0].min():.2f},{dcyl[0].max():.2f}]", flush=True)
    sw2 = sw2_explicit(states)
    print(f"  SW2(explicit 2-root) nonzero {int(np.count_nonzero(np.abs(sw2)>1e-9))}/{len(states)} range[{sw2.min():.0f},{sw2.max():.0f}]", flush=True)
    run("+SW0+SW1+EX", [sw0, sw1, ex])
    run("★ +SW0+SW1+SW2(exact 2-root)", [sw0, sw1, sw2])
    run("★ +SW0+SW1+SW2+BR+EX+degcyl", [sw0, sw1, sw2, brp, ex] + dcyl)
    print("(GPT predicts SW2 kills 0.125 -> ~0.101; STOP-RULE: if >=0.098 abandon low-root 2-color)", flush=True)
    print("(SOUND iff bound stays >= 0.08; the true medium-band answer is d_mono=0.08)", flush=True)
    print("DONE", flush=True)
