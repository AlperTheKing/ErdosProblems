"""Exact enumeration of short R29-compatible cable trees."""
import itertools,json
from collections import deque
T=(0,1,2,3); C=(0,0,1,1)
def tree(s,n):
 d=[1]*n
 for x in s:d[x]+=1
 e=[]
 for x in s:
  a=next(i for i,z in enumerate(d) if z==1);e.append(tuple(sorted((a,x))));d[a]-=1;d[x]-=1
 a,b=[i for i,z in enumerate(d) if z==1];e.append(tuple(sorted((a,b))));return tuple(sorted(e))
def canon(e,n):
 ss=tuple(range(4,n));out=[]
 for im in itertools.permutations(ss):
  p=dict(zip(ss,im));out.append(tuple(sorted(tuple(sorted((p.get(a,a),p.get(b,b)))) for a,b in e)))
 return min(out)
def dist(e,n):
 A=[[]for _ in range(n)]
 for a,b in e:A[a].append(b);A[b].append(a)
 d=[-1]*n;d[0]=0;q=deque([0])
 while q:
  x=q.popleft()
  for y in A[x]:
   if d[y]<0:d[y]=d[x]+1;q.append(y)
 return d
rec=[];tot={}
for n in range(4,8):
 seen={canon(tree(s,n),n) for s in itertools.product(range(n),repeat=n-2)}
 seen={e for e in seen if all(dist(e,n)[t]%2==C[t] for t in T)};good=tests=0
 for e in sorted(seen):
  ss=tuple(range(4,n));stable=[];bad=None
  for mask in range(1<<len(ss)):
   seed=tuple(ss[i] for i in range(len(ss)) if mask>>i&1);tests+=1
   missing=set(range(n))-(set(T)|set(seed))
   if not missing:stable.append(seed);good+=1
   elif bad is None:bad={'seeds':seed,'omitted_vertex':min(missing)}
  d=dist(e,n);rec.append({'n':n,'edges':e,'terminal_distances_from_r':tuple(d[t] for t in T),'stable_seed_sets':stable,'first_unseeded_falsifier':bad})
 tot[str(n-1)]={'topologies':len(seen),'seed_sets_tested':tests,'stable_seed_sets':good}
r29=canon(((0,4),(1,4),(2,5),(3,6),(4,5),(4,6)),7);matches=[i for i,x in enumerate(rec) if x['n']==7 and x['edges']==r29]
out={'arithmetic':'integer only','terminal_order':['r','m','cL','cR'],'terminal_colors':C,'range':{'edges_min':3,'edges_max':6},'totals':tot,'r29_canonical_edges':r29,'r29_record_indices':matches,'records':rec}
with open('tmp/fanout/adversarial_search_cable/results.json','w') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'totals':tot,'records':len(rec),'r29_matches':matches},indent=2))
