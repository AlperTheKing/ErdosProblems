"""Extract exact ingredients of the coupled (A) inequality at the TIGHT case (max ratio 7/9):
   H?AFBo] side=000000111 f=(6,8) P=(6,1,7,3,8).  (A): E_0 + delta_P*L^2 <= (L/5)(N^2-Gamma).
"""
from fractions import Fraction as F
from _singleton_core import ell_map
from _trunc_verify import chi_profile as endpt_chi
from _h import dec
from _satzmu_conn import struct_for_side

n,E=dec("H?AFBo]")
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
side=[int(c) for c in "000000111"]
st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
N=F(n); Gamma=sum(T)
f=(6,8); P=[6,1,7,3,8]; L=len(P)
h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
deltaP=(S/L)**2-q
chiP=[0]*n
for end in (P[0],P[-1]):
    ch=endpt_chi(n,adj,side,end,M,n)
    for r in range(n): chiP[r]+=ch[r]
E0=sum((2*r+1)*chiP[r] for r in range(n))
lhs=E0+deltaP*L*L
rhs=F(L,5)*(N*N-Gamma)
print("N=%d L=%d Gamma=%d  N^2-Gamma=%s"%(n,L,Gamma,str(N*N-Gamma)))
print("T on path:",[T[P[i]] for i in range(L)]," (T values, /N = h_i)")
print("S=%s  q=%s  delta_P=(S/L)^2-q=%s"%(str(S),str(q),str(deltaP)))
print("chiP (endpoint DG profile):",chiP)
print("E_0 = sum(2r+1)chiP =",E0)
print("delta_P*L^2 =",deltaP*L*L)
print("(A) LHS = E_0+delta_P*L^2 =",lhs)
print("(A) RHS = (L/5)(N^2-Gamma) =",rhs)
print("ratio LHS/RHS =",lhs/rhs,"=",float(lhs/rhs))
print("Tax_0=",lhs," Slack-relevant (L/5)D_all=",rhs," (A) holds:",lhs<=rhs)
