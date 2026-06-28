"""COAREA probe: express (O ell)_f via gate cuts and CD.

The load identity:  T(v) = sum_g ell(g) p_g(v)  (P1).  And sum_v T(v)=Gamma.
For a fixed bad edge f with geodesic interval [a..b], gates G_i={v:d_B(a,v)<=i}, i=0..h, h=ell(f)-1.

KEY ATTEMPT (coarea for a single geodesic measure p_f):
  (O ell)_f = sum_v p_f(v) T(v).
  Since p_f has mass 1 in each layer (sum_{v in I_i}p_f(v)=1) and is supported on layers I_0..I_h,
  write (O ell)_f = sum_{i=0}^h <p_f|_{I_i}, T>.
  We want to compare to N*(h+1). Equivalent: AVERAGE of layer-load <= N.

NEW IDEA — gate-difference (coarea of T itself):
  Define phi(v) = d_B(a,v) (a 1-Lipschitz integer function on B-graph).
  Crofton/coarea:  for any edge (x,y) in B, |phi(x)-phi(y)|=1, and
  sum_{i=0}^{h-1} delta_B(G_i) = sum_{(x,y) in B} #{i: G_i separates x,y} = sum_{(x,y) in B, both within dist h} |phi(x)-phi(y)| capped.
  This counts B-edges by gate, = 'B-edge length' in phi-metric.
  Likewise sum_i delta_M(G_i) = sum_{(x,y) in M} (gate-separations) = M-edge phi-length.
  CD per gate => sum_i delta_M(G_i) <= sum_i delta_B(G_i).  [verify, and that RHS<=N*ell.]

  Then RELATE sum_i delta_M(G_i) to the load.  For the bad edge g=(x,y) in M, the gate-separation
  count = |phi(x)-phi(y)| (number of gates strictly between). Conjecture: this is tied to ell(g)*<p_f,p_g>?
Test all these exactly."""
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
    n=info['n']; T=info['T']; N=n; M=info['M']; ell=info['ell']
    Bset=info['Bset']; Mset=info['Mset']
    res=[]
    O={}  # overlap O_{f,g}=<p_f,p_g>
    pfs={f:pf_vec(info,f) for f in M}
    for f in M:
        for g in M:
            pf=pfs[f]; pg=pfs[g]
            O[(f,g)]=sum(pf[v]*pg.get(v,F(0)) for v in pf)
    for f in M:
        a,b=f; h=ell[f]-1
        da=bdist(info,a)
        phi={v:da.get(v,10**9) for v in range(n)}
        Of=sum(pfs[f][v]*T[v] for v in pfs[f])
        # gate-separation phi-length of M edges and B edges (capped within [0,h] gates i=0..h-1)
        def gatesep(edgeset):
            tot=0
            for (x,y) in edgeset:
                px,py=phi[x],phi[y]
                if px>10**8 or py>10**8: continue
                lo,hi=min(px,py),max(px,py)
                # number of gates G_i (i=0..h-1) with exactly one endpoint inside, i.e. lo<=i<hi
                tot+=sum(1 for i in range(h) if lo<=i<hi)
            return tot
        Mlen=gatesep(Mset); Blen=gatesep(Bset)
        # sum_i deltaM(G_i), sum_i deltaB(G_i), i=0..h-1  (equal to Mlen,Blen by coarea)
        # CD-derived candidate: is Of <= something * Blen? compare ratios
        # Also: ell(g)*O_{fg} summed = Of (since Of=sum_g ell(g)O_{fg})
        Of2=sum(ell[g]*O[(f,g)] for g in M)
        res.append(dict(f=f,h=h,ell=ell[f],N=N,Of=Of,Of2=Of2,Mlen=Mlen,Blen=Blen,
                        cd=(Mlen<=Blen), Bbound=(Blen<=F(N)*ell[f])))
    return res

def run(nmin,nmax,limit=None):
    print(f"=== coarea census N={nmin}..{nmax} ===")
    cdfail=0; bfail=0; nf=0; idmismatch=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(info):
                nf+=1
                if r['Of']!=r['Of2']: idmismatch+=1
                if not r['cd']: cdfail+=1
                if not r['Bbound']: bfail+=1
    print(f"bad_edges={nf} | Of==sum ell(g)O_fg mismatch:{idmismatch} | M-phi-len<=B-phi-len(CD) fails:{cdfail} | B-phi-len<=N*ell fails:{bfail}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs=analyze(info)
        print(f"  C5[{t}] N={n}: cdfail={sum(not r['cd'] for r in rs)} Bboundfail={sum(not r['Bbound'] for r in rs)}")
        r=rs[0]; print(f"    f={r['f']} Of={float(r['Of']):.1f} Mlen={r['Mlen']} Blen={r['Blen']} N*ell={r['N']*r['ell']}")
