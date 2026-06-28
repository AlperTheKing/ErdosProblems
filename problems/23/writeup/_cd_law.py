"""Confirm the structural failure law for LP-f (variant a):
   In the single-bad-edge case the LP-f optimum = (min separating-cut B-cost m_f) * ell(f) * ||p_f||^2,
   whereas the budget is N*ell(f). So LP-f FAILS  <=>  m_f * ||p_f||^2 > N.
   For C5 anchor: m_f>=2 always (need to cross the odd cycle twice). Predict & verify over census N<=9
   single-bad-edge graphs."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _crofton_lp import all_cuts
from _cd_cut_landscape import overlap_exact, variant_a

print("single-bad-edge graphs: verify LP-f opt == m_f*ell*||p_f||^2 and failure <=> m_f*||p_f||^2 > N")
tot=0; fails=0; lawok=0
for nn in [7,8,9]:
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None or len(info['M'])!=1: continue
        tot+=1
        Oe,pf=overlap_exact(info); cuts=all_cuts(n,info)
        M=info['M']; ell=info['ell']; N=n; f=M[0]
        Off=Oe[0][0]
        mf=min(dB for (dB,sep) in cuts if sep[0]>0.5)
        oa,ta=variant_a(info,Oe,cuts,0)
        predicted=mf*ell[f]*Off
        if abs(oa-float(predicted))<1e-6: lawok+=1
        lp_fails = oa>float(ta)+1e-6
        law_pred = (mf*Off > N)
        if lp_fails: fails+=1
        if lp_fails!=law_pred:
            print(f"  LAW MISMATCH g6={g6} f={f} mf={mf} Off={Off} N={N} lp_fails={lp_fails} law={law_pred}")
print(f"  single-bad-edge graphs N<=9: {tot}  LP-f-opt==m_f*ell*||p_f||^2 in {lawok}/{tot}  LP-fails={fails}")
print(f"  (law: LP-f fails <=> m_f*||p_f||^2 > N)")

# the 2-bad-edge small-gap N=9 case
print("\n--- H?q`qjo (2 bad edges, smallest variant-a gap) ---")
n,E=dec("H?q`qjo"); info=loads(n,E)
Oe,pf=overlap_exact(info); cuts=all_cuts(n,info)
M=info['M']; ell=info['ell']; N=n
print(f"  M={M} ell={ {f:ell[f] for f in M} }")
for j,f in enumerate(M):
    Oell=sum(ell[M[g]]*Oe[j][g] for g in range(len(M)))
    oa,ta=variant_a(info,Oe,cuts,j)
    print(f"  f={f}: (O ell)_f={Oell} N*ell={float(ta)} LPopt={oa:.4f} gap={oa-float(ta):+.4f} "
          f"O_row={[str(Oe[j][g]) for g in range(len(M))]}")
