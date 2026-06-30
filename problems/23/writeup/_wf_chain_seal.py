"""SEAL: verify the full logical chain EXACTLY on census<=10 (fast) + key blowups + MycGrotzsch N23.
Chain for every NONUNIQUE bad edge f on a gamma-min connected-B max cut:
  (I)  row_f = sum_i a_i           (layer identity)
  (II) var_f = sum_i (a_i-<S>)^2 + sum_i w_i   (variance ANOVA identity)
  (III) var_f <= ell_f (Smax-<S>)(<S>-Smin)    (Bhatia-Davis, elementary)
  (IV) target  n^2 >= var_f + n row_f          (== n(n-row)>=var)
  (V)  STRONG' ell_f[(Smax-<S>)(<S>-Smin)+ n<S>] <= n^2   ==>  (IV) via (III)
Verify (I),(II),(III) are EQUALITIES/INEQ that hold with 0 violation, and STRONG'=>target pointwise.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
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
    for parts in [[2,2,2,2,2],[3,3,3,3,3],[1,5,2,2,5],[1,6,2,2,6],[1,2,1,2,1,2,1]]:
        nn,EE=blowup(parts); adj,cuts=gmins(nn,EE)
        for s in cuts: yield (f"blow{parts}",nn,adj,s)
    nn,EE=mycielski(*mycielski(5,Cn(5)))
    adj,cuts=gmins(nn,EE)
    for s in cuts: yield ("MycGrotzschN23",nn,adj,s)

bad_I=bad_II=bad_III=bad_target=bad_implies=0; nrows=0
for nm,n,adj,s in cases():
    b=build(n,adj,s)
    if b is None: continue
    M,ell,T,mu,cyc,S,pf=b
    for f in M:
        Ps=cyc[f]
        if len(Ps)<2: continue
        L=ell[f]; k=len(Ps)
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mean=row/ll
        var=sum(d[v]*(S[v]-mean)**2 for v in d)
        Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
        layer_w=[dict() for _ in range(L)]
        for P in Ps:
            for i,v in enumerate(P): layer_w[i][v]=layer_w[i].get(v,F(0))+F(1,k)
        a=[sum(layer_w[i][v]*S[v] for v in layer_w[i]) for i in range(L)]
        w=[sum(layer_w[i][v]*(S[v]-a[i])**2 for v in layer_w[i]) for i in range(L)]
        nrows+=1
        if sum(a)!=row: bad_I+=1
        if sum((a[i]-mean)**2 for i in range(L))+sum(w)!=var: bad_II+=1
        BD=ll*(Smax-mean)*(mean-Smin)
        if var>BD: bad_III+=1
        target_ok = F(n)**2 >= var+F(n)*row
        if not target_ok: bad_target+=1
        strongp = ll*((Smax-mean)*(mean-Smin)+F(n)*mean) <= F(n)**2
        if strongp and not target_ok: bad_implies+=1   # STRONG' must imply target
print("nonunique rows:",nrows)
print("bad (I) row=sum a_i:",bad_I)
print("bad (II) var ANOVA:",bad_II)
print("bad (III) Bhatia-Davis var<=ell(Smax-<S>)(<S>-Smin):",bad_III)
print("bad (IV) target n^2>=var+n row:",bad_target)
print("bad (V) STRONG' true but target false:",bad_implies)
print("SEAL", "OK" if bad_I==bad_II==bad_III==bad_target==bad_implies==0 else "FAILED")
