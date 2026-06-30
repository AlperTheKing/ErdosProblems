from fractions import Fraction as F
from _h import dec,Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side,kcomponents

def boundary_edges(n,adj,side,H):
 out=[]; dB=dM=0
 for u in H:
  for v in adj[u]:
   if v in H or u>v: continue
   typ='B' if side[u]!=side[v] else 'M'
   out.append((u,v,typ))
   if typ=='B': dB+=1
   else: dM+=1
 return dB,dM,out

g6='G?q`v_'; n,E=dec(g6); adj,cuts=gmins(n,E)
print('n',n,'E',E,'cuts',len(cuts))
for side in cuts:
 if ''.join(map(str,side))!='11110000': continue
 print('side',side,'Bconn',Bconn(n,adj,side))
 M,ell,T,mu,cyc=struct_for_side(n,adj,side)
 eta=F(n*n,25)-len(M); comp_map,find=kcomponents(n,cyc); cid=[find(v) for v in range(n)]
 print('M',M,'ell',ell,'eta',eta,'T',list(enumerate(T)),'cyc',cyc)
 print('comp',{c:[v for v in range(n) if cid[v]==c] for c in sorted(set(cid))})
 levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
 for j in range(len(levs)-1):
  tj=levs[j]; tn=levs[j+1]; w=tn-tj; H=set(v for v in range(n) if T[v]>tj)
  h=len(H); dB,dM,be=boundary_edges(n,adj,side,H); sig=dB-dM; coef=F(n)+eta-tj-tn; Bj=w*(25*coef*h-F(n)*sig)
  print('band',j,'[',tj,tn,']','H',sorted(H),'h',h,'coef',coef,'sig',sig,'Bj',Bj,'pre',2*tj<F(n),'hn',2*tj>=F(n) and Bj<0,'boundary',be)
