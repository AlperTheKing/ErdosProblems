#!/usr/bin/env python3
"""fam10_analyze.py -- summarize a tier0 screen output, optionally joined to a
vertex sweep, for the fractional-vertex family."""
import collections
import json
import sys


def key(r):
    return (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def main(argv):
    tier = load(argv[1])
    vs = {}
    if len(argv) > 2:
        for r in load(argv[2]):
            vs[key(r)] = r
    st = collections.Counter(r["status"] for r in tier)
    ok = [r for r in tier if r["status"] == "OK"]
    print("status:", dict(st))
    print("OK:", len(ok))
    bad = [r for r in ok if r.get("moment_criteria_consistent") is False
           or r.get("hstar_1_identity_ok") is False
           or r.get("interior_check_ok") is False]
    print("audit failures:", len(bad))
    hits = [r for r in ok if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG")]
    print("HITS (TIER0|JACKPOT|NEG):", len(hits))
    for r in hits[:20]:
        print("  HIT", r["lam"], r["mu"], r["nu"], r.get("d"), r.get("hstar"),
              r.get("TIER0"), r.get("JACKPOT"), r.get("NEG"))
    negh = [r for r in ok if any(h < 0 for h in r.get("hstar", []))]
    print("negative h*_j:", len(negh))
    print("d distribution:", dict(collections.Counter(r["d"] for r in ok)))
    best_hd = max(ok, key=lambda r: (r.get("hstar_d") or 0))
    print("max h*_d:", best_hd.get("hstar_d"), best_hd["lam"], best_hd["mu"],
          best_hd["nu"], "d", best_hd["d"], "h*", best_hd.get("hstar"))
    for lo in (0, 2, 4):
        sub = [r for r in ok if r["d"] >= lo and r.get("hstar_1") is not None]
        if not sub:
            print("min h*_1-h*_d over d>=%d: (empty)" % lo)
            continue
        m = min(sub, key=lambda r: r["hstar_1"] - r["hstar_d"])
        print("min h*_1-h*_d over d>=%d: %d  at %s %s %s d=%d h*=%s c=%d"
              % (lo, m["hstar_1"] - m["hstar_d"], m["lam"], m["mu"], m["nu"],
                 m["d"], m.get("hstar"), m.get("c")))
    if vs:
        nl = [r for r in ok if vs.get(key(r), {}).get("maxden", 1) > 1]
        print("non-lattice (maxden>=2) with OK screen:", len(nl))
        nl.sort(key=lambda r: -vs[key(r)]["fracratio"])
        for r in nl[:25]:
            v = vs[key(r)]
            print("   %s %s %s | c=%d d=%d dimlo=%d nv=%d nfrac=%d ratio=%.3f den=%d"
                  " | h*=%s  h1=%s hd=%s margin=%s"
                  % (r["lam"], r["mu"], r["nu"], r["c"], r["d"], v["dim_lo"],
                     v["nverts"], v["nfrac"], v["fracratio"], v["maxden"],
                     r.get("hstar"), r.get("hstar_1"), r.get("hstar_d"),
                     None if r.get("hstar_1") is None
                     else r["hstar_1"] - r["hstar_d"]))
        sub = [r for r in nl if r.get("hstar_1") is not None]
        if sub:
            m = min(sub, key=lambda r: r["hstar_1"] - r["hstar_d"])
            print("min margin among NON-LATTICE: %d at %s %s %s d=%d"
                  % (m["hstar_1"] - m["hstar_d"], m["lam"], m["mu"], m["nu"],
                     m["d"]))


if __name__ == "__main__":
    main(sys.argv)
