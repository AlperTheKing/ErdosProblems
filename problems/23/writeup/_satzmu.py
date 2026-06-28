"""Codex block 27: SAT-ZMU. For connected-B gamma-min maxcut with O nonempty: every zero-mu cut edge has
NEITHER endpoint saturated (T!=N). Violation = a zero-mu cut edge with an endpoint T==N (= _zmu.test's 'sat').
Stress on census + blow-ups + Mycielskians + a BROAD battery of adversarial glued-island constructions
(the only non-vacuous gate, and where full ZMU already died). Hunt for a saturated zero-mu boundary edge.
Exact Fraction."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import test as zmu_test, mu_edges
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free, build_K_T, Kcomponents

def report(name, info, hunt=True):
    if info is None: return 0,0
    r=zmu_test(info)
    if r is None:
        return 0,0   # O empty
    nsat=len(r['sat']); nz=r['nzero']
    if nsat>0:
        print(f"  {name}: *** SAT-ZMU VIOLATION sat={r['sat']} (zero-mu edge with saturated endpoint) | zero-mu={nz} O={r['O']}",flush=True)
    return nsat, nz

def glue(islandN, islandE, gadgetN, gadgetE, bridges):
    n,E=union_disjoint((islandN,islandE),(gadgetN,gadgetE))
    for (i,j) in bridges: E=E+[(i, islandN+j)]
    return n,E

def battery():
    cases=[]
    g15=mycielski(7,Cn(7))      # Myc(C7) N=15
    gr=mycielski(5,Cn(5))       # Grotzsch N=11
    g23=mycielski(*gr)          # Myc(Grotzsch) N=23
    islands=[("C5",5,Cn(5)),("C7",7,Cn(7))]
    gadgets=[("MycC7",g15),("Grotzsch",gr)]
    for iname,iN,iE in islands:
        for gname,(gN,gE) in gadgets:
            # try many bridge sets (single + double), all island-vertex 0/1/2 to gadget vertex 0..min(gN,8)
            brs=[[(0,0)],[(0,1)],[(0,2)],[(0,gN-1)],
                 [(0,0),(2,3)],[(0,0),(1,4)],[(0,2),(2,5)],[(1,0),(3,4)]]
            for br in brs:
                if any(j>=gN for _,j in br): continue
                n,E=glue(iN,iE,gN,gE,br)
                if n>22: continue
                if is_triangle_free(n,E):
                    cases.append((f"{iname}+{gname} br{br} N={n}",n,E))
    return cases

if __name__=="__main__":
    print("=== SAT-ZMU exact stress (violation = zero-mu cut edge with a SATURATED T=N endpoint) ===")
    totsat=0; tested=0
    # adversarial glued constructions (the decisive non-vacuous gate)
    print("--- glued-island constructions ---")
    for name,n,E in battery():
        s,z=report(name,loads(n,E)); totsat+=s; tested+=1
    print(f"  [{tested} constructions tested, SAT-ZMU violations={totsat}]",flush=True)
    # named + blow-ups + Mycielskians
    print("--- named / Mycielskians ---")
    from _superphi import blow
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); s,z=report(g6,loads(n,E)); totsat+=s
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(7,Cn(7))
    for nm,(nn,EE) in [("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]:
        s,z=report(nm,loads(nn,EE)); totsat+=s
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2)]:
        nn,EE=blow(g6,t)
        info=loads(nn,EE)
        if info: s,z=report(f"{g6}[{t}]",info); totsat+=s
    # census
    print("--- census ---")
    for nn in range(8,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        csat=0; cz=0; cO=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=zmu_test(info)
            if r is None: continue
            cO+=1; cz+=r['nzero']; csat+=len(r['sat'])
            if r['sat'] and wit is None: wit=(g6,r['sat'])
        print(f"  census N={nn}: graphs-with-O={cO} zero-mu-edges={cz} SAT-ZMU-viol={csat}"+(f" WIT {wit}" if wit else ""),flush=True)
        totsat+=csat
    print(f"\nTOTAL SAT-ZMU violations across all gates: {totsat}")
