#!/usr/bin/env python3
"""Exhaustive: pipe all triangle-free connected graphs from nauty geng, check each for
TIGHT (Gamma=N^2) connected-B max-cut with m>=2 and NO safe peel. This is the definitive
small-N obstruction hunt covering necklaces and everything else.

Usage: geng -tc N | python adv_geng_tight.py N
Reads graph6 lines on stdin.
"""
import sys
sys.path.insert(0,'/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance

def g6_decode(line):
    line=line.strip()
    if not line: return None
    data=[ord(c)-63 for c in line]
    n=data[0]; bits=[]
    for x in data[1:]:
        for k in range(5,-1,-1):
            bits.append((x>>k)&1)
    adj=[set() for _ in range(n)]
    idx=0
    for j in range(1,n):
        for i in range(j):
            if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
            idx+=1
    return n,adj

def main():
    obstr=0; near=0; tight=0; total=0
    near_examples=[]
    for line in sys.stdin:
        dec=g6_decode(line)
        if dec is None: continue
        n,adj=dec
        if n>26: continue
        total+=1
        r=check_instance(n,adj)
        if not (r.get("ok") and r.get("triangle_free") and r.get("B_connected")): continue
        g=r.get("gamma"); n2=r.get("n2")
        if g is None: continue
        if r.get("tight"): tight+=1
        if r.get("ge_n2") and r.get("m",0)>=2 and r.get("has_safe_peel") is False:
            obstr+=1
            print(f"*** OBSTRUCTION g6={line.strip()} N={n} m={r['m']} gamma={g} n2={n2} side={r['side']} | {r['detail']}")
        elif r.get("m",0)>=2 and r.get("tight") and r.get("has_safe_peel") is True:
            pass  # expected: tight with peel
        # track near-tight no-peel
        ratio=g/n2
        if r.get("m",0)>=2 and ratio>=0.95 and r.get("has_safe_peel") is False:
            near+=1
            if len(near_examples)<10:
                near_examples.append((line.strip(),n,r['m'],g,n2,ratio))
    print(f"SUMMARY N-bucket: total_checked={total} tight={tight} obstructions={obstr} near_nopeel={near}")
    for ex in near_examples:
        print(f"  near-nopeel g6={ex[0]} N={ex[1]} m={ex[2]} gamma={ex[3]} n2={ex[4]} ratio={ex[5]:.4f}")

if __name__=="__main__":
    main()
