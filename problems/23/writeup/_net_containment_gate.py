"""Exact-test Codex block-197 (M)-replacement: on a connected-B cut with NO bracket hub, the P-CONTAINED
atom demand routes to off-path component spans (max-flow == total contained demand) => no contained overload.
Atom = geodesic Q of bad g!=f with Q subset P; load at position i = sum 1/|cyc(g)| over contained atoms
through x_i. Component C: span [lo,hi] (path positions with cut-edges into C), cap |C|. Flow: source->pos i
(cap load_i), pos i -> C iff lo<=i<=hi (inf), C->sink (cap |C|). Feasible iff maxflow==sum load.
Bracket hub = a path vertex that is shared endpoint of two straddling P-contained chords (one ending from
left, one starting to right). CLAIM: NO bracket hub => containment flow feasible. Battery: census N<=9 all
connB + N=26-66 nested/crossing/detour-ballast + N=39 FULL-DETOUR obstruction + glued + Mycielskians.
Report no-bracket cuts where containment INFEASIBLE (would refute). Exact Fraction max-flow."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _M_tailswitch_gate import build_pd, tri_free
from _codex190_ismax_check import add_cut_leaves
from _tail_positive_extra_counterexample import add_cut_path

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

def check_cut(n,adj,s,name,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        # contained chords (one geodesic subset P, contiguous) + load
        load=[F(0)]*L; chords=[]
        for g in M:
            if g==f: continue
            k=len(cyc[g]); gcontained=False; gint=None
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1:
                        gcontained=True; gint=(pp[0],pp[-1])
                        for i in range(pp[0],pp[-1]+1): load[i]+=F(1,k)
                        break
            if gcontained: chords.append(gint)
        if all(x==0 for x in load): continue
        # bracket hub?
        hub=False
        endsAt={}; startsAt={}
        for (a,b) in chords:
            endsAt.setdefault(b,0); startsAt.setdefault(a,0)
        for i in range(L):
            if any(b==i for (a,b) in chords) and any(a==i for (a,b) in chords): hub=True; break
        acc['rows']+=1
        if hub: acc['bracket']+=1;
        # off-path components
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        # containment max-flow
        posidx=[i for i in range(L) if load[i]>0]; nc=len(comps); npn=len(posidx)
        Nn=2+npn+nc; capm=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
        for j,i in enumerate(posidx): capm[0][2+j]=load[i]; total+=load[i]
        for jc,(lo,hi,c) in enumerate(comps): capm[2+npn+jc][1]=c
        BIG=total+1
        for j,i in enumerate(posidx):
            for jc,(lo,hi,c) in enumerate(comps):
                if lo<=i<=hi: capm[2+j][2+npn+jc]=BIG
        feas = maxflow(capm,0,1,Nn)==total
        if not hub:
            acc['nobracket']+=1
            if not feas:
                acc['nobracket_infeas']+=1
                if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,chords,[(lo,hi,c) for lo,hi,c in comps])
        else:
            if feas: acc['bracket_feas']+=1

if __name__=="__main__":
    acc={'rows':0,'bracket':0,'nobracket':0,'nobracket_infeas':0,'bracket_feas':0,'first':None}
    print("=== NET-CONTAINMENT flow gate (block 197): no-bracket => contained atoms route to components ===",flush=True)
    from _h import maxcut_all
    for nn in range(6,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        r0=acc['rows']; ni0=acc['nobracket_infeas']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for s in maxcut_all(n,adj):
                if Bconn(n,adj,list(s)): check_cut(n,adj,list(s),g6,acc)
        print(f"  census N={nn} ALL connB GLOBAL-MAX cuts: rows(+{acc['rows']-r0}) nobracket-INFEAS(+{acc['nobracket_infeas']-ni0})",flush=True)
    # full-detour obstruction + nested/crossing/chain + detour ballast + leaves
    layouts=[("nested",12,[(0,8),(2,6)],None),("crossing",12,[(0,6),(2,8)],None),
             ("chain",12,[(0,4),(4,8),(8,12)],None)]
    for name,pend,chords,_ in layouts:
        n,E=build_pd(pend,chords); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not tri_free(n,adj): continue
        r0=acc['rows']; ni0=acc['nobracket_infeas']
        check_cut(n,adj,[v%2 for v in range(n)],name,acc)
        print(f"  {name} N={n}: rows(+{acc['rows']-r0}) nobracket-INFEAS(+{acc['nobracket_infeas']-ni0})",flush=True)
    # full-detour obstruction (THE (M) killer)
    n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]
    n,E,side=add_cut_path(n,list(E),side,0,12,14)
    adj=[set() for _ in range(n)]
    for a,b in sorted(set(E)): adj[a].add(b); adj[b].add(a)
    r0=acc['rows']; ni0=acc['nobracket_infeas']
    check_cut(n,adj,side,"FULL-DETOUR-N39",acc)
    print(f"  FULL-DETOUR-N39: rows(+{acc['rows']-r0}) nobracket-INFEAS(+{acc['nobracket_infeas']-ni0})",flush=True)
    # detour ballast m=1..4 (two-sided partial)
    n0,E0=build_pd(12,[(0,8),(2,6)]); s0=[v%2 for v in range(n0)]
    for md in range(1,4):
        n,E,s=n0,list(E0),list(s0)
        for _ in range(md):
            n,E,s=add_cut_path(n,E,s,0,3,5); n,E,s=add_cut_path(n,E,s,8,5,5)
        adj=[set() for _ in range(n)]
        for a,b in sorted(set(E)): adj[a].add(b); adj[b].add(a)
        r0=acc['rows']; ni0=acc['nobracket_infeas']
        check_cut(n,adj,s,f"detour-m{md}",acc)
        print(f"  detour-m{md} N={n}: rows(+{acc['rows']-r0}) nobracket-INFEAS(+{acc['nobracket_infeas']-ni0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); r0=acc['rows']; ni0=acc['nobracket_infeas']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin: rows(+{acc['rows']-r0}) nobracket-INFEAS(+{acc['nobracket_infeas']-ni0})",flush=True)
    print(f"\n  TOTAL contained-rows={acc['rows']} bracket={acc['bracket']} no-bracket={acc['nobracket']}",flush=True)
    print(f"  NO-BRACKET containment INFEASIBLE = {acc['nobracket_infeas']} (claim: 0)",flush=True)
    if acc['first']: print(f"  first no-bracket infeasible: {acc['first']}",flush=True)
    print(f"  === {'REFUTED: no-bracket containment can be infeasible' if acc['nobracket_infeas'] else 'block-197 HOLDS: no-bracket => P-contained atoms route to components (no contained overload) -- robust (M)-replacement'} ===",flush=True)
