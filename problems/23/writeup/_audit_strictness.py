"""Adversarial probe of the WEAKEST link: condition (1) strictness rho(K_QQ) < N (Aqq nonsingular).
The proposed proof only gives rho(K_QQ) <= N (Perron row-sum). Strictness is hand-waved.
Risks:
 (a) some q in Q has T[q] = N exactly (boundary), so K_QQ-rowsum could equal N at that q.
 (b) Aqq singular (rho(K_QQ)=N) => Schur undefined.
We scan census+blowups for: min margin (N - rho(K_QQ)) via min positive eigenvalue of Aqq (float, just to locate),
exact #q with T[q]==N, and exact det(Aqq)==0 occurrences. Also: how SMALL does det(Aqq) / min-eig get
on overloaded blow-ups (does it approach singular as we push extremal-like structure)?"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _audit_stress import build_K, blow
from _schur_spec import matinv_frac

def aqq_data(info):
    K,T,N,n=build_K(info)
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    nq=len(Q)
    Aqq=[[(F(N) if Q[i]==Q[j] else F(0))-K[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    Inv=matinv_frac(Aqq)
    singular = Inv is None
    n_boundary = sum(1 for q in Q if T[q]==N)
    # exact KQQ row sums; max
    kqq_rowsum_max = max((sum(K[Q[i]][Q[j]] for j in range(nq)) for i in range(nq)), default=F(0))
    # margin N - max KQQ rowsum (lower bounds N-rho(K_QQ) is NOT valid; rho<=rowsum. margin>0 => rho could still =N? no:
    # rho(K_QQ) <= max rowsum. If max rowsum < N then rho < N strictly. So this margin>0 PROVES strictness!)
    margin = F(N) - kqq_rowsum_max
    return dict(N=N,nq=nq,singular=singular,n_boundary=n_boundary,kqq_rowsum_max=kqq_rowsum_max,margin=margin)

def overloaded(nn,stride=1):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
    ov=[]
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        if any(t>n for t in info['T']): ov.append(g6)
    return ov

if __name__=="__main__":
    print("=== strictness probe: rho(K_QQ) < N via max-K_QQ-rowsum margin; #boundary T[q]=N; singular Aqq ===",flush=True)
    worst_margin=None; sing=0; max_boundary=0; tot=0; zeromargin=0
    # census
    for nn in range(7,12):
        st=1 if nn<=10 else 3
        for g6 in overloaded(nn,st):
            d=aqq_data(loads(*dec(g6)))
            if d is None: continue
            tot+=1
            if d['singular']: sing+=1; print(f"  SINGULAR Aqq census {g6} N={nn}",flush=True)
            max_boundary=max(max_boundary,d['n_boundary'])
            if d['margin']<=0: zeromargin+=1; print(f"  MARGIN<=0 (rowsum>=N) {g6} N={nn}: max KQQ rowsum={float(d['kqq_rowsum_max'])}",flush=True)
            if worst_margin is None or d['margin']<worst_margin: worst_margin=d['margin']
    print(f"  census N<=11: tested {tot} | singular Aqq={sing} | rowsum>=N cases={zeromargin} | worst (N-maxKQQrowsum)={float(worst_margin) if worst_margin is not None else 'na'} | max #boundary(T[q]=N)={max_boundary}",flush=True)
    # blowups
    print("=== blow-ups t=2 (N<=22) ===",flush=True)
    wm2=None; sing2=0; zm2=0; tot2=0; mb2=0
    for nn in range(8,12):
        for g6 in overloaded(nn, 1 if nn<=10 else 10):
            NN,EE=blow(g6,2)
            if NN>22: continue
            info=loads(NN,EE)
            if info is None: continue
            d=aqq_data(info)
            if d is None: continue
            tot2+=1
            if d['singular']: sing2+=1; print(f"  SINGULAR Aqq blowup {g6}[2] N={NN}",flush=True)
            mb2=max(mb2,d['n_boundary'])
            if d['margin']<=0: zm2+=1; print(f"  MARGIN<=0 blowup {g6}[2] N={NN}: maxKQQrowsum={float(d['kqq_rowsum_max'])}",flush=True)
            if wm2 is None or d['margin']<wm2: wm2=d['margin']
    print(f"  blowups: tested {tot2} | singular={sing2} | rowsum>=N={zm2} | worst (N-maxKQQrowsum)={float(wm2) if wm2 is not None else 'na'} | max #boundary={mb2}",flush=True)
