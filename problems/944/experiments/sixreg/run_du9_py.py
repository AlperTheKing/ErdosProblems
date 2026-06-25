#!/usr/bin/env python3
# Fork-safe resumable d_u=9 descent-core hunt completion.
# Replaces run_du9_resume.sh (xargs -P64 bash -c) which fork-bombed Git-bash (0xC000026B).
# Python on Windows uses CreateProcess (no fork emulation) -> no fork bomb.
# Pipeline per residue r: geng -d3 -D6 13 33:33 r/28160 | core_hunt.exe p9
#   geng stderr  -> s_<r>.gerr  (must contain ">Z N")
#   core_hunt err-> s_<r>.txt   (summary: read=N ... P3pass=z); validity: read==N==>Z
#   core_hunt out-> discarded (per-graph CHI4-NONCRIT dump, not needed)
import os, re, sys, subprocess, glob
from concurrent.futures import ThreadPoolExecutor, as_completed

SR = r"E:\Projects\ErdosProblems\problems\944\experiments\sixreg"
OUTDIR = os.path.join(SR, "core_hunt9b")
GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
COREHUNT = os.path.join(SR, "core_hunt.exe")
MOD = 28160
WORKERS = 64

def valid(r):
    t = os.path.join(OUTDIR, "s_%d.txt" % r)
    g = os.path.join(OUTDIR, "s_%d.gerr" % r)
    if not (os.path.exists(t) and os.path.exists(g)):
        return False
    try:
        mr = re.search(r"read=(\d+)", open(t, encoding="utf-8", errors="ignore").read())
        mz = re.search(r">Z\s+(\d+)", open(g, encoding="utf-8", errors="ignore").read())
    except Exception:
        return False
    return bool(mr and mz and mr.group(1) == mz.group(1))

def run_one(r):
    if valid(r):
        return (r, "skip", "")
    gerr = os.path.join(OUTDIR, "s_%d.gerr" % r)
    txt = os.path.join(OUTDIR, "s_%d.txt" % r)
    arg = "%d/%d" % (r, MOD)
    for _ in range(3):
        with open(gerr, "wb") as fg, open(txt, "wb") as ft:
            p1 = subprocess.Popen([GENG, "-d3", "-D6", "13", "33:33", arg],
                                  stdout=subprocess.PIPE, stderr=fg)
            p2 = subprocess.Popen([COREHUNT, "p9"], stdin=p1.stdout,
                                  stdout=subprocess.DEVNULL, stderr=ft)
            p1.stdout.close()
            p2.wait(); p1.wait()
        if valid(r):
            break
    summ = open(txt, encoding="utf-8", errors="ignore").read().strip() if os.path.exists(txt) else ""
    if re.search(r"P3pass=[1-9]", summ):
        with open(os.path.join(OUTDIR, "SURVIVORS.txt"), "a") as fs:
            fs.write("SURVIVOR r=%d %s\n" % (r, summ))
    return (r, "ok" if valid(r) else "FAIL", summ)

def main():
    todo_file = os.path.join(OUTDIR, "remaining.txt")
    residues = []
    with open(todo_file) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                residues.append(int(ln))
    residues = [r for r in residues if not valid(r)]
    total = len(residues)
    print("residues to run: %d  workers=%d" % (total, WORKERS), flush=True)
    done = 0; fails = 0; survivors = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_one, r): r for r in residues}
        for fut in as_completed(futs):
            r, st, summ = fut.result()
            done += 1
            if st == "FAIL":
                fails += 1
            if "P3pass=" in summ and not summ.rstrip().endswith("P3pass=0"):
                survivors += 1
            if done % 500 == 0:
                print("progress %d/%d done, fails=%d survivors=%d" % (done, total, fails, survivors), flush=True)
    # Aggregate over ALL valid shards in core_hunt9b.
    tot = dict(read=0, bases=0, apexings=0, P1pass=0, P2pass=0, P3pass=0)
    nsh = 0
    for t in glob.glob(os.path.join(OUTDIR, "s_*.txt")):
        r = int(os.path.basename(t)[2:-4])
        if not valid(r):
            continue
        nsh += 1
        for k in tot:
            m = re.search(k + r"=(\d+)", open(t, encoding="utf-8", errors="ignore").read())
            if m:
                tot[k] += int(m.group(1))
    agg = os.path.join(OUTDIR, "agg9b.txt")
    with open(agg, "w") as f:
        line = "AGG shards=%d " % nsh + " ".join("%s=%d" % (k, tot[k]) for k in
               ("read", "bases", "apexings", "P1pass", "P2pass", "P3pass"))
        f.write(line + "\n")
        f.write("PY_FINISHED fails=%d\n" % fails)
    print("DONE. fails=%d  survivors=%d" % (fails, survivors), flush=True)
    print(open(agg).read(), flush=True)

if __name__ == "__main__":
    main()
