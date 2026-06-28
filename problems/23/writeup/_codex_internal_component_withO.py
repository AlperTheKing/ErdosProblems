from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components

worst=None; bad=0; cnt=0; comps=0
for nn in range(5,12):
    nb=0; nc=0
    out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        B=build(info)
        if not B['O']: continue
        for C in components(B['K'],B['n']):
            Cs=set(C)
            if Cs & B['O']: continue
            if len(C)==B['n']: continue
            if all(B['T'][v]==0 for v in C): continue
            nc+=1; comps+=1
            for v in C:
                margin=F(len(C))-B['T'][v]
                cnt+=1
                if margin<0:
                    bad+=1; nb+=1
                    if worst is None or margin<worst[0]: worst=(margin,g6,nn,C,v,B['T'][v],B['O'])
    print('N',nn,'nontriv proper comps',nc,'bad',nb,'worst',worst,flush=True)
print('TOTAL comps',comps,'bad',bad,'cnt',cnt,'worst',worst,flush=True)
