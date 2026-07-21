#!/usr/bin/env python3
"""Exact residual audit of the unwrapped extreme-witness perimeter lemma."""
from __future__ import annotations
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;W0=ROOT/'problems_external/wowii_144'
sys.path[:0]=[str(ROOT/'problems_external/wowii_141/oracle'),str(W0/'oracle'),str(W0/'oracle_exhaustive'),str(W0/'proverC'),str(W0/'wave2'),str(W0/'attack_144_n2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
from verify_ordinary_triameter_n14 import atts
from test_ordinary_witness_cover import j_distances
GENG=ROOT/'tools/nauty2_8_9/geng.exe';OUT=HERE/'ordinary_extreme_pair_n5_14.json'
def audit(g6,R):
 n,a=parse_graph6(g6);g=girth(n,a)
 if g<5:return 'girth_lt_5'
 d=all_pairs_dist(n,a);ec=eccentricities(n,d);r,D=min(ec),max(ec);C=sum(1<<v for v in range(n)if ec[v]==r);e=ecc_of_set(n,d,C)
 if e==0 or e<=D-g//2:return 'nonresidual'
 rr=[v for v in range(n)if dist_to_set(d,v,C)==e];cy,cap=shortest_cycle_vertex_sets(n,a,g,5000)
 if cap:raise RuntimeError('cycle cap')
 lam=2*r+1-g
 for K in cy:
  km=sum(1<<v for v in K);cs=components_outside(a,((1<<n)-1)&~km);aa=[atts(a,K,H)for H in cs];mh=max(dist_to_set(d,x,km)for x in rr);kadj={u:[v for v in K if a[u]>>v&1]for u in K}
  for x in rr:
   h=dist_to_set(d,x,km)
   if h!=mh or h>=e:continue
   xi=next((i for i,H in enumerate(cs)if H>>x&1),None)
   for m in [u for u in K if d[x][u]==h]:
    de=e-h;WW=[u for u in K if d[u][m]<=de-1];EH=[[s for s in WW if max(d[s][y]for y in bits(H))>=r+1]for H in cs]
    if len(WW)==g:R['wrapped_configurations']+=1;continue
    coord={m:0};nb=kadj[m]
    for sign,start in [(1,nb[0]),(-1,nb[1])]:
     prev,cur=m,start
     for j in range(1,de):coord[cur]=sign*j;nxt=[v for v in kadj[cur]if v!=prev][0];prev,cur=cur,nxt
    if set(coord)!=set(WW):raise RuntimeError('coordinate mismatch')
    for z in bits(a[m]&km):
     if not all(not(set(aa[i])=={z} and EH[i])for i in range(len(cs))):continue
     for i,H in enumerate(cs):
      E=EH[i]
      if i==xi or not E or not(set(aa[i])-{z}):continue
      s=min(E,key=lambda u:coord[u]);t=max(E,key=lambda u:coord[u]);L=coord[t]-coord[s];hv,jd,rho=j_distances(a,K,H,z);U=[j for j,y in enumerate(hv)if d[s][y]>=r+1];V=[j for j,y in enumerate(hv)if d[t][y]>=r+1]
      best=min(jd[rho][u]+jd[rho][v]+jd[u][v]for u in U for v in V);sl=best-L-lam-1;key='g_ge_7'if g>=7 else'g_5_6';q=R[key];q['tests']+=1;q['min_slack']=min(q['min_slack'],sl)
      if sl<0 and len(q['failures'])<20:q['failures'].append(dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=de,W=WW,H=list(bits(H)),A=aa[i],E=E,s=s,t=t,span=L,lambda_=lam,best_perimeter=best,slack=sl))
 return 'residual'
def main():
 t=time.time();R=dict(test='W144 extreme endpoint witness perimeter exact n=5..14',per_n={},wrapped_configurations=0,g_ge_7=dict(tests=0,min_slack=10**9,failures=[]),g_5_6=dict(tests=0,min_slack=10**9,failures=[]))
 for n in range(5,15):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True);c=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
  for g6 in p.stdout.split():c['generated']+=1;c[audit(g6,R)]+=1
  R['per_n'][str(n)]=c;print(n,c,flush=True)
 R['elapsed_sec']=round(time.time()-t,2);raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw);sha=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(sha+'  '+OUT.name+'\n');print(R['g_ge_7']);print(R['g_5_6']);print('wrapped',R['wrapped_configurations']);print(sha)
if __name__=='__main__':main()