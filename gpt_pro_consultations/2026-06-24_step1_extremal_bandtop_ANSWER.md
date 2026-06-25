# GPT Pro Answer — extremal high-p band-top: TWO routes (chat 6a3b8a74)

## ROUTE 1 (potential WHOLE-BAND closer, but CONDITIONAL): flag-SDP cert + blow-up + INTEGRALITY
A beta>=37 counterexample blown up (G[t]) has limiting mono-PAIR-density beta(G)/450 = 37/450 = 0.082222.
The order-9 flag-SDP certificate bounds d_mono <= 2/25 + delta (delta ~4.3e-5..6.07e-5) = 0.08006.
Since 0.08222 > 0.08006 — and beta is an INTEGER (36 + 450*delta = 36.03 < 37) — this forces **beta <= 36**.
=> closes idx101 AND the ENTIRE 112<=e<=143 window AT ONCE, no enumeration, no BCL.
KEY REFRAME: the delta>0 that made the SDP "fail" the ASYMPTOTIC conjecture (needs delta=0) is HARMLESS for
the FINITE a(30) because 450*delta < 1 and beta is integer.
**PROVISO (GPT's own, = the crux):** holds ONLY IF the SDP d_mono is the density of an ACTUAL cut (true beta),
not an SDP surrogate, AND the cert is unconditional over the band. ** Step-2's audit found the order-9 d_mono is a
PROFILE-CUT surrogate (deficit 0.089 vs true maxcut 0.0156 on x*), so this proviso is exactly what was NOT
established — likely the false-closure trap unless the cert is recomputed against the TRUE cut.** [3 prior false closures.]
Note: e=143 finite density 143/C(30,2)=0.3287>0.3197 but blow-up density 143/450=0.3178<0.3197, so BCL-high does NOT reach it (consistent).

## ROUTE 2/3 (SOUND, self-contained Step-1 combinatorial path — recommended):
(b) SMALLER EXACT ENCODING — "889 states is misleading". Band-top cells are TINY: total column-excess is only
   **7,6,5,4 for p=33,34,35,36** (degrees forced to 8..11; identities sum_{A∪B}(10-j_v-k_v)=48-p, sum_S(m_r-5)+sum_D(m_r-6)=40-p).
   Branch on the sorted column-excess partition + row-deficit multiset (far smaller than 889 multiplicity vars);
   sort states within A, within B, and D-columns to kill row-permutation symmetry.
   Cut hierarchy: factorized 15-row master -> all W=empty + singleton-W coupled-switch -> min-cut separate all 2048
   R-masks -> full 16384-core-mask separator only for survivors. Every step EXACT.
   **FLOW encoding:** U3(W=empty) family <=> a network (s->b cap 1+k_b, a->t cap 1+k_a, H-edges unit) has
   **min-cut >= 33** (integral flow value 33). For W={r}: terminal caps 1+k_v-2 z_vr, flow value 33+d_R(r)-l_r-m_r.
   12 flow blocks encode all 2^15 row flips without generating them.
(CS/PCN coupled cuts) joint Z (over A∪B) + W (over R) flip, stronger than R-only U3:
   delta_H(Z)+delta_R(W)-|Z|-delta_J(Z,W)-l(W) <= p-33 (CS). Specialized (PCN, I=N_{A∪B}(r), W={r}):
   sum_{j,k} max(j-k+1,0) v_rjk <= m_r + p - 33 - d_R(r) + l_r. (r in S: <= m_r+p-34; r in D: <= m_r+p-31.)
   GPT: "rigorous; NOT established that PCN alone closes p=33..36, but a genuine coupled dense-regime cut."

## Assessment (GPT): (a) stability MISALIGNED (e=143 density 0.159 not near C5-blowup 0.2; Clebsch is a local
obstruction not the extremizer) — not the attack. (b) the finite-gap transfer (route 1) is "the correct robustness
argument" IF its proviso holds. The exact-encoding + flow (route 2/3) is the sound, buildable closure.
