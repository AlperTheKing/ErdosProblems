"""Decisive: does O-K-SUPPORT / the Schur certificate / SPEC hold on the glued construction isl5+gad15 br(0,5) N=20
where DISCONNECTED-K-SELFCAP failed? If O-K-SUPPORT fails here, I propagated a false claim to Codex."""
import numpy as np
from fractions import Fraction as F
from _h import loads
from _bdef_construct import Cn, union_disjoint, mycielski
from _oksupport import ok_viol
from _satzmu_conn import struct_for_side, kcomponents
from _schur_spec import test as schur_test, pf_exact

g15=mycielski(7,Cn(7))
n,E=union_disjoint((5,Cn(5)),g15); E=E+[(0,5)]
info=loads(n,E); N=info['n']; T=info['T']
O=[v for v in range(N) if T[v]>N]
print("isl5+gad15 br(0,5) N=20: loads gamma-min cut")
print("  O=",O," Gamma=",float(info['G']))
v=ok_viol(N,info['adj'],info['side'])
print("  O-K-SUPPORT violations:", v if v else "NONE")
st=struct_for_side(N,info['adj'],info['side']); M,ell,Tt,mu,cyc=st
comp,find=kcomponents(N,cyc)
poscomps=[sorted([w for w in vs if Tt[w]>0]) for root,vs in comp.items()]
poscomps=[c for c in poscomps if c]
print("  #positive-K components:", len(poscomps))
for c in poscomps:
    print("     comp",c[:8],"... size",len(c),"meets O?",bool(set(c)&set(O)),"sample T",[float(Tt[w]) for w in c[:3]])
r=schur_test(info)
print("  Schur cert:", r[0], "| fails=",r[1].get('fails'),"inv_neg=",r[1].get('inv_neg'),"offdiag_pos=",r[1].get('offdiag_pos'),"minrow=",float(r[1]['minrow']) if 'minrow' in r[1] else None)
P,M2,ell2,nn=pf_exact(info)
K=np.zeros((nn,nn))
for d in P:
    vv=np.zeros(nn)
    for a,b in d.items(): vv[a]=float(b)
    K+=np.outer(vv,vv)
rho=max(np.linalg.eigvalsh(K))
print("  rho(K)=",rho," N=",N," SPEC (rho<=N)?",rho<=N+1e-9)
