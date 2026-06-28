"""Codex ASK (blocks 6,7): pin N=11 two-edge failures with HIGH-EFFORT optimizer, test triple support,
dump KKT-core geometry. Writes _kktcore_dump_N11_twoedge.txt.
L(y)=sum_f(sum_i sqrt w_fi)^2, w_fi=sum_{v in I_i(f)} y_v p_f(v), simplex sum y=1.
For failing graphs: full maxL, best-pair, best-triple; supp(y*); overloaded C={T>N}; min k covering supp;
layer weights; overlap matrix O_fg + layer-overlap; KKT residual; structural target: supp(y*) in overloaded
shortest-B-geodesic closure?"""
import numpy as np, subprocess, itertools
from collections import deque
from scipy.optimize import minimize
from _h import dec, GENG, loads
from _layerprice import layers_of

def setup(info):
    n=info['n']; M=info['M']
    L=[(f,)+layers_of(info,f) for f in M]
    return L,n,M

def Lval(L,y):
    tot=0.0
    for (f,lay,pf,h) in L:
        s=sum(np.sqrt(max(sum(y[v]*pf[v] for v in lay[i]),0.0)) for i in range(h+1))
        tot+=s*s
    return tot

def maximizeL(L,n,allowed=None,restarts=20):
    idx=list(range(n)) if allowed is None else sorted(allowed)
    m=len(idx)
    if m==0: return 0.0,np.zeros(n)
    rng=np.random.default_rng(12345)
    cons=[{'type':'eq','fun':lambda z:z.sum()-1.0}]; bnds=[(0.0,1.0)]*m
    best=-1.0; bz=None
    def neg(z):
        y=np.zeros(n)
        for k,v in enumerate(idx): y[v]=max(z[k],0.0)
        return -Lval(L,y)
    starts=[np.full(m,1.0/m)]+[rng.dirichlet(np.ones(m)) for _ in range(restarts)]
    for z0 in starts:
        r=minimize(neg,z0,method='SLSQP',bounds=bnds,constraints=cons,options={'maxiter':500,'ftol':1e-12})
        if -r.fun>best: best=-r.fun; bz=r.x
    y=np.zeros(n)
    for k,v in enumerate(idx): y[v]=max(bz[k],0.0)
    return best,y

def overload_closure(info,C):
    """C + all vertices on shortest B-geodesics between pairs of C-vertices."""
    n=info['n']; adj=info['adj']; side=info['side']
    def geos_between(s,t):
        dist={s:0}; pred={s:[]}; layer=[s]
        while layer:
            nxt=[]
            for u in layer:
                for w in adj[u]:
                    if side[u]!=side[w]:
                        if w not in dist: dist[w]=dist[u]+1; pred[w]=[u]; nxt.append(w)
                        elif dist[w]==dist[u]+1: pred[w].append(u)
            layer=nxt
        if t not in dist: return set()
        seen=set(); st=[t]
        while st:
            x=st.pop(); seen.add(x)
            for p in pred[x]:
                if p not in seen: st.append(p)
        return seen
    clo=set(C)
    for s,t in itertools.combinations(sorted(C),2):
        clo|=geos_between(s,t)
    return clo

def mink_cover(L,M,supp):
    supps=[set(pf.keys()) for (f,lay,pf,h) in L]
    for k in range(1,len(M)+1):
        for comb in itertools.combinations(range(len(M)),k):
            u=set()
            for ei in comb: u|=supps[ei]
            if supp<=u: return k,[M[ei] for ei in comb]
    return len(M),list(M)

def analyze(g6,info,out):
    L,n,M=setup(info); N=n; T=[float(t) for t in info['T']]
    gmax,ystar=maximizeL(L,n,restarts=24)
    supps=[set(pf.keys()) for (f,lay,pf,h) in L]
    bestpair=0.0; bpf=None
    for a,b in itertools.combinations(range(len(M)),2):
        v,_=maximizeL(L,n,allowed=supps[a]|supps[b],restarts=8)
        if v>bestpair: bestpair=v; bpf=(M[a],M[b])
    pairgap=gmax-bestpair
    besttri=bestpair; btf=None
    if pairgap>1e-6 and len(M)>=3:
        for a,b,c in itertools.combinations(range(len(M)),3):
            v,_=maximizeL(L,n,allowed=supps[a]|supps[b]|supps[c],restarts=6)
            if v>besttri: besttri=v; btf=(M[a],M[b],M[c])
    trigap=gmax-besttri
    supp=set(v for v in range(n) if ystar[v]>1e-7)
    C=set(v for v in range(n) if T[v]>N+1e-9)
    k,kedges=mink_cover(L,M,supp)
    clo=overload_closure(info,C)
    in_clo = supp<=clo
    out.write(f"\n==== {g6}  N={n}  |M|={len(M)}  Gamma={info['G']} ====\n")
    out.write(f"  full maxL = {gmax:.6f}  (<=N: {gmax<=N+1e-4})\n")
    out.write(f"  best PAIR maxL = {bestpair:.6f}  pair gap = {pairgap:+.6f}  @ {bpf}\n")
    if pairgap>1e-6:
        out.write(f"  best TRIPLE maxL = {besttri:.6f}  triple gap = {trigap:+.6f}  @ {btf}\n")
    out.write(f"  supp(y*) = {sorted(supp)}  (|supp|={len(supp)})\n")
    out.write(f"  overloaded C={{T>N}} = {sorted(C)}  (T = {[round(t,3) for t in T]})\n")
    out.write(f"  min #edges whose interval-union covers supp(y*): k = {k}  via edges {kedges}\n")
    out.write(f"  overloaded shortest-B-geodesic closure = {sorted(clo)}\n")
    out.write(f"  STRUCTURAL TARGET (4): supp(y*) subset of overloaded-geodesic-closure ? {in_clo}\n")
    # active edges = the covering edges; dump layer weights + overlaps
    active=[M.index(e) for e in kedges]
    out.write("  active-edge layer weights w[f,i] (under y*):\n")
    for ei in active:
        (f,lay,pf,h)=L[ei]
        w=[round(sum(ystar[v]*pf[v] for v in lay[i]),4) for i in range(h+1)]
        out.write(f"    edge {f} ell={info['ell'][f]}: layers={{i:sorted(lay[i]) for i}}={{ {', '.join(str(i)+':'+str(sorted(lay[i])) for i in range(h+1))} }}\n")
        out.write(f"      w[f,.]={w}  p_f on supp={{ {', '.join(str(v)+':'+str(round(pf[v],3)) for v in sorted(supp) if v in pf)} }}\n")
    # overlap matrix among active edges
    out.write("  overlap O_fg = sum_v p_f p_g among active edges:\n")
    for a in active:
        row=[]
        for b in active:
            (fa,laya,pfa,ha)=L[a]; (fb,layb,pfb,hb)=L[b]
            o=sum(pfa.get(v,0)*pfb.get(v,0) for v in set(pfa)|set(pfb))
            row.append(round(o,3))
        out.write(f"    {M[a]}: {row}\n")
    return pairgap,trigap,k,in_clo

if __name__=="__main__":
    fname="_kktcore_dump_N11_twoedge.txt"
    out=open(fname,"w")
    # collect failing N=11 graphs (two-edge gap>1e-3) starting with the known one + scan
    known=["J?`@C_W{Ck?"]
    out.write("KKT-core dump: N=11 two-edge support failures (high-effort optimizer)\n")
    res=[]
    for g6 in known:
        n,E=dec(g6); info=loads(n,E)
        if info is None: out.write(f"{g6}: not loadable\n"); continue
        res.append((g6,)+analyze(g6,info,out))
    # scan to find a 2nd failure (stride)
    found=1
    out2=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()[::40]
    for g6 in out2:
        if found>=2: break
        if g6 in known: continue
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        L,n,M=setup(info)
        if len(M)<3: continue
        gmax,_=maximizeL(L,n,restarts=10)
        supps=[set(pf.keys()) for (f,lay,pf,h) in L]
        bp=max(maximizeL(L,n,allowed=supps[a]|supps[b],restarts=4)[0] for a,b in itertools.combinations(range(len(M)),2))
        if gmax-bp>1e-3:
            res.append((g6,)+analyze(g6,info,out)); found+=1
    out.write("\nSUMMARY:\n")
    for r in res:
        out.write(f"  {r[0]}: pairgap={r[1]:+.4f} trigap={r[2]:+.4f} mink={r[3]} supp_in_closure={r[4]}\n")
    out.close()
    print(open(fname).read())
