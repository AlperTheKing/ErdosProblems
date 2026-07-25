#!/usr/bin/env python3
"""fam9 companion -- EXHAUSTIVE sweep of the small-|nu| window at r = 5.

For every nu = partition of N into exactly 5 positive parts, and every pair
(lam, mu) of partitions with at most 5 parts, |lam|+|mu| = N, lam subset nu,
mu subset nu (both necessary for c > 0), screen the triple.  Symmetry
lam <-> mu quotiented.  This is EXHAUSTIVE in the stated window.
"""
import json, os, subprocess, sys, itertools, time

HERE = os.path.dirname(os.path.abspath(__file__))
SCREEN = os.path.join(HERE, "..", "..", "tier0_screen.py")


def parts_le(n, k, mx):
    """partitions of n into at most k parts, each <= mx"""
    if n == 0:
        yield ()
        return
    if k == 0:
        return
    for first in range(min(n, mx), 0, -1):
        for rest in parts_le(n - first, k - 1, first):
            yield (first,) + rest


def parts_exact(n, k):
    """partitions of n into exactly k positive parts"""
    for p in parts_le(n, k, n):
        if len(p) == k:
            yield p


def subset(a, b):
    return all((a[i] if i < len(a) else 0) <= b[i] for i in range(len(b))) and len(a) <= len(b)


def fmt(t):
    return ";".join(",".join(map(str, p)) for p in t)


def gen(N):
    out = set()
    for nu in parts_exact(N, 5):
        for k in range(1, N):
            for lam in parts_le(k, 5, nu[0]):
                if not subset(lam, nu):
                    continue
                for mu in parts_le(N - k, 5, nu[0]):
                    if not subset(mu, nu):
                        continue
                    a, b = (lam, mu) if lam >= mu else (mu, lam)
                    out.add((a, b, nu))
    return sorted(out)


def screen(triples, tag):
    path = os.path.join(HERE, "_ex_%s_%s.txt" % (os.environ.get("SH","0"), tag))
    with open(path, "w") as f:
        for t in triples:
            f.write(fmt(t) + "\n")
    p = subprocess.run([sys.executable, SCREEN, "--batch", path],
                       capture_output=True, text=True)
    recs = []
    for line in p.stdout.splitlines():
        if line.strip().startswith("{"):
            try:
                recs.append(json.loads(line))
            except Exception:
                pass
    os.remove(path)
    return recs


def main():
    Ns = [int(x) for x in sys.argv[1].split(",")]
    deadline = time.time() + float(sys.argv[2])
    shard = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nsh = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    tested = 0
    stats = {}
    best_hd = (-1, None)
    best_margin = (10 ** 9, None, None, None, None)
    hits = []
    margin_hist = {}
    nonfull = 0
    interior_recs = []
    done_N = []
    for N in Ns:
        tri = gen(N)
        tri = [t for i, t in enumerate(tri) if i % nsh == shard]
        print("N=%d shard=%d/%d triples=%d" % (N, shard, nsh, len(tri)), flush=True)
        aborted = False
        for i in range(0, len(tri), 500):
            if time.time() > deadline:
                print("deadline hit inside N=%d at %d/%d" % (N, i, len(tri)), flush=True)
                aborted = True
                break
            for rec in screen(tri[i:i + 500], "%d_%d" % (N, i)):
                tested += 1
                st = rec.get("status")
                stats[st] = stats.get(st, 0) + 1
                if st != "OK":
                    continue
                d, r = rec["d"], rec["r"]
                if d < (r - 1) * (r - 2) // 2:
                    nonfull += 1
                h1, hd = rec["hstar_1"], rec["hstar_d"]
                t = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
                if hd is not None and hd > best_hd[0]:
                    best_hd = (hd, t)
                if d >= 2 and h1 is not None:
                    m = h1 - hd
                    margin_hist[m] = margin_hist.get(m, 0) + 1
                    if m < best_margin[0]:
                        best_margin = (m, t, rec["hstar"], d, rec["c"])
                if hd and hd >= 1 and d >= 4:
                    interior_recs.append([rec["hstar_sum"], h1 - hd, d, rec["c"],
                                          [list(x) for x in t], rec["hstar"]])
                if rec.get("TIER0") or rec.get("JACKPOT") or rec.get("NEG"):
                    hits.append(rec)
                    print("!!! HIT", t, rec["hstar"], flush=True)
        if not aborted:
            done_N.append(N)
        print("  cum tested=%d minMargin=%s bestHd=%s hits=%d" %
              (tested, best_margin[0], best_hd[0], len(hits)), flush=True)
        if time.time() > deadline:
            break
    interior_recs.sort()
    out = {"window": "r=5, |nu| in %s, exhaustive over all (lam,mu,nu) with "
                     "lam,mu subset nu, |lam|+|mu|=|nu|, nu with exactly 5 "
                     "positive parts; lam<->mu quotiented" % Ns,
           "fully_completed_N": done_N,
           "triplesTested": tested, "status_counts": stats,
           "bestHstarD": {"value": best_hd[0],
                          "triple": [list(x) for x in best_hd[1]] if best_hd[1] else None},
           "minH1MinusHD": {"value": best_margin[0],
                            "triple": [list(x) for x in best_margin[1]] if best_margin[1] else None,
                            "hstar": best_margin[2], "d": best_margin[3], "c": best_margin[4]},
           "margin_histogram": {str(k): v for k, v in sorted(margin_hist.items())},
           "nonFullDimCount": nonfull,
           "interior_d_ge_4": interior_recs[:200],
           "hits": hits}
    with open(os.path.join(HERE, "exhaust9_result_%s.json" % os.environ.get("SH","0")), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("fully_completed_N", "triplesTested",
                                          "status_counts", "bestHstarD",
                                          "minH1MinusHD", "nonFullDimCount",
                                          "margin_histogram")}, indent=1))
    print("interior_d_ge_4 count", len(interior_recs), "hits", len(hits))


if __name__ == "__main__":
    main()
