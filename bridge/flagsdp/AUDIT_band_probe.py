#!/usr/bin/env python3
"""Focus the adversarial d_mono<=U_8 probe on the BCL MEDIUM BAND d_edge in [0.2486, 0.3197].
For a weighted blow-up of template T with weights alpha: d_edge = 2*sum_{u<w edge} a_u a_w (edge density of the
step graphon, in the SAME 2x edge-units used by d_mono/U_8 helpers -> here we report the standard density
sum_{u<w} a_u a_w over normalized alpha, i.e. t(K2)/1). We hunt, within the band, for the SMALLEST U_8 - d_mono.
Templates: C7 (in band at uniform), Petersen (0.30), Heawood/Mobius-Kantor-like cycles, plus weighted sweeps that
push d_edge across the band. Report worst gap among band-resident step-graphons.
"""
import random
from fractions import Fraction as F
from u8_max_check import U8

def cyc(m):
    A=[0]*m
    for i in range(m): A[i]|=1<<((i+1)%m); A[i]|=1<<((i-1)%m)
    return A
def petersen():
    A=[0]*10
    def e(u,v): A[u]|=1<<v; A[v]|=1<<u
    for i in range(5): e(i,(i+1)%5); e(5+i,5+((i+2)%5)); e(i,5+i)
    return A
def edges_of(m,T): return [(u,w) for u in range(m) for w in range(u+1,m) if (T[u]>>w)&1]

def dedge(m,T,a):
    return sum(a[u]*a[w] for (u,w) in edges_of(m,T))   # standard edge density of step graphon
def dmono_w(m,T,a):
    E=edges_of(m,T); tK2=sum(a[u]*a[w] for (u,w) in E); best=0.0
    for mask in range(1<<(m-1)):
        cut=0.0
        for (u,w) in E:
            if ((mask>>u)&1)!=((mask>>w)&1): cut+=a[u]*a[w]
        if cut>best: best=cut
    return 2.0*(tK2-best)

LO,HI=0.2486,0.3197
def main():
    random.seed(11)
    templates=[("C7",7,cyc(7)),("C9",9,cyc(9)),("C11",11,cyc(11)),("Petersen",10,petersen())]
    worst=1e9; worst_info=None; nband=0; nviol=0
    samples=[]
    for (nm,m,T) in templates:
        # uniform
        samples.append((nm,m,T,[1.0/m]*m))
        # weighted sweeps
        for _ in range(150):
            a=[random.uniform(0.3,1.7) for _ in range(m)]; s=sum(a); a=[x/s for x in a]
            samples.append((nm+"w",m,T,a))
    for (nm,m,T,a) in samples:
        de=dedge(m,T,a)
        if not (LO<=de<=HI): continue
        nband+=1
        dm=dmono_w(m,T,a)
        u8=float(U8(m,T,[F(int(round(x*10**6)),10**6) for x in a]))
        gap=u8-dm
        if gap<-1e-9:
            nviol+=1
            print(f"VIOLATION {nm} d_edge={de:.4f} d_mono={dm:.6f} U_8={u8:.6f} gap={gap:+.3e} alpha={['%.3f'%x for x in a]}",flush=True)
        if gap<worst: worst=gap; worst_info=(nm,de,dm,u8,gap,a)
    print(f"\n=== BAND probe d_edge in [{LO},{HI}] ===",flush=True)
    print(f"  band-resident step-graphons tested: {nband}",flush=True)
    if worst_info:
        nm,de,dm,u8,gap,a=worst_info
        print(f"  WORST gap U_8 - d_mono = {gap:+.6e}  at {nm} d_edge={de:.4f} (d_mono={dm:.6f}, U_8={u8:.6f})",flush=True)
    print(f"  violations: {nviol}; d_mono<=U_8 holds in band ? {worst>=-1e-9}",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
