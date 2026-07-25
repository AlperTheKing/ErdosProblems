#!/usr/bin/env python3
"""First-improvement stochastic climb of R_1 (faster than full greedy).
Accepts the first randomly-tried neighbor that improves R_1.  Logs the
exact a_1 sign.  a_1<0 iff R_1>1 => KTT counterexample.
Usage: climb_fast.py r "lam" "mu" "nu" [maxiter] [node_cap] [seed]"""
import sys, os, random, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hillclimb_R1 import neighbors, score, canon


def main():
    r = int(sys.argv[1])
    lam = tuple(int(x) for x in sys.argv[2].split(","))
    mu = tuple(int(x) for x in sys.argv[3].split(","))
    nu = tuple(int(x) for x in sys.argv[4].split(","))
    maxiter = int(sys.argv[5]) if len(sys.argv) > 5 else 200
    node_cap = int(sys.argv[6]) if len(sys.argv) > 6 else 5 * 10 ** 9
    random.seed(int(sys.argv[7]) if len(sys.argv) > 7 else 1)
    cache = {}
    lam, mu, nu = canon(lam, mu, nu)
    cur = score(lam, mu, nu, node_cap, cache)
    print("seed R1=%.6f d=%d M=%d nu=%s" % (float(cur[0]), cur[1], cur[2], nu), flush=True)
    best = cur[0]
    t0 = time.time()
    for it in range(maxiter):
        nbrs = neighbors(lam, mu, nu, r)
        random.shuffle(nbrs)
        moved = False
        for (L, Mu, N) in nbrs:
            s = score(L, Mu, N, node_cap, cache)
            if s is None or s[0] is None:
                continue
            if s[0] > cur[0]:
                lam, mu, nu, cur = L, Mu, N, s
                moved = True
                if s[0] > best:
                    best = s[0]
                    print("it %3d R1=%.6f d=%d M=%d nu=%s lam=%s mu=%s (t=%.0fs)" %
                          (it, float(s[0]), s[1], s[2], nu, lam, mu, time.time() - t0),
                          flush=True)
                    if s[0] > 1:
                        print("*** R1>1 => a_1<0 => COUNTEREXAMPLE ***", lam, mu, nu,
                              "hstar=", s[3], flush=True)
                        return
                break
        if not moved:
            print("local max it=%d R1=%.6f nu=%s lam=%s mu=%s d=%d M=%d (t=%.0fs)" %
                  (it, float(cur[0]), nu, lam, mu, cur[1], cur[2], time.time() - t0),
                  flush=True)
            return
    print("maxiter reached R1=%.6f nu=%s lam=%s mu=%s" % (float(cur[0]), nu, lam, mu))


if __name__ == "__main__":
    main()
