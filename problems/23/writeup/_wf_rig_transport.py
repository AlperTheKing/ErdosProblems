"""ROUTE (d) -- LEVEL-VARIABLE TRANSPORT / amortization gate.

THE SINGLE CHECKABLE INEQUALITY (PREFIX-LOAD-PSC-5 / running-balance potential Phi):
  For every threshold tau >= 0,
     Phi(tau) := integral_0^tau [ (N^2 - 25 beta + 25 N - 50 s) |H_s|  -  5N (dB(H_s) - dM(H_s)) ] ds  >= 0,
  where beta=|M|, H_s={v:T_v>s}, dB/dM = #cut/#bad boundary edges of H_s, sigma=dB-dM>=0 (max-cut).
  Phi is the running balance ("potential"). Equivalently per T-filtration slab [t_j,t_j+w_j):
     contrib_j = w_j*|H_j|*( (N^2-25 beta) - 25(2 t_j + w_j - N) )  -  5N*w_j*sigma_j,
  Phi(tau) = sum_{slabs ending <= tau} contrib_j   (we test Phi at EVERY breakpoint = its minima).

REDUCTION (exact algebra, see header of algebra_check):
  tau=inf endpoint:  Phi(inf) = 25*( Gamma(N^2/25 - beta) - [ sum_v T_v(T_v-N) + (N/5)(TV_cut-TV_bad) ] ),
  using coarea  int 2s|H_s|=sum T^2, int|H_s|=Gamma, int(dB-dM)=TV_cut-TV_bad.
  Phi(inf) >= 0  <=>  LOAD-PSC-5 (master, c=5, the harsher one).
  LOAD-PSC-5  =>  LOAD-PSC-25  =>  Erdos beta <= N^2/25.
  PREFIX-LOAD-PSC-5 (Phi(tau)>=0 for ALL tau) is STRICTLY STRONGER than the tau=inf endpoint:
  it is the amortized statement that every prefix of withdrawals is paid by banked deposit.

TRANSPORT / DEPOSIT-WITHDRAWAL split (route-d diagnostic): split each slab at s=N/2.
  DEPOSIT mass  (the part of contrib_j on levels s<=N/2; coeff (25N-50s)>=0 there) -- termwise >=0-shaped.
  WITHDRAWAL mass (levels s>N/2) -- can be negative; must be covered by accumulated deposit.
  We report min running balance (margin) + min over the suffix split, + the binding config.

EXACT Fraction throughout. Battery = the standing battery (two-lane, k-lane, census N=7..11 ALL gmin cuts,
C5/C7/C9[t], non-uniform blow-ups, Grotzsch, Myc(Grotzsch) N=23, M(C7), M(C9), glued islands).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary(n, adj, side, Hset):
    dB = dM = 0
    for u in Hset:
        for v in adj[u]:
            if v in Hset: continue
            if side[u] != side[v]: dB += 1
            else: dM += 1
    return dB, dM

def chk(name, n, adj, side, acc):
    if not Bconn(n, adj, side): return
    st = struct_for_side(n, adj, side)
    if st is None: return
    M, ell, T, mu, cyc = st
    if not M: return
    m = len(M); D = F(n*n) - 25*m          # D = N^2 - 25 beta
    Nh = F(n, 2)                            # the split level s = N/2
    levels = sorted(set([F(0)] + [v for v in set(T) if v > 0]))
    # build per-slab data
    slabs = []
    for j in range(len(levels)-1):
        tj = levels[j]; wj = levels[j+1] - levels[j]
        Hset = set(v for v in range(n) if T[v] > tj)
        if not Hset: continue
        Hsz = len(Hset); dB, dM = boundary(n, adj, side, Hset); sig = dB - dM
        # contrib_j = wj*Hsz*( D - 25*(2 tj + wj - N) ) - 5N*wj*sig
        contrib = wj*Hsz*(D - 25*(2*tj + wj - F(n))) - 5*F(n)*wj*sig
        slabs.append((tj, wj, Hsz, sig, contrib))
    acc['n'] += 1
    # ---- running balance Phi at every breakpoint; record minimum (the binding prefix) ----
    cum = F(0); mn = F(0); mn_at = None
    # Phi(0)=0 included as a baseline minimum candidate
    for (tj, wj, Hsz, sig, contrib) in slabs:
        cum += contrib
        if cum < mn:
            mn = cum; mn_at = (float(tj+wj), Hsz, sig)
    if mn < acc['minPhi'][0]:
        acc['minPhi'] = (mn, name, n, m, mn_at)
    if mn < 0:
        acc['vPhi'] += 1
        if acc['fPhi'] is None:
            acc['fPhi'] = (name, ''.join(map(str, side)), n, m, float(mn), mn_at)
    # ---- transport diagnostic: total deposit (s<=N/2) and total withdrawal (s>N/2) ----
    dep = F(0); wd = F(0)
    for (tj, wj, Hsz, sig, contrib) in slabs:
        lo = tj; hi = tj + wj
        # split contrib at s=N/2 along the s-integral; the |H|,sig are constant on the slab so we
        # split the integrand exactly. integrand(s)=(D+25N-50s)Hsz - 5N sig (constant in s except -50s Hsz).
        # contrib over [a,b] = (D+25N)*(b-a)*Hsz - 25*(b^2-a^2)*Hsz - 5N*(b-a)*sig
        def part(a, b):
            return (D+25*F(n))*(b-a)*Hsz - 25*(b*b-a*a)*Hsz - 5*F(n)*(b-a)*sig
        if hi <= Nh:
            dep += part(lo, hi)
        elif lo >= Nh:
            wd += part(lo, hi)
        else:
            dep += part(lo, Nh); wd += part(Nh, hi)
    # record minimum deposit and the (deposit+withdrawal balance) -- both should be: dep>=0, dep+wd=Phi(inf)>=0
    if dep < acc['minDep'][0]:
        acc['minDep'] = (dep, name, n, m)
    if wd < acc['minWd'][0]:
        acc['minWd'] = (wd, name, n, m)
    tot = dep + wd
    if tot < acc['minTot'][0]:
        acc['minTot'] = (tot, name, n, m)
    if dep < 0:
        acc['depNeg'] += 1

def blowup(parts):
    mm = len(parts); off = [0]*(mm+1)
    for i in range(mm): off[i+1] = off[i] + parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i+1) % mm
        for a in range(off[i], off[i+1]):
            for b in range(off[j], off[j+1]): EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))

def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E: a[x].add(y); a[y].add(x)
    return a

if __name__ == "__main__":
    acc = {'n': 0, 'vPhi': 0, 'fPhi': None, 'depNeg': 0,
           'minPhi': (F(10**18), '', '', '', None),
           'minDep': (F(10**18), '', '', ''), 'minWd': (F(10**18), '', '', ''),
           'minTot': (F(10**18), '', '', '')}
    print("=== ROUTE-d TRANSPORT: PREFIX-LOAD-PSC-5 running-balance Phi(tau)>=0 (EXACT) ===", flush=True)
    for L in range(8, 21, 2):
        n, E, side, _ = build_two_lane(L); chk("two-lane-L%d" % L, n, adj_of(n, E), side, acc)
    for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap); n, E, side, bad = build_k_lane(Ll, k, bad)
        chk("klane-L%dk%d" % (Ll, k), n, adj_of(n, E), side, acc)
    print("  two-lane+k-lane: vPhi=%d minPhi=%s depNeg=%d" % (acc['vPhi'], float(acc['minPhi'][0]), acc['depNeg']), flush=True)
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        a0 = acc['vPhi']
        for g6 in outg:
            n, E = dec(g6); adj, cuts = gmins(n, E)
            for s in cuts: chk("cen%s" % g6, n, adj, s, acc)
        print("  census N=%d (vPhi+%d)" % (nn, acc['vPhi']-a0), flush=True)
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t]*cyc)
            if n > 26: continue
            adj, cuts = gmins(n, E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]" % (cyc, t), n, adj, s, acc)
    for parts in [[2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2], [1, 3, 2, 2, 3]]:
        n, E = blowup(parts)
        if n > 26: continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []): chk("nu%s" % parts, n, adj, s, acc)
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    def bridge(b1, b2, u, v):
        nn, E = union_disjoint(b1, b2); n1 = b1[0]; return nn, E + [(u, n1+v)]
    for name, (nn, E) in [("Grotzsch", grot), ("Myc(Grotzsch)", mycg), ("M(C7)", mycielski(7, Cn(7))),
                          ("M(C9)", mycielski(9, Cn(9))),
                          ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
                          ("C9|C9", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]: chk(name, nn, adj, s, acc)
    print("  blow-ups + Mycielskians + glued done", flush=True)
    print("\n  total configs=%d" % acc['n'], flush=True)
    print("  PREFIX-LOAD-PSC-5 (Phi>=0): violations=%d  min running balance=%s" % (acc['vPhi'], float(acc['minPhi'][0])), flush=True)
    print("    binding config: %s" % (acc['minPhi'][1:],), flush=True)
    if acc['fPhi']: print("    first violation: %s" % (acc['fPhi'],), flush=True)
    print("  DEPOSIT (s<=N/2) min=%s at %s ; deposit<0 count=%d" % (float(acc['minDep'][0]), acc['minDep'][1:], acc['depNeg']), flush=True)
    print("  WITHDRAWAL (s>N/2) min=%s at %s" % (float(acc['minWd'][0]), acc['minWd'][1:]), flush=True)
    print("  TOTAL Phi(inf)=dep+wd min=%s at %s (== LOAD-PSC-5 margin*1)" % (float(acc['minTot'][0]), acc['minTot'][1:]), flush=True)
    print("  === PREFIX-LOAD-PSC-5 %s ===" % ("HOLDS" if not acc['vPhi'] else "FAILS"), flush=True)
