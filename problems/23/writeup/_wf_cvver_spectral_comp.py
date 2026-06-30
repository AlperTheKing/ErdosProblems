"""ADVERSARIAL independent verifier of route 'spectral_comp' for (CV).

CLAIM under test (GERSH): for every bad edge f in K-component c,
    R_f := sum_{g in c} <p_f,p_g> / (|cyc_f| |cyc_g|)  <=  N + eta,
where eta = N^2/25 - beta. R_f is the Gershgorin row-sum of the symmetric entrywise-nonneg
matrix Dm = D^{-1/2} O_c D^{-1/2}, D=diag(|cyc_f|^2). Prior agent claims GERSH holds on the
FULL battery (0 viol) and proven-implies (CV).

This file re-implements EVERYTHING from scratch (own struct, own p_f, own O_c, own R_f and own
(CV) check) -- it does NOT import _cv_gate. It:
  (1) recomputes (CV) directly (sum_{v in c} T_v^2 <= (N+eta) Gamma_c) as the ground truth,
  (2) recomputes R_f = Gershgorin row-sum of Dm and checks R_f <= N+eta (GERSH),
  (3) recomputes the true normalized spectral radius rho(Dm) via the (exact-rational) ground
      truth bound rho(Dm) <= max_f R_f and ALSO an independent lower witness rho(Dm) >= u^T Dm u/||u||^2
      with u=ell (which equals w^T O_c w / Gamma_c, the (CV) Rayleigh quotient),
  (4) cross-checks the algebra rho(Dm)<=N+eta  ==>  (CV) on every component (i.e. whenever GERSH
      holds, (CV) must hold; flag any component where GERSH passes but (CV) fails -- that would
      break the IMPLICATION, not just the inequality).
ALL exact Fraction. Reports binding component, extremal constant, viol counts. Hunts counterexamples
especially on Myc(Grotzsch) N=23, glued bridges, dense k-lanes, asymmetric blow-ups, extra graphs.

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import subprocess, itertools
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG

# ============================================================================
# FROM-SCRATCH primitives (do not reuse struct_for_side / Ogram / kcomponents)
# ============================================================================

def adj_of(n, E):
    a=[set() for _ in range(n)]
    for x,y in E:
        if x!=y: a[x].add(y); a[y].add(x)
    return a

def is_trifree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def all_max_cuts(n, adj):
    """All max cuts as 0/1 side vectors (brute over 2^(n-1), fixing vertex0=0)."""
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1; cuts=[]
    for m in range(1<<(n-1)):
        side=[0]*n
        for u in range(1,n): side[u]=(m>>(u-1))&1
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best: best=c; cuts=[side[:]]
        elif c==best: cuts.append(side[:])
    return best, cuts

def Bconn(n, adj, side):
    seen={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v); q.append(v)
    return len(seen)==n

def shortest_alt_geos(adj, side, s, t):
    """All shortest CUT-edge (alternating) paths from s to t. Returns list of vertex-lists."""
    dist={s:0}; pred={s:[]}; layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist: dist[v]=dist[u]+1; pred[v]=[u]; nxt.append(v)
                    elif dist[v]==dist[u]+1: pred[v].append(u)
        layer=nxt
    if t not in dist: return []
    out=[]
    def rec(v, acc):
        if v==s: out.append([s]+acc[::-1]); return
        for p in pred[v]: rec(p, acc+[v])
    rec(t, [])
    return out

def build_struct(n, adj, side):
    """From scratch: bad edges M, geodesic sets cyc[f], ell[f]=|geo path| (#vertices),
    p_f as dict v->#geos thru v, |cyc_f|=#geos, T(v)=sum_f (ell_f/|cyc_f|) p_f(v).
    Returns None if any bad edge has no alternating geodesic.
    Also returns kcomp find() via union-find over geodesic vertex sets (each path = clique)."""
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    cyc={}; ell={}; ncyc={}; pf={}
    T=[F(0)]*n
    for f in M:
        Ps=shortest_alt_geos(adj, side, f[0], f[1])
        if not Ps: return None
        cyc[f]=Ps; ncyc[f]=len(Ps); ell[f]=len(Ps[0])
        cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pf[f]=cnt  # v -> integer #geos thru v
        sh=F(ell[f], ncyc[f])
        for v,c in cnt.items(): T[v]+=sh*c
    # union-find over geodesic paths
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: par[ra]=rb
    for f in M:
        for P in cyc[f]:
            for i in range(1,len(P)): union(P[0],P[i])
    return dict(n=n, M=M, cyc=cyc, ell=ell, ncyc=ncyc, pf=pf, T=T, find=find)

# ============================================================================
# CORE CHECKS
# ============================================================================

def Opair(pf_f, pf_g):
    """<p_f,p_g> = sum_v p_f(v) p_g(v)  (exact int -> Fraction)."""
    # iterate smaller dict
    if len(pf_f) > len(pf_g): pf_f, pf_g = pf_g, pf_f
    s=0
    for v,a in pf_f.items():
        b=pf_g.get(v,0)
        if b: s+=a*b
    return F(s)

def check_graph(name, n, adj, side, acc):
    if not Bconn(n, adj, side): return
    st=build_struct(n, adj, side)
    if st is None: return
    M=st['M']; cyc=st['cyc']; ell=st['ell']; ncyc=st['ncyc']; pf=st['pf']; T=st['T']; find=st['find']
    beta=len(M); N=n; eta=F(N*N,25)-beta; A=F(N)+eta   # A = N + eta

    # group bad edges by K-component
    comp_edges={}
    for f in M:
        r=find(f[0]); comp_edges.setdefault(r,[]).append(f)
    # group vertices by K-component (for direct (CV))
    comp_verts={}
    for v in range(n): comp_verts.setdefault(find(v),[]).append(v)

    for r, fs in comp_edges.items():
        vs=comp_verts.get(r,[])
        # ---- (CV) ground truth: sum_{v in c} T_v^2 <= A * Gamma_c ----
        S2=sum(T[v]*T[v] for v in vs)
        Gamma_v=sum(T[v] for v in vs)           # = sum_{v in c} T_v
        Gamma_ell=sum(F(ell[f])**2 for f in fs) # = sum_{f in c} ell_f^2
        if Gamma_v==0: continue
        cv_margin=A*Gamma_v - S2
        acc['ncomp']+=1
        if cv_margin < acc['cv_min'][0]:
            acc['cv_min']=(cv_margin, name, N, beta, len(vs), str(Gamma_v))
        cv_ok = (cv_margin >= 0)
        if not cv_ok:
            acc['cv_viol']+=1
            if acc['cv_first'] is None:
                acc['cv_first']=(name, N, beta, len(vs), str(cv_margin))

        # sanity: Gamma_v should equal Gamma_ell (the claimed identity)
        if Gamma_v != Gamma_ell:
            acc['ident_break']+=1
            if acc['ident_first'] is None:
                acc['ident_first']=(name, N, str(Gamma_v), str(Gamma_ell))

        # ---- build O_c restricted to this component's bad edges ----
        mfs=len(fs)
        Oc=[[F(0)]*mfs for _ in range(mfs)]
        for i in range(mfs):
            for j in range(i, mfs):
                val=Opair(pf[fs[i]], pf[fs[j]])
                Oc[i][j]=val; Oc[j][i]=val

        # ---- GERSH: R_f = sum_g O_c[f,g]/(ncyc_f ncyc_g) <= A ----
        max_Rf=F(-1); argmax=None
        for i in range(mfs):
            Rf=F(0)
            for j in range(mfs):
                Rf += Oc[i][j] / (F(ncyc[fs[i]]) * F(ncyc[fs[j]]))
            gersh_margin = A - Rf
            if Rf > max_Rf: max_Rf=Rf; argmax=fs[i]
            acc['nrow']+=1
            if gersh_margin < acc['gersh_min'][0]:
                acc['gersh_min']=(gersh_margin, name, N, beta, str(Rf), str(A))
            if gersh_margin < 0:
                acc['gersh_viol']+=1
                if acc['gersh_first'] is None:
                    acc['gersh_first']=(name, N, beta, str(fs[i]), str(Rf), str(A), str(gersh_margin))

        # ---- IMPLICATION cross-check: if GERSH holds on this comp (max_Rf<=A) then (CV) MUST hold ----
        gersh_comp_ok = (max_Rf <= A)
        if gersh_comp_ok and not cv_ok:
            acc['impl_break']+=1
            if acc['impl_first'] is None:
                acc['impl_first']=(name, N, beta, str(max_Rf), str(A), str(cv_margin))

        # ---- independent lower witness for rho(Dm): Rayleigh at u=ell vector ----
        # w^T O_c w / Gamma_ell  with w_f=ell_f/ncyc_f  equals u^T Dm u/||u||^2, u_f=ell_f.
        # This is the (CV) Rayleigh quotient; must be <= rho(Dm) <= max_Rf. Track for context.
        wOw=F(0)
        for i in range(mfs):
            for j in range(mfs):
                wOw += F(ell[fs[i]],ncyc[fs[i]]) * Oc[i][j] * F(ell[fs[j]],ncyc[fs[j]])
        if Gamma_ell>0:
            rayl = wOw / Gamma_ell   # = w^T O_c w / Gamma  (the actual quantity (CV) bounds by A)
            # this must be <= max_Rf (Gershgorin) always, and (CV) <=> rayl <= A
            if rayl > max_Rf + F(1,10**9):  # rayl should never exceed Gershgorin bound
                acc['rayl_above_gersh']+=1
            if rayl > acc['rayl_max'][0]:
                acc['rayl_max']=(rayl, name, N, str(A))

def run_battery():
    from _bdef_construct import mycielski, Cn, union_disjoint
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane
    from _wf_lrsbreak_0c import greedy_chords

    acc=dict(ncomp=0, nrow=0,
             cv_viol=0, cv_first=None, cv_min=(F(10**18),'','','','',''),
             gersh_viol=0, gersh_first=None, gersh_min=(F(10**18),'','','','',''),
             impl_break=0, impl_first=None,
             ident_break=0, ident_first=None,
             rayl_above_gersh=0, rayl_max=(F(-1),'','',''),
             )

    def blowup(parts):
        mm=len(parts); off=[0]*(mm+1)
        for i in range(mm): off[i+1]=off[i]+parts[i]
        nn=off[mm]; EE=[]
        for i in range(mm):
            j=(i+1)%mm
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,sorted(set(EE))
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

    # --- two-lane + k-lane ---
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); check_graph("two-lane-L%d"%L, n, adj_of(n,E), side, acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad)
        check_graph("klane-L%dk%d"%(Ll,k), n, adj_of(n,E), side, acc)
    print("  two-lane+k-lane done: GERSH viol=%d  (CV) viol=%d  impl-break=%d"%(acc['gersh_viol'],acc['cv_viol'],acc['impl_break']),flush=True)

    # --- C5/C7/C9 blow-ups uniform t=1..5 ---
    for cc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): check_graph("C%d[%d]"%(cc,t), n, adj, s, acc)

    # --- asymmetric / non-uniform blow-ups (extra adversarial) ---
    nu_list=[[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],
             [1,4,1,4,1],[5,1,5,1,5],[1,1,5,5,5],[2,5,1,5,2],
             [1,2,1,2,1,2,1],[3,1,3,1,3,1,3],[1,4,2,3,1,4,2]]
    for parts in nu_list:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): check_graph("nu%s"%parts, n, adj, s, acc)
    print("  blow-ups (uniform+asymmetric) done: GERSH viol=%d  (CV) viol=%d  impl-break=%d"%(acc['gersh_viol'],acc['cv_viol'],acc['impl_break']),flush=True)

    # --- Mycielskians + glued bridges (the prime adversarial targets) ---
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    named=[("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),
           ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
           ("bridge(C7,Grotzsch)",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
           ("bridge(C9,C9)",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
           ("bridge(C5,C7)",bridge((5,Cn(5)),(7,Cn(7)),0,0)),
           ("bridge(C5,Grotzsch)",bridge((5,Cn(5)),mycielski(5,Cn(5)),0,0)),
           ("bridge(C7,C7)",bridge((7,Cn(7)),(7,Cn(7)),0,0)),
           ("bridge(C5,C5)",bridge((5,Cn(5)),(5,Cn(5)),0,0))]
    for nm,(nn,E) in named:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: check_graph(nm, nn, adj, s, acc)
    print("  Mycielskians + glued bridges done: GERSH viol=%d  (CV) viol=%d  impl-break=%d"%(acc['gersh_viol'],acc['cv_viol'],acc['impl_break']),flush=True)

    # --- census geng -tc N=7..11, ALL gamma-min cuts ---
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gv0=acc['gersh_viol']; cv0=acc['cv_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_graph("cen%s"%g6, n, adj, s, acc)
        print("  census N=%d done (GERSH viol +%d, (CV) viol +%d)"%(nn,acc['gersh_viol']-gv0,acc['cv_viol']-cv0),flush=True)

    return acc

if __name__=="__main__":
    print("=== ADVERSARIAL verify: route spectral_comp (GERSH) for (CV) ===",flush=True)
    acc=run_battery()
    print("\n----- RESULTS -----",flush=True)
    print("  components tested = %d   bad-edge rows tested = %d"%(acc['ncomp'],acc['nrow']),flush=True)
    print("  identity Gamma_v==Gamma_ell breaks = %d %s"%(acc['ident_break'], acc['ident_first'] or ''),flush=True)
    print()
    print("  (CV) ground-truth violations = %d"%acc['cv_viol'],flush=True)
    print("    (CV) MIN margin = %s  at %s"%(float(acc['cv_min'][0]), acc['cv_min'][1:]),flush=True)
    if acc['cv_first']: print("    (CV) first viol: %s"%(acc['cv_first'],),flush=True)
    print()
    print("  GERSH (R_f<=N+eta) violations = %d"%acc['gersh_viol'],flush=True)
    print("    GERSH MIN margin = %s  at (name,N,beta,Rf,A)=%s"%(float(acc['gersh_min'][0]), acc['gersh_min'][1:]),flush=True)
    if acc['gersh_first']: print("    GERSH first viol: %s"%(acc['gersh_first'],),flush=True)
    print()
    print("  IMPLICATION breaks (GERSH holds on comp but (CV) fails) = %d  %s"%(acc['impl_break'], acc['impl_first'] or ''),flush=True)
    print("  Rayleigh-above-Gershgorin anomalies = %d   max Rayleigh quotient = %s"%(acc['rayl_above_gersh'], float(acc['rayl_max'][0])),flush=True)
    print()
    g_ok = (acc['gersh_viol']==0); c_ok=(acc['cv_viol']==0); i_ok=(acc['impl_break']==0); id_ok=(acc['ident_break']==0)
    print("  === GERSH %s | (CV) %s | IMPLICATION %s | IDENTITY %s ==="%(
        "HOLDS" if g_ok else "FAILS", "HOLDS" if c_ok else "FAILS",
        "SOUND" if i_ok else "BROKEN", "OK" if id_ok else "BROKEN"),flush=True)
