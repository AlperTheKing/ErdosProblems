from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

best=None; rows=[]
for nn in range(5,12):
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
            d=analyze_one(B,C)
            if d['sz']==1 and d['mass']==0: continue
            slack=d['deficit']-d['dB']
            row=(slack,g6,nn,C,d)
            rows.append(row)
            if best is None or slack<best[0]: best=row
print('count',len(rows))
print('best',best[0] if best else None, best[1:4] if best else None)
if best:
    slack,g6,nn,C,d=best
    n,E=dec(g6); info=loads(n,E); B=build(info); Cs=set(C)
    print('O',sorted(B['O']),'M',B['M'],'ellv',B['ellv'],'side',info['side'])
    print('C',C,'deficit',d['deficit'],'dB',d['dB'],'mass',d['mass'],'nFC',d['nFC'])
    cross=[e for e in B['Bset'] if (e[0] in Cs)^(e[1] in Cs)]
    print('cross',cross)
    print('v T slack S crossdeg')
    degc={v:0 for v in C}
    for a,b in cross: degc[a if a in Cs else b]+=1
    for v in C: print(v,B['T'][v],B['N']-B['T'][v],B['S'][v],degc[v])
    print('bad edges inside')
    for fi,f in enumerate(B['M']):
        if B['supp'][fi] <= Cs: print(fi,f,'ell',B['ellv'][fi],'p',B['P'][fi])
