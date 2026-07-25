"""R8: analyse the exact census output (R8_census_n*_q*.txt).

Questions answered exactly, for every connected triangle-free graph on n <= 8 vertices and
every integer weighting with denominator q:
  Q1. Is 25*M(a) <= q^2 always?  (the conjecture on this finite grid)
  Q2. Which graphs attain 25*M = q^2, and is that exactly the class containing an induced C5?
  Q3. What does the ARGMAX SET look like -- is it exactly the set of balanced C5-blow-up
      weightings (i.e. does the support split into 5 classes of weight q/5 forming a
      blow-up pattern)?
  Q4. For graphs with an induced C5, what is the largest value of 25M/q^2 attained by a
      weighting that is NOT a balanced blow-up weighting?  (the stability margin)
"""
import sys, os, re, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import from_g6, Graph


def parse(fn):
    out = []
    cur = None
    for line in open(fn):
        if line.startswith("G "):
            if cur:
                out.append(cur)
            t = line.split()
            d = dict(g6=t[1])
            for kv in t[2:]:
                k, v = kv.split("=")
                d[k] = int(v)
            cur = dict(hdr=d, argmax=[], gridloc=None, locreps=[], profile=None)
        elif line.strip().startswith("ARGMAX"):
            cur["argmax"].append([int(z) for z in line.split()[1:]])
        elif line.strip().startswith("GRIDLOCMAX"):
            cur["gridloc"] = [tuple(int(z) for z in kv.split(":")) for kv in line.split()[1:]]
        elif line.strip().startswith("LOCREP"):
            t = line.split()
            cur["locreps"].append((int(t[1]), [int(z) for z in t[3:]]))
        elif line.strip().startswith("PROFILE"):
            t = line.split()
            cur["profile"] = [int(z) for z in t[3:]]
    if cur:
        out.append(cur)
    return out


def is_balanced_blowup_weighting(g, a, q):
    """True iff supp(a) can be partitioned into 5 classes each of weight q/5 such that
    every edge of H[supp] joins consecutive classes (i.e. a is a balanced C5-blow-up weighting)."""
    if q % 5:
        return False
    supp = [v for v in range(g.n) if a[v] > 0]
    k = len(supp)
    if k < 5:
        return False
    target = q // 5
    for assign in itertools.product(range(5), repeat=k):
        if len(set(assign)) != 5:
            continue
        cl = {v: assign[i] for i, v in enumerate(supp)}
        w = [0] * 5
        for i, v in enumerate(supp):
            w[assign[i]] += a[v]
        if any(wi != target for wi in w):
            continue
        ok = True
        for (u, v) in g.edges:
            if u in cl and v in cl:
                du = (cl[u] - cl[v]) % 5
                if du not in (1, 4):
                    ok = False
                    break
        if ok:
            return True
    return False


def main(files):
    for fn in files:
        rows = parse(fn)
        q = rows[0]["hdr"]["q"]
        n = rows[0]["hdr"]["n"]
        viol = [r for r in rows if 25 * r["hdr"]["bestM"] > q * q]
        tight = [r for r in rows if 25 * r["hdr"]["bestM"] == q * q]
        hasC5 = [r for r in rows if r["hdr"]["nC5"] > 0]
        print(f"\n=== {os.path.basename(fn)}   n={n}  q={q}  graphs={len(rows)} ===")
        print(f"  violations of 25M <= q^2 : {len(viol)}")
        print(f"  graphs with an induced C5: {len(hasC5)}")
        print(f"  graphs attaining 25M = q^2 (psi = 1/25): {len(tight)}")
        s1 = set(r["hdr"]["g6"] for r in tight)
        s2 = set(r["hdr"]["g6"] for r in hasC5)
        print(f"  {{attain 1/25}} == {{contain induced C5}} ? {s1 == s2}"
              + ("" if s1 == s2 else f"   only-C5: {sorted(s2-s1)[:6]}  only-tight: {sorted(s1-s2)[:6]}"))
        # structure of the argmax vectors that were printed
        bad = []
        for r in tight:
            g = from_g6(r["hdr"]["g6"])
            for a in r["argmax"]:
                if not is_balanced_blowup_weighting(g, a, q):
                    bad.append((r["hdr"]["g6"], a))
        print(f"  printed ARGMAX vectors that are NOT balanced C5-blow-up weightings: {len(bad)}")
        for b in bad[:6]:
            print("     ", b)
        # top few non-tight graphs with an induced C5? (none expected)
        vals = sorted(set(F(25 * r["hdr"]["bestM"], q * q) for r in rows), reverse=True)
        print(f"  distinct values of 25*maxM/q^2 over all graphs (top 8): "
              f"{[str(v) for v in vals[:8]]}")
        # runner-up value among graphs WITHOUT an induced C5
        noc5 = [r for r in rows if r["hdr"]["nC5"] == 0]
        if noc5:
            mx = max(noc5, key=lambda r: r["hdr"]["bestM"])
            print(f"  best graph WITHOUT an induced C5: {mx['hdr']['g6']} "
                  f"25M/q^2 = {F(25*mx['hdr']['bestM'], q*q)} = {float(F(25*mx['hdr']['bestM'], q*q)):.6f}")


if __name__ == "__main__":
    main(sys.argv[1:])
