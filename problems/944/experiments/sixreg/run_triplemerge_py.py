#!/usr/bin/env python3
# Fork-safe resumable TRIPLE-CONTRACTION (two-merge) n=13 quotient hunt.
# Near-regular family: base = 12-vertex conn Delta<=6 graphs, e in {29,30,31,32};
# apex (merged vertex) degree 7..11, residual base deficiency D'<=4 (all-mode auto-filter).
# Pipeline per shard: geng -c -D6 12 e:e r/MOD | core_hunt2 all 4
#   geng stderr -> s_<e>_<r>.gerr (">Z N"); core_hunt2 err -> .txt summary; validity read==N==>Z.
# 64 workers, CreateProcess (no Git-bash fork bomb). Resumable: valid shards skipped.
import os, re, subprocess, glob
from concurrent.futures import ThreadPoolExecutor, as_completed

SR = r"E:\Projects\ErdosProblems\problems\944\experiments\sixreg"
OUTDIR = os.path.join(SR, "core_hunt2_data")
GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
CH2 = os.path.join(SR, "core_hunt2.exe")
ECLASSES = [29, 30, 31, 32]
MOD = 4000
DMAX = "4"
WORKERS = 64

os.makedirs(OUTDIR, exist_ok=True)

def paths(e, r):
    return (os.path.join(OUTDIR, "s_%d_%d.gerr" % (e, r)),
            os.path.join(OUTDIR, "s_%d_%d.txt" % (e, r)),
            os.path.join(OUTDIR, "s_%d_%d.out" % (e, r)))

def valid(e, r):
    g, t, _ = paths(e, r)
    if not (os.path.exists(g) and os.path.exists(t)):
        return False
    try:
        mr = re.search(r"read=(\d+)", open(t, encoding="utf-8", errors="ignore").read())
        mz = re.search(r">Z\s+(\d+)", open(g, encoding="utf-8", errors="ignore").read())
    except Exception:
        return False
    return bool(mr and mz and mr.group(1) == mz.group(1))

def run_one(e, r):
    if valid(e, r):
        return ("skip", "")
    g, t, o = paths(e, r)
    arg = "%d/%d" % (r, MOD)
    for _ in range(3):
        with open(g, "wb") as fg, open(t, "wb") as ft, open(o, "wb") as fo:
            p1 = subprocess.Popen([GENG, "-c", "-D6", "12", "%d:%d" % (e, e), arg],
                                  stdout=subprocess.PIPE, stderr=fg)
            p2 = subprocess.Popen([CH2, "all", DMAX], stdin=p1.stdout, stdout=fo, stderr=ft)
            p1.stdout.close()
            p2.wait(); p1.wait()
        if valid(e, r):
            break
    summ = open(t, encoding="utf-8", errors="ignore").read().strip() if os.path.exists(t) else ""
    # survivor = a P3 candidate
    if os.path.exists(o):
        txt = open(o, encoding="utf-8", errors="ignore").read()
        if "CANDIDATE" in txt:
            with open(os.path.join(OUTDIR, "SURVIVORS.txt"), "a") as fs:
                fs.write("e=%d r=%d %s\n%s\n" % (e, r, summ, txt))
    # keep .out only if it has candidates; else discard to save disk
    if os.path.exists(o):
        keep = "CANDIDATE" in open(o, encoding="utf-8", errors="ignore").read()
        if not keep:
            try: os.remove(o)
            except OSError: pass
    return ("ok" if valid(e, r) else "FAIL", summ)

def main():
    jobs = [(e, r) for e in ECLASSES for r in range(MOD)]
    jobs = [(e, r) for (e, r) in jobs if not valid(e, r)]
    print("shards to run: %d (e in %s, MOD=%d) workers=%d" % (len(jobs), ECLASSES, MOD, WORKERS), flush=True)
    done = fails = surv = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_one, e, r): (e, r) for (e, r) in jobs}
        for fut in as_completed(futs):
            st, summ = fut.result()
            done += 1
            if st == "FAIL": fails += 1
            if done % 1000 == 0:
                print("progress %d/%d fails=%d" % (done, len(jobs), fails), flush=True)
    # aggregate over ALL valid shards
    tot = dict(read=0, bases=0, apexings=0, P1pass=0, P2pass=0, P3pass=0)
    per_e = {e: dict(read=0, P2pass=0, P3pass=0, shards=0) for e in ECLASSES}
    nsh = 0
    for t in glob.glob(os.path.join(OUTDIR, "s_*_*.txt")):
        b = os.path.basename(t)[2:-4]
        e, r = (int(x) for x in b.split("_"))
        if not valid(e, r): continue
        nsh += 1
        s = open(t, encoding="utf-8", errors="ignore").read()
        for k in tot:
            m = re.search(k + r"=(\d+)", s)
            if m: tot[k] += int(m.group(1))
        per_e[e]["shards"] += 1
        for k in ("read", "P2pass", "P3pass"):
            m = re.search(k + r"=(\d+)", s)
            if m: per_e[e][k] += int(m.group(1))
    with open(os.path.join(OUTDIR, "agg.txt"), "w") as f:
        f.write("AGG shards=%d " % nsh + " ".join("%s=%d" % (k, tot[k]) for k in
               ("read", "bases", "apexings", "P1pass", "P2pass", "P3pass")) + "\n")
        for e in ECLASSES:
            f.write("  e=%d %s\n" % (e, per_e[e]))
        f.write("PY_FINISHED fails=%d\n" % fails)
    print("DONE fails=%d" % fails, flush=True)
    print(open(os.path.join(OUTDIR, "agg.txt")).read(), flush=True)

if __name__ == "__main__":
    main()
