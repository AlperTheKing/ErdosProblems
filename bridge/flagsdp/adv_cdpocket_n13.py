#!/usr/bin/env python3
"""Parallel driver: exhaustive N=13 (i)-CD-mode probe across shards."""
import sys
from multiprocessing import Pool
import adv_cdpocket as M

def run(args):
    res, mod, gate = args
    return M.scan(13, res, mod, gate)

if __name__=="__main__":
    MOD=int(sys.argv[1]) if len(sys.argv)>1 else 40
    gate=float(sys.argv[2]) if len(sys.argv)>2 else 0.60
    tasks=[(r,MOD,gate) for r in range(MOD)]
    tot=0; ci=0; bi=(-1.0,None); ba=(-1.0,None)
    with Pool(MOD) as p:
        for o in p.imap_unordered(run, tasks):
            tot+=o[0]; ci+=o[1]
            if o[2][0]>bi[0]: bi=o[2]
            if o[3][0]>ba[0]: ba=o[3]
    print(f"=== N=13 EXHAUSTIVE (i)-mode probe gate>={gate}: m>=2&ratio>=gate checked={tot} "
          f"#with(i)appearing-anywhere={ci}")
    print(f"  highest-ratio NO-SAFE-PEEL: {bi[0]:.4f} {bi[1]}")
    print(f"  highest-ratio EVERY-edge-fails-WITH-(i): {ba[0]:.4f} {ba[1]}")
