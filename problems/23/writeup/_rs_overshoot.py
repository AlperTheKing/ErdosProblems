"""Find graphs where the layer-MAX bound (sum_i max_{I_i} S) overshoots N, but rowsum_f stays <= N.
These are the cases where anti-concentration (p_f-weighting) is doing real work."""
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact
from collections import deque
import subprocess
GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'

def analyze(info):
    P,M,ell,n=pf_exact(info)
    adj=info['adj']; side=info['side']
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    res=[]
    for fi,f in enumerate(M):
        a,b=f
        d={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        L=ell[f]; pf=P[fi]
        layers={}
        for v in pf: layers.setdefault(d[v],[]).append(v)
        rowsum=sum(pf[v]*S[v] for v in pf)
        maxsum=F(0)
        for i in range(L):
            vs=layers.get(i,[])
            maxsum+=max((S[v] for v in vs),default=F(0))
        res.append((f,L,rowsum,maxsum))
    return res,n

if __name__=="__main__":
    big_overshoot=[]
    for nn in [8,9,10,11]:
        out=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        # subsample large censuses
        stride = 1 if nn<=9 else (5 if nn==10 else 40)
        cnt=0; over_cnt=0; worst_gap=None
        for g6 in out[::stride]:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            cnt+=1
            res,n=analyze(info)
            for (f,L,rs,maxsum) in res:
                if maxsum>n:  # layer-max bound overshoots
                    over_cnt+=1
                    gap=maxsum-rs  # how much anti-conc saved
                    if worst_gap is None or maxsum-n>worst_gap[0]:
                        worst_gap=(maxsum-n, g6, f, L, rs, maxsum, n)
                # sanity: rowsum must be <= n (ROWSUM-O)
                assert rs<=n, (g6,f,L,str(rs),n)
        print('N=%d (stride %d): %d graphs, %d (edge) overshoot-cases'%(nn,stride,cnt,over_cnt))
        if worst_gap:
            print('   worst overshoot: maxsum-N=%s g6=%s ell=%d rowsum=%s maxsum=%s N=%d'%(
                str(worst_gap[0]),worst_gap[1],worst_gap[3],str(worst_gap[4]),str(worst_gap[5]),worst_gap[6]))
    print('All rowsum<=N assertions passed.')
