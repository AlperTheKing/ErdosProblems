# Digest: GPT-5.5 Pro (FK) reply, 2026-06-12 (thread c/6a29bd3c)
Audited line by line; verification status per item.

## Verdict (GPT, honest)
- NO proof of (FK); "plausible but currently unproved; missing ingredient is a
  deletion-colouring rigidity lemma". Route assessment: realistic all-size path =
  minimal-shore restriction + boundary-piece certificate induction.

## Item 1 — arithmetic signature of an unfrozen full vertex  [VERIFIED]
For H with Delta<=6, sum b = 6, unfrozen full v, witness psi (X_i, B_i, e_ij):
  e(H) = 3|V|-3;  e_ij + e_ik + 2 = 6|X_i| - B_i;
  e_ij = 3(|X_i|+|X_j|-|X_k|) + B_k - 4;  all B_i same parity.
CHECKED: hand-rederived (global sum gives e(H-v)=3n-9, consistent); deficiency-0
variant e_ij = 3(|X_i|+|X_j|-|X_k|) - 1 verified on ALL 23 real unfrozen instances
from the n=14 census (verify_charge_identity_reg.py: 23 instances, 0 fails);
deficiency-6 variant verified on random instance (verify_charge_identity.py).

## Item 2 — component charge identity  [VERIFIED]
kappa(C) = |bd_H C| + b(C); singleton kappa = 6 always;
  sum_{C in comps H[X_i u X_j]} kappa(C) = 6|X_k| + 8 - 2 B_k    (deficiency 6)
  (deficiency-0 variant: = 6|X_k| + 2; verified on the same 23 instances).
Under "augmented internally super-6-ec" (kappa(X)>=8 for proper 2<=|X|<=n-2):
  c_ij <= |X_k| + 1; non-singleton components cost 2 surplus units from budget
  8 - 2B_k; B_k >= 4 => budget <= 0 (extremely restrictive).  [algebra checked]

## Item 3 — NEW cheap necessary filter  [VERIFIED on 23/23]
v unfrozen => complement of H[N(v)] contains a perfect matching (3 same-colour
nonedge pairs). Cheap pre-[K] search filter.

## Item 4 — minimal-shore kappa>=8 lemma  [rigorous-informal, ACCEPTED]
If H is a MINIMAL nontrivial 6-shore, then |bd_H X| + b(X) >= 8 for all proper X
with 2<=|X|<=|V|-2 (a 6-value would be a smaller nontrivial 6-shore; 7 excluded
by parity of cuts in 6-regular G). Restricting (FK) to minimal shores is ENOUGH
for the #944 endgame (a counterexample target with a nontrivial 6-cut has a
minimal one).

## Item 5 — counterexample shape (for machine search a=15..18)
Filters in order: connected; Delta<=6; sum b=6; 3-colourable; (5) every full v:
complement N(v) has perfect matching; (6) every full v: H-v has a nonextendable
proper 3-colouring; (7) kappa(X)>=6 all X; (8) kappa(X)>=8 proper X (minimal).
GPT: dies at 5/6 => local proof likely; survives 5,6 but dies at [K] => the
obstruction is global extension. Shape: cells glued by colour-compatible 4/6-edge
interfaces (NOT 2-edge), deficiencies on outer boundary.

## Item 6 — finite certificate architecture C(a0)  [programme, not yet started]
Rooted boundary pieces (P, dP) with stubs, q(P) = b_P-total + |dP| = 6; finite
boundary state table (extendability per boundary colouring tau; per-vertex
(2,2,2)-extension; certified-frozen flag); certificate = irreducible pieces up to
a0 + reducibility proof + gluing lemma preserving 3-col/Delta/deficiency/
all-full-unfrozen. Then C(a0) + no irreducible counterexample <= a0 => FK all a.

## Errors found in GPT reply
None substantive this round (all checked claims passed). NOTE: our n=14 census
(maxUnfrozen=4) post-dates GPT's reply context; its "almost every vertex
unfrozen" shape requirement is consistent with the rarity data.

## Next concrete steps
(a) implement filters 5-6 as a fast searcher; hunt the shape at a=15..16 (random
    + structured cells), 32 workers;
(b) squeeze the charge lemma at B_k>=4 mathematically (budget<=0 case analysis);
(c) start the boundary-piece state-table enumerator (certificate programme);
(d) feed n=14 census data (fullyUnfrozen=0, max=4, the 7 graphs) to next round.
