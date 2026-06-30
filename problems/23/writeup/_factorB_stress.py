"""Pre-stress factorization (A)+(B) on LARGER non-gamma-min cuts (N=11,12) than _factor_gate's census N<=10,
   to catch boundary cases for lemma (B) [the remaining open problem] before committing to its proof.
   Random triangle-free connected graphs N in {11,12}, ALL max cuts (negative ports live on non-gamma-min cuts).
   Reuses _factor_gate.run (exact (A)+(B) checks).  Usage: python _factorB_stress.py <seed> <count>
"""
import sys, random
import _factor_gate as fg
import _crux_extract as cx
from _bdef_construct import is_triangle_free

def main():
    seed=int(sys.argv[1]) if len(sys.argv)>1 else 11
    count=int(sys.argv[2]) if len(sys.argv)>2 else 150
    rng=random.Random(seed)
    acc=dict(ports=0,A_fail=0,B_fail=0,Bk=0,Bmin=None,A_ex=None,B_ex=None)
    made=0; tries=0; rowsneg=0
    while made<count and tries<count*300:
        tries+=1
        nn=rng.choice([11,12])
        p=rng.uniform(0.14,0.34)
        E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not E or not is_triangle_free(nn,E): continue
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        # connected check
        seen={0}; stk=[0]
        while stk:
            u=stk.pop()
            for w in adj[u]:
                if w not in seen: seen.add(w); stk.append(w)
        if len(seen)!=nn: continue
        made+=1
        p0=acc['ports']
        fg.run("rand%d_%d"%(seed,made),nn,adj,E,cx.all_max_cuts(nn,adj,E)[1],acc)
        if made%25==0:
            print("  made=%d ports=%d A_fail=%d B_fail=%d"%(made,acc['ports'],acc['A_fail'],acc['B_fail']),flush=True)
    print("="*55)
    print("random N in {11,12} graphs tested:",made)
    print("negative ports:",acc['ports'])
    print("LEMMA A failures:",acc['A_fail'],acc['A_ex'] or '')
    print("LEMMA B failures:",acc['B_fail'],"over",acc['Bk'],"checks",acc['B_ex'] or '')
    print("min Lemma B margin:",str(acc['Bmin']))
    print("VERDICT:", "A+B HOLD on N=11,12 sample" if acc['A_fail']==0 and acc['B_fail']==0 else "FAILS")

if __name__=="__main__":
    main()
