"""Hunt for a PROVABLE lemma implying A: <p_f, T> <= N*ell(f).
Test candidates EXACTLY on census N<=11 + odd-cycle blowups to N<=25 + N22 killer.
Each candidate is a (hopefully manifestly-provable) inequality that implies A.

Recall: T_w = sum_g ell(g) p_g(w);  <p_f,T> = sum_g ell(g) O_fg ;  O_fg=<p_f,p_g>.
We need sum_g ell(g) O_fg <= N ell(f).

Candidates (report fail count + worst ratio to target):
 (C1) 'mass-N law':  for each f,  sum_g O_fg * ell(g) <= N * O_ff^{?}... no. Try:
      <p_f,T> <= N * ||p_f||_1 = N ell(f) directly is A. Decompose by g-distance.
 (C2) Per-OTHER-edge transfer: O_fg <= (ell(f)+ell(g))/2 * (something)? test O_fg <= min(ell(f),ell(g)).
 (C3) The KEY anti-concentration: T_w <= N for w 'deep' ... instead test
      sum_g ell(g) O_fg = sum_w p_f(w) T_w ; split T_w = T_w^{in} (g whose geodesic 'aligns' with f) ...
 (C4) Cauchy-Schwarz pairing:  <p_f,T> <= sqrt(<p_f,p_f>) sqrt(<T,T>) -- too weak, test anyway scaled.
 (C5) ELL-MONOTONE rowsum: A is O ell <= N ell. Compare to proven O1<=N (ROWSUM-O). Does
      O ell <= N ell follow from O1<=N + O_fg<=? Test: is O ell <= ell(f)*max_g[(O1)_g]? no.
      Test directly whether  (O ell)_f / ell(f) <= (O 1)_f  i.e. weighted avg of ell under O_f-row <= ...
      Actually test  (O ell)_f <= ell(f) * (O1)_f / 1 ??? i.e. is  <p_f,T>/ell(f) <= (O1)_f?
      That would give A from ROWSUM-O. CHECK:  <p_f,T> <= ell(f) * (O1)_f ?
 (C6) The cleanest: is  T_w-averaged-over-p_f  <=  ell(f)-... test  <p_f,T> <= <p_f,S>*N/?
      <p_f,S> = (O1)_f <= N. And T_w = sum_g ell(g)p_g(w) <= ell_max * S_w. So <p_f,T> <= ell_max <p_f,S>
      <= ell_max * N. Too weak (ell_max factor). But maybe  <p_f,T> <= N <p_f,S> ??? i.e. avg ell under
      the load weighting <= N/(O1)_f *... test  <p_f,T> <= N (O1)_f / ??? Just test  <p_f,T> <= N*(O1)_f.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def build(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; cyc=info['cyc']; m=len(M)
    pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        di=pf[i]
        for j in range(m):
            s=F(0)
            for v,pv in di.items():
                pw=pf[j].get(v)
                if pw is not None: s+=pv*pw
            O[i][j]=s
    ellv=[F(ell[M[g]]) for g in range(m)]
    R=[sum(O[i][j]*ellv[j] for j in range(m)) for i in range(m)]  # <p_f,T>
    O1=[sum(O[i][j] for j in range(m)) for i in range(m)]
    return n,N,m,O,ellv,R,O1

def cand(info):
    n,N,m,O,ellv,R,O1=build(info)
    res={}
    # A itself
    res['A']=max((R[f]-F(N)*ellv[f]) for f in range(m)) if m else F(0)
    # C5: <p_f,T> <= ell(f)*(O1)_f  ?  (would give A from ROWSUM-O since (O1)_f<=N)
    res['C5']=max((R[f]-ellv[f]*O1[f]) for f in range(m)) if m else F(0)
    # C6: <p_f,T> <= N*(O1)_f ?
    res['C6']=max((R[f]-F(N)*O1[f]) for f in range(m)) if m else F(0)
    # C2 check: O_fg <= min(ell_f,ell_g) (entrywise) -- structural
    c2=F(0)
    for i in range(m):
        for j in range(m):
            d=O[i][j]-min(ellv[i],ellv[j])
            if d>c2: c2=d
    res['C2_Ofg<=min']=c2
    return res,m

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

def run():
    keys=['A','C5','C6','C2_Ofg<=min']
    worst={k:(F(-10**9),None) for k in keys}; ng=0
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            r,m=cand(info)
            for k in keys:
                if r[k]>worst[k][0]: worst[k]=(r[k],(g6,nn))
    print(f"=== candidates implying A, census graphs={ng} (want max residual <= 0) ===")
    for k in keys:
        w,g=worst[k]
        print(f"  {k:16s}: worst residual={float(w):+.5f} @ {g}  ({'HOLDS' if w<=0 else 'FAILS'})")

if __name__=="__main__":
    run()
    print("--- blowups ---")
    for L,q in [(5,2),(5,3),(5,4),(7,2),(7,3),(9,2)]:
        nn=L*q
        n,E=cycle_blowup(L,q); info=loads(n,E)
        if info is None: continue
        r,m=cand(info)
        print(f"  C{L}[{q}] N={nn}: A={float(r['A']):+.3f} C5={float(r['C5']):+.3f} C6={float(r['C6']):+.3f} C2={float(r['C2_Ofg<=min']):+.3f}")
