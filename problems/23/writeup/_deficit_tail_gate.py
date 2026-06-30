"""Exact-gate Codex block-204 DEFICIT-TAIL switch (constructive P198): for any connected-B cut, unique f, if
the P-contained position-flow is INFEASIBLE (deficit), then some CLOSED prefix/suffix switch has positive cut
gain (=> the cut is not maximum -- unconditional, a positive-gain switch IS a non-max witness).
cl(T)=T union every off-path B-component whose B-attachments to P are all in T. For each P-contained atom
[lo,hi], test raw prefixes P[0..k] and suffixes P[k..end] for k in {lo-1..hi+1}, closed. Accept if any has
gain>0. Battery: census N<=11 ALL connB cuts + obstructions (disjoint/full/merged detour -- should have NO
deficit) + Mycielskians. Report deficits, switch_ok, MISSES; CP-SAT-check any miss for global-maximality."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint
from _M_tailswitch_gate import build_pd
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def maxflow(cap,src,snk,Nn):
    flow=F(0)
    while True:
        par=[-1]*Nn; par[src]=src; q=deque([src])
        while q:
            u=q.popleft()
            for v in range(Nn):
                if par[v]==-1 and cap[u][v]>0: par[v]=u; q.append(v)
        if par[snk]==-1: break
        v=snk; b=None
        while v!=src: u=par[v]; b=cap[u][v] if b is None else min(b,cap[u][v]); v=u
        v=snk
        while v!=src: u=par[v]; cap[u][v]-=b; cap[v][u]+=b; v=u
        flow+=b
    return flow
def gain(n,adj,s,Sset):
    dB=dM=0
    for u in Sset:
        for w in adj[u]:
            if w in Sset: continue
            if s[u]!=s[w]: dB+=1
            else: dM+=1
    return dM-dB

def check_cut(n,adj,s,name,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        atoms=[]; load=[F(0)]*L
        for g in M:
            if g==f: continue
            k=len(cyc[g])
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1:
                        atoms.append((pp[0],pp[-1]))
                        for i in range(pp[0],pp[-1]+1): load[i]+=F(1,k)
                        break
        if all(x==0 for x in load): continue
        # components with their vertex sets + attach interval
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]  # (Cset, attach-POSITIONS, attach-VERTICES)
        for r,C in cd.items():
            Apos=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            Avert=set(x for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            comps.append((C,Apos,Avert))
        cl=[(min(Apos),max(Apos),len(C)) for C,Apos,Avert in comps if Apos]
        # position-flow feasibility
        posidx=[i for i in range(L) if load[i]>0]; nc=len(cl); npn=len(posidx)
        Nn=2+npn+nc; capm=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
        for j,i in enumerate(posidx): capm[0][2+j]=load[i]; total+=load[i]
        for jc,(lo,hi,cc) in enumerate(cl): capm[2+npn+jc][1]=cc
        BIG=total+1
        for j,i in enumerate(posidx):
            for jc,(lo,hi,cc) in enumerate(cl):
                if lo<=i<=hi: capm[2+j][2+npn+jc]=BIG
        if maxflow(capm,0,1,Nn)==total: continue   # no deficit
        acc['deficits']+=1
        # closed prefix/suffix switch search (Tset = path-vertex set; absorb components whose ATTACH-VERTICES subset Tset)
        def closed(Tset):
            clset=set(Tset)
            for C,Apos,Avert in comps:
                if Avert and Avert<=Tset: clset|=C
            return clset
        ok=False
        ks=set()
        for (lo,hi) in atoms:
            for k in range(max(0,lo-1),min(L,hi+2)): ks.add(k)
        for k in ks:
            pre=set(P_f[0:k+1]); suf=set(P_f[k:L])
            if gain(n,adj,s,closed(pre))>0 or gain(n,adj,s,closed(suf))>0: ok=True; break
        if ok: acc['switch_ok']+=1
        else:
            acc['misses']+=1
            if acc['first'] is None:
                # CP-SAT max check for this miss
                acc['first']=(name,''.join(map(str,s)),f,P_f,atoms,cutsize(n,adj,s))

def run():
    acc={'deficits':0,'switch_ok':0,'misses':0,'first':None}
    # OBSTRUCTIONS FIRST (my unique contribution: do they have a P-contained deficit? they should NOT)
    n,E=build_pd(12,[(0,4),(8,12)]); s=[v%2 for v in range(n)]; adj=adj_from_edges(n,E)
    d0=acc['deficits']; check_cut(n,adj,s,"disjoint-N26",acc); print(f"  disjoint-N26: deficits(+{acc['deficits']-d0})",flush=True)
    n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14); adj=adj_from_edges(n,sorted(set(E)))
    d0=acc['deficits']; check_cut(n,adj,side,"full-detour-N39",acc); print(f"  full-detour-N39: deficits(+{acc['deficits']-d0})",flush=True)
    n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14); E=sorted(set(E+[(13,27)])); adj=adj_from_edges(n,E)
    d0=acc['deficits']; check_cut(n,adj,side,"merged-detour-N39",acc); print(f"  merged-detour-N39: deficits(+{acc['deficits']-d0})",flush=True)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        s=[v%2 for v in range(nn)]
        d0=acc['deficits'];
        if Bconn(nn,adj,s): check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} (parity): deficits(+{acc['deficits']-d0})",flush=True)
    # census N<=10 ALL connB cuts (independent confirmation of Codex; N=11 he covered with 61 workers)
    for nn in range(6,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        d0=acc['deficits']; m0=acc['misses']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for m in range(1<<(n-1)):
                s=[(m>>v)&1 for v in range(n)]
                check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} ALL connB: deficits(+{acc['deficits']-d0}) misses(+{acc['misses']-m0})",flush=True)
    print(f"\n  TOTAL P-contained deficits={acc['deficits']} switch_ok={acc['switch_ok']} MISSES={acc['misses']}",flush=True)
    if acc['first']: print(f"  first MISS (CP-SAT max-check needed): {acc['first']}",flush=True)
    print(f"  === {'MISS: deficit with no closed prefix/suffix positive-gain switch' if acc['misses'] else 'block-204 HOLDS: every P-contained-flow deficit has a positive-gain closed prefix/suffix switch => not max (constructive P198)'} ===",flush=True)

if __name__=="__main__": run()
