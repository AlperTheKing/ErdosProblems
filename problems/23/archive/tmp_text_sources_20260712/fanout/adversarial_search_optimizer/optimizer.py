import json,hashlib,itertools
from collections import defaultdict
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(enc(x)).hexdigest()
def quotient(I):
 C=json.loads(json.dumps(I));maps=[]
 for a in C['atoms']:
  seen={};rows=[];mp=[]
  for r in a['rows']:
   s=enc(r)
   if s not in seen:seen[s]=len(rows);rows.append(r)
   mp.append(seen[s])
  a['rows']=rows;maps.append(mp)
 return C,maps
def score(I,pick):
 U=set();S=set();n=defaultdict(int)
 for a,r in zip(I['atoms'],pick):
  q=a['rows'][r]
  for v in q['vertices']:U.add(v);n[v]+=1
  S|={tuple(sorted(e)) for e in q.get('support_edges',[])}
 E=[tuple(sorted(e)) for e in I['base_edges'] if set(e)<=U and tuple(sorted(e)) not in S];p={v:v for v in U}
 def F(v):
  while p[v]!=v:p[v]=p[p[v]];v=p[v]
  return v
 for x,y in E:
  x,y=F(x),F(y)
  if x!=y:p[max(x,y)]=min(x,y)
 active=set()
 for a in I['atoms']:
  x,y=a['endpoints']
  if x in U and y in U and F(x)==F(y):active|={v for v in U if F(v)==F(x)}
 terms=[]
 for v in sorted(active):
  t=I.get('cost_tables',{}).get(str(v),I['default_cost']);c=n[v];q=t[c] if c<len(t) else t[-1]+(c-len(t)+1)*I.get('overflow_slope',0)
  if q:terms.append([v,c,q])
 return {'score':sum(x[2] for x in terms),'active':sorted(active),'off_support':sorted(E),'terms':terms}
def solve(I):
 for t in list(I.get('cost_tables',{}).values())+[I['default_cost']]:assert all(type(x)is int and x>=0 for x in t)
 C,m=quotient(I);leaves=[]
 for p in itertools.product(*[range(len(a['rows'])) for a in C['atoms']]):leaves.append([list(p),score(C,p)['score']])
 b=min(leaves,key=lambda x:(x[1],x[0]));z={'format':'exact-scoped-opt-v1','instance_sha256':digest(I),'quotient_sha256':digest(C),'orbit_maps':m,'best_score':b[1],'best_picks':b[0],'best_evaluation':score(C,b[0]),'terminal_scores':leaves,'lower_bound':'0 from nonnegative costs'};z['certificate_sha256']=digest(z);return z
def verify(I,z):assert z==solve(I)
