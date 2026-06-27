"""Audit the SOUNDNESS DIRECTION: U_8(W) must be an UPPER bound on d_mono(W) for real graphons.
d_mono = 2*beta/N^2, beta = edges - MaxCut. U8 = sum_R (selfloop + sum_offdiag - profileMaxCut).
The profile-MaxCut groups the 8 non-anchor vertices into PROFILE CLASSES then cuts the class graph.
A class-level cut is a SPECIAL (more constrained) cut => profileMaxCut <= true blowup MaxCut.
Therefore U8 = e - profileMaxCut >= e - trueMaxCut = beta-density => U8 >= d_mono.  <-- SOUND (over-estimates beta, never cuts a real graph off the <=2/25 wall incorrectly).
We test on every small tri-free graph: U_8(G) >= d_mono(G) must hold (margin >=0)."""
import flag_engine as fe
from u8_max_check import U8, dmono

worst=1e9; worstG=None; nbad=0
for nn in (5,6,7,8):
    gs=fe.enumerate_graphs(nn,triangle_free=True)
    for (k,A) in gs:
        u=float(U8(nn,A)); dm=dmono(nn,A); margin=u-dm
        if margin<worst: worst=margin; worstG=(nn,A)
        if margin< -1e-9: nbad+=1
    print(f"n={nn}: {len(gs)} graphs scanned, running worst (U8 - d_mono) margin = {worst:+.3e}",flush=True)
print(f"\nWORST margin U_8 - d_mono = {worst:+.6e}  (>=0 => U8 is a valid UPPER bound => SOUND)")
print(f"#graphs with U8 < d_mono (UNSOUND) = {nbad}")
