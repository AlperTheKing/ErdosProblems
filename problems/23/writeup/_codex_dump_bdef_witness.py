from fractions import Fraction as F
from _h import dec, loads
from _bdef_theory import build, components, analyze_one

g6='I??CABoNo'
n,E=dec(g6); info=loads(n,E); B=build(info)
print('g6',g6,'n',n,'side',B['N'],'M',B['M'],'ellv',B['ellv'],'Bedges',len(B['Bset']))
print('O',sorted(B['O']))
for C in components(B['K'],B['n']):
    Cs=set(C)
    if Cs & B['O']: continue
    d=analyze_one(B,C)
    if d['sz']==1 and d['mass']==0: continue
    cross=[(a,b) for (a,b) in B['Bset'] if (a in Cs)^(b in Cs)]
    degc={v:0 for v in C}
    for a,b in cross:
        degc[a if a in Cs else b]+=1
    slack={v:B['N']-B['T'][v] for v in C}
    print('\nC',C,'sz',d['sz'],'mass',d['mass'],'deficit',d['deficit'],'dB',d['dB'],'nFC',d['nFC'],'bd_ok',d['bd_ok'])
    print('cross',cross)
    print('v: T slack crossdeg S')
    for v in C:
        print(v, B['T'][v], slack[v], degc[v], B['S'][v])
    print('bad edges inside:')
    for fi,f in enumerate(B['M']):
        if B['supp'][fi] <= Cs:
            print(fi,f,'ell',B['ellv'][fi],'supp',sorted(B['supp'][fi]),'p',B['P'][fi])
