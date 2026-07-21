#!/usr/bin/env python3
"""Exact residual audit of q_H + (2r+1-g) <= 2 R_z(H)."""
from __future__ import annotations
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
W141=ROOT/'problems_external'/'wowii_141'/'oracle';W144=ROOT/'problems_external'/'wowii_144'
sys.path[:0]=[str(W141),str(W144/'oracle'),str(W144/'oracle_exhaustive'),str(W144/'proverC'),str(W144/'wave2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe';OUT=HERE/'ordinary_depth_n5_14.json'
def atts(adj,K,H):return sorted(a for a in K if any(adj[v]>>a&1 for v in bits(H)))
def depth(adj,K,H,z):
 km=sum(1<<v for v in K)&~(1<<z);d={v:1 for v in bits(H) if adj[v]&km};q=list(d)
 for u in q:
  for v in bits(adj[u]&H):
   if v not in d:d[v]=d[u]+1;q.append(v)
 return max(d.values()) if d else 0
def audit(g6,R):
 n,adj=parse_graph6(g6);g=girth(n,adj)
 if g<5:return 'girth_lt_5'
 dist=all_pairs_dist(n,adj);ecc=eccentricities(n,dist);r,D=min(ecc),max(ecc);C=sum(1<<v for v in range(n) if ecc[v]==r);e=ecc_of_set(n,dist,C)
 if e==0 or e<=D-g//2:return 'nonresidual'
 realizers=[v for v in range(n) if dist_to_set(dist,v,C)==e];cycles,cap=shortest_cycle_vertex_sets(n,adj,g,5000)
 if cap:raise RuntimeError('cycle cap')
 lam=2*r+1-g
 for K in cycles:
  km=sum(1<<v for v in K);cs=components_outside(adj,((1<<n)-1)&~km);aa=[atts(adj,K,H) for H in cs];maxh=max(dist_to_set(dist,x,km) for x in realizers)
  for x in realizers:
   h=dist_to_set(dist,x,km)
   if h!=maxh or h>=e:continue
   for m in [a for a in K if dist[x][a]==h]:
    delta=e-h;W=[a for a in K if dist[a][m]<=delta-1];EH=[[s for s in W if max(dist[s][y] for y in bits(H))>=r+1] for H in cs];xi=next((i for i,H in enumerate(cs) if H>>x&1),None)
    for z in bits(adj[m]&km):
     if not all(not(set(aa[i])=={z} and EH[i]) for i in range(len(cs))):continue
     for i,H in enumerate(cs):
      if i==xi or not EH[i] or not(set(aa[i])-{z}):continue
      rd=depth(adj,K,H,z);sl=2*rd-len(EH[i])-lam;key='g_ge_7' if g>=7 else 'g_5_6';d=R[key];d['tests']+=1;d['min_slack']=min(d['min_slack'],sl)
      if sl<0 and len(d['failures'])<20:d['failures'].append(dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=delta,W=W,H=list(bits(H)),attachments=aa[i],EH=EH[i],R=rd,lambda_=lam,slack=sl))
 return 'residual'
def main():
 t=time.time();R=dict(test='W144 ordinary rooted-depth residual exact n=5..14',per_n={},g_ge_7=dict(tests=0,min_slack=10**9,failures=[]),g_5_6=dict(tests=0,min_slack=10**9,failures=[]))
 for n in range(5,15):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True);c=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
  for g6 in p.stdout.split():c['generated']+=1;c[audit(g6,R)]+=1
  R['per_n'][str(n)]=c;print(n,c,flush=True)
 R['elapsed_sec']=round(time.time()-t,2);raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw);sha=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(sha+'  '+OUT.name+'\n');print(R['g_ge_7']['tests'],R['g_ge_7']['min_slack'],len(R['g_ge_7']['failures']));print(R['g_5_6']['tests'],R['g_5_6']['min_slack'],len(R['g_5_6']['failures']));print(sha)
if __name__=='__main__':main()