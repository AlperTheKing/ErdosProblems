#!/usr/bin/env python3
"""
band2_extremal_check.py -- independent re-verification of the band-2 EXTREMAL
triples (max normalized volume, record h*_2, min coefficient, max V at h*_1=0)
against BOTH external exact LR engines at n = 1..5.

Also re-runs the Reeve positive control (T_q, q = 12,13) so the record shows the
same machinery does flag the textbook negative case.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hive4  # noqa: E402

ENG = os.path.join(os.path.dirname(HERE), "engine")
EXE_A = os.path.join(ENG, "lr_hive.exe")
EXE_B = os.path.join(ENG, "engineB_lrrule.py")
D = os.path.join(HERE, "runs", "band2")


def pstr(p):
    p = [x for x in p if x > 0]
    return ",".join(str(x) for x in p) if p else "0"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def check(lam, mu, nu, nmax=5):
    r = hive4.analyze(list(lam), list(mu), list(nu))
    rec = {"lam": list(lam), "mu": list(mu), "nu": list(nu),
           "dim": r["dim"], "c": r["c"],
           "V": str(r["volume_normalized"]), "hstar": list(r["hstar"]),
           "poly": [hive4._fmt_frac(c) for c in r["poly"]],
           "min_coeff": hive4._fmt_frac(r["min_coeff"]), "neg": r["neg"],
           "L": list(r["L"]), "verified": r["verified"],
           "vol_crosscheck": r["vol_crosscheck"], "deg_eq_dim": r["deg_eq_dim"],
           "stretched": {}}
    for n in range(1, nmax + 1):
        Pn = hive4.polyval(r["poly"], n)
        l, m, v = [x * n for x in lam], [x * n for x in mu], [x * n for x in nu]
        a = run([EXE_A, pstr(l), pstr(m), pstr(v)])
        b = run([sys.executable, EXE_B, pstr(l), pstr(m), pstr(v)])
        rec["stretched"][n] = {"P(n)": str(Pn), "engineA": a, "engineB": b,
                               "agree": (a == b == str(Pn))}
    rec["all_agree"] = all(x["agree"] for x in rec["stretched"].values())
    return rec


def main():
    man = json.load(open(os.path.join(D, "manifest.json")))
    targets = {}
    for key in ("max_volume", "max_volume_hstar1_zero"):
        t = man[key][1]
        if t:
            targets[key] = (t[0], t[1], t[2])
    t = man["record_hstar2"][1]
    if t:
        targets["record_hstar2"] = (t[0], t[1], t[2])
    t = man["min_coeff_any"]
    if t:
        targets["min_coeff_any"] = (t[1][0], t[1][1], t[1][2])
    t = man["min_a1"]
    if t:
        targets["min_a1"] = (t[1][0], t[1][1], t[1][2])

    out = {"band": man["band"], "checks": {}}
    for k, (lam, mu, nu) in targets.items():
        out["checks"][k] = check(lam, mu, nu)
        print(k, out["checks"][k]["lam"], out["checks"][k]["mu"],
              out["checks"][k]["nu"], "P=", out["checks"][k]["poly"],
              "h*=", out["checks"][k]["hstar"],
              "ALL_ENGINES_AGREE=", out["checks"][k]["all_agree"], flush=True)

    # Reeve positive control
    ctrl = {}
    for q in (12, 13, 20):
        A, b = hive4.reeve_hrep(q)
        rr = hive4.analyze_polytope(A, b, label="reeve_%d" % q)
        ctrl[q] = {"hstar": list(rr["hstar"]),
                   "poly": [hive4._fmt_frac(c) for c in rr["poly"]],
                   "a1": hive4._fmt_frac(rr["poly"][1]),
                   "neg": rr["neg"], "V": str(rr["volume_normalized"])}
        print("REEVE q=%d a1=%s NEG=%s h*=%s" % (q, ctrl[q]["a1"], ctrl[q]["neg"],
                                                 ctrl[q]["hstar"]))
    out["reeve_positive_control"] = ctrl
    out["all_engines_agree"] = all(v["all_agree"] for v in out["checks"].values())
    with open(os.path.join(D, "extremal_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("ALL EXTREMAL CROSS-CHECKS AGREE:", out["all_engines_agree"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
