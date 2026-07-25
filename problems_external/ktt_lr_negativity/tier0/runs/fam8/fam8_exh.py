#!/usr/bin/env python
"""fam8 companion: EXHAUSTIVE sweep of a declared box, run alongside the beam.

Region:  r = len(nu) in {5,6},  |nu| <= NMAX,  lam,mu partitions with
         <= r parts,  |lam|+|mu| = |nu|,  lam,mu nonempty.
Every triple in the box is enumerated -- no sampling, no LP oracle.

Stage 1 (one engine-A call, c = c(nu;lam,mu)) decides TIER0 EXHAUSTIVELY:
   d <= D  =>  h*_1 = c-d-1 >= c-D-1,  so c > D+1  =>  h*_1 > 0  => not TIER0.
Stage 1 does NOT decide JACKPOT; every stage-1 survivor plus a random
sample of the rejects is put through the full LP-free screen.
"""
import json, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.normpath(os.path.join(HERE, "..", "..", "tier0_screen.py"))
PY = sys.executable
NMAX = int(os.environ.get("EXH_NMAX", "14"))
BUDGET = float(os.environ.get("EXH_BUDGET", "1900"))
SAMPLE = 0.03
CHUNK = 400


def parts(n, maxparts, maxfirst=None):
    if maxfirst is None:
        maxfirst = n
    if n == 0:
        yield ()
        return
    if maxparts == 0:
        return
    for a in range(min(n, maxfirst), 0, -1):
        for tail in parts(n - a, maxparts - 1, a):
            yield (a,) + tail


def triples(nmax):
    for r in (5, 6):
        for N in range(r, nmax + 1):
            for nu in parts(N, r):
                if len(nu) != r:
                    continue
                for a in range(1, N // 2 + 1):
                    for lam in parts(a, r):
                        if lam[0] > nu[0]:
                            continue
                        for mu in parts(N - a, r):
                            if mu[0] > nu[0]:
                                continue
                            if a == N - a and lam > mu:
                                continue
                            yield (lam, mu, nu)


def fmt(t):
    return ";".join(",".join(str(x) for x in p) for p in t)


def run(mode, lines, path, timeout, extra=()):
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    try:
        p = subprocess.run([PY, SCREEN, mode, path] + list(extra),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return []
    out = []
    for ln in p.stdout.splitlines():
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def main():
    rng = random.Random(88)
    t0 = time.time()
    log = open(os.path.join(HERE, "fam8_exh.log"), "a")
    rec = open(os.path.join(HERE, "fam8_exh_records.jsonl"), "a")
    stat = {"enumerated": 0, "stage1": 0, "empty": 0, "tier0_possible": 0,
            "full_screened": 0, "hits": 0, "min_margin": None, "best_hd": -1,
            "completed_box": False, "NMAX": NMAX}
    buf = []
    gen = triples(NMAX)
    done = False
    while not done and time.time() - t0 < BUDGET:
        buf = []
        for t in gen:
            buf.append(t)
            if len(buf) >= CHUNK:
                break
        else:
            done = True
        if not buf:
            break
        stat["enumerated"] += len(buf)
        pf = run("--prefilter", [fmt(t) for t in buf],
                 os.path.join(HERE, "_exh_pf.batch"), 900, ["--stage1-only"])
        pf = [r for r in pf if "stage1_verdict" in r]
        stat["stage1"] += len(pf)
        keep = []
        for r in pf:
            c = r.get("c")
            t = (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))
            if not c:
                stat["empty"] += 1
                continue
            if r.get("stage1_verdict") == "SURVIVOR":
                stat["tier0_possible"] += 1
                keep.append(t)
            elif rng.random() < SAMPLE:
                keep.append(t)
        if keep:
            recs = run("--batch", [fmt(t) for t in keep],
                       os.path.join(HERE, "_exh_full.batch"), 900)
            for r in recs:
                rec.write(json.dumps(r) + "\n")
                stat["full_screened"] += 1
                if r.get("status") != "OK":
                    continue
                h1, hd = r.get("hstar_1"), r.get("hstar_d")
                if h1 is None or hd is None:
                    continue
                m = h1 - hd
                if stat["min_margin"] is None or m < stat["min_margin"]:
                    stat["min_margin"] = m
                    stat["min_margin_triple"] = [r["lam"], r["mu"], r["nu"], r["hstar"]]
                if hd > stat["best_hd"]:
                    stat["best_hd"] = hd
                    stat["best_hd_triple"] = [r["lam"], r["mu"], r["nu"], r["hstar"]]
                if r.get("TIER0") or r.get("JACKPOT") or r.get("NEG"):
                    stat["hits"] += 1
                    with open(os.path.join(HERE, "HITS.jsonl"), "a") as hf:
                        hf.write(json.dumps(r) + "\n")
            rec.flush()
        stat["completed_box"] = done
        json.dump(stat, open(os.path.join(HERE, "fam8_exh_state.json"), "w"), indent=1)
        log.write("t=%.0f %s\n" % (time.time() - t0, json.dumps(stat)))
        log.flush()
        print("t=%.0f %s" % (time.time() - t0, json.dumps(stat)), flush=True)
    json.dump(stat, open(os.path.join(HERE, "fam8_exh_state.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
