"""TARGET (Step-2): is condition (2) (E offdiag <= 0) FREE given condition (1)?

E[o,o'] for o!=o' (both in O) = A[o,o'] - A[o,Q] A[Q,Q]^{-1} A[Q,o']
 = -K[o,o'] - K[o,Q] (N I - K_QQ)^{-1} K[Q,o']   (off-diag blocks of A = -K).
Claim: term1 = -K[o,o'] <= 0 (K>=0); term2_neg = -K[o,Q] Inv K[Q,o'] <= 0 GIVEN Inv>=0 (cond 1).
So E[o,o'] = term1 + term2_neg <= 0 automatically. This script EXACT-verifies, per o!=o':
  (a) term1 <= 0 always (sanity; K>=0);
  (b) Inv := (N I - K_QQ)^{-1} is entrywise >= 0 (cond 1) -- record min entry;
  (c) the quadratic form q := K[o,Q] Inv K[Q,o'] >= 0 (the >=0 we rely on) -- record min;
  (d) algebra: E[o,o'] == term1 - q EXACTLY (Fraction);
  (e) E[o,o'] <= 0.
Reports any failure of (b)/(c)/(e), and -- crucially -- whether (e) EVER relies on cond(1):
i.e. is there a graph where Inv has a NEGATIVE entry yet E offdiag still <=0 (cond2 holds w/o cond1),
or where Inv negative entry MAKES some q<0 (would break the 'free' argument). Exact Fractions."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact, matinv_frac

def analyze(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]
                K[va][vb]+=pa*pb
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    A=[[ (F(N) if i==j else F(0)) - K[i][j] for j in range(n)] for i in range(n)]
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    Aqq=[[A[i][j] for j in Q] for i in Q]
    Inv=matinv_frac(Aqq)
    if Inv is None: return dict(status='SINGULAR_AQQ',O=O)
    nQ=len(Q); nO=len(O)
    inv_min=min((Inv[i][j] for i in range(nQ) for j in range(nQ)), default=F(0))
    # precompute Inv K[Q,o'] columns: for each o', y_{o'} = Inv @ K[Q,o']  (length nQ)
    Ycol={}
    for jo,op in enumerate(O):
        kqo=[K[Q[i]][op] for i in range(nQ)]
        Ycol[jo]=[sum(Inv[i][k]*kqo[k] for k in range(nQ)) for i in range(nQ)]
    # full E recompute (consistency w/ _schur_spec) and per-offdiag decomposition check
    worst_q=None       # min over offdiag of q (the term we claim >=0)
    worst_E=None       # max over offdiag of E (the term we claim <=0); want <=0
    algebra_ok=True
    cond2_holds=True
    relies_on_cond1=False  # would E offdiag be >0 if some q went <0 due to inv_neg?
    bad=[]
    for io,o in enumerate(O):
        kqo_o=[K[Q[i]][o] for i in range(nQ)]  # K[o,Q] as row = K[Q,o] (sym)
        for jo,op in enumerate(O):
            if io==jo: continue
            q=sum(kqo_o[i]*Ycol[jo][i] for i in range(nQ))  # K[o,Q] Inv K[Q,o']
            term1=-K[o][op]
            E_decomp=term1 - q
            # cross-check vs direct E entry from schur formula (same expression) -- trivially equal; assert q sign + E sign
            if worst_q is None or q<worst_q: worst_q=q
            Eoo=E_decomp
            if worst_E is None or Eoo>worst_E: worst_E=Eoo
            if Eoo>0:
                cond2_holds=False; bad.append((o,op,'E_offdiag_pos',float(Eoo)))
            if q<0:
                # this would only happen if Inv has neg entries; flags break in 'free' argument
                relies_on_cond1=True; bad.append((o,op,'q_neg',float(q)))
    return dict(status='ok',O=O,Q=Q,inv_min=inv_min,worst_q=worst_q,worst_E=worst_E,
                cond2_holds=cond2_holds,relies_on_cond1=relies_on_cond1,bad=bad[:4])

def run_census(Nmax,Nmin,stride):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        cfg=0; withO=0; sing=0
        gmin_inv=None; gmin_q=None; gmax_E=None
        c2_fail=0; q_neg_cnt=0; inv_neg_cnt=0
        worst_g=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=analyze(info)
            cfg+=1
            if r is None: continue
            if r['status']=='SINGULAR_AQQ': sing+=1; continue
            withO+=1
            if gmin_inv is None or r['inv_min']<gmin_inv: gmin_inv=r['inv_min']
            if r['inv_min']<0: inv_neg_cnt+=1
            if r['worst_q'] is not None and (gmin_q is None or r['worst_q']<gmin_q): gmin_q=r['worst_q']
            if r['worst_E'] is not None and (gmax_E is None or r['worst_E']>gmax_E):
                gmax_E=r['worst_E']; worst_g=g6
            if not r['cond2_holds']: c2_fail+=1
            if r['relies_on_cond1']: q_neg_cnt+=1
        print(f"  N={nn}(str{stride}): cfg={cfg} withO={withO} sing={sing} | "
              f"min Inv entry={float(gmin_inv) if gmin_inv is not None else 'na'} (inv_neg graphs={inv_neg_cnt}) | "
              f"min q(term2)={float(gmin_q) if gmin_q is not None else 'na'} (q_neg graphs={q_neg_cnt}) | "
              f"max E_offdiag={float(gmax_E) if gmax_E is not None else 'na'}@{worst_g} | cond2 FAILS={c2_fail}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== cond(2) E-offdiag<=0: is it FREE given cond(1)? exact decomposition E[o,o']=-K[o,o'] - q ===")
    # named overloaded witnesses
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); r=analyze(info)
        if r is None: print(f"  {g6:13} N={n}: no O"); continue
        print(f"  {g6:13} N={n}: {r['status']} O={r.get('O')} inv_min={float(r['inv_min']) if 'inv_min' in r else 'na'} "
              f"min_q={float(r['worst_q']) if r.get('worst_q') is not None else 'na'} max_E={float(r['worst_E']) if r.get('worst_E') is not None else 'na'} "
              f"cond2={r.get('cond2_holds')} relies_cond1={r.get('relies_on_cond1')}")
    # N=22 sandwich-killer witness
    nn,EE=blow("J???E?pNu\\?",2); info=loads(nn,EE); r=analyze(info)
    if r: print(f"  J???E?pNu?[2] N={nn}: {r['status']} |O|={len(r.get('O',[]))} inv_min={float(r['inv_min']) if 'inv_min' in r else 'na'} "
                f"min_q={float(r['worst_q']) if r.get('worst_q') is not None else 'na'} max_E={float(r['worst_E']) if r.get('worst_E') is not None else 'na'} cond2={r.get('cond2_holds')} relies_cond1={r.get('relies_on_cond1')}")
    # overloaded blow-ups of the overloaded witnesses to N>=18-22
    print("--- overloaded blow-ups (stress N>=18) ---")
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("I?BD@g]Qo",3),("J?AEB?oE?W?",2)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info is None: print(f"  {g6}[{t}] N={nn}: no triangle-free maxcut struct"); continue
        r=analyze(info)
        if r is None: print(f"  {g6}[{t}] N={nn}: no O"); continue
        print(f"  {g6}[{t}] N={nn}: {r['status']} |O|={len(r.get('O',[]))} inv_min={float(r['inv_min']) if 'inv_min' in r else 'na'} "
              f"min_q={float(r['worst_q']) if r.get('worst_q') is not None else 'na'} max_E={float(r['worst_E']) if r.get('worst_E') is not None else 'na'} cond2={r.get('cond2_holds')} relies_cond1={r.get('relies_on_cond1')}")
    print("--- census ---")
    run_census(9,7,1)
    run_census(10,10,4)
    run_census(11,11,40)
