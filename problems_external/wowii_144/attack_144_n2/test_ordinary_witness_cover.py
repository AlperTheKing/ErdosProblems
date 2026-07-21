#!/usr/bin/env python3
"""Exact diagnostics for W144 ordinary-component inequality.

Tests both the registered residual window and a stronger unrestricted version
using the full shortest cycle.  The rooted distance R is d_J(rho, .), where
J is the apex graph associated with z.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
W141=ROOT/'problems_external'/'wowii_141'/'oracle'
W144=ROOT/'problems_external'/'wowii_144'
sys.path[:0]=[str(W141),str(W144/'oracle'),str(W144/'oracle_exhaustive'),str(W144/'proverC'),str(W144/'wave2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from lemma_e_tests import components_of_mask,edges_in_mask
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe'
OUT=HERE/'ordinary_witness_cover_n5_12.json'

def attachment_set(adj,K,H):
    return sorted(a for a in K if any(adj[v]>>a&1 for v in bits(H)))

def mu_component(adj,K,H,z):
    kmask=sum(1<<v for v in K); hv=list(bits(H)); best=0; witness=0
    for ss in range(1,1<<len(hv)):
        if ss.bit_count()<=best: continue
        mask=sum(1<<hv[i] for i in range(len(hv)) if ss>>i&1)
        cc=components_of_mask(adj,mask)
        if edges_in_mask(adj,mask)!=mask.bit_count()-len(cc): continue
        if all(sum((adj[v]&(kmask&~(1<<z))).bit_count() for v in bits(C))==1 for C in cc):
            best=mask.bit_count(); witness=mask
    return best,witness

def j_distances(adj,K,H,z):
    """Return root distances and pair distances in J_z(H)."""
    hv=list(bits(H)); root=max(hv,default=-1)+1
    # Work with local integer indices to avoid collision with G labels.
    loc={v:i for i,v in enumerate(hv)}; rho=len(hv); ja=[0]*(rho+1)
    kmask=sum(1<<v for v in K)&~(1<<z)
    for v in hv:
        i=loc[v]
        for w in bits(adj[v]&H): ja[i]|=1<<loc[w]
        if adj[v]&kmask:
            ja[i]|=1<<rho; ja[rho]|=1<<i
    def bfs(s):
        d=[10**9]*len(ja); d[s]=0; q=[s]
        for u in q:
            for v in bits(ja[u]):
                if d[v]==10**9: d[v]=d[u]+1; q.append(v)
        return d
    dd=[bfs(i) for i in range(len(ja))]
    return hv,dd,rho

def witness_diagnostic(adj,K,H,z,E,dist,r):
    hv,jd,rho=j_distances(adj,K,H,z)
    full=(1<<len(E))-1
    covers=[]
    for y in hv:
        covers.append(sum(1<<i for i,s in enumerate(E) if dist[s][y]>=r+1))
    R=max((jd[rho][i] for i in range(len(hv))),default=0)
    best_tau=-1; best_pair=None; cover_num=99
    for i,y in enumerate(hv):
        if covers[i]==full:
            cover_num=1
            tau=jd[rho][i]
            if tau>best_tau: best_tau=tau;best_pair=[y]
    for i,y in enumerate(hv):
      for j in range(i+1,len(hv)):
        if (covers[i]|covers[j])==full:
            cover_num=min(cover_num,2)
            tau=(jd[rho][i]+jd[rho][j]+jd[i][j]+1)//2
            if tau>best_tau: best_tau=tau;best_pair=[y,hv[j]]
    # Exact minimum witness-set cover number, only as a finite diagnostic.
    if full==0: cover_num=0
    elif cover_num>2:
      for ss in range(1,1<<len(hv)):
        if ss.bit_count()>=cover_num: continue
        cov=0
        for i in range(len(hv)):
            if ss>>i&1:cov|=covers[i]
        if cov==full:cover_num=ss.bit_count()
    return dict(R=R,cover_number=cover_num,best_two_tau=best_tau,best_pair=best_pair,
                witness_covers={str(y):[E[i] for i in range(len(E)) if covers[j]>>i&1]
                                for j,y in enumerate(hv)})

def base_record(g6,n,g,r,D,e,K,H,z,E,mu,forest,diag):
    return dict(graph6=g6,n=n,g=g,r=r,D=D,e=e,K=K,H=list(bits(H)),z=z,E=E,
                attachments=attachment_set(CURRENT_ADJ,K,H),mu=mu,forest=list(bits(forest)),**diag)

CURRENT_ADJ=[]

def audit_graph(g6,R):
    global CURRENT_ADJ
    n,adj=parse_graph6(g6);CURRENT_ADJ=adj;g=girth(n,adj)
    if g<5:return 'girth_lt_5'
    dist=all_pairs_dist(n,adj); ecc=eccentricities(n,dist); r,D=min(ecc),max(ecc)
    C=sum(1<<v for v in range(n) if ecc[v]==r); e=ecc_of_set(n,dist,C)
    residual=e>0 and e>D-g//2
    cycles,cap=shortest_cycle_vertex_sets(n,adj,g,5000)
    if cap:raise RuntimeError('cycle cap')
    lam=2*r+1-g
    for K in cycles:
      kmask=sum(1<<v for v in K); comps=components_outside(adj,((1<<n)-1)&~kmask)
      # Stronger unrestricted statement: E is taken on all of K.
      for H in comps:
       E=[s for s in K if max(dist[s][y] for y in bits(H))>=r+1]
       if not E:continue
       for z in K:
        if not (set(attachment_set(adj,K,H))-{z}):continue
        mu,forest=mu_component(adj,K,H,z);diag=witness_diagnostic(adj,K,H,z,E,dist,r)
        depth_slack=2*diag['R']-len(E)-lam; mu_slack=2*mu-len(E)-lam
        R['unrestricted_tests']+=1;R['unrestricted_depth_min']=min(R['unrestricted_depth_min'],depth_slack);R['unrestricted_mu_min']=min(R['unrestricted_mu_min'],mu_slack)
        rec=base_record(g6,n,g,r,D,e,K,H,z,E,mu,forest,diag)|dict(lambda_=lam,depth_slack=depth_slack,mu_slack=mu_slack,residual=residual)
        if depth_slack<0 and len(R['unrestricted_depth_failures'])<20:R['unrestricted_depth_failures'].append(rec)
        if mu_slack<0 and len(R['unrestricted_mu_failures'])<20:R['unrestricted_mu_failures'].append(rec)
      if not residual:continue
      realizers=[v for v in range(n) if dist_to_set(dist,v,C)==e]
      maxh=max(dist_to_set(dist,x,kmask) for x in realizers)
      for x in realizers:
       h=dist_to_set(dist,x,kmask)
       if h!=maxh or h>=e:continue
       for m in [a for a in K if dist[x][a]==h]:
        delta=e-h;W=[a for a in K if dist[a][m]<=delta-1]
        EH=[[s for s in W if max(dist[s][y] for y in bits(H))>=r+1] for H in comps]
        xidx=next((i for i,H in enumerate(comps) if H>>x&1),None)
        for z in bits(adj[m]&kmask):
         atts=[attachment_set(adj,K,H) for H in comps]
         safe=all(not(set(atts[i])=={z} and EH[i]) for i in range(len(comps)))
         if not safe:continue
         for i,H in enumerate(comps):
          if i==xidx or not EH[i] or not(set(atts[i])-{z}):continue
          mu,forest=mu_component(adj,K,H,z);diag=witness_diagnostic(adj,K,H,z,EH[i],dist,r)
          depth_slack=2*diag['R']-len(EH[i])-lam;mu_slack=2*mu-len(EH[i])-lam
          pair_slack=2*diag['best_two_tau']-len(EH[i])-lam if diag['best_two_tau']>=0 else -999
          R['residual_tests']+=1;R['residual_depth_min']=min(R['residual_depth_min'],depth_slack);R['residual_mu_min']=min(R['residual_mu_min'],mu_slack);R['residual_pair_min']=min(R['residual_pair_min'],pair_slack);R['residual_cover_max']=max(R['residual_cover_max'],diag['cover_number'])
          rec=base_record(g6,n,g,r,D,e,K,H,z,EH[i],mu,forest,diag)|dict(lambda_=lam,depth_slack=depth_slack,mu_slack=mu_slack,pair_slack=pair_slack,x=x,h=h,m=m,delta=delta,W=W)
          if depth_slack<0 and len(R['residual_depth_failures'])<20:R['residual_depth_failures'].append(rec)
          if mu_slack<0 and len(R['residual_mu_failures'])<20:R['residual_mu_failures'].append(rec)
          if (diag['cover_number']>2 or pair_slack<0) and len(R['residual_pair_failures'])<20:R['residual_pair_failures'].append(rec)
    return 'residual' if residual else 'nonresidual'

def main():
    t=time.time();R=dict(test='W144 ordinary witness/depth exact n=5..12',per_n={},
      unrestricted_tests=0,unrestricted_depth_min=10**9,unrestricted_mu_min=10**9,unrestricted_depth_failures=[],unrestricted_mu_failures=[],
      residual_tests=0,residual_depth_min=10**9,residual_mu_min=10**9,residual_pair_min=10**9,residual_cover_max=0,residual_depth_failures=[],residual_mu_failures=[],residual_pair_failures=[])
    for n in range(5,13):
      p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
      counts=dict(generated=0,girth_lt_5=0,nonresidual=0,residual=0)
      for g6 in p.stdout.split():
        counts['generated']+=1;counts[audit_graph(g6,R)]+=1
      R['per_n'][str(n)]=counts;print(n,counts,flush=True)
    R['elapsed_sec']=round(time.time()-t,3)
    raw=(json.dumps(R,indent=2,sort_keys=True)+'\n').encode();OUT.write_bytes(raw)
    digest=hashlib.sha256(raw).hexdigest().upper();OUT.with_suffix('.json.sha256').write_text(digest+'  '+OUT.name+'\n')
    print({k:R[k] for k in ('unrestricted_tests','unrestricted_depth_min','unrestricted_mu_min','residual_tests','residual_depth_min','residual_mu_min','residual_pair_min','residual_cover_max')})
    print('fail counts',len(R['unrestricted_depth_failures']),len(R['unrestricted_mu_failures']),len(R['residual_depth_failures']),len(R['residual_pair_failures']))
    print('sha256',digest)
if __name__=='__main__':main()