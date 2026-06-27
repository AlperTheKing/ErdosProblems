"""GPT's diagnostic: the LOCAL SUPPORT-COUPLE (LSC):  for all F subset M,  sum_{z in S_F} u(z) >= 2 sum_{z in S_F, T>N} o(z),
where S_f = union of f's shortest B-geodesic cycles, S_F = union over f in F. Equivalently min_F sum_{z in S_F} w(z) >= 0,
w(z)=u(z)=(N-T(z))_+ if underloaded, -2 o(z)=-2(T(z)-N) if overloaded, 0 if neutral. LSC => SH => EDGE-Hall => COUPLE.
Brute over F (|M| small) or greedy. If LSC holds census-wide, the proof target is clean (per GPT)."""
from itertools import combinations
import subprocess
from census_GPI import dec, GENG
from _ph_mincut import loads

def lsc_min(info):
    n=info['n']; T=info['T']; M=info['M']; cyc=info['cyc']; N=n
    w={};
    for z in range(n):
        if T[z]<N: w[z]=float(N-T[z])
        elif T[z]>N: w[z]=-2.0*float(T[z]-N)
        else: w[z]=0.0
    Sf=[set(z for C in cyc[f] for z in C) for f in M]
    m=len(M)
    best=0.0  # F=empty gives 0; we want min over nonempty too
    if m<=18:
        for r in range(1,m+1):
            for comb in combinations(range(m),r):
                S=set();
                for i in comb: S|=Sf[i]
                val=sum(w[z] for z in S)
                if val<best: best=val
    else:
        # greedy: start empty, add edge that most decreases the union-w
        S=set(); cur=0.0; used=[False]*m
        while True:
            bi=-1; bd=0.0
            for i in range(m):
                if used[i]: continue
                ns=S|Sf[i]; nv=sum(w[z] for z in ns)
                if nv-cur<bd: bd=nv-cur; bi=i
            if bi<0: break
            used[bi]=True; S|=Sf[bi]; cur=sum(w[z] for z in S); best=min(best,cur)
    return best

def run_named():
    fails=["I?BD@g]Qo","J?AADagROl?","J?ABAqoeaX?","J??CE?{{?]?"]
    print("=== LSC on PH-failing + binding graphs (min_F sum_{S_F} w ; >=0 means LSC holds) ===")
    for g6 in fails:
        n,E=dec(g6); info=loads(n,E)
        print(f"  {g6:13} N={n} | LSC min = {lsc_min(info):.3f}  ({'HOLDS' if lsc_min(info)>=-1e-9 else 'VIOLATED'})")

def run_census(Nmax,Nmin=8):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=viol=0; worst=0.0; wg=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; mn=lsc_min(info)
            if mn<worst: worst=mn; wg=g6
            if mn<-1e-9: viol+=1
        print(f"  N={nn}: configs={nt} | LSC violations={viol} | worst min_F sum w = {worst:.3f} ({wg})",flush=True)

if __name__=="__main__":
    run_named()
    run_census(11,8)
