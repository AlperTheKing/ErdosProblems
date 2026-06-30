"""Layer-level sufficient conditions for target n^2 >= var + n*row, with
   row = sum_i a_i, var = sum_i (a_i-<S>)^2 + sum_i w_i  (<S>=row/ell).
Candidate sufficient lemmas (test exact, hunt fails):
 (P1) per-layer:  a_i^2 + w_i + n*a_i <= n^2 / ell  for each i ?  (sum gives target without the +(Σa)^2/ell helper... too strong?)
 (P2) Smax <= n  (already 0-fail full battery) and a_i <= n.
 (P3) sum_i (a_i^2 + w_i) <= Smax * row   (i.e. <S^2>*ell <= Smax*row) -> equivalent to <S^2><=Smax<S>, trivially TRUE (S<=Smax).
 (P4) STRONG row*(Smax+n-<S>)<=n^2, restated per-layer.
 (P5) the 'second-moment' bound: sum_v p_f(v) S(v)^2 <= n * row  ??  (would give ell<S^2> <= n*row => var = ell<S^2>-row^2/ell <= n*row-row^2/ell;
       then target n^2 >= var+n*row <= 2n*row-row^2/ell; need n^2>=2n*row-row^2/ell i.e (n-row/?)... check)
Measure each.  Battery census<=10 + blowups.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_var_0 import build

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

def cases():
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: yield (f"c{nn}:{g6}",n,adj,s)
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,5,2,2,5],[1,2,1,2,1,2,1],[1,6,2,2,6]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)

if __name__=="__main__":
    print("=== layer-level sufficient conditions ===",flush=True)
    nrows=0
    f_P1=0; f_P5=0; w_P5=None; f_amax=0
    f_secmom=0; w_secmom=None  # P5: sum p S^2 <= n*row
    for nm,n,adj,s in cases():
        b=build(n,adj,s)
        if b is None: continue
        M,ell,T,mu,cyc,S,pf=b
        for f in M:
            Ps=cyc[f]
            if len(Ps)<2: continue
            L=ell[f]; k=len(Ps)
            d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
            sm=sum(d[v]*S[v]**2 for v in d)   # = ell*<S^2>
            layer_w=[dict() for _ in range(L)]
            for P in Ps:
                for i,v in enumerate(P): layer_w[i][v]=layer_w[i].get(v,F(0))+F(1,k)
            a=[sum(layer_w[i][v]*S[v] for v in layer_w[i]) for i in range(L)]
            w=[sum(layer_w[i][v]*(S[v]-a[i])**2 for v in layer_w[i]) for i in range(L)]
            nrows+=1
            # P1 per-layer
            for i in range(L):
                if a[i]**2 + w[i] + F(n)*a[i] > F(n)**2/L: f_P1+=1; break
            # a_i <= n
            for i in range(L):
                if a[i]>F(n): f_amax+=1; break
            # P5 second moment: sum p S^2 <= n*row
            slk=F(n)*row - sm
            if slk<0:
                f_secmom+=1
                if w_secmom is None or slk<w_secmom[0]: w_secmom=(slk,nm,f,n,str(row),str(sm))
    print("nonunique rows:",nrows)
    print(f"P1 per-layer (a^2+w+n a <= n^2/ell) fails: {f_P1}")
    print(f"a_i<=n fails: {f_amax}")
    print(f"P5 sum_v p S^2 <= n*row fails: {f_secmom} worst:{w_secmom}")
