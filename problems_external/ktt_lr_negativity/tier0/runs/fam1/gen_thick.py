#!/usr/bin/env python
"""Thickened cell: lam=(2t,2t,t), mu=(k,3t,2t,t), nu=(k+t,4t,3t,2t,t)
   (t=1 is the verified non-lattice base cell), plus all two-box perturbations.
usage: gen_thick.py OUT TMIN TMAX KMIN KMAX"""
import sys, itertools
sys.path.insert(0, ".")
from gen_fam1c import valid, slots, apply_delta, deltas


def base(t, k):
    return ([2 * t, 2 * t, t], [k, 3 * t, 2 * t, t], [k + t, 4 * t, 3 * t, 2 * t, t])


def main():
    out = sys.argv[1]
    tmin, tmax, kmin, kmax = map(int, sys.argv[2:6])
    seen, order = set(), []
    for t in range(tmin, tmax + 1):
        for k in range(kmin, kmax + 1):
            trip = base(t, k)
            if sum(trip[0]) + sum(trip[1]) != sum(trip[2]):
                continue
            S = slots(trip)
            for mv in [[]] + deltas(S, 2, 2):
                q = apply_delta(trip, mv)
                if q and q not in seen:
                    seen.add(q); order.append(q)
    with open(out, "w") as f:
        for (l, m, n) in order:
            f.write("%s;%s;%s\n" % (",".join(map(str, l)), ",".join(map(str, m)),
                                    ",".join(map(str, n))))
    sys.stderr.write("emitted %d\n" % len(order))


if __name__ == "__main__":
    main()
