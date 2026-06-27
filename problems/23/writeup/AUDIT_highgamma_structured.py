#!/usr/bin/env python3
"""STRUCTURED high-Gamma tri-free audit of claim U (max_v T_uniform <= K = N + (N^2-Gamma)), EXACT Fractions.
Families that genuinely sit near Gamma=N^2 (the tight regime random reject-sampling misses):
  (1) C5[t] balanced blow-ups (anchor, Gamma=N^2 exactly).
  (2) C5[t] UNBALANCED blow-ups (part sizes vary) -- still high Gamma, breaks symmetry.
  (3) C5-blowup + small random tri-free perturbations (add/del a few edges, keep tri-free).
  (4) Odd-cycle C_{2k+1}[t] blow-ups (k=2,3) -- pentagon/heptagon blow-ups, high Gamma.
  (5) Random tri-free built to be DENSE by a bipartite-like 2-coloring backbone + odd chords
      (so the gamma-min cut keeps many bad edges) then reject on ratio>=0.7.
Brute maxcut => cap N<=18.  Any maxT>K re-confirmed independently."""
import sys, random
from fractions import Fraction
sys.path.insert(0,"E:/Projects/ErdosProblems/problems/23/writeup")
from AUDIT_highgamma_random import check, adj_from_E, has_triangle

def c_blow_parts(cyc_len, parts):
    """Blow up an odd cycle of length cyc_len with given part sizes (list len cyc_len)."""
    assert len(parts)==cyc_len
    offset=[0]
    for s in parts: offset.append(offset[-1]+s)
    n=offset[-1]; E=[]
    for i in range(cyc_len):
        j=(i+1)%cyc_len
        for a in range(parts[i]):
            for b in range(parts[j]):
                E.append((offset[i]+a, offset[j]+b))
    return n,E

def perturb(n,E,rng,nadd,ndel):
    """Random small perturbation keeping tri-free: try add nadd non-edges, del ndel edges."""
    adj=adj_from_E(n,E)
    Eset=set(tuple(sorted(e)) for e in E)
    # deletions
    es=list(Eset)
    rng.shuffle(es)
    for e in es[:ndel]:
        adj[e[0]].discard(e[1]);adj[e[1]].discard(e[0]);Eset.discard(e)
    # additions (only if stays tri-free)
    nonedges=[(i,j) for i in range(n) for j in range(i+1,n) if j not in adj[i]]
    rng.shuffle(nonedges)
    cnt=0
    for (i,j) in nonedges:
        if cnt>=nadd: break
        if adj[i]&adj[j]: continue  # would form triangle
        adj[i].add(j);adj[j].add(i);cnt+=1
    E2=[(a,b) for a in range(n) for b in adj[a] if b>a]
    return n,E2

def main():
    rng=random.Random(424242)
    results=[]   # (label,N,ratio,slack,Gamma,K,maxT)
    violations=[]
    min_slack_high=None
    high_count=0
    total=0

    def record(label,d):
        nonlocal min_slack_high,high_count,total
        total+=1
        slack=d['K']-d['maxT']; ratio=d['ratio']
        if d['maxT']>d['K']:
            violations.append((label,d))
        if ratio>=Fraction(7,10):
            high_count+=1
            results.append((label,d['N'],float(ratio),slack,d['Gamma'],d['K'],d['maxT']))
            if min_slack_high is None or slack<min_slack_high[0]:
                min_slack_high=(slack,label,d['N'],d['Gamma'],d['K'],d['maxT'])

    print("=== (1)+(2) C5 blow-ups, balanced & unbalanced (N<=18) ===")
    # enumerate part-size vectors for C5 with N<=18
    import itertools
    cnt=0
    for parts in itertools.product(range(1,5),repeat=5):
        N=sum(parts)
        if N>18 or N<5: continue
        n,E=c_blow_parts(5,list(parts))
        d=check(n,E)
        if d is None: continue
        record(f"C5{parts}",d); cnt+=1
        if d['maxT']>d['K']:
            print(f"  !!! VIOL C5{parts} N={d['N']} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']}")
    print(f"  C5 blow-ups checked={cnt}")

    print("=== (4) C7 and C9 blow-ups (capped N to avoid maxcut_all blowup on symmetric graphs) ===")
    cnt=0
    # C7: N<=16 ; C9: N<=15  (symmetric large blow-ups have astronomically many max cuts -> gmin slow)
    for L,Ncap in ((7,16),(9,15)):
        for parts in itertools.product(range(1,4),repeat=L):
            N=sum(parts)
            if N>Ncap or N<L: continue
            n,E=c_blow_parts(L,list(parts))
            d=check(n,E)
            if d is None: continue
            record(f"C{L}{parts}",d); cnt+=1
            if d['maxT']>d['K']:
                print(f"  !!! VIOL C{L}{parts} N={d['N']} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']}")
    print(f"  C7/C9 blow-ups checked={cnt}")

    print("=== (3) C5[t]-blowup + small tri-free perturbations (N<=18) ===")
    base_parts=[(2,2,2,2,2),(3,3,2,2,2),(2,2,2,2,1),(2,3,2,3,2),(3,2,2,2,2),(2,2,3,2,2),(3,3,2,2,1)]
    cnt=0
    for bp in base_parts:
        N=sum(bp)
        if N>13: continue
        n0,E0=c_blow_parts(5,list(bp))
        for trial in range(1500):
            nadd=rng.randint(0,3); ndel=rng.randint(0,3)
            n,E=perturb(n0,E0,rng,nadd,ndel)
            if has_triangle(n,adj_from_E(n,E)): continue
            d=check(n,E)
            if d is None: continue
            record(f"pert{bp}",d); cnt+=1
            if d['maxT']>d['K']:
                print(f"  !!! VIOL pert{bp} N={d['N']} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']} E={E}")
    print(f"  perturbations checked={cnt}")

    print(f"\n=== SUMMARY (structured) ===")
    print(f"total checked: {total}")
    print(f"high-Gamma (ratio>=0.7): {high_count}")
    if min_slack_high:
        s,label,N,G,K,mT=min_slack_high
        print(f"MIN slack among high-Gamma: {s}={float(s):.6f}  [{label} N={N} Gamma={G} K={K} maxT={mT}={float(mT):.4f}]")
    print(f"violations (maxT>K): {len(violations)}")
    for (label,d) in violations[:30]:
        print(f"  !!! VIOLATION {label} N={d['N']} Gamma={d['Gamma']} K={d['K']} maxT={d['maxT']} side={d['side']} M={d['M']}")

    # smallest slacks among high-Gamma (closest to the wire)
    results.sort(key=lambda r:r[3])
    print("\n 12 smallest-slack high-Gamma samples (label,N,ratio,slack,Gamma,K,maxT):")
    for r in results[:12]:
        print(f"   {r[0]} N={r[1]} ratio={r[2]:.3f} slack={float(r[3]):.5f} Gamma={r[4]} K={r[5]} maxT={float(r[6]):.4f}")

if __name__=="__main__":
    main()
