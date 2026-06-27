"""Find the PERMISSIVE PH-infeasible census graphs (N=10,11) and dump the min-cut obstruction:
which overshoot atoms have insufficient shadow capacity. Determines: is PH-fail real (COUPLE holds but
prefix-defect shadow too small) or shadow-reading artifact? Reports COUPLE status of each failing graph."""
import subprocess
from fractions import Fraction as F
from census_GPI import dec, GENG
import _ph_maxflow_test as P

def couple_holds(info):
    n=info['n']; T=info['T']; Uover=info['Uover']; G=info['G']
    return Uover <= n*n-G

def detail(g6):
    n,E=dec(g6); info=P.loads_atoms(n,E)
    if info is None: return None
    st,mf,dem,uo=P.ph_test(info)
    if st!='INFEASIBLE': return None
    # gather atoms + shadows
    T=info['T']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']
    atoms=[]
    allsh=set()
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        for C in Ps:
            for j,w in enumerate(C):
                if T[w]>N:
                    m=(T[w]-N)*F(ell[f],nf)/T[w]
                    sh,eta=P.shadow(info,f,C,j)
                    atoms.append((w,float(m),sorted(sh),eta)); allsh|=sh
    capsh=sum((N-T[z]) for z in allsh if T[z]<N)
    return dict(g6=g6,n=n,Gamma=info['G'],Uover=float(info['Uover']),Uunder=float(info['Uunder']),
               maxflow=mf,demand=dem,couple=couple_holds(info),
               n_atoms=len(atoms),union_shadow=sorted(allsh),cap_union_shadow=float(capsh),
               sample_atoms=atoms[:6])

for nn in (10,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    found=0
    for g6 in out:
        d=detail(g6)
        if d:
            found+=1
            print(f"\n[N={nn}] {d['g6']} Gamma={d['Gamma']} deficit={d['n']**2-d['Gamma']}")
            print(f"   Uover={d['Uover']:.3f} Uunder={d['Uunder']:.3f} | COUPLE holds={d['couple']} | maxflow={d['maxflow']:.3f} < demand(2Uover)={d['demand']:.3f}")
            print(f"   union shadow={d['union_shadow']} cap={d['cap_union_shadow']:.3f} (need >= demand {d['demand']:.3f}: {d['cap_union_shadow']>=d['demand']-1e-9})")
            print(f"   n_atoms={d['n_atoms']} sample(w,mass,shadow,eta)={[(a[0],round(a[1],3),a[2],a[3]) for a in d['sample_atoms']]}")
        if found>=4 and nn==11: break
    print(f"--- N={nn}: shown {found} permissive PH-failures ---")
