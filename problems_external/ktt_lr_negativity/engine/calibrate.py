#!/usr/bin/env python3
"""
calibrate.py -- CALIBRATION GATE for the two independent exact LR engines.

  Engine A: lr_hive.exe            (C++, Knutson-Tao hive model)
  Engine B: engineB_lrrule.py      (Python, classical LR lattice-word rule)

Phases (all arithmetic exact; outputs compared as raw decimal strings):
  1. Cross-compare A vs B on 300 random triples, r(nu)<=5, |nu|<=16
     (280 seeded random weight-matched triples + 20 deterministic edge triples,
      incl. weight-mismatch, too-many-parts, empty partitions, cap semantics).
     Exact match required on EVERY line.
  2. 20 random c=1 triples (both engines agree c=1): stretched counts
     c(n*nu; n*lam, n*mu) for n=1..6 must equal 1 on BOTH engines (KTW).
  3. 20 random c=2 triples: stretched counts must equal n+1 for n=1..6 on
     BOTH engines (Ikenmeyer/Sherman).

Artifacts under calib/: batch inputs, raw engine outputs, summary.json.
Exit 0 iff every check passed. Deterministic seeds recorded below.
"""

import hashlib
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_A = os.path.join(HERE, "lr_hive.exe")
ENGINE_B = os.path.join(HERE, "engineB_lrrule.py")
CALIB = os.path.join(HERE, "calib")
PY = sys.executable

SEED_300 = 20260721001   # phase 1 random triples
SEED_C1 = 20260721002    # phase 2 pool draw
SEED_C2 = 20260721003    # phase 3 pool draw

N_RANDOM = 280
N_EDGE = 20
N_C1 = 20
N_C2 = 20
STRETCH_MAX = 6
POOL_NU_MAX = 12         # keep stretch-by-6 cheap: |n*nu| <= 72


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def partitions_maxparts(n, maxparts, maxpart=None):
    """All partitions of n with at most maxparts parts (weakly decreasing)."""
    if maxpart is None:
        maxpart = n
    if n == 0:
        return [()]
    out = []
    for first in range(min(n, maxpart), 0, -1):
        if maxparts == 0:
            break
        for rest in partitions_maxparts(n - first, maxparts - 1, first):
            out.append((first,) + rest)
    return out


_PCACHE = {}


def pset(n, maxparts=5):
    key = (n, maxparts)
    if key not in _PCACHE:
        _PCACHE[key] = partitions_maxparts(n, maxparts)
    return _PCACHE[key]


def pstr(p):
    return ",".join(str(x) for x in p) if p else "0"


def scale(p, n):
    return tuple(n * x for x in p)


def run_batch(engine, batch_path, out_path):
    """Run one engine in batch mode; return list of raw output lines."""
    if engine == "A":
        cmd = [ENGINE_A, "--batch", batch_path]
    else:
        cmd = [PY, ENGINE_B, "--batch", batch_path]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    dt = time.time() - t0
    if r.returncode != 0:
        raise RuntimeError(
            f"engine {engine} batch failed rc={r.returncode}: {r.stderr[:500]}")
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip() != ""]
    with open(out_path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return lines, dt


def gen_random_triples(rng, count):
    """Weight-matched random triples: nu r<=5, |nu|<=16, |lam|+|mu|=|nu|."""
    triples = []
    seen = set()
    while len(triples) < count:
        N = rng.randint(2, 16)
        nu = rng.choice(pset(N, 5))
        k = rng.randint(1, N - 1)
        lam = rng.choice(pset(k, 5))
        mu = rng.choice(pset(N - k, 5))
        t = (lam, mu, nu)
        if t in seen:
            continue
        seen.add(t)
        triples.append(t)
    return triples


def edge_lines():
    """20 deterministic edge lines: (line, why). Cap column exercised."""
    e = []
    # 8 weight mismatches -> 0
    for lam, mu, nu in [("3,1", "2,1", "5,3"), ("4", "4", "4,3,2"),
                        ("2,2", "1,1", "2,2,1"), ("5,1", "1", "5,1"),
                        ("1", "1", "3"), ("6,2", "2,1", "6,2,1,1,1"),
                        ("3,3,3", "3", "3,3,3,3,3"), ("2", "2", "5")]:
        e.append((f"{lam};{mu};{nu}", "weight mismatch -> 0"))
    # 6 too-many-parts (lam or mu has more parts than nu) -> 0
    for lam, mu, nu in [("1,1,1,1,1,1", "2", "4,2,1,1"),
                        ("2", "1,1,1,1,1,1", "4,2,1,1"),
                        ("2,1,1,1,1,1", "1", "4,2,1,1"),
                        ("1,1,1,1,1,1,1,1", "1,1", "5,4,1"),
                        ("3,1,1,1", "2,1", "6,3"),
                        ("1,1,1,1,1,1", "1,1,1,1,1,1", "6,4,2")]:
        e.append((f"{lam};{mu};{nu}", "parts(lam/mu) > parts(nu) -> 0"))
    # 3 empty-partition forms
    e.append(("0;3,3,1;3,3,1", "empty lam -> c=1"))
    e.append(("3,2;0;3,2", "empty mu -> c=1"))
    e.append(("0;0;0", "all empty -> c=1"))
    # 3 cap-semantics lines (c=2 triple)
    e.append(("2,1;2,1;3,2,1;1", "cap 1 < c=2 -> CAP_EXCEEDED"))
    e.append(("2,1;2,1;3,2,1;2", "cap 2 = c -> 2"))
    e.append(("2,1;2,1;3,2,1;1000000000000", "big cap -> 2"))
    assert len(e) == N_EDGE
    return e


def phase1(summary):
    rng = random.Random(SEED_300)
    triples = gen_random_triples(rng, N_RANDOM)
    lines = [f"{pstr(l)};{pstr(m)};{pstr(n)}" for (l, m, n) in triples]
    lines += [ln for (ln, _why) in edge_lines()]
    batch = os.path.join(CALIB, "triples300.batch")
    with open(batch, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    outA, dtA = run_batch("A", batch, os.path.join(CALIB, "phase1_A.out"))
    outB, dtB = run_batch("B", batch, os.path.join(CALIB, "phase1_B.out"))
    mism = []
    if len(outA) != len(lines) or len(outB) != len(lines):
        mism.append(f"line-count A={len(outA)} B={len(outB)} in={len(lines)}")
    else:
        for i, (a, b) in enumerate(zip(outA, outB)):
            if a != b:
                mism.append(f"line {i+1} [{lines[i]}]: A={a} B={b}")
    nonzero = sum(1 for v in outA if v not in ("0",) and v.isdigit())
    dist = {}
    for v in outA:
        dist[v] = dist.get(v, 0) + 1
    summary["phase1"] = {
        "n_lines": len(lines), "n_random": N_RANDOM, "n_edge": N_EDGE,
        "seed": SEED_300, "mismatches": mism,
        "batch_sha256": sha256(batch),
        "outA_sha256": sha256(os.path.join(CALIB, "phase1_A.out")),
        "outB_sha256": sha256(os.path.join(CALIB, "phase1_B.out")),
        "runtime_A_s": round(dtA, 2), "runtime_B_s": round(dtB, 2),
        "nonzero_count": nonzero,
        "value_distribution": {k: dist[k] for k in sorted(
            dist, key=lambda s: (len(s), s))},
        "pass": not mism,
    }
    return not mism


def find_pool(target_c, need, seed, max_rounds=200):
    """Random triples where BOTH engines return target_c; |nu|<=POOL_NU_MAX."""
    rng = random.Random(seed)
    pool = []
    seen = set()
    rounds = 0
    while len(pool) < need and rounds < max_rounds:
        rounds += 1
        cand = []
        while len(cand) < 400:
            N = rng.randint(3, POOL_NU_MAX)
            nu = rng.choice(pset(N, 5))
            k = rng.randint(1, N - 1)
            lam = rng.choice(pset(k, 5))
            mu = rng.choice(pset(N - k, 5))
            t = (lam, mu, nu)
            if t in seen:
                continue
            seen.add(t)
            cand.append(t)
        batch = os.path.join(CALIB, f"pool_c{target_c}_round{rounds}.batch")
        with open(batch, "w", newline="\n") as f:
            f.write("\n".join(
                f"{pstr(l)};{pstr(m)};{pstr(n)}" for (l, m, n) in cand) + "\n")
        outA, _ = run_batch("A", batch, batch + ".A")
        outB, _ = run_batch("B", batch, batch + ".B")
        for t, a, b in zip(cand, outA, outB):
            if a != b:
                raise RuntimeError(f"pool disagreement on {t}: A={a} B={b}")
            if a == str(target_c):
                pool.append(t)
        # keep only round files that contributed; delete bulky rejects
        for ext in ("", ".A", ".B"):
            os.remove(batch + ext)
    if len(pool) < need:
        raise RuntimeError(f"pool c={target_c}: only {len(pool)} found")
    draw = random.Random(seed + 7).sample(pool, need)
    return draw, len(pool)


def stretch_phase(name, target_c, expect_fn, seed, summary):
    draw, poolsize = find_pool(target_c, {1: N_C1, 2: N_C2}[target_c], seed)
    lines, meta = [], []
    for (lam, mu, nu) in draw:
        for n in range(1, STRETCH_MAX + 1):
            lines.append(f"{pstr(scale(lam, n))};{pstr(scale(mu, n))};"
                         f"{pstr(scale(nu, n))}")
            meta.append((lam, mu, nu, n))
    batch = os.path.join(CALIB, f"stretch_{name}.batch")
    with open(batch, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    outA, dtA = run_batch("A", batch, os.path.join(CALIB, f"stretch_{name}_A.out"))
    outB, dtB = run_batch("B", batch, os.path.join(CALIB, f"stretch_{name}_B.out"))
    fails = []
    for (lam, mu, nu, n), a, b in zip(meta, outA, outB):
        exp = str(expect_fn(n))
        if a != exp or b != exp:
            fails.append(f"({pstr(lam)};{pstr(mu)};{pstr(nu)}) n={n}: "
                         f"A={a} B={b} expected={exp}")
    summary[name] = {
        "seed": seed, "pool_size_found": poolsize,
        "triples": [f"{pstr(l)};{pstr(m)};{pstr(n)}" for (l, m, n) in draw],
        "n_checks": len(lines), "failures": fails,
        "batch_sha256": sha256(batch),
        "outA_sha256": sha256(os.path.join(CALIB, f"stretch_{name}_A.out")),
        "outB_sha256": sha256(os.path.join(CALIB, f"stretch_{name}_B.out")),
        "runtime_A_s": round(dtA, 2), "runtime_B_s": round(dtB, 2),
        "pass": not fails,
    }
    return not fails


def main():
    os.makedirs(CALIB, exist_ok=True)
    summary = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "engineA": ENGINE_A, "engineB": ENGINE_B,
               "engineA_sha256": sha256(ENGINE_A),
               "engineB_sha256": sha256(ENGINE_B)}
    ok1 = phase1(summary)
    print(f"PHASE1 (300-triple cross-compare): {'PASS' if ok1 else 'FAIL'}")
    if not ok1:
        for m in summary["phase1"]["mismatches"][:20]:
            print("  MISMATCH:", m)
    ok2 = stretch_phase("c1", 1, lambda n: 1, SEED_C1, summary)
    print(f"PHASE2 (20 c=1 stretched n=1..6 == 1): {'PASS' if ok2 else 'FAIL'}")
    if not ok2:
        for m in summary["c1"]["failures"][:20]:
            print("  FAIL:", m)
    ok3 = stretch_phase("c2", 2, lambda n: n + 1, SEED_C2, summary)
    print(f"PHASE3 (20 c=2 stretched n=1..6 == n+1): {'PASS' if ok3 else 'FAIL'}")
    if not ok3:
        for m in summary["c2"]["failures"][:20]:
            print("  FAIL:", m)
    summary["all_pass"] = ok1 and ok2 and ok3
    with open(os.path.join(CALIB, "summary.json"), "w", newline="\n") as f:
        json.dump(summary, f, indent=1)
    print("OVERALL:", "PASS" if summary["all_pass"] else "FAIL")
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
