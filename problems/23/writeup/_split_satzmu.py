"""Codex block 32: split of SAT-ZMU-CLASS.
Lemma A (SAT-ZMU-T0): every zero-mu cut edge uv with T(u)=N has T(v)=0.
Lemma B (ZERO-SAT-ADJ): if T(z)=0 and z is B-adjacent to v with T(v)=N, then O is empty.
A violation: A = zero-mu edge with a T=N endpoint and other endpoint T!=0;
            B = a B-edge (z,v), T[z]=0, T[v]=N, in an O-NONEMPTY config. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges
from _superphi import blow
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def testA(info):
    N=info['n']; T=info['T']
    mu=mu_edges(info); viol=[]
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]==N and T[v]!=0: viol.append((u,v,float(T[u]),float(T[v])))
        if T[v]==N and T[u]!=0: viol.append((v,u,float(T[v]),float(T[u])))
    return viol

def testB(info):
    N=info['n']; T=info['T']; Bset=info['Bset']
    O=[v for v in range(N) if T[v]>N]
    if not O: return []
    viol=[]
    for (a,b) in Bset:
        if T[a]==0 and T[b]==N: viol.append((a,b,float(T[a]),float(T[b]),len(O)))
        if T[b]==0 and T[a]==N: viol.append((b,a,float(T[b]),float(T[a]),len(O)))
    return viol

def show(name, info):
    if info is None: return 0,0
    va=testA(info); vb=testB(info)
    if va: print(f"  {name}: *** LEMMA-A VIOLATION {va[:3]}",flush=True)
    if vb: print(f"  {name}: *** LEMMA-B VIOLATION {vb[:3]} M={info['M']}",flush=True)
    return len(va),len(vb)

def battery():
    cases=[]; g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); g23=mycielski(*gr)
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr,g23]:
            for br in [[(0,0)],[(0,1)],[(0,gN-1)],[(0,0),(2,3)],[(0,2),(2,5)],[(1,0),(3,4)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=24 and is_triangle_free(n,E): cases.append((f"isl{iN}+gad{gN} br{br} N={n}",n,E))
    return cases

if __name__=="__main__":
    print("=== Lemma A (SAT-ZMU-T0) + Lemma B (ZERO-SAT-ADJ) exact stress ===")
    tA=0; tB=0
    print("--- glued constructions ---")
    for name,n,E in battery():
        a,b=show(name,loads(n,E)); tA+=a; tB+=b
    print("--- named / Mycielskians / blow-ups ---")
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(7,Cn(7))
    named=[("Grotzsch",(n1,E1)),("MycGrotzsch N=23",(n2,E2)),("MycC7 N=15",(m1,F1))]
    for nm,(nn,EE) in named:
        a,b=show(nm,loads(nn,EE)); tA+=a; tB+=b
    for g6,t in [("J?AADBWeay?",2),("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); a,b=show(f"{g6}[{t}]",loads(nn,EE)); tA+=a; tB+=b
    print("--- census N=7..11 (all graphs) ---")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ca=0; cb=0; wa=None; wb=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            va=testA(info); vb=testB(info)
            ca+=len(va); cb+=len(vb)
            if va and wa is None: wa=(g6,va[0])
            if vb and wb is None: wb=(g6,vb[0])
        print(f"  census N={nn}: Lemma-A viol={ca}{' WITA '+str(wa) if wa else ''} | Lemma-B viol={cb}{' WITB '+str(wb) if wb else ''}",flush=True)
        tA+=ca; tB+=cb
    print(f"\nTOTAL: Lemma-A violations={tA}, Lemma-B violations={tB}")
