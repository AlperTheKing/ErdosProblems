"""Inspect the COMP_NO_LEAK cases: a K_QQ-component with no leakage to O.
We want to know: is N*I-K_QQ still nonsingular there (det>0)? If yes, WHY (what gives strictness)?
The candidate mechanism: within a no-leak component, row sums of K_QQ equal T[q], but is T[q]<N
strictly for some q in the component? (i.e. r_Q>0 somewhere in the component, with KQQ irreducible
on that component => Perron strict). Or maybe T[q]=N for ALL q in component => then need another reason."""
from fractions import Fraction as F
from _h import dec, GENG, loads
from _cond1_proof import build_K, det_frac, reach_components
from _schur_spec import matinv_frac

def inspect(g6, blowt=1):
    n,E=dec(g6)
    if blowt>1:
        EE=[]
        for (a,b) in E:
            for i in range(blowt):
                for j in range(blowt): EE.append((a*blowt+i,b*blowt+j))
        n,E=n*blowt,EE
    info=loads(n,E)
    K,T,O,Q,N,nn=build_K(info)
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    leak=[sum(K[Q[i]][o] for o in O) for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    r=[F(N)-T[Q[i]] for i in range(m)]
    print(f"g6={g6} blow={blowt} N={N} |Q|={m} |O|={len(O)} ncomp={ncomp}")
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        c_leak=any(leak[i]>0 for i in nodes)
        c_allr0=all(r[i]==0 for i in nodes)
        rvals=[float(r[i]) for i in nodes]
        leakvals=[float(leak[i]) for i in nodes]
        # det of A_QQ restricted to this component (the block)
        block=[[ (F(N) if i==j else F(0)) - KQQ[nodes[i]][nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))]
        d=det_frac(block)
        # max KQQ-rowsum within component (full row, includes other-component entries? no, components are
        # KQQ-disconnected so cross entries are 0). within-comp rowsum:
        rs=[sum(KQQ[i][j] for j in range(m)) for i in nodes]  # full KQQ rowsum
        print(f"  comp{c}: size={len(nodes)} leak={c_leak} all_r=0?{c_allr0} det_block_pos={d>0} "
              f"r={rvals} leak={leakvals} KQQrowsums={[float(x) for x in rs]}")
    # full det
    AQQ=[[ (F(N) if i==j else F(0)) - KQQ[i][j] for j in range(m)] for i in range(m)]
    print(f"  full det>0: {det_frac(AQQ)>0}; inv>=0: {matinv_frac(AQQ) is not None and all(x>=0 for row in matinv_frac(AQQ) for x in row)}")

if __name__=="__main__":
    inspect("H?AAF_}")          # N=9 fail
    inspect("J?AE@`KkH{?")      # N=11 fail
