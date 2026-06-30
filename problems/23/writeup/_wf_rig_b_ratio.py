"""Measure RHS_quad = Q1 - sum T(T-N) vs TV penalty, and Cauchy-Schwarz feasibility."""
from fractions import Fraction as F
import _wf_rig_b_measure as MZ

def main():
    rows=[]
    for nm,n,E in MZ.CONFIGS:
        adj,cuts=MZ.gmins(n,E)
        if not cuts: continue
        q=MZ.quants(n,adj,cuts[0])
        if q: rows.append((nm,q))
    grot=MZ.mycielski(5,MZ.Cn(5)); mycg=MZ.mycielski(grot[0],grot[1])
    for nm,(nn,EE) in [('Grotzsch',grot),('Myc(Grotzsch)',mycg),('M(C7)',MZ.mycielski(7,MZ.Cn(7)))]:
        adj,cuts=MZ.gmins(nn,EE)
        for s in cuts[:1]:
            q=MZ.quants(nn,adj,s)
            if q: rows.append((nm,q))
    print('%-16s %12s %10s %10s %8s %10s'%('name','RHSq','penN5','ratio','Dcut','TVcut^2/Dcut'))
    for nm,q in rows:
        N=q['N']
        RHSq=q['Q1']-(N*q['Gamma']-N**3)-q['nx2']
        pen=F(N,5)*(q['TVcut']-q['TVbad'])
        r=float(pen/RHSq) if RHSq!=0 else 0.0
        tv2=F(q['TVcut']**2,q['Dcut']) if q['Dcut']!=0 else F(0)
        print('%-16s %12s %10s %10.4f %8s %10.3f'%(nm,str(RHSq),str(pen),r,str(q['Dcut']),float(tv2)))

if __name__=='__main__':
    main()
