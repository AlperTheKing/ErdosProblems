from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def inc_cut(info):
    n=info['n']; inc=[F(0) for _ in range(n)]
    for f in info['M']:
        Ps=info['cyc'][f]; nf=len(Ps); sh=F(1,nf)
        for P in Ps:
            for i,v in enumerate(P):
                inc[v] += sh if (i==0 or i==len(P)-1) else 2*sh
    return inc

def test(Nmax=11):
    worst=None; bad=0; cnt=0
    for nn in range(5,Nmax+1):
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        nb=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            inc=inc_cut(info); T=info['T']; N=n
            degB=[0]*n
            for a,b in info['Bset']:
                degB[a]+=1; degB[b]+=1
            for v in range(n):
                margin=(N-T[v]) - (F(degB[v])-inc[v])
                cnt+=1
                if margin<0:
                    bad+=1; nb+=1
                    if worst is None or margin<worst[0]: worst=(margin,g6,v,N,T[v],degB[v],inc[v])
        print('N',nn,'bad',nb,'running worst',worst)
    print('TOTAL bad',bad,'cnt',cnt,'worst',worst)
if __name__=='__main__': test(11)
