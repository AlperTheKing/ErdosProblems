"""Push the clean certificate  C(f) := sum_v p_f(v) S(v) <= N,  S(v)=sum_g p_g(v).
Implies rho(O)<=maxrowsum(O)=max_f C(f) <= N => SPEC => Cycle-SM => Gamma<=N^2.

Probe structure for a proof:
 (1) sum_v S(v) = sum_g ell(g) =: L (total geodesic length).  max S(v)=? distribution.
 (2) Per-layer: C(f)=sum_i [ sum_{v in I_i(f)} p_f(v) S(v) ] = sum_i <p_f|I_i, S>. mass(I_i)=1.
     So C(f)=sum_i (p_f-weighted layer-avg of S). Is each layer-avg <= N? (=> trivial sum<=N(h+1), too weak;
     we need sum<=N not N(h+1)). The RIGHT statement is the layer-AVERAGED S-avg <= N/(h+1)?? No:
     C(f)<=N means AVERAGE over the ell(f)=h+1 layers of (layer S-avg) <= N/(h+1)? No: sum<=N, h+1 terms,
     so average layer-S-avg <= N/(h+1). That's STRONG (each ~N/ell). Check per-layer S-avg values.
 (3) Compare C(f) to a 'self + others': C(f)=sum_v p_f(v)^2 + sum_v p_f(v) S_{-f}(v), S_{-f}=S-p_f.
     diag term sum_v p_f(v)^2 = O_ff = ||p_f||^2 <= ell(f). off term = sum_{g!=f} O_fg.
 (4) Does CD give it? C(f)=sum_g O_fg. Try cut/Crofton on the UNWEIGHTED incidence.
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
    Ltot=sum(S.values())  # = sum_g ell(g)
    maxS=max(S.values()) if S else F(0)
    out=[]
    for f in M:
        a,b=f; h=ell[f]-1
        da=bdist(info,a); db=bdist(info,b)
        # per layer p_f-weighted avg of S
        layeravg=[F(0)]*(h+1)
        for v in pfs[f]:
            if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h:
                layeravg[da[v]]+=pfs[f][v]*S[v]
        Cf=sum(layeravg)
        # diag + off
        diag=sum(pfs[f][v]*pfs[f].get(v,F(0)) for v in pfs[f])  # ||p_f||^2
        out.append(dict(f=f,h=h,ell=ell[f],N=N,Cf=Cf,layeravg=layeravg,
                        diag=diag, maxlayeravg=max(layeravg),
                        layer_le_N=all(x<=F(N) for x in layeravg)))
    return out, Ltot, maxS

def run(nmin,nmax,limit=None):
    print(f"=== S-certificate census N={nmin}..{nmax} ===")
    cfail=0; layerfail=0; nf=0; worstCf=F(0); wg=None
    worst_maxlayer=F(0); wlg=None; maxS_over_N=F(0); msg=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            rs,Ltot,maxS=analyze(info)
            if maxS/F(n)>maxS_over_N: maxS_over_N=maxS/F(n); msg=(g6,str(maxS),n)
            for r in rs:
                nf+=1
                if r['Cf']>F(r['N']): cfail+=1
                if r['Cf']/F(r['N'])>worstCf: worstCf=r['Cf']/F(r['N']); wg=(g6,r['f'],str(r['Cf']),r['N'])
                if not r['layer_le_N']: layerfail+=1
                if r['maxlayeravg']/F(r['N'])>worst_maxlayer: worst_maxlayer=r['maxlayeravg']/F(r['N']); wlg=(g6,r['f'],str(r['maxlayeravg']),r['N'])
    print(f"bad_edges={nf} | C(f)=sum p_f S > N fails:{cfail} | per-layer S-avg>N fails:{layerfail}")
    print(f"  worst C(f)/N = {float(worstCf):.5f} @ {wg}")
    print(f"  worst per-layer S-avg / N = {float(worst_maxlayer):.5f} @ {wlg}")
    print(f"  worst max_v S(v)/N = {float(maxS_over_N):.5f} @ {msg}")

if __name__=="__main__":
    run(7,11)
    print("\n=== blowups (extremal, expect C(f)=N) ===")
    for t in range(1,7):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs,Ltot,maxS=analyze(info)
        cf=max(float(r['Cf']) for r in rs)
        print(f"  C5[{t}] N={n}: max C(f)={cf:.3f} (=N? {abs(cf-n)<1e-9}) maxS={float(maxS):.3f} maxS/N={float(maxS)/n:.3f}")
