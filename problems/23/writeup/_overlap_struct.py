"""Triangle-free should limit pairwise geodesic overlap <p_f,p_g>. Probe:
 - max <p_f,p_g> for f!=g, and the structure (do two distinct bad-edge geodesics share many vertices?).
 - Menger/shortest: two SHORTEST odd cycles in a tri-free graph can't share a long path without a chord.
 - KEY candidate (would give rho(O)<=N via Gershgorin-like if overlaps small):
     For each f: O_ff + sum_{g!=f} <p_f,p_g> <= N  (= ROWSUM-O).
   Off-diagonal mass sum_{g!=f}<p_f,p_g> = C(f)-O_ff. Compare to N-O_ff.
 - Does the # of g with <p_f,p_g>>0 (geodesic-overlapping edges) times max-overlap stay <= N-O_ff?
 - Compute the 'overlap graph' degree and max overlap per pair, look for a clean cap like <p_f,p_g><=1 (FALSE?)
   or <p_f,p_g> <= min(||p_f||^2,||p_g||^2) (CS, trivial).
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def ip(a,b):
    s=F(0)
    for w,av in a.items():
        bv=b.get(w)
        if bv is not None: s+=av*bv
    return s

def run(nmin,nmax,limit=None):
    print("=== off-diagonal overlap structure ===")
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        max_pair=F(0); mp=None
        # candidate: max over f of sum_{g!=f}<p_f,p_g>  vs N - O_ff
        worst_off=F(-10); wo=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; m=len(M)
            pfs=[pf_vec(info,f) for f in M]
            O=[[ip(pfs[i],pfs[j]) for j in range(m)] for i in range(m)]
            for i in range(m):
                offsum=sum(O[i][j] for j in range(m) if j!=i)
                diag=O[i][i]
                # ROWSUM-O: diag+offsum<=N
                resid=(diag+offsum)-n
                if resid>worst_off: worst_off=resid; wo=(g6,M[i],float(diag),float(offsum),n)
                for j in range(m):
                    if j!=i and O[i][j]>max_pair: max_pair=O[i][j]; mp=(g6,M[i],M[j],float(O[i][j]))
        print(f"  N={nn}: max <p_f,p_g> (f!=g)={float(max_pair):.4f} @ {mp} | worst ROWSUM resid={float(worst_off):+.4f} (diag,off)@{wo}",flush=True)

if __name__=="__main__":
    run(7,10,limit=None)
