"""PRECISE strictness mechanism for condition (1).

K_QQ >= 0. Decompose Q into KQQ-irreducible components (strongly connected comps of the
graph i~j iff KQQ[i][j]>0; symmetric so just connected comps). N*I-K_QQ is block-... actually
since components are KQQ-DISCONNECTED, N*I-K_QQ is block-diagonal w.r.t. components. So
det(N*I-K_QQ) = prod over comps det(N*I_C - block_C), and inverse>=0 iff each block is
nonsingular M-matrix.

For each irreducible component C (KQQ restricted to C is irreducible nonneg, or 1x1):
  within-Q row sum at q in C: s[q] := sum_{q' in Q} KQQ[q][q'] = T[q] - leak[q] <= T[q] <= N.
PERRON (irreducible nonneg, Frobenius): rho(block_C) <= max_{q in C} s[q] <= N, with rho(block_C)
  = N STRICTLY IMPOSSIBLE unless s[q] = N for EVERY q in C
  (irreducible nonneg matrix has rho < max-rowsum unless all rowsums equal, and then rho=common rowsum).
  s[q]=N requires T[q]=N AND leak[q]=0 (since T[q]<=N, leak[q]>=0).
So rho(block_C) < N  <=>  NOT all q in C satisfy (T[q]=N and leak[q]=0).

CLAIM to prove: a "critical" component C (all q in C have T[q]=N, leak[q]=0, KQQ-irreducible)
  CANNOT EXIST in a config with O nonempty AND B connected.  (If it could, A would be singular.)

This script:
 (A) verifies the block-diagonal-by-component reduction (det = prod of block dets) EXACTLY.
 (B) for each component, reports whether it is "critical" (all T=N & leak=0). Counts critical comps.
 (C) verifies det(block_C) > 0 for every component (=> nonsingular) EXACTLY.
 (D) reports the GLOBAL r=N-T sum on Q and the leak sum, to see the conservation law.
We expect: ZERO critical components ever (that's the theorem for (1)). Stress to N=22 blowups.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, det_frac, reach_components

def analyze(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    leak=[sum(K[Q[i]][o] for o in O) for i in range(m)]
    r=[F(N)-T[Q[i]] for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    # within-Q rowsum
    s=[sum(KQQ[i][j] for j in range(m)) for i in range(m)]
    # identity check: s[i] == T[Q[i]] - leak[i]
    ident=all(s[i]==T[Q[i]]-leak[i] for i in range(m))
    critical=0; block_det_pos=True; prod=F(1)
    crit_info=[]
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        is_crit = all((r[i]==0 and leak[i]==0) for i in nodes)
        if is_crit: critical+=1; crit_info.append((len(nodes),[Q[i] for i in nodes]))
        block=[[ (F(N) if i==j else F(0)) - KQQ[nodes[i]][nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))]
        bd=det_frac(block); prod*=bd
        if bd<=0: block_det_pos=False
    AQQ=[[ (F(N) if i==j else F(0)) - KQQ[i][j] for j in range(m)] for i in range(m)]
    fulldet=det_frac(AQQ)
    blockprod_ok = (prod==fulldet)
    return dict(N=N,m=m,nO=len(O),ncomp=ncomp,ident=ident,critical=critical,
                crit_info=crit_info,block_det_pos=block_det_pos,blockprod_ok=blockprod_ok,
                fulldet_pos=fulldet>0)

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; crit=0; bad=0; ident_bad=0; bp_bad=0; detbad=0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=analyze(info)
            if d is None: continue
            nt+=1
            if not d['ident']: ident_bad+=1
            if not d['blockprod_ok']: bp_bad+=1
            if not d['block_det_pos']: detbad+=1
            if not d['fulldet_pos']: bad+=1
            if d['critical']>0:
                crit+=1
                if wg is None: wg=(g6,d['crit_info'])
        print(f"  N={nn}(str{stride}): with-O={nt} | CRITICAL-comp graphs={crit}{(' @'+str(wg)) if wg else ''} | "
              f"ident_bad={ident_bad} blockprod_bad={bp_bad} block_det<=0={detbad} fulldet<=0={bad}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== Strictness mechanism: NO critical KQQ-component (all T=N & leak=0) ===")
    for g6,t in [("H?AAF_}",1),("J?AE@`KkH{?",1),("J???E?pNu\\?",2),
                 ("I?BD@g]Qo",2),("J?`@C_W{Ck?",2)]:
        nn,EE=blow(g6,t); info=loads(nn,EE)
        if info:
            d=analyze(info)
            if d:
                print(f"  {g6}[{t}] N={d['N']}: ncomp={d['ncomp']} critical={d['critical']} "
                      f"ident={d['ident']} blockprod_ok={d['blockprod_ok']} block_det_pos={d['block_det_pos']} fulldet_pos={d['fulldet_pos']}")
    run_census(9,7,1)
    run_census(10,10,3)
    run_census(11,11,20)
