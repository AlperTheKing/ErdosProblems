"""Unpack CW-T:  (K T)_v <= N T_v  <=>  sum_f p_f(v)[(O ell)_f - N ell(f)] <= 0  for all v.
Define R_f := (O ell)_f = sum_g ell(g) <p_f,p_g> = <p_f, T>.   (KT)_v = sum_f p_f(v) R_f.
Question A: does the PER-EDGE  R_f <= N ell(f)  hold? (a weighted ROWSUM-O; would give CW-T trivially since p_f>=0)
Question B: if A fails, does the p_f(v)-WEIGHTED-AVG version  sum_f p_f(v) R_f <= N sum_f p_f(v) ell(f)  hold?
Also test CW-S analog:  (K S)_v <= N S_v  <=> sum_f p_f(v)[(O 1)_f - N] <= 0,  (O1)_f = sum_v p_f(v)S(v) (= ROWSUM-O LHS).
  So CW-S = p_f(v)-weighted-avg of (ROWSUM-O residual) <= 0. ROWSUM-O = each residual <=0 (stronger).
Report: max_f (R_f - N ell(f))/(N ell(f))  [A], and max_f (O1_f - N) [ROWSUM-O], and CW-T/CW-S maxes.
EXACT Fractions, census N<=11 + blowups."""
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
    # O exact
    O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            s=F(0)
            di=pf[i]
            for v,pv in di.items():
                pw=pf[j].get(v)
                if pw is not None: s+=pv*pw
            O[i][j]=s
    ellv=[F(ell[M[g]]) for g in range(m)]
    R=[sum(O[i][j]*ellv[j] for j in range(m)) for i in range(m)]   # R_f=(O ell)_f
    O1=[sum(O[i][j] for j in range(m)) for i in range(m)]          # (O1)_f = ROWSUM-O LHS
    return n,N,m,pf,O,ellv,R,O1

def analyze(info):
    n,N,m,pf,O,ellv,R,O1=build(info)
    # Question A: R_f <= N ell(f)
    A_max=F(0); A_fail=0
    for f in range(m):
        if ellv[f]==0: continue
        resid=(R[f]-F(N)*ellv[f])
        rr=resid/(F(N)*ellv[f])
        if resid>0: A_fail+=1
        if rr>A_max: A_max=rr
    # ROWSUM-O: O1_f <= N
    RS_max=F(0); RS_fail=0
    for f in range(m):
        if O1[f]>F(N): RS_fail+=1
        d=O1[f]-F(N)
        if d>RS_max: RS_max=d
    return A_fail,A_max,RS_fail,RS_max,m

def run():
    print("=== Question A (R_f=(O ell)_f <= N ell(f)) vs ROWSUM-O, exact ===")
    Afail=0;Amax=F(0);Awg=None;RSfail=0;RSmax=F(0);RSwg=None;ng=0
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            af,am,rf,rm,m=analyze(info)
            Afail+=af; RSfail+=rf
            if am>Amax: Amax=am; Awg=(g6,nn)
            if rm>RSmax: RSmax=rm; RSwg=(g6,nn)
    print(f"  census graphs={ng}")
    print(f"  [A] R_f<=N ell(f): fail edges={Afail} worst (R-N ell)/(N ell)={float(Amax):.5f}@{Awg}")
    print(f"  [ROWSUM-O] O1_f<=N: fail edges={RSfail} worst (O1-N)={float(RSmax):.5f}@{RSwg}")

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

if __name__=="__main__":
    run()
    print("--- blowups: does A hold there too? ---")
    for L in [5,7,9]:
        for q in range(2,5):
            nn=L*q
            if nn>26: continue
            n,E=cycle_blowup(L,q); info=loads(n,E)
            if info is None: continue
            af,am,rf,rm,m=analyze(info)
            print(f"  C{L}[{q}] N={nn}: [A]fail={af} (R-Nell)/(Nell)max={float(am):.5f} | [RSO]fail={rf} max={float(rm):.5f}")
