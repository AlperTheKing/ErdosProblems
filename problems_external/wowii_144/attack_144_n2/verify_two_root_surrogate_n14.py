#!/usr/bin/env python3
"""Exact audit of a two-legal-root surrogate for W144 ordinary components."""
from __future__ import annotations
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;W0=ROOT/'problems_external/wowii_144'
sys.path[:0]=[str(ROOT/'problems_external/wowii_141/oracle'),str(W0/'oracle'),str(W0/'oracle_exhaustive'),str(W0/'proverC'),str(W0/'wave2'),str(W0/'attack_144_n2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
from verify_ordinary_triameter_n14 import atts,jmetric
from test_active_capacity import rooted_depth
GENG=ROOT/'tools/nauty2_8_9/geng.exe';OUT=HERE/'two_root_surrogate_n5_14.json'
def hdist(adj,H,s):
 d={s:0};q=[s]
 for u in q:
  for v in bits(adj[u]&H):
   if v not in d:d[v]=d[u]+1;q.append(v)
 return d
def audit(g6,R):
 n,a=parse_graph6(g6);g=girth(n,a)
 if g<5:return 'girth_lt_5'
 d=all_pairs_dist(n,a);ec=eccentricities(n,d);r,D=min(ec),max(ec);C=sum(1<<v for v in range(n)if ec[v]==r);e=ecc_of_set(n,d,C)
 if e==0 or e<=D-g//2:return 'nonresidual'
 rr=[v for v in range(n)if dist_to_set(d,v,C)==e];cy,cap=shortest_cycle_vertex_sets(n,a,g,5000)
 if cap:raise RuntimeError('cycle cap')
 lam=2*r+1-g
 for K in cy:
  km=sum(1<<v for v in K);cs=components_outside(a,((1<<n)-1)&~km);AA=[atts(a,K,H)for H in cs];mh=max(dist_to_set(d,x,km)for x in rr)
  for x in rr:
   h=dist_to_set(d,x,km)
   if h!=mh or h>=e:continue
   xi=next((i for i,H in enumerate(cs)if H>>x&1),None)
   for m in [u for u in K if d[x][u]==h]:
    de=e-h;WW=[u for u in K if d[u][m]<=de-1];EH=[[s for s in WW if max(d[s][y]for y in bits(H))>=r+1]for H in cs]
    for z in bits(a[m]&km):
     if not all(not(set(AA[i])=={z} and EH[i])for i in range(len(cs))):continue
     for i,H in enumerate(cs):
      roots=sorted(set(AA[i])-{z});q=len(EH[i])
      if i==xi or not q or len(roots)!=2:continue
      hv=list(bits(H));hd={u:hdist(a,H,u)for u in hv};B=[[u for u in hv if a[u]>>root&1]for root in roots];ell=2+min(hd[u][v]for u in B[0]for v in B[1]);rd=rooted_depth(a,K,H,z);bound=max(ell,2*rd);sl=bound-q-lam;key='g_ge_7'if g>=7 else'g_5_6';Q=R[key];Q['tests']+=1;Q['min_slack']=min(Q['min_slack'],sl)
      if sl<0 and len(Q['failures'])<20:Q['failures'].append(dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=de,W=WW,H=list(bits(H)),roots=roots,E=EH[i],root_cycle=ell,R=rd,P=jmetric(a,K,H,z)[0],bound=bound,lambda_=lam,slack=sl))
 return 'residual'
def main():
 t=time.time();R=dict(test='W144 two-root surrogate exact n=5..14',per_n={},g_ge_7=dict(tests=0,min_slack=10**9,failures=[]),g_5_6=dict(tests=0,min_slack=10**9,failures=[]))
 for n in range(5,15):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True);c=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
  for g6 in p.stdout.split():c['generated']+=1;c[audit(g6,R)]+=1
  R['per_n'][str(n)]=c;print(n,c,flush=True)
 R['elapsed_sec']=round(time.time()-t,2);raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw);sha=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(sha+'  '+OUT.name+'\n');print(R['g_ge_7']);print(R['g_5_6']);print(sha)
if __name__=='__main__':main()