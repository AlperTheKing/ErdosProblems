"""Verify the PRECISE statement underpinning the irreducible-case proof:
   The K-graph restricted to the load-bearing set L={v: T[v]>0} is CONNECTED (=> K|_L irreducible).
If true for a config with O nonempty, the irreducible-case theorem proves condition (1) for it.
Report any config where K|_L is disconnected (would be outside the proven case)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K

def kconn_on_load(K,T,n):
    L=[v for v in range(n) if T[v]>0]
    if not L: return True,0
    Lset=set(L); start=L[0]; seen={start}; st=[start]
    while st:
        u=st.pop()
        for v in L:
            if v not in seen and K[u][v]>0: seen.add(v); st.append(v)
    return len(seen)==len(L), len(L)

def run(Nmax,Nmin=7):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; disc=0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,O,Q,N,_=build_K(info)
            if not O: continue
            nt+=1
            conn,_=kconn_on_load(K,T,n)
            if not conn:
                disc+=1
                if wg is None: wg=g6
        print(f"  N={nn}: with-O={nt} | K|_load DISCONNECTED={disc}{(' ex='+wg) if wg else ''} (0 => irreducible-case proof covers all)",flush=True)

if __name__=="__main__":
    print("=== K-graph on load-bearing set {T>0} connected? (irreducible-case coverage) ===")
    run(11,7)
