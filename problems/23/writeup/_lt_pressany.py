"""Test transport feasibility with PRESS_MODE='any' (pressure debt payable by ANY causal source) and
volume still same-K-component. If this restores feasibility on the full battery, the missing-arc diagnosis is:
pressure debt from cut edges not covered by a geodesic (e.g. bridges) needs non-local bank."""
import _level_transport as LT
LT.PRESS_MODE='any'        # relax pressure admissibility
LT.ADMIT_MODE='comp'       # volume: same K-component
import subprocess
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _level_transport import feasible, blow, bridge

nfe=0; ntot=0; first=None
def go(name,n,adj,side):
    global nfe,ntot,first
    if n>24: return
    r=LT.feasible(name,n,adj,side,verbose=False)
    if r is None: return
    ntot+=1
    if not r['feas']:
        nfe+=1
        if first is None: first=(name,''.join(map(str,side)),n,r['beta'],str(r['slack']))

for c in (5,7,9):
    for t in range(1,5):
        n,E=blow([t]*c)
        if n>24: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): go("C%d[%d]"%(c,t),n,adj,s)
for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,1,2,1,3]]:
    n,E=blow(parts)
    if n>24: continue
    adj,cuts=gmins(n,E)
    for s in (cuts[:2] if cuts else []): go("nu%s"%parts,n,adj,s)
print("  blow-ups: infeas=%d/%d"%(nfe,ntot),flush=True)
grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                  ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                  ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0)),("Grotzsch|C5",bridge(mycielski(5,Cn(5)),(5,Cn(5)),0,0))]:
    adj,cuts=gmins(nn,E)
    for s in cuts[:3]: go(nm,nn,adj,s)
print("  Mycielskian+glued: infeas=%d/%d"%(nfe,ntot),flush=True)
for nn in range(7,12):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    b0=nfe
    for g6 in outg:
        n,E=dec(g6); adj,cuts=gmins(n,E)
        for s in cuts: go("cen%s"%g6,n,adj,s)
    print("  census N=%d: infeas+%d (total %d/%d)"%(nn,nfe-b0,nfe,ntot),flush=True)
print("\n  PRESS_MODE=any: TOTAL=%d INFEASIBLE=%d %s"%(ntot,nfe,("FIRST %s"%(first,)) if first else ""),flush=True)
print("  === %s ==="%("FEASIBLE EVERYWHERE => missing arc = non-local pressure (bridge/uncovered cut edges)" if not nfe else "STILL FAILS => deeper gap"),flush=True)
