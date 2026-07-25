"""Stage 1 of the fam3 census: exhaustive r=6, |nu|<=22.

Enumerates every triple (lam,mu,nu) with
  - nu a partition with EXACTLY 6 positive parts, |nu| <= 22   (=> r = 6, D = 10)
  - lam, mu partitions with at most 6 parts, |lam| + |mu| = |nu|
  - lam_i <= nu_i and mu_i <= nu_i  (containment: NECESSARY for c > 0,
    Littlewood-Richardson; a triple failing it has c = 0 and is EMPTY, and
    the engine is still run on a random control sample to confirm)
  - |lam| <= |mu|, and lam <= mu lexicographically when |lam| = |mu|
    (c(nu;lam,mu) = c(nu;mu,lam) so the polytopes have identical P and h*)

and calls engine A once per triple at n = 1 to get c.  This is exactly
stage 1 of tier0_screen.prefilter_triples (one engine call, n = 1); the
verdicts are recomputed here with the same rules:
    c = 0            -> REJECT_EMPTY
    c > D + 1 = 11   -> REJECT_HSTAR1_POSITIVE  (TIER0 impossible; JACKPOT
                        NOT decided -- those go to the stratified stage 2)
    otherwise        -> SURVIVOR
Agreement with the instrument is checked separately on a sample.
"""
import os, sys, subprocess, json, time
from multiprocessing import Pool

ENGINE_A = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine/lr_hive.exe"
WORK = r"C:/Users/a/AppData/Local/Temp/claude/E--Projects-ErdosProblems/f1987d98-c6e4-47b0-90c4-e402adf2c40c/scratchpad/s1"
CAP = 10**12
NUMAX = 22
R = 6
D = (R - 1) * (R - 2) // 2  # 10


def parts_exact(n, k, maxpart=None):
    if maxpart is None:
        maxpart = n
    if k == 0:
        if n == 0:
            yield ()
        return
    if n < k:
        return
    for first in range(min(maxpart, n - k + 1), 0, -1):
        for rest in parts_exact(n - first, k - 1, first):
            yield (first,) + rest


def parts_atmost_cont(n, nu):
    """partitions of n with at most len(nu) parts, contained in nu."""
    res = []
    k = len(nu)

    def rec(rem, i, prev, cur):
        if rem == 0:
            res.append(tuple(cur))
            return
        if i >= k:
            return
        hi = min(prev, nu[i], rem)
        # need rem <= hi*(k-i)
        lo = max(1, -(-rem // (k - i)))
        for v in range(hi, lo - 1, -1):
            cur.append(v)
            rec(rem - v, i + 1, v, cur)
            cur.pop()

    rec(n, 0, n, [])
    return res


def gen_triples():
    for m in range(R, NUMAX + 1):
        for nu in parts_exact(m, R):
            sub = {}
            for a in range(0, m + 1):
                sub[a] = parts_atmost_cont(a, nu)
            for a in range(0, m // 2 + 1):
                b = m - a
                for lam in sub[a]:
                    for mu in sub[b]:
                        if a == b and lam > mu:
                            continue
                        yield (lam, mu, nu)


def fmt(p):
    return ",".join(str(x) for x in p) if p else "0"


def run_shard(idx):
    path = os.path.join(WORK, "sh%03d.batch" % idx)
    out = subprocess.run([ENGINE_A, "--batch", path],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("engine exit %d: %s" % (out.returncode, out.stderr[:300]))
    lines = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    with open(path, "r") as f:
        inp = [ln.strip() for ln in f if ln.strip()]
    if len(lines) != len(inp):
        raise RuntimeError("shard %d: %d out for %d in" % (idx, len(lines), len(inp)))
    with open(os.path.join(WORK, "sh%03d.out" % idx), "w") as f:
        f.write("\n".join(lines) + "\n")
    return idx, len(lines)


def main():
    os.makedirs(WORK, exist_ok=True)
    t0 = time.time()
    trips = list(gen_triples())
    n = len(trips)
    print("triples", n, "gen %.1fs" % (time.time() - t0), flush=True)
    NSH = 240
    per = (n + NSH - 1) // NSH
    shards = []
    for i in range(NSH):
        chunk = trips[i * per:(i + 1) * per]
        if not chunk:
            break
        with open(os.path.join(WORK, "sh%03d.batch" % i), "w", newline="\n") as f:
            f.write("\n".join("%s;%s;%s;%d" % (fmt(l), fmt(m), fmt(v), CAP)
                              for (l, m, v) in chunk) + "\n")
        shards.append(i)
    print("shards", len(shards), "per", per, flush=True)
    t1 = time.time()
    with Pool(60) as pool:
        for idx, k in pool.imap_unordered(run_shard, shards):
            pass
    print("engine %.1fs" % (time.time() - t1), flush=True)

    # collate
    stats = {"EMPTY": 0, "REJECT_HSTAR1_POSITIVE": 0, "SURVIVOR": 0, "CAP": 0}
    surv = []
    cbig = []
    ci = 0
    for i in shards:
        with open(os.path.join(WORK, "sh%03d.out" % i)) as f:
            vals = [ln.strip() for ln in f if ln.strip()]
        for v in vals:
            t = trips[ci]
            ci += 1
            try:
                c = int(v)
            except ValueError:
                stats["CAP"] += 1
                continue
            if c == 0:
                stats["EMPTY"] += 1
            elif c > D + 1:
                stats["REJECT_HSTAR1_POSITIVE"] += 1
                cbig.append((c, t))
            else:
                stats["SURVIVOR"] += 1
                surv.append((c, t))
    assert ci == n, (ci, n)
    print(json.dumps(stats), flush=True)
    with open(os.path.join(WORK, "survivors.txt"), "w", newline="\n") as f:
        for c, (l, m, v) in surv:
            f.write("%s;%s;%s\n" % (fmt(l), fmt(m), fmt(v)))
    with open(os.path.join(WORK, "cbig.txt"), "w", newline="\n") as f:
        for c, (l, m, v) in cbig:
            f.write("%d|%s;%s;%s\n" % (c, fmt(l), fmt(m), fmt(v)))
    json.dump({"triples": n, "stats": stats, "D": D, "NUMAX": NUMAX,
               "elapsed_s": time.time() - t0},
              open(os.path.join(WORK, "stage1.json"), "w"), indent=1)
    print("survivors", len(surv), "cbig", len(cbig), flush=True)


if __name__ == "__main__":
    main()
