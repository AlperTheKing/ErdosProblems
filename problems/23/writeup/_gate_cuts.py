"""TASK 2: gate (superlevel/geodesic-ball) cuts G_i = {v: d_B(a,v) <= i}.
CD gives delta_M(G_i) <= delta_B(G_i). Does summing CD over the gates G_i (i=0..h-1)
bound (O ell)_f = sum_v p_f(v) T(v)?

Idea behind a 'gate telescope': T(v) = sum_w K_{vw} where K=P P^T, K_{vw}=sum_g p_g(v)p_g(w).
For the geodesic of f, p_f(v) is supported on layers; relate sum_v p_f(v) T(v) to cut crossings.

Concretely test the natural CD-derived bound:
  (O ell)_f = sum_i L_i,  and  sum over gate-cut budget:
  For each gate G_i, the # of B-edges leaving G_i is delta_B(G_i); CD => delta_M(G_i)<=delta_B(G_i).
  Does sum_{i=0}^{h-1} delta_B(G_i) relate to N*ell(f)?  Also test: is (O ell)_f <= sum_i delta_B(G_i)?
Report exact census + blowups."""
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

def gate_data(info, f):
    """gates G_i={v:d_B(a,v)<=i}; deltaB(G_i)=# B-edges crossing, deltaM(G_i)=# M-edges crossing."""
    n=info['n']; a,b=f; h=info['ell'][f]-1
    da=bdist(info,a)
    Bset=info['Bset']; Mset=info['Mset']
    gates=[]
    for i in range(h+1):
        Gi=set(v for v in range(n) if da.get(v,10**9)<=i)
        dB=sum(1 for (x,y) in Bset if (x in Gi)!=(y in Gi))
        dM=sum(1 for (x,y) in Mset if (x in Gi)!=(y in Gi))
        gates.append((i,Gi,dB,dM))
    return gates, da, h

def analyze(info):
    n=info['n']; T=info['T']; N=n; res=[]
    for f in info['M']:
        pf=pf_vec(info,f)
        gates,da,h=gate_data(info,f)
        Of=sum(pf[v]*T[v] for v in pf)   # (O ell)_f
        # CD holds on each gate?
        cd_ok=all(dM<=dB for (_,_,dB,dM) in gates)
        sumdB=sum(dB for (_,_,dB,_) in gates[:h])  # i=0..h-1
        sumdB_all=sum(dB for (_,_,dB,_) in gates)
        res.append(dict(f=f,h=h,Of=Of,ell=info['ell'][f],N=N,cd_ok=cd_ok,
                        sumdB=sumdB,sumdB_all=sumdB_all,
                        bound1=(Of<=sumdB), bound2=(Of<=sumdB_all),
                        bound3=(sumdB_all<=F(N)*info['ell'][f])))
    return res

def run(nmin,nmax,limit=None):
    print(f"=== gate cuts census N={nmin}..{nmax} ===")
    cd_fail=0; b1=0; b2=0; b3=0; nf=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(info):
                nf+=1
                if not r['cd_ok']: cd_fail+=1
                if not r['bound1']: b1+=1
                if not r['bound2']: b2+=1
                if not r['bound3']: b3+=1
        print(f"  N={nn} done")
    print(f"bad_edges={nf} | CD-on-gates fails:{cd_fail} | (Of<=sum_{{i<h}}dB) fails:{b1} | (Of<=sum_all dB) fails:{b2} | (sum_all dB<=N*ell) fails:{b3}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,5):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs=analyze(info)
        print(f"  C5[{t}] N={n}: cd_ok={all(r['cd_ok'] for r in rs)} b1fail={sum(not r['bound1'] for r in rs)} b2fail={sum(not r['bound2'] for r in rs)} b3fail={sum(not r['bound3'] for r in rs)}")
        for r in rs[:1]:
            print(f"    sample f={r['f']} Of={float(r['Of']):.2f} sumdB={r['sumdB']} sumdB_all={r['sumdB_all']} N*ell={r['N']*r['ell']}")
