"""_wf_deficit_adv.py  --  INDEPENDENT gate of GPT-Pro's DEFICIT-AWARE (LOAD-based) closing Farkas
certificate for Erdos #23 (delta=0 / L=5 PATH-GAMMA reduction).

Prior SIZE-based cone was INFEASIBLE on the glued C5|C7 N=12 witness. The fix: LOAD-based generators
(T = uniform geodesic load from struct_for_side), plus product-slack generators (h_i h_{i+1} - q).

Target inequality, per gamma-min connected-B max cut + bad edge f with ell_f=5 and shortest blue
geodesic P=(x0..x4):
  N=#vertices, Gamma=sum_v T[v], h_i=T[x_i]/N, S=sum h_i, q=min_i(h_i h_{i+1}),
  25*M(P) = 5*(N^2-Gamma) - 25*sum_i(T[x_i]-N) - S^2 + 25*q   (exact Fraction).
Goal: M(P) >= 0.

CERTIFICATE (uniform position-indexed nonneg combo):
  25*M(P) = sum_U alpha_U dGamma(U) + sum_W beta_W (deltaB(W)-deltaM(W)) + sum_i lambda_i (h_i h_{i+1} - q)
with alpha,beta,lambda >= 0 the SAME across every row. Each generator is >= 0 on a gamma-min cut:
  - dGamma(U) >= 0 for NEUTRAL (deltaB(U)=deltaM(U)) connected-B switches U  (gamma-minimality)
  - deltaB(W)-deltaM(W) >= 0                                                  (max-cut)
  - h_i h_{i+1} - q >= 0                                                      (def of q)

EXACT: all generator values and the target are Fractions; LP guesses coeffs with floats; candidate
coeffs are rationalized and the identity is RE-VERIFIED exactly as Fractions on every row.

Run from E:/Projects/ErdosProblems/problems/23/writeup  ->  python _wf_deficit_adv.py
"""
import sys, itertools, subprocess
from fractions import Fraction as F
from collections import deque
sys.path.insert(0, '.')
import numpy as np
from scipy.optimize import linprog

from _h import dec, GENG, Bconn, maxcut_all, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski

# ------------------------------------------------------------------ basic structure helpers
def adj_of(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def gamma_of(n, adj, side):
    st=struct_for_side(n, adj, side)
    if st is None: return None
    return sum(st[2])

def gmin_cuts(n, adj):
    """All connected-B max cuts achieving the minimum Gamma (=sum ell^2)."""
    cuts=[s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj, s, u, v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return []
    gm=min(g for _,g in cand)
    return [s for s,g in cand if g==gm]

def deltaB(n, adj, side, U):
    Uset=set(U)
    return sum(1 for u in range(n) for v in adj[u]
               if v>u and side[u]!=side[v] and ((u in Uset)^(v in Uset)))

def deltaM(n, adj, side, U):
    Uset=set(U)
    return sum(1 for u in range(n) for v in adj[u]
               if v>u and side[u]==side[v] and ((u in Uset)^(v in Uset)))

def dGamma(n, adj, side, U):
    """Gamma(flip U) - Gamma, exact via struct_for_side on flipped side. None if flipped-B
    disconnected or no valid geodesic structure."""
    nb=side[:]
    for v in U: nb[v]^=1
    if not Bconn(n, adj, nb): return None
    g0=gamma_of(n, adj, side); g1=gamma_of(n, adj, nb)
    if g0 is None or g1 is None: return None
    return g1-g0

def is_neutral_conn(n, adj, side, U):
    """neutral switch: deltaB(U)==deltaM(U) AND flipped-B connected."""
    if deltaB(n,adj,side,U)!=deltaM(n,adj,side,U): return False
    nb=side[:]
    for v in U: nb[v]^=1
    return Bconn(n,adj,nb)

# ------------------------------------------------------------------ rows: (graph,cut) -> L=5 path rows
def path_rows(n, E):
    """Every gamma-min connected-B max cut, every bad edge f with ell_f=5 and a UNIQUE shortest blue
    geodesic P=(x0..x4). Returns list of dicts with the row's exact data + the structure to build
    generators. Restricts to unique-geodesic rows so P is well-defined (matches GPT-Pro spec)."""
    adj=adj_of(n,E); rows=[]
    for side in gmin_cuts(n, adj):
        st=struct_for_side(n, adj, side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        N=n; G=sum(T)
        for f in M:
            if ell[f]!=5: continue
            Ps=cyc[f]
            if len(Ps)!=1: continue       # unique geodesic -> P well-defined
            P=Ps[0]
            if len(P)!=5: continue
            rows.append(dict(n=n,E=E,adj=adj,side=side[:],N=N,Gamma=G,T=[T[v] for v in range(n)],
                             M=list(M),ell=dict(ell),f=f,P=list(P),mu={k:v for k,v in mu.items()}))
    return rows

# ------------------------------------------------------------------ position-indexed generators
# Each generator's NAME is position-indexed so the LP coefficient is uniform across rows.
def build_generators(row):
    n=row['n']; adj=row['adj']; side=row['side']; N=row['N']; T=row['T']; P=row['P']
    gens={}   # name -> Fraction value (the generator's value on this row)
    pos={v:i for i,v in enumerate(P)}

    # ---- alpha : neutral connected switch generators (dGamma >= 0) ----
    # single on-path vertex flips
    for i,xi in enumerate(P):
        nm='A_single_%d'%i
        if is_neutral_conn(n,adj,side,[xi]):
            d=dGamma(n,adj,side,[xi]); gens[nm]=d if d is not None else F(0)
        else:
            gens[nm]=F(0)
    # on-path pairs
    for i in range(5):
        for j in range(i+1,5):
            nm='A_pair_%d_%d'%(i,j)
            U=[P[i],P[j]]
            if is_neutral_conn(n,adj,side,U):
                d=dGamma(n,adj,side,U); gens[nm]=d if d is not None else F(0)
            else:
                gens[nm]=F(0)
    # on-path vertex + off-path blue neighbor (aggregate per position: sum of dGamma over all such y)
    for i,xi in enumerate(P):
        nm='A_offnbr_%d'%i
        tot=F(0)
        for y in adj[xi]:
            if y in pos: continue
            if side[y]==side[xi]: continue   # blue neighbor
            U=[xi,y]
            if is_neutral_conn(n,adj,side,U):
                d=dGamma(n,adj,side,U)
                if d is not None: tot+=d
        gens[nm]=tot

    # ---- beta : max-cut generators (deltaB - deltaM >= 0) ----
    for i,xi in enumerate(P):
        gens['B_single_%d'%i]=F(deltaB(n,adj,side,[xi])-deltaM(n,adj,side,[xi]))
    for i in range(5):
        for j in range(i,5):
            U=[P[k] for k in range(i,j+1)]
            gens['B_int_%d_%d'%(i,j)]=F(deltaB(n,adj,side,U)-deltaM(n,adj,side,U))
    # layer sets Lambda_i : BFS layers in blue graph from x0 = P[0], restricted to path positions
    # Lambda_i = {x_i} for a path is degenerate; instead use full-graph blue BFS layers from x0.
    d={P[0]:0}; q=deque([P[0]])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    maxlayer=max(d.values()) if d else 0
    for L in range(0, min(maxlayer,4)+1):
        W=[v for v in range(n) if d.get(v,-1)==L]
        gens['B_layer_%d'%L]=F(deltaB(n,adj,side,W)-deltaM(n,adj,side,W))

    # ---- lambda : product-slack generators (h_i h_{i+1} - q >= 0) ----
    h=[F(T[P[i]],N) for i in range(5)]
    qmin=min(h[i]*h[(i+1)%5] for i in range(5))
    for i in range(5):
        gens['L_prod_%d'%i]=h[i]*h[(i+1)%5]-qmin

    return gens

def target_25M(row):
    N=row['N']; G=row['Gamma']; T=row['T']; P=row['P']
    h=[F(T[P[i]],N) for i in range(5)]        # h_i = T[x_i]/N
    S=sum(h)                                   # S in h-units (NOTE def)
    qmin=min(h[i]*h[(i+1)%5] for i in range(5))
    # 25*M = 5*(N^2-Gamma) - 25*sum_i(T[x_i]-N) - S^2 + 25*q   (S,q in h-units)
    return F(5)*(N*N-G) - F(25)*sum(T[P[i]]-N for i in range(5)) - S*S + F(25)*qmin

# ------------------------------------------------------------------ certificate LP (uniform coeffs)
def fixed_feature_names():
    names=[]
    for i in range(5): names.append('A_single_%d'%i)
    for i in range(5):
        for j in range(i+1,5): names.append('A_pair_%d_%d'%(i,j))
    for i in range(5): names.append('A_offnbr_%d'%i)
    for i in range(5): names.append('B_single_%d'%i)
    for i in range(5):
        for j in range(i,5): names.append('B_int_%d_%d'%(i,j))
    for L in range(5): names.append('B_layer_%d'%L)
    for i in range(5): names.append('L_prod_%d'%i)
    return names

def collect(rows):
    names=fixed_feature_names()
    Arows=[]; bvec=[]; rawgens=[]
    for row in rows:
        g=build_generators(row)
        vec=[g.get(nm,F(0)) for nm in names]
        Arows.append(vec); bvec.append(target_25M(row)); rawgens.append(g)
    return names, Arows, bvec, rawgens

def solve_uniform(names, Arows, bvec):
    """Find alpha,beta,lambda >= 0 with A @ c == b for EVERY row (uniform). Float LP guess."""
    m=len(names); R=len(Arows)
    Af=np.array([[float(x) for x in r] for r in Arows], dtype=float)
    bf=np.array([float(x) for x in bvec], dtype=float)
    # feasibility: minimize 0 s.t. Af c = bf, c>=0
    res=linprog(c=np.zeros(m), A_eq=Af, b_eq=bf, bounds=[(0,None)]*m, method='highs')
    return res, Af, bf

def rationalize(x, maxden=10**6):
    return F(x).limit_denominator(maxden)

def verify_exact(names, Arows, bvec, cfrac):
    """Check A @ cfrac == b exactly on every row, and cfrac>=0."""
    if any(c<0 for c in cfrac): return False, 'negative-coeff'
    for r,(vec,t) in enumerate(zip(Arows,bvec)):
        s=sum(vec[k]*cfrac[k] for k in range(len(names)))
        if s!=t: return False, ('row %d: got %s want %s'%(r,s,t))
    return True, 'ok'

# ------------------------------------------------------------------ generator-nonnegativity audit
def audit_nonneg(rows):
    """Confirm each generator class is >=0 on gamma-min cuts (the premise of the cone)."""
    bad=[]
    for ri,row in enumerate(rows):
        g=build_generators(row)
        for nm,val in g.items():
            if nm.startswith('A_') or nm.startswith('B_') or nm.startswith('L_'):
                if val<0: bad.append((ri,nm,val,row['n'],row['f']))
    return bad

# ================================================================== drivers
def graphs_battery():
    bat=[]
    # decisive witness: glued C5|C7 N=12 with single bridge (0,5)
    n,E=union_disjoint((5,Cn(5)),(7,Cn(7))); E=E+[(0,5)]
    bat.append(('C5|C7 N=12 bridge(0,5)', n, E))
    # other glue bridges
    for br in [[(0,5),(1,6)],[(0,5),(2,7)],[(4,5)]]:
        n,E=union_disjoint((5,Cn(5)),(7,Cn(7))); E=E+br
        bat.append(('C5|C7 N=12 %s'%br, n, E))
    # C5 | C5
    n,E=union_disjoint((5,Cn(5)),(5,Cn(5))); E=E+[(0,5)]
    bat.append(('C5|C5 N=10 bridge', n, E))
    # C5 | C9
    n,E=union_disjoint((5,Cn(5)),(9,Cn(9))); E=E+[(0,5)]
    bat.append(('C5|C9 N=14 bridge', n, E))
    # C5 island + Mycielskian(C7) (N=20) -- C5 embedded near an O-bearing gadget
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    n,E=union_disjoint(isl,g15); E=E+[(0,5)]
    bat.append(('C5 + Myc(C7) N=20 bridge', n, E))
    # Grotzsch = Myc(C5) N=11 (C5 embedded in Mycielskian)
    n,E=mycielski(5,Cn(5))
    bat.append(('Grotzsch=Myc(C5) N=11', n, E))
    return bat

def nonuniform_blowup_rows():
    """Adversarial: nonuniform C5 blow-ups (where uniform-load structure breaks)."""
    out=[]
    from _stark1 import odd_blowup
    for sizes in [(1,3,1,3,1),(1,2,3,2,1),(2,1,2,1,2),(1,4,1,4,1),(3,1,3,1,3),(1,2,1,2,1)]:
        n,E,adj,side=odd_blowup(5,list(sizes))
        out.append(('C5%s N=%d'%(sizes,n), n, E))
    return out

if __name__=='__main__':
    print("=== _wf_deficit_adv : gate GPT-Pro DEFICIT-AWARE (LOAD-based) Farkas certificate ===", flush=True)

    # (1) collect rows from the battery
    allrows=[]; labels=[]
    bat=graphs_battery()+nonuniform_blowup_rows()
    for nm,n,E in bat:
        rs=path_rows(n,E)
        for r in rs: r['label']=nm
        allrows+=rs
        print("  rows from %-28s : %d (N=%d)"%(nm,len(rs),n), flush=True)
    print("  TOTAL L=5 unique-geodesic gamma-min rows: %d"%len(allrows), flush=True)

    # (2) generator nonnegativity audit
    bad=audit_nonneg(allrows)
    print("\n[AUDIT] generators with NEGATIVE value on a gamma-min row: %d"%len(bad), flush=True)
    for b in bad[:10]: print("    NEG %s"%(b,), flush=True)

    # (3) isolate the decisive witness row(s) and report 25*M / C_L / product slacks
    print("\n[WITNESS] decisive glued C5|C7 N=12 f=(0,4) P=(0,1,2,3,4):", flush=True)
    for row in allrows:
        if row['label'].startswith('C5|C7 N=12 bridge(0,5)') and row['f']==(0,4):
            N=row['N']; T=row['T']; P=row['P']
            h=[F(T[P[i]],N) for i in range(5)]
            S=sum(h); qmin=min(h[i]*h[(i+1)%5] for i in range(5))
            CL=S*S-25*qmin
            print("    N=%d Gamma=%d T_path=%s"%(N,row['Gamma'],[str(T[P[i]]) for i in range(5)]), flush=True)
            print("    S=%s q=%s C_L=S^2-25q=%s  25*M=%s"%(S,qmin,CL,target_25M(row)), flush=True)
            g=build_generators(row)
            prodslacks=[g['L_prod_%d'%i] for i in range(5)]
            print("    product-slacks (h_i h_{i+1}-q): %s"%[str(x) for x in prodslacks], flush=True)
            nzB=[(k,str(v)) for k,v in g.items() if k.startswith('B_') and v!=0]
            nzA=[(k,str(v)) for k,v in g.items() if k.startswith('A_') and v!=0]
            print("    nonzero A (switch) gens: %s"%nzA, flush=True)
            print("    nonzero B (maxcut) gens: %s"%nzB, flush=True)
            break

    # (4) UNIFORM certificate LP across ALL rows
    names, Arows, bvec, rawgens = collect(allrows)
    res, Af, bf = solve_uniform(names, Arows, bvec)
    print("\n[LP uniform across %d rows] status=%s success=%s"%(len(allrows),res.status,res.success), flush=True)
    if res.success:
        cf=[rationalize(x) for x in res.x]
        ok,msg=verify_exact(names, Arows, bvec, cf)
        print("  EXACT verify of rationalized coeffs: %s (%s)"%(ok,msg), flush=True)
        if ok:
            print("  UNIFORM CERTIFICATE coefficients (nonzero):", flush=True)
            for nm,c in zip(names,cf):
                if c!=0: print("     %s = %s"%(nm,c), flush=True)
    else:
        print("  UNIFORM LP INFEASIBLE -> cone too small across the battery.", flush=True)

    # (4b) EXACT Farkas certificate of uniform infeasibility:  y with A^T y >= 0 (exact) and b^T y < 0.
    if not res.success:
        R=len(allrows); m=len(names)
        Af2=np.array([[float(x) for x in r] for r in Arows])
        bf2=np.array([float(x) for x in bvec])
        rf=linprog(c=np.zeros(R), A_ub=-Af2.T, b_ub=np.zeros(m),
                   A_eq=np.array([bf2]), b_eq=np.array([-1.0]),
                   bounds=[(None,None)]*R, method='highs')
        if rf.success:
            y=[F(v).limit_denominator(10**7) for v in rf.x]
            colmin=None; colviol=False
            for k in range(m):
                s=sum(Arows[r][k]*y[r] for r in range(R))
                if s<0: colviol=True
                colmin=s if colmin is None or s<colmin else colmin
            bdot=sum(bvec[r]*y[r] for r in range(R))
            print("\n[FARKAS exact] uniform infeasibility certificate y (rationalized):", flush=True)
            print("  min_k (A^T y)_k = %s (need >=0 ; columns violated=%s)"%(colmin,colviol), flush=True)
            print("  b^T y = %s (need <0 for valid Farkas)"%bdot, flush=True)
            if (not colviol) and bdot<0:
                print("  ==> EXACT Farkas certificate VALID: uniform cone CANNOT contain 25*M.", flush=True)
            else:
                print("  ==> rationalized y not exactly valid; HiGHS float infeasibility (status 2) stands.", flush=True)
            nzrows=[(allrows[r]['label'],allrows[r]['f'],str(y[r])) for r in range(R) if y[r]!=0]
            print("  rows carrying the obstruction (nonzero y): %d"%len(nzrows), flush=True)
            for z in nzrows[:12]: print("     %s"%(z,), flush=True)

    # (5) per-row feasibility (does the cone reach 25*M on EACH row in isolation?)
    print("\n[PER-ROW] does the cone reach 25*M on each row alone?", flush=True)
    nfail=0; firstfail=None
    for ri,row in enumerate(allrows):
        g=build_generators(row)
        vec=[g.get(nm,F(0)) for nm in names]
        t=target_25M(row)
        Af1=np.array([[float(x) for x in vec]]).T  # m x 1 ... need single eq
        m=len(names)
        r1=linprog(c=np.zeros(m), A_eq=np.array([[float(x) for x in vec]]),
                   b_eq=np.array([float(t)]), bounds=[(0,None)]*m, method='highs')
        if not r1.success:
            nfail+=1
            if firstfail is None: firstfail=(ri,row['label'],row['f'],str(t))
    print("  per-row infeasible rows: %d / %d"%(nfail,len(allrows)), flush=True)
    if firstfail: print("  FIRST per-row failure: %s"%(firstfail,), flush=True)
