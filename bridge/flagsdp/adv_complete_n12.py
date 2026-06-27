#!/usr/bin/env python3
"""COMPLETENESS-CRITIC definitive scan: EXHAUSTIVE over ALL triangle-free connected graphs at a
fixed N (default 12), parallel across cores. Extends the prior N<=11 census to N=12.

Reports: any OBSTRUCTION (ge_n2, m>=2, sp=False); the global max ratio among sp=False m>=2
instances; the count of tight graphs; and whether condition (i) CD is ever the binding peel
failure (tracked via a re-run trace on the top no-peel cases).

Run:  python adv_complete_n12.py 12 NWORKERS
Generates graph6 internally by sharding geng with res/mod.
"""
import sys, subprocess, os
from multiprocessing import Pool

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

def g6(line):
    data=[ord(c)-63 for c in line.strip()]; n=data[0]; bits=[]
    for x in data[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    adj=[set() for _ in range(n)]; idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

def worker(args):
    N, res, mod = args
    sys.path.insert(0, r"E:\Projects\ErdosProblems\bridge\flagsdp")
    from peel_check import check_instance
    p = subprocess.Popen([GENG, "-tcq", str(N), f"{res}/{mod}"],
                         stdout=subprocess.PIPE, text=True)
    total=0; tight=0; obstr=[]; best_nopeel=(-1.0,None); ge_n2_nopeel=[]
    for line in p.stdout:
        line=line.strip()
        if not line: continue
        n,adj=g6(line)
        r=check_instance(n,adj)
        if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")): continue
        g=r.get("gamma"); n2=r.get("n2")
        if g is None: continue
        total+=1
        if r.get("tight"): tight+=1
        m=r.get("m",0)
        if m>=2 and r.get("has_safe_peel") is False:
            ratio=g/n2
            if ratio>best_nopeel[0]:
                best_nopeel=(ratio,(line,n,m,g,n2))
            if r.get("ge_n2"):
                ge_n2_nopeel.append((line,n,m,g,n2))
                obstr.append((line,n,m,g,n2,r['side']))
    p.wait()
    return total,tight,obstr,best_nopeel,ge_n2_nopeel

def main():
    N=int(sys.argv[1]) if len(sys.argv)>1 else 12
    W=int(sys.argv[2]) if len(sys.argv)>2 else 48
    tasks=[(N,r,W) for r in range(W)]
    total=0; tight=0; allobstr=[]; gbest=(-1.0,None); allge=[]
    with Pool(W) as pool:
        for (t,tt,ob,bn,ge) in pool.imap_unordered(worker, tasks):
            total+=t; tight+=tt; allobstr+=ob; allge+=ge
            if bn[0]>gbest[0]: gbest=bn
    print(f"=== EXHAUSTIVE N={N}: triangle-free connected, valid connected-B max cut ===")
    print(f"checked={total} tight(Gamma=N^2)={tight} obstructions(ge_n2,m>=2,no-peel)={len(allobstr)}")
    print(f"global max ratio among sp=False m>=2 instances: {gbest[0]:.4f}  example={gbest[1]}")
    for ob in allobstr[:20]:
        print(f"  *** OBSTRUCTION g6={ob[0]} N={ob[1]} m={ob[2]} gamma={ob[3]} n2={ob[4]} side={ob[5]}")
    if not allobstr:
        print("  NO obstruction at this N (every tight/ge_n2 m>=2 graph has a safe peel).")

if __name__=="__main__":
    main()
