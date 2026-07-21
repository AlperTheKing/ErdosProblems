#!/usr/bin/env python3
"""analyze.py -- aggregate the THEORY-3 re-mining results."""
import json
import collections
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))


def load(fn):
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        return []
    out = []
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if l:
            out.append(json.loads(l))
    return out


def sec(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


# ---------------------------------------------------------------- (1) seeds
sec("(1) THE 30 PURGED route_N_seeds_nearest + 9 route_N_maxden3 SEEDS")
seeds = sorted(load("seeds39_profile.jsonl"), key=lambda r: r["idx"])
pop39 = json.load(open(os.path.join(HERE, "seeds39_pop.json")))
resolved = [r for r in seeds if r["status"] == "OK"]
print("resolved %d / 39   (unresolved = engine search budget, never a verdict)"
      % len(resolved))
print("%-3s %-24s %-20s %-24s %-2s %-3s %-4s %-5s %-24s %-12s %s"
      % ("#", "lam", "mu", "nu", "r", "d", "c", "V", "h*", "min coeff", "NEG"))
for r in seeds:
    meta = pop39[r["idx"]]
    f = lambda p: ",".join(map(str, p))
    if r["status"] != "OK":
        print("%-3d %-24s %-20s %-24s %-2d %s"
              % (r["idx"], f(r["lam"]), f(r["mu"]), f(r["nu"]), r["r"], r["status"]))
        continue
    co = [Fraction(x) for x in r["coeffs_low_to_high"]]
    print("%-3d %-24s %-20s %-24s %-2d %-3d %-4d %-5d %-24s %-12s %s"
          % (r["idx"], f(r["lam"]), f(r["mu"]), f(r["nu"]), r["r"], r["d"],
             r["c"], r["hstar_sum"], str(r["hstar"]), str(min(co)), r["neg"]))
missing = [i for i in range(39) if i not in {r["idx"] for r in seeds}] + \
          [r["idx"] for r in seeds if r["status"] != "OK"]
print("unresolved indices:", sorted(set(missing)))
if resolved:
    print("max sum h* over resolved seeds:",
          max(r["hstar_sum"] for r in resolved))
    print("NEG hits among resolved seeds:",
          sum(1 for r in resolved if r["neg"]))
    print("all held-out points matched:",
          all(r["heldout_ok"] for r in resolved))
    print("all h* round-trips ok:",
          all(r["hstar_roundtrip_ok"] for r in resolved))

# ------------------------------------------------- (2) wave-4 population
sec("(2) THE WAVE-4 POPULATION RE-SCREENED (old filter labels vs true h*)")
wpop = json.load(open(os.path.join(HERE, "wave4_pop.json")))
prof = {}
for fn in ("pop_profile_part1.jsonl", "pop_profile_cand.jsonl",
           "pop_profile_ns.jsonl"):
    for r in load(fn):
        prof[r["idx"]] = r
st = collections.Counter(r["status"] for r in prof.values())
print("population %d triples (r-dist %s)"
      % (len(wpop), dict(collections.Counter(len(w["nu"].split(",")) for w in wpop))))
print("screened   %d ; status %s" % (len(prof), dict(st)))

rows = []
for i, w in enumerate(wpop):
    p = prof.get(i)
    if p is None or p["status"] != "OK":
        continue
    if p["d"] is None or p["d"] < 1:
        continue
    rows.append((w, p))
print("usable (status OK, d>=1): %d" % len(rows))

h1z = [(w, p) for (w, p) in rows if p["hstar"][1] == 0]
print("h*_1 = 0 population: %d" % len(h1z))
lab = collections.Counter(w["status"] for w, _ in h1z)
print("  old-filter label among them:", dict(lab))
tot = sum(lab.values())
if tot:
    print("  ==> FRACTION DESTROYED BY THE OLD 'must be a simplex' FILTER: "
          "%d/%d = %.1f%%" % (lab["NOT_SIMPLEX"], tot,
                              100.0 * lab["NOT_SIMPLEX"] / tot))
for rr in (5, 6, 7):
    sub = [(w, p) for (w, p) in h1z if len(w["nu"].split(",")) == rr]
    if not sub:
        continue
    l2 = collections.Counter(w["status"] for w, _ in sub)
    print("  r=%d : h*_1=0 count %d, NOT_SIMPLEX %d (%.1f%%)"
          % (rr, len(sub), l2["NOT_SIMPLEX"],
             100.0 * l2["NOT_SIMPLEX"] / len(sub)))
vd = collections.Counter(p["hstar_sum"] for _, p in h1z)
print("  volume (sum h*) distribution inside h*_1=0:", dict(sorted(vd.items())))
big = [(w, p) for (w, p) in h1z if p["hstar_sum"] > 1]
print("  h*_1=0 AND sum h* >= 2:", len(big))
for w, p in sorted(big, key=lambda t: -t[1]["hstar_sum"])[:20]:
    print("    V=%d d=%d %s | %s | %s  h*=%s  oldlabel=%s"
          % (p["hstar_sum"], p["d"], w["lam"], w["mu"], w["nu"],
             p["hstar"], w["status"]))

# ------------------------------------------------------- (3) max volume
sec("(3) MAXIMUM sum h* ANYWHERE IN THE PURGED POPULATION")
okrows = [(w, p) for (w, p) in rows]
purged = [(w, p) for (w, p) in okrows if w["status"] == "NOT_SIMPLEX"]
kept = [(w, p) for (w, p) in okrows if w["status"] == "CERTIFIED_SIMPLEX"]
for name, grp in (("PURGED (old label NOT_SIMPLEX)", purged),
                  ("KEPT   (old label CERTIFIED_SIMPLEX)", kept)):
    if not grp:
        continue
    b = max(grp, key=lambda t: t[1]["hstar_sum"])
    print("%-38s n=%-5d max sum h* = %d" % (name, len(grp), b[1]["hstar_sum"]))
    print("    %s | %s | %s   d=%d  h*=%s"
          % (b[0]["lam"], b[0]["mu"], b[0]["nu"], b[1]["d"], b[1]["hstar"]))
print("\ntop 10 volumes in the purged (NOT_SIMPLEX) population:")
for w, p in sorted(purged, key=lambda t: -t[1]["hstar_sum"])[:10]:
    print("  V=%-7d d=%-3d h*_1=%-6d %s | %s | %s" %
          (p["hstar_sum"], p["d"], p["hstar"][1], w["lam"], w["mu"], w["nu"]))
negs = [(w, p) for (w, p) in okrows if p["neg"]]
print("\nNEGATIVE-COEFFICIENT HITS in the whole re-screened population:", len(negs))
for w, p in negs:
    print("   ", w, p["poly"])

# ------------------------------------------------- exhaustive ladder scans
sec("(4) EXHAUSTIVE LADDER SCANS (LP-free instrument, nothing filtered but c<=D+1)")
for tag, fn in (("r=5, 5<=|nu|<=17", "ladder_r5.jsonl"),
                ("r=5, 18<=|nu|<=19", "ladder_r5_hi.jsonl"),
                ("r=6, 6<=|nu|<=16", "ladder_r6.jsonl"),
                ("r=6, |nu|=17", "ladder_r6_hi.jsonl")):
    rs = load(fn)
    if not rs:
        continue
    ok = [r for r in rs if r["status"] == "OK"]
    d1 = [r for r in ok if r["d"] is not None and r["d"] >= 1]
    z = [r for r in d1 if r["hstar"][1] == 0]
    vv = collections.Counter(r["hstar_sum"] for r in z)
    mx = max((r["hstar_sum"] for r in d1), default=0)
    print("%-20s screened %-7d  h*_1=0 %-7d  vol-dist %s  max sum h* (whole slice) %d  NEG %d"
          % (tag, len(ok), len(z), dict(sorted(vv.items())), mx,
             sum(1 for r in ok if r["neg"])))

# --------------------------------------------- vertex measurement (rigorous)
sec("(5) RIGOROUS VERTEX MEASUREMENT ON THE h*_1 = 0 POPULATION (r=5 exhaustive)")
vm = load("vm_r5_all.out")
src = {json.loads(l)["idx"]: json.loads(l)
       for l in open(os.path.join(HERE, "vm_r5_all.jsonl"), encoding="utf-8")}
c = collections.Counter(r["vstatus"] for r in vm)
print("measured %d of the r=5 h*_1=0 population; %s" % (len(vm), dict(c)))
if vm:
    n_ns = c["PROVABLY_NOT_SIMPLEX"]
    print("  provably NOT a simplex: %d / %d = %.3f%%  (lower bound: random "
          "objectives can only under-count vertices)"
          % (n_ns, len(vm), 100.0 * n_ns / len(vm)))
byV = collections.defaultdict(collections.Counter)
for r in vm:
    byV[src[r["idx"]]["V"]][r["vstatus"]] += 1
for V in sorted(byV):
    t = sum(byV[V].values())
    print("  sum h* = %d : n=%-6d provably-non-simplex %d (%.1f%%)"
          % (V, t, byV[V]["PROVABLY_NOT_SIMPLEX"],
             100.0 * byV[V]["PROVABLY_NOT_SIMPLEX"] / t))

vm2 = load("vm_V2.out")
if vm2:
    s2 = {json.loads(l)["idx"]: json.loads(l)
          for l in open(os.path.join(HERE, "vm_V2.jsonl"), encoding="utf-8")}
    c2 = collections.Counter(r["vstatus"] for r in vm2)
    print("\nALL ladder-carrying triples (h*_1=0 AND sum h* >= 2) found by the "
          "exhaustive scans: %d ; vertex verdicts %s" % (len(vm2), dict(c2)))
