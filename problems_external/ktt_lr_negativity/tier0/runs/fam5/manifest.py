#!/usr/bin/env python
"""fam5 manifest builder: exact aggregation of every screened record."""
import json, glob, collections as C, hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = ["w1_small.jsonl", "w2_mid.jsonl", "w3_big.jsonl", "climb.jsonl",
       "probe.jsonl"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    recs, files = [], {}
    seen = set()
    for s in SRC:
        p = os.path.join(HERE, s)
        if not os.path.exists(p):
            continue
        n = 0
        for ln in open(p):
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            k = (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
            n += 1
            if k in seen:
                continue
            seen.add(k)
            recs.append(r)
        files[s] = {"lines": n, "sha256": sha(p), "bytes": os.path.getsize(p)}

    ok = [r for r in recs if r.get("status") == "OK"]
    g = [r for r in ok if r.get("hstar_1") is not None]
    audits = sum(1 for r in ok if not (r.get("hstar_1_identity_ok", True)
                                       and r.get("interior_check_ok", True)
                                       and r.get("moment_criteria_consistent", True)
                                       and r.get("heldout_ok", True)
                                       and r.get("hstar_roundtrip_ok", True)))
    marg = [(r["hstar_1"] - r["hstar_d"], r) for r in g]
    mn = min(m for m, _ in marg) if marg else None
    att = [r for m, r in marg if m == mn][:3]
    bd = max((r["hstar_d"] for r in ok if r["hstar_d"] is not None), default=None)
    abest = [r for r in ok if r["hstar_d"] == bd][:3]
    bd1 = max((r["hstar_d"] for r in g), default=None)
    abest1 = [r for r in g if r["hstar_d"] == bd1][:3]
    hits = [r for r in ok if r.get("JACKPOT") or r.get("TIER0") or r.get("NEG")]
    p2 = [r for r in g if r["hstar_d"] > 0 and r["d"] >= 2]
    m3 = min((r["hstar_1"] - r["hstar_d"]) for r in p2) if p2 else None

    def slim(r):
        return {k: r[k] for k in ("lam", "mu", "nu", "r", "d", "c", "hstar",
                                  "hstar_sum", "hstar_1", "hstar_d",
                                  "degree_bound", "coeffs_low_to_high")
                if k in r}

    man = {
        "family": "fam5 SHORT-vs-LONG: lam 2-3 parts vs mu 4-7 parts, nu 5-7 parts, r in {5,6,7}",
        "exhaustive": False,
        "sampling": ("randomised: nu built from lam+mu by random downward unit "
                     "moves, constrained to nu_i >= max(lam_i,mu_i); three "
                     "weight strata (wmax 5/12/26, |nu| <= 34/60/80) plus a "
                     "beam search minimising h*_1 - h*_d seeded on the "
                     "wave-1 margin-0 d>=2 frontier"),
        "instrument": "../../tier0_screen.py (mandated LP-free exact screen; no LP oracle, no simplex filter)",
        "engine": "A:lr_hive.exe (batch), cap 1e15",
        "files": files,
        "distinct_triples_screened": len(recs),
        "status_counts": dict(C.Counter(r.get("status") for r in recs)),
        "OK": len(ok),
        "with_hstar1_d_ge_1": len(g),
        "audit_failures": audits,
        "d_distribution": dict(sorted(C.Counter(r["d"] for r in ok).items())),
        "dimension_deficient_d_lt_D": sum(1 for r in ok if r["d"] < r["degree_bound"]),
        "min_h1_minus_hd": mn,
        "min_h1_minus_hd_attained_by": [slim(r) for r in att],
        "min_h1_minus_hd_count": sum(1 for m, _ in marg if m == mn),
        "max_hstar_d_all": bd,
        "max_hstar_d_all_examples": [slim(r) for r in abest],
        "max_hstar_d_d_ge_1": bd1,
        "max_hstar_d_d_ge_1_examples": [slim(r) for r in abest1],
        "interior_positive_and_d_ge_2": len(p2),
        "min_margin_interior_positive_d_ge_2": m3,
        "margin_distribution": dict(sorted(C.Counter(m for m, _ in marg).items())),
        "JACKPOT": sum(1 for r in ok if r.get("JACKPOT")),
        "TIER0": sum(1 for r in ok if r.get("TIER0")),
        "NEG": sum(1 for r in ok if r.get("NEG")),
        "hits": [r for r in hits],
        "margin0_d_ge_2": sum(1 for m, r in marg if m == 0 and r["d"] >= 2),
        "margin0_d_ge_2_d_dist": dict(sorted(C.Counter(
            r["d"] for m, r in marg if m == 0 and r["d"] >= 2).items())),
        "note": ("A null census is NOT evidence for the KTT conjecture. "
                 "CAP_EXCEEDED / EMPTY / ENGINE_ERROR records are SKIPs, "
                 "never mathematical verdicts."),
    }
    json.dump(man, open(os.path.join(HERE, "manifest.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in man.items()
                      if k not in ("files", "margin_distribution")}, indent=1)[:4000])


if __name__ == "__main__":
    main()
