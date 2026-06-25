# Digest: GPT-5.5 Pro (FK) ROUND 2, 2026-06-12 (thread c/6a29bd3c, 21k chars)
Audited line by line. ALL Q1 steps verified by me (see checks below).

## Q1 — ZERO-BUDGET ACCOUNTING THEOREM  [AUDITED, rigorous]
Setting: minimal-shore hypotheses (Delta<=6, sum b=6, kappa(X)>=8 for proper
2<=|X|<=|V|-2), unfrozen full v, witness psi, pair {i,j}, k third colour.
Notation: p=|X_i|+|X_j|, q=|X_k|, B=B_k, c=#components of P=H[X_i u X_j],
r=#non-singletons, zeta=sum(kappa(C)-8) over non-singletons, h=q-c, e=e_ij.
- L1 (edge formula): e = 3(p-q)+B-4.                       [verified earlier 23/23]
- L2 (charge identity): sum_C kappa(C) = 6q+8-2B.          [verified earlier 23/23]
- L3 (surplus equation): 6c+2r+zeta = 6q+8-2B, i.e. 2r+zeta = 6h+8-2B.
  [MY CHECKS: singleton kappa=6 always; non-singleton C has 2<=|C|<=n-3 so
  kappa>=8 applies; kappa(C) EVEN since kappa(C)=6|C|-2e(C); consistent with my
  (S1) inequality, now an equation.]
- B=4: h>=0; h=0 <=> ALL-SINGLETON: forces p=q, e_ij=0, c=p=q; h>=1 => p>=q+1
  [via spanning-forest e>=p-c].
- B=5: h>=1; h=1 => exactly (two kappa=8 components) OR (one kappa=10).
- B=6: h>=1; h=1 => exactly one kappa=8 component.
- ALL-SINGLETON STRUCTURE: bipartite near-6-regular (X_i u X_j) vs X_k, sides
  q=q, b-split 2/4, cross edges 6q-6 <= q^2 => q>=5, |V(H)|=2q+1>=11.
  [checked: 6q-6 = 6p-(6-B)-4 with p=q,B=4 ✓]
Status: rigorous-informal, audit complete; computationally vacuous on current
data (no minimal-shore unfrozen instance exists yet) but identities pre-verified.

## Q2 — DCRL(M) rigidity lemma (conjectural, exact)
"No irreducible minimal-shore all-unfrozen graph exists": every H satisfying
minimal-shore + all-full-unfrozen contains a state-reducible piece P with <=M
vertices and augmented boundary <=8. Finite verification plan = Q3 programme.

## Q3 — BOUNDARY-PIECE CERTIFICATE FORMALISM  [implementable spec]
- Piece P=(V,E,S,a,b): stubs S anchored by a:S->V; d(x)+#stubs(x)+b(x)=6.
- kappa_P(Y)=|bd_E Y|+|S(Y)|+b(Y); cut profile mu_P(U)=min_Y(|bd Y|+b(Y)+|S(Y) xor U|)
  (needed so replacements preserve kappa>=8).
- Col(P) subset [3]^S: anchor-consistent boundary colourings extendable to P.
- Unf(P,v) subset [3]^{S\S_v} x [3]^{S_v}: deletion data (alpha on non-v stubs =
  anchor colours; eta on v-stubs = OUTSIDE endpoint colours) extendable to P-v
  with N(v)-counts exactly (2,2,2) counting eta.
- FrozenFlag(P): some full v with Unf(P,v) empty => v frozen in EVERY completion
  [SOUND: global witness restricts to Unf element ✓; not complete].
- Composition lemmas: colouring (inequality across glued edges); deletion-state
  (EQUALITY eta(s)=beta(t) across deleted-v stubs — the opposite endpoint colour
  feeds the (2,2,2) count) [proof sketch sound ✓].
- FK-simulation: same S; Col equal; same deficiency; ROBUSTLY INTERNALLY UNFROZEN
  (every compatible outside beta admits internal deletion witnesses); fewer
  vertices; optional mu-domination. Replacement lemma preserves: 3-colourability,
  deficiency, all-full-unfrozen, (with mu-dom) cut bounds [proof sketch sound ✓].
- Boundary size: 8 REQUIRED from the start (kappa=8 components with b=0 have
  ordinary boundary 8; a 6-table cannot see the charge-equality pieces).
- Implementation: bitsets over 3^8=6561 boundary assignments; state hash modulo
  stub permutations + colour permutations; search smaller FK-simulators;
  certificate = every irreducible piece has FrozenFlag or a smaller simulator.

## Errors found
None in Q1 (every step checked). Q3 proofs are sketch-level but structurally
sound; rigor to be established during implementation (the composition lemmas
are mechanical gluing arguments).

## Next
(1) implement piece enumerator + state tables (start M small, |S|<=8);
(2) validate FrozenFlag soundness computationally against n<=14 data
    (a piece cut out of a census graph: certified-frozen => actually frozen);
(3) hunt FK-simulator pairs among small pieces (does ANY reduction exist?);
(4) Lean-formalize Q1 zero-budget theorem (pure double counting — candidate for
    the next PR increment).
