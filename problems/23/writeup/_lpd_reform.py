"""Verify (LPD') <T-N,y> <= sum_f sum_{i<j}(sqrt(w_fi)-sqrt(w_fj))^2 for random y + indicators (=(LPD)),
and the ray-lemma S(v)<=N census-wide. w_{f,i}=sum_{v in I_i(f)} y_v p_f(v)."""
import numpy as np, subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads
from _layerprice import layers_of

def lpd_prime(info, y):
    n=info['n']; M=info['M']; T=info['T']; N=n
    lhs=sum(y[v]*(float(T[v])-N) for v in range(n))
    rhs=0.0
    for f in M:
        lay,pf,h=layers_of(info,f)
        w=[sum(y[v]*pf[v] for v in lay[i]) for i in range(h+1)]
        sq=[np.sqrt(max(x,0.0)) for x in w]
        for i in range(h+1):
            for j in range(i+1,h+1):
                rhs+=(sq[i]-sq[j])**2
    return lhs,rhs

def Svec(info):
    S={}
    for f in info['M']:
        Ps=info['cyc'][f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        for v,c in cnt.items(): S[v]=S.get(v,F(0))+F(c,nf)
    return S

def main():
    print("=== (LPD') lhs<=rhs check (random y + indicators) ===")
    rng=random.Random(1)
    for g6 in ["I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); worst=None; wy=None
        ys=[[1.0]*n]
        ys+=[[1.0 if v==k else 0.0 for v in range(n)] for k in range(n)]
        ys+=[[rng.random() for _ in range(n)] for _ in range(30)]
        for y in ys:
            lhs,rhs=lpd_prime(info,y)
            if worst is None or (lhs-rhs)>worst: worst=lhs-rhs
        tag="OK(<=0)" if worst<=1e-7 else "FAILS"
        print(f"  {g6}: max(lhs-rhs) over {len(ys)} y = {worst:+.5f}  ({tag})")
    print("--- ray-lemma S(v)<=N census ---")
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if nn==11: out=out[::20]
        nt=0; bad=0; mx=None; mg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; S=Svec(info); m=max(S.values())
            if m>nn: bad+=1
            if mx is None or m>mx: mx=m; mg=g6
        print(f"  N={nn}: cfg={nt} | S(v)>N count:{bad} | max S(v)={float(mx):.3f} ratio={float(mx)/nn:.3f} @{mg}",flush=True)

if __name__=="__main__":
    main()
