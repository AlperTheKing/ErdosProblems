"""GUARDRAIL test of GPT-Pro's POT route (2026-06-28): claim H*T >= 0 entrywise (phi=T), H=L_omega+diag(N-T),
   which would give H>=0 by symmetric M-matrix scaling. Reduces to (FAC): M_f T <= N*ell(f)*p_f per bad edge.
   Codex (block 83) reported min(H*T)<0 at MycGrotzsch N=23 -> POT likely REFUTED. Verify INDEPENDENTLY, exact.
   Also check the chordless identity sum_u tau_f(vu) = 2 p_f(v) (needed for M>=0 entrywise)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import a_bar, build_H
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski

def matvec(H, x, n):
    return [sum(H[i][j]*x[j] for j in range(n)) for i in range(n)]

def pot_and_fac(adj, side, n):
    # H*T entrywise
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    HT=matvec(H,T,n)
    minHT=min(HT)
    # struct for FAC + chordless identity
    st=struct_for_side(n,adj,side)
    M,ell,Tt,mu,cyc=st
    # rebuild p_f and tau_f per edge
    fac_fail=0; fac_min=None; chord_bad=0
    for f in M:
        L=ell[f]; ae=a_bar(L); Ps=cyc[f]; k=len(Ps)
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        # tau_f(vu): undirected edge weights on cycle edges
        tau={}  # (min,max)->weight
        ef=(min(f),max(f)); tau[ef]=F(1)  # bad edge f
        for P in Ps:
            for i in range(len(P)-1):
                e2=(min(P[i],P[i+1]),max(P[i],P[i+1])); tau[e2]=tau.get(e2,F(0))+F(1,k)
        # chordless identity: sum_u tau_f(vu) = 2 p_f(v)  for each v in support
        degsum={}
        for (a,b),w in tau.items():
            degsum[a]=degsum.get(a,F(0))+w; degsum[b]=degsum.get(b,F(0))+w
        for v,pv in pf.items():
            if degsum.get(v,F(0)) != 2*pv: chord_bad+=1
        # M_f = ell*diag(p_f) - a_f*L_tau ; (M_f T)(v) <= N*ell*p_f(v)
        # build M_f as dict on support
        supp=set(pf.keys())
        for (a,b) in tau: supp.add(a); supp.add(b)
        for v in supp:
            # (M_f T)(v) = ell*p_f(v)*T(v) - a_f * sum_u tau(vu)*(T(v)-T(u))
            mft = F(L)*pf.get(v,F(0))*T[v]
            for (a,b),w in tau.items():
                if a==v: mft -= ae*w*(T[v]-T[b])
                elif b==v: mft -= ae*w*(T[v]-T[a])
            rhs = F(N)*L*pf.get(v,F(0))
            slack = rhs - mft
            if fac_min is None or slack<fac_min: fac_min=slack
            if slack<0: fac_fail+=1
    return dict(minHT=minHT, fac_fail=fac_fail, fac_min=fac_min, chord_bad=chord_bad, N=N, nbad=len(M))

def gmins(n,E):
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
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def run(nm,n,E):
    adj,cuts=gmins(n,E)
    worstHT=None; faclist=0; chord=0; ncut=0
    for s in cuts:
        d=pot_and_fac(adj,s,n)
        if d is None: continue
        ncut+=1
        if worstHT is None or d['minHT']<worstHT: worstHT=d['minHT']
        faclist+=d['fac_fail']; chord+=d['chord_bad']
    if ncut==0: print(f"  {nm} N={n}: no bad edges"); return
    print(f"  {nm} N={n}: cuts={ncut} min(H*T)={float(worstHT):+.4f} POT-OK={worstHT>=0} FAC-FAILS={faclist} chordID-bad={chord}",flush=True)

if __name__=="__main__":
    print("=== POT guardrail: H*T>=0 entrywise? + FAC: M_f T <= N ell p_f ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run(g6,n,E)
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        worst=None; ff=0; cb=0; tot=0; potfail=0
        for g6 in outg:
            n,E=dec(g6)
            adj,cuts=gmins(n,E)
            for s in cuts:
                d=pot_and_fac(adj,s,n)
                if d is None: continue
                tot+=1
                if worst is None or d['minHT']<worst: worst=d['minHT']
                if d['minHT']<0: potfail+=1
                ff+=d['fac_fail']; cb+=d['chord_bad']
        print(f"  census N={nn}: cuts={tot} min(H*T)={float(worst):+.4f} POT-FAILS(cuts)={potfail} FAC-FAILS={ff} chordID-bad={cb}",flush=True)
