"""Final cross-validation for LEMMA (M), Family #2: use _h.maxcut_all DIRECTLY (the exact all-max-cut
brute) on the largest reachable glued-island graphs (N up to 24) to confirm no global-max interior-overlap.
This double-checks _wf_mhunt_2's fused brute against the canonical maxcut_all helper.
Also reports, for each graph, whether any overlap appears on a maxcut_all-returned (global-max) cut.
EXACT. Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
from _h import maxcut_all, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:
        if a!=b: adj[a].add(b); adj[b].add(a)
    return adj

def overlaps_on_cut(n,adj,s):
    if not Bconn(n,adj,s): return None
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    res=[]
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1: chords.append((pp[0],pp[-1])); break
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                a1,b1=chords[i]; a2,b2=chords[j]
                if a1>a2: a1,b1,a2,b2=a2,b2,a1,b1
                if a2<min(b1,b2): res.append((f,tuple(P_f),(a1,b1),(a2,b2)))
    return res

def check(name,n,E):
    if not is_triangle_free(n,E): print(f"  {name}: not tri-free, skip"); return
    adj=adj_of(n,E)
    cuts=maxcut_all(n,adj)   # EXACT all global-max cuts
    nB=sum(1 for s in cuts if Bconn(n,adj,s))
    ov_total=0; ov_cuts=0
    for s in cuts:
        ov=overlaps_on_cut(n,adj,s)
        if ov: ov_cuts+=1; ov_total+=len(ov)
    print(f"  {name} N={n}: #global-max-cuts={len(cuts)} connB={nB} "
          f"GLOBAL-MAX-cuts-with-interior-overlap={ov_cuts} (overlaps={ov_total})"
          + ("  *** COUNTEREXAMPLE ***" if ov_total else ""),flush=True)
    return ov_total

if __name__=="__main__":
    print("=== maxcut_all cross-validation on largest glued-island graphs (N<=24) ===",flush=True)
    grot=mycielski(5,Cn(5))       # N=11
    mycC7=mycielski(7,Cn(7))      # N=15
    tot=0
    # C7 + Myc(C7) single bridge: N=22
    for la in range(7):
        for lb in [0,7,14]:   # base / mid / apex of Myc(C7)
            n,E=union_disjoint((7,Cn(7)),mycC7); E=E+[(la,7+lb)]
            tot+=check(f"C7+MycC7+brg({la},{lb})",n,E) or 0
    # C5 + Myc(C7) + extra C5 chain: N=20
    n,E=union_disjoint((5,Cn(5)),mycC7,(5,Cn(5)))
    E=E+[(0,5),(5+0,5+mycC7[0]+0)]   # bridge island0->mycC7 base, mycC7 base->island2
    tot+=check("C5+MycC7+C5 chain (N=20)",n,E) or 0
    # Grotzsch + Grotzsch double island bridged: N=22
    for la in range(3):
        n,E=union_disjoint(grot,grot); E=E+[(la,11+0)]
        tot+=check(f"Grot+Grot brg({la},0) N=22",n,E) or 0
    # C5 + Myc(C7) bridge at apex (N=20): apex=14 is the cone tip with O
    for la in range(5):
        n,E=union_disjoint((5,Cn(5)),mycC7); E=E+[(la,5+14)]
        tot+=check(f"C5+MycC7 brg apex({la}) N=20",n,E) or 0
    print(f"\n  === maxcut_all cross-val TOTAL global-max interior-overlaps = {tot} "
          f"({'COUNTEREXAMPLE FOUND' if tot else 'lemma (M) holds'}) ===",flush=True)
