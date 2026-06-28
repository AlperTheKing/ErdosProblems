"""Adversarial exact test of the two-step Neumann supersolution candidate from SCHUR_SPEC_PROOF_DRAFT.md.
phi(o)=1 on O; phi(q)=1 - u(q)/N - (K_QQ u)(q)/N^2 on Q, u=max(N-T,0).
The SOLE nontrivial inequality (claimed):
    N - T(o) + (K_OQ u)(o)/N + (K_OQ K_QQ u)(o)/N^2 >= 0  for every o in O.
Test exactly (Fraction). Also test the FULL claim K phi <= N phi everywhere, and phi>=0.
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

def matvec(K,x,n):
    return [sum(K[i][j]*x[j] for j in range(n)) for i in range(n)]

def test(adj,side,n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=F(n)
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    u=[max(N-T[v],F(0)) for v in range(n)]
    Qset=set(Q)
    uQ=[u[v] if v in Qset else F(0) for v in range(n)]
    KQQu=[sum(K[i][j]*uQ[j] for j in Q) for i in range(n)]
    phi=[F(0)]*n
    for o in O: phi[o]=F(1)
    for q in Q:
        phi[q]=F(1) - u[q]/N - KQQu[q]/(N*N)
    phi_neg=[v for v in range(n) if phi[v]<0]
    Kphi=matvec(K,phi,n)
    viol=[v for v in range(n) if Kphi[v] > N*phi[v]]
    o_fail=[]
    for o in O:
        KOQu=sum(K[o][j]*uQ[j] for j in Q)
        KOQKQQu=sum(K[o][j]*KQQu[j] for j in Q)
        lhs = N - T[o] + KOQu/N + KOQKQQu/(N*N)
        if lhs < 0: o_fail.append((o,float(lhs)))
    return dict(O=len(O), phi_neg=phi_neg, full_viol=viol, o_fail=o_fail,
                phimin=float(min(phi)) if phi else 0.0)

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
        bad = bool(d['phi_neg']) or bool(d['full_viol']) or bool(d['o_fail'])
        tag = "FAIL" if bad else "ok"
        print(f"  {nm} N={n}: |O|={d['O']} phimin={d['phimin']:+.4f} "
              f"phi<0:{len(d['phi_neg'])} Kphi>Nphi:{len(d['full_viol'])} O-ineq-fail:{len(d['o_fail'])} [{tag}]",flush=True)
        if d['o_fail']: print(f"      O-fails: {d['o_fail'][:5]}")
        if d['full_viol']: print(f"      full-viol verts: {d['full_viol'][:8]}")
        return

if __name__=="__main__":
    from _bdef_construct import Cn, mycielski
    print("=== two-step Neumann supersolution exact test ===")
    cur=(5,Cn(5)); run("C5",*cur)
    for t in (2,3,4):
        nn=5*t; EE=[(i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)]
        run("C5["+str(t)+"]",nn,EE)
    cur=(5,Cn(5)); cur=mycielski(*cur); run("Grotzsch=N11",cur[0],cur[1])
    cur2=mycielski(*cur); run("Myc2(C5)=N23",cur2[0],cur2[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    g6list=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]
    for g6 in g6list:
        n,E=dec(g6); run(g6,n,E)
    print("=== census sweep N=5..9 (connected-B gamma-min cuts) ===")
    import subprocess
    for N in range(5,10):
        cnt=0; fails=0
        try:
            out=subprocess.run([GENG,"-c","-t",str(N)],capture_output=True,text=True,timeout=120).stdout
        except Exception as e:
            print("  N="+str(N)+": geng err "+str(e)); continue
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
                if d['phi_neg'] or d['full_viol'] or d['o_fail']: fails+=1
        print("  N="+str(N)+": tested "+str(cnt)+" gamma-min cuts, two-step FAILS="+str(fails),flush=True)
