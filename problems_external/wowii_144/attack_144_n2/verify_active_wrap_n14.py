#!/usr/bin/env python3
"""Exact distribution of wrapped active multiattachment W144 cases."""
from __future__ import annotations
import collections,hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
W141=ROOT/'problems_external'/'wowii_141'/'oracle';W144=ROOT/'problems_external'/'wowii_144'
sys.path[:0]=[str(W141),str(W144/'oracle'),str(W144/'oracle_exhaustive'),str(W144/'proverC'),str(W144/'wave2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe';OUT=HERE/'active_wrap_distribution_n5_14.json'
def atts(adj,K,H):return sorted(a for a in K if any(adj[v]>>a&1 for v in bits(H)))
def inc(d,k):d[k]=d.get(k,0)+1
def audit(g6,R):
 n,adj=parse_graph6(g6);g=girth(n,adj)
 if g<5:return 'girth_lt_5'
 dist=all_pairs_dist(n,adj);ecc=eccentricities(n,dist);r,D=min(ecc),max(ecc);C=sum(1<<v for v in range(n) if ecc[v]==r);e=ecc_of_set(n,dist,C)
 if e==0 or e<=D-g//2:return 'nonresidual'
 realizers=[v for v in range(n) if dist_to_set(dist,v,C)==e];cycles,cap=shortest_cycle_vertex_sets(n,adj,g,5000)
 if cap:raise RuntimeError('cycle cap')
 for K in cycles:
  km=sum(1<<v for v in K);cs=components_outside(adj,((1<<n)-1)&~km);aa=[atts(adj,K,H) for H in cs];maxh=max(dist_to_set(dist,x,km) for x in realizers)
  for x in realizers:
   h=dist_to_set(dist,x,km)
   if h!=maxh or h>=e:continue
   xi=next((i for i,H in enumerate(cs) if H>>x&1),None)
   if xi is None:continue
   for m in [a for a in K if dist[x][a]==h]:
    delta=e-h;W=[a for a in K if dist[a][m]<=delta-1];EH=[[s for s in W if max(dist[s][y] for y in bits(H))>=r+1] for H in cs]
    for z in bits(adj[m]&km):
     if not all(not(set(aa[i])=={z} and EH[i]) for i in range(len(cs))):continue
     R['active_total']+=1
     q=len(EH[xi]);multi=bool(set(aa[xi])-{m,z});wrapped=delta>g//2
     if q>0:R['active_qpos']+=1
     if q>0 and multi:
      R['qpos_multi']+=1;inc(R['by_g'],str(g));inc(R['by_h'],str(h));inc(R['by_delta'],str(delta));inc(R['by_n'],str(n));inc(R['by_g_h_delta'],f'{g},{h},{delta}')
      if wrapped:
       R['qpos_multi_wrapped']+=1
       if len(R['wrapped_examples'])<20:R['wrapped_examples'].append(dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=delta,W=W,Hx=list(bits(cs[xi])),attachments=aa[xi],EHx=EH[xi]))
 return 'residual'
def main():
 t=time.time();R=dict(test='W144 active qpos multiattachment wrap distribution exact n=5..14',per_n={},active_total=0,active_qpos=0,qpos_multi=0,qpos_multi_wrapped=0,by_g={},by_h={},by_delta={},by_n={},by_g_h_delta={},wrapped_examples=[])
 for n in range(5,15):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True);c=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
  for g6 in p.stdout.split():c['generated']+=1;c[audit(g6,R)]+=1
  R['per_n'][str(n)]=c;print(n,c,flush=True)
 R['elapsed_sec']=round(time.time()-t,2);raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw);sha=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(sha+'  '+OUT.name+'\n');print({k:R[k] for k in ('active_total','active_qpos','qpos_multi','qpos_multi_wrapped','by_g','by_h','by_delta','by_g_h_delta')});print(sha)
if __name__=='__main__':main()