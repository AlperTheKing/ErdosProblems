"""STRATEGY-1 charging probe. Goal: prove sum_v p_f(v) S(v) <= N  (ROWSUM-O).

Key reformulation:
  C(f) = sum_v p_f(v) S(v) = sum_g <p_f,p_g>.
A single shortest f-geodesic C visits exactly ell(f) vertices, one per layer I_i(f), i=0..h (h=ell-1).
With p_f the layer-uniform measure (sum_{v in I_i} p_f(v)=1), C(f) = sum_i E_{v~p_f|I_i}[ S(v) ].

We want C(f) <= N. Since there are ell(f) layers, this means the AVERAGE layer-S-value is <= N/ell(f).
Equivalently sum_i (layer-avg S) <= N.

Idea A (vertex-charge): assign to each vertex w a "charge" c_{f}(w) = sum_i p_f-weight that 'sees' w via S.
Actually S(w) is the same for every f; the f-specific part is the p_f weighting.

We probe several EXACT candidate inequalities that would IMPLY ROWSUM-O, focusing on the geometry
of S along f's geodesic interval. We work in the bipartite cut graph B (side= max-cut bipartition).

Observables per bad edge f (exact Fraction):
 1. C(f), and C(f)-N.
 2. layer profile a_i = sum_{v in I_i} p_f(v) S(v)   (the per-layer contribution; sum_i a_i = C(f)).
 3. Symmetry: a_i vs a_{h-i}.
 4. The 'B-degree budget': for each vertex v on f's interval, how many bad edges g have a geodesic through v,
    and is S(v) controlled by deg_B(v) or by the number of bad edges incident-ish.
 5. TEST: a_i <= |I_i| ? (layer size). And sum_i |I_i| relation to N.
 6. TEST the 'fractional Hall' / assignment idea: does there exist weights so that S mass is charged <=1 per vertex.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def bdist(info,s):
    adj=info['adj']; side=info['side']
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    res=[]
    for f in M:
        a,b=f; h=ell[f]-1
        da=bdist(info,a)
        # layers
        layers=[[] for _ in range(h+1)]
        for v in pfs[f]:
            i=da.get(v,-1)
            if 0<=i<=h: layers[i].append(v)
        a_i=[sum(pfs[f][v]*S[v] for v in layers[i]) for i in range(h+1)]
        Cf=sum(a_i)
        Lsizes=[len(layers[i]) for i in range(h+1)]
        res.append(dict(f=f,h=h,ell=ell[f],Cf=Cf,a_i=a_i,Lsizes=Lsizes,N=N,
                        layers=layers, S={v:S[v] for v in pfs[f]}))
    return res,S

def run(nmin,nmax,limit=None):
    # Look at where the worst C(f)/N is and inspect a_i / layer structure
    print(f"=== charge probe N={nmin}..{nmax} ===")
    worst=F(0); winfo=None
    # candidate: a_i <= 1 for all i? (then C(f)<=ell(f)<=? no). Check max a_i.
    maxa=F(0); maxa_g=None
    # candidate: sum_i a_i <= sum_i (max S in layer i)? trivial.
    # candidate: a_i + a_{h-i} <= 2 ?  (symmetric pair) -> already ruled out per memory. skip.
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            rs,S=analyze(info)
            for r in rs:
                if r['Cf']/F(r['N'])>worst: worst=r['Cf']/F(r['N']); winfo=(g6,r['f'],[float(x) for x in r['a_i']],r['Lsizes'],r['N'],float(r['Cf']))
                m=max(r['a_i']) if r['a_i'] else F(0)
                if m>maxa: maxa=m; maxa_g=(g6,r['f'])
    print(f"worst C(f)/N={float(worst):.5f} @ {winfo}")
    print(f"max single-layer a_i = {float(maxa):.4f} @ {maxa_g}")

if __name__=="__main__":
    run(7,10, limit=2000)
    print("\n--- detailed inspection of a tight extremal C5[3] ---")
    n,E=blow(3); info=loads(n,E)
    rs,S=analyze(info)
    r=rs[0]
    print(f"  f={r['f']} ell={r['ell']} Cf={r['Cf']} N={r['N']}")
    print(f"  layer sizes={r['Lsizes']}")
    print(f"  a_i={[str(x) for x in r['a_i']]}")
    print(f"  S on interval={ {v:str(S[v]) for v in r['S']} }")
