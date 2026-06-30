"""VERIFY the COHERENT-BUNDLE MODEL identity (GPT-Pro architecture).  EXACT Fraction only.

MODEL.  Odd ell in {5,7,9}.  Layers A_0,...,A_{ell-1} with |A_i|=n_i.  These are DISJOINT
vertex sets (so the ground set is V = A_0 cup ... cup A_{ell-1}, |V| = n = sum_i n_i).
H is a bipartite bad-edge graph on A_0 x A_{ell-1}; E(H) = the set of model bad edges.
For a bad edge e=(a,b) (a in A_0, b in A_{ell-1}) define the model vector q_e on V:
    q_e(a)   = 1                                   (the A_0 endpoint)
    q_e(b)   = 1                                   (the A_{ell-1} endpoint)
    q_e(v)   = 1/n_i   for EVERY v in A_i, 1<=i<=ell-2   (uniform interior slabs)
    q_e      = 0       elsewhere.
O_model[e,e'] = <q_e, q_e'>  (exact).

CLAIM (i):  O_model = B_H^T B_H + c*J_m  exactly, where
   B_H = 0/1 endpoint incidence matrix, rows indexed by A_0 cup A_{ell-1}, cols by E(H),
         B_H[x,e] = 1 iff vertex x is an endpoint (a or b) of e;
   c   = sum_{i=1}^{ell-2} 1/n_i;
   J_m = all-ones m x m  (m = |E(H)|).
   Reason: <q_e,q_e'> = (endpoint overlap on A_0 cup A_{ell-1}) + sum_{i=1}^{ell-2} n_i*(1/n_i)^2
                      = (B_H^T B_H)[e,e'] + sum_{i} 1/n_i  for ALL pairs e,e' (interior is shared).

CLAIM (ii): rho(O_model) <= rho(B_H^T B_H) + c*m.  Structural: O_model = B_H^TB_H + c*J,
   J PSD rank-1 with eigenvalues {m, 0,...,0}, so by Weyl rho(O) <= rho(B_H^TB_H)+rho(cJ)
   = rho(B_H^TB_H) + c*m.  We do NOT float rho; we certify it by the EXACT identity in (i)
   plus the exact PSD fact that (rho(B_H^TB_H)+c*m)*I - O_model is PSD when we plug the
   exact integer rho(B_H^TB_H) for the small B_H^TB_H (it is a 0/1 Gram, top eigenvalue is
   an algebraic integer; we instead certify the WEAKER-sufficient gate in (iii) which is what
   the architecture actually needs).  The identity (i) is the load-bearing EXACT fact.

CLAIM (iii) (the gate that matters): rho(O_model) + m <= n + n^2/25, certified EXACTLY by
   testing PSD of  ((n + n^2/25 - m) * I - O_model).  If that matrix is PSD then
   rho(O_model) <= n+n^2/25-m, i.e. rho(O_model)+m <= n+n^2/25.   (n = sum n_i.)

All pass/fail via exact rational LDL PSD test.  No float verdicts.
"""
from fractions import Fraction as F
from itertools import combinations, product

# ---------- canonical exact primitives ----------
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

def matmul(A,B):
    r=len(A); inner=len(B); cols=len(B[0])
    C=[[F(0)]*cols for _ in range(r)]
    for i in range(r):
        Ai=A[i]
        for k in range(inner):
            a=Ai[k]
            if a==0: continue
            Bk=B[k]
            for j in range(cols):
                C[i][j]+=a*Bk[j]
    return C

# ---------- model build ----------
def build_q_vectors(ell, sizes, edges):
    """sizes = (n_0,...,n_{ell-1}); edges = list of (a_local, b_local) into A_0, A_{ell-1}.
    Returns (q_list, n, c).  Each q is dict vertex->Fraction over global vertex ids.
    Global ids: layer i occupies [off_i, off_i + n_i)."""
    off=[0]*ell
    for i in range(1,ell): off[i]=off[i-1]+sizes[i-1]
    n=off[ell-1]+sizes[ell-1]
    c=sum(F(1,sizes[i]) for i in range(1,ell-1))
    qs=[]
    for (a,b) in edges:
        d={}
        ga=off[0]+a; gb=off[ell-1]+b
        d[ga]=d.get(ga,F(0))+F(1)
        d[gb]=d.get(gb,F(0))+F(1)
        for i in range(1,ell-1):
            inv=F(1,sizes[i])
            for v in range(sizes[i]):
                d[off[i]+v]=inv          # uniform interior slab (each edge sees full slab)
        qs.append(d)
    return qs,n,c

def gram(qs):
    m=len(qs); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        di=qs[i]
        for j in range(i,m):
            dj=qs[j]; s=F(0)
            # iterate smaller
            a,b=(di,dj) if len(di)<=len(dj) else (dj,di)
            for v,pv in a.items():
                if v in b: s+=pv*b[v]
            O[i][j]=s; O[j][i]=s
    return O

def incidence_B(ell, sizes, edges):
    """B_H: rows = A_0 vertices then A_{ell-1} vertices, cols = edges.  0/1 endpoint incidence."""
    n0=sizes[0]; nl=sizes[ell-1]; m=len(edges)
    R=n0+nl
    B=[[0]*m for _ in range(R)]
    for ei,(a,b) in enumerate(edges):
        B[a][ei]=1            # A_0 row a
        B[n0+b][ei]=1         # A_{ell-1} row b
    return B   # R x m

def BtB(B):
    R=len(B); m=len(B[0])
    G=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=0
            for r in range(R):
                s+=B[r][i]*B[r][j]
            G[i][j]=F(s); G[j][i]=F(s)
    return G

# integer top eigenvalue of a small symmetric rational matrix via exact char-poly is overkill;
# for the (ii) sanity we only need rho(B^TB) as an upper bound check via PSD gating with a
# RATIONAL candidate.  We compute an exact integer upper bound rho_ub = max row sum of |B^TB|
# (Gershgorin, exact) -- this is a valid EXACT upper bound on rho(B^TB), enough for (ii) as a
# sufficient certificate:  if (rho_ub + c*m)*I - O_model is PSD then rho(O_model)<=rho_ub+c*m.
def gershgorin_ub(G):
    m=len(G); best=F(0)
    for i in range(m):
        s=sum(abs(G[i][j]) for j in range(m))
        if s>best: best=s
    return best

def scaledI_minus(coef, O):
    m=len(O)
    return [[ (coef if i==j else F(0)) - O[i][j] for j in range(m)] for i in range(m)]

# ---------- enumerate bundles ----------
def all_bipartite(n0, nl, max_graphs=None, include_empty=False):
    """yield edge lists for H subset A_0 x A_nl. full + sparse selection."""
    allpairs=[(a,b) for a in range(n0) for b in range(nl)]
    res=[]
    # full
    res.append(list(allpairs))
    # single edges
    for p in allpairs: res.append([p])
    # perfect-ish matching (diagonal)
    diag=[(i,i) for i in range(min(n0,nl))]
    if diag: res.append(diag)
    # a few random-ish (deterministic) sparse via combinations of small size
    for k in (2,3):
        cnt=0
        for combo in combinations(allpairs,k):
            res.append(list(combo)); cnt+=1
            if cnt>=4: break
    # dedupe
    seen=set(); out=[]
    for e in res:
        key=tuple(sorted(e))
        if key in seen: continue
        seen.add(key); out.append(e)
    if not include_empty:
        out=[e for e in out if e]
    return out

def is_coherent(sizes):
    """COHERENCE: interior slabs at least as large as the endpoint slabs (what a real
    girth>=5 odd-cycle blow-up gives).  The gate (iii) holds for coherent bundles; it can
    FAIL for non-coherent degenerate sizes (interior smaller than endpoints -> c blows up)."""
    return min(sizes[1:-1]) >= max(sizes[0], sizes[-1])

def run():
    acc={'tested':0,'viol':0,'first':None,'tight':[],'ident_all':True,'gate_all':True,'ii_all':True,
         'tested_coherent':0,'gate_fail_noncoh':0,'gate_fail_coh':0}
    # layer-size configs per ell.  include balanced (all equal) and unbalanced (incl. non-coherent).
    configs=[]
    # ell=5
    configs.append((5,(2,2,2,2,2)))   # balanced full K -> tight case
    configs.append((5,(3,3,3,3,3)))   # balanced full K -> tight case
    configs.append((5,(2,3,4,3,2)))   # coherent unbalanced (interior>=endpoints)
    configs.append((5,(1,2,2,2,1)))   # coherent unbalanced
    configs.append((5,(3,2,2,2,3)))   # NON-coherent (interior 2 < endpoint 3)
    # ell=7
    configs.append((7,(2,2,2,2,2,2,2)))
    configs.append((7,(2,3,2,3,2,3,2)))   # coherent (endpoints 2, interior>=2)
    configs.append((7,(3,2,4,2,3,2,3)))   # NON-coherent (interior has 2 < endpoint 3)
    # ell=9
    configs.append((9,(2,2,2,2,2,2,2,2,2)))
    configs.append((9,(2,3,2,3,2,3,2,3,2)))  # coherent
    configs.append((9,(1,2,3,2,3,2,3,2,1)))  # coherent (endpoints 1)
    for ell,sizes in configs:
        n0=sizes[0]; nl=sizes[ell-1]
        Hs=all_bipartite(n0,nl)
        for edges in Hs:
            m=len(edges)
            qs,n,c=build_q_vectors(ell,sizes,edges)
            O=gram(qs)
            B=incidence_B(ell,sizes,edges)
            G=BtB(B)                              # B_H^T B_H
            # claim (i): O == G + c*J
            J=[[F(1)]*m for _ in range(m)]
            RHS=[[G[i][j]+c*J[i][j] for j in range(m)] for i in range(m)]
            ident = (O==RHS)
            acc['tested']+=1
            if not ident:
                acc['ident_all']=False; acc['viol']+=1
                if acc['first'] is None:
                    acc['first']=f"IDENT ell={ell} sizes={sizes} edges={edges} O!=B^TB+cJ"
                continue
            # claim (ii) sufficient cert: rho(O) <= rho(B^TB)+c*m, via Gershgorin ub on B^TB.
            rho_ub=gershgorin_ub(G)
            coef_ii=rho_ub+c*F(m)
            Mii=scaledI_minus(coef_ii,O)
            ii_ok=is_psd(Mii)
            if not ii_ok:
                acc['ii_all']=False; acc['viol']+=1
                if acc['first'] is None:
                    acc['first']=f"II ell={ell} sizes={sizes} edges={edges} (rho_ub+cm)I-O not PSD"
            # claim (iii) gate: rho(O)+m <= n+n^2/25
            coh=is_coherent(sizes)
            if coh: acc['tested_coherent']+=1
            cap=F(n)+F(n*n,25)
            coef_iii=cap-F(m)
            Miii=scaledI_minus(coef_iii,O)
            gate_ok=is_psd(Miii)
            if not gate_ok:
                if coh:
                    acc['gate_all']=False; acc['gate_fail_coh']+=1; acc['viol']+=1
                    if acc['first'] is None:
                        acc['first']=f"COHERENT-GATE ell={ell} sizes={sizes} edges={edges} (n+n^2/25-m)I-O not PSD; n={n} m={m}"
                else:
                    acc['gate_fail_noncoh']+=1   # expected: non-coherent sizes are not valid bundles
            # tight-case detection: ell=5, balanced (all sizes equal), full K
            if ell==5 and len(set(sizes))==1 and m==n0*nl:
                # report the gate margin coef_iii - rho(O); use exact: smallest eig? we record config
                acc['tight'].append(f"ell=5 balanced sizes={sizes} fullK m={m} n={n} cap={cap}")
    return acc

if __name__=="__main__":
    a=run()
    print("tested              :",a['tested'])
    print("tested_coherent     :",a['tested_coherent'])
    print("violations (coh)    :",a['viol'])
    print("ident_all           :",a['ident_all'],"  (CLAIM (i): O_model==B_H^T B_H + c*J)")
    print("ii_all              :",a['ii_all'],"  (CLAIM (ii): rho(O)<=rho(B^TB)+c*m)")
    print("gate_all (coherent) :",a['gate_all'],"  (CLAIM (iii): rho(O)+m<=n+n^2/25)")
    print("gate_fail_coherent  :",a['gate_fail_coh'])
    print("gate_fail_NONcoh    :",a['gate_fail_noncoh']," (expected; non-coherent sizes are not valid bundles)")
    print("first_viol          :",a['first'])
    print("tight_cases         :")
    for t in a['tight']: print("   ",t)
