"""Test candidate strong inequalities (subsets of the slack) on the sample configs:
  (A) S>=0 itself (= RHSq - pen, with RHSq = Q1 - sumT(T-N))
  (B) Q1 - nx2 - pen >= 0   [drop the +N(N^2-Gamma) term: is the harder ineq still true?]
  (C) Q1 - nx2 >= 0          [pure V2-budget]
  (D) Q1 - (N/5)*TVcut >= 0  [budget vs raw cut TV, drop nx2 and bad]
  (E) Q1/2 - nx2 >= 0        [V2 with K=2]
where Q1=Gamma*(N^2/25-beta), nx2=||x||^2, pen=(N/5)(TVcut-TVbad).
"""
from fractions import Fraction as F
import _wf_rig_b_measure as MZ

def rows():
    R=[]
    for nm,n,E in MZ.CONFIGS:
        adj,cuts=MZ.gmins(n,E)
        if not cuts: continue
        q=MZ.quants(n,adj,cuts[0])
        if q: R.append((nm,q))
    grot=MZ.mycielski(5,MZ.Cn(5)); mycg=MZ.mycielski(grot[0],grot[1])
    for nm,(nn,EE) in [('Grotzsch',grot),('Myc(Grotzsch)',mycg),('M(C7)',MZ.mycielski(7,MZ.Cn(7)))]:
        adj,cuts=MZ.gmins(nn,EE)
        for s in cuts[:1]:
            q=MZ.quants(nn,adj,s)
            if q: R.append((nm,q))
    return R

def main():
    print('%-16s %8s %8s %8s %8s %8s'%('name','S(A)','B','C','D','E'))
    for nm,q in rows():
        N=q['N']
        Q1=q['Q1']; nx2=q['nx2']; pen=F(N,5)*(q['TVcut']-q['TVbad'])
        A=q['S']
        B=Q1-nx2-pen
        C=Q1-nx2
        D=Q1-F(N,5)*q['TVcut']
        E=Q1-2*nx2
        def f(z):
            return 'OK' if z>=0 else 'NEG(%s)'%float(z)
        print('%-16s %8s %8s %8s %8s %8s'%(nm,f(A),f(B),f(C),f(D),f(E)))

if __name__=='__main__':
    main()
