"""ADVERSARIAL INDEPENDENT verification of route 'spectral'.
Central inequality (claimed to HOLD on full battery with extremal K=151/16):
    V2 := sum_v (T_v - N)^2  <=  K * Gamma * (N^2/25 - beta)
  with Gamma = sum_f ell(f)^2 ,  beta = |M| ,  Gbud := N^2/25 - beta .

This file re-implements the load machinery check FROM SCRATCH (own struct via _satzmu_conn.struct_for_side,
which itself recomputes M, ell, geodesics, T). It does NOT import the previous agent's gate (_wf_rig_spec.py).

For each config (graph + gamma-min connected-B max cut) it computes EXACT Fraction:
    V2,  Gamma,  Gbud,  and the binding ratio  r := V2 / (Gamma * Gbud)   (when Gbud>0).
The claimed bound HOLDS at K iff  r <= K  for all configs with Gbud>0, AND V2==0 whenever Gbud<=0.

We report:
  - global max ratio r* (the true extremal K on this battery) as an exact Fraction,
  - the binding config,
  - any config with Gbud<=0 but V2>0 (a HARD refutation of "holds with any finite K"),
  - explicit PASS/FAIL of the claim K<=151/16 (i.e. is r* <= 151/16 ?).

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint

K_CLAIM = F(151, 16)   # 9.4375

# ---- own gamma-min connected-B max-cut enumerator (independent of _stark1.gmins) ----
def gmins(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb:
            continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0:
                ok = False; break
            G += (d + 1) ** 2
        if ok:
            cand.append((s, G))
    if not cand:
        return adj, []
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm]

def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E:
        a[x].add(y); a[y].add(x)
    return a

def blowup(parts):
    mm = len(parts); off = [0] * (mm + 1)
    for i in range(mm):
        off[i + 1] = off[i] + parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i + 1) % mm
        for a in range(off[i], off[i + 1]):
            for b in range(off[j], off[j + 1]):
                EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))

# global accumulator
ACC = dict(
    n=0,
    rmax=(F(-1), '', 0, 0),          # (ratio, name, N, beta) max over configs with Gbud>0
    fail_count=0,                    # configs with r > K_CLAIM
    first_fail=None,
    hard_refute=[],                  # configs with Gbud<=0 and V2>0  (any finite K fails)
    gbud0_ok=0,                      # configs with Gbud==0 and V2==0 (rigidity confirmed)
    gbud_neg=0,                      # configs with Gbud<0 (beta>N^2/25 -- should be impossible if Erdos holds)
)

def chk(name, n, adj, side):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = n
    beta = len(M)
    Gamma = sum(F(ell[f]) ** 2 for f in M)
    V2 = sum((t - F(N)) ** 2 for t in T)
    Gbud = F(N * N, 25) - F(beta)
    ACC['n'] += 1
    if Gbud < 0:
        ACC['gbud_neg'] += 1
        # beta > N^2/25: would itself violate Erdos. Record loudly.
        ACC['hard_refute'].append((name, N, beta, float(Gamma), float(V2), float(Gbud), 'BETA>N^2/25'))
        return
    if Gbud == 0:
        if V2 == 0:
            ACC['gbud0_ok'] += 1
        else:
            ACC['hard_refute'].append((name, N, beta, float(Gamma), float(V2), 0.0, 'Gbud=0 but V2>0'))
        return
    # Gbud > 0
    r = V2 / (Gamma * Gbud)
    if r > ACC['rmax'][0]:
        ACC['rmax'] = (r, name, N, beta)
    if r > K_CLAIM:
        ACC['fail_count'] += 1
        if ACC['first_fail'] is None:
            ACC['first_fail'] = (name, N, beta, str(r), float(r), str(V2), str(Gamma), str(Gbud))

def run_battery():
    # try to import lane builders; they pull in ortools. If unavailable, skip lanes (note in report).
    have_lanes = True
    try:
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from _verify_two_lane import build_two_lane
            from _wf_lrsbreak_0 import build_k_lane
            from _wf_lrsbreak_0c import greedy_chords
    except Exception as e:
        have_lanes = False
        print("  [lane builders unavailable: %r -- skipping two-lane/k-lane]" % e, flush=True)

    if have_lanes:
        for L in range(8, 21, 2):
            n, E, side, _ = build_two_lane(L)
            chk("two-lane-L%d" % L, n, adj_of(n, E), side)
        for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
            bad = greedy_chords(Ll, k, gap)
            n, E, side, bad = build_k_lane(Ll, k, bad)
            chk("klane-L%dk%d" % (Ll, k), n, adj_of(n, E), side)
        print("  two-lane + k-lane done (rmax so far=%s)" % float(ACC['rmax'][0]), flush=True)

    # census geng -tc N=7..11, ALL gamma-min cuts
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in outg:
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for s in cuts:
                chk("cen%s" % g6, n, adj, s)
        print("  census N=%d done (rmax so far=%s)" % (nn, float(ACC['rmax'][0])), flush=True)

    # C5/C7/C9 [t] uniform blow-ups t=1..5
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t] * cyc)
            if n > 26:
                continue
            adj, cuts = gmins(n, E)
            for s in (cuts[:1] if cuts else []):
                chk("C%d[%d]" % (cyc, t), n, adj, s)

    # non-uniform blow-ups
    for parts in [[2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2], [1, 3, 2, 2, 3]]:
        n, E = blowup(parts)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []):
            chk("nu%s" % parts, n, adj, s)

    # Mycielskians + glued islands
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    def bridge(b1, b2, u, v):
        nn, E = union_disjoint(b1, b2); n1 = b1[0]
        return nn, E + [(u, n1 + v)]
    extra = [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
             ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9))),
             ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
             ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]
    for name, (nn, E) in extra:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]:
            chk(name, nn, adj, s)
    print("  blow-ups + Mycielskians + glued islands done (rmax so far=%s)" % float(ACC['rmax'][0]), flush=True)

if __name__ == "__main__":
    print("=== INDEPENDENT VERIFY route 'spectral': V2 <= K*Gamma*(N^2/25-beta), claim K=151/16 ===", flush=True)
    run_battery()
    r, name, N, beta = ACC['rmax']
    print("\n  total configs checked = %d" % ACC['n'], flush=True)
    print("  Gbud==0 with V2==0 (rigidity confirmed) = %d" % ACC['gbud0_ok'], flush=True)
    print("  Gbud<0 (beta>N^2/25!) count = %d" % ACC['gbud_neg'], flush=True)
    print("  EXTREMAL ratio r* = V2/(Gamma*Gbud) = %s = %.6f" % (str(r), float(r)), flush=True)
    print("    binding config: name=%s N=%d beta=%d" % (name, N, beta), flush=True)
    print("  claimed K = 151/16 = %.6f" % float(K_CLAIM), flush=True)
    print("  r* <= 151/16 ? %s   (r*/K = %.6f)" % (r <= K_CLAIM, float(r / K_CLAIM)), flush=True)
    print("  configs with r > 151/16 = %d" % ACC['fail_count'], flush=True)
    if ACC['first_fail']:
        print("  FIRST K-FAIL: %s" % (ACC['first_fail'],), flush=True)
    if ACC['hard_refute']:
        print("  *** HARD REFUTATIONS (Gbud<=0 but V2>0, or beta>N^2/25) ***", flush=True)
        for hr in ACC['hard_refute']:
            print("     %s" % (hr,), flush=True)
    print("\n  === CLAIM 'V2<=151/16 * Gamma*Gbud holds on battery' : %s ===" % (
        "HOLDS (0 violations)" if (ACC['fail_count'] == 0 and not ACC['hard_refute']) else "FAILS"), flush=True)
