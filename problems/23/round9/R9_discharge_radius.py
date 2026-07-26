"""
R9 / Erdos #23 -- LOCALITY RADIUS of the max-cut hypothesis, exactly.

A discharging scheme is local: its rules are verified inside bounded neighbourhoods, so the
only facts about the maximum cut it can use are those shared by every cut that is stable
under switching sets of bounded size.  This script computes, exactly, over the C5 blow-up
family, the largest s such that some graph carries a cut with

      25 * mono > N^2      and      no improving switch of size <= sN,

i.e. the radius any such scheme must exceed.  Vertices inside a class are twins, so counting
vectors k = (k_0..k_4) exhaust all switching sets, and increasing-|k| enumeration gives the
exact minimum improving size.
"""
from fractions import Fraction
from itertools import product
from R9_discharge_lib import bip_blowup_c5


def stats(a, chi):
    N = sum(a)
    mono = sum(a[i] * a[(i + 1) % 5] for i in range(5) if chi[i] == chi[(i + 1) % 5])
    return N, mono


def sigma(a, chi):
    out = []
    for i in range(5):
        s = o = 0
        for j in ((i - 1) % 5, (i + 1) % 5):
            if chi[j] == chi[i]:
                s += a[j]
            else:
                o += a[j]
        out.append(o - s)
    return out


def delta(a, chi, k):
    d = 0
    for i in range(5):
        j = (i + 1) % 5
        if chi[i] == chi[j]:
            d += (a[i] - k[i]) * (a[j] - k[j]) + k[i] * k[j] - a[i] * a[j]
        else:
            d += (a[i] - k[i]) * k[j] + k[i] * (a[j] - k[j])
    return d


def comps(s, bounds, idx=0):
    """all vectors k >= 0 with sum s and k_i <= bounds[i]"""
    if idx == 4:
        if s <= bounds[4]:
            yield (s,)
        return
    for v in range(min(s, bounds[idx]) + 1):
        for rest in comps(s - v, bounds, idx + 1):
            yield (v,) + rest


def min_improving(a, chi):
    """exact smallest improving switch, by increasing size"""
    N = sum(a)
    for s in range(1, N + 1):
        for k in comps(s, a):
            if delta(a, chi, k) < 0:
                return s, k
    return None


def scan(N):
    best = None
    npairs = 0
    for a0 in range(N + 1):
        for a1 in range(N + 1 - a0):
            for a2 in range(N + 1 - a0 - a1):
                for a3 in range(N + 1 - a0 - a1 - a2):
                    a = [a0, a1, a2, a3, N - a0 - a1 - a2 - a3]
                    for cm in range(1, 31):
                        chi = [(cm >> i) & 1 for i in range(5)]
                        Nn, mono = stats(a, chi)
                        if 25 * mono <= Nn * Nn:
                            continue
                        if any(s < 0 for s in sigma(a, chi)):
                            continue
                        npairs += 1
                        r = min_improving(a, chi)
                        if r is None:
                            continue
                        ratio = Fraction(r[0], Nn)
                        if best is None or ratio > best[0]:
                            best = (ratio, a[:], chi[:], r, mono)
    return best, npairs


print("N   #violating locally-optimal class cuts   max radius   witness")
allbest = None
for N in (10, 15, 20, 25, 30, 35, 40, 45):
    best, npairs = scan(N)
    if best is None:
        print(f"{N:3d} {npairs:6d}   none")
        continue
    ratio, a, chi, r, mono = best
    print(f"{N:3d} {npairs:6d}   {str(ratio):>7s} = {float(ratio):.4f}   "
          f"a={a} chi={chi} mono={mono} (bip={bip_blowup_c5(a)}, N^2/25={Fraction(N*N,25)}) "
          f"switch={r[1]}")
    if allbest is None or ratio > allbest[0]:
        allbest = (ratio, N, a, chi, r, mono)
print()
ratio, N, a, chi, r, mono = allbest
print(f"MAXIMUM over the scanned range: {ratio} = {float(ratio):.4f} N")
print(f"  witness C5{a}, N={N}, class cut chi={chi}, mono={mono}, 25*mono={25*mono} > "
      f"N^2={N*N}, bip={bip_blowup_c5(a)} <= {Fraction(N*N,25)}")
print(f"  smallest improving switch: {r[0]} vertices {r[1]}")
print()
print("Reading: a local rule that only knows 'no improving switch of size <= sN exists'")
print(f"is unusable below s = {float(ratio):.4f}; verifying stability at that radius means")
print("checking exponentially many (>= C(N, N/4)) switching sets, which no discharging")
print("rule with bounded-radius verification does.")
