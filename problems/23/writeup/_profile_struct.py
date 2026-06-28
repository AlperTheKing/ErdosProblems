"""Probe the layer-load profile L_i for structure that yields sum_i L_i <= N(h+1).
Candidate cancellations to test EXACTLY:
 (P1) partial-sum / prefix gate: S_k = sum_{i=0}^{k} L_i <= N*(k+1) for all k?  (uniform prefix bound)
 (P2) the COMPLEMENT: tail T_k = sum_{i=k}^{h} L_i <= N*(h-k+1)?
 (P3) symmetric average of prefix & its reverse: (S_k + reverse)/2 ?
 (P4) midpoint-anchored: L_i <= N + (correction telescoping to 0)?
 (P5) Abel summation: sum L_i = sum (S_h) ... look at deltas D_i=L_i - L_{i-1}.
 (P6) endpoints a,b are single vertices: L_0 = p_f(a)T(a)=1*T(a)=T(a) (p_f(a)=1), L_h=T(b).
      Is L_0<=N and L_h<=N always (endpoints not overloaded)?  i.e. are geodesic ENDPOINTS never overloaded?
Record which holds census-wide + blowups, with worst gaps."""
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

def layer_loads(info,f):
    n=info['n']; T=info['T']; a,b=f; h=info['ell'][f]-1
    pf=pf_vec(info,f); da=bdist(info,a); db=bdist(info,b)
    L=[F(0)]*(h+1)
    for v in pf:
        if da.get(v,-1)>=0 and db.get(v,-1)>=0 and da[v]+db[v]==h:
            L[da[v]]+=pf[v]*T[v]
    return L,h

def analyze(info):
    n=info['n']; N=n; res=[]
    for f in info['M']:
        L,h=layer_loads(info,f)
        # prefix and tail bounds
        p_fail=False; t_fail=False
        for k in range(h+1):
            if sum(L[:k+1])>F(N)*(k+1): p_fail=True
            if sum(L[k:])>F(N)*(h-k+1): t_fail=True
        # endpoint loads
        L0,Lh=L[0],L[h]
        endpt_over = (L0>F(N)) or (Lh>F(N))
        res.append(dict(f=f,h=h,L=L,N=N,
                        prefix_ok=not p_fail, tail_ok=not t_fail,
                        endpt_over=endpt_over, L0=L0, Lh=Lh))
    return res

def run(nmin,nmax,limit=None):
    print(f"=== profile census N={nmin}..{nmax} ===")
    pf=0; tf=0; ef=0; nf=0
    ex_p=None; ex_e=None
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in analyze(info):
                nf+=1
                if not r['prefix_ok']:
                    pf+=1
                    if ex_p is None: ex_p=(g6,r['f'],[str(x) for x in r['L']])
                if not r['tail_ok']: tf+=1
                if r['endpt_over']:
                    ef+=1
                    if ex_e is None: ex_e=(g6,r['f'],str(r['L0']),str(r['Lh']),r['N'])
    print(f"bad_edges={nf}")
    print(f"  (P1) prefix S_k<=N(k+1) fails:{pf}  ex={ex_p}")
    print(f"  (P2) tail T_k<=N(h-k+1) fails:{tf}")
    print(f"  (P6) endpoint L_0 or L_h > N fails:{ef}  ex={ex_e}")

if __name__=="__main__":
    run(7,10)
    print("\n=== blowups ===")
    for t in range(1,6):
        n,E=blow(t); info=loads(n,E)
        if info is None: continue
        rs=analyze(info)
        print(f"  C5[{t}] N={n}: prefix_fail={sum(not r['prefix_ok'] for r in rs)} tail_fail={sum(not r['tail_ok'] for r in rs)} endpt_over={sum(r['endpt_over'] for r in rs)}")
