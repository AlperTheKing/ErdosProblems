"""On the GLUED ISLAND battery (where O-K-SUPPORT just failed), test the SATURATION-correct cond(1) statements:
(a) NO-SAT-Q-ONLY: no SATURATED (T==N) Q-only K-component (a positive-K component disjoint from O with all T==N);
(b) SAT-ZMU-CONN: zero-mu B-edge with a saturated (T=N) endpoint u => Kcomp(u) meets O;
(c) Schur certificate passes (cond 1/2/3) and SPEC rho(K)<=N.
Over ALL connected maxcuts of each construction. If (a)/(b)/(c) survive while O-K-SUPPORT fails, the saturation
qualifier is the right one. Exact Fraction (+ float rho for SPEC)."""
import numpy as np
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _schur_spec import test as schur_test, pf_exact

def checks_side(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    comp,find=kcomponents(n,cyc)
    # (a) NO-SAT-Q-ONLY: positive-K component disjoint from O with all T==N
    sat_qonly=0
    for root,vs in comp.items():
        pos=[v for v in vs if T[v]>0]
        if not pos: continue
        if set(pos)&O: continue
        if all(T[v]==N for v in pos): sat_qonly+=1
    # (b) SAT-ZMU-CONN
    satconn_viol=0
    if O:
        for e,val in mu.items():
            if val!=0: continue
            u,v=e
            for a in (u,v):
                if T[a]==N and not (comp[find(a)] & O): satconn_viol+=1
    return sat_qonly, satconn_viol, len(O)

def run(n,E,name):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    tot_satq=0; tot_satconn=0; ncuts=0
    for s in cuts:
        r=checks_side(n,adj,s)
        if r is None: continue
        ncuts+=1; tot_satq+=r[0]; tot_satconn+=r[1]
    # Schur cert + SPEC on loads (gamma-min) cut
    info=loads(n,E); sc='?'; spec='?'
    if info:
        rr=schur_test(info); d1=rr[1] or {}; sc=rr[0]+("/fails"+str(len(d1.get('fails',[]))) if rr[0]!='ok' else "")
        P,M2,ell2,nn=pf_exact(info); K=np.zeros((nn,nn))
        for d in P:
            vv=np.zeros(nn)
            for a,b in d.items(): vv[a]=float(b)
            K+=np.outer(vv,vv)
        rho=max(np.linalg.eigvalsh(K)); spec=f"rho={rho:.2f}<=N={info['n']}:{rho<=info['n']+1e-9}"
    print(f"  {name}: cuts={ncuts} | (a)SAT-Q-ONLY comps={tot_satq} | (b)SAT-ZMU-CONN viol={tot_satconn} | Schur={sc} | SPEC {spec}",flush=True)
    return tot_satq, tot_satconn

if __name__=="__main__":
    print("=== saturation-correct cond(1) on the GLUED battery (where O-K-SUPPORT failed) ===")
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    TA=0; TB=0
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE,gname in [(*g15,'MycC7'),(*gr,'Grotzsch')]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n<=22 and is_triangle_free(n,E):
                    a,b=run(n,E,f"isl{iN}+{gname} br{br} N={n}"); TA+=a; TB+=b
    print(f"\nTOTAL over glued battery: (a)SAT-Q-ONLY components={TA}  (b)SAT-ZMU-CONN violations={TB}")
    print("(a)=0 and (b)=0 with Schur=ok everywhere => saturation-qualified cond(1) survives the glued battery.")
