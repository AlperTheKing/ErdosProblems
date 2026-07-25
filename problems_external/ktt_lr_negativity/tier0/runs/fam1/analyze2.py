#!/usr/bin/env python
"""Tier-0 analysis. d=0 records are degenerate (h*_d aliases h*_0=1, h*_1 undefined)
and are excluded from the h*_d / margin statistics; d=1 has h*_1 == h*_d identically
(margin 0 forced) and is reported separately."""
import sys, json, collections

recs = []
for fn in sys.argv[1:]:
    for line in open(fn):
        line = line.strip()
        if line:
            recs.append(json.loads(line))

print("records", len(recs), dict(collections.Counter(r.get("status") for r in recs)))
ok = [r for r in recs if r.get("status") == "OK"]
audit = [r for r in ok if not (r.get("heldout_ok") and r.get("hstar_roundtrip_ok")
                               and r.get("interior_check_ok") and r.get("hstar_1_identity_ok")
                               and r.get("moment_criteria_consistent") and r.get("hstar_nonneg"))]
print("OK", len(ok), "audit failures", len(audit))
print("NEG", sum(1 for r in ok if r.get("NEG")),
      "TIER0", sum(1 for r in ok if r.get("TIER0")),
      "JACKPOT", sum(1 for r in ok if r.get("JACKPOT")))

core = [r for r in ok if r["d"] >= 2]
core4 = [r for r in ok if r["d"] >= 4]
print("d>=2:", len(core), " d>=4:", len(core4))

def K(r): return (r["lam"], r["mu"], r["nu"])

for name, pool in (("d>=2", core), ("d>=4", core4)):
    if not pool:
        continue
    bd = max(pool, key=lambda r: r["hstar_d"])
    print("[%s] max h*_d = %d at %s d=%d h*=%s" % (name, bd["hstar_d"], K(bd), bd["d"], bd["hstar"]))
    m = min(pool, key=lambda r: r["hstar_1"] - r["hstar_d"])
    print("[%s] min h*_1-h*_d = %d at %s d=%d h*=%s c=%d" %
          (name, m["hstar_1"] - m["hstar_d"], K(m), m["d"], m["hstar"], m["c"]))
    print("[%s] margin hist (lowest 8): %s" % (name,
          sorted(collections.Counter(r["hstar_1"] - r["hstar_d"] for r in pool).items())[:8]))
    inter = [r for r in pool if r["hstar_d"] > 0]
    print("[%s] records with an INTERIOR lattice point: %d" % (name, len(inter)))
    if inter:
        mi = min(inter, key=lambda r: r["hstar_1"] - r["hstar_d"])
        print("   best among them: margin %d  %s d=%d h*=%s" %
              (mi["hstar_1"] - mi["hstar_d"], K(mi), mi["d"], mi["hstar"]))
        print("   h*_d hist:", sorted(collections.Counter(r["hstar_d"] for r in inter).items())[:10])
    z = [r for r in pool if r["hstar_1"] == 0]
    print("[%s] h*_1==0: %d ; h*_d among them: %s" %
          (name, len(z), dict(collections.Counter(r["hstar_d"] for r in z))))
    print("[%s] min Sum h*: %d" % (name, min(r["hstar_sum"] for r in pool)))

# non-lattice detection proxy: Sum h* (normalized volume) vs c and interior;
# a lattice polytope has Sum h* >= ... ; we instead record denominators via P(1)=c
# and the known identity h*_1 = c-(d+1).  Report the count of records whose
# h*-vector violates any LATTICE inequality (Hibi / Stanley monotone / h*_d<=h*_1).
def viol(r):
    h = r["hstar"]; d = r["d"]
    v = []
    if d >= 1 and h[d] > h[1]:
        v.append("h*_d>h*_1")
    # Hibi lower bound: h*_1 <= h*_j for 1<=j<=d-1 when h*_d>0
    if d >= 2 and h[d] > 0:
        for j in range(1, d):
            if h[j] < h[1]:
                v.append("hibi_j%d" % j)
    # Stanley monotonicity, correct form with s = deg h*
    s = max([j for j in range(d + 1) if h[j] != 0] or [0])
    for i in range(0, s + 1):
        if sum(h[:i + 1]) > sum(h[s - i:s + 1]):
            v.append("stanley_i%d" % i)
    return v

vs = collections.Counter()
for r in core:
    for x in viol(r):
        vs[x] += 1
print("lattice-inequality violations over d>=2:", dict(vs) if vs else "NONE")

# frequency of h*-shapes at d>=4
print("top h* shapes at d>=4:",
      collections.Counter(tuple(r["hstar"]) for r in core4).most_common(10))
