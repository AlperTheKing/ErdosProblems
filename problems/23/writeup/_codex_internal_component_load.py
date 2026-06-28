from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components

def test(Nmax=11):
    worst=None; bad=0; cnt=0
    for nn in range(5,Nmax+1):
        nb=0
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info)
            for C in components(B['K'],B['n']):
                Cs=set(C)
                if Cs & B['O']: continue
                for v in C:
                    margin=F(len(C))-B['T'][v]
                    cnt+=1
                    if margin<0:
                        bad+=1; nb+=1
                        if worst is None or margin<worst[0]: worst=(margin,g6,nn,C,v,B['T'][v],B['O'])
        print('N',nn,'bad',nb,'worst',worst,flush=True)
    print('TOTAL bad',bad,'cnt',cnt,'worst',worst,flush=True)
if __name__=='__main__': test(11)
