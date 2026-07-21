#!/usr/bin/env python3
"""band9 hunter-9 SECOND independent cross-engine check (fresh random gap classes).

For each sampled gap class: fast scanner (--one) vs hive4.py exact Ehrhart vs
LR engine A (lr_hive.exe) vs LR engine B (engineB_lrrule.py) at stretch n=1,2.
All comparisons exact integers.  Any disagreement is printed as MISMATCH and
never smoothed over.
"""
import json
import random
import subprocess
import sys

R4 = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve"
ENG = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine"
SCAN = R4 + "/bandscan9c.exe"
HIVE = R4 + "/hive4.py"
EA = ENG + "/lr_hive.exe"
EB = ENG + "/engineB_lrrule.py"


def scan_one(g):
    out = subprocess.run([SCAN, "--one"] + [str(x) for x in g],
                         capture_output=True, text=True).stdout.strip()
    if "not band-realisable" in out:
        return None
    d = {}
    for tok in out.split():
        k, _, v = tok.partition("=")
        d[k] = v
    return d


def plist(s):
    return [int(x) for x in s.strip("()").split(",") if int(x) != 0 or False]


def fmt(p):
    p = [x for x in p if x > 0]
    return ",".join(str(x) for x in p) if p else "0"


def lr(engine, lam, mu, nu, n):
    L = fmt([n * x for x in lam])
    M = fmt([n * x for x in mu])
    N = fmt([n * x for x in nu])
    if engine == "A":
        cmd = [EA, L, M, N, "100000000"]
    else:
        cmd = [sys.executable, EB, L, M, N, "100000000"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    return r.stdout.strip().splitlines()[-1].strip()


def main():
    rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 9009)
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 40   # gap entry cap
    recs = []
    tries = 0
    while len(recs) < want and tries < 200000:
        tries += 1
        g = [rnd.randint(0, cap) for _ in range(9)]
        d = scan_one(g)
        if d is None or d.get("valid") != "1":
            continue
        if int(d["V"]) <= 0:
            continue           # want dim 3
        if int(d["L1"]) > 4000:
            continue           # keep LR engines tractable
        recs.append((g, d))
    print("# sampled %d dim-3 band gap classes (of %d tries)" % (len(recs), tries))
    bad = 0
    out = []
    for g, d in recs:
        lam = [int(x) for x in d["lam"].strip("()").split(",")]
        mu = [int(x) for x in d["mu"].strip("()").split(",")]
        nu = [int(x) for x in d["nu"].strip("()").split(",")]
        sp = lambda p: " ".join(str(x) for x in p if x > 0) or "0"
        h = subprocess.run([sys.executable, HIVE, sp(lam), sp(mu), sp(nu)],
                           capture_output=True, text=True, timeout=3600)
        J = json.loads(h.stdout.strip().splitlines()[-1])
        a1 = lr("A", lam, mu, nu, 1)
        b1 = lr("B", lam, mu, nu, 1)
        a2 = lr("A", lam, mu, nu, 2)
        b2 = lr("B", lam, mu, nu, 2)
        line = dict(g=g, W=d["W"], lam=lam, mu=mu, nu=nu,
                    scan=dict(L1=d["L1"], L2=d["L2"], L3=d["L3"], six_a1=d["6a1"], V=d["V"]),
                    hive4=dict(dim=J.get("dim"), c=J.get("c"), V=J.get("volume_normalized"),
                               hstar=J.get("hstar"), P=J.get("poly"),
                               verified=J.get("verified"), neg=J.get("neg"),
                               L=J.get("L"), min_coeff=J.get("min_coeff")),
                    engineA_n1=a1, engineB_n1=b1, engineA_n2=a2, engineB_n2=b2)
        agree_n1 = (a1 == b1 == d["L1"] == str(J.get("c")))
        agree_n2 = (a2 == b2 == d["L2"] == str(J["L"][2]))
        agree_scan_hive = (d["L3"] == str(J["L"][3]) and d["V"] == str(J["volume_normalized"]))
        line["agree_scan_hive_L3_V"] = agree_scan_hive
        agree_n2 = agree_n2 and agree_scan_hive and bool(J.get("verified"))
        line["agree_n1"] = agree_n1
        line["agree_n2"] = agree_n2
        if not (agree_n1 and agree_n2):
            bad += 1
            print("MISMATCH", json.dumps(line))
        out.append(line)
        print(json.dumps(line))
    print("# MISMATCHES = %d / %d" % (bad, len(out)))
    with open(R4 + "/runs/band9/xcheck2.json", "w") as f:
        json.dump(dict(mismatches=bad, n=len(out), records=out), f, indent=1)


main()
