from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
W141=ROOT/'problems_external'/'wowii_141'/'oracle'; W144=ROOT/'problems_external'/'wowii_144'
sys.path[:0]=[str(W141),str(W144/'oracle'),str(W144/'oracle_exhaustive'),str(W144/'proverC'),str(W144/'wave2')]
from invariants import all_pairs_dist,dist_to_set,ecc_of_set,eccentricities,girth
from lemma_e_tests import components_of_mask,edges_in_mask
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside

def mu_component(n,adj,K,H,z):
    kmask=sum(1<<v for v in K); hv=list(bits(H)); best=0; bestmask=0
    for ss in range(1,1<<len(hv)):
        if ss.bit_count()<=best: continue
        mask=sum(1<<hv[i] for i in range(len(hv)) if ss>>i&1)
        comps=components_of_mask(adj,mask)
        if edges_in_mask(adj,mask)!=mask.bit_count()-len(comps): continue
        if all(sum((adj[v]&(kmask&~(1<<z))).bit_count() for v in bits(C))==1 for C in comps):
            best=mask.bit_count(); bestmask=mask
    return best,bestmask

def rooted_depth(adj,K,H,z):
    kmask=sum(1<<v for v in K)&~(1<<z)
    ds={v:1 for v in bits(H) if adj[v]&kmask}; frontier=list(ds)
    for u in frontier:
        for v in bits(adj[u]&H):
            if v not in ds:ds[v]=ds[u]+1;frontier.append(v)
    return max(ds.values()) if ds else 0
def preserving_mu(n,adj,K,H,z,EH,dist,r):
    kmask=sum(1<<v for v in K); hv=list(bits(H)); best=-1; cov=-1; win=0
    for ss in range(1,1<<len(hv)):
        mask=sum(1<<hv[i] for i in range(len(hv)) if ss>>i&1)
        cc=components_of_mask(adj,mask)
        if edges_in_mask(adj,mask)!=mask.bit_count()-len(cc): continue
        if not all(sum((adj[v]&(kmask&~(1<<z))).bit_count() for v in bits(C))==1 for C in cc):continue
        sz=mask.bit_count();cv=sum(max(dist[sig][y] for y in bits(mask))>=r+1 for sig in EH)
        if (sz,cv)>(best,cov):best,cov,win=sz,cv,mask
    return best,cov,win
def analyze(g6):
    n,adj=parse_graph6(g6); gg=girth(n,adj)
    if gg<5:return []
    dist=all_pairs_dist(n,adj); ecc=eccentricities(n,dist); r,D=min(ecc),max(ecc)
    C=sum(1<<v for v in range(n) if ecc[v]==r); e=ecc_of_set(n,dist,C)
    if e==0 or e<=D-gg//2:return []
    rr=[v for v in range(n) if dist_to_set(dist,v,C)==e]
    cycles,cap=shortest_cycle_vertex_sets(n,adj,gg,5000)
    if cap:return []
    out=[]
    for K in cycles:
      kmask=sum(1<<v for v in K); comps=components_outside(adj,((1<<n)-1)&~kmask)
      maxh=max(dist_to_set(dist,x,kmask) for x in rr)
      for x in rr:
       h=dist_to_set(dist,x,kmask)
       if h!=maxh or h>=e:continue
       for m in [a for a in K if dist[x][a]==h]:
        delta=e-h; W=[a for a in K if dist[a][m]<=delta-1]
        EH=[[s for s in W if max(dist[s][y] for y in bits(H))>=r+1] for H in comps]
        xidx=next((i for i,H in enumerate(comps) if H>>x&1),None)
        attsets=[sorted(a for a in K if any(adj[v]>>a&1 for v in bits(H))) for H in comps]
        for z in bits(adj[m]&kmask):
          safe=True
          for i,H in enumerate(comps):
            att={a for a in K if any(adj[v]>>a&1 for v in bits(H))}
            if att=={z} and EH[i]:safe=False
          mus=[mu_component(n,adj,K,H,z) for H in comps]
          preserve=[preserving_mu(n,adj,K,H,z,EH[i],dist,r) for i,H in enumerate(comps)]
          S=sum(map(len,EH)); corr=max(0,2*delta-gg)
          glob=2*(sum(q for q,_ in mus)-h)-S-corr
          ordinary=min((2*mus[i][0]-len(EH[i]) for i in range(len(comps)) if i!=xidx),default=999)
          strong=min((2*mus[i][0]-len(EH[i])-(2*r+1-gg) for i in range(len(comps)) if i!=xidx and EH[i]),default=999)
          depthstrong=min((2*rooted_depth(adj,K,comps[i],z)-len(EH[i])-(2*r+1-gg) for i in range(len(comps)) if i!=xidx and EH[i]),default=999)
          capture=max((len(EH[i])-preserve[i][1] for i in range(len(comps)) if i!=xidx and EH[i]),default=0)
          cyclic_components=max((len(components_of_mask(adj,sum(1<<v for v in E))) for E in EH if E),default=0)
          active=None if xidx is None else 2*(mus[xidx][0]-h)-len(EH[xidx])-corr
          twoterm=None if xidx is None else min(mus[xidx][0]-h-dist[x][y]+1 for y in bits(comps[xidx]))
          triterm=None if xidx is None else min(mus[xidx][0]-((h+dist[m][y]+dist[x][y]+1)//2-1) for y in bits(comps[xidx]))
          pointwise=None if xidx is None or not EH[xidx] else min(dist[m][sig]-(delta-(mus[xidx][0]-h)) for sig in EH[xidx])
          out.append(dict(g6=g6,n=n,g=gg,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=delta,W=W,safe=safe,S=S,corr=corr,glob=glob,ordinary=ordinary,strong=strong,depthstrong=depthstrong,capture=capture,cyclic_components=cyclic_components,active=active,twoterm=twoterm,triterm=triterm,pointwise=pointwise,xidx=xidx,attsets=attsets,EH=[len(a) for a in EH],mu=[a for a,_ in mus],muw=[list(bits(b)) for _,b in mus]))
    return out

def main():
    records=[]; geng=ROOT/'tools'/'nauty2_8_9'/'geng.exe'
    for n in range(5,13):
      p=subprocess.run([str(geng),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
      for g6 in p.stdout.split():records.extend(analyze(g6))
    safe=[a for a in records if a['safe']]
    print('records',len(records),'safe',len(safe))
    for key in ('glob','ordinary'):
      vals=[a for a in safe if a[key] is not None]; print(key,min((a[key] for a in vals),default=None))
      for a in vals:
       if a[key]<0:print('FAIL',key,a);break
    print('g>=7 disc',[a for a in safe if a['g']>=7 and a['cyclic_components']>1][:2]); print('max cyclic E comps',max((a['cyclic_components'] for a in safe),default=0)); print('DISCE',[a for a in safe if a['cyclic_components']>1][:2]); print('g>=7 multi',[a for a in safe if a['g']>=7 and any(a['EH'][i] and len(set(a['attsets'][i])-{a['z']})>1 for i in range(len(a['EH'])) if i!=a['xidx'])][:5]); print('g>=7 depth fail',[a for a in safe if a['g']>=7 and a['depthstrong']<0][:2]); print('g>=7 depth min',min((a['depthstrong'] for a in safe if a['g']>=7 and a['depthstrong']!=999),default=None)); print('depthstrong min',min((a['depthstrong'] for a in safe if a['depthstrong']!=999),default=None)); print('DEPTHSTRONGFAIL',[a for a in safe if a['depthstrong']<0][:3]); print('strong min',min((a['strong'] for a in safe if a['strong']!=999),default=None)); print('STRONGFAIL',[a for a in safe if a['strong']<0][:2]); print('CAPTUREFAIL',[a for a in safe if a['capture']>0][:2])
    act=[a for a in safe if a['active'] is not None]
    print('active',len(act),'min',min((a['active'] for a in act),default=None)); print('active qpos min',min((a['active'] for a in act if a['EH'][a['xidx']]),default=None)); print('AQMIN',[a for a in act if a['EH'][a['xidx']] and a['active']==min((b['active'] for b in act if b['EH'][b['xidx']]),default=999)][:3])
    print('twoterm min',min((a['twoterm'] for a in act),default=None)); print('triterm min',min((a['triterm'] for a in act),default=None)); print('TRIFAIL',[a for a in act if a['triterm']<0][:2]); print('pointwise min',min((a['pointwise'] for a in act if a['pointwise'] is not None),default=None)); print('POINTFAIL',[a for a in act if a['pointwise'] is not None and a['pointwise']<0][:2]); print('TWOTERMFAIL',[a for a in act if a['twoterm']<0][:2])
    print('EQORD', [a for a in safe if a['ordinary']==0][:3])
    print('EQACT', [a for a in act if a['active']==0 and a['EH'][a['xidx']]>0][:5])
    for a in act:
      if a['active']<0:print('FAIL active',a);break
    groups={}
    for a in records:groups.setdefault((a['g6'],tuple(a['K']),a['x'],a['m']),[]).append(a)
    bad=[]
    for aa in groups.values():
      if not any(a['safe'] and a['glob']>=0 and (a['active'] is None or a['active']>=0) for a in aa):bad.append(aa)
    print('groups',len(groups),'bad_active_groups',len(bad))
    if bad:print('BADGROUP',bad[0])
if __name__=='__main__':main()















