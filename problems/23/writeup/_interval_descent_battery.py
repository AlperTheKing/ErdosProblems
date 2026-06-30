"""Run Codex's INTERVAL-DESCENT check (block 259) on the ROUTE-KILLER battery: Mycielskian N=23, glued islands,
two-lane, k-lane, blow-ups -- cases his census/N26 scout did not cover. For each gmins cut, find interval-Hall
failures; for each, check has_descent (a switch preserving cut size + B-connected + lowering Gamma). no_descent
count must be 0 (=> Gamma-min cut has no failure => high-side UPO). Uses Codex's lab logic (coverage extension)."""
import subprocess
from _codex_interval_descent_gate import has_descent
from _codex_interval_failure_switch_lab import adj_from_edges, interval_failures
from _h import dec, GENG, Bconn
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def scan(name,n,E,side,acc):
    if not Bconn(n,adj_from_edges(n,E),side): return
    adj=adj_from_edges(n,E)
    try:
        fails=interval_failures(n,adj,side,name)
    except Exception as ex:
        acc['err']+=1; return
    acc['nconf']+=1; acc['nfail']+=len(fails)
    for failure in fails:
        hits=has_descent(n,E,adj,side,failure)
        if not hits:
            acc['nodesc']+=1
            if acc['first'] is None: acc['first']=(name,n,failure.get('path'))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nconf':0,'nfail':0,'nodesc':0,'err':0,'first':None}
    # two-lane + k-lane
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); scan("two-lane-L%d"%L,n,E,side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); scan("klane-L%dk%d"%(Ll,k),n,E,side,acc)
    print("  two-lane+k-lane: confs=%d fails=%d nodesc=%d err=%d"%(acc['nconf'],acc['nfail'],acc['nodesc'],acc['err']),flush=True)
    # blow-ups (gmins)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>30: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): scan("C%d[%d]"%(c,t),n,E,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>30: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): scan("nu%s"%parts,n,E,s,acc)
    # Mycielskians + glued (route-killers)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: scan(nm,nn,E,s,acc)
    print("  + blow-ups + Mycielskians + glued: confs=%d fails=%d nodesc=%d err=%d"%(acc['nconf'],acc['nfail'],acc['nodesc'],acc['err']),flush=True)
    print("\n  total configs=%d  interval-Hall failures=%d  NO-DESCENT (obstructions)=%d  errors=%d"%(acc['nconf'],acc['nfail'],acc['nodesc'],acc['err']),flush=True)
    if acc['first']: print("  first no-descent: %s"%(acc['first'],),flush=True)
    print("  === INTERVAL-DESCENT on route-killers: %s ==="%("HOLDS (every failure has a Gamma-descending switch)" if acc['nodesc']==0 else "FAILS -- obstruction found"),flush=True)
