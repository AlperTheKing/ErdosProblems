from fractions import Fraction as F
from _h import dec, loads
from _audit_strictness import aqq_data, overloaded
from _audit_stress import blow

print('=== FAST strictness: census N=8,9,10 full + N=11 stride 25; blowups t=2 to N=22 ===',flush=True)
wm=None; sing=0; mb=0; tot=0; zm=0
for nn in range(8,11):
    for g6 in overloaded(nn,1):
        d=aqq_data(loads(*dec(g6)))
        if d is None: continue
        tot+=1
        if d['singular']: sing+=1; print('  SINGULAR',g6,'N=',nn,flush=True)
        mb=max(mb,d['n_boundary'])
        if d['margin']<=0: zm+=1; print('  MARGIN<=0',g6,'N=',nn,'maxrow=',float(d['kqq_rowsum_max']),flush=True)
        if wm is None or d['margin']<wm: wm=d['margin']
for g6 in overloaded(11,25):
    d=aqq_data(loads(*dec(g6)))
    if d is None: continue
    tot+=1
    if d['singular']: sing+=1; print('  SINGULAR',g6,'N=11',flush=True)
    mb=max(mb,d['n_boundary'])
    if d['margin']<=0: zm+=1
    if wm is None or d['margin']<wm: wm=d['margin']
print('  census: tested',tot,'| singular=',sing,'| margin<=0:',zm,'| worst margin(N-maxKQQrow)=',float(wm),'| max #boundary(T=N)=',mb,flush=True)

print('=== blowups t=2 (N<=22) ===',flush=True)
wm2=None; sing2=0; tot2=0; zm2=0; mb2=0
for nn in range(8,12):
    st=1 if nn<=10 else 15
    for g6 in overloaded(nn,st):
        NN,EE=blow(g6,2)
        if NN>22: continue
        info=loads(NN,EE)
        if info is None: continue
        d=aqq_data(info)
        if d is None: continue
        tot2+=1
        if d['singular']: sing2+=1; print('  SINGULAR',g6,'[2] N=',NN,flush=True)
        mb2=max(mb2,d['n_boundary'])
        if d['margin']<=0: zm2+=1; print('  MARGIN<=0',g6,'[2] N=',NN,flush=True)
        if wm2 is None or d['margin']<wm2: wm2=d['margin']
print('  blowups: tested',tot2,'| singular=',sing2,'| margin<=0:',zm2,'| worst margin=',float(wm2) if wm2 is not None else 'na','| max #boundary=',mb2,flush=True)
