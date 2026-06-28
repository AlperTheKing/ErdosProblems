"""LARGE non-uniform odd-cycle blow-up gate (quotient-level exact) for the SURVIVING target full-inverse cond3,
   and a map of where the dead diagonal surrogates (ROW-SUM, STAR-K-multi) fail. N up to ~1500.
   C_m[n_0..n_{m-1}] (m odd). gamma-min connected-B max cut leaves the MIN-PRODUCT edge (a,a+1) monochromatic
   (bad class V_a-V_{a+1}, ell=m, geodesic through all m parts). Quotient symmetry (g/loads constant per part):
     Pi(i) = nbad/n_i (intermediate), = n_{a+1} (part a), = n_a (part a+1);  nbad=n_a*n_{a+1};  T_i = m*Pi(i).
     full-inverse cond3 (closed form): every geodesic hits each part once => reduced A_QQ g: N g_i - Pi(i) S = N-T_i,
       S = A/(N-B), A=sum_{i in Q}(N-T_i), B=sum_{i in Q}Pi(i); O-row(p) = N - T_p + Pi(p)*S for each overloaded part p.
     ROW-SUM(p): sum_{q in Q} (per-vertex) K[o,q]R_q/(R_q+s_q) >= T_p-N, K[o in p][q in part j]=nbad/(n_p n_j)... (full).
     STAR-K-multi(p over its own part): handled by ROW-SUM margin = Z-row-sum (same as |O|=1 logic per part)."""
import random
from fractions import Fraction as F

def analyze(m, n):
    N=sum(n)
    # min-product edge
    prods=[(n[i]*n[(i+1)%m], i) for i in range(m)]
    pmin,a=min(prods); b=(a+1)%m
    nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad, n[i])          # intermediate
    T=[m*Pi(i) for i in range(m)]
    O=[i for i in range(m) if T[i]>N]
    if not O: return None
    Q=[i for i in range(m) if i not in O]
    A=sum(F(N)-T[i] for i in Q); B=sum(Pi(i) for i in Q)
    if N-B==0: return dict(degenerate=True)
    S=A/(F(N)-B)
    # full-inverse cond3: O-row per overloaded part
    cond3_ok=True; cond3_min=None
    for p in O:
        orow=F(N)-T[p]+Pi(p)*S
        if cond3_min is None or orow<cond3_min: cond3_min=orow
        if orow<0: cond3_ok=False
    # K[o in part p][q in part j] for the per-vertex ROW-SUM (o overloaded in part p):
    #   p intermediate, j intermediate: nbad/(n_p n_j); j=a: n_b/n_p; j=b: n_a/n_p; j=p(self, diff vtx): nbad/(n_p n_p)
    def Koq(p, j):
        # o in part p (intermediate, since overloaded parts are intermediate small-n_i); q in part j
        if j==a: return F(n[b], n[p])
        if j==b: return F(n[a], n[p])
        return F(nbad, n[p]*n[j])
    # ROW-SUM(p): o in part p; s_q = sum_{o' in O} K[o'][q] = sum_{p2 in O} n_{p2}? no: s_q=sum over O-VERTICES.
    #   For q in part j: s_q = sum_{p2 in O} n_{p2} * Koq(p2,j)  (n_{p2} vertices in overloaded part p2).
    rowsum_ok=True; stark_ok=True; rs_min=None
    for p in O:
        Do=T[p]-N
        lhs=F(0)
        for j in Q:
            Rq=F(N)-T[j]
            if Rq<=0: continue
            s_q=sum(n[p2]*Koq(p2,j) for p2 in O)
            Kpj=Koq(p,j)
            lhs += n[j]*Kpj*Rq/(Rq+s_q)
        marg=lhs-Do
        if rs_min is None or marg<rs_min: rs_min=marg
        if marg<0: rowsum_ok=False
        # STAR-K-multi on O-block: row-sum of Z for row p = N-T_p + sum_q K[p,q] s_q/(R_q+s_q)... = ROW-SUM margin
        # (Z is the O-block matrix; its row sums are exactly the ROW-SUM margins). Z PSD requires more, but
        # ROW-SUM fail => Z has a negative row sum => (for diagonally-structured Z) not diag-dominant; we report
        # STAR-K-multi as failing whenever any Z row-sum<0 (necessary cond for diag-dom PSD).
    stark_ok = rowsum_ok  # row-sum<0 => Z not diag-dominant (the regime we care about)
    return dict(N=N, O=len(O), cond3_ok=cond3_ok, cond3_min=cond3_min, rowsum_ok=rowsum_ok,
                rs_min=rs_min, m=m, a=a)

if __name__=="__main__":
    print("=== LARGE non-uniform odd-cycle blow-up gate: full-inverse cond3 vs dead surrogates ===",flush=True)
    # The GPT-Pro counterexample, as a sanity check:
    d=analyze(7,[3,423,173,7,176,7,423])
    print(f"  C7[3,423,173,7,176,7,423] N={d['N']}: cond3 {'HOLDS' if d['cond3_ok'] else 'FAILS'} (min {float(d['cond3_min']):.3f}); ROW-SUM/STAR-K-multi {'hold' if d['rowsum_ok'] else 'FAIL'} (min {float(d['rs_min']):.4f})",flush=True)
    rng=random.Random(20260628)
    for m in (5,7,9,11):
        c3fail=0; rsfail=0; tot=0; both_c3ok_rsfail=0; worst_c3=None
        for _ in range(40000):
            # extreme non-uniform: mix tiny and huge parts
            n=[rng.choice([1,2,3,5,7,10,20,50,100,200,400,800]) for _ in range(m)]
            if sum(n)>1600 or sum(n)<m: continue
            d=analyze(m,n)
            if d is None or d.get('degenerate'): continue
            tot+=1
            if not d['cond3_ok']:
                c3fail+=1
                if worst_c3 is None or d['cond3_min']<worst_c3: worst_c3=d['cond3_min']
            if not d['rowsum_ok']: rsfail+=1
            if d['cond3_ok'] and not d['rowsum_ok']: both_c3ok_rsfail+=1
        wc=f" worst-cond3={float(worst_c3):.3f}" if worst_c3 is not None else ""
        print(f"  C{m}: tested={tot}  cond3-FAILS={c3fail}{wc}  ROW-SUM/STAR-K-FAILS={rsfail}  (cond3-ok-but-surrogate-fails={both_c3ok_rsfail})",flush=True)
