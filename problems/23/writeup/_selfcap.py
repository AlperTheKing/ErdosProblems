"""Independent fast exact-test of Codex's CONSTANT-LOAD-SELFCAP (block 86): for a PROPER positive K/omega
   component C (carries bad edges, |C|<n) with T constant = lambda on C, claim lambda <= |C|.
   Rules out the dangerous zero-ground Q component (T==N, |C|<N) directly. No subgraph maxcut needed -> fast."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def check(n,E):
    adj,cuts=gmins(n,E)
    tested=0; bad=0; worst=None
    for s in cuts:
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,mu,cyc=st
        kc,_=kcomponents(n,cyc)
        for root,C in kc.items():
            if len(C)<2 or len(C)>=n: continue
            if not any(f[0] in C and f[1] in C for f in M): continue   # positive
            Tv={T[v] for v in C}
            if len(Tv)!=1: continue
            lam=next(iter(Tv)); tested+=1
            slack=len(C)-lam
            if worst is None or slack<worst: worst=slack
            if lam>len(C): bad+=1
    return tested,bad,worst

if __name__=="__main__":
    print("=== CONSTANT-LOAD-SELFCAP: lambda <= |C| (independent, exact) ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); t,b,w=check(cur[0],cur[1]); print(f"  {nm}: const-load comps={t} SELFCAP-BAD={b} min(|C|-lam)={w}",flush=True)
    cur=(7,Cn(7)); cur=mycielski(*cur); t,b,w=check(cur[0],cur[1]); print(f"  Myc(C7)=N15: comps={t} BAD={b} minslack={w}",flush=True)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); gt=0;gb=0;gw=None
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                t,b,w=check(n,E); gt+=t; gb+=b
                if w is not None and (gw is None or w<gw): gw=w
    print(f"  glued battery: const-load comps={gt} SELFCAP-BAD={gb} minslack={gw}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0;bad=0;ws=None
        for g6 in outg:
            n,E=dec(g6); t,b,w=check(n,E); tot+=t; bad+=b
            if w is not None and (ws is None or w<ws): ws=w
        print(f"  census N={nn}: const-load comps={tot} SELFCAP-BAD={bad} min(|C|-lam)={ws}",flush=True)
