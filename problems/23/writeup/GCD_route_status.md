# ρ(K)≤N via K ⪯ diag(T)−L_ω ⪯ N·I — GREEN-CAPACITY DOMINATION

Status 2026-06-28. The δ=0 conjecture (every triangle-free G on N vertices: β=e−MaxCut ≤ N²/25)
reduces EXACTLY to SPEC: ρ(K) ≤ N, where K = PPᵀ, P[v,f]=p_f(v) geodesic-incidence, T=K·1 the load,
Σ_v T(v)=Γ. GPT-Pro's route (chat "Spectral Inequality Proof") sandwiches K between two PSD matrices.

## The two-sided sandwich
For a bad edge f=ab, ℓ=ℓ(f)=dist_B(a,b)+1 (odd, ≥5). Each shortest B-geodesic Q closed by f is a
simple odd ℓ-cycle C(f,Q) (distinct vertices, from shortest path). q_Q = its vertex-indicator.
CHORDLESS-CAVEAT (workflow wh4jnw0zb Angle-A catch): "a chord shortens the geodesic" excludes only
CROSS (B-edge) chords; a SAME-side (M-edge) chord does NOT change dist_B and can occur — but ONLY on
non-γ-min cuts (witness H?AFBo] non-min cut, same-side chord, ρ(K)=9.12>N). On γ-min cuts: 0 chords of
any kind (verified all gate). (LC) itself needs only that C(f,Q) is a simple ℓ-cycle (chord-independent:
L_{C(f,Q)} uses only the ℓ cycle edges), so the per-cycle bound holds regardless; chordlessness is a
γ-minimality property used elsewhere, not a prerequisite of (LC).
- p_f(v) = Pr_{Q∈P_f}(v ∈ C(f,Q));   τ_f(e) = Pr_{Q∈P_f}(e ∈ E(C(f,Q))),  τ_f(f)=1.
- Rational coefficient  ā_ℓ := ℓ³/(4(ℓ²−2))  (< sharp a*_ℓ = ℓ/(2+2cos(π/ℓ));  ā_ℓ > ℓ/4).
- ω(e) := Σ_{f∈M} ā_{ℓ(f)} τ_f(e);   L_ω = weighted Laplacian on B∪M.

**(LC) Local comparison — ELEMENTARY (PROVEN mechanism + exact-validated per edge).**
  Standalone proof note: LOCAL_CIRCULANT_PSD.md.
  K + L_ω ⪯ diag(T),  i.e.  M − K ⪰ 0  where M := diag(T) − L_ω.
Proof: circulant fact J_ℓ + a*_ℓ L_{C_ℓ} ⪯ ℓ·I_ℓ holds per cycle, EXACTLY at the sharp coeff
a*_ℓ=ℓ/(2+2cos(π/ℓ)): J_ℓ and L_{C_ℓ} are co-diagonalized by the Fourier basis; eigenvalues of
J+aL are ℓ (constant mode, tight) and a·2(1−cos(2πk/ℓ)) (k≠0), maximized at k=(ℓ±1)/2 giving
2a(1+cos(π/ℓ)) ≤ ℓ ⟺ a ≤ a*_ℓ. Restricted to the ℓ support coords I_ℓ=diag(q_Q), so
q_Q q_Qᵀ + a*_ℓ L_{C(f,Q)} ⪯ ℓ diag(q_Q). Take E_Q (Laplacian linear in edge weights ⟹
E[L_{C(f,Q)}]=L_{τ_f}): E[q qᵀ] + a*_ℓ L_{τ_f} ⪯ ℓ diag(p_f). Jensen p_f p_fᵀ ⪯ E[q qᵀ] and
ā_ℓ ≤ a*_ℓ give p_f p_fᵀ + ā_ℓ L_{τ_f} ⪯ ℓ diag(p_f). Sum over f, Σ_f ℓ diag(p_f)=diag(T). ∎

  Coefficient bound ā_ℓ ≤ a*_ℓ (ℓ≥5 odd), RIGOROUS: ā_ℓ ≤ a*_ℓ ⟺ cos(π/ℓ) ≤ (ℓ²−4)/ℓ²; since
  cos x ≤ 1−x²/2+x⁴/24 with x=π/ℓ, suffices π²/2 − π⁴/(24ℓ²) ≥ 4, and π²/2 − π⁴/(24·25) = 4.7725 ≥ 4. ∎
  EXACT per-bad-edge validation (`_lc_verify.py`): ℓ diag(p_f) − p_f p_fᵀ − ā_ℓ L_{τ_f} ⪰ 0 holds on
  EVERY bad edge — census N=7,8,9 all γ-min cuts (53+337+2421 bad edges), Mycielskians incl N=23,
  named N=8..11: 0 PSD failures. (Per-edge ⟹ summed M−K⪰0; this is the stronger point-of-use form.)

**(GCD) Green-capacity domination — THE ONE REMAINING LEMMA.**
  L_ω + diag(N − T) ⪰ 0,  i.e.  N·I − M ⪰ 0,  i.e.  L_ω ⪰ diag(T − N).
Equivalent Schur-capacity form (O={T>N}, Q=V\O, D_O=diag(T−N|O), R_Q=diag(N−T|Q)):
  (CAP)  L_{ω,OO} − L_{ω,OQ}(L_{ω,QQ}+R_Q)⁺L_{ω,QO} ⪰ D_O.
The ω-network must route the overload (T−N on O) through the deficit (N−T on Q). It is GLOBAL:
finite-depth Neumann of (L_{ω,QQ}+R_Q)⁺ is what the dead (k2) proxy truncated, hence its N=23 failure.

Together: N·I − K = (N·I − M) + (M − K) = [GCD] + [LC] ⪰ 0 ⟹ ρ(K) ≤ N ⟹ Γ≤N² ⟹ β≤N²/25.

## Exact-PSD gate (BOTH halves, 0 fails) — `_gcd.py`
| family | result |
|---|---|
| C5[t] extremal t=1,2,3 | tight, mineig 0, constant null mode (predicted) |
| Grötzsch N=11 / Myc(Grötzsch) N=23 | +1.46 / **+1.72 — survives the (k2) killer** |
| Myc(C7) N=15, named N=8..11 | PSD-exact |
| blow-ups to N=24 | +1.79 |
| **glued-island battery** (504 γ-min cuts) | **0 fails — survives the ZMU / O-K-SUPPORT killer** |
| census N=7..10 ALL γ-min cuts | 53+280+1916+16016 cuts, 0 fails |

Both batteries that killed every prior cond1/cond3 candidate are passed. Remaining work = a PROOF of (GCD).

## Next
Direct proof of (GCD)/(CAP): an explicit capacitary potential / flow on the ω-network certifying that the
effective conductance from O dominates D_O, using odd-girth≥5 (chordless cycles ⟹ no short-circuit). Consult
GPT-Pro for the construction; exact-verify any test before trusting. Codex's CAGE OT/Farkas machinery may
prove (CAP) directly (overload→deficit transport). Source: gpt_pro_consultations/2026-06-28_ROWSUMO_green-capacity_GPT.md.

## SYNTHESIS (5-angle workflow wh4jnw0zb, 10 agents + adversarial cross-check) -- 2026-06-28

THE SURVIVING CRUX (all angles converge): the **full-inverse-g superharmonic certificate** (pure-K, no L_omega):
  A = N*I - K, O={T>N}, Q={T<=N}, g := A_QQ^{-1}(N-T)_Q, phi=(1 on O, 1-g on Q).
  cond1: A_QQ=(N*I-K)_QQ nonsingular Stieltjes + 0<=g<=1  [well-posed / H_QQ PD].
  cond3: for all o in O,  N-T(o) + sum_{q in Q} K[o,q] g(q) >= 0   [K phi <= N phi on O; equality on Q].
EXACT 0-fail full gate (_opencap.py): census N=7..11 (7939 O-cuts @N11), glued battery (292 O-cuts), Myc N=23
(+6.56), named. This is Codex's Collatz-Wielandt supersolution with the FULL inverse (not a Neumann truncation).

COND1 CORRECTION (2026-06-28): the broad constant-load induction shortcut is FALSE. A pinned Wagner gadget
(`_codex_pinned_wagner_counter.py`) has a proper positive K/omega component C with T|C=25/2, |C|=8, so
lambda<=|C| fails; the induced cut on C is also not a maxcut (8 vs 10). The local scans missed it because it
has N=26 and geodesically idle pinning paths. What may still survive is the narrower saturated dangerous case:
proper C with T|C=N, O nonempty, and omega(C,O)=0. Do not claim cond1 from CONSTANT-LOAD-COMPONENT-BRIDGE or
SELFCAP as stated. cond3 remains the O-row inequality below.

WORKFLOW NEGATIVE RESULTS (all exact-verified, prune the search):
- SCALAR Hall/max-flow cut (overload(S)<=boundary-capacity for all S subset O) is PROVEN INSUFFICIENT for the
  matrix domination (abstract counterexample g=[0,2],c=1,d=[1,1]: all indicator cuts pass, Y_eff-D_O=[[0,-1],
  [-1,2]] indefinite). Off-diagonal energy-current term invisible to scalar cuts => no pure scalar transport/
  Hall proof of cond3 works. (On real census the scalar cut always holds -- necessary-not-sufficient.)
- PER-EDGE telescoping REFUTED circular: atoms A_f = a_bar L_{tau_f} - ell diag(p_f) are NSD full-rank; the
  only reservoir bound that closes it (sum p_f p_f^T <= N*I) IS SPEC. Confirmed exact.
- The CHEAP 2-step Neumann truncation phi2 = 1 - u_Q/N - K_QQ u_Q/N^2 DIES at N=23 (Myc2(C5) vertex 22, -0.723
  exact); only the FULL inverse g survives. (SCHUR_SPEC_PROOF_DRAFT.md's "exact tests support two-step" is FALSE
  at N=23 -- correct it.)
- Swapping a_bar(ell)->ell/4 in L_omega does NOT break PSD on census N<=9 + N=23 => odd-girth>=5 enters via
  ell>=5 / geodesic structure / the load T, NOT via the cycle-weight surplus a_bar>ell/4 (~0.05-0.11, not binding).

TOP TECHNIQUE (Angle E): M-matrix / Allegretto-Piepenbrink ground-state criterion -- H>=0 <=> exists phi>0 with
H phi>=0 (H is a connected Z-matrix). The canonical capacitary phi (=1 on O, phi_Q=(L_{omega,QQ}+R_Q)^{-1}
L_{omega,QO}1 in [0,1]) works exactly. Same object as the full-g certificate (K vs L_omega form) and the (CAP)
Schur form. CAUTION: this existence form is Perron-Frobenius-EQUIVALENT to SPEC; the narrowing is to prove the
SPECIFIC canonical phi superharmonic.

PROVABLE SUB-TARGET (Angle D, exact-certified, NON-circular): |O|=1 reduces to the LOCAL STAR INEQUALITY
  LB1(o) := sum_{w ~omega o, N-T(w)>0} omega(ow)(N-T(w))/(omega(ow)+(N-T(w)))  >=  T(o)-N,
since C_eff(o<->ground) >= LB1 (Rayleigh, proven) and (CAP)|_{|O|=1} <=> C_eff >= T(o)-N (exact identity).
0 fails / 6233 cuts (min ratio 1.05, tight witness Myc(C7) N=15 o=14). |O|=2 => 2-port det condition.
Next: prove the |O|=1 star inequality (per-bad-edge charging) / GPT-Pro. Files: _opencap.py, _clcb_audit.py,
_selfcap.py, _cap.py, _cond1_audit.py.

