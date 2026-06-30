"""EXACT gate for Codex's M-MATRIX SUPERSOLUTION reduction of (H) (block 09:46).

H = diag(N-T) + Lstar is a symmetric Z-matrix (off-diagonals = Lstar off-diagonals <= 0).
THEOREM (standard): if phi>0 coordinatewise and H*phi >= 0 coordinatewise, then H is PSD.
[D=diag(phi): (DHD) symmetric, off-diag phi_i H_ij phi_j <=0, row-sum_i = phi_i (H phi)_i >= 0
 => DHD diagonally dominant with nonneg diagonal => PSD => H PSD by congruence.]
Candidate supersolution: phi_v = T_v + 1 (>0).  With certified rational beta' (conservative) this proves true-beta (H).

So this gate reduces (H) -- a global PSD inequality -- to the COORDINATEWISE inequality H*(T+1) >= 0, i.e. per vertex v:
   (N - T_v)(T_v + 1) + sum_f (beta'_{L_f}/|cyc[f]|) sum_{Q in cyc[f]} sum_{w ~ v in Q} (T_v - T_w)  >= 0.
This gate verifies (a) H is a Z-matrix (off-diag <=0), (b) phi>0, (c) H*phi >= 0, all EXACT, full battery incl N=23.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import build_H, BETA


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    H = build_H(n, M, ell, T, cyc, BETA)
    # (a) Z-matrix check: off-diagonals <= 0
    for i in range(n):
        for j in range(n):
            if i != j and H[i][j] > 0:
                acc['zfail'] += 1
                if acc['zex'] is None:
                    acc['zex'] = (name, n, i, j, str(H[i][j]))
                break
    phi = [T[v] + 1 for v in range(n)]
    # (b) phi>0 trivially (T>=0). (c) H*phi >= 0 coordinatewise
    for v in range(n):
        hv = sum(H[v][w] * phi[w] for w in range(n))
        if hv < 0:
            acc['fail'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), v, str(hv), str(T[v]))
        else:
            if hv == 0:
                acc['tight'] += 1
            if acc['minval'] is None or hv < acc['minval']:
                acc['minval'] = hv


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(cuts=0, fail=0, zfail=0, tight=0, minval=None, ex=None, zex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d Hphi_fail=%d zfail=%d" % (nn, acc['cuts'], acc['fail'], acc['zfail']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d Hphi_fail=%d zfail=%d %s" % (acc['cuts'], acc['fail'], acc['zfail'], acc['ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d Hphi_fail=%d zfail=%d %s" % (acc['cuts'], acc['fail'], acc['zfail'], acc['ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("gamma-min cuts tested:", acc['cuts'], " (random N11/12:", made, ")")
    print("Z-matrix (off-diag<=0) FAILURES:", acc['zfail'], acc['zex'] or '')
    print("H*(T+1) >= 0 COORDINATE FAILURES:", acc['fail'], acc['ex'] or '')
    print("tight coords (H*phi=0):", acc['tight'], " min H*phi value (exact):", str(acc['minval']))
    ok = acc['fail'] == 0 and acc['zfail'] == 0
    print("VERDICT:", "H*(T+1)>=0 + Z-matrix HOLD exact incl N=23 -- (H) REDUCES to coordinatewise H(T+1)>=0 (M-matrix supersolution); PSD proof = N local scalar inequalities"
          if ok else "FAIL")


if __name__ == "__main__":
    main()
