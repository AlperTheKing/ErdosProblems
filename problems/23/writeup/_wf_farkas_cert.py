"""UNIFORM FARKAS DUAL-CERTIFICATE gate for PATH-GAMMA (L=5).

For each (gamma-min connected-B max cut, bad edge f with ell_f=5, shortest blue geodesic P of f) we build ONE row:
  target  F(P) = (5/25)(N^2 - Gamma) - sum_{x in P}(T(x)-N)
  and a FIXED, POSITION-INDEXED list of canonical generators g_1..g_K (>=0 on a gamma-min max cut).
Then solve the conic-membership LP:  find lambda>=0 UNIFORM across all rows with  F(P_i) = sum_k lambda_k g_{i,k}.
Float-solve to GUESS lambda, then VERIFY EXACTLY in Fraction on every row.

Generators (position-indexed by the path P=(x_0..x_4), all >=0 on a gamma-min MAX cut):
  (CUT) delta_B(U)-delta_M(U) for U in:
        - single path vertices x_0..x_4                          [5]
        - path intervals [j,k], 0<=j<=k<=4 (contiguous)          [15]
        - layer sets Lambda_i, i=0..4                            [5]
  (SWITCH) Gamma(s^W)-Gamma(s) for neutral connected single on-path-vertex flips W={x_j}, j=0..4 (0 if inactive) [5]
  (C5)  (sum_i n_i)^2 - 25*min_i(n_i n_{i+1})  from layer sizes n_i=|Lambda_i|                     [1]
Total K = 31 generators, identical indexing across every row.

Run from E:/Projects/ErdosProblems/problems/23/writeup:  python _wf_farkas_cert.py
"""
import os, sys, subprocess, itertools
from fractions import Fraction as F
from collections import deque
import numpy as np
from scipy.optimize import linprog

from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free

# ---------------- blue-graph BFS distance (cut edges only) ----------------
def bdist_from(adj, side, s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d

# ---------------- Gamma of a side vector (None if not gamma-eligible: not connected-B / no bad edge / disconnected bad) ----------------
def gamma_of(n, adj, side):
    if not Bconn(n, adj, side): return None
    st=struct_for_side(n, adj, side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    return sum(ell[f]**2 for f in M)

# ---------------- generator block for ONE row ----------------
def row_generators(n, adj, side, st, f, P):
    """Return (F_target, gvec) where gvec is the fixed length-K Fraction list, and a label list (once)."""
    M,ell,T,mu,cyc=st
    N=n
    Gamma=sum(ell[g]**2 for g in M)
    L=ell[f]                      # ==5 here
    Pset=set(P)
    # target
    Ftar=F(L,25)*(N*N-Gamma)-sum(T[x]-N for x in P)

    # blue / mono adjacency as edge predicates
    def is_blue(u,v): return side[u]!=side[v]
    def is_mono(u,v): return side[u]==side[v]
    # delta_B(U)-delta_M(U): count edges crossing boundary of U
    def cut_margin(U):
        Us=set(U)
        dB=0; dM=0
        for u in range(n):
            for v in adj[u]:
                if v<=u: continue
                cross=(u in Us)^(v in Us)
                if not cross: continue
                if is_blue(u,v): dB+=1
                else: dM+=1
        return F(dB-dM)

    gens=[]; labels=[]

    # (CUT) single path vertices x_0..x_4
    for j in range(5):
        gens.append(cut_margin([P[j]])); labels.append(f"CUTv{j}")
    # (CUT) path intervals [j,k]
    for j in range(5):
        for k in range(j,5):
            gens.append(cut_margin(P[j:k+1])); labels.append(f"CUTint[{j},{k}]")
    # (CUT) layers Lambda_i: Lambda_i = {v: dB(x_0,v)=i and dB(v,x_4)=4-i}
    d0=bdist_from(adj, side, P[0])
    dL=bdist_from(adj, side, P[L-1])
    Lam=[[] for _ in range(L)]
    for v in range(n):
        if v in d0 and v in dL:
            i=d0[v]
            if i<L and dL[v]==(L-1-i):
                Lam[i].append(v)
    for i in range(5):
        gens.append(cut_margin(Lam[i])); labels.append(f"CUTlayer{i}")

    # (SWITCH) neutral connected single on-path vertex flip W={x_j}: gap = Gamma(s^W)-Gamma(s) >=0 (gamma-min)
    # only valid if delta_B(W)==delta_M(W) (flip keeps it a MAX cut) AND flipped side still connected-B & gamma-eligible.
    for j in range(5):
        xj=P[j]
        s2=side[:]; s2[xj]=1-s2[xj]
        # neutrality: cut size unchanged <=> delta_B({xj})==delta_M({xj})
        dB=sum(1 for v in adj[xj] if is_blue(xj,v))
        dM=sum(1 for v in adj[xj] if is_mono(xj,v))
        g=F(0)
        if dB==dM:
            G2=gamma_of(n, adj, s2)
            if G2 is not None:
                g=F(G2-Gamma)        # >=0 by gamma-minimality (only if s2 still a valid gamma-eligible MAX cut)
        gens.append(g); labels.append(f"SWITCHv{j}")

    # (C5) cyclic-min-product slack from layer sizes
    nsz=[len(Lam[i]) for i in range(5)]
    tot=sum(nsz)
    minprod=min(nsz[i]*nsz[(i+1)%5] for i in range(5))
    gens.append(F(tot*tot-25*minprod)); labels.append("C5slack")

    return Ftar, gens, labels

# ---------------- validity: a PATH-GAMMA instance needs a gamma-min global-MAX connected-B cut ----------------
def is_global_maxcut(n, adj, side):
    E=[(u,v) for u in range(n) for v in adj[u] if v>u]
    sz=sum(1 for u,v in E if side[u]!=side[v])
    mx=max(sum(1 for u,v in E if s[u]!=s[v]) for s in maxcut_all(n,adj))
    return sz==mx

def is_gamma_min(n, adj, side):
    """Among all connected-B global-MAX cuts, is `side` of minimum Gamma?"""
    if not is_global_maxcut(n, adj, side): return False
    G0=gamma_of(n, adj, side)
    if G0 is None: return False
    best=None
    for s in maxcut_all(n,adj):
        if not is_global_maxcut(n,adj,s): continue
        g=gamma_of(n,adj,s)
        if g is None: continue
        if best is None or g<best: best=g
    return best is not None and G0==best

# ---------------- collect rows from one (n,adj,side) ----------------
def collect_rows(name, n, adj, side, rows, labels_box, dedupe, require_gmin=False, path_cap=None):
    if not Bconn(n, adj, side): return
    if require_gmin and not is_gamma_min(n, adj, side): return
    st=struct_for_side(n, adj, side)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if ell[f]!=5: continue
        Ps=cyc[f] if path_cap is None else cyc[f][:path_cap]
        for P in Ps:
            Ftar, gens, labels = row_generators(n, adj, side, st, f, P)
            if labels_box[0] is None: labels_box[0]=labels
            key=(tuple(gens), Ftar)
            if key in dedupe: continue
            dedupe.add(key)
            rows.append((name, n, f, tuple(P), Ftar, gens))

# ---------------- builders ----------------
def from_E(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def blow_cyclic(L, sizes):
    n=sum(sizes); start=[0]*L
    for i in range(1,L): start[i]=start[i-1]+sizes[i-1]
    adj=[set() for _ in range(n)]
    for i in range(L):
        j=(i+1)%L
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u=start[i]+a; v=start[j]+b; adj[u].add(v); adj[v].add(u)
    side=[None]*n
    for i in range(L):
        for a in range(sizes[i]): side[start[i]+a]=i%2
    return n,adj,side

def glue_C5_C7():
    # C5 (0..4) glued to C7 (5..11) by a single bridge edge (0,5); both odd cycles -> bad edges of ell 5 and 7.
    E=[(i,(i+1)%5) for i in range(5)]
    E+=[(5+i,5+(i+1)%7) for i in range(7)]
    E+=[(0,5)]
    return 12, E

# ============================================================ MAIN ============================================================
def main():
    rows=[]; labels_box=[None]; dedupe=set()
    fam_of_row=[]   # parallel family tag per row

    def tag(name):
        if name.startswith("C5["): return "pureC5"
        if name.startswith("theta"): return "theta"
        if name.startswith("glue"): return "glued"
        return "census"

    # --- census N<=10, gamma-min cuts via gmins ---
    MAXN=int(os.environ.get("PG_MAXN","10"))
    for nn in range(5,MAXN+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj=from_E(n,E)
            _,cuts=gmins(n,E)
            for side in cuts:
                before=len(rows)
                collect_rows(f"cen{g6}", n, adj, side, rows, labels_box, dedupe)
                for _ in range(len(rows)-before): fam_of_row.append("census")
        print(f"  [census N={nn}] cumulative rows={len(rows)}", flush=True)

    print("  [post-census] entering theta section", flush=True)
    # --- theta-witness graphs (gamma-min global-max connected-B cuts via gmins) ---
    for g6 in ["G?Fw","H?AFBo]"]:
        n,E=dec(g6); adj=from_E(n,E)
        _,cuts=gmins(n,E)
        for side in cuts:
            before=len(rows)
            collect_rows(f"theta{g6}", n, adj, side, rows, labels_box, dedupe)
            for _ in range(len(rows)-before): fam_of_row.append("theta")

    # --- uniform + nonuniform C5 blow-ups: feed ONLY genuine gamma-min global-max cuts via gmins ---
    # Uniform t=1..3 (t=4, n=20, omitted: its deduped rows are blow-up-isomorphic to t<=3 and the
    # geodesic enumeration in struct_for_side is exponential; nonuniform cases below stress asymmetry).
    c5_sizes=[[t]*5 for t in range(1,4)]+[[2,1,2,1,2],[3,2,3,2,3],[2,1,2,1,3]]
    for sizes in c5_sizes:
        n,adj,_=blow_cyclic(5,sizes)
        E=[(u,v) for u in range(n) for v in adj[u] if v>u]
        _,cuts=gmins(n,E)
        cap=64 if n>=16 else None   # cap shortest-geodesic enumeration for large blow-ups (avoids 4^k explosion)
        for side in cuts:
            before=len(rows)
            collect_rows(f"C5{tuple(sizes)}", n, adj, side, rows, labels_box, dedupe, path_cap=cap)
            for _ in range(len(rows)-before): fam_of_row.append("pureC5")
        print(f"  [C5{tuple(sizes)}] cuts={len(cuts)} cap={cap} cumulative rows={len(rows)}", flush=True)

    # --- C5 | C7 glued (gamma-min global-max connected-B cuts via gmins) ---
    n,E=glue_C5_C7(); adj=from_E(n,E)
    _,cuts=gmins(n,E)
    for side in cuts:
        before=len(rows)
        collect_rows("glueC5C7", n, adj, side, rows, labels_box, dedupe)
        for _ in range(len(rows)-before): fam_of_row.append("glued")

    labels=labels_box[0]
    K=len(labels) if labels else 0
    print(f"collected rows={len(rows)} generators K={K}")
    if not rows:
        print("NO ROWS"); return
    # family breakdown
    from collections import Counter
    print("family row counts:", dict(Counter(fam_of_row)))

    # ---------------- LP (float) : find lambda>=0 with G lambda = F ----------------
    G=np.array([[float(g) for g in gv] for (_,_,_,_,_,gv) in rows])   # rows x K
    Fv=np.array([float(ft) for (_,_,_,_,ft,_) in rows])
    # equality feasibility: minimize 0 s.t. G lambda = F, lambda>=0
    # linprog: A_eq @ x = b_eq
    res=linprog(c=np.zeros(K), A_eq=G, b_eq=Fv, bounds=[(0,None)]*K, method="highs")
    print("LP status:", res.status, res.message)
    if res.status!=0:
        # try least-squares NNLS-style relaxation to expose the missing direction (Farkas)
        analyze_infeasible(G, Fv, labels, rows, fam_of_row)
        return

    lam_float=res.x
    print("float lambda (nonzero):")
    for k in range(K):
        if abs(lam_float[k])>1e-9:
            print(f"   {labels[k]:>14s}  {lam_float[k]:.6f}")

    # ---------------- exact verification: round lambda to small rationals ----------------
    lam_exact=[round_rat(v) for v in lam_float]
    ok, badrows = verify_exact(G_rows(rows), [ft for (_,_,_,_,ft,_) in rows], lam_exact, K)
    if ok:
        print("EXACT VERIFY: PASS (G lambda == F as Fractions on every row)")
        report_support(lam_exact, labels, rows, fam_of_row)
        return

    print(f"EXACT VERIFY with naive rounding FAILED on {len(badrows)} rows; trying support-restricted exact solve...")
    # restrict to float-support and solve exact rational system on that support
    supp=[k for k in range(K) if abs(lam_float[k])>1e-7]
    lam2=exact_solve_support(rows, supp, K)
    if lam2 is not None:
        ok2, badrows2 = verify_exact(G_rows(rows), [ft for (_,_,_,_,ft,_) in rows], lam2, K)
        if ok2 and all(lam2[k]>=0 for k in range(K)):
            print("EXACT VERIFY (support-restricted rational solve): PASS")
            report_support(lam2, labels, rows, fam_of_row)
            return
        else:
            print(f"support-restricted solve: nonneg={all(lam2[k]>=0 for k in range(K))} verify_bad={0 if ok2 else len(badrows2)}")
    print("APPROXIMATE ONLY: float LP feasible but no exact nonneg rational certificate confirmed.")
    print("float support:", [labels[k] for k in supp])

def G_rows(rows):
    return [gv for (_,_,_,_,_,gv) in rows]

def round_rat(x, maxden=60):
    return F(x).limit_denominator(maxden)

def verify_exact(Gr, Fr, lam, K):
    bad=[]
    for i,(gv,ft) in enumerate(zip(Gr,Fr)):
        s=sum(lam[k]*gv[k] for k in range(K))
        if s!=ft: bad.append(i)
    return (len(bad)==0), bad

def exact_solve_support(rows, supp, K):
    """Solve G[:,supp] lambda = F exactly (least-squares via rational normal equations) -- only if consistent."""
    Gr=[gv for (_,_,_,_,_,gv) in rows]
    Fr=[ft for (_,_,_,_,ft,_) in rows]
    m=len(supp)
    # normal equations A^T A x = A^T b in exact Fraction
    ATA=[[F(0)]*m for _ in range(m)]
    ATb=[F(0)]*m
    for gv,ft in zip(Gr,Fr):
        a=[gv[supp[j]] for j in range(m)]
        for j in range(m):
            ATb[j]+=a[j]*ft
            for l in range(m):
                ATA[j][l]+=a[j]*a[l]
    x=gauss_solve(ATA, ATb)
    if x is None: return None
    lam=[F(0)]*K
    for j in range(m): lam[supp[j]]=x[j]
    return lam

def gauss_solve(A, b):
    n=len(A)
    M=[[A[i][j] for j in range(n)]+[b[i]] for i in range(n)]
    r=0
    for c in range(n):
        piv=None
        for i in range(r,n):
            if M[i][c]!=0: piv=i; break
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]
        pv=M[r][c]
        M[r]=[x/pv for x in M[r]]
        for i in range(n):
            if i!=r and M[i][c]!=0:
                fct=M[i][c]
                M[i]=[M[i][j]-fct*M[r][j] for j in range(n+1)]
        r+=1
    x=[F(0)]*n
    # back out: assume full rank on pivot cols
    for i in range(n):
        # find pivot col in row i
        for c in range(n):
            if M[i][c]==1 and all(M[i][cc]==0 for cc in range(n) if cc!=c):
                x[c]=M[i][n]; break
    return x

def report_support(lam, labels, rows, fam_of_row):
    K=len(labels)
    print("=== CERTIFICATE TEMPLATE (uniform lambda support) ===")
    for k in range(K):
        if lam[k]!=0:
            print(f"   {labels[k]:>14s}  = {lam[k]}")
    # per-family check: does the SAME lambda close every family row exactly? (it does, by construction of verify)
    from collections import defaultdict
    famrows=defaultdict(list)
    for i,(_,_,_,_,ft,gv) in enumerate(rows): famrows[fam_of_row[i]].append((ft,gv))
    print("--- per-family: same uniform lambda exact-closes all rows ---")
    for fam,rs in famrows.items():
        allok=all(sum(lam[k]*gv[k] for k in range(K))==ft for ft,gv in rs)
        # also tightness profile: how many rows have F=0 (tight) vs >0
        ntight=sum(1 for ft,_ in rs if ft==0)
        print(f"   {fam:>8s}: rows={len(rs)} exact-closed={allok} tight(F=0)={ntight}")

def analyze_infeasible(G, Fv, labels, rows, fam_of_row):
    print("=== INFEASIBLE: searching Farkas dual direction (row not in cone) ===")
    # Farkas: exists y with y^T G <= 0 (componentwise, since lambda>=0) and y^T F > 0.
    # find via LP: maximize y^T F s.t. G^T y <= 0, -1<=y<=1.
    m,K=G.shape
    res=linprog(c=-Fv, A_ub=G.T, b_ub=np.zeros(K), bounds=[(-1,1)]*m, method="highs")
    if res.status==0 and -res.fun>1e-7:
        y=res.x
        print(f"Farkas certificate of infeasibility found: y^T F = {-res.fun:.6e} > 0 while G^T y <= 0.")
        contrib=[(abs(y[i]), i) for i in range(m)]
        contrib.sort(reverse=True)
        print("top rows in the missing direction:")
        for w,i in contrib[:8]:
            nm,n,f,P,ft,gv=rows[i]
            print(f"   y={y[i]:+.4f} fam={fam_of_row[i]} {nm} N={n} bad={f} P={P} F={float(ft):.4f}")
    else:
        print("no clean Farkas direction from bounded LP; reporting per-family infeasibility instead.")

if __name__=="__main__":
    main()
