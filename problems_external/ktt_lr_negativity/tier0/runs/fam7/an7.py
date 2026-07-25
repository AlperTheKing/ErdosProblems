#!/usr/bin/env python3
"""Family-7 analyzer: aggregate tier0_screen jsonl records.

Tracks (i) max h*_d, (ii) min (h*_1 - h*_d), (iii) TIER0/JACKPOT, (iv) NEG,
(v) record smallest c among triples with an interior lattice point, per d.
"""
import json, sys, glob, os

state = {
    "n_records": 0,
    "n_ok": 0,
    "n_status": {},
    "best_hstar_d": (-1, None),
    "min_h1_minus_hd": (None, None),
    "min_c_with_interior": {},   # d -> (c, triple, hstar)
    "hits": [],
    "n_interior_pos": 0,
    "n_by_d": {},
    "min_h1_by_d": {},           # d -> (h1, triple) over interior-positive
}


def key(rec):
    return (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))


def feed(rec, st):
    st["n_records"] += 1
    s = rec.get("status")
    st["n_status"][s] = st["n_status"].get(s, 0) + 1
    if s != "OK":
        return
    st["n_ok"] += 1
    d = rec["d"]
    st["n_by_d"][d] = st["n_by_d"].get(d, 0) + 1
    hd = rec.get("hstar_d")
    h1 = rec.get("hstar_1")
    if d is None or d < 2 or h1 is None or hd is None:
        return
    k = key(rec)
    if hd is not None and hd > st["best_hstar_d"][0]:
        st["best_hstar_d"] = (hd, {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                                   "d": d, "c": rec["c"], "hstar": rec["hstar"]})
    if hd is not None and h1 is not None:
        m = h1 - hd
        if st["min_h1_minus_hd"][0] is None or m < st["min_h1_minus_hd"][0]:
            st["min_h1_minus_hd"] = (m, {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                                         "d": d, "c": rec["c"], "hstar": rec["hstar"],
                                         "hstar_1": h1, "hstar_d": hd})
    if hd is not None and hd > 0:
        st["n_interior_pos"] += 1
        cur = st["min_c_with_interior"].get(str(d))
        if cur is None or rec["c"] < cur[0]:
            st["min_c_with_interior"][str(d)] = (rec["c"],
                {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"],
                 "hstar": rec["hstar"], "hstar_1": h1, "hstar_d": hd,
                 "hstar_sum": rec["hstar_sum"]})
        cur2 = st["min_h1_by_d"].get(str(d))
        if cur2 is None or h1 < cur2[0]:
            st["min_h1_by_d"][str(d)] = (h1,
                {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"], "c": rec["c"],
                 "hstar": rec["hstar"], "hstar_d": hd})
    if rec.get("TIER0") or rec.get("JACKPOT") or rec.get("NEG"):
        st["hits"].append(rec)
    # audit flags
    for f in ("heldout_ok", "hstar_roundtrip_ok", "interior_check_ok",
              "hstar_1_identity_ok", "moment_criteria_consistent",
              "hstar_nonneg", "hstar_tail_zero"):
        if rec.get(f) is False:
            st.setdefault("audit_failures", []).append({"field": f, "triple": k})


def main():
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    for fn in files:
        with open(fn) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                feed(json.loads(line), state)
    out = dict(state)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
