"""Verify the betweenness factorization of the geodesic measure:
   p_f(v) = sigma_a(v) * sigma_b(v) / sigma_ab   where
   sigma_a(v) = # shortest B-paths a->v, sigma_b(v) = # shortest B-paths v->b, sigma_ab = # shortest a->b paths.
This holds for v on the geodesic interval (d(a,v)+d(v,b)=d(a,b)=ell-1).
If confirmed, p_f factorizes through layers and we can analyze frame bound via path-counting / Dirichlet.

Also test the LAYER-TRANSITION (flow) law: for v in I_i, define the forward transition
   from layer i-1 to i: p_f restricted satisfies a conservation? Check sum.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, loads

def bcount(info,s):
    """# shortest B-paths from s to each vertex (BFS path counts), and distances."""
    adj=info['adj']; side=info['side']
    dist={s:0}; cnt={s:1}; q=deque([s]); order=[s]
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w]:
                if w not in dist:
                    dist[w]=dist[u]+1; cnt[w]=cnt[u]; q.append(w); order.append(w)
                elif dist[w]==dist[u]+1:
                    cnt[w]+=cnt[u]
    return dist,cnt

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def check(info):
    M=info['M']; ell=info['ell']
    bad=0
    for f in M:
        a,b=f
        da,ca=bcount(info,a)
        db,cb=bcount(info,b)
        sab=ca.get(b,0)
        pf=pf_vec(info,f)
        for v in pf:
            # factorization
            if da.get(v,-1)<0 or db.get(v,-1)<0:
                pred=F(0)
            elif da[v]+db[v]!=ell[f]-1:
                pred=F(0)
            else:
                pred=F(ca[v]*cb[v], sab)
            if pred!=pf[v]:
                bad+=1
                if bad<=3: print(f"   MISMATCH {f} v={v}: pf={pf[v]} pred={pred}")
    return bad

def run(nmin,nmax,limit=None):
    print("=== verify p_f(v)=sigma_a(v)sigma_b(v)/sigma_ab factorization ===")
    tot=0; badtot=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            tot+=1
            badtot+=check(info)
        print(f"  N<={nn}: graphs={tot} factorization mismatches={badtot}",flush=True)

if __name__=="__main__":
    run(7,10,limit=None)
