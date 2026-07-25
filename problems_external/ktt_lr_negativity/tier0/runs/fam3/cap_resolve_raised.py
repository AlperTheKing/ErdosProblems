"""Resolve the 13 remaining fat triples: engine B lr_count with max_states
raised to 4e8 (the default 2e7 DP-state cap was the only obstruction; the
actual counts are ~1e5).  Full exact profile P(0..12) -> tier0 screen_profile.
"""
import os, json, importlib.util, sys
from multiprocessing import Pool

TIER0 = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/tier0_screen.py"
ENGB = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/engineB_lrrule.py"
WORK = r"C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/f1987d98-c6e4-47b0-90c4-e402adf2c40c/scratchpad/s1"

sys.setrecursionlimit(2_000_000)
ts_spec = importlib.util.spec_from_file_location("tier0_screen", TIER0)
ts = importlib.util.module_from_spec(ts_spec)
ts_spec.loader.exec_module(ts)
eb_spec = importlib.util.spec_from_file_location("eb", ENGB)
eb = importlib.util.module_from_spec(eb_spec)
eb_spec.loader.exec_module(eb)


def sc(p, n):
    return [x * n for x in p]


def one(args):
    lam, mu, nu = args
    D = ts.ambient_bound(nu)
    profile = {}
    for n in range(D + 3):
        profile[n] = eb.lr_count(sc(list(lam), n), sc(list(mu), n),
                                 sc(list(nu), n), cap=None,
                                 max_states=400_000_000)
    rec = ts.screen_profile(profile, D)
    rec.pop("degree_bound", None)
    rec.update({"lam": list(lam), "mu": list(mu), "nu": list(nu),
                "r": len(nu), "engine": "B:lr_count max_states=4e8",
                "note": "engine-A NODE_CAP + engine-B default-state-cap skip; "
                        "resolved with raised DP-state limit"})
    return rec


def main():
    fails = [json.loads(l) for l in open(os.path.join(WORK, "capB.jsonl"))]
    trips = [(tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
             for r in fails if r["status"] == "ENGINEB_FAIL"]
    print("resolving", len(trips), flush=True)
    with Pool(13) as p:
        recs = list(p.imap_unordered(one, trips))
    with open(os.path.join(WORK, "capB2.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    from collections import Counter
    print("status", Counter(r["status"] for r in recs))
    ok = [r for r in recs if r["status"] == "OK"]
    print("d hist", dict(Counter(r["d"] for r in ok)))
    print("TIER0", sum(r["TIER0"] for r in ok),
          "JACKPOT", sum(r["JACKPOT"] for r in ok),
          "NEG", sum(r["NEG"] for r in ok))
    ms = [r["hstar_1"] - r["hstar_d"] for r in ok if r["hstar_1"] is not None]
    print("min margin", min(ms) if ms else None, "max hd",
          max(r["hstar_d"] for r in ok) if ok else None)
    print("audit_fail", sum(1 for r in ok if not (
        r["heldout_ok"] and r["hstar_1_identity_ok"] and r["interior_check_ok"]
        and r["moment_criteria_consistent"] and r["hstar_roundtrip_ok"])))
    print("neg_hstar", sum(1 for r in ok if any(x < 0 for x in r["hstar"])))


if __name__ == "__main__":
    main()
