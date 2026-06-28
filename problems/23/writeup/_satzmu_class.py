"""Codex block 30: SAT-ZMU-CLASS. If a cut edge e=uv has mu(e)=0 AND one endpoint saturated (T=N), then
(1) the OTHER endpoint has T=0, and (2) O is empty. (Implies SAT-ZMU.) Test on ALL configs (incl O-empty,
where the incidences live). Violation = a saturated-zero-mu incidence with other-endpoint T>0 OR O nonempty.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def incidences(info):
    """Return (n_incid, violations) where an incidence is a zero-mu cut edge with a saturated endpoint."""
    N=info['n']; T=info['T']
    O=[v for v in range(N) if T[v]>N]
    Oempty=(len(O)==0)
    mu=mu_edges(info)
    viol=[]; nincid=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        su=(T[u]==N); sv=(T[v]==N)
        if not (su or sv): continue
        nincid+=1
        # classification: other endpoint T=0 AND O empty
        other_T0 = (T[v]==0 if su and not sv else (T[u]==0 if sv and not su else (T[u]==0 or T[v]==0)))
        ok = other_T0 and Oempty
        if not ok:
            viol.append((u,v,float(T[u]),float(T[v]),len(O)))
    return nincid, viol

def show(name, info):
    if info is None: print(f"  {name}: loads None"); return 0,0
    ni,vi=incidences(info)
    if vi:
        print(f"  {name} (N={info['n']}): *** SAT-ZMU-CLASS VIOLATION incidences={ni} viol={vi[:3]} O={[v for v in range(info['n']) if info['T'][v]>info['n']]} M={info['M']}",flush=True)
    return ni,len(vi)

def battery():
    cases=[]; g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,gN-1)],[(0,0),(2,3)],[(0,2),(2,5)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=24 and is_triangle_free(n,E): cases.append((f"isl{iN}+gad{gN} br{br} N={n}",n,E))
    return cases

if __name__=="__main__":
    print("=== SAT-ZMU-CLASS exact stress (incl O-empty, where incidences live) ===")
    tot_i=0; tot_v=0
    print("--- glued constructions ---")
    for name,n,E in battery():
        ni,nv=show(name,loads(n,E)); tot_i+=ni; tot_v+=nv
    print("--- named / Mycielskians / blow-ups ---")
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(7,Cn(7))
    for nm,(nn,EE) in [("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]:
        ni,nv=show(nm,loads(nn,EE)); tot_i+=ni; tot_v+=nv
    for g6,t in [("J?AADBWeay?",2),("J???E?pNu\\?",2),("I?BD@g]Qo",2)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        ni,nv=show(f"{g6}[{t}]",info); tot_i+=ni; tot_v+=nv
    print("--- census N=7..11 (ALL graphs incl O-empty) ---")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ci=0; cv=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ni,vi=incidences(info)
            ci+=ni; cv+=len(vi)
            if vi and wit is None: wit=(g6,vi[0])
        print(f"  census N={nn}: saturated-zero-mu incidences={ci} | SAT-ZMU-CLASS violations={cv}"+(f" WIT {wit}" if wit else ""),flush=True)
        tot_i+=ci; tot_v+=cv
    print(f"\nTOTAL: incidences={tot_i}, SAT-ZMU-CLASS violations={tot_v}")
