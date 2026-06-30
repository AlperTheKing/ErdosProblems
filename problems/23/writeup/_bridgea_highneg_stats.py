"""Stats for high-negative BRIDGE-A bands: coefficient sign and component support."""
import subprocess
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

def chk(name,n,adj,side,acc):
 if not Bconn(n,adj,side): return
 st=struct_for_side(n,adj,side)
 if not st: return
 M,ell,T,mu,cyc=st
 if not M: return
 eta=F(n*n,25)-len(M); levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
 comp_map,find=kcomponents(n,cyc); cid=[find(v) for v in range(n)]
 for j in range(len(levs)-1):
  tj=levs[j]; tn=levs[j+1]; wj=tn-tj
  if 2*tj<F(n): continue
  H=set(v for v in range(n) if T[v]>tj)
  if not H: continue
  h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
  coef=F(n)+eta-tj-tn
  Bj=wj*(25*coef*h - F(n)*sig)
  if Bj<0:
   acc['high']+=1
   if coef<0: acc['coef_neg']+=1
   elif coef==0: acc['coef_zero']+=1
   else:
    acc['coef_pos']+=1
    if acc['first_pos'] is None: acc['first_pos']=(name,''.join(map(str,side)),n,len(M),j,str(tj),str(tn),h,str(sig),str(coef),str(Bj))
   comps=set(cid[v] for v in H)
   if len(comps)>1: acc['multi']+=1

def run(maxn=11):
 acc={'high':0,'coef_neg':0,'coef_zero':0,'coef_pos':0,'first_pos':None,'multi':0}
 for nn in range(7,maxn+1):
  for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
   n,E=dec(g6); adj,cuts=gmins(n,E)
   for side in cuts: chk('cen'+g6,n,adj,side,acc)
  print('N',nn,acc,flush=True)
 print(acc)
run()
