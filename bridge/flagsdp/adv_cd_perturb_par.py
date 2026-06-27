#!/usr/bin/env python3
"""Parallel C5[q] perturbation hunt (incremental, prints per shard)."""
import sys
from multiprocessing import Pool
import adv_cd_perturb as P

def run(args):
    q, iters, seed = args
    best,obstr=P.edit_and_test(P.C5q,(q,),4,iters,seed)
    return best,obstr

if __name__=="__main__":
    q=int(sys.argv[1]); per=int(sys.argv[2]); W=int(sys.argv[3])
    tasks=[(q,per,s) for s in range(W)]
    gbest=(-1.0,None); allob=[]
    with Pool(W) as pool:
        for best,obstr in pool.imap_unordered(run, tasks):
            if best[0]>gbest[0]: gbest=best
            allob+=obstr
    print(f"=== C5[{q}] perturbation (N={5*q}) {per*W} samples total ===")
    print(f"  best no-safe-peel ratio={gbest[0]:.4f} info={gbest[1]}")
    print(f"  obstructions(ge_n2,no-peel)={len(allob)}")
    for o in allob[:5]: print("   OBSTRUCTION", o)
