"""Exact parametric global-minimum double-star Hall search (integer only)."""
from dataclasses import dataclass, asdict
import argparse, hashlib, json
@dataclass(frozen=True)
class Result:
 a:int; b:int; extra:int; aliases:int; coupling:int; locks:int; n:int; score:int; hub_demand:int; hub_reach:int; hub_gap:int; min_cut_loss:int
def flags(k,n): return (0,) if k==0 else ((1,) if k==n else (0,1))
def verify(a,b,e,u,c):
 assert a>=2 and b>=2 and e>=0 and u>=1 and c>=1
 locks=2*a*b-2+e; mn=10**30
 for hr in (0,1):
  for hl in (0,1):
   for hR in (0,1):
    for p in range(a+1):
     for q in range(b+1):
      for loL in flags(p,a):
       for loR in flags(q,b):
        lock=p*b-loL+q*a-loR+e*hr
        blue=(hr!=hl)+(hr!=hR)+(a-p if hl else p)+(b-q if hR else q)
        bad=p*(b-q)+(a-p)*q; loss=lock+blue-bad; mn=min(mn,loss); assert loss>=0
 n=4+a+b+2*locks; m=a*b
 score=2*(a*4*(b-1)+b*4*(a-1)+3*(5*m-a-b-3))
 demand=6*(5*m-a-b-3); core=3+a+b
 reach=2*(3*(n-core)+a*(a-1)+b*(b-1))
 return Result(a,b,e,u,c,locks,n,score,demand,reach,demand-reach,mn)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--max-side',type=int,default=18); ap.add_argument('--max-extra',type=int,default=8); ap.add_argument('--max-alias',type=int,default=4); ap.add_argument('--max-coupling',type=int,default=4); ap.add_argument('--output',default='search_results.json'); z=ap.parse_args(); rows=[]
 for a in range(2,z.max_side+1):
  for b in range(a,z.max_side+1):
   for e in range(z.max_extra+1):
    for u in range(1,z.max_alias+1):
     for c in range(1,z.max_coupling+1): rows.append(verify(a,b,e,u,c))
 pos=[x for x in rows if x.hub_gap>0]; first=min(pos,key=lambda x:(x.n,x.a*x.b,x.a,x.b,x.extra))
 payload={'parameters':vars(z),'cases':len(rows),'positive':len(pos),'first_positive':asdict(first),'formula':{'N':'4+a+b+2(2ab-2+e)','score':'2[4a(b-1)+4b(a-1)+3(5ab-a-b-3)]','hub_gap':'2(3ab-a^2-b^2-2a-2b-6e)'},'rows':[asdict(x) for x in rows]}
 raw=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode(); open(z.output,'wb').write(raw)
 print('cases',len(rows),'positive',len(pos)); print('first',json.dumps(asdict(first),sort_keys=True)); print('output_sha256',hashlib.sha256(raw).hexdigest()); print('script_sha256',hashlib.sha256(open(__file__,'rb').read()).hexdigest())
if __name__=='__main__': main()

