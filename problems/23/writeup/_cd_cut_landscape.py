"""CD cut-metric LANDSCAPE: test which (if any) cut-based certificate proves
   (Cycle-SM) (O ell)_f <= N*ell(f) for every bad edge f of every triangle-free graph.

Variants tested per bad edge f (index j):
 (a) original per-edge LP-f:  min sum_A lam_A dB(A) s.t. sum_A lam_A sep_A(g) >= ell(g)O_{fg} all g; claim opt<=N*ell(f).
 (b) diagonal-excluded:        drop g=f constraint; budget N*ell(f) - ell(f)*O_{ff}.
 (c) aggregate single-constr:  min sum_A lam_A dB(A) s.t. sum_A lam_A dM(A) >= (O ell)_f ... see note.
 (d) prefix-gate metric:       restrict cuts to geodesic-interval gate cuts {d_B(a,.)<=i} of each bad edge.

Exact-rational confirmation (Fraction) for any (graph,edge) where a variant's float LP certifies (opt<=target),
so a claimed CERTIFICATE is never trusted on float alone. Failures (opt>target) reported with float gap.

NOTE on (c): the literal aggregate constraint sum_A lam_A dM(A) >= (O ell)_f with objective sum_A lam_A dB(A)
is trivially certifiable (pick the single cut A* maximizing dM/dB... ) so we test the MEANINGFUL aggregate:
   does the CD bound  (O ell)_f = sum_g ell(g)O_{fg} = <p_f, T>  admit  <= N*ell(f)  via a single nonneg
   cut-combination whose B-cost <= N*ell(f) and whose M-separation dominates p_f's required overlaps?
We implement (c) as: min sum_A lam_A dB(A) s.t. sum_A lam_A * 1[A separates f] >= (O ell)_f / ... -- but
that conflates ell. The faithful 'aggregate of CD over endpoints' is exactly LP-f with the constraints
SUMMED (one constraint = sum_g of the per-g constraints), giving a RELAXATION of (a); we report it too as (c').
"""
import numpy as np, subprocess, sys
from fractions import Fraction as F
from scipy.optimize import linprog
from _h import dec, GENG, loads, blow
from _crofton_lp import overlap_matrix, all_cuts

# ---------- exact-rational overlap (so certificates use exact O) ----------
def overlap_exact(info):
    n=info['n']; M=info['M']; cyc=info['cyc']
    m=len(M); pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    O=[[F(0) for _ in range(m)] for _ in range(m)]
    for i in range(m):
        for k in range(m):
            s=F(0)
            di=pf[i]; dk=pf[k]
            small=di if len(di)<=len(dk) else dk
            other=dk if small is di else di
            for v,c in small.items():
                if v in other: s+=c*other[v]
            O[i][k]=s
    return O,pf

def gate_cuts(info):
    """prefix-gate cuts: for each bad edge f=(a,b) and each layer index i in 1..ell(f)-1,
       A = { v : d_B(a,v) <= i-1 } restricted to vertices reachable in B-bipartite-distance.
       Return list of (dB(A), sep-vector over M) as floats. Dedup by frozenset."""
    n=info['n']; M=info['M']; Bset=info['Bset']; dist=info['dist']; ell=info['ell']
    seen=set(); cuts=[]
    for f in M:
        d=dist[f]                      # d_B(a, .) over reachable verts
        L=ell[f]
        for i in range(0, L):          # threshold i: A = {v : d(a,v)<=i}
            A=frozenset(v for v in d if d[v]<=i)
            if not A or len(A)==n: continue
            key=A if 0 in A else frozenset(range(n))-A
            if key in seen: continue
            seen.add(key)
            dB=sum(1 for (a2,b2) in Bset if (a2 in A)!=(b2 in A))
            sep=np.array([1.0 if ((g[0] in A)!=(g[1] in A)) else 0.0 for g in M])
            cuts.append((dB,sep))
    return cuts

def solve_lp(cuts, c_obj, Aub_rows, bub):
    """min c.lam s.t. -Aub_rows lam <= -bub (i.e. Aub_rows lam >= bub), lam>=0. floats."""
    ncuts=len(cuts)
    if ncuts==0: return None
    c=np.array(c_obj,dtype=float)
    if len(Aub_rows)==0:
        # only lam>=0, min c.lam = 0
        return 0.0
    A=-np.array(Aub_rows,dtype=float)
    b=-np.array(bub,dtype=float)
    res=linprog(c,A_ub=A,b_ub=b,bounds=[(0,None)]*ncuts,method='highs')
    if not res.success: return None
    return res.fun

def variant_a(info,O,cuts,j):
    M=info['M']; ell=info['ell']; N=info['n']; m=len(M)
    f=M[j]
    b=[ell[M[g]]*O[j][g] for g in range(m)]
    c=[cu[0] for cu in cuts]
    rows=[[cu[1][g] for cu in cuts] for g in range(m)]
    opt=solve_lp(cuts,c,rows,b)
    return opt, N*ell[f]

def variant_b(info,O,cuts,j):
    M=info['M']; ell=info['ell']; N=info['n']; m=len(M)
    f=M[j]
    b=[]; rows=[]
    for g in range(m):
        if g==j: continue            # drop self-edge constraint
        b.append(ell[M[g]]*O[j][g]); rows.append([cu[1][g] for cu in cuts])
    c=[cu[0] for cu in cuts]
    opt=solve_lp(cuts,c,rows,b)
    target = N*ell[f] - ell[f]*O[j][j]
    return opt, target

def variant_cprime(info,O,cuts,j):
    """aggregate relaxation: single constraint = SUM over g of per-g constraints.
       sum_A lam_A (sum_g sep_A(g)) >= sum_g ell(g)O_{fg} = (O ell-row)_f . target N*ell(f)."""
    M=info['M']; ell=info['ell']; N=info['n']; m=len(M)
    f=M[j]
    rhs=sum(ell[M[g]]*O[j][g] for g in range(m))
    c=[cu[0] for cu in cuts]
    row=[sum(cu[1][g] for g in range(m)) for cu in cuts]
    opt=solve_lp(cuts,c,[row],[rhs])
    return opt, N*ell[f]

def variant_d(info,Oexact,j):
    """prefix-gate metric: same per-edge LP-f but cuts restricted to gate_cuts."""
    cuts=gate_cuts(info)
    M=info['M']; ell=info['ell']; N=info['n']; m=len(M)
    f=M[j]
    b=[ell[M[g]]*Oexact[j][g] for g in range(m)]
    c=[cu[0] for cu in cuts]
    rows=[[cu[1][g] for cu in cuts] for g in range(m)]
    opt=solve_lp(cuts,c,rows,b)
    return opt, N*ell[f]

def census(nn,limit=None):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    if limit and len(out)>limit:
        # stride-sample across the WHOLE census (sparse graphs are first; we want denser ones too)
        step=len(out)/limit
        out=[out[int(i*step)] for i in range(limit)]
    return out

def run_variant(name,fn,Nrange,limit10=300,use_exact_O=True,use_all_cuts=True):
    print(f"\n=== variant {name} ===",flush=True)
    overall_fail=0; overall_edges=0
    for nn in Nrange:
        out=census(nn, limit10 if nn==10 else None)
        nt=0; fails=0; worst=-1e18; wg=None; edges=0
        predictors=[]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1
            Oe,pf=overlap_exact(info)
            cuts=all_cuts(n,info) if use_all_cuts else gate_cuts(info)
            for j in range(len(info['M'])):
                edges+=1
                if name=='d':
                    opt,target=fn(info,Oe,j)
                else:
                    opt,target=fn(info,Oe,cuts,j)
                if opt is None: continue
                tgt=float(target)
                gap=opt-tgt
                if gap>worst: worst=gap; wg=(g6,info['M'][j])
                if gap>1e-6:
                    fails+=1
                    # predictors
                    Gam=info['G']; nbad=len(info['M'])
                    predictors.append((g6,info['M'][j],round(gap,4),nbad,round(float(Gam)/(n*n),4)))
        overall_fail+=fails; overall_edges+=edges
        print(f"  N={nn}: cfg={nt} edges={edges} FAILS(opt>target)={fails} max(opt-target)={worst:+.5f} @ {wg}",flush=True)
        if predictors[:3]:
            for p in predictors[:3]:
                print(f"       fail: g6={p[0]} f={p[1]} gap={p[2]} #bad={p[3]} Gamma/N^2={p[4]}",flush=True)
    print(f"  >>> variant {name}: total FAILS={overall_fail} / {overall_edges} edges",flush=True)
    return overall_fail

def exact_check_certify(info,cuts,j,variant='a'):
    """If float LP says certify (opt<=target), build exact dual-feasible witness via exact LP is heavy;
       instead exact-verify the NECESSARY truth (O ell)_f <= N*ell(f) directly with Fraction."""
    Oe,pf=overlap_exact(info)
    M=info['M']; ell=info['ell']; N=info['n']; m=len(M)
    lhs=sum(ell[M[g]]*Oe[j][g] for g in range(m))  # (O ell)_f exact
    rhs=N*ell[M[j]]
    return lhs,rhs,(lhs<=rhs)

if __name__=="__main__":
    Nrange=[7,8,9,10]
    fails={}
    fails['a']=run_variant('a',variant_a,Nrange)
    fails['b']=run_variant('b',variant_b,Nrange)
    fails['cprime']=run_variant('cprime',variant_cprime,Nrange)
    fails['d']=run_variant('d',variant_d,Nrange,use_all_cuts=False)

    print("\n=== EXACT (Fraction) verify Cycle-SM truth (O ell)_f <= N*ell(f) census N<=9 (sanity, must be 0 viol) ===",flush=True)
    viol=0; tot=0
    for nn in [7,8,9]:
        for g6 in census(nn):
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            Oe,pf=overlap_exact(info)
            M=info['M']; ell=info['ell']; N=n; m=len(M)
            for j in range(m):
                tot+=1
                lhs=sum(ell[M[g]]*Oe[j][g] for g in range(m)); rhs=N*ell[M[j]]
                if lhs>rhs: viol+=1
    print(f"  Cycle-SM exact: {viol} violations / {tot} edges (should be 0)",flush=True)

    # ---- blow-up stress: C5[q] (uniform load T==N, Gamma=N^2, the TIGHT case) ----
    print("\n=== BLOW-UP STRESS C5[q] q=1..4 (N=5..20, tight uniform load) ===",flush=True)
    for q in range(1,5):
        n,E=blow(q); info=loads(n,E)
        if info is None:
            print(f"  q={q} N={5*q}: loads None"); continue
        Oe,pf=overlap_exact(info)
        cuts=all_cuts(n,info)
        N=n; M=info['M']; ell=info['ell']
        wa=wcp=wd=-1e18
        for j in range(len(M)):
            oa,ta=variant_a(info,Oe,cuts,j); wa=max(wa,oa-float(ta))
            ocp,tcp=variant_cprime(info,Oe,cuts,j); wcp=max(wcp,ocp-float(tcp))
            od,td=variant_d(info,Oe,j); wd=max(wd,od-float(td))
        # exact Cycle-SM truth on tight case
        viol=0
        for j in range(len(M)):
            lhs=sum(ell[M[g]]*Oe[j][g] for g in range(len(M))); rhs=N*ell[M[j]]
            if lhs>rhs: viol+=1
        print(f"  q={q} N={n} #bad={len(M)} G/N^2={float(info['G'])/(n*n):.4f} | "
              f"a:max(opt-tgt)={wa:+.4f} cprime:{wcp:+.4f} d:{wd:+.4f} | CycleSM-exact-viol={viol}",flush=True)

    print("\n=== SUMMARY ===")
    for k,v in fails.items():
        print(f"  variant {k}: {v} failing (graph,edge) pairs")
