"""Stage 2 of the fam3 census: the FULL mandated LP-free screen on every
non-empty triple of the exhaustive r=6, |nu| <= 22 family.

Uses tier0_screen.screen_triples() unmodified (exact profile P(0..D+2) from
engine A, exact Newton interpolation, two held-out points, exact h*).
No LP oracle, no simplex filter, no float decides anything.
"""
import os, sys, json, time, importlib.util
from multiprocessing import Pool

TIER0 = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/tier0_screen.py"
WORK = r"C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/f1987d98-c6e4-47b0-90c4-e402adf2c40c/scratchpad/s1"
CHUNK = 1500

_spec = importlib.util.spec_from_file_location("tier0_screen", TIER0)
ts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ts)


def load_triples():
    trips = []
    with open(os.path.join(WORK, "survivors.txt")) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            trips.append(tuple(ts.parse_partition(x) for x in ln.split(";")))
    with open(os.path.join(WORK, "cbig.txt")) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            _c, rest = ln.split("|", 1)
            trips.append(tuple(ts.parse_partition(x) for x in rest.split(";")))
    return trips


ALL = None


def work(job):
    i, lo, hi = job
    recs = ts.screen_triples(ALL[lo:hi])
    agg = {
        "n": 0, "status": {}, "d_hist": {}, "hsum_hist": {},
        "min_margin": None, "min_margin_trip": None,
        "max_hd": -1, "max_hd_trip": None,
        "margin_hist": {},
        "min_margin2": None, "min_margin2_trip": None, "max_hd2": -1,
        "max_hd2_trip": None,
        "hits": [], "audit_fail": [], "neg_hstar": [],
        "margin_zero": 0,
    }
    for r in recs:
        agg["n"] += 1
        st = r.get("status")
        agg["status"][st] = agg["status"].get(st, 0) + 1
        if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG"):
            agg["hits"].append(r)
        if st != "OK":
            continue
        d = r["d"]
        agg["d_hist"][d] = agg["d_hist"].get(d, 0) + 1
        hs = r.get("hstar_sum")
        agg["hsum_hist"][hs] = agg["hsum_hist"].get(hs, 0) + 1
        for k in ("hstar_1_identity_ok", "interior_check_ok",
                  "moment_criteria_consistent", "heldout_ok",
                  "hstar_roundtrip_ok", "hstar_tail_zero"):
            if k in r and r[k] is not True:
                agg["audit_fail"].append({"key": k, "rec": r})
                break
        if any(x < 0 for x in r.get("hstar", [])):
            agg["neg_hstar"].append(r)
        h1, hd = r.get("hstar_1"), r.get("hstar_d")
        if h1 is None or hd is None:
            continue
        m = h1 - hd
        agg["margin_hist"][m] = agg["margin_hist"].get(m, 0) + 1
        if m == 0:
            agg["margin_zero"] += 1
        if agg["min_margin"] is None or m < agg["min_margin"]:
            agg["min_margin"] = m
            agg["min_margin_trip"] = [r["lam"], r["mu"], r["nu"], r["d"],
                                      r["c"], r["hstar"]]
        if hd > agg["max_hd"]:
            agg["max_hd"] = hd
            agg["max_hd_trip"] = [r["lam"], r["mu"], r["nu"], r["d"],
                                  r["c"], r["hstar"]]
        if d >= 2:
            if agg["min_margin2"] is None or m < agg["min_margin2"]:
                agg["min_margin2"] = m
                agg["min_margin2_trip"] = [r["lam"], r["mu"], r["nu"], r["d"],
                                           r["c"], r["hstar"]]
            if hd > agg["max_hd2"]:
                agg["max_hd2"] = hd
                agg["max_hd2_trip"] = [r["lam"], r["mu"], r["nu"], r["d"],
                                       r["c"], r["hstar"]]
    return agg


def init(trips):
    global ALL
    ALL = trips


def merge(a, b):
    a["n"] += b["n"]
    for k in ("status", "d_hist", "hsum_hist", "margin_hist"):
        for kk, vv in b[k].items():
            a[k][kk] = a[k].get(kk, 0) + vv
    a["margin_zero"] += b["margin_zero"]
    a["hits"].extend(b["hits"])
    a["audit_fail"].extend(b["audit_fail"])
    a["neg_hstar"].extend(b["neg_hstar"])
    if b["min_margin"] is not None and (a["min_margin"] is None or
                                        b["min_margin"] < a["min_margin"]):
        a["min_margin"] = b["min_margin"]
        a["min_margin_trip"] = b["min_margin_trip"]
    if b["max_hd"] > a["max_hd"]:
        a["max_hd"] = b["max_hd"]
        a["max_hd_trip"] = b["max_hd_trip"]
    if b["min_margin2"] is not None and (a["min_margin2"] is None or
                                         b["min_margin2"] < a["min_margin2"]):
        a["min_margin2"] = b["min_margin2"]
        a["min_margin2_trip"] = b["min_margin2_trip"]
    if b["max_hd2"] > a["max_hd2"]:
        a["max_hd2"] = b["max_hd2"]
        a["max_hd2_trip"] = b["max_hd2_trip"]
    return a


def main():
    t0 = time.time()
    trips = load_triples()
    print("triples", len(trips), flush=True)
    jobs = [(i, lo, min(lo + CHUNK, len(trips)))
            for i, lo in enumerate(range(0, len(trips), CHUNK))]
    total = {"n": 0, "status": {}, "d_hist": {}, "hsum_hist": {},
             "min_margin": None, "min_margin_trip": None,
             "max_hd": -1, "max_hd_trip": None, "margin_hist": {},
             "min_margin2": None, "min_margin2_trip": None, "max_hd2": -1,
             "max_hd2_trip": None,
             "hits": [], "audit_fail": [], "neg_hstar": [], "margin_zero": 0}
    done = 0
    with Pool(60, initializer=init, initargs=(trips,)) as pool:
        for agg in pool.imap_unordered(work, jobs, chunksize=1):
            total = merge(total, agg)
            done += 1
            if done % 40 == 0:
                print("%d/%d  %.0fs  minmargin=%s maxhd=%s hits=%d"
                      % (done, len(jobs), time.time() - t0,
                         total["min_margin"], total["max_hd"],
                         len(total["hits"])), flush=True)
    total["elapsed_s"] = time.time() - t0
    json.dump(total, open(os.path.join(WORK, "stage2.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in total.items()
                      if k not in ("hits", "audit_fail", "neg_hstar")},
                     indent=1), flush=True)
    print("hits", len(total["hits"]), "audit_fail", len(total["audit_fail"]),
          "neg_hstar", len(total["neg_hstar"]), flush=True)


if __name__ == "__main__":
    main()
