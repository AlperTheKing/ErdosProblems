#!/usr/bin/env python3
"""fam1 beam climb: expand carriers by one box move, keep the ones that raise
Sum h* at small h*_1.  Screening = lpfree_screen.py only (LP-free, exact)."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpfree_screen as L
from fam1_perturb import box_moves, canon


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--beam", type=int, default=300)
    ap.add_argument("--maxlen-nu", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=400)
    ap.add_argument("--h1max", type=int, default=0,
                    help="keep carriers with h*_1 <= this for the next round")
    ap.add_argument("--seen", default=None, help="jsonl files already screened")
    args = ap.parse_args()

    seen = set()
    if args.seen:
        for p in args.seen.split(","):
            if not p:
                continue
            for line in open(p):
                r = json.loads(line)
                seen.add(canon((tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))))

    seeds = [(tuple(t[0]), tuple(t[1]), tuple(t[2]))
             for t in json.load(open(args.seeds))]
    fh = open(args.out, "w")
    t0 = time.time()
    frontier = seeds
    best = (0, None)
    nneg = 0
    ntot = 0
    for rnd in range(args.rounds):
        cand = []
        for t in frontier:
            for u in box_moves(t, maxlen_nu=args.maxlen_nu):
                c = canon(u)
                if c not in seen:
                    seen.add(c); cand.append(u)
        sys.stderr.write("round %d: %d new candidates\n" % (rnd, len(cand)))
        sys.stderr.flush()
        keep = []
        for i in range(0, len(cand), args.chunk):
            recs = L.screen_triples(cand[i:i + args.chunk])
            for r in recs:
                ntot += 1
                fh.write(json.dumps(r) + "\n")
                if r.get("neg"):
                    nneg += 1
                if r.get("status") != "OK" or r.get("d") is None or r["d"] < 3:
                    continue
                if r["hstar_1"] is not None and r["hstar_1"] <= args.h1max:
                    keep.append((r["hstar_sum"], r["d"],
                                 (tuple(r["lam"]), tuple(r["mu"]), tuple(r["nu"]))))
                    if r["hstar_sum"] > best[0]:
                        best = (r["hstar_sum"], (r["lam"], r["mu"], r["nu"]),
                                r["hstar"], r["d"])
            fh.flush()
            sys.stderr.write("  %d/%d %.0fs kept=%d best=%s neg=%d\n"
                             % (min(i + args.chunk, len(cand)), len(cand),
                                time.time() - t0, len(keep), best[0], nneg))
            sys.stderr.flush()
        keep.sort(key=lambda z: (-z[0], -z[1]))
        frontier = [z[2] for z in keep[:args.beam]]
        sys.stderr.write("round %d done: frontier %d, best %s\n"
                         % (rnd, len(frontier), json.dumps(best[1:])))
        if not frontier:
            break
    sys.stderr.write("BEAM DONE tot=%d neg=%d best=%s %.0fs\n"
                     % (ntot, nneg, json.dumps(list(best[1:])), time.time() - t0))
    fh.close()


if __name__ == "__main__":
    main()
