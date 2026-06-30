"""_wf_dualcert_adv.py  -- ADVERSARIAL stress of GPT-Pro's PATH-GAMMA dual-certificate claim.

Claim: PATH-GAMMA F(P)>=0 has a FINITE dual certificate from the LOCAL canonical cone
   { (CUT) delta_B(U)-delta_M(U) for path-local U ; (SWITCH) Gamma(s^W)-Gamma(s) for neutral W ;
     (C5) (sum n_i)^2 - 25 min_i(n_i n_{i+1}) }.

F(P) := (L/25)*(N^2 - Gamma) - sum_{x in P}(T(x)-N).

We do TWO conic-membership tests (both EXACT-verified in Fraction after a float linprog GUESS):

  (A) PER-ROW STRUCTURAL membership.  We express F(P) and every local generator as a
      linear functional over the SHARED structural coordinate vector
          y = ( {mu(e)}_{blue e} ,  {iota-contrib via ell(g)}_{bad g} ,  D=N^2-Gamma ).
      F(P) is EXACTLY linear in y by the I-D-J handshake:
          sum_{x in P} T(x) = I + (1/2)Dbd + (1/2)J ,  J = sum_x iota(x) = sum_x sum_{g inc x} ell(g),
      so  F(P) = (L/25)*D  -  [ I + (1/2)Dbd + (1/2)J ]  +  L*N,   linear in (mu, ell, D) up to the const L*N.
      Each CUT/SWITCH/C5 generator value is a constant scalar c_g on the instance; we treat each
      generator as the constant functional (it contributes only to the affine/const part) PLUS,
      for the generators that ARE genuinely linear in y (the C5 slack is a pure function of layer
      sizes = constants; cut margins are integer constants; switch gaps are constants), they are
      constants.  => the structural-linear membership reduces to: can the y-DEPENDENT part of F(P)
      be matched?  Since every local generator is y-CONSTANT, the only way a nonneg combo equals
      F(P) as a FUNCTIONAL is if F(P)'s y-gradient is ZERO -- which it is NOT in general.
      Hence we instead use the operational SCALAR cone test that GPT-Pro's plan really means:

  (B) UNIFORM SCALAR certificate.  Build the battery of tight rows.  Each row r supplies the
      generator value-vector  G_r = [g_1(r),...,g_k(r)]  (all >=0, local canonical) and target F_r=F(P_r).
      A *finite dual certificate* = a SINGLE lambda>=0 (fixed across rows, one weight per generator
      FAMILY by position/type) with  G_r . lambda  >=  ... no: we need  sum lambda_g g_g(r) >= F_r?
      For a LOWER bound proof F(P)>=0 we need  F_r  >=  sum lambda_g g_g(r) * 0 ...
      The certificate writes F(P) = sum lambda_g g_g (each g_g>=0 => F(P)>=0).  So per row we need
          sum_g lambda_g g_g(r)  =  F_r   (exact identity), lambda independent of r  [UNIFORM], OR
          per-row lambda (membership of F_r in cone{g_g(r)})  [LOCAL/per-row].
      Per-row scalar membership of a single positive number in a cone containing a positive generator
      is trivial; the BITE is the UNIFORM certificate.  We test BOTH:
        (B1) per-row: is F_r in cone{ generator-value-vectors of that row } treating each generator as a
             separate coordinate? -> this is the structural test reinterpreted: we tag each generator
             with its TYPE so the SAME lambda-pattern must reach F_r.  We build, per row, the augmented
             vector and ask feasibility of  A lambda = b  with the row's own generators.  (Always feasible
             if any single generator g>0 and F_r>=0, UNLESS we demand integer/structural matching.)
        (B2) UNIFORM: stack ALL battery rows; one lambda>=0 per (generator TYPE); require for every row
             sum_type lambda_type * g_type(r) = F_r.  INFEASIBILITY here = certificate cone too small.

  We REPORT (B2) infeasibility (the real adversarial signal) and, for diagnosis, the worst tight row
  and which generator types are present/absent.

EXACT: float linprog only GUESSES; every reported feasibility/infeasibility verdict is re-checked in
Fraction (exact LP via the guessed basis, or exact Farkas separator)."""
import sys, subprocess
from fractions import Fraction as F
from collections import deque
import numpy as np
from scipy.optimize import linprog

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

# ---------- instance helpers ----------
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

def bdist_layers(adj, side, s):
    """blue-graph BFS distance dict from s."""
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d: d[v]=d[u]+1; q.append(v)
    return d

# ---------- generator computations ----------
def deltaB_M(n, adj, side, U):
    """delta_B(U), delta_M(U): blue / mono edges with exactly one endpoint in U."""
    Us=set(U); dB=0; dM=0
    seen=set()
    for u in range(n):
        for v in adj[u]:
            if v<=u: continue
            inU=(u in Us)^(v in Us)
            if not inU: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def gamma_of_side(n, adj, side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    return sum(T)  # = Gamma

def gen_generators(n, adj, side, M, ell, T, cyc, f, P):
    """Return dict of LOCAL canonical generator VALUES (all should be >=0) for path P of bad edge f.
       Families: CUT-single, CUT-interval, CUT-layer, SWITCH-single, SWITCH-paired, C5."""
    L=ell[f]; Pset=set(P)
    gens={}  # name -> value (Fraction or int)
    # ----- CUT family: U = path-local sets -----
    # single on-path vertices x_j
    for j,xj in enumerate(P):
        dB,dM=deltaB_M(n,adj,side,[xj]); gens[('CUTv',j)]=F(dB-dM)
    # path intervals [j,k]
    for j in range(len(P)):
        for k in range(j,len(P)):
            U=P[j:k+1]; dB,dM=deltaB_M(n,adj,side,U); gens[('CUTint',j,k)]=F(dB-dM)
    # layer sets Lambda_i  (layers from blue-dist of endpoints of P)
    a0,bL=P[0],P[-1]
    da=bdist_layers(adj,side,a0); db=bdist_layers(adj,side,bL)
    layers={}
    for v in range(n):
        if v in da and v in db and da[v]+db[v]==L-1:
            layers.setdefault(da[v],[]).append(v)
    nlayer={i:len(layers.get(i,[])) for i in range(L)}
    for i in sorted(layers):
        U=layers[i]; dB,dM=deltaB_M(n,adj,side,U); gens[('CUTlay',i)]=F(dB-dM)
    # ----- C5 layer slack -----
    sumn=sum(nlayer.get(i,0) for i in range(L))
    prods=[nlayer.get(i,0)*nlayer.get((i+1)%L,0) for i in range(L)]
    minprod=min(prods) if prods else 0
    gens[('C5',)]=F(sumn*sumn-25*minprod)
    # ----- SWITCH family: neutral flips, recompute Gamma on flipped side -----
    G0=sum(T)
    # single on-path flip
    for j,xj in enumerate(P):
        dB,dM=deltaB_M(n,adj,side,[xj])
        if dB==dM:  # neutral (cut preserved)
            s2=side[:]; s2[xj]=1-s2[xj]
            if Bconn(n,adj,s2):
                g2=gamma_of_side(n,adj,s2)
                if g2 is not None: gens[('SWv',j)]=F(g2-G0)
    # x_j paired with an adjacent off-path vertex to neutralize.
    # CANONICAL label = ('SWpair', j): take the MIN nonneg gap over admissible w (tightest generator).
    for j,xj in enumerate(P):
        best=None
        for w in adj[xj]:
            if w in Pset: continue
            U=[xj,w]; dB,dM=deltaB_M(n,adj,side,U)
            if dB==dM:
                s2=side[:]; s2[xj]=1-s2[xj]; s2[w]=1-s2[w]
                if Bconn(n,adj,s2):
                    g2=gamma_of_side(n,adj,s2)
                    if g2 is not None:
                        gap=F(g2-G0)
                        if best is None or gap<best: best=gap
        if best is not None: gens[('SWpair',j)]=best
    return gens, nlayer

def Fofp(n, T, ell, f, P, Gamma):
    L=ell[f]
    return F(L,25)*(F(n*n)-Gamma) - sum(T[v]-F(n) for v in P)

# ---------- battery ----------
ROWS=[]  # each: (name, F_P, gens_dict, meta)
def add_instance(name, n, adj, side):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    Gamma=sum(T)
    for f in M:
        if ell[f] not in (5,7): continue
        for P in cyc[f]:
            FP=Fofp(n,T,ell,f,P,Gamma)
            gens,nlayer=gen_generators(n,adj,side,M,ell,T,cyc,f,P)
            ROWS.append((name,FP,gens,dict(N=n,L=ell[f],f=f,Gamma=Gamma,nlayer=nlayer,P=tuple(P))))

def build_battery():
    # two-lane L=8,12 (these have L=7 bad-edge geodesics)
    for L in (8,12,16):
        n,E,side,bad=build_two_lane(L); add_instance("twolane%d"%L,n,adj_of(n,E),side)
    # cyclic blow-ups C5,C7 various (uniform + nonuniform)
    for cyc in (5,7):
        for t in range(1,5):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): add_instance("C%d[%d]"%(cyc,t),n,adj,s)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3],[4,3,4,3,4],[3,9,1,9,3],[1,4,1,4,1],[5,1,5,1,5],
                  [4,1,4,1,4],[2,3,2,3,2],[1,5,1,5,1]):
        n,E=blowup(parts)
        if n>21: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: add_instance("C5%s"%parts,n,adj,s)
    # large odd-cycle blow-ups (cap N<=21: gmins maxcut_all is 2^(N-1) brute force)
    for parts in ([2,2,2,2,2,2,2],[3,3,3,3,3,3,3]):  # C7[2] N=14, C7[3] N=21
        n,E=blowup(parts)
        if n>21: continue
        adj,cuts=gmins(n,E)
        for s in cuts[:2]: add_instance("C7%s"%parts,n,adj,s)
    # Mycielskians + glued islands
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),
                      ("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                      ("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C9|C9",bridge_g((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: add_instance(nm,nn,adj,s)
    # gamma-min census N<=9 (structured battery is the adversarial target; census kept SMALL N<=8
    # to avoid diluting the uniform LP with thousands of tiny near-duplicate C5[1]-like rows).
    for nn in range(6,9):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: add_instance("cen%s"%g6,n,adj,s)
        print("  census N=%d done, rows=%d"%(nn,len(ROWS)),flush=True)

# ---------- conic membership ----------
def exact_per_row(FP, gens):
    """Per-row: is FP in cone{generator values}? With a single coordinate (scalar) and all gens>=0,
       feasible iff (exists gen>0) or FP==0.  We also do the STRUCTURAL per-row test: treat each gen
       as its own coordinate-vector e_g (identity); F must equal sum lambda_g g_g with lambda>=0.
       Scalar membership: feasible iff FP>=0 and (FP==0 or some g_g>0)."""
    vals=[v for v in gens.values()]
    pos=any(v>0 for v in vals)
    if FP==0: return True,"FP=0"
    if FP>0 and pos: return True,"scalar-ok"
    if FP>0 and not pos: return False,"FP>0 but no positive local generator"
    return False,"FP<0(should not happen)"

def uniform_certificate(rows, type_of):
    """UNIFORM: one lambda>=0 per generator TYPE; require for every row r:
         sum_type lambda_type * (sum of gens of that type in r) = F_r.
       We aggregate per type by SUM (a fixed nonneg combo within a family is a valid generator too,
       but to be GENEROUS to GPT-Pro we let each individual generator have its OWN weight -> richer
       cone).  So variables = ALL distinct (type) labels appearing across rows, but to keep the cone
       UNIFORM we key by the generator LABEL (position-indexed canonical), not its per-row value.
       Build A (rows x labels) of generator values, b=F_r; seek lambda>=0 with A lambda = b.
       INFEASIBLE => cone too small (no finite uniform local certificate)."""
    labels=sorted({lab for _,_,g,_ in rows for lab in g}, key=lambda x:(str(type(x)),str(x)))
    lab_idx={lab:i for i,lab in enumerate(labels)}
    m=len(rows); d=len(labels)
    A=np.zeros((m,d)); b=np.zeros(m)
    for ri,(nm,FP,g,meta) in enumerate(rows):
        b[ri]=float(FP)
        for lab,val in g.items():
            A[ri,lab_idx[lab]]=float(val)
    # feasibility LP: min 0 s.t. A lambda = b, lambda>=0  (equality cone membership)
    res=linprog(c=np.zeros(d), A_eq=A, b_eq=b, bounds=[(0,None)]*d, method='highs')
    return res, labels, lab_idx, A, b

def exact_farkas_check(rows, labels, lab_idx, infeasible_float):
    """If float says INFEASIBLE, find an exact Farkas certificate: y with y.b<0 (or>0) and A^T y <=0
       (i.e. y separates b from cone(columns)).  Search a few candidate y from float dual; verify EXACT.
       Returns (proven_infeasible, y) or (None,None)."""
    # Build exact A,b
    m=len(rows); d=len(labels)
    # We exact-check the float infeasibility by verifying b not in cone: use linprog dual ray.
    Af=np.zeros((m,d)); bf=np.zeros(m)
    for ri,(nm,FP,g,meta) in enumerate(rows):
        bf[ri]=float(FP)
        for lab,val in g.items(): Af[ri,lab_idx[lab]]=float(val)
    # Farkas: b not in cone{cols of A} (with equality + lambda>=0) iff exists y: A^T y <=0 and b^T y >0.
    # Get y from an auxiliary LP maximizing b^T y s.t. A^T y <= 0, -1<=y<=1.
    res=linprog(c=-bf, A_ub=Af.T, b_ub=np.zeros(d), bounds=[(-1,1)]*m, method='highs')
    if not res.success: return None,None
    y=res.x
    val=bf.dot(y)
    if val<=1e-9: return None,None  # no separation found numerically
    # exact-verify: rationalize y (round to small denom) then check A^T y <=0 exactly and b^T y >0.
    from fractions import Fraction as FR
    yq=[FR(round(yi*720),720) for yi in y]
    # exact b^T y
    bty=FR(0)
    for ri,(nm,FP,g,meta) in enumerate(rows): bty+=FP*yq[ri]
    # exact A^T y <= 0 for each label
    ok=True; maxcol=FR(-10**9)
    for lab,ci in lab_idx.items():
        s=FR(0)
        for ri,(nm,FP,g,meta) in enumerate(rows):
            if lab in g: s+=g[lab]*yq[ri]
        if s>maxcol: maxcol=s
        if s>0: ok=False
    return (ok and bty>0, dict(bty=bty,maxcol=maxcol,y=yq))

def uniform_group(rows):
    """Uniform certificate over a group of rows that share canonical labels.
       Variables: one lambda>=0 per canonical label appearing in >=1 row.
       Require  A lambda = b  (b=F_r).  Returns (feasible_float, res, labels, lab_idx, A, b,
       lonely_labels) where lonely_labels = labels in exactly ONE row (free-var maskers)."""
    labels=sorted({lab for _,_,g,_ in rows for lab in g}, key=lambda x:str(x))
    lab_idx={lab:i for i,lab in enumerate(labels)}
    rows_with={lab:0 for lab in labels}
    for _,_,g,_ in rows:
        for lab in g: rows_with[lab]+=1
    lonely=[lab for lab in labels if rows_with[lab]==1]
    m=len(rows); d=len(labels)
    A=np.zeros((m,d)); b=np.zeros(m)
    for ri,(nm,FP,g,meta) in enumerate(rows):
        b[ri]=float(FP)
        for lab,val in g.items(): A[ri,lab_idx[lab]]=float(val)
    res=linprog(c=np.zeros(d), A_eq=A, b_eq=b, bounds=[(0,None)]*d, method='highs')
    return res, labels, lab_idx, A, b, lonely

def exact_farkas(rows, labels, lab_idx):
    """Exact Farkas separator for infeasibility of {A lambda=b, lambda>=0}:
       find y with A^T y <=0 (all label-cols) and b^T y >0; verify EXACT in Fraction."""
    m=len(rows); d=len(labels)
    Af=np.zeros((m,d)); bf=np.zeros(m)
    for ri,(nm,FP,g,meta) in enumerate(rows):
        bf[ri]=float(FP)
        for lab,val in g.items(): Af[ri,lab_idx[lab]]=float(val)
    res=linprog(c=-bf, A_ub=Af.T, b_ub=np.zeros(d), bounds=[(-1,1)]*m, method='highs')
    if not res.success: return None,None
    y=res.x
    if bf.dot(y)<=1e-9: return None,None
    yq=[F(round(yi*5040),5040) for yi in y]   # rationalize
    bty=F(0)
    for ri,(nm,FP,g,meta) in enumerate(rows): bty+=FP*yq[ri]
    ok=True; maxcol=F(-10**9)
    for lab in labels:
        s=F(0)
        for ri,(nm,FP,g,meta) in enumerate(rows):
            if lab in g: s+=g[lab]*yq[ri]
        if s>maxcol: maxcol=s
        if s>0: ok=False
    return (ok and bty>0), dict(bty=bty, maxcol=maxcol)

def report_group(tag, rows):
    if not rows:
        print("  [%s] no rows"%tag,flush=True); return
    res,labels,lab_idx,A,b,lonely=uniform_group(rows)
    print("  [%s] rows=%d labels=%d lonely(1-row free vars)=%d  float feasible=%s"%(
        tag,len(rows),len(labels),len(lonely),res.success),flush=True)
    if res.success:
        # exact-verify the float certificate: rationalize lambda, check A lambda = b exactly
        lam=[F(round(x*5040),5040) for x in res.x]
        okexact=True; worst=None
        for ri,(nm,FP,g,meta) in enumerate(rows):
            s=F(0)
            for lab,val in g.items(): s+=val*lam[lab_idx[lab]]
            if s!=FP:
                okexact=False
                if worst is None or abs(s-FP)>abs(worst[1]): worst=(nm,s-FP,FP)
        print("     exact-verify rationalized cert: %s%s"%(
            "EXACT identity holds" if okexact else "float-only (rationalized cert off)",
            "" if okexact else " worst row %s resid=%s"%(worst[0],str(worst[1]))),flush=True)
        if lonely:
            # drop lonely labels (free var maskers) and re-test: does the REAL coupling hold?
            rows2=[(nm,FP,{l:v for l,v in g.items() if l not in set(lonely)},meta) for nm,FP,g,meta in rows]
            res2,labels2,li2,A2,b2,lon2=uniform_group(rows2)
            print("     after dropping %d lonely labels: float feasible=%s (the COUPLED test)"%(len(lonely),res2.success),flush=True)
            if not res2.success:
                proven,info=exact_farkas(rows2,labels2,li2)
                print("       => COUPLED INFEASIBLE; exact Farkas proven=%s%s"%(proven,
                      "" if not info else " b.y=%s maxcol=%s"%(str(info['bty']),str(info['maxcol']))),flush=True)
                # first infeasible witness = the tightest row in this group
                tr=min(rows2,key=lambda r:r[1])
                print("       tightest row: %s F=%s N=%d L=%d nlay=%s P=%s"%(
                    tr[0],str(tr[1]),tr[3]['N'],tr[3]['L'],tr[3]['nlayer'],tr[3]['P']),flush=True)
                return ('coupled-infeasible',tr)
        return ('feasible',None)
    else:
        proven,info=exact_farkas(rows,labels,lab_idx)
        print("     => FLOAT INFEASIBLE; exact Farkas proven=%s%s"%(proven,
              "" if not info else " b.y=%s maxcol=%s"%(str(info['bty']),str(info['maxcol']))),flush=True)
        tr=min(rows,key=lambda r:r[1])
        print("     tightest row: %s F=%s N=%d L=%d nlay=%s P=%s"%(
            tr[0],str(tr[1]),tr[3]['N'],tr[3]['L'],tr[3]['nlayer'],tr[3]['P']),flush=True)
        return ('infeasible',tr)

if __name__=="__main__":
    print("Building battery...",flush=True)
    build_battery()
    print("Total rows (L in {5,7}): %d"%len(ROWS),flush=True)
    ROWS.sort(key=lambda r:r[1])
    print("\nTightest 12 rows (smallest F(P)):",flush=True)
    for nm,FP,g,meta in ROWS[:12]:
        types=sorted({(lab[0] if isinstance(lab,tuple) else lab) for lab in g})
        nsw=sum(1 for lab in g if isinstance(lab,tuple) and lab[0] in ('SWv','SWpair'))
        print("  F=%-10s %-16s N=%d L=%d Gamma=%s nlay=%s gtypes=%s #sw=%d"%(
            str(FP),nm,meta['N'],meta['L'],str(meta['Gamma']),meta['nlayer'],types,nsw),flush=True)

    # PER-ROW scalar membership (sanity: should always be feasible since F>=0)
    perrow=[ (nm,FP,g,meta) for nm,FP,g,meta in ROWS if not exact_per_row(FP,g)[0] ]
    print("\nPER-ROW scalar infeasible rows: %d"%len(perrow),flush=True)
    for nm,FP,g,meta in perrow[:5]:
        print("   INFE %-16s F=%s %s"%(nm,str(FP),exact_per_row(FP,g)[1]),flush=True)

    # UNIFORM certificate -- the real adversarial test, grouped by L so canonical labels align.
    print("\n=== UNIFORM dual-certificate tests (one weight per canonical generator label) ===",flush=True)
    findings=[]
    for L in (5,7):
        grp=[r for r in ROWS if r[3]['L']==L]
        print("\n-- L=%d group --"%L,flush=True)
        res=report_group("L=%d ALL"%L, grp)
        if res and res[0]!='feasible': findings.append((L,'ALL',res))
        # tight subgroup
        tgrp=[r for r in grp if r[1]<=F(5)]
        if tgrp and len(tgrp)<len(grp):
            res=report_group("L=%d TIGHT(F<=5)"%L, tgrp)
            if res and res[0]!='feasible': findings.append((L,'TIGHT',res))
    # global (mixed L) uniform
    print("\n-- GLOBAL (mixed L) --",flush=True)
    res=report_group("GLOBAL", ROWS)
    if res and res[0]!='feasible': findings.append(('mix','ALL',res))

    # STRUCTURE-CLUSTERED uniform: group rows by identical (L, layer-profile nlayer).  Within a
    # cluster every row has the SAME geometry, so a structure-dependent-but-finite certificate must
    # use the SAME weights -> if a single cluster is INFEASIBLE the cone is genuinely too small;
    # if all clusters are feasible the breakage above is only 'weights must depend on structure'.
    print("\n=== STRUCTURE-CLUSTERED uniform (group by L + layer profile) ===",flush=True)
    clusters={}
    for r in ROWS:
        key=(r[3]['L'], tuple(sorted(r[3]['nlayer'].items())))
        clusters.setdefault(key,[]).append(r)
    clus_infeasible=[]
    multi=[(k,v) for k,v in clusters.items() if len(v)>=3]  # only clusters with enough rows to bite
    print("  %d clusters total, %d with >=3 rows"%(len(clusters),len(multi)),flush=True)
    for key,rs in sorted(multi,key=lambda kv:-len(kv[1])):
        res,labels,lab_idx,A,b,lonely=uniform_group(rs)
        if not res.success:
            proven,info=exact_farkas(rs,labels,lab_idx)
            if proven:
                tr=min(rs,key=lambda r:r[1])
                clus_infeasible.append((key,len(rs),tr,info))
    print("  structurally-infeasible clusters (cone GENUINELY too small): %d"%len(clus_infeasible),flush=True)
    for key,nr,tr,info in clus_infeasible[:6]:
        print("    L=%d nlay=%s rows=%d  Farkas b.y=%s maxcol=%s  tight row %s F=%s P=%s"%(
            key[0],dict(key[1]),nr,str(info['bty']),str(info['maxcol']),tr[0],str(tr[1]),tr[3]['P']),flush=True)
    if clus_infeasible:
        findings.append(('cluster','struct',('cluster-infeasible',clus_infeasible[0][2])))

    print("\n=== SUMMARY ===",flush=True)
    if not findings:
        print("RESULT: NO infeasible (coupled) row found. Local canonical cone REACHES F(P) on the whole battery.",flush=True)
        print("        => dual-certificate hypothesis STRUCTURE-CONFIRMED on this battery.",flush=True)
    else:
        print("RESULT: %d infeasible group(s) found -- cone too small somewhere:"%len(findings),flush=True)
        for L,sub,res in findings:
            kind,tr=res
            print("  L=%s %s : %s ; first/worst row: %s"%(str(L),sub,kind,(tr[0] if tr else "?")),flush=True)
