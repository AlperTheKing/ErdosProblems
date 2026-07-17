# Finite-certificate rescout — 2026-07-13

## Verdict

No genuinely unburned finite-certificate target survived the second-wave gate.
In particular, a new bounded run on #617, #993, or #647 is not defensible as an
"easy overlooked" attack.  #617 is the least crowded of the three on the public
site, but the local workspace shows that its direct computation was already
calibrated and parked as a months-to-years search.

This is a negative scouting result, not a claim about the truth of any problem.

## Scope and reproducibility

- Input: `C:\tmp\erdosproblems_current.yaml`
- SHA-256: `7108DC960B65C891AFD4C9555EF76D6607418B321A786A0457F863D75A7A2605`
- Entries whose current state is `falsifiable`: 27.
- Excluded as directed: #23, #106, #128, #458, #488, #699, #768, #835,
  and #885; #273 is stopped and is not in this status class.
- The remaining 21 entries were checked against their official page and thread:
  #64, #97, #107, #114, #167, #242, #287, #375, #398, #548, #583,
  #617, #628, #723, #743, #779, #982, #993, #1020, #1041, and #1082.
- Targeted local-history search found no problem directory for #617/#647/#993,
  but `handoff.md` and the top-level `search617/` directory contain extensive
  earlier work.  That older history is load-bearing and reverses the apparent
  public-site impression that #617 is fresh.

## Full remaining-list triage

| IDs | Gate result |
|---|---|
| #64, #167, #548, #583, #628, #723, #743, #1020 | Famous global graph/design conjectures.  A finite counterexample would settle each, but no bounded witness family has a theorem-level bridge or an untried small frontier.  #723 begins with the projective-plane order-12 barrier; #743 also has a 2024 claimed proof awaiting verification. |
| #97, #982, #1082 | Exact Euclidean-realizability constraints, not a finite combinatorial certificate unless a concrete coordinate construction is already in hand.  The #97 thread's proposed reduction to nine points depends on an explicitly challenged removable-vertex lemma. |
| #107 | The happy-ending conjecture; current upper bounds remain exponentially larger than the conjectured exact value. |
| #114 | Tao proves the claim for sufficiently large degree; certified computation on the thread covers through degree 14.  The remaining finite-but-unspecified gap is not one bounded exact test. |
| #242 | Erdős–Straus; verified through `10^18`.  Another finite range cannot resolve the universal statement. |
| #287 | Public exact search already explored 287,110,935 nodes for `n_1=12`; later certificates force any counterexample to enormous length.  Further finite exclusions have no closing bridge. |
| #375 | Grimm's conjecture; the official page notes consequences beyond Legendre-scale prime-gap control. |
| #398 | Brocard–Ramanujan; no extra solution is known below `10^9` in the factorial index. |
| #617 | First open case is the finite `r=5`, `K_26` coloring, but it is locally burned; details below. |
| #779 | Direct finite witness in principle, but verified through `n=1000` and the official heuristic predicts failures to be extraordinarily rare. |
| #993 | Direct tree witness in principle, but exhaustive through 29 vertices and heavily sampled through 101; details below. |
| #1041 | Forty-seven public comments and a continuous analytic parameter space; no small exact witness frontier emerged. |

## Requested comparison: #617 versus #993 versus #647

### #617 — finite and direct, but already burned locally

The exact affirmative certificate would be a 5-coloring of the 325 edges of
`K_26` such that every one of its 230,230 six-vertex subsets sees all five
colors.  Such a coloring would immediately disprove the original universal
statement at `r=5`; there is no surrogate bridge.

A naive exact one-hot SAT encoding has:

- `325 * 5 = 1,625` Boolean variables;
- `230,230 * 5 = 1,151,150` color-coverage clauses of length 15;
- 325 at-least-one and `325*C(5,2)=3,250` at-most-one clauses;
- 1,154,725 clauses in total.

Publicly, [the official page](https://www.erdosproblems.com/617) lists one
current worker and its thread contains no computation.  The primary source is
P. Erdős and A. Gyárfás, *Split and balanced colorings of complete graphs*,
Discrete Mathematics 200 (1999), 79–86,
[DOI 10.1016/S0012-365X(98)00323-9](https://doi.org/10.1016/S0012-365X(98)00323-9).
It states the `K_{r^2+1}` conjecture, proves `r=3,4`, and gives the affine-plane
`K_{r^2}` construction.  Targeted searches for the exact terminology located
no later primary paper resolving or computing `r=5`.

The local record is decisive:

- `handoff.md:50,60-80` marks #617 parked and records a months-to-years brute
  estimate.
- `handoff.md:67-70` records that the easier `K_17/r=4` calibration remained
  unknown after 41 minutes.
- `handoff.md:61` and `search617/gpt_r5_routes_synthesis.md` record 111 of 120
  `K_26/r=5` cubes timing out at 300 seconds.
- `search617/` already contains SAT, CP-SAT, local search, cube-and-conquer,
  affine perturbation, degree-matrix, design-theory, and flag-algebra work.

Therefore another bounded SAT run would repeat an executed formulation.  It is
not a fresh one-shot attack under the direct-proof guard.

### #993 — more crowded and much more exhaustively searched

[The official thread](https://www.erdosproblems.com/forum/thread/993) lists two
current workers and records exhaustive verification through 29 vertices.  At
order 29 alone, 5,469,566,585 unlabeled trees were checked with zero
unimodality failures; PatternBoost searches sampled trees through order 101,
again without a witness.  The thread links the exact artifacts at
[BrettRey/erdos-problem-993](https://github.com/BrettRey/erdos-problem-993).
It also cites Kadrawi–Levit's primary non-log-concavity result
[arXiv:2305.01784](https://arxiv.org/abs/2305.01784) and Ramos–Sun's later
AI-assisted sampling study [arXiv:2510.18826](https://arxiv.org/abs/2510.18826).

A search at order 30 is finite, but a zero result would only add one order and
would not settle the original statement.  Existing negative evidence gives no
reason to expect a witness there.  One bounded run is therefore not defensible.

### #647 — the cleanest certificate, but outside `falsifiable` and maximally burned

#647 is currently classified `verifiable`: a single integer `n>24` satisfying
the divisor inequalities would prove the requested existence statement.  It
was compared at the root agent's request even though it is outside this scout's
status filter.

[The official thread](https://www.erdosproblems.com/forum/thread/647) lists four
current workers.  It contains an independently checkable certificate excluding
all candidates through
`615,736,321,200,000,000` (`6.157...*10^17`), with verifier artifacts in
[the frontier-certificate repository](https://github.com/scottdhughes/erdos647-proof-chain/tree/main/frontier-certificate).
It also reports a direct segmented sieve through `10^12` and several modular
and prime-chain reductions.

Another bounded interval is exactly a cascade of finite exclusions with no
theorem closing existence or nonexistence.  The direct-proof guard rules it out.

## Concrete exact object: obstruction to the canonical #617 construction

The following is a proved obstruction, not a solution of #617.  It kills the
obvious attempt to extend the Erdős–Gyárfás affine-plane coloring by one vertex.
It was independently rederived in this scout and then found already recorded
in `search617/strategyC_designtheory_assessment.md`; no novelty is claimed.

**Lemma.** Let `q>=3` be a prime power.  Color the edges of the affine plane
`AG(2,q)` on `q^2` points with `q` colors by assigning `q-1` direction classes
individual colors and merging the remaining two direction classes into the
last color, as in Erdős–Gyárfás.  This coloring cannot be extended to a
coloring of `K_{q^2+1}` in which every `q+1` vertices see all `q` colors.

**Proof.** Add a proposed new vertex `v`.  For an individually colored
direction `c`, let `A_c` be the affine points whose edge to `v` has color `c`.
The color-`c` graph on the affine points is the disjoint union of the `q`
parallel lines of that direction, each a `K_q`.

Choose one point from each of those parallel lines.  The resulting `q` points
span no color-`c` edge.  Consequently every such transversal must meet `A_c`,
or those `q` points together with `v` form a `q+1` set missing color `c`.
If no whole parallel line lies in `A_c`, choose on each line a point outside
`A_c`; this is an unhit transversal.  Hence `A_c` contains a full line of
direction `c`.

There are at least two individually colored directions because `q>=3`.  Lines
from distinct directions meet in exactly one affine point, but the sets `A_c`
are pairwise disjoint because each edge from `v` has one color.  Contradiction.

For `q=5`, an independent exact enumeration checked all `5^4=625` choices of
one forced line in each of the four singleton directions.  Every pair of
different-direction lines intersect once, and the number of pairwise-disjoint
four-line choices is zero.  The executed output was:

```text
q= 5
line_choices= 625
pair_intersection_hist= {(0, 1): {1: 25}, (0, 2): {1: 25},
 (0, 3): {1: 25}, (1, 2): {1: 25}, (1, 3): {1: 25},
 (2, 3): {1: 25}}
pairwise_disjoint_4tuples= 0
```

The stronger local SAT family keeps the four singleton direction classes fixed
but allows the two merged directions and all 25 new-vertex edges to vary.  It
also returned exact `UNSAT` in 0.3 seconds:

- `search617/sat_617_affine.py` SHA-256
  `63D0FEA3BB4FA9B6C96505A0561A9615EA4328347FCDAAEEF9C1B966E629CE32`
- `search617/affine.out` SHA-256
  `D5BFCA0F1A32C0F599C5AD6D0B9F2124F96AF403F962F98DECCE146C1F407844`
- `search617/strategyC_designtheory_assessment.md` SHA-256
  `594B69000A90F091649F836E135E22FBDDBA0B6B22A4A49BC08B382B31F85C78`
- `search617/k26_r5_base.cnf` SHA-256
  `A79BAEE110C28FFBCEB6E6561FF3D03119E5A354E1D335CF9A316575793CB1CB`

This obstruction also explains why an affine warm start does not rescue the
already-calibrated full `K_26/r=5` search.  It does not constrain arbitrary
balanced colorings, so promoting it to a global argument would require exactly
the missing geometric-forcing/stability theorem identified in the local
assessment.  Pursuing that promotion would be a reformulation maze.

## Recommendation

Do not launch another #617/#993/#647 bounded run.  Preserve #617's reusable
encoding and exact verifier, but require a new theorem that collapses its full
search before resuming it.  The second wave found no finite-certificate target
that meets both conditions: genuinely unburned and directly capable of settling
the original statement in one bounded action.
