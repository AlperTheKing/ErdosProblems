#!/usr/bin/env python3
"""VERIFIER (adversarial) -- independent replay of farkas_dual Finding 4 on the two
archived t=5 engine hits #298 (R49) and #264 (R50). Own graph6 decoder, own
enumeration, own sweeps. Pure integers.

Per hit:
  H1  decode graph6; expect n=18, 24 edges, connected bipartite; print shores.
  H2  available atoms = same-shore blue-distance-4 pairs (expect 32 for #298,
      30 for #264); candidate profile owners (blue deg 5 AND available-bad deg 5).
  H3  engine cross-checks:
        #264 at S={4,5,6,7,8,11,14,16}: fixedBlue (expect 2), badCross on the
        available SUPERSET (report claims 24; colleague's script asserts 23 -- settle it).
        #298: max kappa on the SUPERSET (engine sigma=-20 is about ITS selection).
  H4  enumerate ALL 25-atom selections keeping owner 0's five bads, atom graph
      triangle-free, union of complete-row supports = all 24 edges, max SDR = 24,
      every 1-atom deletion SDR = 24.  (same axiom set as the colleague; expect
      5 for #298 / 3 for #264)
  H5  per surviving selection: max kappa over all 2^18 (gray code), singleSafe
      count, kappa(badNbrs(owner)), and (for #264) badCross/kappa at the fixed
      engine switch.  Claims: #298 max-kappa range {19,20} singleSafe 0;
      #264 range {21,22} singleSafe 0 with 21 attained at the fixed switch.
"""
from itertools import combinations
import sys

G6 = {"hit298": "Q??????wE_[?EGs?D_@A?C_B???",
      "hit264": "Q??????wE_Bws?s?DCD??@?@???"}

def decode_g6(s):
    vals = [ord(c) - 63 for c in s]
    assert all(0 <= v < 64 for v in vals), "bad g6 char"
    n = vals[0]
    need = (n * (n - 1) // 2 + 5) // 6
    assert len(vals) - 1 == need, (len(vals) - 1, need)
    bits = []
    for v in vals[1:]:
        bits.extend(((v >> 5) & 1, (v >> 4) & 1, (v >> 3) & 1,
                     (v >> 2) & 1, (v >> 1) & 1, v & 1))
    E = set()
    t = 0
    for col in range(1, n):
        for row in range(col):
            if bits[t]:
                E.add(frozenset((row, col)))
            t += 1
    return n, E

def sweep_max(N, atom_list, blue_list, collect=0):
    inc_a = [[] for _ in range(N)]
    inc_b = [[] for _ in range(N)]
    for k, e in enumerate(atom_list):
        u, w = tuple(e); inc_a[u].append(k); inc_a[w].append(k)
    for k, e in enumerate(blue_list):
        u, w = tuple(e); inc_b[u].append(k); inc_b[w].append(k)
    side = [0] * N
    ka = kb = 0
    best = 0; args = [0]
    mask = 0
    AT = [tuple(e) for e in atom_list]
    BT = [tuple(e) for e in blue_list]
    for g in range(1, 1 << N):
        u = (g & -g).bit_length() - 1
        side[u] ^= 1
        mask ^= (1 << u)
        for k in inc_a[u]:
            a0, a1 = AT[k]
            ka += 1 if (side[a0] ^ side[a1]) else -1
        for k in inc_b[u]:
            a0, a1 = BT[k]
            kb += 1 if (side[a0] ^ side[a1]) else -1
        val = ka - kb
        if val > best:
            best = val; args = [mask]
        elif val == best and collect and len(args) < collect:
            args.append(mask)
    return best, args

def kappa_at(S, atom_list, blue_list):
    ms = 0
    for u in S:
        ms |= 1 << u
    ka = sum(1 for e in atom_list for u, w in [tuple(e)] if ((ms >> u) ^ (ms >> w)) & 1)
    kb = sum(1 for e in blue_list for u, w in [tuple(e)] if ((ms >> u) ^ (ms >> w)) & 1)
    return ka, kb, ka - kb

def analyze(tag, g6, owner, fixed_S=None):
    print("=" * 72)
    N, BLUE = decode_g6(g6)
    print("%s: n=%d, edges=%d" % (tag, N, len(BLUE)))
    assert N == 18
    ab = [set() for _ in range(N)]
    for e in BLUE:
        u, w = tuple(e); ab[u].add(w); ab[w].add(u)
    col = [None] * N
    col[0] = 0; fr = [0]
    while fr:
        nx = []
        for u in fr:
            for w in ab[u]:
                if col[w] is None:
                    col[w] = col[u] ^ 1; nx.append(w)
                else:
                    assert col[w] != col[u], "not bipartite"
        fr = nx
    assert all(c is not None for c in col), "disconnected"
    sh0 = sorted(u for u in range(N) if col[u] == 0)
    sh1 = sorted(u for u in range(N) if col[u] == 1)
    print("  shores %d+%d: %s | %s" % (len(sh0), len(sh1), sh0, sh1))

    def bfs(src):
        d = [None] * N; d[src] = 0; f2 = [src]
        while f2:
            nx = []
            for u in f2:
                for w in ab[u]:
                    if d[w] is None:
                        d[w] = d[u] + 1; nx.append(w)
            f2 = nx
        return d
    D = [bfs(u) for u in range(N)]
    AV = sorted((frozenset((u, w)) for u, w in combinations(range(N), 2)
                 if col[u] == col[w] and D[u][w] == 4), key=sorted)
    print("  available atoms: %d" % len(AV))
    deg_av = [sum(1 for e in AV if u in e) for u in range(N)]
    owners = [u for u in range(N) if len(ab[u]) == 5 and deg_av[u] == 5]
    print("  candidate owners (blueDeg=5, availBadDeg=5): %s ; owner used = %d (availBadDeg %d)"
          % (owners, owner, deg_av[owner]))

    def rows_of(at):
        s, t = sorted(at)
        res = []
        for n1 in ab[s]:
            for n2 in ab[n1]:
                if n2 == s:
                    continue
                for n3 in ab[n2]:
                    if n3 in (s, n1):
                        continue
                    if t in ab[n3] and t not in (s, n1, n2):
                        res.append((s, n1, n2, n3, t))
        return res
    F = {}
    for at in AV:
        rr = rows_of(at)
        assert rr, at
        F[at] = frozenset(frozenset((r[k], r[k + 1])) for r in rr for k in range(4))

    BL = sorted(BLUE, key=lambda e: sorted(e))
    # H3 superset checks
    if fixed_S is not None:
        ka, kb, kk = kappa_at(fixed_S, AV, BL)
        print("  SUPERSET at fixed S=%s: badCross=%d fixedBlue=%d kappa=%d"
              % (sorted(fixed_S), ka, kb, kk))
    best_sup, args_sup = sweep_max(N, AV, BL)
    print("  SUPERSET max kappa = %d at S=%s"
          % (best_sup, sorted(u for u in range(N) if (args_sup[0] >> u) & 1)))

    # ---- H4 enumeration ----
    forced = [at for at in AV if owner in at]
    assert len(forced) == 5, len(forced)
    droppable = [at for at in AV if owner not in at]
    nd = len(droppable)
    k_drop = len(AV) - 25
    pos = {at: i for i, at in enumerate(droppable)}
    tri_masks = []
    aset = set(AV)
    for u, w, z in combinations(range(N), 3):
        e1, e2, e3 = frozenset((u, w)), frozenset((u, z)), frozenset((w, z))
        if e1 in aset and e2 in aset and e3 in aset:
            mask = 0
            allforced = True
            for e in (e1, e2, e3):
                if e in pos:
                    mask |= 1 << pos[e]; allforced = False
            assert not allforced, "triangle of forced atoms -- no valid selection"
            tri_masks.append(mask)
    print("  triangles among available atoms: %d ; droppable %d choose %d = enumerating"
          % (len(tri_masks), nd, k_drop))
    # per-edge coverage masks over droppable + forced counts
    edge_dropmask = {}
    edge_forcedcnt = {}
    for e in BL:
        mset = 0; fc = 0
        for at in AV:
            if e in F[at]:
                if at in pos:
                    mset |= 1 << pos[at]
                else:
                    fc += 1
        edge_dropmask[e] = mset
        edge_forcedcnt[e] = fc
    crit_edges = [(edge_dropmask[e], bin(edge_dropmask[e]).count('1'))
                  for e in BL if edge_forcedcnt[e] == 0]
    crit_edges = [em for em, cnt in crit_edges if cnt <= k_drop + 6]

    EIDX = {e: i for i, e in enumerate(BL)}
    def sdr_size(atom_list):
        matched = {}
        def try_row(p2, seen):
            for e in F[atom_list[p2]]:
                ei = EIDX[e]
                if ei in seen:
                    continue
                seen.add(ei)
                if ei not in matched or try_row(matched[ei], seen):
                    matched[ei] = p2
                    return True
            return False
        got = 0
        for p2 in range(len(atom_list)):
            if try_row(p2, set()):
                got += 1
        return got

    survivors = []
    tried = 0
    stage_tri = stage_cov = stage_sdr = 0
    for combo in combinations(range(nd), k_drop):
        tried += 1
        dm = 0
        for i2 in combo:
            dm |= 1 << i2
        ok = True
        for tm in tri_masks:
            if not (dm & tm):
                ok = False; break
        if not ok:
            continue
        stage_tri += 1
        cov = True
        for em in crit_edges:
            if (em & ~dm) == 0:
                cov = False; break
        if not cov:
            continue
        # full union check (cheap masks may not be exhaustive)
        kept = [at for at in AV if not (at in pos and (dm >> pos[at]) & 1)]
        un = set()
        for at in kept:
            un |= F[at]
        if len(un) != 24:
            continue
        stage_cov += 1
        if sdr_size(kept) != 24:
            continue
        if all(sdr_size([o for o in kept if o != at2]) == 24 for at2 in kept):
            stage_sdr += 1
            survivors.append(kept)
    print("  tried %d ; passed-tri %d ; passed-union %d ; VALID (circuit) %d"
          % (tried, stage_tri, stage_cov, len(survivors)))

    # ---- H5 measurements ----
    results = []
    for kept in survivors:
        AL = sorted(kept, key=lambda e: sorted(e))
        mval, margs = sweep_max(N, AL, BL)
        aall = [set(ab[u]) for u in range(N)]
        for e in kept:
            u, w = tuple(e); aall[u].add(w); aall[w].add(u)
        n_safe = 0
        safelist = []
        for u in sh0:
            for w in sh1:
                e = frozenset((u, w))
                if e in BLUE:
                    continue
                if aall[u] & aall[w]:
                    continue
                okp = True
                for at in kept:
                    s, t = tuple(at)
                    if min(D[s][u] + 1 + D[w][t], D[s][w] + 1 + D[u][t]) <= 4:
                        okp = False; break
                if okp:
                    n_safe += 1; safelist.append((u, w))
        bn = sorted(set(w for at in kept if owner in at for w in at if w != owner))
        _, _, k_bn = kappa_at(bn, AL, BL)
        row = {"maxk": mval, "safe": n_safe, "k_badnbrs": k_bn}
        if fixed_S is not None:
            ka, kb, kk = kappa_at(fixed_S, AL, BL)
            row["S_badCross"] = ka; row["S_kappa"] = kk
        results.append(row)
        if safelist:
            print("    !!! singleSafe pairs found: %s" % safelist)
    print("  PER-SELECTION: max-kappa values %s ; singleSafe %s ; kappa(badNbrs(owner)) %s"
          % (sorted(set(r["maxk"] for r in results)),
             sorted(set(r["safe"] for r in results)),
             sorted(set(r["k_badnbrs"] for r in results))))
    if fixed_S is not None and results:
        print("  PER-SELECTION at fixed S: badCross %s ; kappa %s"
              % (sorted(set(r["S_badCross"] for r in results)),
                 sorted(set(r["S_kappa"] for r in results))))
    return results

res298 = analyze("hit298", G6["hit298"], owner=0)
res264 = analyze("hit264", G6["hit264"], owner=0, fixed_S={4, 5, 6, 7, 8, 11, 14, 16})
print("DONE v_hits")
