"""
R9 / Erdos #23 -- the one global potential with the right shape: the MOTZKIN-STRAUS DEFICIT.

Phi(x) = 1/4 - W(x) >= 0  for triangle-free H (Motzkin-Straus), where W(x) = sum over edges
of x_u x_v.  The unique linear certificate that is tight at BOTH extremal points --
(W,psi) = (1/5, 1/25) at C5[n] and (W,psi) = (1/4, 0) at K_{m,m} -- is

        psi(H,x) + (4/5) W(x)  <=  1/5              (MS-deficit certificate)

which delivers psi <= 1/25 exactly on the half-space W >= 1/5.  This script tests it
exactly, and tests the complementary low-density piece psi <= W/5 that would close the
other half.

Also: a census gate for the T4 claim that the amortised deletion mechanism is confined to
the graphs on which the un-amortised one-step induction already works.
"""
import random
from fractions import Fraction
from R9_discharge_lib import (witnesses, psi_exact, W_mass, num_edges, bip_exact,
                              edges, dp_greedy_value, g6_decode, degrees,
                              make_c5_blowup, bip_blowup_c5)

def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def ms_test(n, adj, x):
    p = psi_exact(n, adj, x)
    w = W_mass(n, adj, x)
    return p, w, (p + Fraction(4, 5) * w <= Fraction(1, 5)), (p <= w / 5)


hdr("MS-1.  uniform weights on the mandated witnesses")
print(f"{'graph':26s} {'psi':>10s} {'W':>10s} {'psi+4W/5<=1/5':>14s} {'psi<=W/5':>10s}")
for (name, n, adj) in witnesses():
    x = [Fraction(1, n)] * n
    p, w, ok1, ok2 = ms_test(n, adj, x)
    print(f"{name:26s} {str(p):>10s} {str(w):>10s} {str(ok1):>14s} {str(ok2):>10s}"
          f"{'   <== psi<=W/5 FALSE' if not ok2 else ''}")

hdr("MS-2.  random exact rational weightings (uniform over integer compositions)")
random.seed(20260726)
fails1 = fails2 = 0
worst1 = None
trials = 0
for (name, n, adj) in witnesses():
    for q in (5, 7, 11, 13, 20):
        for _ in range(60):
            # random composition of q into n nonneg parts
            cuts = sorted(random.randint(0, q) for _ in range(n - 1))
            parts = [b - a for a, b in zip([0] + cuts, cuts + [q])]
            x = [Fraction(p, q) for p in parts]
            p, w, ok1, ok2 = ms_test(n, adj, x)
            trials += 1
            if not ok1:
                fails1 += 1
                print(f"   MS-LINE FAILS: {name} x={parts}/{q} psi={p} W={w}")
            if not ok2:
                fails2 += 1
            margin = Fraction(1, 5) - p - Fraction(4, 5) * w
            if worst1 is None or margin < worst1[0]:
                worst1 = (margin, name, parts, q, p, w)
print(f"  trials={trials}   MS-line violations={fails1}   psi<=W/5 violations={fails2}")
m, name, parts, q, p, w = worst1
print(f"  tightest MS-line margin: {m} at {name} x={parts}/{q}, psi={p}, W={w}")

hdr("MS-3.  the C5 blow-up family (where the certificate must be exactly tight)")
for a in ([1]*5, [2]*5, [3]*5, [3,1,2,2,1], [7,7,12,7,12], [2,2,2,2,0], [7,2,7,7,2]):
    N = sum(a)
    b = bip_blowup_c5(a)
    x = [Fraction(1, N)] * N
    W = Fraction(sum(a[i]*a[(i+1) % 5] for i in range(5)), N*N)
    psi = Fraction(b, N*N)
    ok1 = psi + Fraction(4,5)*W <= Fraction(1,5)
    print(f"  C5{str(a):18s} N={N:3d} psi={str(psi):>10s} W={str(W):>10s} "
          f"MS-line ok={ok1}  margin={Fraction(1,5)-psi-Fraction(4,5)*W}"
          f"   psi<=W/5: {psi <= W/5}")

hdr("MS-4.  verdict on the MS-deficit potential")
print("""  The certificate psi + (4/5)W <= 1/5 survives every exact test above, but its
  consequence is EXACTLY the already-published dense half: it yields psi <= 1/25 only
  when W >= 1/5, i.e. |E| >= N^2/5, and that regime is closed by
  Erdos-Faudree-Pach-Spencer (1988): bip <= |E| - 4|E|^2/N^2, which equals N^2/25 at
  |E| = N^2/5 and is decreasing beyond.  Comparison of the two bounds on the dense half:""")
print(f"  {'|E|/N^2':>9s} {'MS-line: 1/5-4|E|/(5N^2)':>26s} {'EFPS: |E|/N^2-4(|E|/N^2)^2':>28s}")
for num, den in ((1,5),(21,100),(11,50),(23,100),(6,25),(1,4)):
    e = Fraction(num, den)
    print(f"  {str(e):>9s} {str(Fraction(1,5)-Fraction(4,5)*e):>26s} {str(e-4*e*e):>28s}")
print("""  Both vanish at |E| = N^2/4 and both give N^2/25 at |E| = N^2/5; the MS line is the
  slightly stronger of the two strictly between.  Neither says anything in the open band
  N^2/20 < |E| < N^2/5, which is where the problem lives.  The complementary low-density
  piece psi <= W/5 (which together with the MS line would give exactly 1/25 at the crossing
  W = 1/5) is FALSE: see the N=14 witness above (bip = 7 > 32/5 = |E|/5).""")

hdr("T4-CENSUS.  gate: on every triangle-free graph of the census, is the amortised")
print("  mechanism (V <= N^2/25) confined to graphs where the plain one-step induction")
print("  (floor(delta/2) <= (2N-1)/25) already works?")
import os
src = None
for cand in (r"..\round7\audit_tf9.g6", r"..\round7\tf9.g6", r"..\round7\audit_tf8.g6"):
    if os.path.exists(cand):
        src = cand
        break
print(f"  census file: {src}")
if src:
    tot = mech = plain = both = 0
    viol = 0
    with open(src) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n, adj = g6_decode(line)
            m = num_edges(n, adj)
            V, _ = dp_greedy_value(n, adj)
            b = bip_exact(n, adj)
            assert V >= b and V >= Fraction(m - n, 2)
            tot += 1
            okm = V <= Fraction(n * n, 25)
            okp = min(degrees(n, adj)) // 2 <= Fraction(2 * n - 1, 25)
            mech += okm
            plain += okp
            both += (okm and okp)
            if okm and not okp:
                viol += 1
    print(f"  graphs={tot}  mechanism works={mech}  plain step works={plain}  "
          f"mechanism-but-not-plain={viol}")
    print(f"  containment 'mechanism => plain step' holds on the whole census: {viol == 0}")
