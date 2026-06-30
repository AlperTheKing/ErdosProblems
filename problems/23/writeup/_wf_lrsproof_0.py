"""B2 proof-validation harness (Claude, Step-2).
Target: Tmax = max_v T(v) <= 2N  (=> B1 => LRS-RHS slack chain).

T(v)=sum_f w_f * (#f-geos thru v), w_f=ell_f/|cyc_f|.
mu(e) for cut-edge e = sum_f w_f*(#f-geos using edge e).
D(v)=sum_{f: v endpoint of f} ell_f.

We EXACT-validate, over the standing gate (census gamma-min N<=11, two-lane, iterated
Mycielskians N<=23, blow-ups), every intermediate claim before trusting it:
  (H) handshake:  sum_{e at v, e in B} mu(e) == 2T(v) - D(v)   [exact identity]
  Probe Tmax/N actual ratios.
  Sub-lemma candidates toward Tmax<=2N and hunt counterexamples.

All Fraction-exact. struct_for_side gives M,ell,T,mu,cyc on a fixed cut.
"""
import subprocess, itertools
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos, loads, blow
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, blow_g, is_triangle_free

# ---------- gamma-min cut enumeration (all minimizers, connected-B, max cut) ----------
def gmin_cuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    cand=[]
    for s in cuts:
        if not Bconn(n,adj,s): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

# ---------- per-cut quantities ----------
def cut_data(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    N=n
    # D(v)=sum_{f endpoint v} ell_f
    D=[F(0)]*n
    for f in M:
        D[f[0]]+=F(ell[f]); D[f[1]]+=F(ell[f])
    # mu already keyed by cut-edges (only edges actually on geodesics nonzero)
    # incident-mu sum at v over cut-edges:
    inc=[F(0)]*n
    for (a,b),val in mu.items():
        inc[a]+=val; inc[b]+=val
    Gamma=sum(F(ell[f])**2 for f in M)
    beta=len(M)
    return dict(N=N,M=M,ell=ell,T=T,mu=mu,cyc=cyc,D=D,inc=inc,Gamma=Gamma,beta=beta,adj=adj,side=side)

# ---------- (H) handshake check: inc[v] == 2T[v]-D[v] ----------
def check_handshake(cd):
    N=cd['N']; bad=[]
    for v in range(N):
        lhs=cd['inc'][v]; rhs=2*cd['T'][v]-cd['D'][v]
        if lhs!=rhs: bad.append((v,lhs,rhs))
    return bad

# ---------- degree bounds on a max cut ----------
def cut_degrees(cd):
    """For a MAX cut, every vertex has cut-degree >= non-cut-degree (else flipping increases cut).
       deg_cut(v) = # B-edges at v ; deg_M_local(v)= # same-side (mono) edges at v (NOT just bad-edge M)."""
    N=cd['N']; adj=cd['adj']; side=cd['side']
    dc=[0]*N; dm=[0]*N
    for v in range(N):
        for w in adj[v]:
            if side[v]!=side[w]: dc[v]+=1
            else: dm[v]+=1
    return dc,dm

def run_gate():
    rows=[]
    worst={'ratio':F(0),'where':None,'detail':None}
    hs_fail=[]
    # collect Tmax/N over gate
    def consume(name,n,E):
        nonlocal worst
        if not is_triangle_free(n,E): return
        adj,cuts=gmin_cuts(n,E)
        for s in cuts:
            cd=cut_data(n,adj,s)
            if cd is None: continue
            hb=check_handshake(cd)
            if hb: hs_fail.append((name,s,hb[:3]))
            Tmax=max(cd['T']); N=cd['N']
            r=F(Tmax,N) if N else F(0)
            if r>worst['ratio']:
                worst['ratio']=r
                vmax=max(range(N),key=lambda v:cd['T'][v])
                worst['where']=name
                worst['detail']=dict(N=N,Tmax=Tmax,Tmax_f=float(Tmax),ratio=float(r),
                                     beta=cd['beta'],vmax=vmax,
                                     D_vmax=cd['D'][vmax],inc_vmax=cd['inc'][vmax])
    # census
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); consume("census"+g6,n,E)
        print(f"  census N={nn} done; running worst Tmax/N={float(worst['ratio']):.4f} @ {worst['where']}",flush=True)
    # two-lane
    from _verify_two_lane import build_two_lane
    for L in (8,12):
        n,E,side,bad=build_two_lane(L)
        consume(f"two-lane L={L}",n,E)
    print(f"  two-lane done; worst Tmax/N={float(worst['ratio']):.4f}",flush=True)
    # blow-ups C5[t]
    for t in range(1,7):
        n,E=blow(t); consume(f"C5[{t}]",n,E)
    # general odd-cycle blow-ups + non-uniform
    for m in (5,7,9):
        consume(f"C{m}",*( (m,Cn(m)) ))
    # iterated Mycielskians up to N<=23
    cur=(5,Cn(5))
    for nm in ["Grotzsch11","Myc2(C5)23"]:
        cur=mycielski(*cur)
        if cur[0]<=23: consume(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); consume("Myc(C7)15",cur[0],cur[1])
    cur=(9,Cn(9)); cur=mycielski(*cur)
    if cur[0]<=23: consume("Myc(C9)19",cur[0],cur[1])
    # glued island+gadget battery (the bad-edge-coexists-with-O witnesses)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>23 or not is_triangle_free(n,E): continue
                consume(f"isl{iN}+gad{gN}",n,E)
    print(f"  Mycielskian+glued done; worst Tmax/N={float(worst['ratio']):.4f}",flush=True)
    return worst,hs_fail

if __name__=="__main__":
    print("=== B2 harness: handshake identity + Tmax/N probe over standing gate ===",flush=True)
    worst,hs_fail=run_gate()
    print("\n--- RESULTS ---")
    print(f"handshake failures: {len(hs_fail)}"+ (f"  e.g. {hs_fail[0]}" if hs_fail else " (identity HOLDS exactly everywhere)"))
    print(f"WORST Tmax/N over gate = {float(worst['ratio']):.6f}  at {worst['where']}")
    print(f"  detail={worst['detail']}")
    print(f"  B2 (Tmax<=2N) margin: worst ratio {float(worst['ratio']):.4f} vs 2.0")
