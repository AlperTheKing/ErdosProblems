import random
from harness import *

def greedy_delete(N, edges, target_e, batch_eval=True):
    cur=list(edges)
    while len(cur)>target_e:
        # evaluate deleting each candidate edge in one batched call
        cands=cur
        graphs=[(N,[x for x in cur if x!=ed]) for ed in cands]
        res=evalmany(graphs)
        # pick deletion that keeps beta highest
        best_b=-1; best_idx=0
        for i,(b,e,mc,d,tf) in enumerate(res):
            if b>best_b:
                best_b=b; best_idx=i
        cur=[x for x in cur if x!=cands[best_idx]]
    return cur

random.seed(1)
N,edges=c5_blowup_parts([4,4,4,4,4])  # N=20, 80 edges
for tgt in [64,60,56,52,50]:
    res=greedy_delete(N,list(edges),tgt)
    b,e,mc,d,tf=evalone(N,res)
    print(f"N=20 C5[4]->del to e={tgt}: beta={b} e={e} maxcut={mc} dens={d:.4f} tf={tf} band={in_band(N,e)} N^2/25=16 ratio={b/16:.3f}")
