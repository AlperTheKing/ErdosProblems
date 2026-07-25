"""Resolve the 84 engine-A NODE_CAP skips with engine B over the full profile.

For each of the 84 triples the engine-A DFS blows past its 2e8 node-visit
safety cap at n = 12 (the triple is "fat": boundary values ~ 250, so the
DFS explores > 2e8 partial hives even though the final count is tiny).  This
is a documented SKIP, never a math verdict.  Engine B counts by the
Littlewood-Richardson rule and is unaffected, so it delivers the exact
profile P(0..12).  We then run the SAME exact tier-0 machinery from
tier0_screen (Newton interpolation, held-out n=11,12, exact h*).
"""
import os, json, importlib.util, subprocess, sys
from fractions import Fraction
from multiprocessing import Pool

TIER0 = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0/tier0_screen.py"
ENGB = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/engineB_lrrule.py"
WORK = r"C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/f1987d98-c6e4-47b0-90c4-e402adf2c40c/scratchpad/s1"

spec = importlib.util.spec_from_file_location("tier0_screen", TIER0)
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)


def sc(p, n):
    return ",".join(str(x * n) for x in p) if p else "0"


def one(args):
    lam, mu, nu = args
    D = ts.ambient_bound(nu)  # 10
    lines = []
    for n in range(D + 3):     # 0..12
        lines.append("%s;%s;%s;%d" % (sc(lam, n), sc(mu, n), sc(nu, n),
                                      4 * 10**18))
    path = os.path.join(WORK, "b_%s.batch" % abs(hash(args)))
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    r = subprocess.run([sys.executable, ENGB, "--batch", path],
                       capture_output=True, text=True)
    os.unlink(path)
    vals = [x.strip() for x in r.stdout.splitlines() if x.strip()]
    if len(vals) != D + 3 or any(not v.lstrip("-").isdigit() for v in vals):
        return {"lam": list(lam), "mu": list(mu), "nu": list(nu),
                "status": "ENGINEB_FAIL", "raw": vals, "stderr": r.stderr[:200]}
    profile = {n: int(vals[n]) for n in range(D + 3)}
    rec = ts.screen_profile(profile, D)
    rec.pop("degree_bound", None)
    rec.update({"lam": list(lam), "mu": list(mu), "nu": list(nu),
                "r": len(nu), "engine": "B:engineB_lrrule.py",
                "note": "engine-A NODE_CAP skip resolved by engine B"})
    return rec


def main():
    trips = [tuple(ts.parse_partition(x) for x in l.strip().split(";"))
             for l in open(os.path.join(WORK, "cap.txt")) if l.strip()]
    print("resolving", len(trips), "with engine B", flush=True)
    with Pool(40) as p:
        recs = list(p.imap_unordered(one, trips))
    with open(os.path.join(WORK, "capB.jsonl"), "w") as f:
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
