"""TASK 1: per-layer loads L_i(f)=sum_{v in I_i(f)} p_f(v) T(v), where
I_i(f)={v: d_B(a,v)=i, d_B(v,b)=h-i}, h=ell(f)-1, geodesic interval layers.
Confirm sum_i L_i = (O ell)_f <= N(h+1); individual L_i can exceed N.
Test cross-layer cancellation: symmetric pair L_i + L_{h-i} <= 2N exactly (Fraction)."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads, blow

def pf_vec(info, f):
    """p_f(v) = fraction of f's shortest B-geodesics through v (Fraction)."""
    Ps = info['cyc'][f]; nf = len(Ps)
    cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def layers(info, f):
    """interval layers I_i: d_B(a,v)=i and d_B(v,b)=h-i. Return dict i->set of v.
    Using f=(a,b), h=ell-1. Compute d_B from a and from b restricted to cut B."""
    adj=info['adj']; side=info['side']; a,b=f; h=info['ell'][f]-1
    def bdist(s):
        d={s:0}; q=deque([s])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        return d
    da=bdist(a); db=bdist(b)
    L={i:set() for i in range(h+1)}
    for v in da:
        if v in db and da[v]+db[v]==h:
            L[da[v]].add(v)
    return L, h

def analyze(info):
    n=info['n']; T=info['T']; N=n
    res=[]
    for f in info['M']:
        pf=pf_vec(info,f)
        L,h=layers(info,f)
        # per-layer load
        Li=[]
        for i in range(h+1):
            li=sum(pf.get(v,F(0))*T[v] for v in L[i])
            Li.append(li)
        total=sum(Li)
        # cross-check: total == (O ell)_f == sum_v pf(v) T(v)
        cross=sum(pf[v]*T[v] for v in pf)
        # symmetric pair check L_i + L_{h-i} <= 2N
        symviol=[]
        for i in range((h+1+1)//2):
            j=h-i
            if i==j:
                s=Li[i]; bnd=F(N)
            else:
                s=Li[i]+Li[j]; bnd=F(2*N)
            if s>bnd: symviol.append((i,j,s,bnd))
        # mass per layer must be 1
        mass=[sum(pf.get(v,F(0)) for v in L[i]) for i in range(h+1)]
        res.append(dict(f=f,h=h,Li=Li,total=total,cross=cross,N=N,
                        symviol=symviol, mass=mass,
                        ell=info['ell'][f]))
    return res

def run_census(nmin,nmax,limit=None):
    print(f"=== census N={nmin}..{nmax} ===")
    glob_symviol=0; glob_total_viol=0; nf=0; ng=0
    maxLi_over_N=F(0); maxLi_g=None
    layermass_bad=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        n_symviol=0; n_total_viol=0; cnt=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            cnt+=1
            for r in analyze(info):
                nf+=1
                assert r['total']==r['cross'], (g6,r['f'],r['total'],r['cross'])
                for m in r['mass']:
                    if m!=1: layermass_bad+=1
                if r['total']>F(r['N'])*r['ell']:
                    n_total_viol+=1; glob_total_viol+=1
                if r['symviol']:
                    n_symviol+=1; glob_symviol+=1
                    if glob_symviol<=5:
                        print(f"   SYMVIOL {g6} f={r['f']} h={r['h']}: {r['symviol']}")
                for i,li in enumerate(r['Li']):
                    if li>F(r['N']):
                        q=li/F(r['N'])
                        if q>maxLi_over_N: maxLi_over_N=q; maxLi_g=(g6,r['f'],i,li,r['N'])
        ng+=cnt
        print(f"  N={nn}: cfg={cnt} | symviol(L_i+L_(h-i)>2N): {n_symviol} | total>N*ell: {n_total_viol}")
    print(f"--- totals: graphs={ng} bad_edges={nf} | sympair_viol={glob_symviol} | totalbound_viol={glob_total_viol} | layermass!=1: {layermass_bad}")
    print(f"--- max L_i/N (overloaded layer): {float(maxLi_over_N):.4f} @ {maxLi_g}")

if __name__=="__main__":
    run_census(7,10)
    print("\n=== blow-ups C5[t] (uniform extremal, T==N) ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: print(f"  t={t}: loads None"); continue
        rs=analyze(info)
        anyviol=any(r['symviol'] for r in rs)
        maxq=max((float(li)/r['N'] for r in rs for li in r['Li']),default=0)
        print(f"  C5[{t}] N={n}: bad_edges={len(rs)} sympair_viol={anyviol} max L_i/N={maxq:.4f} G={info['G']} N^2={n*n}")
