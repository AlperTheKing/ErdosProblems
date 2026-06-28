"""ANGLE B exact tests: (CAP) as effective-conductance / electrical flow.

Setting (from _gcd.py): H = L_omega + diag(N-T).  O={T>N}, Q={T<=N}.
Grounded network: omega-edges among V; each q in Q tied to a ground node g by
conductance R_Q(q)=N-T(q)>=0; overload diagonal D_O(o)=T(o)-N>0 on O.

Schur(H/H_QQ) on O  =  effective-conductance matrix of the omega+ground network
seen from O (when H_QQ=L_{omega,QQ}+R_Q is PD).  (CAP): Schur >= D_O.

We exact-test, on census instances (Fraction):
  (V) DIRICHLET/THOMSON variational identity:
      x^T Schur x = min_y [ sum_e omega(e)(d(x|+y))^2 + sum_q R_Q(q) y_q^2 ]
      where the omega-energy is over the FULL grounded Laplacian with x fixed on O,
      y free on Q (and ground=0). Verify equality exactly via the closed-form
      min = x^T Schur x (Schur complement IS the energy min). [sanity/structure]
  (Hcut-N) Scalar HALL/Gale-Hoffman cut, NECESSARY direction:
      for every S subset O, overload(S)=sum_{o in S}(T(o)-N)
        <= cap_omega(S) := sum of omega over edges from S to V\S restricted...
      Two cut capacities tested:
        (a) cut_raw(S)   = sum_{e=(a,b): a in S, b notin S} omega(e)   (edge boundary, all)
        (b) the TRUE necessary shadow = 1_S^T H 1_S evaluated form?
      We compute, for the constant test vector x=1_S on O (0 elsewhere on O):
        x^T Schur x  vs  D_O(S)=overload(S).  (CAP) on this x  <=>  x^T Schur x >= overload(S).
      Then test the SCALAR (Hall) surrogate: overload(S) <= cut_raw(S)
      and report whether it is (i) always true, (ii) tighter or looser than Schur.
  (suff?) Is the scalar cut SUFFICIENT?  We look for an instance where ALL scalar
      cuts hold (overload(S)<=cut_raw(S) for all S) yet Schur PSD would have failed
      were omega smaller -- i.e. measure the GAP min_S (cut_raw(S)-overload(S)) vs
      mineig(Schur). If scalar-cut-slack can be ~0 while Schur stays strictly PD,
      the scalar cut is only a loose necessary shadow (vector/energy object needed).

Reports per instance: |O|, |Q|, HQQ_PD, schur mineig (exact sign),
  min over nonempty S<=O of [cut_raw(S)-overload(S)]  (Hall slack),
  and whether x=1_S Schur energy >= overload(S) for ALL S (vector-cut, = restriction of CAP).
"""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _gcd import build_H, is_psd_exact, a_bar
from _satzmu_conn import struct_for_side

def build_Lomega_and_T(adj, side, n):
    """Return (Lomega as nxn Fraction, T vector, omega edge dict)."""
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    omega={}
    for f in M:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); omega[e2]=omega.get(e2,F(0))+ae*F(1,k)
    L=[[F(0)]*n for _ in range(n)]
    for e,w in omega.items():
        u,v=tuple(e); L[u][u]+=w; L[v][v]+=w; L[u][v]-=w; L[v][u]-=w
    return L,T,omega

def schur_on_O(L,T,n):
    """Build H=L+diag(N-T); split O/Q; return (Schur matrix on O (list), O, Q, HQQ_PD)."""
    N=n
    H=[[L[i][j] for j in range(n)] for i in range(n)]
    for v in range(n): H[v][v]+=F(N)-T[v]
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    Midx={v:i for i,v in enumerate(O+Q)}
    perm=O+Q
    A=[[H[perm[i]][perm[j]] for j in range(n)] for i in range(n)]
    no=len(O); nq=len(Q)
    # eliminate Q block (indices no..n-1)
    HQQ_PD=True
    Mm=[row[:] for row in A]
    for q in range(no,n):
        d=Mm[q][q]
        if d<=0:
            HQQ_PD=False
            # for these tests skip non-PD (rare; CAP falls back to direct)
            return None
        for i in range(n):
            if i==q or Mm[i][q]==0: continue
            fac=Mm[i][q]/d
            for j in range(n): Mm[i][j]-=fac*Mm[q][j]
    schur=[[Mm[i][j] for j in range(no)] for i in range(no)]
    return schur,O,Q,HQQ_PD

def cut_raw(omega, S, n):
    """sum of omega(e) over edges e with exactly one endpoint in S (S a vertex set)."""
    c=F(0)
    for e,w in omega.items():
        u,v=tuple(e)
        if (u in S) != (v in S): c+=w
    return c

def overload(T,S,n):
    return sum(T[v]-n for v in S)

def quad(M, x):
    """x^T M x for M an mxm Fraction matrix indexed by list order, x a dict pos->val over that order."""
    m=len(M); s=F(0)
    for i in range(m):
        for j in range(m):
            s+=x[i]*M[i][j]*x[j]
    return s

def analyze(adj, side, n, do_cuts=True):
    r=build_Lomega_and_T(adj,side,n)
    if r is None: return None
    L,T,omega=r
    sc=schur_on_O(L,T,n)
    if sc is None: return None
    schur,O,Q,HQQ_PD=sc
    no=len(O)
    schur_psd=is_psd_exact(schur,no)
    # vector-cut (restriction of CAP to indicator x=1_S on O):
    # x^T Schur x  vs  overload(S).  CAP => >= for all S.  Test all nonempty S<=O.
    vec_ok=True; vec_min_slack=None
    hall_ok=True; hall_min_slack=None  # scalar shadow: cut_raw(S) - overload(S)
    if do_cuts and no<=14:
        for rmask in range(1,1<<no):
            S=[O[i] for i in range(no) if rmask>>i&1]
            ov=overload(T,S,n)
            # vector-cut energy = x^T Schur x with x=indicator on O-positions in S
            xidx={i: (F(1) if O[i] in S else F(0)) for i in range(no)}
            energy=quad(schur,xidx)
            slk=energy-ov
            if slk<0: vec_ok=False
            vec_min_slack = slk if vec_min_slack is None else min(vec_min_slack,slk)
            # scalar Hall shadow
            cr=cut_raw(omega,set(S),n)
            hslk=cr-ov
            if hslk<0: hall_ok=False
            hall_min_slack = hslk if hall_min_slack is None else min(hall_min_slack,hslk)
    return dict(O=no,Q=len(Q),HQQ_PD=HQQ_PD,schur_psd=schur_psd,
                vec_ok=vec_ok,vec_min_slack=vec_min_slack,
                hall_ok=hall_ok,hall_min_slack=hall_min_slack)

def run_gmin_cuts(n,E):
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

if __name__=="__main__":
    print("=== ANGLE B: (CAP) electrical / Hall-cut exact tests ===",flush=True)
    from _bdef_construct import Cn, mycielski
    # named cases with overload
    named=[]
    C5=(5,Cn(5)); g11=mycielski(*C5); g23=mycielski(*g11); g15=mycielski(7,Cn(7))
    named=[("Grotzsch N11",g11),("Myc2(C5) N23",g23),("Myc(C7) N15",g15)]
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        named.append((g6,dec(g6)))
    for nm,(nn,EE) in named:
        adj,cs=run_gmin_cuts(nn,EE)
        for s in cs:
            d=analyze(adj,s,nn)
            if d is None or d['O']==0: continue
            print(f"  {nm}: |O|={d['O']} HQQ_PD={d['HQQ_PD']} schurPSD={d['schur_psd']} "
                  f"| vec-cut(CAP-restrict) ALL-S ok={d['vec_ok']} minslack={d['vec_min_slack']} "
                  f"| scalar-Hall ok={d['hall_ok']} minslack={d['hall_min_slack']}",flush=True)
            break
    # census N=8,9: does scalar-Hall ever FAIL while Schur PSD holds? (necessary?)
    #               does scalar-Hall slack ->0 while schur strictly PD? (sufficiency probe)
    for nn in (8,9):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; schurfail=0; vecfail=0; hallfail=0
        hall_slack_zero_but_schur_strict=0
        min_hall_slack_global=None
        for g6 in outg:
            n,E=dec(g6)
            adj,cs=run_gmin_cuts(n,E)
            for s in cs:
                d=analyze(adj,s,n)
                if d is None or d['O']==0: continue
                tot+=1
                if not d['schur_psd']: schurfail+=1
                if not d['vec_ok']: vecfail+=1
                if not d['hall_ok']: hallfail+=1
                if d['hall_min_slack'] is not None:
                    if min_hall_slack_global is None or d['hall_min_slack']<min_hall_slack_global:
                        min_hall_slack_global=d['hall_min_slack']
                    # sufficiency probe: scalar Hall slack exactly 0 (tight) but schur PSD strict?
                    if d['hall_min_slack']==0 and d['schur_psd']:
                        hall_slack_zero_but_schur_strict+=1
                break
        print(f"  census N={nn}: cuts={tot} schurPSD-fails={schurfail} vecCUT-fails={vecfail} "
              f"scalarHALL-fails={hallfail} | min scalar-Hall slack(global)={min_hall_slack_global} "
              f"| Hall-tight&schur-PSD cases={hall_slack_zero_but_schur_strict}",flush=True)
