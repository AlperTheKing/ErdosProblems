#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('b',HERE/'exhaustive_n2_n8_9.py')
b=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(b)

def comps(mask,adj): return b.components_outside(adj,mask)
def bits(mask): return b.bits(mask)
def edges(mask,adj):
    return sum((adj[v]&mask).bit_count() for v in bits(mask))//2

def mu_component(adj,K,H,z):
    vs=list(bits(H)); km=sum(1<<v for v in K); best=0
    for sb in range(1,1<<len(vs)):
        if sb.bit_count()<=best: continue
        F=sum(1<<vs[i] for i in range(len(vs)) if sb>>i&1)
        cc=comps(F,adj)
        if edges(F,adj)!=F.bit_count()-len(cc): continue
        ok=True
        for C in cc:
            t=0
            for v in bits(C): t+=(adj[v]&km&~(1<<z)).bit_count()
            if t!=1: ok=False; break
        if ok: best=F.bit_count()
    return best

def check(line):
    n,adj=b.parse_graph6(line); g=b.girth(n,adj)
    if g<5:return None
    dist=b.all_pairs_dist(n,adj); ecc=b.eccentricities(n,dist); r,D=min(ecc),max(ecc)
    C=sum(1<<v for v in range(n) if ecc[v]==r); e=b.ecc_of_set(n,dist,C)
    if e==0 or e<=D-g//2:return None
    cycles,cap=b.shortest_cycle_vertex_sets(n,adj,g,5000); assert not cap
    out=[]
    for K in cycles:
      km=sum(1<<v for v in K); Hs=comps(((1<<n)-1)&~km,adj); mucache={}
      for x in range(n):
       if b.dist_to_set(dist,x,C)!=e:continue
       h=b.dist_to_set(dist,x,km)
       if h>=e:continue
       for m in K:
        if dist[x][m]!=h:continue
        de=e-h; W=[s for s in K if dist[s][m]<=de-1]; corr=max(0,2*de-g)
        q=[]
        for H in Hs:
          q.append(sum(max(dist[s][y] for y in bits(H))>=r+1 for s in W))
        for z in K:
         if z==m:continue
         mus=mucache.setdefault(z,[mu_component(adj,K,H,z) for H in Hs])
         nons_fail=[]
         zonly=[]
         for i,H in enumerate(Hs):
          ats=set()
          for v in bits(H): ats.update(bits(adj[v]&km))
          if ats-{z}:
           if q[i]>2*mus[i]: nons_fail.append((i,q[i],mus[i],sorted(ats)))
          elif q[i]: zonly.append((i,q[i],mus[i],sorted(ats)))
         xi=next((i for i,H in enumerate(Hs) if H>>x&1),None)
         xgap=None if xi is None else 2*(mus[xi]-h)-q[xi]
         globalgap=2*(sum(mus)-h)-sum(q)-corr
         out.append((globalgap,xgap,nons_fail,zonly,(n,g,r,D,e,list(K),x,h,m,z,de,W,corr,q,mus)))
    return out

def main():
    totals={'instances':0,'choices':0,'nons_fail':0,'xgap_neg':0,'global_bad_graphs':0}
    worstx=None; bad=[]
    for n in range(8,13):
      p=subprocess.run([str(b.GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
      residual=0; nbad=0
      for line in p.stdout.split():
       recs=check(line)
       if recs is None:continue
       residual+=1; totals['instances']+=1; totals['choices']+=len(recs)
       if any(rr[2] for rr in recs): totals['nons_fail']+=1
       for rr in recs:
        if rr[1] is not None and rr[1]<0:
         totals['xgap_neg']+=1
         if worstx is None or rr[1]<worstx[0]:worstx=(rr[1],line,rr)
       if recs and max(rr[0] for rr in recs)<0:
        nbad+=1; bad.append((line,max(rr[0] for rr in recs),max(recs,key=lambda q:q[0])))
      totals['global_bad_graphs']+=nbad
      print('n',n,'residual',residual,'bad',nbad,flush=True)
    print(totals); print('worstx',worstx); print('bad',bad[:10])
if __name__=='__main__':main()



