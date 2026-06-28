"""Attack ROWSUM-O = sum_v p_f(v) S(v) <= N via CD/cut certificates and structural bounds.
S(v)=sum_g p_g(v).  Note sum_v S(v)=L=sum_g ell(g).

Key reformulations to test EXACTLY (census small + blowups):
 (R1) Per-layer of f:  sum_v p_f(v) S(v) = sum_{i=0}^{h} [ sum_{v in I_i(f)} p_f(v) S(v) ] = sum_i a_i,
      where a_i = layer-i p_f-weighted avg of S, and layer mass sum_{v in I_i}p_f(v)=1.
      So ROWSUM-O <=> sum_i a_i <= N <=> AVERAGE over the ell(f) layers of a_i <= N/ell(f).
      On blowups a_i = N/ell(f) exactly (equipartition). Test the per-layer a_i values; is there a
      'gate-monotone' or convexity structure giving sum a_i <= N?
 (R2) S restricted to f's geodesic vs S elsewhere. Is sum_v p_f(v) S(v) <= sum_{v: d_B(a,v)+d_B(v,b)=h} S(v)
      (drop p_f<=1 only on the INTERVAL, not all supp)? = sum over geodesic-interval of S. Test <=N.
 (R3) Counting: S(v) = sum_g p_g(v). For each g, p_g(v)>0 iff v on a shortest B-geodesic of g.
      sum_v p_f(v) S(v) = sum_g sum_v p_f(v) p_g(v) = sum_g <p_f,p_g> = sum_g O_fg.
      For g with disjoint interval from f, O_fg=0. So only g whose geodesic-interval MEETS f's interval contribute.
      Test: #{g: O_fg>0} (the 'interacting' bad edges) and whether sum_g O_fg <= N via a charging
      'each vertex charged <=1 total across the f-interval'.
 (R4) THE INTERVAL-CHARGING IDENTITY: assign to vertex v the value p_f(v)*S(v). Total = ROWSUM-O.
      Since p_f(v)<=1, p_f(v)*S(v) <= S(v), and = S(v) only where p_f(v)=1 (unique-geodesic vertices).
      Test charge per vertex <= 1? i.e. p_f(v)*S(v) <= 1 for each v? then sum <= |supp|<=N. (likely FALSE)
Report exact."""
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
    out=[]
    for f in M:
        a,b=f; h=ell[f]-1
        da=bdist(info,a); db=bdist(info,b)
        # interval = all v with da+db=h (geodesic interval, may include non-shortest-of-f? no: shortest only)
        interval=[v for v in range(n) if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h]
        Cf=sum(pfs[f][v]*S[v] for v in pfs[f])
        # R2: sum over interval of S(v)
        R2=sum(S[v] for v in interval)
        # R4: max per-vertex charge p_f(v)*S(v)
        maxcharge=max((pfs[f][v]*S[v] for v in pfs[f]), default=F(0))
        # R1: layer avgs
        a_i={}
        for v in pfs[f]:
            if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h:
                a_i[da[v]]=a_i.get(da[v],F(0))+pfs[f][v]*S[v]
        out.append(dict(f=f,h=h,ell=ell[f],N=N,Cf=Cf,R2=R2,maxcharge=maxcharge,
                        a_i=[a_i.get(i,F(0)) for i in range(h+1)],
                        R2_ok=(R2<=F(N)), R4_ok=(maxcharge<=F(1))))
    return out

def run(nmin,nmax,limit=None):
    print(f"=== ROWSUM-O CD/structure census N={nmin}..{nmax} ===")
    nf=0; r2fail=0; r4fail=0; worstR2=F(0); wr2=None; maxcharge=F(0); wmc=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(info):
                nf+=1
                if not r['R2_ok']:
                    r2fail+=1
                    if r['R2']/F(r['N'])>worstR2: worstR2=r['R2']/F(r['N']); wr2=(g6,r['f'],str(r['R2']),r['N'])
                if not r['R4_ok']:
                    r4fail+=1
                    if r['maxcharge']>maxcharge: maxcharge=r['maxcharge']; wmc=(g6,r['f'],str(r['maxcharge']))
    print(f"bad_edges={nf}")
    print(f"  (R2) sum_{{interval}} S <= N fails:{r2fail}  worst R2/N={float(worstR2):.4f} @ {wr2}")
    print(f"  (R4) max per-vertex charge p_f*S <=1 fails:{r4fail}  max charge={float(maxcharge):.4f} @ {wmc}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs=analyze(info)
        r=rs[0]
        print(f"  C5[{t}] N={n}: Cf={float(r['Cf']):.2f} R2(interval-S)={float(r['R2']):.2f} maxcharge={float(r['maxcharge']):.3f} a_i={[float(x) for x in r['a_i']]}")
