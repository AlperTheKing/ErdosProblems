import itertools, random
from beta_tools import is_triangle_free, beta, maxcut_fast

def c5_blowup_parts(sizes):
    # sizes: list of 5 part sizes
    offs=[0]
    for s in sizes: offs.append(offs[-1]+s)
    N=offs[5]
    edges=[]
    for p in range(5):
        q=(p+1)%5
        for i in range(sizes[p]):
            for j in range(sizes[q]):
                edges.append((offs[p]+i, offs[q]+j))
    return N, edges, offs, sizes

def band_ok(N,e):
    d=2*e/(N*N)
    return 0.2486 < d < 0.3197

def report(name,N,edges):
    tf,wit=is_triangle_free(N,edges)
    if not tf:
        return f"{name}: NOT triangle-free {wit}"
    b,ee,mc=beta(N,edges)
    d=2*ee/(N*N)
    target=N*N/25.0
    flag = "IN-BAND" if 0.2486<d<0.3197 else ""
    return f"{name}: N={N} e={ee} beta={b} density={d:.4f} N^2/25={target:.2f} ratio={b/target:.3f} {flag}"

# Strategy 1: C5[4] (N=20, density 0.4, beta 16) then delete edges to drop into band.
# Band for N=20: e in (49.7,63.9) -> e in [50,63]. We have 80 edges. Delete 17-30 edges.
# Delete edges to minimize beta loss. Random greedy.
N,edges,offs,sizes=c5_blowup_parts([4,4,4,4,4])
print(report("C5[4] full", N, edges))

# greedy: repeatedly delete the edge whose removal least decreases beta (or even increases)
def greedy_delete_to_target(N, edges, target_e, trials=1):
    edges=list(edges)
    best_overall=None
    cur=list(edges)
    while len(cur)>target_e:
        b0,_,_=beta(N,cur)
        # sample candidate edges to remove
        cand=cur if len(cur)<=80 else random.sample(cur,80)
        best_b=-1; best_i=None
        for ed in cand:
            tmp=[x for x in cur if x!=ed]
            b,_,_=beta(N,tmp)
            if b>best_b:
                best_b=b; best_i=ed
        cur=[x for x in cur if x!=best_i]
    return cur

random.seed(1)
res=greedy_delete_to_target(N, edges, 63)
print(report("C5[4]->63 greedy", N, res))
res2=greedy_delete_to_target(N, edges, 55)
print(report("C5[4]->55 greedy", N, res2))
res3=greedy_delete_to_target(N, edges, 50)
print(report("C5[4]->50 greedy", N, res3))
