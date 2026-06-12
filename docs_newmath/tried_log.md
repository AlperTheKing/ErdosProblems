# TRIED LOG — autonomous new-math loop over open Erdős problems

Mission (2026-06-09 user directive): find genuinely NEW math on open Erdős problems; fail fast; never
formalize/re-prove known results. One problem at a time. Verdict per problem: SUCCESS / UNAVAILABLE / STUCK.

---

## #19 — Erdős--Faber--Lovász / edge-disjoint complete graphs — UNAVAILABLE (2026-06-09)
- Novelty gate: local `_scan_problems.yaml` still listed this as decidable, but current erdosproblems search pages mark #19
  PROVED. The main EFL conjecture is covered by Kang--Kelly--Kühn--Methuku--Osthus, "A proof of the
  Erdős--Faber--Lovász conjecture", Annals of Mathematics 198 (2023), proving the large-n form and resolving the
  maintained problem status.
- Verdict: UNAVAILABLE for new-math mission; do not formalize/re-prove. Move on.

## #1082 — no-three-collinear sets and distinct distances — STUCK/PARTLY UNAVAILABLE (2026-06-10)
- Target: an n-point no-three-collinear set determines at least floor(n/2) distinct distances; stronger local version
  asks for a point seeing floor(n/2) distinct distances.
- Novelty gate: current erdosproblems keeps the global distance-count problem open, with Szemeredi's n/3 bound as
  the closest named general result. The stronger local version is already false/AI-raced (small Harborth-style
  examples and the later 42-point construction with every point seeing only 20 distances), so that route is
  unavailable for new math.
- Why STUCK: the remaining global problem is hard discrete geometry rather than a finite certificate target. No
  specific new structural idea held; do not recycle the local false variant as progress.

## #1041 — lemniscate/root path length bound — STUCK (2026-06-10)
- Target: prove the Erdős--Herzog--Piranian style claim that two roots of a monic polynomial can be joined inside
  the lemniscate by a path of length < 2.
- Novelty gate: the component/connectivity ingredients are known, while the sharp length bound remains open and
  is heavily AI-raced. Recent public proof attempts have serious gaps: gradient-flow/tree topology failures noted
  by Tao, and later subharmonicity-style gaps.
- Why STUCK: plausible routes require genuine complex-analytic/topological innovation, not a bounded finite check.
  No gate-passing complete proof strategy held.

## #23 — triangle-free graphs far from bipartite, exact a(25) — ACTIVE (2026-06-10)
- Target: prove the new finite exact value a(25)=25, where a(N)=max_G(e(G)-maxcut(G)) over triangle-free graphs
  on N vertices. Lower bound is the balanced C5 blow-up with five parts of size 5. OEIS A389646 currently lists
  values only through N=23; BCL gives a(N) <= N^2/23.5, hence only a(25) <= 26.
- Novelty gate: current exact-value target appears uncovered after checking erdosproblems #23 history, OEIS
  A389646, McKay data links, and Balogh--Clemen--Lidicky. BCL density intervals reduce any 25-vertex counterexample
  to 75 <= e <= 95.
- Current route: GPT-5.5 Pro suggested the stronger low-degree reduction. If G has 25 vertices, 75<=e<=95, and
  beta(G)=e-maxcut(G)>=26, then avg degree <=7.6 gives a vertex v with d<=7; for H=G-v,
  beta(H)>=26-floor(d/2)>=23 and 68<=e(H)<=95. Thus it suffices to certify no 24-vertex triangle-free graph
  with 68<=e<=95 and beta>=23. C++ lazy SAT/MaxCut campaign in `search23/` is in progress.

## #993 — independence-sequence unimodality of trees — UNAVAILABLE (2026-06-09)
- Target: unimodality of the independence polynomial of the hub-of-spiders family T_{m,t,1} (the cases
  m=2,3 we had a complete H_k≥0 + bridge proof for).
- Closest known results: Galvin (arXiv:2502.10654) introduced this exact family and its non-log-concavity;
  Li (arXiv:2603.03025, Mar 2026) covers the "unimodal-but-not-log-concave tree family" CATEGORY (the
  T_{3,m,n}/T*_{3,m,n} families) — i.e. the m=2,3 unimodality is PUBLISHED. Full #993 conjecture (all trees)
  is a famous hard open problem; the uniform-all-m hub-of-spiders sub-case is GPT-walled (slope-ratio
  S_k/T_k monotonicity; additive-concavity route proven FALSE; m≥10 (B*) thin-diagonal walled rounds 13–17).
- Why no new math: our m=2,3 proof re-proves a published theorem (Li/Galvin) → formalizing it is the
  prohibited consolation prize; no gate-passing new idea for the open uniform-m case.
- Artifact (PARKED, not a deliverable under this mission): `formal-conjectures/galvin_dom.lean` (993 lines,
  0 sorry, clean axioms) — complete m=2 H_k≥0, bridge B1, m=3 3-of-4 row bounds. Real verified Lean, but
  formalization of known results. Keep; do not pursue.

## #677 — repeated lcm of equal-length windows — STUCK (2026-06-09)
- Target: M(n,k)=lcm(n+1,…,n+k). Prove (or disprove) M(n,k)≠M(m,k) for all m≥n+k (lcm of a length-k window
  never recurs at a later DISJOINT window). [Er79][Er79d][ErGr80], number theory. erdosproblems.com: OPEN,
  "cannot be resolved with a finite computation."
- Closest known: Cambie [Ca24]=arXiv:2410.09138 RESOLVED the adjacent #678 (M(n,k)>M(m,k+1) i.o.), even
  Lean-verified — but NOT #677. No paper found resolving #677 (searched 2024–2026 lcm literature: also
  arXiv:2407.04226, 2512.20055 — unrelated to this exact question).
- Attempt (bounded): counterexample search k≤30, n≤30000 → 0 disjoint-window equalities. (Sanity: lcm
  VALUES do repeat 1514× for k≤30,n≤5000, but every repeat is within the gap m<n+k, i.e. overlapping
  windows — never a disjoint later window. Consistent with the conjecture being TRUE.) VERIFIED NUMERICALLY.
- Why STUCK: universal/infinitary statement (not finitely verifiable), believed true, no counterexample;
  the only finite NEW result would be a counterexample (none found, none expected); a proof is research-level
  analytic NT in an expert-actively-worked neighborhood (Cambie). No specific new idea held → fail fast.

---

## #1110 — representability by sums of p^k q^l (antichain) — STUCK (2026-06-09)
- Target [ErLe96]: p>q≥2 coprime, n "representable" = Σ of distinct p^k q^l forming an antichain under
  divisibility. For {p,q}≠{2,3}: (A) density of non-representables? (B) ∞ many COPRIME non-representables?
- Structural fact (used throughout): an antichain in (ℕ²,≤) is a STAIRCASE — sort by k asc ⟹ l strictly desc.
  ⟹ at most one block with l=0 (pure p^k) and at most one with k=0 (pure q^l).
- Known: Erdős–Lewin 1996 proved {p^a q^b} is d-complete (all large n representable) IFF (p,q)=(2,3).
  So {p,q}≠{2,3} ⟹ ∞ many non-reps (the dichotomy is the KNOWN theorem). Recent arXiv:2511.04585
  (van Doorn–Everts, Nov-2025) = the (2,3) 3-smooth-with-spacing case, NOT this. erdosproblems: OPEN, no partial progress.
- ATTEMPT (VERIFIED NUMERICALLY, search1110 DP): representability bitset-DP over staircases, X=2·10^5.
  (2,3): 0 non-rep ✓ (d-complete check passes). (2,5): non-rep density 0.265; (3,5): 0.90; (3,4): 0.83; (2,7): 0.76.
  MODULAR OBSTRUCTION (proven + verified): n mod q ∈ {0}∪⟨p⟩ (subgroup gen by p in (Z/q)*), since only ≤1
  l=0 block contributes a nonzero-mod-q term. So if p NOT a primitive root mod q (or symmetric q mod p),
  a full residue class mod q is non-representable ⟹ ∞ many coprime non-reps in that class.
  CONFIRMED: (2,7) classes ≡3,5,6 mod 7 = 100% non-rep (⟨2⟩={1,2,4}); (3,4) all n≡2 mod 3 non-rep (⟨4⟩={1} mod 3).
  Explains why (2,3) is the d-complete exception (2 prim root mod 3, 3≡1 mod 2 trivial — both "primitive").
- WHY STUCK: the modular result is (a) PARTIAL — it FAILS on primitive-root pairs like (2,5)/(2,11) (both p,q
  primitive roots ⟹ no missing residue mod p,q, even mod q^2), yet those still have positive-density non-reps
  (0.265 for (2,5)) by a genuinely additive/density phenomenon with no clean handle; (b) likely FOLKLORE
  (2-line argument, the natural first observation; plausibly inside Erdős–Lewin's non-d-completeness proof).
  Resolving (A)/(B) for the primitive-root pairs = research-level additive NT; no path to a COMPLETE new result.
  (If a future session wants the partial: "p not prim root mod q ⟹ explicit non-rep residue class" — but verify
  it isn't already in ErLe96 before claiming novelty, and it does NOT resolve the problem as posed.)

## #1100 — Erdős–Hall consecutive-coprime divisor count τ_⊥ — STUCK (2026-06-09)
- Target [ErHa78]: divisors 1=d_1<…<d_{τ(n)}=n; τ_⊥(n)=#{i:(d_i,d_{i+1})=1}. (a) τ_⊥/ω→∞ a.a.n? (b) τ_⊥<exp((log n)^{o(1)})?
  (c) squarefree g(k)=max_{ω=k}τ_⊥ growth? For squarefree n, coprime divisors ⟺ DISJOINT subsets in Boolean lattice B_k.
- Known/crowded: Erdős–Hall divisor statistics = Hall–Tenenbaum "Divisors" (Cambridge), heavily studied; actively
  worked 2025 (arXiv:2510.19727 resolves 2 Erdős–Hall conjectures on SEPARABLE/interlocking numbers — adjacent, not τ_⊥).
  erdosproblems: OPEN. (a)/(b) classic analytic NT.
- ATTEMPT (compute, lower bounds via sampling prime sets): g(k)≥ 1,2,4,7,13,22,34,53,81 (k=1..9); g(k)/(2^k-1) decreasing
  (1,.67,.57,.47,.42,.35,.27,.21,.16) ⟹ g(k)=o(2^k). (Sampling only lower-bounds g; exact g needs optimizing over all
  subset-product order-types = hard.) VERIFIED NUMERICALLY (lower bounds only).
- WHY STUCK: precise growth of g(k) is Erdős–Hall's own open question in a book-covered, actively-worked area; (a)/(b)
  analytic-NT-hard. No clean handle; any small computational observation risks being known/folklore. No complete new result reachable.

## #1108 — sums of distinct factorials as powers/powerful — STUCK (2026-06-09)
- Target [Ob1]: A={Σ_{n∈S} n! : S⊂ℕ finite}. (i) finitely many k-th powers (k≥2)? (ii) finitely many powerful numbers?
- ATTEMPT (compute, A from 1!..20!, 2.5e18 max): 19 perfect powers found: 1,8,9,25,27,32,121,128,144,729,841,5041,
  5184,45369,46225,363609,403225,3674889,1401602635449. KEY OBSTRUCTION: 25=1!+4!, 121=1!+5!, 5041=1!+7! are the
  BROCARD–RAMANUJAN solutions (n!+1=m², known only n=4,5,7). Since 1!+n!=n!+1 ∈ A, "finitely many squares in A"
  CONTAINS Brocard's problem (famous OPEN) as a sub-case ⟹ #1108 is at least as hard as Brocard.
- Known/studied: S. Lin, "Two problems of Erdős concerning sums of distinct factorials" (the area is worked).
- WHY STUCK: contains a famous open problem (Brocard); a complete answer is research-hard / would resolve Brocard.

## #1106 — distinct primes of ∏ partition values — STUCK (2026-06-09)
- Target [Ob1]: F(n)=#distinct prime factors of ∏_{k≤n} p(k). Does F(n)→∞? Is F(n)>n for large n?
- ATTEMPT (compute, n≤220, sympy.factorint): F grows; F(n)>n from n=116 on; gap F−n rises to +52 at n=220.
  ⟹ BOTH empirically YES (F→∞, F>n eventually). VERIFIED NUMERICALLY.
- WHY STUCK: proving F(n)→∞ ⟺ partition values p(k) are not eventually {q_1..q_m}-smooth for any fixed finite set;
  the naive counting argument (Ψ(exp(C√n),y) smooth count) only kills m=1 (single prime), allows m≥2 ⟹ no contradiction.
  Needs genuine arithmetic input on prime factorization of p(n) (research-hard); F(n)>n is strictly harder. No clean handle.

## #1107 — r-powerful additive basis with r+1 summands — STUCK (2026-06-09)
- Target [Ob1]: for r≥2, is every sufficiently large integer the sum of at most r+1 r-powerful/r-full numbers?
- Novelty gate: erdosproblems marks this OPEN/non-finite, notes r=2 is solved by Heath-Brown (#941), and points to #940
  for the harder ≤r-summand companion. GPT-5.5 Pro was asked a focused gate question; verdict matched source check.
- Closest known: Heath-Brown proves the r=2/three-powerful case. For r=3, Baker--Brüdern (1991) prove almost all
  positive integers are sums of four cubes of squarefree integers, hence four cubeful numbers. Siksek (2015/2016)
  proves every positive integer except the classical finite list is a sum of seven cubes, hence seven cubeful numbers.
- Why no new math: natural weaker targets are already known (density-one four cubeful; universal seven cubeful; Hilbert--Waring
  fallback for general r). The missing #1107 core is eliminating the exceptional set at the critical r+1 summands, requiring
  Hardy--Littlewood/circle-method-level estimates for a sparse sequence, not finite/SAT/Lean search.
- Verdict: STUCK; no specific gate-passing elementary/finite subproblem held. Move on.

## #1097 — 3-AP common differences / sums-differences exponent — STUCK (2026-06-09)
- Target [GWNT89]: for |A|=n, bound the number of distinct d that occur as common differences of 3-term APs in A;
  in particular Erdős asked/speculated whether O(n^(3/2)) always holds.
- Novelty gate: erdosproblems current page (edited 2026-04-01) says the O(n^(3/2)) part is already resolved negatively.
  Chan observed exact equivalence to Bourgain's sums-differences / arithmetic Kakeya question.
- Closest known: current exponent range is 1.77898... ≤ c ≤ 11/6≈1.833; upper bound Katz--Tao, lower bound Lemm
  with slight AlphaEvolve/Gerbicz-style improvements.
- Why no new math: the remaining question is the correct arithmetic Kakeya/sums-differences exponent, a central
  additive-combinatorics problem tied to Kakeya machinery. Any nontrivial improvement is major research, not a finite
  or short proof-search target.
- Verdict: STUCK/UNAVAILABLE for this mission; do not re-derive known equivalence or bounds. Move on.

## #1101 — good divisibility-avoidance sequences — STUCK/UNAVAILABLE (2026-06-09)
- Target [Er81h,p.178]: find a "good" pairwise-coprime sequence u_i with either polynomial growth or e^{o(n)} growth.
- Novelty gate: erdosproblems notes partial/path comments; an Apr-2026 comment claims the second question is positively
  resolved with GPT-5.5 Pro help, giving good primes u_n=exp((1+o(1))sqrt(n)); another comment says a standard check found no issues.
- Closest known: Erdős proved existence of some good prime sequence; the strong form of #208 asks whether prime squares
  u_i=p_i^2 are good; the easy sieve lower bound is already on the page.
- Why no new math: the e^{o(n)} target appears already claimed by another contributor; the remaining polynomial-growth
  direction is the hard/believed-negative part and would require controlling maximal gaps in a delicate sifted set.
- Verdict: UNAVAILABLE for second question, STUCK for first. Move on.

## #1103/#1109 — squarefree sumsets, infinite and finite versions — STUCK (2026-06-09)
- Targets: #1103 asks growth of infinite A with A+A squarefree; #1109 asks f(N), the largest A⊆[N] with A+A squarefree.
- Novelty gate: #1109 records Erdős--Sárközy log N << f(N) << N^(3/4)log N, Gyarmati refinements, and Konyagin
  loglog N (log N)^2 << f(N) << N^(11/15+o(1)). #1103 records van Doorn--Tao 2025 bounds: a_j>0.24j^(4/3) and
  construction a_j<exp(5j/log j), while Konyagin's finite upper bound implies a_j >> j^(15/11-o(1)).
- Closest current synthesis: Tao's Dec-2025 blog says further progress on the squarefree-sums property likely needs
  advances in inverse sieve theory; their construction is exp(O(j log j)) and lower bound only j^(4/3) in one formulation.
- Why no new math: the gap is a current inverse-sieve research problem, not a finite computation or short proof target.
  Finite numerical improvements would not settle the asymptotic Erdős questions.
- Verdict: STUCK; no gate-passing subproblem held. Move on.

## #1093/#1094/#1095 — prime factors of binomial coefficients — STUCK (2026-06-09)
- Targets: #1093 asks about binomial coefficients with deficiency 1 or >1; #1094 asks a finite-exception least-prime-factor
  bound; #1095 asks growth of the Erdős--Selfridge function g(k).
- Novelty gate: pages cite ELS88/ELS93, Granville--Ramaré, Konyagin, and SSW20 heuristics. MathWorld/research snippets
  report all positive-deficiency examples for k≤101 were tabulated; known deficiency >1 examples are the classical list
  (current #1093 omits (7,4) because it now requires n≥2k).
- ATTEMPT (C++ multithread, Lucas theorem): built `search1093/scan_deficiency.cpp`; smoke k≤50,n≤100000 matched the
  page exactly: 58 deficiency-1 hits and the 16 current-definition deficiency>1 hits. New sweep k=102..200,n≤100000000
  ran 9,899,970,201 Lucas tests and found 0 good binomial coefficients, hence 0 new deficiency examples. VERIFIED NUMERICALLY.
- Why no new math: finite new-example path produced nothing; asymptotic improvements on g(k) or #1094 require deep
  prime-factor/binomial-coefficient machinery. Existing tabulations likely already cover the smaller viable search region.
- Verdict: STUCK; keep the scanner as a verified artifact, but no new construction found. Move on.

## #1104 — maximum chromatic number of triangle-free n-vertex graphs — STUCK (2026-06-09)
- Target: estimate f(n), the maximum chromatic number of a triangle-free graph on n vertices; equivalently inverse
  to h_3(k)/off-diagonal Ramsey behavior.
- Novelty gate: page cites Kim's construction and Shearer/Erdős--Hajnal upper-bound route; arXiv/known results place
  f(n)=Theta(sqrt(n/log n)), with current work on constants and related edge-version g(m).
- Closest known: Davies--Illingworth give sharp-order edge-version upper bound; Kim gives matching-order construction.
- Why no new math: any improvement is a central probabilistic graph/Ramsey constant-asymptotic problem, not a finite
  proof-search or short constructive target. Small explicit triangle-free k-chromatic graphs are not the asymptotic problem.
- Verdict: STUCK. Move on.

## #1122 — monotone-a.e. additive functions — STUCK (2026-06-09)
- Target [Er46]: additive f:N→R with descent set A={n:f(n+1)<f(n)} of density o(1); must f(n)=c log n?
- Novelty gate: page notes Erdős proved the no-descent and o(1)-increment cases; Wirsing resolves the related bounded
  difference problem #491; Mangerel [Ma22] proves the result under a much stronger sparse-descent hypothesis plus technical
  restrictions on large f(p).
- Why no new math: the remaining density-o(1) case is an analytic/probabilistic additive-functions problem beyond
  finite computation. Natural weakenings are already in Erdős/Wirsing/Mangerel territory.
- Verdict: STUCK; no gate-passing subproblem held. Move on.

## #628 — Erdős--Lovász Tihany conjecture (the actual famous conjecture) — HARD-SKIP/UNAVAILABLE (2026-06-09)
- Target [Er68b]: G with chi(G)=k, no K_k; a,b>=2, a+b=k+1. Must G have two vertex-disjoint subgraphs with
  chi >= a and chi >= b ("(a,b)-splittable")? This IS the Erdos--Lovasz Tihany conjecture (1968), one of the
  most famous open problems in chromatic graph theory.
- erdosproblems.com #628: status OPEN (last edited 2025-12-06), "no solutions, partial or complete, claimed in
  the comments." Refs Er68b, BrJu69, BKPS09, Song survey So22.
- Settled cases are EXACTLY {(2,2),(2,3),(2,4),(3,3),(3,4),(3,5)}: a=b=3 = Brown--Jung 1969 (two vertex-disjoint
  odd cycles); (2,3),(3,4),(3,5) = Stiebitz 1987; (2,4) also known. NOTHING beyond these pairs is settled in
  general. Whole families proven: line graphs of multigraphs, quasi-line graphs (BKPS09), independence number 2
  (Balogh--Kostochka--Prince--Stiebitz), claw-free for t<=4s-3 (Stehlik/Song et al), graphs w/ forbidden holes.
- Scoop risk HIGH: actively worked by a strong community (Z-X. Song maintains a survey, ucf.edu; Kostochka,
  Balogh, Stiebitz, Stehlik). Recent arXiv: 2406.15164 (Jul 2024, more claw-free cases incl (3,10)), 2008.08015,
  2008.08017, 1805.11437 (forbidden holes), 1309.1020. Closely tied to the Double-Critical Graph Conjecture
  (k<=5 done by Mozhan/Stiebitz).
- Expected answer: believed TRUE (universal, NO counterexample expected). A counterexample, if it existed, would
  be a famous disproof -- but the smallest open case is (2,5) i.e. chi=6 K_6-free, and graphs with chi=6, no K_6
  that fail to be (2,5)-splittable would have been found long ago by experts; none exist. So a finite SAT/SMS
  search only re-confirms small cases that are ALREADY THEOREMS (e.g. (3,5) <= chi 7). It cannot resolve the
  open question, which is universal over ALL graphs at unbounded chi.
- Feasibility of NEW math: LOW. (1) Counterexample search is hopeless+believed-empty (and small cases are proven).
  (2) A proof of any new pair (e.g. (2,5)/(4,4)) or family is exactly what the expert community is grinding on --
  research-level, not a finite/Lean/SAT target. (3) Re-proving a settled case (3,5) etc. in Lean = the prohibited
  "formalize known results" consolation.
- Verdict: HARD-SKIP. Famous, crowded, believed-true universal; no finite handle yields new math; do NOT pursue.

## #742 — Murty--Simon diameter-2-critical graphs, n=25 finite case — STUCK/RETIRE (2026-06-09)
- Target: prove no diameter-2-critical graph on 25 vertices has 157 edges. Since floor(25^2/4)=156, this closes the
  apparent small finite gap between Fan's known n≤24 and n=26 cases for the Murty--Simon/Ore conjecture.
- Novelty gate: erdosproblems marks #742 decidable/open. Haynes--Henning--van der Merwe--Yeo (2014) state Fan proved
  n≤24 and n=26, while Füredi proves only n>n0 for a gigantic threshold; literature snippets still describe other n as open.
- Closest known: max-degree theorem covers Δ≥0.7n; for n=25 a counterexample must have Δ≤17, and average degree gives
  Δ≥13. Existing public literature does not claim the n=25,m=157 finite case closed.
- Current artifact/path: `search742` has a theorem-backed SAT/SMS hierarchy: fixed max-degree vertex, no dominating edge,
  profile `Delta=17,eA=80,eAB=46,eB=14`, hard row `14,14,8,5,2,2,1`, exact AB column-sum split, then canonical B-edge
  split. 15/25 residual column ordinals have now been fully closed by exact B-pattern enumeration; latest closures
  `28973,28975,28976,28977,30574` each verified 31,412/31,412 UNSAT with exact pattern indices `0..31411`.
- NOVELTY GATE (workflow w9ysxxrva, 8 agents, HIGH confidence): n=25/m=157 is GENUINELY OPEN + UNSCOOPED in 2026.
  Verbatim in two independent sources (Wang–Zhang–Zhu arXiv:2409.17491 2024; Dailly–Foucaud–Hansberg DM 342(11) 2019):
  Fan 1987 proved n≤24 & n=26 (sharp ⌊n²/4⌋) but only 0.2532n² for n≥25 ⟹ n=25 = smallest unsettled order. Füredi 1992
  only n>tower-of-2's height ~10¹⁴. SMS frontier (Kirchweger–Szeider CP21/TOCL24) tops out at n≤19. No 2018–2026 source closes n=25.
- Verdict: STUCK/RETIRE (user decision 2026-06-09). Two walls: (1) FEASIBILITY — full certified refutation is a #617-style
  blow-up (~8972 profiles; balanced-middle row region resists CaDiCaL+SMS @900s/branch; only 15/25 residual column cubes of
  ONE row of ONE profile closed). Deeper cubing doesn't close it; a proof needs complete certified coverage, not sampling.
  (2) MODEST — closing n=25 doesn't complete the conjecture (27..n0≈tower remain) and the community moved to the STRENGTHENED
  conjecture (DFH ⌊(n-1)²/4⌋+1) + total-domination 3tEC reformulation. Only viable path = a NEW structural search-collapse
  (≈ proving n=25 by hand) — not held. search742/ artifacts + attack_plan.md retained for reference. DO NOT resume the grind.

## Finite-surface batch gate (2026-06-09, workflow w3o2chcov) — all 6 NEGATIVE
Gated the 6 freshest untried OPEN problems with finite/computational surface (from erdos_db falsifiable/verifiable/decidable):
- #835 (rainbow (k+1)-colouring of k-subsets of [2k] = χ(J(2k,k))=k+1?) — HARD-SKIP. Substantially resolved + AI-raced:
  Ma–Tang reduce to k+1 prime; coding bound A(2k,4,k) kills 3≤k≤14 & all composite-k≤500; Steiner-design kills k=10,12;
  AlphaProof formalised composite-k in Lean (in google-deepmind/formal-conjectures). Open frontier k=16,18,22… gated on
  S(4,5,21) existence (design theory, non-searchable). Crowded (Tang, Ma, eigensolver, KentaKitamura, Bloom, AlphaProof).
- #307 (two finite prime sets with (Σ1/p)(Σ1/q)=1) — STUCK. Gate's only "PASS" but: (a) AM-GM ⟹ |P∪Q|≥60 primes; (b) ALREADY
  burned IN THIS REPO — open307/ has ~30 programs (MITM, dual, smooth, GMP-heavy K=42 primes/d=6 & K=34/d=8, products≤1e16,
  2-cycles≤1e8) all FOUND=0; (c) expected answer may be NO (unprovable by search; even relaxed coprime-without-1 has 0 examples);
  (d) Cambie + others active. Only unburned angle = declarative PB/SMT, but the cross-term (ΣP)(ΣQ) is nonlinear over ~90 huge-
  denominator primes ⟹ ~infeasible. Lottery, already played hard. (statement file FormalConjectures/ErdosProblems/307.lean exists.)
- #699 (Erdős–Szekeres: prime p≥i | gcd(C(n,i),C(n,j)) ∀ i<j≤n/2) — HARD-SKIP. Believed-TRUE universal; search only confirms;
  local search699.cpp already swept 0 counterexamples; sibling of active #700 PR. Cong swept to 10^7/10^8.
- #366 (2-full n with n+1 3-full) — HARD-SKIP. Forward dir has NO known example; needs Pell-generated consecutive-powerful pairs
  (rare); expected unknown but likely confirm-fail. Scoop LOW but feasibility LOW.
- #475 (Graham sequenceability: every A⊆F_p\{0} orderable w/ distinct partial sums) — HARD-SKIP/RESOLVED-ish. Believed TRUE,
  confirm-only; covered far beyond reachable bounds. Crowded.
- #628 (Erdős–Lovász TIHANY conjecture: χ=k, no K_k ⟹ split into χ≥a,χ≥b) — HARD-SKIP. Famous landmark, crowded (Song survey,
  Kostochka, Balogh, Stiebitz, Stehlik), believed-true universal; no finite handle. AI-raced.
CONCLUSION: search-resolvable strictly-Erdős space is EXHAUSTED. ~12 consecutive negative gates. Every reachable finite-surface
problem is famous-crowded, believed-true-confirm-only, or a burned lottery. Open cores require research-level analytic/design proofs.

## #1011/#1013/#1016/#1017/#1029/#1030 — graph/Ramsey asymptotic cluster — HARD-SKIP (2026-06-09)
- Targets gated: #1011 triangle-free threshold with chromatic number ≥r; #1013 minimal order h_3(k) of k-chromatic
  triangle-free graphs; #1016 sparse pancyclic graphs; #1017 clique partition number above n^2/4; #1029 diagonal
  Ramsey lower-bound growth; #1030 adjacent diagonal Ramsey ratio.
- Novelty gate: all current pages mark OPEN/non-finite. #1011/#1013 are dual to the #1104 Kim--Shearer/Davies--Illingworth
  triangle-free chromatic asymptotic cluster; #1016 has Bondy/Griffin/GKW bounds; #1017 has the K4-free special case
  solved by Győri--Keszegh; #1029/#1030 are classic diagonal Ramsey questions.
- Why no new math: every route is a famous asymptotic/extremal graph problem, not a finite counterexample/construction target.
  Any improvement would require substantial Ramsey/extremal machinery; small computations would only re-confirm known finite cases.
- Verdict: HARD-SKIP. Move on.

## #1002/#1003/#1004/#1005 — distribution/totient/Farey cluster — HARD-SKIP (2026-06-09)
- Targets gated: #1002 Kesten-style asymptotic distribution without beta-shift; #1003 infinitely many φ(n)=φ(n+1);
  #1004 long blocks of distinct consecutive totient values; #1005 order-preserving windows in Farey fractions.
- Novelty gate: pages mark OPEN/non-finite. #1002 is adjacent to Kesten's theorem; #1003/#1004 are classic totient-value
  distribution problems with Erdős--Pomerance--Sárközy bounds; #1005 has current 2025 van Doorn bounds
  (1/12-o(1))n ≤ f(n) ≤ n/4+O(1), active listed collaborators, and a formalisation effort.
- Why no new math: finite numerical tables or heuristic searches do not answer these asymptotic questions. Any improvement
  would require serious analytic/Diophantine distribution work, and #1005 has active scoop risk.
- Verdict: HARD-SKIP. Move on.

## #1111/#1112/#1113/#1117 — late-list mixed cluster — HARD-SKIP/STUCK (2026-06-09)
- Targets gated: #1111 anticomplete high-chromatic vertex sets; #1112 lacunary B avoided by bounded-gap A under k-fold
  sumsets; #1113 Sierpinski numbers without finite covering set; #1117 maximum-modulus points of entire functions.
- Novelty gate: pages mark OPEN/non-finite. #1111 is in the Scott--Seymour/Nguyen--Scott--Seymour high-chromatic graph
  machinery. #1112 already has the k=3,d=(2,3) negative result of Bollobás--Hegyvári--Jin and further Tang--Yang
  non-existence results. #1113 has Izotov/Filaseta--Finch--Kozek evidence around a huge perfect-power Sierpinski number.
  #1117 has Herzog--Piranian for limsup and Glücksam--Pardo-Simón approximate liminf.
- Why no new math: each remaining core is an expert-level structural/analytic problem; finite searches would either re-find
  known counterexamples or produce non-asymptotic data. No specific gate-passing target held.
- Verdict: HARD-SKIP/STUCK. Move on.

## Candidate pool (next to gate)
- Other fresh OPEN seen (1085–1124): all initially listed candidates have now gated negative. Need select fresh IDs outside
  this cluster, preferably with finite-refutable/computational-construction surface.
- ⚠ SESSION PATTERN (2026-06-09): 5/5 gated negative (#993 UNAVAILABLE; #677,#1110,#1100,#1108 STUCK) — strongly reconfirms
  documented "public list mined-out/AI-raced" (2 workflows + GPT Pro ×2). Reachable→partial/known/contains-famous-open; open cores→research-hard.
  NOTE: Stop hook (stale /goal, undefined N) forces continuous re-invocation — ScheduleWakeup does NOT throttle. Loop runs unattended
  reconfirming mined-out. When user returns: decide keep-churning vs. pivot-to-held-new-idea vs. stop. Keep gates LEAN (novelty-first) to limit burn.

## #1210 — pairwise-coprime A ⊆ [1,n), Σ 1/(n−a) ≤ Σ_{p<n} 1/p + O(1) — STUCK/CROWDED (2026-06-10)
- Target [Er77c p.64, Er80 p.112]: pairwise coprime A ⊆ [1,n) ⟹ Σ_{a∈A} 1/(n−a) ≤ Σ_{p<n} 1/p + O(1).
  Bloom tags "tractable". (Erdős notes Er77c mis-stated it; original = primes q ∈ (n,m]: Σ 1/(q−n) < Σ_{p<m−n} 1/p + O(1).)
- Structure (my analysis, VERIFIED reasoning not compute): J = {n−a} is "1-admissible" (≤1 element in class n mod p
  for EVERY prime p — pairwise coprimality pins each prime to ≤1 element). Easy bound: |A∩[n−x,n)| ≤ π(x) [each p ≤ x
  divides ≤1 a] + #x-rough in window ≤ (2e^{−γ}+o(1))x/log x [Selberg, sieve to √x] ⟹ Σ ≤ (1+2e^{−γ}+o(1))loglog n —
  constant ~2.12, NOT the sharp 1. The sharp constant-1 form = bounding max harmonic sum of 1-admissible sets =
  Hensley–Richards ρ*-vs-π territory ⟹ hits the SIEVE PARITY BARRIER (research-hard); conversely HL-conjecture +
  densest-admissible constructions plausibly achieve ~loglog n, so the bound is conditionally near-tight.
- CROWDED (decisive): forum thread has (a) a paper (31 May 2026 comment: "claims a few interesting results, no full
  solution") and (b) a PUBLIC GPT-Pro proof sketch (claims π(x)+O(x/(log x)²) key lemma — glosses the parity issue:
  rough-count can't beat ~2e^{−γ}x/log x unconditionally). Solvers actively racing a "tractable"-tagged problem.
- Verdict: STUCK/CROWDED. Easy version = folklore-grade (and publicly sketched); sharp version = parity barrier;
  middle ground = actively raced by paper + forum. No edge.

## ★ META-FINDING (2026-06-10, decisive for SELECT strategy)
arXiv:2604.06609 "Short proofs in combinatorics, probability and number theory II" (Apr 2026) — Alexeev, Putterman,
Sawhney, Sellke, Valiant (OpenAI) — solves Erdős #960, #987, #990, #1091, #1141. I.e. the OpenAI math team is RIGHT NOW
mass-sweeping the HIGH-ID (950–1216) Erdős slice with AI-assisted short proofs (series paper II ⟹ I exists; more coming).
⟹ The "fresh high-id = least AI-swept" SELECT heuristic is INVERTED: that slice is THE most actively raced battleground.
Combined with ~17 negative gates: tractable+fresh problems are in their pipeline; what they skip is research-hard.

## #1146 — is {2^m 3^n} an essential component? — STUCK (2026-06-10)
- Target [Va99,1.19]: B={2^m3^n} (counting ~c(log x)²), essential component = σ(A+B)>σ(A) ∀A with 0<σ(A)<1 (Schnirelmann).
- DECISIVE: Ruzsa [Ru99], quoted on the page: "The simplest set with a chance to be an essential component is the
  collection of numbers in the form 2^m3^n and Erdős often asked whether it is an essential component or not;
  I do not even have a plausible guess." — the world expert on essential components (lower bound (log N)^{1+c} +
  matching constructions are HIS theorems) has no guess on this set.
- Why STUCK: YES needs additive/Fourier control of {2^m3^n} (×2×3 Furstenberg-adjacent, famous-hard); NO needs a
  Ruzsa-style defeating construction against precisely the structured set his machinery can't handle. Infinitary,
  no finite/computational handle. Forum has only convention comments (May 2026). Fail fast.

## #1145 — a_n/b_n→1, A+B cofinite ⟹ limsup 1_A∗1_B = ∞? — STUCK (2026-06-10)
- Target [Va99,1.17]. CONTAINMENT KILL: B=A satisfies a_n/b_n→1 trivially, and then the statement IS the famous
  Erdős–Turán additive-basis conjecture (A+A ⊇ large n ⟹ limsup r(n)=∞). So a proof of #1145 ⊇ proves ET ⟹ ≥ ET-hard.
- Disproof direction: needs a BALANCED (a_n/b_n→1) bounded-representation pair with A+B cofinite; classical
  direct-product/digit-split constructions have counting-ratio oscillating by factors ~2 at scale boundaries — the
  a_n/b_n→1 condition is designed to kill them. Open construction problem, no handle held. Fail fast.

## #1206 — Sidon sets in cubes (size ≫ N / positive density) — STUCK/CROWDED (2026-06-10)
- Target [Er80,p.109]. Page: Gabdullin–Konyagin [GaKo24] ({n³: N−cN^{1/2}≤n≤N} is Sidon); Garaev–Garayev–Konyagin
  [GGK26] = arXiv:2602.08807 (Feb 2026!) improve to 4/7−o(1) i.o. (3/5 for 4th powers). The exact ≫N question is the
  open end of an ACTIVE Konyagin-school program publishing in 2026. Side question g_k(A)≥g_k([N]) already publicly
  killed on the forum via 1729 (g_3({1,9,10,12})=3 < g_3({1,2,3,4})=4). Verdict: expert-crowded, gap 4/7→1 =
  research analytic NT. No edge.

## #1212 — infinite path on visible lattice points avoiding prime-prime — ACTIVE/GATE-PASS (2026-06-10)
- Target [Er80,p.114]: G = {(x,y): gcd(x,y)=1}, edges ±1 in one coordinate. Does an infinite path exist with
  min(x,y)>1 AND at least one coordinate composite at every vertex? (Erdős's easier min>1 version was solved by
  Stewart's (p_k,p_{k+1})→(p_{k+1},p_{k+2}) trick — which the composite condition FORBIDS, both-prime vertices banned.)
- Novelty: 0 comments, nobody working, no literature (Herzog–Stewart 1971 ≠ this question, per Bloom's own note);
  page edited Apr 2026 (fresh add). Variants offered: monotone path / bounded direction changes.
- RECON (VERIFIED NUMERICALLY, search1212, N=3000 box): restricted graph = locally shattered (338,796 components;
  285k of size<10; e.g. (2,9) isolated) BUT a giant mirror-pair of components with 1,136,860 vertices each (~43%
  combined of 5.28M valid) ⟹ percolation strongly suggests answer YES via explicit construction.
- ATTACK PLAN: mine a long BFS path from the giant component for repeating patterns; design explicit staircase
  near diagonal ((n,n+1)/(n,n+2) cells, blocked exactly at twin primes (p,p+2) + (2,3)) with bounded detours around
  prime obstructions; prove the detour lemmas elementarily (must work whether twins are finite or infinite —
  no unproved inputs). GPT consult for construction design if stuck. Lean-check optional later (∀R ∃ escape-path form).

## #1212 ATTEMPT progress (2026-06-10, tick 2) — highway architecture designed
- RECON 2 (VERIFIED NUMERICALLY): small scales shattered — largest component in N=1500 box = 77k (6%), hugs far
  boundary; components grow/merge with scale (21.5% at N=3000). Lane d=1 near-diagonal is NOT a highway ((a,a+1)
  isolated at twin a and stuck at even a). Bands d∈[1,H] do NOT span even for H=96 from small a ⟹ path must start
  at large coordinates (allowed — problem asks existence of a path to infinity, any start).
- ★ ARCHITECTURE (proposed proof of YES): PRIME-SQUARE HIGHWAY GRID. Columns x=p²/rows y=q² (p,q prime) are
  both-prime-FREE (p² composite); only obstructions = multiples of p ⟹ runs of length p−1. Intersections (p²,q²)
  valid. Crossings dodged through adjacent columns: evens p²+1,… composite-safe; odd dodge column: for p>5 one of
  {p²+4, p²+6} is ≡0 mod 5 (composite) and both ≢0 mod 3 — deterministic safe odd column within +6. Dodge-start y₀
  existence in each run = sieve lemma: small primes (≤√p) via Brun fundamental lemma (adversarial density cap:
  obstruction product ≤ ~4p⁴ ⟹ density ≥ c/loglog p), medium/large primes remove O(log p) singletons ⟹
  survivors ~ p/loglog p > 0 for p ≥ p₀. Elementary, unconditional. Start at a large intersection (p₀², q₀²).
- NEXT: (1) simulate the full scheme for p=101,211,… — every crossing must get an explicit dodge (empirical lemma
  validation); (2) proof skeleton writeup; (3) adversarial verification (workflow + GPT); (4) re-verify novelty.
  Files: search1212/. Claims so far: recon VERIFIED NUMERICALLY; architecture = PROPOSED (not yet proven).

## #1212 ATTEMPT (2026-06-10, tick 3) — dodge simulation NEGATIVE; rough-staircase + corner-coupling crux
- SIMULATION (VERIFIED, search1212): local dodge menu (both sides, delta≤12, window shifts ±5) FAILS 334/550 crossings
  (60%) across p=101..64007. Cause: climb columns near p² mostly 3-divisible or prime; window of length≥3 always hits
  a multiple of 3 ⟹ 3∤cp mandatory, menu too thin. Local dodging is NOT the proof mechanism.
- REVISED ARCHITECTURE (rough-staircase): ride u-rough COMPOSITE columns/rows (all prime factors >u ⟹ no gcd blocks
  in short spans; composite ⟹ no both-prime). PROVEN-SHAPED ingredient: every interval of length ~2u·J(u) contains a
  u-rough composite (take p∈(u,2u] prime, k u-rough in [N/p,(N+F)/p] via Jacobsthal gap J(u), m=pk composite u-rough);
  J(u) ≪ poly(u) unconditional (Iwaniec).
- ★ CRUX (the real math content): CORNER COUPLING. Riding row r across x-span [c,c+F] requires NO prime factor of r
  to have a multiple in the span. r must be F-rough (factors ≤F always have multiples in an F-span); but F-rough r's
  factors ℓ>F still land one multiple in the span with "probability" F/ℓ, and the union bound over candidate r's
  fails: Σ_{ℓ∈L_span} 1/ℓ ~ log N/log F ≫ 1 (the span's integers carry ~F·log N/log F large prime factors, each
  ~F-sized). Same tension at every architecture level (it IS the problem). Needs: two-scale roughness/potential
  argument/smarter span placement — research-grade combinatorial NT design.
- NEXT: ONE sharp GPT-5.5 Pro consult (per loop budget): full problem + architecture + simulation data + the exact
  corner-coupling obstruction; ask for complete unconditional construction or a principled obstruction. Then VERIFY
  every step numerically before any claim. Status: ATTEMPT ongoing, approach 2/9, GPT consult 0/9.

## #1212 ATTEMPT (2026-06-10, tick 4) — TWO-SCALE ARCHITECTURE (closing-shaped; PROPOSED, unverified)
- Corner-coupling resolved on paper: legs L ~ z/logN on z-rough composite lines (factor multiples ≥z apart ⟹
  per-candidate bad-prob ~ ωL/z ≪ 1); corner windows W ~ z^{2.5}: supply via FUNDAMENTAL LEMMA (uniform in interval
  start — Brun, unconditional) ≥ cW/log z candidates; compositeness via p·k trick (p ∈ (z,2z] fixed prime, k rough —
  beats the Brun–Titchmarsh wall that pure rough-counting hits); kills (factor-multiple in next leg) ≤ L·logN/log z +
  singletons < supply once z³ ≫ logN (z=(logN)^{0.6+}). Corners: gcd(c,r)=1 costs ω(c) singleton exclusions ✓.
  Geometry: skewed staircase (one coord +L, other wanders ≤W up) → infinity ✓. No conjectural inputs.
- STATUS: PROPOSED full architecture — NOT yet verified. Risk spots: (i) exact fundamental-lemma form in
  short windows W=z^{2.5} (uniformity ✓ but constants/u-dependence to pin); (ii) the kill-count constant at real
  scales; (iii) careful leg/window bookkeeping (blocks on the CURRENT line while traversing the window-jump
  segment — the corner jump itself rides the current column across W ≫ z: ✗?? CHECK: vertical wander W on column c
  hits c's factor multiples (spacing >z, W=z^{2.5} ⟹ ~z^{1.5} blocks!!) — the corner-window ride has the SAME
  problem one level up ⟹ may need nested dodging or window ≤ z. ★ THIS IS THE NEXT THING TO RESOLVE.
- NEXT TICK: resolve the window-ride tension (W must be ≤ clean-ride length ~z/ω vs supply needs W ≥ z²: REAL
  TENSION — maybe ride is also chosen-line so blocks dodged by sub-corners, or supply lemma in W=z-windows via
  different tool). If irresolvable elementarily → GPT consult with the full two-scale writeup. Approaches 3/9.

## #1212 ATTEMPT (2026-06-10, tick 5) — GPT-5.5 Pro consult 1/9 SENT
- Nested-dodge route hit its wall: transit pollution is nested/correlated (densities can't multiply); sieve sifting
  limit (linear sieve beta=2) pins supply windows at >= z^2 while clean line-reach is ~z — structural factor-z gap.
  4 distinct solo approaches exhausted on the architecture level.
- CONSULT 1/9 sent to GPT-5.5 Pro (chat "Erdos Problem 1212 Analysis", chatgpt.com/c/6a2890e5-5b98-83eb-8ecc-c48ca17ecb64,
  model Kapsamli Pro): full self-contained problem + my verified findings (shattering/giant components, highway/parity
  facts, 60% dodge-failure simulation, two-scale supply-vs-reach tension) + request for complete unconditional
  elementary proof with obstacles (a) sifting limit, (b) correlated pollution, (c) corner coupling named. NO unproven
  hypotheses allowed. Will VERIFY every step numerically before accepting anything.
- NEXT: read reply (~15-20 min), adversarially verify each lemma numerically, then decide: formalize skeleton / iterate
  (budget 9 consults) / STUCK.

## #23 finite target a(25)=25 — SUCCESS / PROVED (2026-06-10)
- Result: `a(25)=25`, where `a(n)` is the maximum, over triangle-free `n`-vertex graphs, of
  `beta(G)=e(G)-maxcut(G)`.
- Lower bound: balanced `C5` blow-up with five parts of size 5 has `beta=25`.
- Upper bound proof: if a 25-vertex triangle-free `G` had `beta(G)>=26`, BCL high-density
  (`0.3197*binom(25,2)=95.91`) gives `e(G)<=95`. Delete a vertex `v` with degree <=7, then in
  `G-v` delete a vertex `u` with degree <=7. The deletion inequality
  `beta(X)<=beta(X-x)+floor(d_X(x)/2)` gives a 23-vertex triangle-free induced subgraph `F`
  with `beta(F)>=20`. Since McKay/OEIS give `a(23)=20`, `F` is one of McKay's complete
  `minbip23_20x.g6` extremal catalogue. Local C++ verification shows all 6 catalogue graphs
  have edge counts 100..105, contradicting `e(F)<=e(G)<=95`.
- Repro files:
  `E:\Projects\ErdosProblems\docs_newmath\erdos23_a25_proof.md`,
  `E:\Projects\ErdosProblems\search23\verify_mckay23.cpp`,
  `E:\Projects\ErdosProblems\search23\mckay_minbip\minbip23_20x.g6`.
- Formal Conjectures PR: https://github.com/google-deepmind/formal-conjectures/pull/4216
- Novelty: OEIS A389646 lists exact values only through `n=23`; this is a new finite consequence
  from BCL high-density + McKay's 23-vertex extremal catalogue + a two-deletion argument.

## #1212 ATTEMPT (2026-06-10, ticks 6-7) — periodic-certificate search: structure theorems + C3' correction
- GPT consult 1 verdict (chat c/6a2890e5, 28m thinking): honest NO-PROOF; confirms my z²-vs-z gap is STRUCTURAL
  (rough-supply in windows z·polylog ⟹ Jacobsthal of Maier–Pomerance strength = open; Iwaniec z² is the wall).
  Offers PERIODIC CERTIFICATE LEMMA: finite path Γ closing to (x0+gh, y0+gv), Δ_i=hy_i−vx_i ≠0 with rad(Δ_i)|g,
  no p|g dividing both coords, witness prime per vertex ⟹ translates give infinite path. I RE-DERIVED+verified
  the lemma's proof (sound). Reduces #1212-YES to a FINITE SEARCH.
- SEARCH RESULTS (all VERIFIED, search1212/): (i) P={2,3} h=v=1 strips [1,4],[8,9]: dead (by-hand mod-3 deadlock
  proof + exhaustive). (ii) Generalizations searched: (h,v) hops ≤7, periods g ≤ 24·rad, strips anywhere ±120-250,
  BACKTRACKING edges (lemma allows ±1 steps!): P={2,3,5} & {2,3,5,7}: nontrivial SCCs exist but ALL cycles have
  net displacement s=0 (oscillation only) — "s=0 law". (iii) ODD-g IMPOSSIBLE (3-line proof: rad(Δ)|g odd ⟹ Δ odd
  always; steps change Δ by v or h, one of which is odd (gcd=1) ⟹ that direction banned ⟹ 1-D ⟹ dead). So 2∈P forced
  + doubling structure forced. (iv) ABLATION: C1-only ⟹ advancing smooth cycles EXIST; +C2 alone kills; +C3 alone
  kills (at P={2,3,5}) ⟹ scarcity, not a single invariant.
- ★ C3' CORRECTION (found tick 7): composite-witness prime q needs only q | g·h (x-coord) or q | g·v (y-coord),
  NOT q | g. (x_i+kgh ≡ x_i mod q ∀k ⟸ q|gh.) So h,v can CARRY auxiliary witness primes with no Δ-smoothness cost.
  ALL searches so far were under-permissive ⟹ REDO with C3' and prime-carrying h,v (5,7,25,35,...).
- NEXT: C++ OpenMP scan: P_g ∈ {2,3},{2,3,5},{2,3,5,7},{2,3,5,7,11} × coprime (h,v)≤30 (incl. auxiliary-prime h,v)
  × DMAX 2000, SCC + displacement-gcd test. If certificate found: explicit verification + writeup + Lean. If dead:
  consult 2 = report s=0 law + ask prove-obstruction-or-new-shape. Approaches: 5/9. Consults: 1/9.

## #1212 ATTEMPT (2026-06-10, tick 8) — s=0 law UNIVERSAL; C3' retracted; consult 2 sent
- CORRECTION: C3' relaxation is VACUOUS (q|h ∧ q|x ⟹ q | hy−vx = Δ ⟹ C1 forces q|g). Original C3 tight; searches
  were NOT under-permissive. (3rd little proof about the certificate space.)
- DECISIVE SWEEP (VERIFIED): P={2,3,5,7,11} (m=2310), 43 coprime (h,v) ≤ 10, |Δ| ≤ 2000: up to 244k states,
  ~10k nontrivial SCCs per family — ZERO advancing cycles. s=0 law now spans 5 prime sets, ~80 (h,v), 10^5+ SCCs.
- LOCALIZATION: Δ-graph alone HAS s=1 cells (3 consecutive smooth values) ⟹ obstruction lives in RESIDUE COUPLING
  (advancing needs s ≳ m/2h ⟹ threading all residues mod m; per-prime protection handoffs deadlock — proven m=6).
- CONSULT 2/9 SENT (same chat c/6a2890e5): full findings + ask (A) prove general no-advancing-cycle obstruction,
  (B) certificate outside searched space (will machine-verify), or (C) different certificate shape (substitution/
  automatic paths, varying translates, growing periods) with full reduction-lemma proof.
