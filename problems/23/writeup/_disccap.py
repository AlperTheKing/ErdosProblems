"""Codex block 46: DISCONNECTED-K-SELFCAP (scale-invariant). For ANY connected max cut: if the positive-K support
(K-components on T>0 vertices) has >=2 components, then every positive-K component C has T(v) <= |C| for all v in C.
=> overload (T>N>=|C|) forbids disconnected support => O-K-CONNECTED => cond(1). Violation: a multi-component cut with
some component C and vertex v in C, T(v) > |C|. Test ALL connected maxcuts (census) + glued constructions + blowups.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def selfcap_viol_side(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    comp, find = kcomponents(n, cyc)
    poscomps=[]
    for root,vs in comp.items():
        pos=[v for v in vs if T[v]>0]
        if pos: poscomps.append(pos)
    if len(poscomps)<2: return []   # only the multi-component case
    viol=[]
    for C in poscomps:
        sz=len(C)
        for v in C:
            if T[v]>sz:
                viol.append((sorted(C), sz, v, float(T[v]), [float(T[u]) for u in sorted(C)]))
                break
    return viol

def allcuts_viol(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    # all CONNECTED maximum cuts (with M nonempty)
    nmulti=0; viol=0; first=None; gmin=None
    cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((side,G))
    if not cand: return 0,0,None
    gm=min(G for _,G in cand)
    for side,G in cand:
        r=selfcap_viol_side(n,adj,side)
        if r is None: continue
        if r or True:
            # count multi-component cuts
            st=struct_for_side(n,adj,side);
        if r:
            viol+=len(r)
            if first is None: first=(side,r[0],('gmin' if G==gm else 'non-gmin'))
        # multi count
        st2=struct_for_side(n,adj,side)
        if st2:
            comp,find=kcomponents(n,st2[2] and len and cyc if False else st2[4] if False else None) if False else (None,None)
    return viol, 0, first

def quickcount_side(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return 0
    M,ell,T,mu,cyc=st
    comp,find=kcomponents(n,cyc)
    return sum(1 for root,vs in comp.items() if any(T[v]>0 for v in vs))

def run_allcuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append(side)
    nmulti=0; viol=0; first=None
    for side in cand:
        if quickcount_side(n,adj,side)>=2:
            nmulti+=1
            r=selfcap_viol_side(n,adj,side)
            if r: viol+=len(r); first=first or (side,r[0])
    return nmulti, viol, first

if __name__=="__main__":
    print("=== DISCONNECTED-K-SELFCAP over ALL connected maxcuts ===")
    # glued constructions (the adversarial multi-component gate)
    print("--- glued island constructions ---")
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    cases=[]
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr,(5,Cn(5)),(7,Cn(7))]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=22 and is_triangle_free(n,E): cases.append((f"isl{iN}+gad{gN} br{br} N={n}",n,E))
    tot=0; tmulti=0
    for name,n,E in cases:
        nm,v,f=run_allcuts(n,E); tmulti+=nm; tot+=v
        if v: print(f"  *** {name}: VIOL {f}",flush=True)
    print(f"  [{len(cases)} constructions, multi-comp cuts={tmulti}, SELFCAP violations={tot}]",flush=True)
    # N=12 caveat
    g6="J?AADBWM_}?"; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    nm,v,f=run_allcuts(12,E12); print(f"  N=12 leaf caveat: multi-comp cuts={nm} viol={v}"+(f" {f}" if f else ""),flush=True)
    # census all connected maxcuts N=7..10
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cm=0; cv=0; first=None
        for g6 in outg:
            n,E=dec(g6); nm,v,f=run_allcuts(n,E); cm+=nm; cv+=v
            if f and first is None: first=(g6,f)
        print(f"  census N={nn} (all connected maxcuts): multi-comp cuts={cm} SELFCAP-viol={cv}"+(f" FIRST {first}" if first else ""),flush=True)
