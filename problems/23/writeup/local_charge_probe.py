#!/usr/bin/env python3
"""Test LOCALIZED charging bounds for (R): ell_max(w)*R(w) <= K = N+(N^2-Gamma).
We want a bound that is TIGHT at C5[q] and PROVABLE via CD + shortestness, i.e. that splits K's budget
into a part 'paid' by w's own cycles and the global deficit.

Candidate families measured (each: does CANDIDATE >= ell_max(w)*R(w) hold for all w? tight at C5[q]?):

 (P1) ell_max(w)*R(w) <= N                     [FALSE off-extremal? -- it's <=K always but is it <=N? test]
 (P2) ell_max(w)*R(w) <= T_uniform(w) + (L-Lbar)*R   trivial identity, skip
 (P3) The "energy" bound: for each f thru w, p_f(w) <= ell(f)/N  ??  -> R(w) <= sum ell(f)/N over F(w)
      => ell_max*R <= L * (1/N) sum_{f in F(w)} ell(f).  Tight at C5[q]? L=5, sum ell=5*|F(w)|=5*q^2,
      /N=5q^2/(5q)=q, *L=5q=N. YES potentially tight. test p_f(w)<=ell(f)/N and the resulting bound<=K.
 (P4) sum_{f in F(w)} ell(f) <= N + (N^2-Gamma)/L_min ... measure sum_{f thru w} ell(f) vs N.
"""
import io, contextlib, subprocess
from fractions import Fraction as F
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def per_graph(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    n_=n
    R=[F(0) for _ in range(n)]; ellmax=[0]*n
    sumell_thru=[F(0) for _ in range(n)]    # sum_{f in F(w)} ell(f)
    pmax_over_ellratio=F(0)                  # max over (f,w) of p_f(w)/(ell(f)/N) -- tests P3 premise <=1
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        through=[0]*n
        for P in Ps:
            for v in set(P): through[v]+=1
        for v in range(n):
            if through[v]>0:
                pf=F(through[v],nf)
                R[v]+=pf
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
                sumell_thru[v]+=ell[f]
                ratio = pf / F(ell[f],n)    # p_f(w) / (ell/N)
                if ratio>pmax_over_ellratio: pmax_over_ellratio=ratio
    return dict(n=n,G=G,K=n+(n*n-G),R=R,ellmax=ellmax,sumell_thru=sumell_thru,
                pmax_ratio=pmax_over_ellratio)

def run(graphs,acc):
    for nm,(n,E) in graphs:
        d=per_graph(n,E)
        if d is None: continue
        n=d['n']; K=d['K']; G=d['G']
        if d['pmax_ratio']>acc['p3prem']: acc['p3prem']=d['pmax_ratio']; acc['p3arg']=nm
        for w in range(n):
            Rw=d['R'][w]
            if Rw==0: continue
            L=d['ellmax'][w]; SE=d['sumell_thru'][w]
            lr=L*Rw
            # P1: L*R<=N ?
            if lr>n: acc['P1fail']+=1;
            if lr>n and lr-n>acc['P1worst']: acc['P1worst']=float(lr-n); acc['P1arg']=(nm,w,float(lr),n)
            # P3 bound: L * SE / N  >= L*R  ?  (i.e. R <= SE/N)
            p3 = L*SE/F(n)
            if lr>p3: acc['P3fail']+=1
            if lr>p3 and float(lr-p3)>acc['P3worst']: acc['P3worst']=float(lr-p3); acc['P3arg']=(nm,w,float(lr),float(p3))
            # is P3 bound <= K? (needs to be, to be useful)
            if p3>K: acc['P3overK']+=1
            if p3>K and float(p3-K)>acc['P3overKworst']: acc['P3overKworst']=float(p3-K); acc['P3overKarg']=(nm,w,float(p3),K,G,n)

if __name__=="__main__":
    acc=dict(P1fail=0,P1worst=0.0,P1arg=None,P3fail=0,P3worst=0.0,P3arg=None,
             P3overK=0,P3overKworst=0.0,P3overKarg=None,p3prem=F(0),p3arg=None)
    graphs=[(f"C5[{q}]",blow(q)) for q in (2,3,4)]
    graphs.append(("n8",dec("G?\x60F\x60w")))
    run(graphs,acc)
    for nn in range(5,8):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        run([(g6,dec(g6)) for g6 in out],acc)
    print("P1 (L*R<=N): fails=%d worst-excess=%.3f at %s"%(acc['P1fail'],acc['P1worst'],acc['P1arg']))
    print("P3 premise max p_f(w)/(ell/N) = %s (%.3f)  [<=1 needed for P3] at %s"%(acc['p3prem'],float(acc['p3prem']),acc['p3arg']))
    print("P3 bound (R<=SE/N i.e. L*R<=L*SE/N): fails=%d worst=%.3f at %s"%(acc['P3fail'],acc['P3worst'],acc['P3arg']))
    print("P3 bound exceeds K: count=%d worst=%.3f at %s"%(acc['P3overK'],acc['P3overKworst'],acc['P3overKarg']))
