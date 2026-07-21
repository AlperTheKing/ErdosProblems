#!/usr/bin/env python3
"""Aggregate the FAM-14 control lane. All exact; Fractions parsed from strings."""
import collections
import glob
import json
import sys
from fractions import Fraction


def load(paths):
    recs = []
    for p in paths:
        for l in open(p, encoding="utf-8"):
            l = l.strip()
            if l:
                recs.append(json.loads(l))
    return recs


def main(argv):
    paths = []
    for a in argv[1:]:
        paths.extend(glob.glob(a))
    recs = load(paths)
    # de-dup by triple
    uniq = {}
    for r in recs:
        uniq[(tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))] = r
    recs = list(uniq.values())

    st = collections.Counter(r.get("status", "?") for r in recs)
    ok = [r for r in recs if r.get("status") == "OK"]
    empty = [r for r in recs if r.get("status") == "EMPTY"]
    unres = [r for r in recs if str(r.get("status", "")).startswith("UNRESOLVED")]

    print("triples (unique): %d" % len(recs))
    for k, v in sorted(st.items()):
        print("  status %-28s %d" % (k, v))

    pos = [r for r in ok if r.get("d", -1) >= 0]
    print("\nresolved non-empty: %d   empty (c=0, P==0): %d   unresolved: %d"
          % (len(pos), len(empty), len(unres)))

    # (i) base rate of h*_1 = 0
    byd = collections.defaultdict(lambda: [0, 0])
    h1zero = 0
    for r in pos:
        d = r["d"]
        byd[d][0] += 1
        if r.get("hstar_1") == 0:
            byd[d][1] += 1
            h1zero += 1
    print("\n(i) h*_1 = 0 base rate: %d/%d = %.4f"
          % (h1zero, len(pos), h1zero / max(1, len(pos))))
    print("    by d:  d  n   h1=0   rate")
    for d in sorted(byd):
        n, z = byd[d]
        print("        %3d %5d %5d  %.4f" % (d, n, z, z / n))

    # h*_1 = 0 with d >= 2 (the only nontrivial stratum -- d<=1 forces V=1)
    nt = [r for r in pos if r["d"] >= 2]
    ntz = [r for r in nt if r.get("hstar_1") == 0]
    print("    nontrivial stratum d>=2: %d;  of those h*_1=0: %d (%.4f)"
          % (len(nt), len(ntz), len(ntz) / max(1, len(nt))))
    print("    d>=2 AND h*_1=0 AND V>=2: %d"
          % len([r for r in ntz if r.get("hstar_sum", 0) >= 2]))

    # (ii) volume distribution
    vols = collections.Counter(r.get("hstar_sum") for r in pos)
    print("\n(ii) normalized volume V = sum h* distribution (resolved non-empty):")
    for v in sorted(x for x in vols if x is not None):
        print("      V=%-6d %6d" % (v, vols[v]))
    mx = max(pos, key=lambda r: r.get("hstar_sum", 0)) if pos else None
    if mx:
        print("    max V = %d at lam=%s mu=%s nu=%s (d=%d, h*_1=%d, h*=%s)"
              % (mx["hstar_sum"], mx["lam"], mx["mu"], mx["nu"], mx["d"],
                 mx["hstar_1"], mx["hstar"]))
    z = [r for r in pos if r.get("hstar_1") == 0]
    if z:
        mz = max(z, key=lambda r: r.get("hstar_sum", 0))
        print("    max V at h*_1=0 : %d  lam=%s mu=%s nu=%s d=%d h*=%s"
              % (mz["hstar_sum"], mz["lam"], mz["mu"], mz["nu"], mz["d"],
                 mz["hstar"]))
    z2 = [r for r in pos if (r.get("hstar_1") or 0) <= 2]
    if z2:
        mz2 = max(z2, key=lambda r: r.get("hstar_sum", 0))
        print("    max V at h*_1<=2: %d  lam=%s mu=%s nu=%s d=%d h*_1=%d h*=%s"
              % (mz2["hstar_sum"], mz2["lam"], mz2["mu"], mz2["nu"], mz2["d"],
                 mz2["hstar_1"], mz2["hstar"]))

    # (iii) global minimum monomial coefficient
    best = None
    for r in pos:
        for cs in r.get("coeffs_low_to_high", []):
            c = Fraction(cs)
            if best is None or c < best[0]:
                best = (c, r)
    if best:
        print("\n(iii) global minimum monomial coefficient = %s  (lam=%s mu=%s nu=%s, poly=%s)"
              % (best[0], best[1]["lam"], best[1]["mu"], best[1]["nu"],
                 best[1].get("poly")))

    # (iv) any negative coefficient
    hits = [r for r in pos if r.get("neg")]
    print("\n(iv) triples with a strictly NEGATIVE coefficient: %d" % len(hits))
    for r in hits:
        print("   HIT lam=%s mu=%s nu=%s d=%d h*=%s poly=%s"
              % (r["lam"], r["mu"], r["nu"], r["d"], r["hstar"], r.get("poly")))

    # per-r breakdown
    print("\n(v) per-r breakdown (unbiased two-stage design, pooled over N):")
    print("      r  sampled  empty  resolved  d>=2  h1=0&d>=2  maxV  maxV@h1=0")
    for rr in sorted({x["r"] for x in recs}):
        sub = [x for x in recs if x["r"] == rr]
        se = [x for x in sub if x.get("status") == "EMPTY"]
        so = [x for x in sub if x.get("status") == "OK"]
        s2 = [x for x in so if x.get("d", -1) >= 2]
        sz = [x for x in s2 if x.get("hstar_1") == 0]
        mv = max([x.get("hstar_sum", 0) for x in so] or [0])
        mz = max([x.get("hstar_sum", 0) for x in so if x.get("hstar_1") == 0] or [0])
        print("      %2d %7d %6d %9d %5d %10d %5d %9d"
              % (rr, len(sub), len(se), len(so), len(s2), len(sz), mv, mz))

    # V distribution conditional on h*_1 = 0 and d >= 2
    cz = collections.Counter(r.get("hstar_sum") for r in pos
                             if r.get("hstar_1") == 0 and r["d"] >= 2)
    print("\n(vi) V distribution on the stratum {h*_1 = 0, d >= 2} (n=%d):" % sum(cz.values()))
    for v in sorted(cz):
        print("      V=%-4d %6d" % (v, cz[v]))

    # instrument integrity
    badv = [r for r in pos if not (r.get("heldout_ok") and r.get("hstar_roundtrip_ok")
                                   and r.get("hstar_tail_zero") and r.get("hstar_0_is_1"))]
    print("\ninstrument integrity failures (heldout/roundtrip/tail/h*_0): %d" % len(badv))
    neghs = [r for r in pos if not r.get("hstar_nonneg")]
    print("h* with a negative entry (would contradict Stanley): %d" % len(neghs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
