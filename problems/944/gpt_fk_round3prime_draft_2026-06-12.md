# GPT-5.5 Pro (FK) ROUND 3′ — the interface dichotomy (REPLACES the banner-flagged round-3 draft)
(2026-06-12 evening. Thread: continue c/6a29bd3c. The old round-3 draft is OBSOLETE —
its Q1/Q3 asked you to prove sub-goals of (FK), which we have REFUTED. Everything
below is machine-verified unless marked otherwise; the round-2 formalism and the
zero-budget theorem stand unchanged and are assumed.)

## What happened since round 2 (one-day chain, all certificates on disk)
1. Bipartite locked-censuses extended to kappa in {14,16,18,20}, m<=13: free
   (locked=0) pieces exist (P3, C4, K_{2,3}, K_{3,3}, K_{3,4}, K_{4,4}, kappa=20
   shapes to m=10). The empirical law "free => e<=2m" (HL) and its per-block
   restatement are REFUTED: bridged 2xK44 graphs are free with e=2m+1 (kappa=30)
   and even 2-connected with e=2m+2 (kappa=28). Mechanism: a cross-neighbour whose
   only cross-edge goes to the deleted vertex becomes colour-free.
2. The kappa=8 census law ("every kappa=8 piece is FrozenFlag", exhaustive m<=18)
   does NOT extend: the PG(2,5) incidence graph (62 vtcs, 6-regular bipartite,
   girth 6) is unlockable at EVERY vertex; minus 4 edges it is a FREE kappa=8
   piece. Locking is small-girth rigidity, not size (K66, Q6, circulants
   C_{2k}(1,3,5), all random 6-regular bipartite m<=36: every vertex locked;
   m=40 randoms: first unlockable vertices appear).
3. ** (FK) IS REFUTED. ** H* := PG(2,5) incidence minus 3 vertex-disjoint edges
   (labels (0,32),(7,41),(15,33) in canonical F5^3 rep order): connected,
   bipartite, Delta<=6, Sum b = 6, |V| = 62, and NO vertex is frozen — all 62
   witness colourings independently re-verified. kappa(X)>=8 holds with slack
   (heuristic hunt min = 10; rigorous super-6-ec of PG incidence deferred).
   So "every connected 3-colourable Delta<=6 deficiency-6 graph >=9 vtcs has a
   frozen full vertex" is FALSE, and the per-shore freezing route to Theorem B
   (all shore sizes) cannot close as designed.
4. ROBUST freezing has teeth though. With anchors A = the six degree-5 vertices
   and gamma in [3]^6 the OUTSIDE stub-endpoint colours:
   served(gamma, v) := exists proper 3-col of H*-v, exactly (2,2,2) on N(v),
   anchor colours avoiding gamma componentwise.
   Result (MRV engine + OR-Tools CP-SAT cross-check, gapless): all 729 gamma are
   Col-compatible, BUT 864 canonical (gamma, v) pairs are STARVED. Structure:
   one gamma-family starves the SAME 16 line-side vertices, the dual family
   starves the same 15-16 point-side vertices.
5. SELF-PAIRING EXPERIMENT. Exact-trace tables on H*: Col (achievable anchor
   traces; |Col| = 480/729, S3-closed), UnfTrace(v) for all 56 full vertices,
   AnchorWit(a) for the 6 anchors (sizes 150/408/204/408/204/150). For
   G(pi) = two copies of H* + 6 cut edges over ALL 720 stub-matchings:
   * 720/720 pairings are 3-COLOURABLE => never 4-chromatic, never critical.
   * The best pairing serves ALL 124 vertices — the freezing screen alone would
     NOT have killed it; the chi=4 requirement did.

## The dichotomy (proposed corrected keystone)
For a 4-critical 6-regular G with a nontrivial 6-edge-cut (shores H, K, stub
matching pi), criticality forces BOTH:
 (a) NO avoiding pair: no tau in Col(H), gamma in Col(K) with
     tau_s != gamma_{pi(s)} for all six stubs s  [else G is 3-colourable]; and
 (b) servedness: every full vertex on each side has, for the partner-realizable
     traces, a matching witness [else that vertex is frozen in every completion
     colouring — the audited zero-budget freezing argument].
(a) wants the Col tables POOR/structured; (b) wants them RICH. H* fails (a)
against every partner including itself.

CONTEXT (literature gate done): Gallai–Toft 1970 covers separating edge sets of
size <= k in (k+1)-chromatic critical graphs (k=3 here: cuts of size <= 3, with
the one-colour / rainbow shore structure). Our regime |F| = 6 = 2k is NOT
covered by classical theory; it is exactly SkSt25's open Problem 5.2 territory.

## NEW (post-draft measurement): Avoid-COMPLETENESS — the sharpest form
Avoid(Col(H*)) = [3]^6 EXACTLY (729/729 coverage, machine-verified): every gamma
is componentwise-avoided by some tau in Col(H*). Since any shore of a 4-critical
graph is 3-colourable (proper subgraph), its Col is nonempty — so H* paired with
ANY partner under ANY matching yields a 3-colourable G. PROVED (machine):
H* is not a shore of any 4-critical 6-regular graph, full stop; excluded by
table-completeness, not freezing.

## Questions
Q1 (MAIN — prove or refute) CONJECTURE (D), the corrected keystone:
   for every minimal-shore H (connected, Delta<=6, Sum b=6, kappa(X)>=8,
   |V|>=15), EITHER (branch 1) some full vertex is frozen against every
   partner-realizable trace, OR (branch 2) Avoid(Col(H)) = [3]^6.
   Either branch kills a nontrivial 6-cut (branch 1 kills criticality at v,
   branch 2 kills chi=4), so (D) => Theorem B for ALL shore sizes => no
   4-critical 6-regular graph has a nontrivial 6-edge-cut. Evidence: every
   censused small piece is branch 1; H* is deep in branch 2 (|Col| = 480,
   full coverage). Suggested route: show everywhere-unfrozenness needs enough
   colouring flexibility (girth-6-like) that Col becomes avoidance-complete —
   classify S3-closed A subset [3]^6 with Avoid(A) != [3]^6 ("deficient
   tables": each uncovered gamma means A subset of the 665-set Clash(gamma))
   and show deficient Col forces a frozen vertex.
   (Counting note: Avoid(tau) has 2^6 = 64 elements; |A| >= 666 trivially
   forces full coverage; |Col(H*)| = 480 shows realizable tables can sit below
   the trivial threshold yet still cover — structure does the work.)
Q2: Is ANY extension of Gallai–Toft to separating sets of size in (k, 2k]
   known (especially k=3, |F| in {4,5,6}), or partial structure results for
   6-edge-cuts in 4-critical graphs beyond Dirac edge-connectivity? Cite.
Q3: The starved structure on H* (the same 16 line-side vertices across a whole
   gamma-family; point/line duality) suggests an invariant predicting Bad(v)
   directly from the PG geometry (e.g. v's incidence relation to the 3 deleted
   edges). Identify it — it should generalize to arbitrary shores and could
   make (b) checkable analytically rather than by search.

## Data available on request (all on disk, certificates verified)
Col(H*) as 480 traces (S3-closed, can ship orbit reps); UnfTrace tables;
starved families; fk_witnesses.txt (62 verified witnesses);
tools: kappa8_free_hunt.cpp, robust_fk2.cpp, pair_tables.cpp, CP-SAT scripts.

## Status guardrails (unchanged)
Theorems A+B as published (finite shore ranges; PR #4237; arXiv note) are
unaffected. Do NOT claim Problem 5.2 progress beyond: per-shore (FK) refuted +
interface dichotomy formulated + self-pairing excluded. Everything sent to you
will be audited line by line before acceptance.

## ADDENDUM (19:25) — (D) sweep data: 62 shores, ZERO refutation candidates
dichotomy_sweep.cpp, m=20..64, populations: random 6-reg bipartite -3e (36),
random balanced tripartite 6-reg -3e (20), circulants C_{2k}(1,3,5)-3e (4),
Q6-3e, PG(2,5)-3e. Per graph: lockedFull (branch 1) and Avoid(Col) coverage
(branch 2). RESULTS:
- ALL tripartite samples: |Col| = 6 EXACTLY (only the colour-permutations of the
  tripartition — proper 3-colouring is RIGID), Avoid coverage ~333-450/729
  (deficient), and EVERY full vertex locked (e.g. m=63: 57/57). Pure branch 1.
- ALL bipartite-family samples: |Col| in [96, 567] and Avoid = 729/729 WITHOUT
  EXCEPTION across all sizes. Branch 2 (mostly also branch 1).
- PG(2,5)-3e: the only everywhere-unfrozen sample; pure branch 2.
NEITHER count = 0. (D) survives a diverse falsification sweep.
OBSERVED MECHANISM: Avoid-deficiency <=> some gamma clashes with EVERY achievable
trace (global alignment of all proper 3-colourings with a fixed pattern) <=>
near-rigidity; rigidity visibly forces freezing (tripartite: traces are
(3,3,0)-shaped, never (2,2,2)). Suggested decomposition of Q1:
Q1e (easy half?): Col deficient (exists uncovered gamma) => some full vertex
   frozen. The tripartite data realize the extreme |Col| = 6 case; what is the
   weakest rigidity that still forces freezing?
Q1h (hard half): everywhere-unfrozen => Avoid-complete (PG is the only known
   everywhere-unfrozen example; its geometry gives flexibility AND coverage).

## ADDENDUM 2 (20:25) — (D) AS STATED IS REFUTED; ask (D-prime) + (R3) instead
PG(2,5)-star3 (delete 3 edges at one vertex y; profile (3,1,1,1), m=62) is a
machine-verified NEITHER instance: lockedFull = 0 (PG witnesses survive edge
deletion) and Avoid(Col) = 567/729 — the ceiling, since gammas rainbow on y''s 3
same-vertex stubs are unavoidable for EVERY graph (vertex y cannot avoid 3
banned colours). b<=2 stacking does NOT break avoid-completeness
(PG-P3+e profile (2,1,1,1,1): still 729/729). A 40-graph stacked-profile sweep
(incl. crafted 3x(b=2)+common-neighbour blockers) found no other NEITHER:
all small stacked instances are branch 1.
SO replace Q1 by:
Q1' (D-prime, pairing level): for every nontrivial 6-cut (H,K,pi) of a 4-critical
   6-regular graph: some full vertex on some side is frozen, or an avoiding
   Col-pair exists. The PG-star3 hole forces partner analysis: H''s unavoidable
   set is ONLY {162 rainbow-at-3-stubs gammas}, so a surviving partner needs
   Col(K) (restricted via pi) inside that rainbow set = every proper 3-colouring
   of K rainbow on 3 prescribed anchors.
Q1'a (R3): prove that a deficiency-6 shore K whose every proper 3-colouring is
   rainbow on 3 prescribed stub-anchors has a frozen full vertex. Note: the
   trivial rainbow-forcer (the 3 cut edges land on a triangle of K) gives
   K4 <= G, excluded since a 4-critical graph containing K4 is K4 (classical);
   so only Hajos/diamond-chain-type forcers remain — they are dense, odd-cycle
   rich, and kappa(X)>=8 + Delta<=6 constrain them severely.
Q1'b: prove spread/b<=2 bipartite shores are avoid-complete (empirical: 100%
   across all sweeps; the K33-minus-PM rainbow-anchor blocking pattern was
   repaired by hand in all cases — find the general repair argument).
NEW DATA: complete n=15 unfrozen census (1,470,293,676 graphs, all classes
validated): fullyUnfrozen = 0, max #unfrozen vertices = 5 (unique graph).
Freezing is universal at n=15; flexibility (PG world, m=62) needs size+girth.

## ADDENDUM 3 (21:05) — fair (R3) test: STRONGLY SUPPORTED
Diamond gadget (K4-free rainbow forcer: a,b,u,t diamond => psi(u)=psi(t); edges
u-v, v-w, t-w) attached to the FLEXIBLE PG(2,5) bulk via 17 distinct pads
(m=68, 128-bit engine, 4 randomized instances): ALL 4 are machine-verified
rainbow-rigid (|Col| = 84..150, every trace rainbow on the u,v,w stubs) and ALL
4 have 35-43 of 62 full vertices LOCKED — the gadget froze two thirds of the
previously everywhere-unfrozen PG bulk, while the gadget interior itself
(a, b, t) stays unlockable (deleting a gadget vertex breaks the diamond).
Mechanism: rainbow-forcing rigidity leaks through the pads and kills (2,2,2)
witnesses in the bulk. (R3) survived 6/6 falsification attempts incl. this fair
one. With Q1'b (100% across sweeps) the (D-prime) stack now rests on two
well-supported computational pillars + the b=3 case analysis. Please prioritize:
a proof of (R3) via the rigidity-leak mechanism (rainbow forcer => equality
gadget => pinned colours => witness death), and the general repair argument
for Q1'b.

## ADDENDUM 4 (22:05) — Q1'b RESOLVED by multi-agent proof attack: REFUTED as
## stated, SALVAGED LEMMA PROVED; (R3) is now the single load-bearing open piece
- Q1'b is FALSE: if the six anchors span a full cross-K_{3,3} with rainbow bans
  per side, unavoidability follows in four lines (cross-adjacency => the two
  anchor colour-sets are disjoint => one triple monochromatic => rainbow ban
  hit). Exact-count verified on explicit 18-vertex instances; a second family
  (K33 minus PM + common-neighbour blocker) also fails (the anchor system has
  exactly two solutions, both cyclic rainbow derangements).
- SALVAGED LEMMA (PROVED): under the Q1'b hypotheses (spread b<=1), avoidance
  holds for every gamma UNLESS the split is 3+3, both triples are rainbow-banned,
  and all six label-matching cross edges are present. In particular anchors
  pairwise non-adjacent => avoid-complete. (Parity: a_P = a_Q mod 6, so splits
  are 0+6 / 3+3 / 6+0; each anchor-anchor edge kills at most one of the six
  ordered base colourings.)
- PAIRING-LEVEL consequence: the fatal pattern is harmless for (D-prime) — a
  K33-anchored shore forces a monochromatic anchor triple in EVERY colouring, so
  its partner can always realize a non-fatal trace and an avoiding pair exists.
  All escape routes funnel into partner hyper-rigidity.
- => UPDATED ASK: (R3)-family is now THE load-bearing open conjecture:
  "a deficiency-6 shore whose every proper 3-colouring is rainbow on 3 prescribed
  stub-anchors (or: monochromatic/structured on prescribed anchor sets) has a
  frozen full vertex." 14/14 computational support incl. PG+diamond-gadget m=68
  (rigidity leaks through 17 pad edges and freezes 35-43 of 62 bulk vertices
  while the gadget interior stays unlockable). Please give the sharpest proof
  route for rigidity-leak => freezing under Delta<=6 + kappa(X)>=8.

## ADDENDUM 5 (22:48) — (R3) SCOPE CORRECTION (machine-verified)
Bare-TRIANGLE anchors (rainbow forced with zero rigidity leak) admit an
everywhere-unfrozen realization: triangle + PG(2,5) bulk, m=65, fixed-seed
instance 1: lockedFull = 0. So (R3) must be scoped to NON-triangle anchor
triples (at least one pair forced by an equality gadget rather than an edge).
The triangle case is harmless in deployment: anchors pairwise adjacent in K plus
their three cut edges into a single H-vertex y give K4 <= G, and a 4-critical
graph containing K4 is K4. CORRECTED (R3-prime): a deficiency-6 shore whose
every proper 3-colouring is rainbow on 3 prescribed anchors that do NOT form a
triangle has a frozen full vertex. All 14/14 supporting instances (2 edges + 1
diamond) are in scope. Note also (easy, provable): bipartite shores can never be
rainbow-rigid (the 2-colouring already makes two same-side anchors share, and a
triangle is non-bipartite), so (R3-prime) instances are inherently odd-cycle-rich.

## ADDENDUM 6 (23:15) — (R3-prime) ALSO REFUTED (K68, parity-pad rule); the ask
## changes one final time: criticality-locality is the load-bearing question
- K68: PG bulk + diamond gadget with PARITY-routed pads satisfies EVERYTHING
  (incl. min kappa = 8 exactly) and has ZERO frozen full vertices while being
  rainbow-rigid on its deficient non-triangle stub triple (multi-solver verified;
  artifacts r3c/). GQ(5,5)-bulk version K318: 0/312 frozen. The freezing pillar
  is dead for large parity-compatible bulks. Salvage kept: (R3-prime) is TRUE
  exhaustively for n <= 13 (1.87e9 graphs); forced-equal pairs never freeze
  (only forced classes hitting a neighbourhood 3 times do).
- COMBINATION: H = PG-star3 paired with K = K68 (y''s three stubs onto U,V,W)
  gives a 6-regular 130-vertex G with chi >= 4 and a nontrivial 6-cut, passing
  the freezing screen on BOTH sides. G is NOT 4-critical: the chi-certificate is
  CUT-LOCAL (rigid core + y), so chi(G-x) = 4 for every x far from the core.
- FINAL REFRAMED ASK (replaces all previous Q1 variants): in a 4-critical graph,
  chi(G-x) = 3 for EVERY x, so any non-3-colourability certificate must be
  destroyed by every single vertex deletion. Our G shows interface-blocking
  certificates can be local. QUESTION: prove that a nontrivial 6-cut in a
  4-critical 6-regular graph is impossible because any blocked interface
  (no compatible Col-pair under the matching) yields a certificate that some
  vertex deletion does NOT destroy — equivalently, quantify certificate locality:
  the rigidity needed to block all 729-table compatibility cannot be spread so
  that every vertex of BOTH shores participates in it (Delta<=6 budget;
  deficiency 6; kappa>=8). The round-2 Unf-table formalism is the right language:
  criticality says for every x the POST-DELETION tables admit a compatible
  (2,2,2)-pair; derive a contradiction from the conjunction over all x.

## ADDENDUM 7 (00:25, FINAL FORM OF THE QUESTION) — trace-hypo-rigidity
Constrained-stub experiment (all six stubs on the z-triple, b=2 each, parity
pads): 6/6 instances rainbow-rigid with |Col| = 6 (unique trace up to colour
permutation) and ZERO frozen full vertices. The freezing route is dead in every
stub profile. What remains is exact and criticality-shaped:
A 4-critical 6-regular G with a nontrivial 6-cut requires each shore to be
TRACE-HYPO-RIGID: the interface tables block compatibility (G not 3-colourable),
yet for EVERY vertex x the deleted shore''s tables admit a compatibility-restoring
trace with the (2,2,2) condition at the deleted vertex''s neighbourhood (G - x is
3-colourable with balanced trace). Our specimens (K68, K318, K-b2) all FAIL
hypo-rigidity: their rigidity lives in a bounded gadget core, so bulk deletions
keep the block. FINAL QUESTIONS:
Q-A: Does a trace-hypo-rigid deficiency-6 Delta<=6 shore exist at all? (NO =>
     Theorem B for all shore sizes => Problem 5.2''s 6-regular case loses all
     nontrivial 6-cuts. YES => counterexample seed.)
Q-B: Structure: rigidity cores are 4-critical quotients M with e(M) <= 3h-1
     (proved, workflow salvage). Hypo-rigidity needs the core to be destroyed by
     every deletion — i.e. the union of all cores covers K and each vertex lies
     in every core''s "support"? Make this precise and bound it against Delta<=6
     + deficiency 6 + kappa>=8. Note 4-critical graphs themselves are
     vertex-hypo-chromatic in exactly this sense — is there a transfer principle
     ("a shore of a critical graph inherits criticality of its forcing core")?
Q-C: The n<=13 exhaustive base (1.87e9 graphs: rainbow-rigid => >=2 frozen) plus
     smallest-counterexample bracket [14,67] — can the bracket be closed from
     below by structure rather than brute force?
