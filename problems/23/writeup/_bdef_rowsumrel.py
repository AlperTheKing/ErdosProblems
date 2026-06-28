"""Precise relationship: boundary-deficit vs ROWSUM-O.
ROWSUM-O (per bad edge f): r(f) = sum_v p_f(v) S(v) <= N,  S(v)=sum_g p_g(v).   [<=> rho(O=P^T P)<=N <=> A=NI-K PSD]
boundary-deficit (per K-comp C disjoint from O): 1_C^T A 1_C >= dB(C).

Logical facts to confirm numerically:
 (i) A PSD (i.e. ROWSUM-O holds) does NOT imply 1_C^T A 1_C >= dB(C): the +dB slack is extra.
     We confirm A is PSD on ALL census graphs (min eig >=0) while measuring 1_C^T A 1_C - dB.
 (ii) boundary-deficit on indicator vectors does NOT control off-indicator directions, so cannot imply A PSD.
     We exhibit that 1_C^T A 1_C >= dB while there exist x with x^T A x possibly small (min eig << dB).
 (iii) Numerically: is there a graph where ROWSUM-O is TIGHT (some r(f)=N) but boundary-deficit slack is large,
       and vice versa? -> independence.
Report: per-graph (max r(f) over f) vs (min over OTHER/Q-only comps of 1_C^T A 1_C - dB), and min eig sign of A
        on small graphs (float ok for eig sign sanity, but report exact 1_C^T A 1_C)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def maxrowsumO(B):
    P=B['P']; S=B['S']; M=B['M']
    best=F(0)
    for fi in range(len(M)):
        v=sum(P[fi].get(x,F(0))*S[x] for x in P[fi])
        if v>best: best=v
    return best

def scan(Nmin,Nmax):
    # collect (N, maxRowsumO/N, min comp-slack 1_C^T A1_C - dB), check correlation/independence
    n_rowsumO_tight=0; n_bd_tight=0; both_tight=0
    examples=[]
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']
            mr=maxrowsumO(B)  # <= N
            comps=components(K,n)
            minslack=None
            for C in comps:
                Cs=set(C)
                if Cs&O: continue
                if len(C)==1 and T[C[0]]==0: continue
                d=analyze_one(B,C)
                s=d['deficit']-d['dB']
                if minslack is None or s<minslack: minslack=s
            rowsumO_tight=(mr==N)
            bd_tight=(minslack is not None and minslack==0)
            if rowsumO_tight: n_rowsumO_tight+=1
            if bd_tight: n_bd_tight+=1
            if rowsumO_tight and bd_tight: both_tight+=1
            # record a case where rowsumO tight but bd slack large (independence) and vice versa
            if rowsumO_tight and minslack is not None and minslack>=2 and len([e for e in examples if e[0]=='rsO-tight,bd-slack'])<3:
                examples.append(('rsO-tight,bd-slack',g6,float(mr),N,float(minslack)))
            if (not rowsumO_tight) and bd_tight and len([e for e in examples if e[0]=='rsO-slack,bd-tight'])<3:
                examples.append(('rsO-slack,bd-tight',g6,float(mr),N,float(minslack)))
        print(f"  N={nn}: rowsumO_tight={n_rowsumO_tight} bd_tight(slack0)={n_bd_tight} both={both_tight}",flush=True)
    print("=== independence examples ===")
    for e in examples: print("  ",e)

if __name__=="__main__":
    scan(5,10)
