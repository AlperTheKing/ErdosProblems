# The 6-cut shore-exclusion machine (Theorem B material) — 2026-06-11

Referee status: full filter battery refereed VALID by cold GPT-5.5 thread
"Cold Review Adversarial Analysis" (c/6a29bd3c), reply 3. Two wording fixes folded
in below. Method assessed as "a new exact finite obstruction method"; the a=9
near-miss called "a real mathematical story, not just a black-box enumeration".

## Theorem B (current, after a=13)

In every 6-regular `(4,1)` graph, every nontrivial 6-edge-cut shore has size
**at least 14**. Consequently every 6-regular target on `n <= 27` is
super-6-edge-connected.

(a=14 status: the FIRST a=14 run was INVALID — geng silently truncated under
mod-110 splitting at n=14/e=39, no `>Z` terminator; see RESEARCH_LOG 2026-06-11.
A guarded mod-5500 wave rerun is in flight (~8e10 candidates, per-class `>Z` +
`total=` checks); only its result may be cited for shores >= 15 / n <= 29.
a <= 13 results are unaffected: n=13 chunk-0 and the full a=12 count were
re-verified against unsplit geng directly.)

## Setup (all conditions NECESSARY for a shore A, |A| = a)

- Edge count: `6a = 2e(A) + 6`, so `e(A) = 3a - 3` exactly.
- Connectivity (referee-fixed wording): if `G[A]` had components `A_1..A_t`, the
  cuts `∂(A_i)` are disjoint subsets of `∂A` with `|∂(A_i)| >= 6` each by
  `lambda(G) >= 6` (Skottová–Steiner Prop 5.1); their sizes sum to `|∂A| = 6`,
  forcing `t = 1`.
- `Delta(G[A]) <= 6`; deficiency `b(v) = 6 - d_A(v)` = number of cut edges at `v`;
  `0 <= b(v) <= 5` (b=6 would isolate `v` in `G[A]`); `sum b = 6`.

## Filters

- **[B]** deficiency range (above).
- **[C]** `G[A]` 3-colourable, and for EVERY proper 3-colouring the
  deficiency-weighted boundary vector `s_i = sum of b(v) over colour class i`
  (= cut-matrix row sums, independent of the B-side colouring) lies, AS A SORTED
  MULTISET (colour-permutation canonical), in
  `{(6,0,0), (3,3,0), (4,1,1), (2,2,2)}` [Theorem 4.3 row sums].
- **[T]** no nonadjacent `u, v` with `b(u) = 0` and `N_A(u) ⊆ N_A(v)`
  (folklore: no comparable nonneighbours in a vertex-critical graph; `b(u) = 0`
  localizes `N_G(u) = N_A(u)`).
- **[K] Boundary-shortfall lemma** (referee: "the strongest part of the machine";
  name suggested by referee): for every `v ∈ A` there must EXIST a proper
  3-colouring `psi` of `G[A] - v` with
  `sum_i max(0, 2 - cnt_i) <= b(v)`, `cnt_i = #{u ∈ N_A(v) : psi(u) = i}`.
  Necessity: `chi(G-v) = 3` gives `phi` proper on `G-v`; Lemma 1.1 + no-critical-
  edge forces `cnt_i + out_i >= 2` per colour where `out_i` counts `v`'s outside
  cut-neighbours coloured `i`; so `max(0, 2-cnt_i) <= out_i`, summing gives the
  bound; `psi = phi|_{A-v}`. (Referee verified the `b(v) >= 1` case explicitly:
  each outside neighbour contributes one unit to exactly one `out_i`.)

## Results (C++ `enum_shore.cpp`; a=9,10,11 independently re-verified in Python
`verify_shore_indep.py`, identical counts; a=9 kill additionally 3^8 brute-forced)

| a  | generated     | not 3-col     | fail [C]   | fail [T] | fail [K]  | survive |
|---:|--------------:|--------------:|-----------:|---------:|----------:|--------:|
| 9  | 729           | 711           | 9          | 8        | 1         | 0 |
| 10 | 18,655        | 18,345        | 197        | 86       | 27        | 0 |
| 11 | 696,208       | 687,377       | 6,013      | 1,300    | 1,518     | 0 |
| 12 | 32,833,744    | 32,484,081    | 241,863    | 27,322   | 80,478    | 0 |
| 13 | 1,839,349,287 | 1,822,133,664 | 11,944,366 | 788,481  | 4,482,776 | 0 |

Generator: native `geng -q -c -D6 a E:E` (E = 3a-3), nauty 2.8.9 clang-built,
validated against the SMS chain exactly (n=11,12,13 four-way counts + unique
graph). a=12 and a=13 ran as 110 res/mod chunk pairs.

## The a=9 near-miss (explain, don't bury — referee instruction)

The unique graph surviving [B]+[C]+[T] at a=9 is
`H = K_{3,3,3} - M` (g6 `HEzftz{`), `M` a rainbow perfect 3-matching (one missing
cross edge between each pair of colour classes, six distinct endpoints; the six
matching endpoints carry one cut edge each, the three full-degree vertices are
internal). `H` is colouring-rigid (6 proper colourings = one up to S3). [K] kills
it at each internal vertex `v ∈ {0,4,8}`: all six colourings of `H - v` leave some
colour with `<= 1` occurrences on `N(v)` — count 0 would 3-colour `G`, count 1
would give a critical edge.

For a=8 the kill is the clean hand proof: Turán equality forces `K_{3,3,2}` and
the size-2 part becomes a pair of false twins (impossible in a vertex-critical
graph).

## Certificates

- `experiments/sixreg/shore{9,10,11}_certs.txt`: per-graph fate for every
  [B]+[C] survivor (g6 + `fate=twins` or `fate=kill:v<i> b<def>` + ncol).
- Chunk outputs: `shore12_chunks/`, `shore13_chunks/` (110 summaries each).
- Code: `enum_shore.cpp` (filters + cert mode), `verify_shore_indep.py`
  (independent Python), `kill_9shore_survivor.py` + 3^8 brute force.

## Referee guardrails (do not overclaim)

- This does NOT nearly-solve Problem 5.2: a target could be n >= 15, 6-regular,
  super-6-edge-connected, locally Kempe-rigid, with no small 6-cut atom — the
  super-6-edge-connected core is untouched.
- lambda >= 6 is Skottová–Steiner; the contribution is the exact equality-case
  collapse of small 6-cut shores.
- Headline framing (referee): "Small 6-regular candidates for Dirac's k=4 problem
  are forced to be super-6-edge-connected."
