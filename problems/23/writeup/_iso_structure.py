"""Understand WHY link-I isoperimetry |A|<=dB(A) holds for overload superlevels A={T>=c},c>N.
Hypotheses:
 (H1) A is B-independent (no cut edge inside A) => |A|<=dB(A) trivial (min B-deg>=1).
      report e_B(A,A) (internal cut edges of A) -- is it 0?
 (H2) per-vertex T(v) <= N*d_B(v)/2 ?  (clean per-vertex load-vs-degree bound)
 (H3) per-vertex T(v) <= N * (#geodesic-cycles-thru-v adjusted)...
Report census N<=11: max e_B(A,A) over overload superlevels; and max ratio T(v)/(N*d_B(v)/2)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def analyze(info):
    n=info['n']; T=info['T']; N=n
    adj=info['adj']; side=info['side']
    dB=[sum(1 for w in adj[v] if side[w]!=side[v]) for v in range(n)]   # B-degree
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    vals=sorted(set(v for v in o if v>0))
    max_int=0; worst_lvl=None
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        eBAA=sum(1 for (a,b) in info['Bset'] if a in A and b in A)
        if eBAA>max_int: max_int=eBAA; worst_lvl=(float(v),sorted(A))
    # per-vertex T(v) vs N*dB/2
    worst_ratio=None; wv=None
    for v in range(n):
        if dB[v]>0:
            r=T[v]/(F(N*dB[v],2))
            if worst_ratio is None or r>worst_ratio: worst_ratio=r; wv=(v,float(T[v]),dB[v])
    return max_int,worst_lvl,worst_ratio,wv

def run(Nmax,Nmin=8):
    print("--- link-I structure: internal cut edges of overload superlevels + T(v) vs N*dB/2 ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; gmax_int=0; gmax_ratio=None; gi_g=None; gr_g=None; nonindep=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; mi,wl,wr,wv=analyze(info)
            if mi>0: nonindep+=1
            if mi>gmax_int: gmax_int=mi; gi_g=(g6,wl)
            if wr is not None and (gmax_ratio is None or wr>gmax_ratio): gmax_ratio=wr; gr_g=(g6,wv)
        print(f"  N={nn}: cfg={nt} | overload-superlevels NOT B-indep: {nonindep} (max internal cut-edges={gmax_int} @ {gi_g}) | max T(v)/(N*dB/2)={float(gmax_ratio):.4f} @ {gr_g}",flush=True)

if __name__=="__main__":
    run(11,8)
