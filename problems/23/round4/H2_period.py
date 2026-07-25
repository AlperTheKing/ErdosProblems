"""H2_period.py -- exact evaluation of PERIODIC weightings on Gamma_m.

A period-p weighting on Gamma_{p*n} is w[i] = v[i mod p].  These are exactly the
directions that survived the flat-space analysis at m=21, 39 (period 3).
Everything below is exact integer arithmetic.
"""
import sys, itertools, math
from H2_core import edges, total_W, arcbound_fast


def scan_period(m, p, R):
    assert m % p == 0
    E = edges(m)
    worstA = None   # smallest S^2 - 25*AB
    worstW = None   # smallest W^2 - AB*S^2
    nviolA = nviolW = 0
    for v in itertools.product(range(0, R + 1), repeat=p):
        if sum(v) == 0:
            continue
        if math.gcd(*v) > 1 if p > 1 else False:
            continue
        w = [v[i % p] for i in range(m)]
        S = sum(w); W = total_W(w, E)
        AB = arcbound_fast(w, E, m)
        a = S * S - 25 * AB
        b = W * W - AB * S * S
        if a < 0:
            nviolA += 1
            print(f"  *** ARC VIOLATION m={m} p={p} v={v} S^2={S*S} 25AB={25*AB}")
        if b < 0:
            nviolW += 1
            print(f"  *** WSQ VIOLATION m={m} p={p} v={v} W^2={W*W} AB*S^2={AB*S*S}")
        if worstA is None or a * worstA[1] < worstA[0] * (S * S):   # compare a/S^2
            worstA = (a, S * S, v)
        if worstW is None or b * worstW[1] < worstW[0] * (W * W):
            worstW = (b, W * W, v)
    return worstA, worstW, nviolA, nviolW


if __name__ == "__main__":
    jobs = []
    for m in range(6, 49):
        for p in range(1, 7):
            if m % p == 0 and m // p >= 4:
                jobs.append((m, p))
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for (m, p) in jobs:
        if R ** p > 400000:
            continue
        wa, ww, na, nw = scan_period(m, p, R)
        print(f"m={m:3d} p={p} R={R}: ARCviol={na} WSQviol={nw} "
              f"minARCslack={wa[0]}/{wa[1]} at {wa[2]}   minWSQslack={ww[0]}/{ww[1]} at {ww[2]}")
