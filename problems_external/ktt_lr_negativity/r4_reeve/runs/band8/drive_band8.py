#!/usr/bin/env python3
"""
drive_band8.py -- driver for band 8 (W = |nu| in [61,90]) of the r=4
Reeve-dimension census.

Two stages, both exact (bandscan.exe is pure 64-bit integer arithmetic):

  STAGE 1  --nutop W : for EVERY nu shape of weight W (all partitions of W
           into at most 4 parts), hill-climb over the splits (lam,mu) to
           estimate max V.  This is the mandated "maximise the volume
           statistic V, use the engine to steer" step.  Every triple visited
           by the climb is also fed to the global accumulator, so the
           min-a1 / max-V / hits statistics cover it.

  STAGE 2  --nu n1 n2 n3 n4 : EXHAUSTIVE enumeration of ALL ordered splits
           (lam,mu) with at most 4 parts each and |lam|+|mu| = |nu|, for the
           best nu shapes selected in stage 1.

Everything is aggregated into manifest.json.  The stage-2 sub-censuses are
exhaustive; the band as a whole is NOT (see manifest["exhaustive"]).
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "bandscan.exe")

WLO, WHI = 61, 90


def run(args, logname):
    t0 = time.time()
    p = subprocess.run([EXE] + [str(a) for a in args], capture_output=True, text=True)
    out = p.stdout
    with open(os.path.join(HERE, logname), "w") as f:
        f.write(out)
        if p.stderr:
            f.write("\nSTDERR:\n" + p.stderr)
    return out, time.time() - t0


ACC_RE = re.compile(r"^\[(.*?)\] tested=(\d+) pruned_contain=(\d+) nonempty=(\d+) dim3=(\d+) NEG=(\d+)")
MIN_RE = re.compile(r"^\[(.*?)\] min6a1=(-?\d+) \(V=(\d+)\)")
MAXV_RE = re.compile(r"^\[(.*?)\] maxV=(-?\d+)")
MAXVH_RE = re.compile(r"^\[(.*?)\] maxV_hstar1_zero=(-?\d+)")
MAXH2_RE = re.compile(r"^\[(.*?)\] max_hstar2=(-?\d+)")
ARG_RE = re.compile(r"lam=\((.*?)\) mu=\((.*?)\) nu=\((.*?)\)")
HIT_RE = re.compile(r"^\[(.*?)\] HIT ")


def parse(out):
    d = {"tested": 0, "pruned": 0, "nonempty": 0, "dim3": 0, "neg": 0,
         "min6a1": None, "min6a1_V": None, "argmin": None,
         "maxV": -1, "argmaxV": None, "maxVh1z": -1, "argmaxVh1z": None,
         "maxh2": -1, "argmaxh2": None, "hits": []}
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        m = ACC_RE.match(ln)
        if m:
            d["tested"] += int(m.group(2)); d["pruned"] += int(m.group(3))
            d["nonempty"] += int(m.group(4)); d["dim3"] += int(m.group(5)); d["neg"] += int(m.group(6))
            continue
        m = MIN_RE.match(ln)
        if m:
            v = int(m.group(2))
            if d["min6a1"] is None or v < d["min6a1"]:
                d["min6a1"] = v; d["min6a1_V"] = int(m.group(3))
                d["argmin"] = ARG_RE.search(lines[i + 1]).groups()
            continue
        m = MAXV_RE.match(ln)
        if m:
            v = int(m.group(2))
            if v > d["maxV"]:
                d["maxV"] = v; d["argmaxV"] = ARG_RE.search(lines[i + 1]).groups()
            continue
        m = MAXVH_RE.match(ln)
        if m:
            v = int(m.group(2))
            if v > d["maxVh1z"]:
                d["maxVh1z"] = v; d["argmaxVh1z"] = ARG_RE.search(lines[i + 1]).groups()
            continue
        m = MAXH2_RE.match(ln)
        if m:
            v = int(m.group(2))
            if v > d["maxh2"]:
                d["maxh2"] = v; d["argmaxh2"] = ARG_RE.search(lines[i + 1]).groups()
            continue
        if HIT_RE.match(ln):
            d["hits"].append(ln)
    return d


def combine(G, d):
    for k in ("tested", "pruned", "nonempty", "dim3", "neg"):
        G[k] += d[k]
    if d["min6a1"] is not None and (G["min6a1"] is None or d["min6a1"] < G["min6a1"]):
        G["min6a1"] = d["min6a1"]; G["min6a1_V"] = d["min6a1_V"]; G["argmin"] = d["argmin"]
    for a, b in (("maxV", "argmaxV"), ("maxVh1z", "argmaxVh1z"), ("maxh2", "argmaxh2")):
        if d[a] > G[a]:
            G[a] = d[a]; G[b] = d[b]
    G["hits"].extend(d["hits"])


def main():
    G = {"tested": 0, "pruned": 0, "nonempty": 0, "dim3": 0, "neg": 0,
         "min6a1": None, "min6a1_V": None, "argmin": None,
         "maxV": -1, "argmaxV": None, "maxVh1z": -1, "argmaxVh1z": None,
         "maxh2": -1, "argmaxh2": None, "hits": []}
    stage1 = {}
    topnu = {}
    t0 = time.time()
    for W in range(WLO, WHI + 1):
        out, el = run(["--nutop", W, 3, 20260721 + W], "nutop_%d.log" % W)
        d = parse(out)
        combine(G, d)
        nus = []
        for ln in out.splitlines():
            m = re.match(r"^\s+V=(-?\d+) nu=(\d+),(\d+),(\d+),(\d+)", ln)
            if m:
                nus.append((int(m.group(1)), [int(m.group(k)) for k in (2, 3, 4, 5)]))
        topnu[W] = nus
        nshapes = int(re.search(r"nu_shapes=(\d+)", out).group(1))
        stage1[W] = {"nu_shapes": nshapes, "climb_tested": d["tested"], "climb_dim3": d["dim3"],
                     "climb_neg": d["neg"], "climb_min6a1": d["min6a1"], "climb_maxV": d["maxV"],
                     "best_nu": nus[:5], "seconds": round(el, 1)}
        print("W=%d shapes=%d climbed=%d maxV=%d min6a1=%s NEG=%d  (%.1fs)"
              % (W, nshapes, d["tested"], d["maxV"], d["min6a1"], d["neg"], el), flush=True)
    with open(os.path.join(HERE, "stage1_nutop.json"), "w") as f:
        json.dump({"stage1": stage1, "elapsed_s": round(time.time() - t0, 1)}, f, indent=1)

    # ---- stage 2: exhaustive splits of the best nu shapes ------------------
    # top 3 per weight, plus the top 12 at the max-V weight
    sel = []
    bestW = max(range(WLO, WHI + 1), key=lambda W: stage1[W]["climb_maxV"])
    for W in range(WLO, WHI + 1):
        for v, nu in topnu[W][:3]:
            if nu not in sel:
                sel.append(nu)
    for v, nu in topnu[bestW][:12]:
        if nu not in sel:
            sel.append(nu)
    stage2 = []
    for nu in sel:
        out, el = run(["--nu"] + nu, "nu_%s.log" % "_".join(map(str, nu)))
        d = parse(out)
        combine(G, d)
        stage2.append({"nu": nu, "W": sum(nu), "tested": d["tested"], "pruned_contain": d["pruned"],
                       "nonempty": d["nonempty"], "dim3": d["dim3"], "neg": d["neg"],
                       "min6a1": d["min6a1"], "maxV": d["maxV"], "maxV_hstar1_zero": d["maxVh1z"],
                       "max_hstar2": d["maxh2"], "seconds": round(el, 1), "exhaustive_splits": True})
        print("EXH nu=%s tested=%d dim3=%d maxV=%d min6a1=%s NEG=%d (%.1fs)"
              % (nu, d["tested"], d["dim3"], d["maxV"], d["min6a1"], d["neg"], el), flush=True)
        with open(os.path.join(HERE, "stage2_partial.json"), "w") as f:
            json.dump(stage2, f, indent=1)

    G["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "aggregate.json"), "w") as f:
        json.dump({"global": G, "stage1": stage1, "stage2": stage2, "bestW": bestW}, f, indent=1)
    print(json.dumps({k: G[k] for k in ("tested", "nonempty", "dim3", "neg", "min6a1", "maxV", "maxVh1z", "maxh2")}))


if __name__ == "__main__":
    sys.exit(main())
