"""Full-battery exact feasibility of GPT route-(d) causal level-transport (reuses _level_transport.feasible).
Cap N<=24 (covers census N<=11 all gmins cuts + blow-ups + iterated Mycielskians N=23 + glued islands =
the standing gate that killed earlier routes). Report infeasible count + first infeasible config/cut."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _level_transport import feasible, blow, adj_of, bridge

if __name__=="__main__":
    nfe=0; ntot=0; first=None
    def go(name,n,adj,side):
        global nfe,ntot,first
        if n>24: return
        r=feasible(name,n,adj,side,verbose=False)
        if r is None: return
        ntot+=1
        if not r['feas']:
            nfe+=1
            if first is None: first=(name,''.join(map(str,side)),n,r['beta'],str(r['slack']))
    # C5/C7/C9[t]
    for c in (5,7,9):
        for t in range(1,5):
            n,E=blow([t]*c)
            if n>24: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): go("C%d[%d]"%(c,t),n,adj,s)
    # non-uniform blow-ups
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,1,2,1,3]]:
        n,E=blow(parts)
        if n>24: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): go("nu%s"%parts,n,adj,s)
    print("  blow-ups done: infeas=%d/%d"%(nfe,ntot),flush=True)
    # Mycielskians + glued
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0)),("Grotzsch|C5",bridge(mycielski(5,Cn(5)),(5,Cn(5)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: go(nm,nn,adj,s)
    print("  Mycielskian+glued done: infeas=%d/%d"%(nfe,ntot),flush=True)
    # census all gmins cuts N=7..11
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        b0=nfe
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: go("cen%s"%g6,n,adj,s)
        print("  census N=%d done: infeas+%d (total %d/%d)"%(nn,nfe-b0,nfe,ntot),flush=True)
        if first: break
    print("\n  TOTAL configs=%d  TRANSPORT-INFEASIBLE=%d"%(ntot,nfe),flush=True)
    if first: print("  FIRST INFEASIBLE: %s"%(first,),flush=True)
    print("  === causal level-transport %s on full battery (N<=24) ==="%(
        "FEASIBLE EVERYWHERE => GPT proof skeleton confirmed" if not nfe else "FAILS -- skeleton incomplete"),flush=True)
