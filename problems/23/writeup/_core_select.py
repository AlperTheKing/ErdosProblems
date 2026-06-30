"""Gate Codex 381 (A) core-containment + (B) MINIMAL-CORE ROTATION on all Tail<0 witnesses.
   For each Tail<0 row, enumerate parity-interval switches W(J=[a,b],tau); keep neutral (mu=0) connected
   with DeltaGamma<0.  Select the MINIMAL core: J inclusion-minimal, then |J| minimal, then DeltaGamma minimal.
   Check the relaxed rotation decomposition on the minimal core:
     (1) BoundaryExchange<=0; (2) no retained bad edge lengthens; (3) #added==#removed & sum_add ell^2<=sum_rem;
     (4) strictness from Boundary<0 OR a retained shortening.
   Report minimal-core J + decomposition for each witness; any failure.  ALL exact.
"""
import subprocess, itertools
import _crux_extract as cx
from _crux_extract import components_off_path
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def parity_switches_J(n, adj, side, P):
    """yield (a, b, frozenset(W)) for each interval [a,b] + straddler completion."""
    L=len(P); Pset=set(P)
    comps=components_off_path(n,adj,side,Pset)
    info=[]
    for C in comps:
        attach=set()
        for v in C:
            for w in adj[v]:
                if w in Pset and side[w]!=side[v]: attach.add(P.index(w))
        col={}; start=next(iter(C)); col[start]=0; st=[start]
        while st:
            u=st.pop()
            for w in adj[u]:
                if w in C and side[w]!=side[u] and w not in col: col[w]=col[u]^1; st.append(w)
        cls0={v for v in C if col.get(v,0)==0}; cls1={v for v in C if col.get(v,0)==1}
        info.append((C,attach,cls0,cls1))
    for a in range(L):
        for b in range(a,L):
            I=set(range(a,b+1)); base={P[i] for i in I}; forced=set(base); straddle=[]
            for (C,attach,cls0,cls1) in info:
                if not attach: continue
                if attach<=I: forced|=C
                elif attach&I: straddle.append((cls0,cls1))
            choices=[()] if not straddle else itertools.product(*[(0,1)]*len(straddle))
            for ch in choices:
                W=set(forced)
                for sidx,pick in enumerate(ch): W|=(straddle[sidx][0] if pick==0 else straddle[sidx][1])
                yield a,b,frozenset(W)

def ell_map(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    return {frozenset(e):st[1][e] for e in st[0]}

def decomp(n,adj,side,em0,W):
    s2=flip(side,W)
    if not Bconn(n,adj,s2): return None
    em1=ell_map(n,adj,s2)
    if em1 is None: return None
    k0=set(em0); k1=set(em1); added=k1-k0; removed=k0-k1; retained=k0&k1
    boundary=sum(em1[e]**2 for e in added)-sum(em0[g]**2 for g in removed)
    ret=sum(em1[h]**2-em0[h]**2 for h in retained)
    dG=boundary+ret
    no_len=all(em1[h]<=em0[h] for h in retained)
    strict_ret=any(em1[h]<em0[h] for h in retained)
    pair=(len(added)==len(removed)) and (sum(em1[e]**2 for e in added)<=sum(em0[g]**2 for g in removed))
    relaxed=(dG<0) and (boundary<=0) and no_len and pair and (boundary<0 or strict_ret)
    return dG,boundary,ret,len(added),len(removed),relaxed,no_len,strict_ret,pair

def process_row(n,adj,side,M,ell,T,cyc,f,P,acc):
    em0=ell_map(n,adj,side)
    negs=[]   # (a,b,W,dG,decomp)
    seen=set()
    for a,b,W in parity_switches_J(n,adj,side,P):
        if not W or W in seen: continue
        seen.add(W)
        dB,dM=deltas(n,adj,side,W)
        if dB!=dM: continue
        d=decomp(n,adj,side,em0,W)
        if d is None or d[0]>=0: continue
        negs.append((a,b,W,d))
    acc['rows']+=1
    if not negs:
        acc['no_neg']+=1; return
    # minimal core: inclusion-minimal interval [a,b], then length, then dG
    def is_subinterval(x,y): return y[0]<=x[0] and x[1]<=y[1]
    minimal=[]
    for cand in negs:
        ab=(cand[0],cand[1])
        if not any((o is not cand) and is_subinterval((o[0],o[1]),ab) and (o[0],o[1])!=ab for o in negs):
            minimal.append(cand)
    minimal.sort(key=lambda c:(c[1]-c[0], c[3][0]))
    mc=minimal[0]
    if mc[3][5]: acc['relaxed_ok']+=1
    else:
        acc['relaxed_fail']+=1
        if acc['ex'] is None: acc['ex']=(P,mc[0],mc[1],mc[3])
    if len(acc['samples'])<10:
        acc['samples'].append((tuple(P),'J=[%d,%d]'%(mc[0],mc[1]),sorted(mc[2]),'dG=%s bd=%s ret=%s'%(mc[3][0],mc[3][1],mc[3][2])))

def main():
    acc=dict(rows=0,no_neg=0,relaxed_ok=0,relaxed_fail=0,ex=None,samples=[])
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            mc,cuts=cx.all_max_cuts(n,adj,E)
            structs=[]
            for side in cuts:
                if not Bconn(n,adj,side): continue
                st=struct_for_side(n,adj,side)
                if st is None: continue
                structs.append((side,st,sum(st[2])))
            if not structs: continue
            gmin=min(g for (_,_,g) in structs)
            for (side,st,G) in structs:
                if G<=gmin: continue
                M,ell,T,cyc=st[0],st[1],st[2],st[4]
                if not M: continue
                for f in M:
                    if ell[f]%2==0: continue
                    for P in cyc[f]:
                        if len(P)!=ell[f]: continue
                        _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                        if min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))>=0: continue
                        process_row(n,adj,side,M,ell,T,cyc,f,P,acc)
    print("Tail<0 rows:",acc['rows']," (no negative switch:",acc['no_neg'],")")
    print("minimal-core relaxed-invariant OK:",acc['relaxed_ok']," FAIL:",acc['relaxed_fail'],acc['ex'] or '')
    print("\nminimal-core samples (P | J | W | dG/bd/ret):")
    for s in acc['samples']: print("  ",s)
    print("VERDICT:", "MINIMAL-CORE ROTATION holds (B)" if acc['relaxed_fail']==0 and acc['rows']>0 else "FAIL")

if __name__=="__main__":
    main()
