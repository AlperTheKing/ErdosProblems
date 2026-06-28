"""Cleanest CD-cut insufficiency witness: F?o~_ (N=7, single bad edge).
Exact numbers + the structural reason endpoint-separation cuts cannot capture geodesic overlap."""
from fractions import Fraction as F
from _h import dec, loads
from _crofton_lp import all_cuts
from _cd_cut_landscape import overlap_exact, variant_a, gate_cuts

for g6 in ["F?o~_","H??F?~{"]:
    n,E=dec(g6); info=loads(n,E)
    Oe,pf=overlap_exact(info)
    M=info['M']; ell=info['ell']; N=n
    print(f"\n===== {g6}  N={n}  #bad={len(M)}  Gamma={info['G']}  Gamma/N^2={float(info['G'])/(n*n):.4f} =====")
    print(f"  bad edges M={M}  ell={ {f:ell[f] for f in M} }")
    for j,f in enumerate(M):
        Off=Oe[j][j]                       # ||p_f||^2 = <p_f,p_f>
        Oell=sum(ell[M[g]]*Oe[j][g] for g in range(len(M)))  # (O ell)_f
        target=N*ell[f]
        print(f"  f={f}: ||p_f||^2=O_ff={Off}  (O ell)_f={Oell}  N*ell(f)={target}  CycleSM-holds={Oell<=target}")
        print(f"       geodesic density p_f(v): { {v:pf[j][v] for v in sorted(pf[j])} }")
        cuts=all_cuts(n,info)
        oa,ta=variant_a(info,Oe,cuts,j)
        print(f"       LP-f opt={oa:.4f}  budget N*ell(f)={float(ta):.4f}  gap={oa-float(ta):+.4f}")
        # the SINGLE constraint that LP-f must satisfy (only g=f when #bad=1):
        # sum_A lam_A 1[A separates f] >= ell(f)*O_ff,  min sum_A lam_A dB(A).
        # cheapest cut separating f's endpoints has B-cost = (max-cut value contribution) -> compute min dB over separating cuts
        a,b=f
        best=None
        for (dB,sep) in cuts:
            # sep is over M; index of f is j
            if sep[j]>0.5:
                if best is None or dB<best: best=dB
        rhs=ell[f]*Off
        print(f"       min dB over cuts separating f = {best};  required RHS=ell(f)*O_ff={rhs}={float(rhs):.4f}")
        print(f"       => LP must buy lam so that lam*1 >= {float(rhs):.4f} on a cut of B-cost>= {best};"
              f" cheapest = {best}*{float(rhs):.4f} = {best*float(rhs):.4f}  (vs budget {float(ta):.4f})")
