"""Exact-test GPT-Pro's Schur-capacity form (CAP) of (GCD), and confirm (CAP) <=> H=L_omega+diag(N-T)>=0.
   H split by O={T>N}, Q={T<=N}.  H_QQ = L_{omega,QQ}+R_Q (R_Q=N-T>=0 on Q),  H_OO = L_{omega,OO}-D_O.
   (CAP):  L_{omega,OO} - L_{omega,OQ}(L_{omega,QQ}+R_Q)^+ L_{omega,QO} >= D_O
       <=> Schur(H / H_QQ) = H_OO - H_OQ H_QQ^{-1} H_QO >= 0   (when H_QQ is PD).
   Reports: (i) H_QQ PD?  [= cond(1)-flavored well-posedness / Green operator defined]
            (ii) Schur complement on O PSD?  [= cond(3) / capacity dominates overload]
            (iii) agreement with direct H>=0."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _gcd import build_H, is_psd_exact, run_gmin
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski

def cap_test(adj, side, n):
    r=build_H(adj,side,n)
    if r is None: return None
    H,T,N=r
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    sat=[v for v in Q if T[v]==N]
    Hdirect = is_psd_exact(H,n)
    if not O:
        # no overload: H>=0 trivially (diag(N-T)>=0 + Laplacian); CAP vacuous
        return dict(O=0,Q=len(Q),sat=len(sat),HQQ_PD=None,schur_PSD=None,Hdirect=Hdirect,cap_ok=True)
    # Eliminate Q indices from H (Gaussian / Schur). Pivot on H_QQ diagonal in Q order.
    M=[[H[i][j] for j in range(n)] for i in range(n)]
    HQQ_PD=True; HQQ_sing=False
    for q in Q:
        d=M[q][q]
        if d<0: HQQ_PD=False; break
        if d==0:
            # singular H_QQ (saturated isolated). Check row zero on remaining (range condition).
            HQQ_sing=True; HQQ_PD=False
            nz=any(M[q][j]!=0 for j in range(n) if j!=q)
            if nz:
                # genuine singular with nonzero coupling -> CAP via pseudoinverse needed; flag
                pass
            continue
        for i in range(n):
            if i==q or M[i][q]==0: continue
            fac=M[i][q]/d
            for j in range(n): M[i][j]-=fac*M[q][j]
    # O-block of M after eliminating Q = Schur complement (if HQQ_PD)
    schur=[[M[a][b] for b in O] for a in O]
    schur_PSD = is_psd_exact(schur,len(O)) if HQQ_PD else None
    cap_ok = (schur_PSD if HQQ_PD else Hdirect)  # when HQQ not PD, fall back to direct H>=0
    return dict(O=len(O),Q=len(Q),sat=len(sat),HQQ_PD=HQQ_PD,HQQ_sing=HQQ_sing,
                schur_PSD=schur_PSD,Hdirect=Hdirect,cap_ok=cap_ok)

def run_named(nm,n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    res=run_gmin(n,E)  # (uses gamma-min cut selection) -> but we need adj/side; replicate via struct
    # pick gamma-min cuts directly:
    from _h import maxcut_all, Bconn, bdist_restr
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
    if not cand: print(f"  {nm} N={n}: no bad edges"); return
    gm=min(g for _,g in cand)
    for s,g in cand:
        if g!=gm:
            continue
        d=cap_test(adj,s,n)
        if d is None: continue
        tag = "CAP-OK" if d['cap_ok'] else "CAP-FAIL"
        print(f"  {nm} N={n}: |O|={d['O']} |Q|={d['Q']} sat={d['sat']} HQQ_PD={d['HQQ_PD']} "
              f"schurPSD={d['schur_PSD']} H>=0={d['Hdirect']} -> {tag}",flush=True)
        break  # one gamma-min cut suffices to illustrate

if __name__=="__main__":
    print("=== (CAP) Schur-capacity exact test: H_QQ PD? + Schur complement >= D_O? ===",flush=True)
    cur=(5,Cn(5)); run_named("C5",*cur)
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run_named(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run_named("Myc(C7)=N15",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run_named(g6,n,E)
    # census N=7..9: aggregate HQQ_PD and Schur agreement vs direct H>=0
    for nn in range(7,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        from _h import maxcut_all, Bconn, bdist_restr
        tot=0; hqq_notpd=0; cap_fail=0; disagree=0; sat_cases=0
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
            cand=[]
            for s in cuts:
                Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
                if not Mb: continue
                G=0; ok=True
                for (u,v) in Mb:
                    dd=bdist_restr(adj,s,u,v)
                    if dd<0: ok=False; break
                    G+=(dd+1)**2
                if ok: cand.append((s,G))
            if not cand: continue
            gm=min(g for _,g in cand)
            for s,g in cand:
                if g!=gm: continue
                d=cap_test(adj,s,n)
                if d is None or d['O']==0: continue
                tot+=1
                if d['sat']>0: sat_cases+=1
                if d['HQQ_PD'] is False: hqq_notpd+=1
                if not d['cap_ok']: cap_fail+=1
                if d['HQQ_PD'] and (d['schur_PSD']!=d['Hdirect']): disagree+=1
        print(f"  census N={nn}: overloaded-cuts={tot} HQQ_not_PD={hqq_notpd} sat_cases={sat_cases} "
              f"CAP-FAILS={cap_fail} Schur-vs-Hdirect-disagree={disagree}",flush=True)
