#!/usr/bin/env python3
"""
fam12_target2.py -- same exact enumeration as fam12_target.py but with the
h*-degree constraint  s = deg h* <= d - k  imposed (k = 1 by default).

Motivation: Hibi's inequality h*_d <= h*_1 holds for LATTICE polytopes, so
h*_1 = 0 forces h*_d = 0 there.  Hive polytopes need not be lattice polytopes
(the known refuter has half-integral vertices), so BOTH regimes are reported;
the s <= d-1 column is the conservative target list.
"""
import sys
from fam12_target import coeffs_of_hstar, _compositions


def search(d, k=1, Vmax=40, h1=0):
    top = d - k                      # last allowed nonzero index
    if top < 2:
        return None, []
    for V in range(2, Vmax + 1):
        rem = V - 1 - h1
        if rem < 0:
            continue
        found = []
        for h in _compositions(rem, top - 1):     # positions 2..top
            hv = [1, h1] + list(h) + [0] * (d - top)
            c = coeffs_of_hstar(hv, d)
            neg = [i for i, x in enumerate(c) if x < 0]
            if neg:
                found.append((hv, neg, [str(x) for x in c]))
        if found:
            return V, found
    return None, []


if __name__ == "__main__":
    dmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print("=== s <= d-%d ===" % k)
    for d in range(3, dmax + 1):
        V, found = search(d, k=k, Vmax=40)
        if V is None:
            print("d=%2d  none with V<=40" % d)
            continue
        print("d=%2d  Vmin=%2d  #witnesses=%d" % (d, V, len(found)))
        for hv, neg, c in found[:10]:
            print("        h*=%s  negidx=%s" % (hv, neg))
