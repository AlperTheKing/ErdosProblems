"""Exact integer/Fraction checker for the R29 selector trade."""
import hashlib,importlib.util,json
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; LEAD=Path(__file__).with_name('r29_construction.py')
s=importlib.util.spec_from_file_location('r29',LEAD); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
d=m.build(); rows=d['rows']; base=m.scoped_state(d,rows); assert base['score']==30811
adj=m.adjacency(d['n'],d['blue']); trade=list(rows); shapes=Counter(); touch=[Counter(),Counter()]; a,b=d['selectorStart'],d['selectorStop']
for i,(atom,meta) in enumerate(zip(d['atoms'][a:b],d['selectorMeta'])):
 f=m.shortest_rows(adj,*atom); an=[r for r in f if 55 in r]; lo=[r for r in f if 55 not in r]; shapes[len(an),len(lo)]+=1; assert meta['anchorRow'] in an; trade[a+i]=meta['anchorRow']
 hit=set()
 for row in lo:
  x=[v for v in row if v in d['dXToLeaf']]; assert len(x)==1; hit.add(d['dXToLeaf'][x[0]])
 for leaf in hit: touch[meta['region']][leaf]+=1
assert shapes==Counter({(676,4):676}) and all(len(c)==13 and set(c.values())=={27} for c in touch)
t=m.scoped_state(d,tuple(trade)); assert (t['score'],t['collisionTotal'],t['hitNeedTotal'])==(23115,23108,7)
best=None; args=[]
for ll in range(339):
 for lr in range(339):
  al,ar=338-ll,338-lr
  c=lambda x:-(-Fraction(x,27).numerator//Fraction(x,27).denominator)
  z=20411+2*(al+ar+max(0,al-1)+max(0,ar-1))+200*(c(ll)+c(lr))+4*(ll==lr==0)
  if best is None or z<best: best,args=z,[(ll,lr)]
  elif z==best: args.append((ll,lr))
assert best==23115 and args==[(0,0)]
p={'scope':'selector rows only; 707 rigid rows fixed','baseline':30811,'witness':{'all676AnchorRows':True,'score':23115,'delta':-7696,'collision':23108,'hitNeed':7},'model':{'states':339*339,'minimum':best,'argminLocalCounts':[list(x) for x in args],'formula':'20411+2*(AL+AR+(AL-1)_+ +(AR-1)_+)+200*(ceil(LL/27)+ceil(LR/27))+4*1[LL=LR=0]'},'constructionSha256':hashlib.sha256(m.canonical_bytes(d)).hexdigest(),'leadSourceSha256':hashlib.sha256(LEAD.read_bytes()).hexdigest()}
raw=json.dumps(p,sort_keys=True,separators=(',',':')).encode(); p['payloadSha256']=hashlib.sha256(raw).hexdigest(); Path(__file__).with_name('result.json').write_text(json.dumps(p,sort_keys=True,indent=2)+'\n'); print(json.dumps(p,sort_keys=True,separators=(',',':')))




