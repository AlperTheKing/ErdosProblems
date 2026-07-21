#!/usr/bin/env python3
"""Exact local rooted-capacity audit for the W144 residual frontier."""
from __future__ import annotations
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
W141=ROOT/'problems_external'/'wowii_141'/'oracle'; W144=ROOT/'problems_external'/'wowii_144'
sys.path[:0]=[str(W141),str(W144/'oracle'),str(W144/'oracle_exhaustive'),str(W144/'proverC'),str(W144/'wave2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from lemma_e_tests import components_of_mask,edges_in_mask
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe'
OUT=HERE/'component_capacity_n5_14_results.json'

def mu_component(adj,K,H,z):
    kmask=sum(1<<v for v in K); hv=list(bits(H)); best=0; witness=0
    for ss in range(1,1<<len(hv)):
        if ss.bit_count()<=best:continue
        mask=sum(1<<hv[i] for i in range(len(hv)) if ss>>i&1)
        cc=components_of_mask(adj,mask)
        if edges_in_mask(adj,mask)!=mask.bit_count()-len(cc):continue
        if all(sum((adj[v]&(kmask&~(1<<z))).bit_count() for v in bits(C))==1 for C in cc):
            best=mask.bit_count();witness=mask
    return best,witness

def attachment_set(adj,K,H):
    return sorted(a for a in K if any(adj[v]>>a&1 for v in bits(H)))

def rec_base(g6,n,g,r,D,e,K,x,h,m,z,delta,W):
    return dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=delta,W=W)

def audit(g6,result):
    n,adj=parse_graph6(g6); g=girth(n,adj)
    if g<5:return 'girth_lt_5'
    dist=all_pairs_dist(n,adj);ecc=eccentricities(n,dist);r,D=min(ecc),max(ecc)
    C=sum(1<<v for v in range(n) if ecc[v]==r);e=ecc_of_set(n,dist,C)
    if e==0 or e<=D-g//2:return 'nonresidual'
    realizers=[v for v in range(n) if dist_to_set(dist,v,C)==e]
    cycles,cap=shortest_cycle_vertex_sets(n,adj,g,5000)
    if cap:raise RuntimeError('cycle cap')
    for K in cycles:
      kmask=sum(1<<v for v in K);outside=((1<<n)-1)&~kmask
      comps=components_outside(adj,outside);atts=[attachment_set(adj,K,H) for H in comps]
      cache={z:[mu_component(adj,K,H,z) for H in comps] for z in K}
      maxh=max(dist_to_set(dist,x,kmask) for x in realizers)
      for x in realizers:
       h=dist_to_set(dist,x,kmask)
       if h!=maxh or h>=e:continue
       for m in [a for a in K if dist[x][a]==h]:
        delta=e-h;W=[a for a in K if dist[a][m]<=delta-1]
        EH=[[s for s in W if max(dist[s][y] for y in bits(H))>=r+1] for H in comps]
        xidx=next((i for i,H in enumerate(comps) if H>>x&1),None)
        for z in K:
         if z==m:continue
         mus=cache[z]
         base=rec_base(g6,n,g,r,D,e,K,x,h,m,z,delta,W)
         for i,H in enumerate(comps):
          if not (set(atts[i])-{z}):continue
          slack=2*mus[i][0]-len(EH[i]);result['ordinary_tests']+=1
          if EH[i]:
           strong=slack-(2*r+1-g);result['strong_tests']+=1;result['strong_min_slack']=min(result['strong_min_slack'],strong)
           if strong<0 and len(result['strong_failures'])<20:result['strong_failures'].append(base|dict(H=list(bits(H)),attachments=atts[i],EH=EH[i],mu=mus[i][0],forest=list(bits(mus[i][1])),strong_slack=strong))
          result['ordinary_min_slack']=min(result['ordinary_min_slack'],slack)
          rr=base|dict(component_index=i,H=list(bits(H)),attachments=atts[i],EH=EH[i],mu=mus[i][0],forest=list(bits(mus[i][1])),slack=slack,is_x_component=(i==xidx))
          if slack<0 and len(result['ordinary_failures'])<20:result['ordinary_failures'].append(rr)
          if slack==0 and len(result['ordinary_equalities'])<30:result['ordinary_equalities'].append(rr)
         if not (adj[m]>>z&1):continue
         safe=all(not (set(atts[i])=={z} and EH[i]) for i in range(len(comps)))
         if not safe:continue
         S=sum(map(len,EH));corr=max(0,2*delta-g);M=sum(q for q,_ in mus)
         glob=2*(M-h)-S-corr;result['safe_adjacent_tests']+=1
         result['global_min_slack']=min(result['global_min_slack'],glob)
         if xidx is None:
          active=None
         else:
          active=2*(mus[xidx][0]-h)-len(EH[xidx])-corr
          result['active_tests']+=1;result['active_min_slack']=min(result['active_min_slack'],active)
          if set(atts[xidx]).issubset({m,z}):
           q=len(EH[xidx]);key=('q0' if q==0 else 'qpos')+('_wrap' if corr>0 else '_plain')
           d=result['active_special'].setdefault(key,dict(tests=0,min_slack=10**9,tight=[]))
           d['tests']+=1;d['min_slack']=min(d['min_slack'],active)
           if active==d['min_slack'] and len(d['tight'])<10:
            d['tight'].append(base|dict(attachments=atts[xidx],EHx=EH[xidx],mu_x=mus[xidx][0],forest_x=list(bits(mus[xidx][1])),correction=corr,active_slack=active))
         rr=base|dict(S=S,correction=corr,Mz=M,global_slack=glob,EH=[list(a) for a in EH],mu=[q for q,_ in mus],forests=[list(bits(b)) for _,b in mus],active_slack=active,x_component=xidx)
         if glob<0 and len(result['global_failures'])<20:result['global_failures'].append(rr)
         if glob==0 and len(result['global_equalities'])<30:result['global_equalities'].append(rr)
         if active is not None and active<0 and len(result['active_failures'])<20:result['active_failures'].append(rr)
         if active==0 and len(result['active_equalities'])<30:result['active_equalities'].append(rr)
    return 'residual'

def main():
    t=time.time();R=dict(test='W144 exact component capacity n=5..14',generator='nauty geng 2.8.9 -c -t -f',per_n={},ordinary_tests=0,ordinary_min_slack=10**9,ordinary_failures=[],ordinary_equalities=[],safe_adjacent_tests=0,global_min_slack=10**9,global_failures=[],global_equalities=[],active_tests=0,active_min_slack=10**9,active_failures=[],active_equalities=[])
    R['active_special']={}
    R['strong_tests']=0;R['strong_min_slack']=10**9;R['strong_failures']=[]
    for n in range(5,15):
      p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
      counts=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
      for g6 in p.stdout.split():
       counts['generated']+=1;counts[audit(g6,R)]+=1
      R['per_n'][str(n)]=counts;print(n,counts,flush=True)
    R['elapsed_sec']=round(time.time()-t,2)
    raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(digest+'  '+OUT.name+'\n')
    print({k:R[k] for k in ['ordinary_tests','ordinary_min_slack','safe_adjacent_tests','global_min_slack','active_tests','active_min_slack','strong_tests','strong_min_slack']});print('sha256',digest)
if __name__=='__main__':main()


