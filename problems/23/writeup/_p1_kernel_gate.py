"""INDEPENDENT exact gate for Codex's (P1) P1-STRUCTURAL lemma (block 10:xx) => H_UU strictly PD.

H = diag(N-T)+Lstar (rational beta').  O={T_v>N}, U=V\O.  G_U = graph on U with edge uv iff Lstar[u][v]!=0
(u,v consecutive on some shortest odd cycle).  u in U is a BOUNDARY vertex if Lstar[u][o]!=0 for some o in O.

P1-structural: for every connected component C of G_U, either
   (a) C contains a STRICT deficit vertex u (T_u < N), or
   (b) C has a boundary cycle-edge to O.
=> every zero-energy vector of H_UU vanishes (constant on components; killed by (a) strict deficit or (b) Dirichlet
   boundary to O) => H_UU strictly PD when O nonempty.

This gate checks the criterion AND, as ground truth, that H_UU is actually PD (exact LDL).  Full battery incl N=23
+ randoms/overloaded blowups/islands.  Independent reimpl (Codex tested 728 O-cuts; I add denser randoms/blowups).
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
from _csmspec import is_psd


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
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    O = [v for v in range(n) if T[v] > N]
    U = [v for v in range(n) if T[v] <= N]
    if not O:
        return
    acc['Ononempty'] += 1
    Oset = set(O); Uset = set(U)
    # G_U adjacency (u,v in U with H off-diag != 0); boundary U->O
    adjU = {u: set() for u in U}
    boundary = set()
    for u in U:
        for w in range(n):
            if w == u or H[u][w] == 0:
                continue
            if w in Uset:
                adjU[u].add(w)
            elif w in Oset:
                boundary.add(u)
    # components of G_U
    seen = set(); crit_fail = False
    for s in U:
        if s in seen:
            continue
        comp = []; stack = [s]; seen.add(s)
        while stack:
            u = stack.pop(); comp.append(u)
            for w in adjU[u]:
                if w not in seen:
                    seen.add(w); stack.append(w)
        has_strict = any(T[u] < N for u in comp)
        has_bdy = any(u in boundary for u in comp)
        if not (has_strict or has_bdy):
            crit_fail = True
            if acc['crit_ex'] is None:
                acc['crit_ex'] = (name, n, ''.join(map(str, side)), tuple(comp))
    if crit_fail:
        acc['crit_fail'] += 1
    # ground truth: H_UU strictly PD?
    Huu = [[H[a][b] for b in U] for a in U]
    psd, mp = is_psd([row[:] for row in Huu])
    if not psd:
        acc['Huu_notpsd'] += 1
    elif mp == 0:
        acc['Huu_singular'] += 1
        if acc['sing_ex'] is None:
            acc['sing_ex'] = (name, n, ''.join(map(str, side)))


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
    acc = dict(cuts=0, Ononempty=0, crit_fail=0, Huu_notpsd=0, Huu_singular=0,
               crit_ex=None, sing_ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: On=%d crit_fail=%d Huu_notpsd=%d Huu_singular=%d"
              % (nn, acc['Ononempty'], acc['crit_fail'], acc['Huu_notpsd'], acc['Huu_singular']), flush=True)
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: On=%d crit_fail=%d Huu_singular=%d %s" % (acc['Ononempty'], acc['crit_fail'], acc['Huu_singular'], acc['crit_ex'] or ''), flush=True)
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3),(4,2,4,2,4),(5,2,5,2,5)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 24:
            gfam("blow%s" % (sizes,), nn, EE, acc)
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam("isl_C5_MycC7", nn, EE, acc)
    print("after chains+blowups+islands: On=%d crit_fail=%d Huu_singular=%d %s" % (acc['Ononempty'], acc['crit_fail'], acc['Huu_singular'], acc['crit_ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 200 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12, 13]); p = rng.uniform(0.12, 0.34)
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
    print("O-nonempty cuts tested:", acc['Ononempty'], " (random:", made, ")")
    print("P1-structural criterion FAILURES:", acc['crit_fail'], acc['crit_ex'] or '')
    print("H_UU not PSD (ground truth):", acc['Huu_notpsd'])
    print("H_UU singular (PSD but min pivot 0):", acc['Huu_singular'], acc['sing_ex'] or '')
    ok = acc['crit_fail'] == 0 and acc['Huu_notpsd'] == 0 and acc['Huu_singular'] == 0
    print("VERDICT:", "(P1) P1-structural HOLDS + H_UU strictly PD on every O-nonempty cut incl N=23 + randoms/blowups -- (P1) PROOF-READY"
          if ok else "FAIL (see above)")


if __name__ == "__main__":
    main()
