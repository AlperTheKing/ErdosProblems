"""Hard stress of Codex's supersolution phi: full census N=11 exact + overloaded census-graph blow-ups (t=2).
Watch the shrinking min phi(active) -- must stay >0. Report any phi<0 or Kphi>Nphi."""
import subprocess
from _h import dec, GENG, loads
from _superphi import test, blow

# full N=11
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
nt=0; fails=0; minA=None; worstB=None; wg=None
for g6 in out:
    n,E=dec(g6); info=loads(n,E)
    if info is None: continue
    nt+=1; d=test(info)
    if d['fails']:
        fails+=1
        if wg is None: wg=(g6,d['fails'])
    if d['minphi_active'] is not None and (minA is None or d['minphi_active']<minA): minA=d['minphi_active']
    if worstB is None or d['maxB']>worstB: worstB=d['maxB']
    if nt%12000==0: print(f"  ...N11 {nt} done fails={fails} minphiA={float(minA)} maxB={float(worstB)}",flush=True)
print(f"FULL N=11 phi: cfg={nt} FAILS={fails}{' @'+str(wg) if wg else ''} min phi(active)={float(minA)} max(Kphi-Nphi)={float(worstB)}",flush=True)

# overloaded census-graph blow-ups t=2 (N<=22)
print("--- overloaded census-graph blow-ups t=2 ---")
ov=[]
for nn in (9,10,11):
    g=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in g:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        if test(info)['hasO']: ov.append((nn,g6))
        if len(ov)>=50: break
    if len(ov)>=50: break
bad=0; minAb=None
for nn0,g6 in ov[:50]:
    nn,EE=blow(g6,2)
    if nn>22: continue
    info=loads(nn,EE)
    if info is None: continue
    d=test(info)
    if d['fails']: bad+=1; print(f"  PHI FAIL {g6}[2] N={nn}: {d['fails']}",flush=True)
    if d['minphi_active'] is not None and (minAb is None or d['minphi_active']<minAb): minAb=d['minphi_active']
print(f"overloaded blow-ups t=2 ({len(ov[:50])} bases): phi FAILS={bad} | min phi(active)={float(minAb) if minAb is not None else 'na'}",flush=True)
