# C-alltie via DISCONNECTED-K-SELFCAP and induction on N

**Target.** (C-alltie) For a gamma-min connected-B max cut: if O={v:T(v)>N} is nonempty, T(z)=0, and z is
B-adjacent to v with T(v)=N, then Kcomp(v) meets O.

C-alltie follows from **O-K-CONNECTED**: *if O is nonempty, the positive-K support {v:T(v)>0} is a single
K-component.* (Then v,o both load-bearing lie in the one component.) O-K-CONNECTED follows from the
scale-invariant

> **(SELFCAP)** In any connected max cut whose positive-K support has ≥2 components, every positive-K
> component C satisfies T(v) ≤ |C| for all v∈C.

(Contrapositive: O≠∅ means some T(v)>N≥|C|, impossible if disconnected ⟹ support connected.)

## Proven foundational lemmas (rigorous, exact-verified 0-violation over census N≤11)

Let C be a positive-K component (K-component = connected component of {vw:K[v,w]>0}; equivalently the
union-find closure of all bad-edge geodesic vertex sets).

- **(L1) Bad edges never cross C.** A bad edge f=(a,b) has a,b∈supp(p_f) (geodesic endpoints), so a,b lie
  in the same K-component. PROVEN. (`_selfcap_rigor.py`: 0 crossings.)
- **(L2) Interior vertices of C have all neighbors in C.** Interior(C) = C-vertices with no B-neighbor
  outside C. Any neighbor w of v∈interior(C) is joined by a cut (B) or bad edge; bad would cross C (⊥L1),
  so it is a B-edge, hence inside C. PROVEN. (0 outside-neighbors.)
- **(STAB) Geodesics of V\C bad edges avoid C.** supp(p_g)⊆Kcomp(g)⊆V\C for g a V\C bad edge. PROVEN.
  (0 touches.)
- **(STAB-Γ) A boundary-frozen re-cut of C changes only Γ_C.** Flipping any subset of interior(C):
  by L2 only C-internal edges change; boundary B-edges (all preserved) stay cut; bad edges partition into
  V\C (unchanged) and C (per new cut). Global Γ = Γ_rest(unchanged) + Γ_C(new). Verified exactly
  (`_selfcap_stab_gamma.py`: 56 boundary-frozen re-cuts, 0 violations of Γ_new = Γ_rest + Γ_C(new)).
- **(L3, frozen-max)** The induced cut on C is a maximum cut of G[C] **subject to boundary-incident
  vertices frozen** (global maximality + L2). PROVEN. (`_selfcap_gap_pin.py`: frozen_lt_full_max=0.)
- **(L4, frozen-gamma-min)** The induced cut on C minimizes Γ_C among boundary-frozen connected-max
  re-cuts (global gamma-minimality + STAB-Γ). PROVEN.

## Structural facts (exact-verified, drive the induction)

- The induced cut on each positive-K component C **equals the full gamma-min connected max cut of G[C]**
  (`_selfcap_induced_gammamin.py`: 0 of 30 mismatch); equivalently the frozen→full gap is never active
  (`_selfcap_gap_pin.py`: gap_active=0, induced_ne_fullgammamin=0).
- The induced loads T|_C are exactly the loads of the sub-configuration (G[C], induced cut): geodesics stay
  inside C and G[C] is B-connected (verified).
- |C| ≥ 5 always; over census, SELFCAP is tight at the C5 extremizer (T≡5=|C|).
- DISCONNECTED-K-SELFCAP: 0 violations, full census N≤11 (N=10: 87 multi-K cuts; **N=11: 717**), all
  connected max cuts. O-K-CONNECTED on gamma-min cuts: 3052 O-nonempty cuts N≤11, 0 disconnected
  (`_selfcap_chain.py`).

## The induction and the EXACT residual gap

**Inductive scheme.** Strong induction on N. In a multi-K config every positive-K component C has |C|<N,
is triangle-free (subgraph), B-connected, and its induced cut carries loads = the sub-config's loads. **If**
the induced cut on C is a gamma-min connected max cut of G[C], the inductive hypothesis (the load bound
T(v)≤m for gamma-min cuts on m<N vertices) gives T(v)≤|C|, i.e. SELFCAP, hence O-K-CONNECTED, hence C-alltie.

**Residual gap (the single missing step).** Prove **induced cut = FULL gamma-min connected max cut of G[C]**
(equivalently frozen-gamma-min = full-gamma-min on G[C]). What is PROVEN is the *frozen* version (L4): the
induced cut is gamma-min among re-cuts that keep boundary-incident vertices fixed. The gap is the
**frozen→full** step: unfreezing the boundary-incident vertices of C.

Why standard tools stall here:
- The load bound T(v)≤N is FALSE for general connected max cuts (witness J??CB@_~?, N=11, T up to 15>11);
  it holds only for gamma-min cuts. So the induction genuinely needs the induced cut to be gamma-min on
  G[C], not merely some max cut.
- A local splice fails: replacing C's sides by a gamma-min cut σ of G[C] (either embedding) does not always
  preserve global maximality/B-connectivity, because the boundary B-edges pin the boundary-incident
  vertices (`_splice_test`: equal-Γ component cuts are sometimes non-splice-able). The dead-net deletion
  lever does not apply: in EVERY census multi-K case each component is directly B-adjacent to ANOTHER
  positive-K component (all_dead_boundary=0), so there is no isolating dead moat to switch; the components
  are mutually interlocked.
- Hence frozen→full is a genuine global-rigidity fact of the same odd-girth≥5 anti-concentration class as
  ROWSUM-O / NO-Q-ONLY, not a local count.

**Net.** C-alltie is reduced (with all reduction steps rigorously proven) to the scale-invariant, single
statement: *the global gamma-min max cut restricts to a gamma-min max cut on every positive-K component.*
This is cleaner than the earlier NO-Q-ONLY phrasing (it is scale-invariant and inducible on N), but the
residual frozen→full step remains the same irreducible global rigidity.

Files (problems/23/writeup): `_selfcap_rigor.py`, `_selfcap_stab_gamma.py`, `_selfcap_gap_pin.py`,
`_selfcap_induced_gammamin.py`, `_selfcap_chain.py`, `_codex_disconnected_selfcap_allmax.py`.
