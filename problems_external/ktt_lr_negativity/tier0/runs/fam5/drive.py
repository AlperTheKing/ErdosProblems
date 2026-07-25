#!/usr/bin/env python
"""fam5 driver: two-stage, parallel.

Stage 1  : one engine-A call at n=1 per triple -> c.  Only c == 0 (EMPTY, i.e.
           Q is not a polytope at all) is dropped.  NOTHING with c >= 1 is
           dropped -- in particular no h*_1-positive rejection, because the
           JACKPOT condition h*_d > h*_1 is undetermined there.
Stage 2  : the mandated full screen (screen_triples from tier0_screen) on
           every survivor, run in parallel chunks.
All arithmetic inside tier0_screen; this file only schedules.
"""
import os, sys, json, argparse, math
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TIER0 = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, TIER0)
import tier0_screen as T


def parse_line(ln):
    a, b, c = ln.strip().split(";")
    return (T.parse_partition(a), T.parse_partition(b), T.parse_partition(c))


def stage1_chunk(args):
    triples, cap = args
    try:
        return T.engineA_batch([(l, m, v) for (l, m, v) in triples], cap=cap)
    except Exception:
        if len(triples) == 1:
            return ["ERROR"]
        h = len(triples) // 2
        return (stage1_chunk((triples[:h], cap)) +
                stage1_chunk((triples[h:], cap)))


def stage2_chunk(args):
    """Full mandated screen on a chunk.  If the engine process fails on the
    chunk, split and retry, finally per triple; a triple that still fails is
    recorded as ENGINE_ERROR (a SKIP, never a math verdict)."""
    triples, cap = args
    try:
        return T.screen_triples(triples, cap=cap)
    except Exception as e:
        if len(triples) == 1:
            l, m, v = triples[0]
            return [{"lam": list(l), "mu": list(m), "nu": list(v),
                     "r": len(v), "status": "ENGINE_ERROR", "error": str(e)[:200],
                     "neg": False, "NEG": False, "JACKPOT": False, "TIER0": False,
                     "hstar_1": None, "hstar_d": None, "INTERIOR": None}]
        h = len(triples) // 2
        return (stage2_chunk((triples[:h], cap)) +
                stage2_chunk((triples[h:], cap)))


def chunks(seq, k):
    n = len(seq)
    if n == 0:
        return []
    size = max(1, math.ceil(n / k))
    return [seq[i:i + size] for i in range(0, n, size)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--cap", type=int, default=10 ** 12)
    ap.add_argument("--s2-chunk", type=int, default=4)
    a = ap.parse_args()

    triples = [parse_line(ln) for ln in open(a.batch) if ln.strip()]
    # drop size mismatches up front (never a polytope)
    triples = [t for t in triples if sum(t[0]) + sum(t[1]) == sum(t[2])]
    sys.stderr.write("stage0 triples: %d\n" % len(triples))

    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        parts = chunks(triples, a.workers * 4)
        res = list(ex.map(stage1_chunk, [(p, a.cap) for p in parts]))
    cs = [v for r in res for v in r]
    surv = [t for t, c in zip(triples, cs) if isinstance(c, int) and c >= 1]
    empt = sum(1 for c in cs if c == 0)
    other = len(cs) - empt - len(surv)
    sys.stderr.write("stage1: empty=%d survivors=%d nonint=%d\n"
                     % (empt, len(surv), other))

    parts = chunks(surv, max(1, len(surv) // a.s2_chunk + 1))
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        with open(a.out, "w") as f:
            done = 0
            for recs in ex.map(stage2_chunk, [(p, a.cap) for p in parts]):
                for rec in recs:
                    f.write(json.dumps(rec) + "\n")
                done += len(recs)
                f.flush()
                sys.stderr.write("stage2 %d/%d\r" % (done, len(surv)))
    sys.stderr.write("\nstage1_empty=%d stage2_screened=%d\n" % (empt, len(surv)))
    json.dump({"batch": a.batch, "stage0": len(triples), "stage1_empty": empt,
               "stage1_nonint": other, "stage2_screened": len(surv)},
              open(a.out + ".meta.json", "w"), indent=1)


if __name__ == "__main__":
    main()
