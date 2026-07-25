#!/usr/bin/env python
"""fam8 aggregation + manifest.  Measurement only; nothing is filtered."""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))


def load(p):
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def strip(r):
    return {k: r.get(k) for k in ("lam", "mu", "nu", "r", "degree_bound", "d", "c",
                                  "hstar", "hstar_sum", "hstar_1", "hstar_d",
                                  "INTERIOR", "TIER0", "JACKPOT", "NEG",
                                  "coeffs_low_to_high", "u_mean", "u2_mean")}


def main():
    beam = load(os.path.join(HERE, "fam8_records.jsonl"))
    exh = load(os.path.join(HERE, "fam8_exh_records.jsonl"))
    allr = beam + exh
    ok = [r for r in allr if r.get("status") == "OK"]
    status = collections.Counter(r.get("status") for r in allr)
    uniq = {(tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"])) for r in allr}

    best_hd, min_margin = None, None
    hits = []
    audit_bad = []
    dhist = collections.Counter()
    for r in ok:
        h1, hd, d = r.get("hstar_1"), r.get("hstar_d"), r.get("d")
        dhist[d] += 1
        if not (r.get("hstar_1_identity_ok", True) and r.get("interior_check_ok", True)
                and r.get("hstar_roundtrip_ok", True) and r.get("heldout_ok", True)
                and r.get("moment_criteria_consistent", True)
                and r.get("hstar_tail_zero", True)):
            audit_bad.append(strip(r))
        if h1 is None or hd is None or d is None or d < 1:
            continue
        if best_hd is None or hd > best_hd["hstar_d"]:
            best_hd = r
        if min_margin is None or h1 - hd < min_margin["hstar_1"] - min_margin["hstar_d"]:
            min_margin = r
        if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG"):
            hits.append(strip(r))

    # h*_j nonnegativity + the lattice-polytope inequalities, as OBSERVATIONS
    viol = {"stanley_neg_hstar": 0, "hd_gt_h1": 0}
    for r in ok:
        h = r.get("hstar") or []
        if any(x < 0 for x in h):
            viol["stanley_neg_hstar"] += 1
        if r.get("hstar_1") is not None and r.get("hstar_d") is not None \
                and r["hstar_d"] > r["hstar_1"]:
            viol["hd_gt_h1"] += 1

    exh_state = {}
    p = os.path.join(HERE, "fam8_exh_state.json")
    if os.path.exists(p):
        exh_state = json.load(open(p))
    beam_state = {}
    p = os.path.join(HERE, "fam8_state.json")
    if os.path.exists(p):
        beam_state = json.load(open(p))

    man = {
        "family": "fam8 = beam search maximising h*_d - h*_1, plus an exhaustive "
                  "small-box companion sweep",
        "instrument": "tier0_screen.py (LP-free; engine A profile, exact Newton "
                      "interpolation, 2 held-out points, exact h*)",
        "exhaustive": False,
        "sampled": True,
        "beam": {"records": len(beam), "state": beam_state},
        "exhaustive_companion": exh_state,
        "records_total": len(allr),
        "distinct_triples": len(uniq),
        "status_histogram": dict(status),
        "d_histogram": {str(k): v for k, v in sorted(dhist.items(), key=lambda t: (t[0] is None, t[0]))},
        "best_hstar_d": strip(best_hd) if best_hd else None,
        "min_h1_minus_hd": (min_margin["hstar_1"] - min_margin["hstar_d"]) if min_margin else None,
        "min_h1_minus_hd_triple": strip(min_margin) if min_margin else None,
        "hits": hits,
        "audit_failures": audit_bad,
        "observations": viol,
        "note": "A null census is NOT evidence for the KTT conjecture.",
    }
    json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
    print(json.dumps({k: man[k] for k in
                      ("records_total", "distinct_triples", "status_histogram",
                       "d_histogram", "min_h1_minus_hd", "observations")}, indent=1))
    print("best_hstar_d:", json.dumps(man["best_hstar_d"]))
    print("min_margin_triple:", json.dumps(man["min_h1_minus_hd_triple"]))
    print("hits:", len(hits), "audit_failures:", len(audit_bad))


if __name__ == "__main__":
    main()
