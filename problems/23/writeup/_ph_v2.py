"""PH max-flow test v2 -- FAITHFUL TWO-SIDED shadow (GPT round-12: factor 2 = left L_j + right R_j prefixes).
For overshoot atom (f, C=[c_0..c_{ell-1}], w=c_j):  bad edge f=(c_0,c_{ell-1}).
  LEFT prefix  L_j=[c_0..c_j],  RIGHT prefix R_j=[c_j..c_{ell-1}],  S=max_obstruction(C), R=V\\C.
  sh_L = underloaded R-vertices touched by e(C\\L_j,S)+e(L_j,R\\S);  sh_R likewise with R_j.
The 2-to-1 transport: each atom routes mass m to sh_L AND m to sh_R (total 2m); sink cap u(z)=(N-T(z))_+.
PH feasible iff maxflow == 2*U_over. Re-tests the v1 permissive failures, then census."""
from fractions import Fraction as F
from collections import defaultdict, deque
import subprocess
from census_GPI import dec, GENG
from _ph_maxflow_test import loads_atoms, max_obstruction, touched, maxflow

def shadows_2sided(info, C, j):
    n=info['n']; M=info['M']; Bset=info['Bset']; Mset=info['Mset']; T=info['T']
    Cset=set(C); R=set(x for x in range(n) if x not in Cset)
    eta,S=max_obstruction(n,info['adj'],info['side'],M,C); RmS=R-S
    Lj=set(C[:j+1]); CmL=set(C[j+1:])
    Rj=set(C[j:]);   CmR=set(C[:j])
    shL=touched(CmL,S,Bset,Mset)|touched(Lj,RmS,Bset,Mset)
    shR=touched(CmR,S,Bset,Mset)|touched(Rj,RmS,Bset,Mset)
    u=lambda z: T[z]<n
    return set(z for z in shL if u(z)), set(z for z in shR if u(z)), eta

def ph2(info):
    n=info['n']; T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; N=n; Uover=info['Uover']
    if Uover==0: return ('trivial',0.0,0.0)
    cap=defaultdict(lambda: defaultdict(float)); V=set(['__S','__T']); demand=0.0
    k=0
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        for C in Ps:
            for j,w in enumerate(C):
                if T[w]>N:
                    m=float((T[w]-N)*F(ell[f],nf)/T[w])
                    shL,shR,eta=shadows_2sided(info,C,j)
                    aL='L%d'%k; aR='R%d'%k; k+=1; V.add(aL); V.add(aR)
                    cap['__S'][aL]+=m; cap['__S'][aR]+=m; demand+=2*m
                    for z in shL: zid='Z%d'%z; V.add(zid); cap[aL][zid]=1e18
                    for z in shR: zid='Z%d'%z; V.add(zid); cap[aR][zid]=1e18
    for z in range(n):
        if T[z]<N:
            zid='Z%d'%z
            if zid in V: cap[zid]['__T']+=float(N-T[z])
    mf=maxflow(cap,'__S','__T',V)
    return ('feasible' if mf>=demand-1e-7 else 'INFEASIBLE', mf, demand)

# v1 permissive failures
fails=["I?BD@g]Qo","J?AADagROl?","J?ABA_we`Y?","J?ABAqoeaX?","J?ABCfGM@h?"]
print("=== PH v2 (TWO-SIDED shadow) on v1's permissive failures ===")
for g6 in fails:
    n,E=dec(g6); info=loads_atoms(n,E)
    st,mf,dem=ph2(info)
    print(f"  {g6:13} N={n} Uover={float(info['Uover']):.3f} | PH2 {st} (maxflow={mf:.3f} demand={dem:.3f})")
print("--- census N=10,11: count PH2-infeasible (TWO-SIDED) ---")
for nn in (10,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    inf=triv=nt=0
    for g6 in out:
        n,E=dec(g6); info=loads_atoms(n,E)
        if info is None: continue
        nt+=1; st,_,_=ph2(info)
        if st=='trivial': triv+=1
        elif st=='INFEASIBLE': inf+=1
    print(f"  N={nn}: configs={nt} | PH2-infeasible(2-sided)={inf} | trivial={triv}",flush=True)
