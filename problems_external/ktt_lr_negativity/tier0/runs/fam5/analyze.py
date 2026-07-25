#!/usr/bin/env python
"""fam5 analyzer: exact aggregation over screened records."""
import json, sys, collections as C, glob


def load(paths):
    rs = []
    for p in paths:
        for ln in open(p):
            ln = ln.strip()
            if ln:
                rs.append(json.loads(ln))
    return rs


def main():
    paths = []
    for a in sys.argv[1:]:
        paths.extend(glob.glob(a))
    rs = load(paths)
    print("records", len(rs))
    print("status", dict(C.Counter(r["status"] for r in rs)))
    ok = [r for r in rs if r["status"] == "OK"]
    print("OK", len(ok))
    g = [r for r in ok if r.get("hstar_1") is not None]
    print("with h*_1 (d>=1)", len(g))
    if not g:
        return
    # audits
    bad = [r for r in ok if not (r.get("hstar_1_identity_ok", True)
                                 and r.get("interior_check_ok", True)
                                 and r.get("moment_criteria_consistent", True)
                                 and r.get("heldout_ok", True)
                                 and r.get("hstar_roundtrip_ok", True))]
    print("AUDIT FAILURES", len(bad))
    for r in bad[:5]:
        print("  ", r["lam"], r["mu"], r["nu"])
    print("d dist", dict(sorted(C.Counter(r["d"] for r in ok).items())))
    print("dim-deficient d<D", sum(1 for r in ok if r["d"] < r["degree_bound"]),
          "/", len(ok))
    marg = [(r["hstar_1"] - r["hstar_d"], r) for r in g]
    mn = min(m for m, _ in marg)
    print("MIN h*_1 - h*_d =", mn)
    att = [r for m, r in marg if m == mn]
    print("  attained by", len(att), "e.g.", att[0]["lam"], att[0]["mu"], att[0]["nu"],
          "d=", att[0]["d"], "c=", att[0]["c"], "h*=", att[0]["hstar"])
    print("margin dist", dict(sorted(C.Counter(m for m, _ in marg).items())[:12]))
    bd = max(r["hstar_d"] for r in ok)
    ab = [r for r in ok if r["hstar_d"] == bd]
    print("MAX h*_d =", bd, "attained by", len(ab), "e.g.", ab[0]["lam"], ab[0]["mu"],
          ab[0]["nu"], "d=", ab[0]["d"], "c=", ab[0]["c"], "h*=", ab[0]["hstar"])
    print("JACKPOT", sum(1 for r in ok if r["JACKPOT"]),
          " TIER0", sum(1 for r in ok if r["TIER0"]),
          " NEG", sum(1 for r in ok if r["NEG"]))
    for r in ok:
        if r["JACKPOT"] or r["TIER0"] or r["NEG"]:
            print("  HIT", json.dumps(r))
    # margin 0 with d>=2: the frontier
    fr = [r for m, r in marg if m == 0 and r["d"] >= 2]
    print("margin-0 with d>=2:", len(fr))
    print("  d dist there", dict(sorted(C.Counter(r["d"] for r in fr).items())))
    with open("frontier.jsonl", "w") as f:
        for r in fr:
            f.write(json.dumps(r) + "\n")
    # h*_d > 0 population
    pos = [r for r in ok if r["hstar_d"] and r["hstar_d"] > 0
           and r["hstar_1"] is not None]
    print("h*_d > 0 count (d>=1)", len(pos))
    if pos:
        m2 = min((r["hstar_1"] - r["hstar_d"]) for r in pos)
        e2 = [r for r in pos if r["hstar_1"] - r["hstar_d"] == m2][0]
        print("min margin among h*_d>0:", m2, e2["lam"], e2["mu"], e2["nu"],
              "d=", e2["d"], "h*=", e2["hstar"])
        p2 = [r for r in pos if r["d"] >= 2]
        print("h*_d>0 AND d>=2 count", len(p2))
        if p2:
            m3 = min((r["hstar_1"] - r["hstar_d"]) for r in p2)
            e4 = [r for r in p2 if r["hstar_1"] - r["hstar_d"] == m3][0]
            print("  min margin there:", m3, e4["lam"], e4["mu"], e4["nu"],
                  "d=", e4["d"], "c=", e4["c"], "h*=", e4["hstar"])
        bd2 = max(r["hstar_d"] for r in pos)
        e3 = [r for r in pos if r["hstar_d"] == bd2][0]
        print("MAX h*_d among d>=1:", bd2, e3["lam"], e3["mu"], e3["nu"],
              "d=", e3["d"], "c=", e3["c"], "h*=", e3["hstar"])


if __name__ == "__main__":
    main()
