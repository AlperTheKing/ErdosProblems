"""EXACT (Fraction) verification of the two rigorous algebraic facts in the water-filling bridge:
 (A) IDENTITY: sum_f C_f = N*I - K exactly, where C_f = diag(D_f) - p_f p_f^T, D_f(v)=N p_f(v)/S(v),
     K = sum_f p_f p_f^T, S(v)=sum_f p_f(v).  [pure algebra, must be EXACT 0 residual]
 (B) EQUIVALENCE: C_f PSD  <=>  sum_v p_f(v)^2 / D_f(v) <= 1  <=> (1/N) sum_v p_f(v) S(v) <= 1
     <=> sum_v p_f(v) S(v) <= N  (ROWSUM-O).
     C_f = diag(D_f) - p_f p_f^T is a diagonal-minus-rank-one matrix on supp(p_f) (D_f(v)>0 there).
     Such a matrix is PSD iff D_f(v)>=0 all v AND sum_v p_f(v)^2/D_f(v) <= 1 (Schur/Sherman-Morrison, exact).
     We verify the scalar  sum_v p_f(v)^2/D_f(v) = (1/N) sum_v p_f(v) S(v)  EXACTLY, and that it is <=1
     iff ROWSUM-O.
 (A) proves rho(K)=rho(O)<=N is EQUIVALENT to 'all C_f PSD' GIVEN the identity (since sum of PSD is PSD,
     and N*I-K PSD <=> rho(K)<=N). So the ONLY remaining gap to a full proof of Gamma<=N^2 is ROWSUM-O.
Run census N<=10 + C5[t] blowups EXACT."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, blow

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; pf={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf[f]={v:F(cnt[v],nf) for v in cnt}
    return pf

def check(info):
    n=info['n']; N=F(n); M=info['M']
    pf=pf_exact(info)
    S=[sum(pf[f].get(v,F(0)) for f in M) for v in range(n)]
    # K exact
    K=[[F(0)]*n for _ in range(n)]
    for f in M:
        d=pf[f]
        for v,pv in d.items():
            for w,pw in d.items():
                K[v][w]+=pv*pw
    # accumulate sum_f C_f
    acc=[[F(0)]*n for _ in range(n)]
    eq_ok=True
    for f in M:
        d=pf[f]
        # D_f(v)=N*p_f(v)/S(v) on supp
        for v,pv in d.items():
            acc[v][v]+= N*pv/S[v]          # diag part
        for v,pv in d.items():
            for w,pw in d.items():
                acc[v][w]-= pv*pw          # -p_f p_f^T
        # (B) scalar: sum_v p_f(v)^2/D_f(v) = sum_v p_f(v)^2 * S(v)/(N p_f(v)) = (1/N) sum_v p_f(v) S(v)
        lhs=sum(pv*pv/(N*pv/S[v]) for v,pv in d.items())   # = (1/N) sum p_f S
        rhs=sum(pv*S[v] for v,pv in d.items())/N
        if lhs!=rhs: eq_ok=False
        # PSD-of-C_f criterion value (must be <=1 for PSD):
        if lhs>1:
            return ('PSDfail', f, lhs)
    # (A) identity: acc should equal N*I-K on supp(S); off-supp (S=0) acc has 0, target N on diag
    idok=True; maxres=F(0)
    for v in range(n):
        for w in range(n):
            tgt = (N if v==w else F(0)) - K[v][w]
            a = acc[v][w]
            if S[v]==0 and v==w:
                # off-support: acc diag 0, target N (K row 0). identity holds 'on support'; pad
                a = a + N
            r=abs(a-tgt)
            if r>maxres: maxres=r
    return ('ok', maxres, eq_ok)

def run(nmin,nmax,limit=None):
    print(f"=== EXACT water-fill identity+equiv census N={nmin}..{nmax} ===")
    ng=0; idmax=F(0); eqbad=0; psdfail=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            r=check(info)
            if r[0]=='PSDfail': psdfail+=1; print('  PSDFAIL',g6,r[1],r[2])
            else:
                _,res,eqok=r
                if res>idmax: idmax=res
                if not eqok: eqbad+=1
    print(f"graphs={ng} | EXACT identity max-residual |sum C_f-(N I-K)|={idmax} | (B)-scalar-eq mismatches:{eqbad} | C_f-PSD(ROWSUM-O) fails:{psdfail}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups EXACT ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        r=check(info)
        print(f"  C5[{t}] N={n}: {r}")
