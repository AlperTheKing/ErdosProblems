"""Exact test of the FULL Open Capacity Lemma (Schur draft), the genuine crux:
A = N I - K.  O={T>N}, Q=V\O.  Solve A_QQ g = (N-T)_Q exactly.
Claims:  0<=g<=1  AND  N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0  for all o in O.
Equivalently phi=1 on O, phi=1-g on Q is positive N-superharmonic for K.
Test exactly (Fraction) on N=23 and census. Also confirm A_QQ nonsingular (after dropping zero-row comps).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr, GENG
from _satzmu_conn import struct_for_side

def build_K(adj, side, n):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    pf_list=[]
    for f in M:
        Ps=cyc[f]; k=len(Ps); pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        pf_list.append(pf)
    K=[[F(0)]*n for _ in range(n)]
    for pf in pf_list:
        for u in pf:
            for w in pf:
                K[u][w]+=pf[u]*pf[w]
    Tvec=[sum(K[v][j] for j in range(n)) for v in range(n)]
    return K, Tvec

def solve(A, b):
    """Exact Gaussian elimination; returns x or None if singular."""
    m=len(b)
    M=[[A[i][j] for j in range(m)]+[b[i]] for i in range(m)]
    for c in range(m):
        piv=None
        for r in range(c,m):
            if M[r][c]!=0: piv=r; break
        if piv is None: return None
        M[c],M[piv]=M[piv],M[c]
        pv=M[c][c]
        M[c]=[x/pv for x in M[c]]
        for r in range(m):
            if r!=c and M[r][c]!=0:
                fac=M[r][c]
                M[r]=[M[r][j]-fac*M[c][j] for j in range(m+1)]
    return [M[i][m] for i in range(m)]

def test(adj,side,n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=F(n)
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(O=0, status="no-O", g_oob=0, o_fail=[], singular=False)
    # A_QQ = N I - K restricted to Q; b=(N-T)_Q
    idx={v:i for i,v in enumerate(Q)}; m=len(Q)
    AQQ=[[ (N if Q[i]==Q[j] else F(0)) - K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    b=[N-T[Q[i]] for i in range(m)]
    g=solve(AQQ,b)
    if g is None:
        # zero-row component handling: drop rows/cols with all-zero K among Q and T=N
        # detect q with full K-row zero
        keep=[i for i in range(m) if any(K[Q[i]][w]!=0 for w in range(n))]
        Qk=[Q[i] for i in keep]; mk=len(Qk)
        AQQk=[[ (N if Qk[i]==Qk[j] else F(0)) - K[Qk[i]][Qk[j]] for j in range(mk)] for i in range(mk)]
        bk=[N-T[Qk[i]] for i in range(mk)]
        gk=solve(AQQk,bk)
        if gk is None: return dict(O=len(O), status="SINGULAR-even-after-drop", g_oob=-1, o_fail=[], singular=True)
        gmap={Qk[i]:gk[i] for i in range(mk)}
        g=[gmap.get(Q[i],F(0)) for i in range(m)]
        sing=True
    else:
        sing=False
    gmap={Q[i]:g[i] for i in range(m)}
    g_oob=sum(1 for i in range(m) if g[i]<0 or g[i]>1)
    o_fail=[]
    for o in O:
        s=N-T[o]+sum(K[o][q]*gmap[q] for q in Q)
        if s<0: o_fail.append((o,float(s)))
    return dict(O=len(O), status="ok", g_oob=g_oob, o_fail=o_fail, singular=sing,
                gmin=float(min(g)) if g else 0.0, gmax=float(max(g)) if g else 0.0)

def run(nm,n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return
    gm=min(g for _,g in cand)
    for s,g in cand:
        if g!=gm: continue
        d=test(adj,s,n)
        if d is None: continue
        bad = (d['g_oob']!=0) or bool(d['o_fail']) or d['status'].startswith("SING")
        tag="FAIL" if bad else "ok"
        extra="" if d['O']==0 else " gmin=%.3f gmax=%.3f sing=%s"%(d.get('gmin',0),d.get('gmax',0),d['singular'])
        print("  %s N=%d: |O|=%d status=%s g_oob=%d O-fail=%d%s [%s]"%(nm,n,d['O'],d['status'],d['g_oob'],len(d['o_fail']),extra,tag),flush=True)
        if d['o_fail']: print("      O-fails:",d['o_fail'][:5])
        return

if __name__=="__main__":
    from _bdef_construct import Cn, mycielski
    print("=== FULL inverse g Open Capacity Lemma exact test ===")
    cur=(5,Cn(5)); run("C5",*cur)
    cur=(5,Cn(5)); cur=mycielski(*cur); run("Grotzsch=N11",cur[0],cur[1])
    cur2=mycielski(*cur); run("Myc2(C5)=N23",cur2[0],cur2[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    g6list=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]
    for g6 in g6list:
        n,E=dec(g6); run(g6,n,E)
    print("=== census sweep N=5..9 ===")
    import subprocess
    for N in range(5,10):
        cnt=0; fails=0; firstfail=None
        out=subprocess.run([GENG,"-c","-t",str(N)],capture_output=True,text=True,timeout=120).stdout
        for line in out.split():
            if not line: continue
            try: n,E=dec(line)
            except: continue
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
            cc=[]
            for s in cuts:
                Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
                if not Mb: continue
                G=0; ok=True
                for (u,v) in Mb:
                    dd=bdist_restr(adj,s,u,v)
                    if dd<0: ok=False; break
                    G+=(dd+1)**2
                if ok: cc.append((s,G))
            if not cc: continue
            gm=min(g for _,g in cc)
            for s,g in cc:
                if g!=gm: continue
                d=test(adj,s,n)
                if d is None: continue
                cnt+=1
                if (d['g_oob']!=0) or d['o_fail'] or d['status'].startswith("SING"):
                    fails+=1
                    if firstfail is None: firstfail=(line,d)
        print("  N=%d: tested %d cuts, FULL-g FAILS=%d"%(N,cnt,fails),flush=True)
        if firstfail: print("     first fail:",firstfail[0],firstfail[1]['status'],firstfail[1]['g_oob'],firstfail[1]['o_fail'][:3])
