"""CLEAN reformulation of certificate A:
   A(f):  <p_f, T - N*1> <= 0   i.e.   sum_v p_f(v) (T_v - N) <= 0   for every bad edge f.
Equivalently  <p_f,T> <= N*ell(f)  (since sum_v p_f(v)=ell(f)).
This IMPLIES CW-T: (KT)_v = sum_f p_f(v)<p_f,T> <= N sum_f p_f(v) ell(f) = N T_v  => rho(K)<=N => Gamma<=N^2.

Interpretation: T_v = load = sum_g ell(g) p_g(v). A(f) says the geodesic-measure p_f of edge f puts
weight <= N on average against the load. Since sum_v p_f(v)=ell(f) (>=5) and the measure has mass 1 per
layer (ell(f) layers), A(f) is exactly: the AVERAGE over f's ell(f) layers of (layer-p_f-avg of T) <= N.
=> SUFFICES: for each layer i of f,  sum_{v in I_i(f)} p_f(v) T_v <= N? NO that gives N ell(f) trivially-- wait
that IS what we want: sum over layers of (<=N) = ... no we need SUM of layer-values <= N*ell, i.e. AVERAGE layer <=N.
So per-layer  sum_{v in I_i(f)} p_f(v) T_v <= N  would give A (sum of ell(f) layers each<=N gives <=N ell(f)). CHECK per-layer.

ALSO test the EVEN CLEANER possibly-provable form via CD: <p_f,T> = sum_g ell(g)<p_f,p_g>. Is there a cut/CD bound?
Report exact: per-edge A residual, AND per-layer  L_i(f):=sum_{v in I_i} p_f(v)T_v <= N ?"""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info,f):
    Ps=info['cyc'][f]; nf=len(Ps); cnt={}
    for P in Ps:
        for v in P: cnt[v]=cnt.get(v,0)+1
    return {v:F(cnt[v],nf) for v in cnt}

def bdist(info,s):
    adj=info['adj']; side=info['side']; d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    return d

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']
    pfs={f:pf_vec(info,f) for f in M}
    T={v:sum(ell[g]*pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    Amax=F(0); Afail=0; LayerMax=F(0); LayerFail=0
    for f in M:
        a,b=f; h=ell[f]-1
        da=bdist(info,a); db=bdist(info,b)
        # A residual
        Ares=sum(pfs[f][v]*(T[v]-F(N)) for v in pfs[f])
        if Ares>0: Afail+=1
        if ell[f]>0 and Ares/(F(N)*F(ell[f]))>Amax: Amax=Ares/(F(N)*F(ell[f]))
        # per-layer
        layer=[F(0)]*(h+1)
        for v in pfs[f]:
            if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h:
                layer[da[v]]+=pfs[f][v]*T[v]
        for x in layer:
            if x>F(N): LayerFail+=1
            r=x/F(N)
            if r>LayerMax: LayerMax=r
    return Afail,Amax,LayerFail,LayerMax

def cycle_blowup(L,q):
    nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return nn,E

def run():
    print("=== A(f): <p_f,T-N> <= 0  AND per-layer L_i(f)<=N, exact census ===")
    Af=0;Am=F(0);Awg=None;Lf=0;Lm=F(0);Lwg=None;ng=0
    for nn in range(7,12):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            ng+=1
            af,am,lf,lm=analyze(info)
            Af+=af; Lf+=lf
            if am>Am: Am=am; Awg=(g6,nn)
            if lm>Lm: Lm=lm; Lwg=(g6,nn)
    print(f"  census graphs={ng}")
    print(f"  [A] <p_f,T-N><=0 : fail={Af} worst(Ares/(N ell))={float(Am):.5f}@{Awg}")
    print(f"  [per-layer] L_i(f)<=N : fail={Lf} worst(L_i/N)={float(Lm):.5f}@{Lwg}")

if __name__=="__main__":
    run()
    print("--- blowups ---")
    for L in [5,7,9]:
        for q in range(2,5):
            nn=L*q
            if nn>26: continue
            n,E=cycle_blowup(L,q); info=loads(n,E)
            if info is None: continue
            af,am,lf,lm=analyze(info)
            print(f"  C{L}[{q}] N={nn}: A fail={af} worst={float(am):.5f} | layer fail={lf} worst(L/N)={float(lm):.5f}")
