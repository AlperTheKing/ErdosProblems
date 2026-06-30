"""Part 4: does V2 <= K*Gamma*Gbud (K fixed) IMPLY LOAD-PSC-c ?
LOAD-PSC-c LHS:  S := sum_v T_v(T_v - N) + (N/c)*(TV_cut - TV_bad)
              =  [sum_v T_v^2 - N*sum_v T_v] + (N/c)*(TV_cut - TV_bad)
With handshake sum_v T_v = Gamma:
   sum_v T_v(T_v-N) = sum_v T_v^2 - N*Gamma
   and V2 = sum_v (T_v-N)^2 = sum_v T_v^2 - 2N*Gamma + N^2 * N   (since sum_v N^2 = N*N^2 = N^3)
            wait: sum_v (T_v-N)^2 = sum T^2 - 2N sum T + sum N^2 = sum T^2 - 2N*Gamma + N*N^2.
   => sum_v T_v^2 = V2 + 2N*Gamma - N^3.
   => sum_v T_v(T_v-N) = V2 + 2N*Gamma - N^3 - N*Gamma = V2 + N*Gamma - N^3.
So S = V2 + N*Gamma - N^3 + (N/c)*(TV_cut - TV_bad).
LOAD-PSC-c:  S <= Gamma*Gbud  with Gbud = N^2/25 - beta.
i.e.  V2 + N*Gamma - N^3 + (N/c)*(TV_cut-TV_bad) <= Gamma*(N^2/25 - beta).

Now: TV_cut - TV_bad >= 0 (max-cut consistency). So the (N/c) term is >=0, it makes LHS BIGGER.
A bound V2 <= K*Gamma*Gbud does NOT control N*Gamma - N^3 + (N/c)(TV_cut-TVbad), and in fact gives the WRONG
direction (we'd need V2 SMALL plus the big positive (N/c)(...) term to fit under Gamma*Gbud).
This script empirically measures, per config:
   gapPSC := Gamma*Gbud - S                          (LOAD-PSC margin; >=0 means PSC holds)
   and whether V2 <= K*Gamma*Gbud with K=151/16 has ANY logical bearing (does small-V2 force gapPSC>=0?).
We also report the exact identity check S == V2 + N*Gamma - N^3 + (N/c)(TVcut-TVbad).
Verdict on implication is ANALYTIC (below); the numbers just confirm the identity + that the two are independent.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn

def gmins(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    for s in cuts:
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb: continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0: ok = False; break
            G += (d + 1) ** 2
        if ok: cand.append((s, G))
    if not cand: return adj, []
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm]

def measure(n, adj, side, c=25):
    if not Bconn(n, adj, side): return None
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    N = n; beta = len(M)
    Gamma = sum(F(ell[f]) ** 2 for f in M)
    badset = set((min(a, b), max(a, b)) for a, b in M)
    sumT = sum(T); sumT2 = sum(t * t for t in T)
    # handshake check
    handshake_ok = (sumT == Gamma)
    TVcut = F(0); TVbad = F(0)
    for u in range(n):
        for v in adj[u]:
            if v > u:
                d = abs(T[u] - T[v])
                if side[u] != side[v]: TVcut += d
                else: TVbad += d
    S = (sumT2 - N * sumT) + F(N, c) * (TVcut - TVbad)
    V2 = sumT2 - 2 * N * sumT + N * N * N   # = sum (T-N)^2
    V2_alt = sum((t - F(N)) ** 2 for t in T)
    identity_S = (S == V2 + N * Gamma - N ** 3 + F(N, c) * (TVcut - TVbad))
    Gbud = F(N * N, 25) - beta
    gapPSC = Gamma * Gbud - S
    return dict(N=N, beta=beta, Gamma=Gamma, V2=V2, V2_alt=V2_alt, S=S,
                gapPSC=gapPSC, Gbud=Gbud, TVcut=TVcut, TVbad=TVbad,
                handshake_ok=handshake_ok, identity_S=identity_S,
                psc_ok=(gapPSC >= 0))

print("=== Part 4: identity + LOAD-PSC vs V2-bound (c=25) ===", flush=True)
# sanity on a few census + the binding N=11 + pendant N=12 + Myc(Grotzsch)
cases = []
n, E = dec("J????A?oB~?"); cases.append(("binding-N11", n, E))
# C5 + 7 pendants (N=12)
E12 = [(i, (i + 1) % 5) for i in range(5)] + [(0, 5 + k) for k in range(7)]
cases.append(("C5+7pend-N12", 12, E12))
_mg = mycielski(*mycielski(5, Cn(5))); cases.append(("Myc(Grotzsch)N23", _mg[0], _mg[1]))
cases.append(("C5[2]-N10", 10, [(i*2+a, ((i+1)%5)*2+b) for i in range(5) for a in range(2) for b in range(2)]))

all_id = True; all_hs = True; all_psc = True
for nm, n, E in cases:
    adj, cuts = gmins(n, E)
    for s in (cuts[:1] if cuts else []):
        m = measure(n, adj, s, c=25)
        if m is None:
            print("  %s: no struct" % nm); continue
        all_id &= m['identity_S']; all_hs &= m['handshake_ok']; all_psc &= m['psc_ok']
        print("  %-18s N=%d beta=%d Gamma=%s" % (nm, m['N'], m['beta'], str(m['Gamma'])), flush=True)
        print("       handshake(sumT==Gamma)=%s  S-identity=%s  V2==V2_alt=%s" % (
            m['handshake_ok'], m['identity_S'], m['V2'] == m['V2_alt']), flush=True)
        print("       V2=%s  S(LHS)=%s  Gamma*Gbud(RHS)=%s  gapPSC=%s  PSC_ok=%s" % (
            str(m['V2']), str(m['S']), str(m['Gamma'] * m['Gbud']), str(m['gapPSC']), m['psc_ok']), flush=True)
        # the logical test: V2 <= K*Gamma*Gbud (K=151/16) -- does it bound S?  print both sides
        Kval = F(151, 16)
        print("       V2/(Gamma*Gbud)=%.4f (K-bound side)   ;   S/(Gamma*Gbud)=%.4f (PSC side)" % (
            float(m['V2'] / (m['Gamma'] * m['Gbud'])) if m['Gbud'] > 0 else float('nan'),
            float(m['S'] / (m['Gamma'] * m['Gbud'])) if m['Gbud'] != 0 else float('nan')), flush=True)

print("\n  ALL identity_S=%s  ALL handshake=%s  ALL PSC_ok=%s" % (all_id, all_hs, all_psc), flush=True)
print("""
  ANALYTIC VERDICT:
   S = V2 + N*Gamma - N^3 + (N/c)*(TVcut - TVbad).
   LOAD-PSC-c is  S <= Gamma*Gbud.
   The V2-bound 'V2 <= K*Gamma*Gbud' only UPPER-bounds the V2 summand of S; it says NOTHING about
   the term (N/c)*(TVcut - TVbad) >= 0, which ADDS to S and pushes it toward/over the RHS.
   Bounding V2 from above cannot certify S <= Gamma*Gbud (you'd need to bound the cut-pressure term too,
   and with a constant K=151/16 you'd over-count V2 by ~N). Hence the V2-spectral inequality, even if it
   held with a fixed K, does NOT imply LOAD-PSC. (It is a relative of the WEAKER V2-variance control only.)
""", flush=True)
