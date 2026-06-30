import subprocess, sys
from fractions import Fraction as F
from _h import dec,GENG,Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side,kcomponents

def boundary(n,adj,side,H):
 dB=dM=0
 for u in H:
  for v in adj[u]:
   if v in H: continue
   if side[u]!=side[v]: dB+=1
   else: dM+=1
 return dB,dM

def inspect(name,n,adj,side):
 if not Bconn(n,adj,side): return False
 st=struct_for_side(n,adj,side)
 if not st: return False
 M,ell,T,mu,cyc=st
 if not M: return False
 comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]; comps=sorted(set(cid))
 eta=F(n*n,25)-len(M); levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
 interesting=[]; bands=[]
 for j in range(len(levs)-1):
  tj=levs[j]; tn=levs[j+1]; wj=tn-tj; H=set(v for v in range(n) if T[v]>tj)
  if not H: continue
  h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
  cnt={c:0 for c in comps}
  for v in H: cnt[cid[v]]+=1
  Aj=wj*(F(n)+eta-tj-tn)*h; Bj=25*Aj-F(n)*wj*sig
  bands.append((j,tj,tn,H,h,sig,Bj,cnt))
  if 2*tj>=F(n) and Bj<0:
   nz=[c for c in comps if cnt[c]>0]
   if len(nz)>=2:
    interesting.append(j)
 if not interesting: return False
 print('CASE',name,''.join(map(str,side)),'n',n,'m',len(M),'M',M,'ell',ell)
 print('T',list(enumerate(T)))
 print('components',{c:[v for v in range(n) if cid[v]==c] for c in comps})
 for j,tj,tn,H,h,sig,Bj,cnt in bands:
  print('band',j,'[',tj,tn,']','pre',2*tj<F(n),'hn',2*tj>=F(n) and Bj<0,'h',h,'H',sorted(H),'sig',sig,'Bj',Bj,'cnt',cnt,'shares',{c:F(cnt[c],h) for c in comps})
 return True

for nn in range(7,12):
 for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
  n,E=dec(g6); adj,cuts=gmins(n,E)
  for side in cuts:
   if inspect('cen'+g6,n,adj,side): sys.exit(0)
print('none')
