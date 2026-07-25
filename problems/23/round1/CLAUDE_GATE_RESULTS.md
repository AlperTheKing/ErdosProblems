# Round 1 — root-agent (Claude) results, exactly verified

Campaign restarted 2026-07-25 on the CDC-prompt template (GOAL/LOOP v10).
Target: bip(G) <= N^2/25 for every finite triangle-free G, exact constant, no extra hypotheses.

Everything below is either a complete written proof or an explicit object verified in exact
integer arithmetic by two independently written implementations. Nothing here rests on an
estimate or a plausibility argument.

---

## 0. Ruling carried over: the R52/R53 soft pivot is BLOCKED, not live

Its terminal object is `canonicalSoftCollisionFeasibleTuple_exists` (equivalently the
edge-cap-2 variant `canonicalSoftEdgeCapFeasibleTuple_exists`). That statement has strength at
least the conjecture: the compiled chain `softCollisionFlow_to_erdos23` derives 25|M| <= N^2
from it by elementary counting, so proving it *is* proving the conjecture. Under GOAL rule (a)
the route is BLOCKED, and running the never-executed Delta_soft corpus sweep would produce
evidence, not progress. Reopen only if a genuinely new proof mechanism for that lemma appears.

Blocking lemma, verbatim: *for every triangle-free G with a Gamma-minimal maximum cut there
exists a selection omega whose soft collision system admits a feasible integral two-cover.*

---

## 1. Exact ground truth: a(N) for N <= 13

a(N) = max { bip(G) : G triangle-free, |V(G)| = N }. Restricting to CONNECTED G is sound,
since bip is additive over components and sum N_i^2 <= (sum N_i)^2.

Method: nauty `geng -t -c` for the complete connected triangle-free census; exhaustive
Gray-code maxcut over all 2^(N-1) bipartitions; exact integers throughout
(`claude_exact_bip.cpp`). Independently re-verified with a separate graph6 decoder and a
separate brute-force maxcut in Python (`claude_verify_a12.py`, `claude_identify_n12.py`).

| N | connected triangle-free graphs | a(N) | attained by | N^2/25 | a(N)*25/N^2 |
|---|---|---|---|---|---|
| 4 | 3 | 0 | 3 | 0.64 | 0 |
| 5 | 6 | 1 | 1 | 1.00 | **1.000** tight (C5) |
| 6 | 19 | 1 | 2 | 1.44 | 0.694 |
| 7 | 59 | 1 | 15 | 1.96 | 0.510 |
| 8 | 267 | 2 | 7 | 2.56 | 0.781 |
| 9 | 1,380 | 2 | 79 | 3.24 | 0.617 |
| 10 | 9,832 | 4 | 1 | 4.00 | **1.000** tight (C5[2]) |
| 11 | 90,842 | 4 | 13 | 4.84 | 0.826 |
| 12 | 1,144,061 | 5 | 2 | 5.76 | 0.868 |
| 13 | 19,425,052 | 6 | 8 | 6.76 | 0.888 |
| 14 | 445,781,050 | 7 | | 7.84 | 0.893 |
| 15 | running (32 lanes) | ? | | 9.00 | |

Extremal examples: N=12 `K?ABBBwerwBw`; N=13 `L??ED@_~?~^_Fw`; N=14 `M?AE@bH{AYN_LgBs?`.
The conjecture holds at every order checked. Note that the published theorem covers only
N = 5n; the values above for N not divisible by five are new exact coverage.

Note this is verification infrastructure and obstruction-mining, NOT progress toward the general
theorem: GOAL rule (d) explicitly excludes finite ranges of N from counting as progress.

### R1-C3 — the conjecture is INTEGRALLY TIGHT at every order in 10..14 (structure, exact)

Comparing a(N) with floor(N^2/25):

| N | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a(N) | 0 | 1 | 1 | 1 | 2 | **2** | 4 | 4 | 5 | 6 | 7 |
| floor(N^2/25) | 0 | 1 | 1 | 1 | 2 | **3** | 4 | 4 | 5 | 6 | 7 |

**a(N) = floor(N^2/25) for every N in 4..14 except N = 9**, where a(9) = 2 < 3.

Consequence, and it is a sharp one. The natural hope that the conjecture has slack at orders
that are not multiples of five -- which would let an induction pass cheaply through them -- is
FALSE for every order from 10 to 14: the bound is attained as closely as integrality permits, so
a(N) + 1 > N^2/25 at each of those orders. Any proof must therefore be essentially tight at
*every* order, not only at N = 5n. The single exception at N = 9 (where the truth is one below
the integer bound) is unexplained and worth understanding.

Stated as a candidate law: a(N) = floor(N^2/25) for all N >= 10. This is strictly stronger than
the conjecture, so proving it is rule-(a) territory; it is recorded here only as an exactly
verified empirical constraint on the extremal structure.

**CORRECTION, added after R1-C7 and the wide beam runs.** The candidate law above is almost
certainly FALSE from N = 16 onwards, and the "integral tightness" reading of it must not be used.
Two independent search engines -- simulated annealing (300k iterations, four seeds) and beam search
seeded from all 2244 graphs on 13 vertices with bip >= 5, at beam width 8000 with every C5 blow-up
injected at every order -- both stop at a(16) >= 9 and a(17) >= 10, one below floor(256/25) = 10
and floor(289/25) = 11 respectively, while both reach floor exactly at N = 15 and N = 18. Since
R1-C7 proves a(16) <= 10 and a(17) <= 11 outright, the live possibilities are a(16) in {9,10} and
a(17) in {10,11}, and the search evidence points to the lower value in each case. Structurally this
is what one should expect: N^2/25 is attained only when 5 divides N, where the balanced blow-up
realises it, and there is no reason for a(N) to reach the integer floor at other orders. The
targeting argument I built on the "least slack" reading (orders N = +-1 mod 25) is therefore
weaker than stated, quite apart from being superseded by R1-C7, which proves those orders outright
for N <= 40.

---

## 2. R1-C1 — the naive vertex-deletion induction is FALSE (obstruction, exact)

**Statement.** The conjecture cannot be proved by the induction step
bip(G) <= bip(G - v) + (N^2 - (N-1)^2)/25 = bip(G - v) + (2N-1)/25
at a suitably chosen vertex, because the step fails at *every* vertex of the extremal family.

**Proof.** Let N = 5n and consider the balanced blow-up C5[n], with bip(C5[n]) = n^2. Deleting
any vertex leaves the blow-up with parts (n,n,n,n,n-1). For a C5 blow-up with parts
(n_1,...,n_5) the maximum cut is attained by a partition constant on parts, so
bip = min_i n_i n_{i+1}; for (n,n,n,n,n-1) that minimum is n(n-1). Hence
bip(C5[n]) - bip(C5[n] - v) = n^2 - n(n-1) = n exactly, for every vertex v, while the budget is
(2N-1)/25 = (10n-1)/25 < (2/5)n + 1. The step therefore fails for every n >= 1, asymptotically
by the factor 5/2.

**Verification.** Exhaustive over all vertices for n = 1,2,3 with exact brute-force maxcut
(`claude_verify_a12.py`, section 3): drops 1, 2, 3 against budgets 9/25, 19/25, 29/25 -- all
three violated. (The claim that the blow-up maximum cut is constant on parts is not assumed:
the drops were computed by exhaustive enumeration of all 2^(N-1) cuts of the deleted graph.)

**Consequence.** Any induction on N must carry a potential Phi >= bip that is tight on C5[n] and
absorbs a per-vertex drop of order n, i.e. of order N. Family F4 must supply such a potential or
is blocked.

---

## 3. R1-C2 — extremal graphs are NOT always C5 blow-ups (structure, exact)

**Statement.** a(12) = 5, attained by exactly two graphs, `K?ABBBwerwBw` and `K?BD@g]Qvo^?`
(each 12 vertices, 25 edges, maxcut 20). Neither is a blow-up of C5. The best C5 blow-up on 12
vertices has bip = 4.

**Proof of the blow-up bound.** Write the parts of a C5 blow-up on 12 vertices as
(n_1,...,n_5) with sum 12; bip = min_i n_i n_{i+1}. If some n_i = 1 then bip <= n_i n_{i+1} <= 8
but then the remaining four parts sum to 11 and some cyclic pair has product at most 4 (checked
exhaustively). In general at least three parts have size <= 2, and the independence number of
C5 is 2, so two parts of size <= 2 are cyclically adjacent, giving min_i n_i n_{i+1} <= 4. The
value 4 is attained, e.g. at parts (2,2,2,2,4). All 38 part vectors up to rotation and
reflection were checked exactly (`claude_verify_a12.py`, section 2), with maximum cut computed
by exhaustive enumeration rather than by the constant-on-parts formula.

**Structure of the two extremal graphs.** First: degree sequence (5,5,5,5,4,4,4,4,4,4,3,3),
independence number 5, 52 five-cycles, twin classes of sizes (2,2,2,1,1,1,1,1,1). Second: degree
sequence (5,5,4,4,4,4,4,4,4,4,4,4), independence number 5, 51 five-cycles, twin classes
(2,1,1,1,1,1,1,1,1,1,1). Neither has the twin structure of a C5 blow-up (which would be five
classes covering all 12 vertices).

**Verification.** The complete census of all 1,144,061 connected triangle-free graphs on 12
vertices was run twice by two independently written programs (C++ and Python, different graph6
decoders, different maxcut loops); exactly two graphs reach bip = 5 and none reaches 6.

**Consequence, stated precisely.** This refutes "the maximiser of bip among triangle-free graphs
on N vertices is a blow-up of C5", hence refutes any *exact* reduction of a(N) to an
optimisation over blow-ups -- the Motzkin-Straus analogue that family F7 was asked to test. It
does **not** refute the inequality itself, since 5 < 5.76. Only a one-sided (upper-bound)
blow-up argument could survive, and that requires a separate mechanism.

---

## 3b. R1-C4 — the elementary C5-homomorphism mechanism does NOT reach the extremal graphs

**The elementary lemma.** If phi: V(G) -> Z_5 is a homomorphism to C5 (every edge has
phi-difference +-1), put n_j = |phi^{-1}(j)| and let E_j be the edges between classes j and j+1,
so |E_j| <= n_j n_{j+1}. For each i the cut A_i = phi^{-1}({i, i+2}) has exactly |E_{i+3}|
monochromatic edges (inside A_i only difference-2 pairs could appear, and those are non-edges;
inside the complement only the (i+3, i+4) class survives). Hence
bip(G) <= min_i |E_i| <= min_i n_i n_{i+1} <= (prod_i n_i)^{2/5} <= ((N/5)^5)^{2/5} = N^2/25,
by AM-GM twice. So the conjecture is elementary for C5-colourable graphs.

**The obstruction.** Testing C5-colourability on the exact extremal graphs (own backtracking
homomorphism search, `claude_extremal_structure.py`):

| N | extremal graph | chi | alpha | odd girth | hom -> C5 |
|---|---|---|---|---|---|
| 12 | `K?ABBBwerwBw` | 3 | 5 | 5 | **no** |
| 12 | `K?BD@g]Qvo^?` | 4 | 5 | 5 | **no** |
| 13 | `L??ED@_~?~^_Fw` and 3 siblings | 3 | 6 | 5 | yes |
| 13 | `L?`DAboU...` family (4 graphs) | 3 or 4 | 4 or 5 | 5 | **no** |
| 14 | `M?AE@bH{AYN_LgBs?` | 4 | 5 | 5 | **no** |

Both extremal graphs at N = 12 and the extremal graph at N = 14 fail to be C5-colourable, and
two of them are not even 3-colourable. So the tight cases at non-multiples of five lie exactly
outside the reach of the elementary mechanism. Combined with the known theorem of Jin
(triangle-free with min degree > 10N/29 admits a homomorphism to C5), the hard region is the
low-minimum-degree, high-chromatic one, and it contains extremal examples. Family F3 must
supply a mechanism for non-C5-colourable graphs; the Z_5 route alone cannot close the conjecture.

**A Ramsey connection.** The graph `L?`DE`gl@YJODg` (N = 13, bip = 6 = floor(169/25)) is
4-regular with 26 edges, independence number 4 and chromatic number 4 -- the parameters of the
unique (3,5)-Ramsey graph on 13 vertices, the circulant C_13(1,5). The circulant sweep below
confirms it: the best triangle-free circulant on Z_13 is S = {2,3}, which is isomorphic to
C_13(1,5) under multiplication by 7, and it attains bip = 6. At N = 14 the extremal graph has
independence number 5, the minimum possible for a triangle-free graph on 14 vertices since
R(3,5) = 14. So the extremal family for a(N) at non-multiples of five meets the
Ramsey-critical triangle-free graphs.

---

## 3c. R1-C5 — exhaustive exact sweep of all triangle-free circulant graphs, n <= 24

Every circulant on Z_n, i.e. every symmetric connection set S subset {1..n/2}, was built,
tested for triangles, and its maximum cut computed EXACTLY by Gray-code enumeration of all
2^(n-1) bipartitions (`claude_circulant_sweep.cpp`). This family is a natural target: it
contains both the extremal blow-ups (C5[k] is the circulant on Z_{5k} with S = {d : d = +-1 mod 5})
and the cyclic Ramsey graphs.

**927 triangle-free circulants scanned for 5 <= n <= 24; ZERO violations of 25 bip <= n^2.**

| n | 5 | 10 | 15 | 20 | 12 | 13 | 14 | 16 | 17 | 18 | 19 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| max bip over circulants | **1** | **4** | **9** | **16** | 4 | **6** | 6 | 8 | 9 | 10 | 11 | 15 | 16 | 16 | 18 |
| n^2/25 | 1.00 | 4.00 | 9.00 | 16.00 | 5.76 | 6.76 | 7.84 | 10.24 | 11.56 | 12.96 | 14.44 | 17.64 | 19.36 | 21.16 | 23.04 |

The bound is attained **exactly at the multiples of five**, in every case by the C5 blow-up:
the maximising connection sets S = {1}, {2,3}, {1,4,6}, {2,3,7,8} are, respectively, C5, and
graphs isomorphic to C5[2], C5[3], C5[4] (multiplication by 3 mod n carries them to the canonical
form S = {d : d = +-1 mod 5}). At every non-multiple of five the best circulant falls strictly
short of floor(n^2/25), and increasingly so (at n = 24 the best circulant gives 18 against 23).

Consequence: circulants are extremal exactly at multiples of five and nowhere else, so the
extremal structure at non-multiples -- which by R1-C3 still attains floor(n^2/25) -- is
genuinely non-circulant and non-blow-up. Any proof tight at every order must reproduce that
structure.

---

## 3d. R1-C6 — the low-degree reduction (LEMMA, complete proof)

**Lemma.** Let G be a graph on N vertices and v a vertex with
d(v) <= (4N-2)/25. If bip(G - v) <= (N-1)^2/25, then bip(G) <= N^2/25.

**Proof.** Take a bipartition of G - v attaining bip(G - v) monochromatic edges, and place v on
whichever side contains fewer of its neighbours; that side contains at most floor(d(v)/2) of
them, and every other monochromatic edge is unchanged. Hence
bip(G) <= bip(G - v) + floor(d(v)/2). Now
floor(d(v)/2) <= d(v)/2 <= (2N-1)/25 = N^2/25 - (N-1)^2/25,
so bip(G) <= (N-1)^2/25 + (N^2 - (N-1)^2)/25 = N^2/25. (Triangle-freeness is not needed.) []

**Corollary (minimal counterexample has large minimum degree).** If the conjecture fails, then
among the counterexamples of least order N every vertex satisfies
d(v) > (4N-2)/25, i.e. delta(G) > (4N - 2)/25, which is just above 0.16 N.

**Sharpened finite form, used below.** If a(N-1) = A is known exactly, then bip(G) >= B for a
graph G on N vertices forces floor(d(v)/2) >= B - A at every vertex, i.e.
delta(G) >= 2(B - A). With the exact values proved above this gives concrete, checkable
restrictions; for instance a violation at N = 16 needs bip >= 11, and a(15) = 9, so every vertex
of such a graph has degree at least 4. That is what makes a restricted exact census at N = 16
conceivable where the full census (about 10^11 graphs) is not.

Note this lemma is elementary and certainly known; it is recorded here because it is proved in
full, it is load-bearing for the min-degree census route, and it fixes the exact constant 4/25
rather than an asymptotic one.

---

## 3e. Search-engine calibration and what it does and does not show

Two independent search engines were built and validated against the exact censuses:

* **Simulated annealing** over triangle-free graphs with exact bip as objective
  (`claude_hunt.cpp`). At N = 13 it reaches the true optimum bip = 6 within 1235 iterations.
* **Order-by-order beam search** (`claude_beam.cpp`, `claude_beam2.cpp`): from a beam of graphs
  at order n it generates EVERY one-vertex extension exactly -- the new vertex's neighbourhood
  must be an independent set, or a triangle appears -- scores each by exact bip, and keeps the
  best. Seeded from all 2244 graphs on 13 vertices with bip >= 5, it reproduces
  a(14) = 7 and a(15) = 9 exactly; the latter is an independent confirmation of the published
  value a(5n) = n^2 at n = 3.

Lower bounds obtained beyond the census range: a(16) >= 9, a(17) >= 10, a(18) >= 12 = floor(324/25).

**These are lower bounds only.** They do NOT show that a(16) < 10. The beam falls one short of
floor(N^2/25) at N = 16 and 17 but reaches it at N = 18, which is consistent with the beam simply
being weak at some orders. The honest statement is: a(N) = floor(N^2/25) is PROVED for
4 <= N <= 14 except N = 9, and is neither proved nor refuted for N >= 16.

**A structural by-product.** Beaming from the two exact extremal graphs at N = 12 alone reaches
only bip = 5 at N = 13, below a(13) = 6. So no one-vertex extension of an N = 12 extremal graph
is extremal at N = 13: the extremal graphs at consecutive orders are not nested. Any inductive
construction of the extremal family must therefore rebuild it, not extend it.

**Exact decision is currently out of reach at N = 16.** A CP-SAT model with all 2^(N-1) cut
constraints and degree-ordering symmetry breaking decides small cases correctly (at N = 8 it
returns UNSAT for t = 3, matching a(8) = 2) but returns UNKNOWN at N = 13 for t = 7 after 120
seconds; the CEGAR variant with lazily added cuts is likewise far from converging. Proving
a(16) < 10 is therefore not reachable with this model, and the min-degree census of R1-C6 is the
live alternative.

---

## 3f. R1-C7 — THE BLOW-UP IDENTITY AND ITS TWO CONSEQUENCES (gate: CONFIRMED)

Round 1 produced this independently in five of the eight families; I re-derived and re-verified it
myself before accepting it (`claude_gate_blowup.py`).

**Lemma (blow-up identity).** For every graph H and every integer t >= 1,
bip(H[t]) = t^2 bip(H), where H[t] is the balanced blow-up.

**Proof.** Split class i as a_i vertices on side 0 and t - a_i on side 1. The number of
monochromatic edges is sum over ij in E(H) of [a_i a_j + (t - a_i)(t - a_j)]. As a function of a_i
alone this equals a_i * A + (t - a_i) * B with A = sum_{j~i} a_j and B = sum_{j~i} (t - a_j):
affine, because a class is independent so no a_i^2 term arises. An affine function on the box
[0,t]^{V(H)} attains its minimum at a vertex, so some maximum cut is constant on classes; for
class-constant cuts the monochromatic count is exactly t^2 times that of the corresponding cut of
H. []

**Verification.** Brute force over all graphs on 4, 5, 6 vertices with t = 2 and all graphs on
4, 5 vertices with t = 3, computing bip of the blow-up by exhaustive enumeration of all 2^(N-1)
bipartitions: 246 (graph, t) pairs, 0 mismatches.

### Consequence 1 — the conjecture is PROVED for every N <= 40, not only for multiples of five

Since a(5N) >= 25 a(N) (blow up an extremal N-vertex graph by t = 5) and the published theorem
gives a(5m) = m^2 for every m <= 40 (arXiv:2606.28041), we get for every N <= 40

        25 a(N) <= a(5N) = N^2,      i.e.      a(N) <= N^2/25.

The published paper states only the multiples of five; this closes the 32 non-multiples below 40
as well, at no extra cost. It also subsumes my exact censuses for N <= 14 (which remain valuable
as ground truth and as the source of the extremal structure, but are no longer needed for the
inequality).

**This retires the counterexample targets I had selected.** N = 16, 17, 18, 19, 21, 22, 23, 24, 26
are all <= 40 and therefore settled; the hunt at N = 24 and N = 26 was searching already-proved
ground. Correction recorded.

**The live region is N > 40 with 5 not dividing N** (for such N the smallest usable multiple is
5N > 200, beyond the published range). The tightest of those by remaining slack frac(N^2/25) = 0.04
are N = 49, 51, 74, 76, 99, 101, 124, 126, 149, 151, 174, 176, 199.

### Consequence 2 — there is no asymptotic slack, so every threshold route is vacuous

If a(N0) > N0^2/25 for some N0, then a(t N0) >= t^2 a(N0) > (t N0)^2/25 for every t, so violations
recur at arbitrarily large orders. Hence for every N0,

        "a(N) <= N^2/25 for all N >= N0"   is equivalent to   "a(N) <= N^2/25 for all N >= 1".

Consequently c := lim a(N)/N^2 exists and equals sup_N a(N)/N^2 (Fekete, via supermultiplicativity
of a(N)/N^2 along multiples), the conjecture is exactly the statement c <= 1/25, and:

  * **the effective-threshold route (family F1) is BLOCKED at its premise** -- there is no N0 whose
    tail is easier than the whole problem, so "prove it for N >= N0 and check below" cannot be a
    strategy;
  * conversely every asymptotic bound upgrades verbatim to every finite N, so the
    Balogh-Clemen-Lidicky bound holds at every N with N0 = 1, and any counterexample must have
    edge density strictly inside their window at every order;
  * exact computation of a(N) on any finite range can never contribute to a PROOF (a finite set of
    terms never bounds a supremum). It can only ever disprove. This is the precise sense in which
    GOAL rule (d) is not merely a convention but a theorem.

---

## 4. Blocked-route ledger after these results

| route | status | blocking lemma / falsifier |
|---|---|---|
| R52/R53 soft pivot | BLOCKED | terminal lemma has strength >= the conjecture (verbatim above) |
| naive vertex-deletion induction | DEAD | R1-C1: the step is false on C5[n] for every n |
| exact blow-up reduction for a(N) | DEAD | R1-C2: a(12) = 5 > 4 = best C5 blow-up on 12 vertices |

Inherited dead routes (never re-tread unchanged): bare shortest-support Hall/SSE; R55/R57
branch-to-prefix extraction; aggregate token counting without a graph incidence map;
FullBankGlobalPackage consumers used as providers; abstract LP/Farkas shells lacking the
restricted almost-squeeze existence theorem; spectral cycle-Hardy, rho(K2) <= N, CSM-SPEC;
fixed-tuple linear-algebra imitation of the CDC handshake. Falsifiers on record in
`ERDOS23_FINAL_HANDOFF_20260712.md` section 8.

---

## 5. Artifacts

- `claude_exact_bip.cpp` — exact census engine (graph6 in, Gray-code maxcut, exact integers).
- `claude_verify_a12.py` — independent verification of a(12), the blow-up bound, and R1-C1.
- `claude_identify_n12.py` — independent full re-census at N=12 with structural invariants.
- `n13.out`, `n14_*.out` — raw census logs.
- `run_lane14.cmd` — 16-lane residue-split driver for N = 14.
