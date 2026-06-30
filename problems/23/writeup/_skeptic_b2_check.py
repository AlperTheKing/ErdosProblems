"""Verify skeptic claim: C5 blow-up (1,48,6,8,48), canonical cut, claims B2 broken.
Rebuild graph, check tri-free, connected-B, CP-SAT GLOBAL max cut, recompute B2 exactly."""
from fractions import Fraction as F
from _wf_lrsbreak_2 import Cm_blowup_edges, canon_C5_cut, cpmax, trifree, eval_forms
from _h import Bconn

sizes=(1,48,6,8,48)
n,E,start=Cm_blowup_edges(5,list(sizes))
side=canon_C5_cut(sizes)
print("N=",n,"sum sizes=",sum(sizes))
print("starts=",start)
print("side[0]=",side[0],"part starts sides=",[side[s] for s in start])

adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)

# 1. triangle-free
print("trifree=",trifree(n,adj))

# 2. connected-B on this cut
print("Bconn=",Bconn(n,adj,side))

# 3. cut size on this side
cutsz=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
print("cutsz(side)=",cutsz)

# 4. CP-SAT global max
opt,bound,optimal=cpmax(n,E,tl=120)
print("CP-SAT opt=",opt,"bound=",bound,"optimal=",optimal)
print("is_global (cutsz==opt==bound and optimal)=",(cutsz==opt==bound and optimal))

# 5. recompute forms exactly
r=eval_forms(n,adj,side)
N=n
print("--- exact forms ---")
print("|M|=bM=",r['bM'])
print("Gamma=",r['Gamma'],"<= N^2=",N*N,"?",r['Gamma']<=N*N)
print("maxT=",r['maxT'],"= ",float(r['maxT']))
print("2N=",2*N)
print("B2 margin (2N - maxT)=",r['b2'],"= ",float(r['b2']),"  (skeptic claims -18)")
print("LRS margin=",r['lrs'])
print("ROW-LRS margin=",r['row'])
print("PATH-LRS margin=",r['path'])

# which vertex hits maxT
Tvals=None
from _satzmu_conn import struct_for_side
st=struct_for_side(n,adj,side)
M,ell,T,mu,cyc=st
argmax=max(range(n),key=lambda v:T[v])
print("argmax T at vertex",argmax,"T=",T[argmax])
print("T[0]=",T[0])
# ell of all bad edges
print("bad edges ell:",sorted(set(ell[f] for f in M)),"  |M|=",len(M))
