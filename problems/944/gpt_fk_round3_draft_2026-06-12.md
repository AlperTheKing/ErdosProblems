> ########################################################################
> # WARNING (2026-06-12 17:20): DO NOT SEND THIS DRAFT AS-IS.
> # (FK) WAS REFUTED: H* = PG(2,5) incidence minus 3 disjoint edges has NO
> # frozen vertex (62/62 witnesses independently verified) while satisfying
> # connected/bipartite/Delta<=6/Sum b=6/|V|=62 and (empirically) kappa(X)>=10.
> # Q1/Q3 ask GPT to prove sub-goals of this now-refuted conjecture.
> # See PROOF_STATE.md 17:18 block. Round-3 must be REWRITTEN around the
> # counterexample + the ROBUST-(FK) reformulation (Col-compatibility).
> ########################################################################
# GPT-5.5 Pro (FK) ROUND 3 — DRAFT (send to thread c/6a29bd3c when browser available)
Status: drafted 2026-06-12 ~12:40 after the boundary-piece computational programme.

## New verified facts to report (all machine-verified, implementations double-checked
## by independent python brute force; soundness validated on full n<=13 census, 4.2M
## certificate firings, 0 violations)

F1 (FROZEN-PIECE THEOREM, b=0): every connected piece P with Delta<=6, kappa(P) :=
   6|P|-2e(P) = 8, |P| <= 11, that is 3-colourable, has FrozenFlag: a vertex v with
   Unf(P,v) = empty. Counts: m=8:3/3, 9:62/62, 10:1471/1471, 11:48525/48525.
   (Non-3-colourable pieces cannot occur in a 3-colourable host.)
   => an all-unfrozen graph contains NO kappa=8 cut piece on <=11 vertices.

F2 (BIPARTITE LOCKED CENSUS): bipartite kappa=8 pieces (the zero-budget component
   family) for m=11..18 (1, 10, 27, 234, 1051, 33232, 302409, 18663189 pieces):
   EVERY one has >= 8 locked vertices; min locked = 8 (unique m=12 piece), >=10
   for m=13..16, >=12 for m=17, >=10 for m=18. Lockedness of v is independent of
   stub/b designations at other vertices, and total deficiency is 6 < 8: so every
   kappa=8 bicolour component with <= 18 vertices contains a locked FULL vertex
   under EVERY deficiency assignment, in EVERY B_k regime (not only B_k>=4).
   => in a minimal-shore all-unfrozen H, every kappa=8 component of H[X_i u X_j]
   has >= 19 vertices. (m=19 ~ 1.2e9 pieces — past the brute-force frontier.)
   kappa=10 chain extended to m=17 (2,557,444 pieces, all >= 10 locked)
   => kappa=10 components are single edges or >= 18 vertices.

F3 (REPLACEMENT ROUTE DEAD AT SMALL M): the Col-state space is tiny (355 canonical
   tables across all 50,061 kappa=8 b=0 pieces m<=11; 59 cross-size state collisions,
   one state shared by 11,174 pieces across m=8..11) — BUT since every small piece has
   FrozenFlag, no small piece is robustly-internally-unfrozen, so no FK-simulation
   replacement target exists at M<=11. DCRL-by-replacement cannot work with small
   simulators; the live route is M-boundedness or direct large-piece locking.

F4 (large kappa=8 bipartite structure): sides near-balanced — parts (a,b) satisfy
   6a >= e = 3(a+b)-4 and symmetrically, so |a-b| <= 1 for all sizes; pieces are
   near-6-regular dense bipartite.

## Questions

Q1 (LARGE-PIECE LOCKING — the main gap G1): Prove or refute: every connected bipartite
   piece with Delta<=6, kappa=8, |P| >= 18 (near-balanced near-6-regular by F4) has
   >= 7 locked vertices (or even just >= 1 locked vertex among any prescribed set of
   full vertices avoiding <= 6 deficient ones). Computational evidence: min locked
   grows with m (8,10,10,11,10,12 for m=12..17). Candidate mechanisms: (i) density
   forces some vertex whose neighbourhood pair-degrees prevent (<=2,<=2,<=2) splits in
   ALL proper 3-colourings of P-v; (ii) in near-6-regular bipartite pieces, proper
   3-colourings of P-v are near-2-colourings (third colour confined to low-degree
   slack), making the (2,2,2) condition at a degree-6 vertex unreachable; formalize.
   A proof here + F1/F2 closes G1 for all sizes; an explicit unlocked large piece
   would redirect the programme.

F5 (SMALL-COMPONENT MENU + kappa=10/12 censuses): kappa=10 bipartite pieces are a
   single edge (m=2; locked=0 — NOT frozen, the live small structure) or m >= 10;
   censused m=10..16 (1+3+20+105+924+7331+181326 pieces): ALL have >= 8 locked
   vertices => dead under every deficiency assignment. kappa=8 has NO small member
   (bipartite starts m=11). kappa=14 admits P3, kappa=16 admits C4/K_{1,3}, etc.
   GENERAL kappa=8 family (non-bipartite included) extended to m=12: 119.7M
   candidates, 2,055,237 3-colourable, ALL FrozenFlag.
   kappa=12 family censused m=10..16 (839,313 pieces): all >= 8 locked EXCEPT
   exactly TWO pieces below the universal threshold 7: g6 I??F~z{~? (m=10,
   locked=4, lset={6,7,8,9}) and K??FfRc~Fw^_ (m=12, locked=6); these die unless
   B_k <= 2 AND the deficiency sits exactly on their locked vertices.
   => in a minimal-shore all-unfrozen H, every witness-partition non-singleton
   component is a SINGLE EDGE (budget cost 2+zeta = 4), or one of the TWO
   explicit kappa=12 exceptional shapes above (only in B_k<=2 stacked-deficiency
   configurations), or has >= 17 vertices (kappa=8: >= 18; kappa=10: >= 17;
   kappa=12: >= 17), or kappa >= 14 sparse-small (P3, C4, ... — zeta >= 6 each).

Q2 (kappa>=10-ONLY CONFIGURATIONS — gap G2 + pair freedom G4): zero-budget gives
   2r + zeta = 6h + 8 - 2B_k per choice of unfrozen v and pair {i,j}. Characterize
   when ALL THREE pair choices at ALL unfrozen v yield only components with
   kappa >= 10 (zeta >= 2r) or singletons. Can the freedom (3 pairs per v, all v
   unfrozen, plus B_1+B_2+B_3 = 6 forcing some B_k >= 2) force, at SOME (v,{i,j}),
   either a kappa=8 component or the all-singleton extreme? If yes, (FK) reduces to
   Q1 + Q3. If no, we extend the piece programme to kappa=10 (family starts at
   m=10 with K_{5,5}; we can enumerate and locked-census it the same way — say if
   this is the right next compute).

Q3 (ALL-SINGLETON EXTREME — gap G3): B_k=4, e_ij=0: X_i u X_j and X_k both
   independent => H - v bipartite with parts of equal size q >= 5, |V| = 2q+1 >= 11,
   near-6-regular, cross-edge count 6q-6. v's witness needs (2,2,2) on N(v) with
   N(v) split 4 (IJ side) + 2 (K side). But EVERY full vertex of H is unfrozen by
   assumption — derive a contradiction from the bipartite-minus-v structure (e.g.
   deleting a K-side full vertex w: H-w remains bipartite + v; a (2,2,2) witness at w
   needs the third colour, forced onto v's side...). Please give the sharpest
   argument or counter-shape.
   NEW COMPUTATIONAL FACT (allsingleton_search.cpp): the candidate shape is finitely
   enumerable per q — cross-graph = connected balanced bipartite, Delta<=6, 6q-6
   edges (connectivity FORCED: two components would need kappa-sum >= 16 > 12 by
   minimal-shore), apex v -> 4+2 deficient vertices. Exhaustive for q=5,6,7
   (|V| <= 15; 100 + 1695 + 83937 apexings): ZERO all-unfrozen survivors. q=8 run
   (|V| <= 15; 100 + 1695 + 83937 apexings) and q=8 (799,846 cross-graphs,
   29,084,215 apexings): ZERO all-unfrozen survivors. So G3 is computationally
   dead through |V| <= 17; we need the argument for general q. NOTE (proved by
   hand, do not look for a kill at v): the apex v is ALWAYS unfrozen in this
   shape — colour all of B with the third colour and split v's four A-neighbours
   2/2 between the other two colours; proper since A only meets B, and counts are
   (2,2,2). SPARSE-REGIME EXTENSION (g3_random.cpp/g3_counts.cpp/g3_sparse64.cpp,
   random sparse candidates via circulant-minus-matching + MCMC edge swaps;
   deficiency patterns 1^6 AND general): q=10/12/15 x 5000, q=20 x 10k,
   q=25 x 100k samples ALL have a frozen full vertex (refutation trees tiny at
   q<=15; caps negligible at q<=25). Adversarial hill-climb minimizing #frozen:
   q=12 floor 6 (4.5M moves), q=15 floor 5 (1.6M moves, never below 5).
   HONEST GAP: q=30 sampling 98% inconclusive (5e8-node cap; |V|=61 exceeds the
   backtracker); the 1,416 decided samples were all frozen, 0 candidates. ACHIEVABILITY LAW
   (which N(x) count-multisets occur over proper colourings of H-x, full
   cross-vertex x, 300 samples): multisets with an absent colour {600},{510},
   {420},{330} ~always achievable; {411} sometimes (19-75%, rising with q);
   {321} rare (6-32%); {222} almost never (0/300 at q=12; 1-2/300 at q=15) —
   while apex v achieves {222} ALWAYS. So colourings are rigid near-2-colourings
   whose minority deviations cannot balance on a neighbourhood. CAUTION: the
   per-vertex {222} rate RISES with q — individual unfrozen cross-vertices exist
   in the sparse regime; only the all-vertices conjunction fails. A hill-climb
   minimizing #frozen at q=15 is queued (reaching 0 would REFUTE (FK)).
   The theory request: formalize the near-2-colouring rigidity + deviation
   non-concentration as the general-q freezing lemma, OR predict the designed
   counterexample the hill-climb should find. Kill-location stats
   (first frozen vertex, q=7, 83,937 apexings, all killed): v: 0 (consistent),
   4-side adj-to-v: 8,886; 4-side non-adj: 20,259; 2-side (K) adj-to-v: 6,286;
   2-side (K) non-adj: 48,506 — the dominant frozen vertex is a FULL K-SIDE
   vertex not adjacent to v (58%). q=8 (29,084,215 apexings): identical profile
   (v: 0; K-side non-adj 16,516,950 = 57%) — the mechanism is q-stable. The general-q mechanism to formalize: a witness
   at a full B-vertex w needs two N(w)-vertices (in A) coloured with B's colour,
   whose entire B-neighbourhoods must then avoid it — a cascade that the 6q-6
   edge density should make unsatisfiable. Please give the sharpest cascade/
   counting argument.

## Context unchanged
Minimal-shore hypotheses, zero-budget theorem (audited round 2), Unf/Col/FrozenFlag
formalism as specified in round 2 (implementation now validated). Lean port of
zero-budget L1/L2 in progress. Goal: (FK) for all shore sizes => Theorem B complete
=> every 6-edge-cut is a vertex star => star-cut endgame for Problem 5.2.

## ADDENDUM (2026-06-12 ~15:56, add to Q2 before sending) — pair-sum squeeze PC1/PC2
New verified facts strengthening Q2 (derivation: g4_pairsum_note_2026-06-12.md;
numerically verified on the FULL n=12 and n=13 6-regular stocks, 73,392 witnesses,
0 violations, pc_check.cpp):
PC1: it is IMPOSSIBLE (n<=4 contradiction) that all components of all three
  pair-graphs have <=2 vertices: per-pair 11q_k >= 5n-13+2b_k summed over k.
  So at every unfrozen v, every witness owns a >=3-vertex component in some pair.
PC2: 11q_k+5W_k >= 5n-13+2b_k+8R_k per k; summed: sum W_k >= (4n-16)/5+(8/5)sum R_k
  — a linear-in-n vertex mass in >=3-vertex components.
CAVEAT for the menu in F5: "edges or BIG" is incomplete — kappa>=14 small/medium
  components (e<=3m-7; e.g. K_{4,5} m=9 kappa=14, K_{4,4} m=8 kappa=16, all
  m=10..17 e=3m-7 shapes) are live and uncensused. We can locked-census
  kappa=14/16 for m<=14 cheaply. UPDATED Q2: given PC1/PC2, if the kappa=14/16
  small-medium families also die by locked-census, >=3-vertex components are
  forced BIG (>=17) at every unfrozen vertex — does that close G2 (kappa>=10-only
  configurations), e.g. by vertex-mass accounting against sum W_k >= (4n-16)/5?

## ADDENDUM 2 (2026-06-12 ~16:55, REFRAMES Q1 — read before answering) — intrinsic
## large-piece death is REFUTED in both directions; death must be a JOINT argument
New machine-verified facts (kappa8_free_hunt.cpp, hl_check.cpp, verify_pg_witness.py):
(a) kappa=14/16/18/20 bipartite locked-censuses (m<=13) ran: menu does NOT collapse;
    free (locked=0) pieces exist: P3, C4, K_{2,3}, K_{3,3}, K_{3,4}, K_{4,4},
    and kappa=20 shapes up to m=10. Empirical pattern "free => e<=2m" (|C|<=kappa/2)
    suggested itself — and is FALSE in general:
(b) HL refutation: 2xK44 + 1 bridge (m=16, e=33=2m+1, kappa=30) is free; the
    2-bridge variant (e=34, kappa=28) is free AND 2-connected (kills per-block
    restatements); 3-chain m=24 e=50 free. Mechanism: a bridge endpoint whose only
    cross-neighbour is the deleted v becomes colour-free. Saturating bridges
    (2-regular bridge set, kappa=16) locks exactly the bridge endpoints.
(c) kappa=8 law does NOT extend: the PG(2,5) incidence graph (m=62, 6-regular
    bipartite, girth 6) has ALL 62 vertices unlockable (witness independently
    verified, trace exactly (2,2,2)); PG minus 4 edges is a FREE kappa=8 piece
    (e=182=3m-4, all 62 vertices re-tested directly). So "every kappa=8 piece is
    frozen" is a small-m phenomenon (true exhaustively m<=18); minimal free
    kappa=8 piece size is in [19,62]. Locking correlates with SMALL girth-induced
    rigidity, not size: K66, Q6 (m=64), circulants C20/C24/C32(1,3,5), and all
    random 6-reg m<=36 lock at every vertex; girth-6 PG(2,5) is fully free.
(d) Budget coupling (via L2): a pair-graph consisting of ONE kappa=8 component
    forces 6q_k=2b_k<=12 => q_k<=2. Large free pieces are throttled by the global
    budget identity, not by intrinsic locking.
REFRAMED Q1: given (a)-(d), the death of large-piece configurations must come from
the JOINT system: budget identity Sum kappa(C)=6q_k+8-2b_k + PC1/PC2 mass bounds +
small-m censuses + the q_k<=2 throttle. Concretely: can one show that a free
kappa=8 (or kappa<=20) component with m>=19 cannot coexist with the OTHER two
pair-graphs' constraints (their components also need kappa>=8 and carry the
complementary budget 6q_i+8-2b_i, while X_k<=2 starves the opposite class)?
A PG(2,5)-seeded explicit H would refute (FK) outright — alternatively, what
extra hypothesis from the minimal-shore embedding (near-6-regularity of H,
b(x) sum=6, kappa(X)>=8 for ALL proper X, not just pieces) kills the PG seed?
