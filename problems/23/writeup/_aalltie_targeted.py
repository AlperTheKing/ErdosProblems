"""Targeted A-alltie test on graphs where saturation T=N is GENERIC: disjoint unions of odd cycles
   bridged by cut edges (which become zero-mu corridors), plus Mycielskian/blowup families.
ALSO: the gamma-minimality question. For each such graph, test A-alltie on:
   (a) the loads() gamma-min cut, and
   (b) ALL connected max cuts (to see if a non-gamma-min cut can violate A-alltie).
If A-alltie can FAIL on a non-gamma-min connected max cut while holding on gamma-min, then
gamma-minimality is ESSENTIAL (proof must use Gamma-stability).
Exact Fraction."""
import random
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def union_odd_cycles_bridged(cycle_lens, nbridge, seed):
    """disjoint odd cycles, then add nbridge random edges between distinct cycles (kept triangle-free)."""
    rnd=random.Random(seed)
    E=[]; base=0; blocks=[]
    for L in cycle_lens:
        vs=list(range(base, base+L))
        for i in range(L): E.append((vs[i], vs[(i+1)%L]))
        blocks.append(vs); base+=L
    N=base
    adj=[set() for _ in range(N)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    added=0; tries=0
    while added<nbridge and tries<2000:
        tries+=1
        bi,bj=rnd.sample(range(len(blocks)),2)
        a=rnd.choice(blocks[bi]); b=rnd.choice(blocks[bj])
        if b in adj[a]: continue
        if adj[a]&adj[b]: continue  # triangle-free
        adj[a].add(b); adj[b].add(a); E.append((a,b)); added+=1
    return N,E

def Acheck_side(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    cases=0; viol=0; wit=None
    for e,val in mu.items():
        if val!=0: continue
        u,v=e
        for (a,b) in ((u,v),(v,u)):
            if T[a]==N:
                cases+=1
                if T[b]!=0:
                    viol+=1
                    if wit is None: wit=(a,b,str(T[a]),str(T[b]))
    return cases,viol,wit

def all_conn_maxcuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); out=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: out.append((side,G))
    return adj,out

if __name__=="__main__":
    print("=== Targeted A-alltie on odd-cycle gluings: gamma-min vs ALL connected max cuts ===")
    configs=[]
    # two/three C5 bridged
    for nb in [1,2,3]:
        for s in range(40): configs.append((("2xC5",nb,s),[5,5],nb,s))
    for nb in [1,2,3]:
        for s in range(40): configs.append((("3xC5",nb,s),[5,5,5],nb,s))
    for nb in [1,2]:
        for s in range(30): configs.append((("C5+C7",nb,s),[5,7],nb,s))
    for nb in [1,2]:
        for s in range(30): configs.append((("C7+C7",nb,s),[7,7],nb,s))
    gmin_cases=0; gmin_viol=0; nonmin_cases=0; nonmin_viol=0
    gmin_wit=None; nonmin_wit=None
    for tag,lens,nb,s in configs:
        N,E=union_odd_cycles_bridged(lens,nb,s*13+1)
        if N>18: continue
        adj,cand=all_conn_maxcuts(N,E)
        if not cand: continue
        gm=min(G for _,G in cand)
        for side,G in cand:
            r=Acheck_side(N,adj,side)
            if r is None: continue
            c,v,w=r
            if G==gm:
                gmin_cases+=c; gmin_viol+=v
                if v>0 and gmin_wit is None: gmin_wit=(tag,w)
            else:
                nonmin_cases+=c; nonmin_viol+=v
                if v>0 and nonmin_wit is None: nonmin_wit=(tag,w,float(G),float(gm))
    print(f"  GAMMA-MIN cuts: A-alltie cases={gmin_cases} viol={gmin_viol} {gmin_wit or ''}")
    print(f"  NON-MIN connected max cuts: A-alltie cases={nonmin_cases} viol={nonmin_viol} {nonmin_wit or ''}")
    print("  => if NON-MIN viol>0 while GAMMA-MIN viol=0, gamma-minimality is ESSENTIAL.")
