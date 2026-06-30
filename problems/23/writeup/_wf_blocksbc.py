"""EXACT-gate BLOCK-SBC (block-Schur barrier the GPT-Pro proof reduces to).

For each gamma-min connected-B max cut:
 1) (M,ell,T,mu,cyc)=struct_for_side; skip if None or M empty. Build O=gram_O(M,cyc).
 2) comp,find=kcomponents(n,cyc). Group bad edges f by find(f[0]).
 3) VERIFY O block-diagonal over K-components: bad edges f,g in different K-comps => O[f,g]==0 exactly.
    Any nonzero cross-block entry is a STRUCTURAL violation (reported).
 4) For each positive K-component C (>=1 bad edge): m_C=#bad edges, n_C=|comp[root]|, O_C=O restricted to C.
    Gate BLOCK-SBC EXACTLY:  rho(O_C)+m_C <= n_C + n_C^2/25
      <=>  (n_C + n_C^2/25 - m_C)*I - O_C  is PSD (exact rational LDL).

EXACT Fraction only for every pass/fail. Never float for a verdict.

BATTERY: two-lane L in {8,12,16,20}; census N=5..10 (all gmins cuts); C5/C7/C9[t] t=1..4 (N<=24);
Mycielski(C5)=Grotzsch, Mycielski(C7); glued islands C7|Grotzsch, C5|C7 (single bridge).

Run from E:/Projects/ErdosProblems/problems/23/writeup:  python _wf_blocksbc.py
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

# ---------- CANONICAL EXACT primitives (verbatim from task spec) ----------
def adj_of(n, E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

def pf_dict(cyc_f):    # p_f(v) as Fraction
    k=len(cyc_f); d={}
    for P in cyc_f:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d

def gram_O(M, cyc):    # O[i][j]=<p_fi,p_fj> exact
    pf=[pf_dict(cyc[f]) for f in M]; m=len(M); O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        for j in range(i,m):
            s=F(0); di=pf[i]; dj=pf[j]
            for v,pv in di.items():
                if v in dj: s+=pv*dj[v]
            O[i][j]=s; O[j][i]=s
    return O

def is_psd(A):         # exact rational LDL PSD test for symmetric A
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

def has_zero_pivot(A):  # detect a zero pivot during LDL (tightness signature)
    m=len(A); W=[r[:] for r in A]; zero=False
    for k in range(m):
        p=W[k][k]
        if p==0: zero=True; continue
        for i in range(k+1,m):
            if W[i][k]==0: continue
            f=W[i][k]/p
            for j in range(k,m): W[i][j]-=f*W[k][j]
    return zero

# ---------- the BLOCK-SBC gate on one cut ----------
def gate_cut(name, n, adj, side):
    """Return dict with per-component gate results + structural block-diagonality check.
       results: list of (compname, n_C, m_C, c, psd_ok, tight). struct_viol: list of cross-block nonzeros."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    O = gram_O(M, cyc)
    comp, find = kcomponents(n, cyc)
    m = len(M)
    # group bad-edge indices by K-component root (via find(f[0]))
    root_of = [find(M[i][0]) for i in range(m)]
    groups = {}
    for i in range(m):
        groups.setdefault(root_of[i], []).append(i)
    # (3) structural block-diagonality: O[i,j]==0 for i,j in different K-comps
    struct_viol = []
    for i in range(m):
        for j in range(i+1, m):
            if root_of[i] != root_of[j] and O[i][j] != 0:
                struct_viol.append((name, M[i], M[j], str(O[i][j])))
    # (4) gate each positive component
    results = []
    for root, idxs in groups.items():
        m_C = len(idxs)
        n_C = len(comp[root])
        c = F(n_C) + F(n_C*n_C, 25) - F(m_C)   # the rho bound c = n_C + n_C^2/25 - m_C
        # O_C = O restricted to this component's bad edges
        OC = [[O[a][b] for b in idxs] for a in idxs]
        # PSD of c*I - O_C
        B = [[ (c if r==s_ else F(0)) - OC[r][s_] for s_ in range(m_C)] for r in range(m_C)]
        psd_ok = is_psd(B)
        tight = has_zero_pivot(B) and psd_ok
        results.append((root, n_C, m_C, c, psd_ok, tight))
    return dict(name=name, M=M, results=results, struct_viol=struct_viol)

# ---------- battery accumulation ----------
class Acc:
    def __init__(self):
        self.tested=0; self.violations=0; self.first=None
        self.struct_total=0; self.struct_first=None
        self.tight_families=set()
        self.census_first=None   # smallest census violator, for reporting
    def absorb(self, name, gate):
        if gate is None: return
        for (name2, fi, fj, val) in gate['struct_viol']:
            self.struct_total += 1
            if self.struct_first is None:
                self.struct_first = (name2, str(fi), str(fj), val)
        for (root, n_C, m_C, c, psd_ok, tight) in gate['results']:
            self.tested += 1
            if not psd_ok:
                self.violations += 1
                if self.first is None:
                    self.first = (name, n_C, m_C, str(c),
                                  "rho(O_C)+m_C > n_C+n_C^2/25 : (c*I-O_C) NOT PSD")
                if self.census_first is None and name.startswith('census-'):
                    self.census_first = (name, n_C, m_C, str(c))
            if tight:
                # family = name with any '#cut..' / 'census-N..-<g6>' / '[t]' suffix stripped to a clean label
                base = name.split('#')[0]
                if base.startswith('census-N'):
                    fam = base.split('-')[1]          # e.g. 'N10'  (census tight case)
                    fam = 'census-' + fam
                else:
                    fam = base.split('[')[0].strip()  # e.g. 'C5', 'C5|C7', 'two-lane L=8'
                self.tight_families.add(fam)

ACC = Acc()

def run_all_gmins(name, n, E):
    adj, cuts = gmins(n, E)
    for ci, side in enumerate(cuts):
        g = gate_cut(f"{name}#cut{ci}", n, adj, side)
        ACC.absorb(f"{name}#cut{ci}", g)

def cyc_blowup(m, t):
    nn=m*t; E=[]
    for i in range(m):
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, ((i+1)%m)*t+b))
    return nn, E

if __name__=="__main__":
    print("=== BLOCK-SBC EXACT gate: rho(O_C)+m_C <= n_C + n_C^2/25 per K-component ===", flush=True)

    # --- two-lane L in {8,12,16,20}: cut is the GIVEN 'side' (not gmins) ---
    for L in (8,12,16,20):
        n,E,side,bad = build_two_lane(L)
        adj = adj_of(n,E)
        g = gate_cut(f"two-lane L={L}", n, adj, side)
        ACC.absorb(f"two-lane L={L}", g)
        if g is not None:
            rs = "; ".join(f"C(n={nc},m={mc}):PSD={psd}{' TIGHT' if tg else ''}"
                           for (_,nc,mc,c,psd,tg) in g['results'])
            print(f"  two-lane L={L} N={n}: comps=[{rs}] struct_viol={len(g['struct_viol'])}", flush=True)

    # --- census N=5..10, ALL gamma-min cuts ---
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cnt_before = ACC.tested; v_before = ACC.violations; s_before = ACC.struct_total
        for g6 in outg:
            n,E = dec(g6)
            run_all_gmins(f"census-N{nn}-{g6}", n, E)
        print(f"  census N={nn}: graphs={len(outg)} comps_gated={ACC.tested-cnt_before} "
              f"violations+={ACC.violations-v_before} struct_viol+={ACC.struct_total-s_before}", flush=True)

    # --- blow-ups C5/C7/C9[t], t=1..4, N<=24 ---
    for m in (5,7,9):
        for t in (1,2,3,4):
            n,E = cyc_blowup(m,t)
            if n>24: continue
            cnt_before = ACC.tested
            run_all_gmins(f"C{m}[{t}]", n, E)
            print(f"  C{m}[{t}] N={n}: comps_gated={ACC.tested-cnt_before}", flush=True)

    # --- Mycielskians ---
    gn,gE = mycielski(5,Cn(5))      # Grotzsch N=11
    run_all_gmins("Grotzsch(MycC5)", gn, gE)
    print(f"  Grotzsch(MycC5) N={gn}: done (cum tested={ACC.tested})", flush=True)
    gn7,gE7 = mycielski(7,Cn(7))    # N=15
    run_all_gmins("MycC7", gn7, gE7)
    print(f"  MycC7 N={gn7}: done (cum tested={ACC.tested})", flush=True)

    # --- glued islands via union_disjoint + single bridge edge ---
    # C7 | Grotzsch, bridge edge between island vtx 0 and gadget vtx 0
    nA,EA = union_disjoint((7,Cn(7)),(gn,gE))
    EA = EA + [(0, 7+0)]   # bridge: island C7 vtx 0 -- Grotzsch vtx 0 (offset 7)
    run_all_gmins("C7|Grotzsch", nA, EA)
    print(f"  C7|Grotzsch N={nA}: done (cum tested={ACC.tested})", flush=True)
    # C5 | C7, single bridge
    nB,EB = union_disjoint((5,Cn(5)),(7,Cn(7)))
    EB = EB + [(0, 5+0)]   # bridge: C5 vtx 0 -- C7 vtx 0 (offset 5)
    run_all_gmins("C5|C7", nB, EB)
    print(f"  C5|C7 N={nB}: done (cum tested={ACC.tested})", flush=True)

    # ---------- FINAL REPORT ----------
    print("\n=== RESULT ===", flush=True)
    print(f"  components gated      : {ACC.tested}")
    print(f"  PSD violations        : {ACC.violations}")
    print(f"  first violation       : {ACC.first}")
    print(f"  smallest census viol  : {ACC.census_first}")
    print(f"  structural cross-block: {ACC.struct_total} (first: {ACC.struct_first})")
    print(f"  tight families        : {sorted(ACC.tight_families)}")
    holds = (ACC.violations==0)
    print(f"  HOLDS (0 viol)        : {holds}")
    print(f"  block-diagonal held   : {ACC.struct_total==0}")
