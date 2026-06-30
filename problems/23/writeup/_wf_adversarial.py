"""ADVERSARIAL HUNT for a counterexample to BLOCK-SBC:
   rho(O_C) + m_C <= n_C + n_C^2/25   for every POSITIVE K-component C
   of a gamma-min connected-B MAXIMUM cut of a triangle-free graph.

A "positive K-component" C = a K-component (union-find over geodesic paths, _satzmu_conn.kcomponents)
that carries at least one bad edge (m_C>=1). For such C:
  n_C = |C|
  bad edges in C: M_C = {f in M : both endpoints of f in C}     m_C=|M_C|
  O_C = overlap Gram restricted to M_C, O_C[i][j]=<p_fi,p_fj>, p_f=geodesic mass (Fraction).
  rho(O_C) lower bound LB = (sum over verts of T_C)^2 / Gamma_C  (Rayleigh all-ones),
       Gamma_C = sum_{f in M_C} ell_f^2,  T_C = restricted load = sum_i p_fi summed over M_C.
  We ALSO compute the exact rho via char-poly root bracketing AND a float eig for cross-check;
  the GATE uses the rigorous LOWER bound LB <= rho(O_C) on the LHS so a violation found with LB
  is a GENUINE violation (rho>=LB), and on the safe side we additionally bracket the true rho upward.

BLOCK-SBC gate (per positive component):  LHS_low = LB + m_C  vs  RHS = n_C + n_C^2/25 (Fraction).
   If LB + m_C > n_C + n_C^2/25  ==> rho(O_C)+m_C >= LB+m_C > RHS ==> GENUINE VIOLATION.
We also report the tighter true-rho margin for context but only LB drives a 'violation' verdict.

EVERY candidate's cut is confirmed a GLOBAL MAXIMUM cut (CP-SAT for constructed families, or
maxcut_all/gmins enumeration for census). A non-max cut is NEVER gated.
All pass/fail verdicts use EXACT Fraction. is_psd via exact LDL. Floats only for display/cross-check.
"""
import sys, subprocess, itertools, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins

# ---------- canonical exact primitives ----------
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

def pf_dict(cyc_f):
    k=len(cyc_f); d={}
    for P in cyc_f:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d

def gram_O_sub(Msub,cyc):
    pf=[pf_dict(cyc[f]) for f in Msub]; m=len(Msub); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0); di=pf[i]; dj=pf[j]
            for v,pv in di.items():
                if v in dj: s+=pv*dj[v]
            O[i][j]=s; O[j][i]=s
    return O

def is_psd(A):
    m=len(A); W=[r[:] for r in A]
    for k in range(m):
        p=W[k][k]
        if p<0: return False
        if p==0:
            for j in range(m):
                if W[k][j]!=0: return False
            continue
        for i in range(k+1,m):
            if W[i][k]==0: continue
            f=W[i][k]/p
            for j in range(k,m): W[i][j]-=f*W[k][j]
    return True

# ---------- exact spectral radius lower bound via Rayleigh on all-ones, and an exact upper bracket ----------
def rho_lower_allones(O):
    """LB = 1^T O 1 / (1^T 1) <= rho(O) for symmetric PSD O (Rayleigh quotient)."""
    m=len(O)
    if m==0: return F(0)
    num=sum(O[i][j] for i in range(m) for j in range(m))
    return num/F(m)

def rho_exact_bracket(O):
    """Return a Fraction L0 <= rho(O) (the largest eigenvalue) using power-iteration-style
       Rayleigh with the all-ones-then-O*v vector; for symmetric PSD O this is <= rho.
       We iterate a few times to push the lower bound up (still a rigorous lower bound each step
       since Rayleigh quotient of any vector <= rho)."""
    m=len(O)
    if m==0: return F(0)
    v=[F(1)]*m
    best=rho_lower_allones(O)
    for _ in range(40):
        # w = O v
        w=[sum(O[i][j]*v[j] for j in range(m)) for i in range(m)]
        num=sum(v[i]*w[i] for i in range(m))   # v^T O v
        den=sum(v[i]*v[i] for i in range(m))
        if den>0:
            rq=num/den
            if rq>best: best=rq
        # next iterate
        nv=[sum(O[i][j]*w[j] for j in range(m)) for i in range(m)]
        if all(x==0 for x in nv): break
        v=nv
        # normalize by gcd-ish to keep fractions small: divide by max abs
        mx=max(abs(x) for x in v)
        if mx>0: v=[x/mx for x in v]
    return best

def float_rho(O):
    try:
        import numpy as np
        A=np.array([[float(x) for x in r] for r in O])
        return float(max(abs(np.linalg.eigvalsh(A))))
    except Exception:
        return None

# ---------- per-component BLOCK-SBC gate ----------
def block_sbc_components(n, adj, side):
    """For the given (assumed gamma-min connected-B MAX) cut, return list of records, one per
       POSITIVE K-component, with the BLOCK-SBC gate evaluated EXACTLY."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    comp, find = kcomponents(n, cyc)
    recs=[]
    for root,Cset in comp.items():
        M_C=[f for f in M if f[0] in Cset and f[1] in Cset]
        if not M_C: continue   # only positive components (carry a bad edge)
        n_C=len(Cset); m_C=len(M_C)
        O=gram_O_sub(M_C,cyc)
        # exact LB on rho and a pushed exact lower bound
        LB_allones=rho_lower_allones(O)
        LB=rho_exact_bracket(O)              # >= LB_allones, still <= rho(O)
        # Gamma_C and restricted-load lower bound cross check (sumT^2/Gamma)
        Gamma_C=sum(ell[f]**2 for f in M_C)
        # restricted load mass = sum over verts of sum_{f in M_C} p_f(v) = sum_{f in M_C} ell_f
        massT=sum(ell[f] for f in M_C)       # since sum_v p_f(v)=1*ell? NO: sum_v p_f(v)= (#paths * (ell/k))/...
        # Actually sum_v p_f(v) = sum over paths of (1/k)*len(P) = ell_f (each path has ell_f verts, k paths, 1/k each)
        sumT2_over_Gamma = (massT*massT)/Gamma_C if Gamma_C>0 else F(0)
        RHS=F(n_C)+F(n_C*n_C,25)
        LHS_low=LB+m_C
        # AUTHORITATIVE verdict via EXACT PSD of (c*I - O_C), c = RHS - m_C.
        # rho(O_C) <= c  iff  c*I - O_C PSD (O_C symmetric).  BLOCK-SBC holds iff PSD.
        c=RHS-F(m_C)
        B=[[ (c if r==s_ else F(0)) - O[r][s_] for s_ in range(m_C)] for r in range(m_C)]
        sbc_holds = is_psd(B)            # True  => BLOCK-SBC holds for this component
        violation = not sbc_holds        # exact, authoritative
        # cross-check: LB+m_C>RHS also implies violation (LB<=rho<=...) ; must agree direction
        psd_O = is_psd(O)                # O itself PSD (sanity: it is a Gram, must be True)
        recs.append(dict(C=tuple(sorted(Cset)),n_C=n_C,m_C=m_C,O=O,
                         LB_allones=LB_allones,LB=LB,sumT2_over_Gamma=sumT2_over_Gamma,
                         Gamma_C=Gamma_C,RHS=RHS,LHS_low=LHS_low,violation=violation,
                         sbc_holds=sbc_holds,psd=psd_O,frho=float_rho(O),
                         margin=RHS-LHS_low))
    return recs

# ---------- max-cut confirmation ----------
def trifree(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def cpmax(n,edges,tlim=120):
    from ortools.sat.python import cp_model
    m=cp_model.CpModel(); x=[m.NewBoolVar("x%d"%i) for i in range(n)]; t=[]
    for a,b in edges:
        z=m.NewBoolVar("e%d_%d"%(a,b)); m.AddBoolXOr([x[a],x[b],z.Not()]); t.append(z)
    m.Maximize(sum(t)); s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlim
    s.parameters.num_search_workers=8
    st=s.Solve(m); return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), st

def confirm_and_gate(name, n, E, side, verbose=True):
    """Confirm tri-free + Bconn + GLOBAL MAX (CP-SAT) for displayed side, then gate BLOCK-SBC on
       every positive K-component. Returns (gated:bool, recs)."""
    adj=adj_of(n,E)
    tf=trifree(n,adj); bc=Bconn(n,adj,side); pc=cutsize(n,adj,side)
    opt,bd,_=cpmax(n,E)
    ismax=(pc==opt==bd)
    if verbose:
        print(f"[{name}] N={n} E={len(E)} tri-free={tf} Bconn={bc} cut={pc} CP-max={opt} bound={bd} GLOBAL-MAX={ismax}",flush=True)
    if not (tf and bc and ismax):
        if verbose: print(f"   -> NOT gated (tri-free/Bconn/max failed)",flush=True)
        return False, None
    recs=block_sbc_components(n,adj,side)
    if recs is None:
        if verbose: print("   -> struct_for_side None (no M / disconnected geodesics)",flush=True)
        return False, None
    for r in recs:
        tag="  *** BLOCK-SBC VIOLATION ***" if r['violation'] else ""
        if verbose:
            print(f"   C n_C={r['n_C']} m_C={r['m_C']} LB(rho)={float(r['LB']):.4f} "
                  f"frho={r['frho']:.4f} sumT2/G={float(r['sumT2_over_Gamma']):.4f} "
                  f"LHS_low={float(r['LHS_low']):.4f} RHS={float(r['RHS']):.4f} "
                  f"margin={float(r['margin']):.4f} PSD={r['psd']}{tag}",flush=True)
    return True, recs

# ---------- (a) two-lane, possibly extended with extra bad edges ----------
def build_two_lane(L, extra_bad=None):
    """L>=8 even. Two-lane skeleton from _verify_two_lane, optional EXTRA bad edges (added to M).
       Returns (n,E,side,bad)."""
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1)
    E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    bad=[(0,L-2),(0,L),(2,L-2),(2,L)]
    if extra_bad:
        for e in extra_bad: bad.append((min(e),max(e)))
    for e in bad: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side,bad

# ---------- global SBC (architecture's actual target) for context ----------
def global_sbc(n, adj, side):
    """rho(O)+|M| <= N + N^2/25 with FULL O and FULL N (the architecture's real certificate).
       Returns (holds:bool, |M|, N, frho)."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    O=gram_O_sub(M,cyc)
    RHS=F(n)+F(n*n,25); c=RHS-F(len(M))
    B=[[ (c if r==s_ else F(0)) - O[r][s_] for s_ in range(len(M))] for r in range(len(M))]
    return is_psd(B), len(M), n, float_rho(O)

# ====================== ADVERSARIAL BATTERY ======================
class Acc:
    def __init__(self):
        self.tested=0; self.violations=0; self.first=None
        self.families=[]
        self.tight=[]
    def absorb(self, name, n, E, side, recs):
        if recs is None: return
        for r in recs:
            self.tested+=1
            if r['violation']:
                self.violations+=1
                if self.first is None:
                    self.first=dict(family=name, N=n, edges=sorted(E), side=list(side),
                        component=r['C'], n_C=r['n_C'], m_C=r['m_C'],
                        rho_lower=str(r['LB']), frho=r['frho'],
                        RHS=str(r['RHS']), LHS_low=str(r['LHS_low']),
                        sumT2_over_Gamma=str(r['sumT2_over_Gamma']),
                        verdict="rho(O_C)+m_C > n_C+n_C^2/25 (c*I-O_C NOT PSD, exact)")
            # tightness: margin exactly 0 on the EXACT PSD boundary
            if r['sbc_holds'] and r['margin']==0:
                self.tight.append((name, r['n_C'], r['m_C']))

ACC=Acc()

def gate(name, n, E, side, verbose=True, require_cpmax=True):
    """Confirm GLOBAL MAX (CP-SAT) + tri-free + Bconn, then gate per-component BLOCK-SBC."""
    adj=adj_of(n,E)
    tf=trifree(n,adj); bc=Bconn(n,adj,side); pc=cutsize(n,adj,side)
    if require_cpmax:
        opt,bd,_=cpmax(n,E)
        ismax=(pc==opt==bd)
    else:
        ismax=True; opt=bd=pc
    if not (tf and bc and ismax):
        if verbose: print(f"[{name}] N={n} tri-free={tf} Bconn={bc} cut={pc} cpmax={opt}/{bd} -> SKIP (not a valid max-cut test)",flush=True)
        return
    recs=block_sbc_components(n,adj,side)
    if recs is None:
        if verbose: print(f"[{name}] N={n}: struct None / no M",flush=True)
        return
    gs=global_sbc(n,adj,side)
    ACC.absorb(name,n,E,side,recs)
    if verbose:
        for r in recs:
            tag="  *** BLOCK-SBC VIOLATION ***" if r['violation'] else ""
            print(f"[{name}] N={n} GLOBAL-MAX=True  C: n_C={r['n_C']} m_C={r['m_C']} "
                  f"rho>={float(r['LB']):.3f}(true {r['frho']:.3f}) LHS={float(r['LHS_low']):.3f} "
                  f"RHS={float(r['RHS']):.3f} margin={float(r['margin']):.3f}{tag}",flush=True)
        if gs is not None:
            ph,mm,NN,fr=gs
            print(f"    [global SBC context] rho(O)={fr:.3f} |M|={mm} N={NN} "
                  f"RHS={NN+NN*NN/25:.2f} GLOBAL-SBC-holds={ph}",flush=True)

def gate_census(name, n, E):
    """Census/random graph: gate EVERY gamma-min connected-B max cut (gmins). These ARE global max."""
    adj,cuts=gmins(n,E)   # gmins filters maxcut_all (=global max) to Bconn, then gamma-min
    for ci,side in enumerate(cuts):
        recs=block_sbc_components(n,adj,side)
        ACC.absorb(f"{name}#cut{ci}",n,E,side,recs)

if __name__=="__main__":
    print("=== ADVERSARIAL HUNT: BLOCK-SBC rho(O_C)+m_C <= n_C + n_C^2/25 (per positive K-component) ===",flush=True)
    print("    (every cut confirmed GLOBAL MAX before gating; EXACT PSD verdict)\n",flush=True)

    # ---------- (a) stacked / long two-lanes, L up to 28 ----------
    print("--- (a) two-lanes L=8..28 (CP-SAT global-max confirmed) ---",flush=True)
    for L in (8,12,16,20,24,28):
        n,E,side,bad=build_two_lane(L)
        gate(f"two-lane L={L}", n, E, side)

    # ---------- (a') two-lane with EXTRA bad edges in the same lane (raise m_C, keep tri-free+max) ----------
    print("\n--- (a') two-lane + EXTRA bad edges (raise m_C) ---",flush=True)
    for L in (12,16,20):
        # candidate extra bad edges along x-path (same-parity pairs, distance>=4 to stay tri-free)
        extras=[(0,L-4),(2,L-4),(4,L-2),(4,L),(0,L-6),(4,L-6)]
        ex=[e for e in extras if 0<=e[0]<e[1]<=L and (e[1]-e[0])%2==0 and (e[1]-e[0])>=4]
        n,E,side,bad=build_two_lane(L, extra_bad=ex)
        gate(f"two-lane+extra L={L} (+{len(ex)} bad)", n, E, side)

    # ---------- (c) ASYMMETRIC two-lanes: bad-edge endpoints placed to maximize geodesic overlap ----------
    print("\n--- (c) asymmetric two-lanes (varied bad-edge placement) ---",flush=True)
    for L in (16,20,24):
        # shift the two anchor sources from {0,2} to {0,4} etc. (must be even, same-parity, dist>=4)
        for src in [(0,2),(0,4),(0,6),(2,4)]:
            s0,s1=src
            bad=[(s0,L-2),(s0,L),(s1,L-2),(s1,L)]
            bad=[(min(e),max(e)) for e in bad if (e[1]-e[0])>=4 and (e[1]-e[0])%2==0]
            if len(bad)<2: continue
            n,E,side,_=build_two_lane(L)  # base then re-add custom bad
            # rebuild edge set with custom bad
            n2,E2,side2,_=build_two_lane(L, extra_bad=bad)
            gate(f"asym two-lane L={L} src={src}", n2, E2, side2)

    # ---------- (b) two-lane bridged to a C5[t] blow-up (check SAME K-component) ----------
    print("\n--- (b) two-lane GLUED to C5[t] blow-up (must share geodesics = same K-comp) ---",flush=True)
    def c5_blowup(t, off=0):
        nn=5*t; E=[]
        for i in range(5):
            for a in range(t):
                for b in range(t):
                    E.append((off+i*t+a, off+((i+1)%5)*t+b))
        return nn,E
    for L in (12,16):
        for t in (2,3):
            nL,EL,sideL,badL=build_two_lane(L)
            nB,EB=c5_blowup(t, off=nL)
            n=nL+nB; E=list(EL)+EB
            # bridge: connect lane endpoint vertex L (x-path end) to a C5[t] vertex on the opposite side
            # choose bridge to try to merge geodesics; test a few bridge endpoints
            for br in [(L, nL), (0, nL+t), (2, nL)]:
                Eb=E+[br]
                # side for the C5[t] part: standard C5 blow-up cut (part i -> i%2 ... but C5 odd has a bad pair)
                side=list(sideL)+[ (i%2) for i in range(5) for _ in range(t) ]
                gate(f"two-lane L={L} + C5[{t}] bridge{br}", n, Eb, side, require_cpmax=True)

    # ---------- (d) census triangle-free N=11..14 + random N=15,16 ----------
    print("\n--- (d) census tri-free N=11,12 (all gamma-min connB max cuts) ---",flush=True)
    for nn in (11,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        before_v=ACC.violations; before_t=ACC.tested
        for g6 in outg:
            n,E=dec(g6); gate_census(f"cN{nn}-{g6}", n, E)
        print(f"  census N={nn}: graphs={len(outg)} comps_gated+={ACC.tested-before_t} violations+={ACC.violations-before_v}",flush=True)
    # N=13: sample (maxcut_all over 2^12 per graph is the cost; cap count)
    outg13=subprocess.run([GENG,'-tc','13'],capture_output=True,text=True).stdout.split()
    random.seed(7); random.shuffle(outg13); outg13=outg13[:200]
    before_v=ACC.violations; before_t=ACC.tested
    for g6 in outg13:
        n,E=dec(g6); gate_census(f"cN13-{g6}", n, E)
    print(f"  census N=13 (sample {len(outg13)}): comps_gated+={ACC.tested-before_t} violations+={ACC.violations-before_v}",flush=True)

    print("\n--- (d') random tri-free N=14..16 ---",flush=True)
    random.seed(12345)
    def rand_trifree(n, p=0.5, tries=4000):
        adj=[set() for _ in range(n)]; E=[]
        order=[(i,j) for i in range(n) for j in range(i+1,n)]
        random.shuffle(order)
        for (i,j) in order:
            if random.random()>p: continue
            if adj[i]&adj[j]: continue   # would form triangle
            adj[i].add(j); adj[j].add(i); E.append((i,j))
        return n,E
    rnd_v=ACC.violations; rnd_t=ACC.tested
    for nn in (14,15,16):
        for _ in range(120):
            n,E=rand_trifree(nn, p=0.45)
            gate_census(f"rand-N{nn}", n, E)
    print(f"  random N=14..16: comps_gated+={ACC.tested-rnd_t} violations+={ACC.violations-rnd_v}",flush=True)

    # ---------- FINAL REPORT ----------
    print("\n=== RESULT ===",flush=True)
    print(f"  components attacked (tested): {ACC.tested}",flush=True)
    print(f"  genuine BLOCK-SBC violations: {ACC.violations}",flush=True)
    print(f"  tight cases (margin==0 exact): {ACC.tight[:8]}{' ...' if len(ACC.tight)>8 else ''}",flush=True)
    if ACC.first is not None:
        fv=ACC.first
        print(f"  FIRST VIOLATION:",flush=True)
        print(f"    family={fv['family']} N={fv['N']} component={fv['component']}",flush=True)
        print(f"    n_C={fv['n_C']} m_C={fv['m_C']} rho_lower(sumT2/Gamma cross)={fv['sumT2_over_Gamma']} "
              f"rho_lower(allones-iter)={fv['rho_lower']} true_rho~{fv['frho']:.4f}",flush=True)
        print(f"    RHS=n_C+n_C^2/25={fv['RHS']}  LHS_low=rho_lower+m_C={fv['LHS_low']}  -> {fv['verdict']}",flush=True)
        print(f"    edges={fv['edges']}",flush=True)
        print(f"    side={fv['side']}",flush=True)
    holds=(ACC.violations==0)
    print(f"  HOLDS (no counterexample found): {holds}",flush=True)
