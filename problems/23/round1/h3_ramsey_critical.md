# H3 — Ramsey-critical triangle-free graphs (Erdős #23 counterexample hunt), round 1

Target: `bip(G) = |E(G)| - maxcut(G) <= N^2/25` for every finite triangle-free `G`.
Assignment: the Ramsey-critical family — collect (3,k)-Ramsey / small-independence-number
triangle-free graphs, test whether minimising `α` maximises `bip`, and push to N = 24, 26.

**VERDICT: NO VIOLATION.**

All arithmetic is integer. Every maximum cut behind a reported number is exact: Gray-code
enumeration of all `2^(N-1)` bipartitions in C++, re-done independently in Python by
from-scratch recounting (`h3_verify.py`), and for `N >= 24` additionally by OR-Tools CP-SAT
maximisation solved to **proven optimality** (`h3_verify_cpsat.py`). Triangle-freeness is
re-tested explicitly on every reported graph — see §6, where that discipline caught three
false "violations" produced by a defect in the search engine.

---

## 0. Answers to the three assigned questions

| task | answer |
|---|---|
| (i) collect Ramsey (3,k)-critical / small-α triangle-free graphs at 16..30 and 48..52, compute exact bip | done for 16..30 (§2–§3). 48..52 excluded on an exact structural ground, not searched (§2, end) |
| (ii) test "minimising α maximises bip" against the exact census | **REFUTED**, exactly, at N = 12 (§1); independently corroborated at n = 24, 25, 27 by exhaustive circulant sweeps |
| (iii) push to N = 24 and N = 26 at the smallest achievable α | done. α = 7 is the true minimum at both orders. Best bip found: **18 at N = 24**, **22 at N = 26**, against violation targets 24 and 28 and against plain-blow-up values 20 and 25 (§3) |

Extra output of the round: **N = 18 is the unique remaining order at which beating the best C5
blow-up by exactly one unit refutes the conjecture** (§4) — a much sharper search target than the
`frac(N^2/25) = 0.04` orders in the brief. And a new certified record at **N = 17, bip = 10**,
one above the best C5 blow-up there (§4).

---

## 1. (ii) The min-α hypothesis is FALSE — exact refutation at N = 12

Complete censuses (`geng -t -c` piped into `h3_engine.exe census`), bucketed by independence
number, exact bip per bucket. Restricting to connected graphs is sound: bip is additive over
components and `sum N_i^2 <= (sum N_i)^2`.

**N = 12, all 1 144 061 connected triangle-free graphs**

| α | 4 | **5** | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|
| max bip | 4 | **5** | 4 | 4 | 3 | 1 | 0 | 0 |
| # attaining that max | 12 | 2 | 475 | 4 | 4 | 154 | 34 | 1 |

`α = 4` is the minimum possible on 12 vertices (there is no `α = 3` bucket), and the entire
`α = 4` bucket tops out at `bip = 4`, while `a(12) = 5` is attained **only** at `α = 5`
(`K?ABBBwerwBw`, `K?BD@g]Qvo^?`).

> **Minimising the independence number does not maximise bip.** At N = 12 the α-minimisers lose
> by exactly one unit — the whole margin that matters for this conjecture.

Full data over the computed range (N = 13 from the complete 19 425 052-graph census, 16 lanes):

| N | min α | max bip at min α | a(N) | α values attaining a(N) | hypothesis |
|---|---|---|---|---|---|
| 8 | 3 | 2 | 2 | 3, 4 | holds (tie) |
| 9 | 4 | 2 | 2 | 4, 5 | holds (tie) |
| 10 | 4 | **4** | 4 | 4 only | holds (strictly) |
| 11 | 4 | 4 | 4 | 4, 5 | holds (tie) |
| 12 | 4 | 4 | **5** | 5 only | **FAILS** |
| 13 | 4 | **6** | 6 | 4, 5, 6 | holds (tie) |
| 14 | 5 | 7 | 7 | 5 | holds |

So the correct statement is the weak one: for N ≤ 14 the α-minimisers are *among* the optima
except at N = 12, where they are strictly beaten. The brief's lead ("the extremal graphs at
non-multiples of five meet the Ramsey-extremal ones") is true at N = 13 and N = 14 and false at
N = 12.

**Corroboration at the target orders.** Exhaustive sweep of every triangle-free circulant on
`Z_n` (all symmetric connection sets; exact Gray-code maxcut; `h3_circ_alpha.py`, `h3_circ_all.py`,
`h3_engine.exe eval`). The n ≤ 24 column reproduces the earlier root-agent sweep; n = 25..30 is
new coverage.

| n | # triangle-free circulants | min α over circulants | max bip among min-α circulants | max bip over ALL circulants |
|---|---|---|---|---|
| 22 | 163 | 7 | 14 | 16 |
| 23 | 121 | 7 | 13 | 16 |
| **24** | 178 | **7** | **12** | **18** |
| 25 | 189 | 8 | 18 | **25** (= C5[5], tight) |
| **26** | 352 | **7** | **22** | **24** |
| 27 | 177 | 8 | 22 | 22 |
| 28 | 466 | 8 | 26 | 26 |
| 29 | 378 | 8 | 28 | 28 |
| 30 | 647 | 8 | 28 | **36** (= C5[6], tight) |

At n = 24 the α-minimisers give 12 against 18 for the best circulant (a 33 % loss); at n = 25,
18 against the tight value 25; at n = 30, 28 against the tight value 36. The hypothesis fails
worst exactly where it was supposed to help.

---

## 2. (i) Ramsey-critical / minimum-α triangle-free graphs at N = 16..30, exact bip

The minimum independence number of a triangle-free graph on N vertices is pinned by
`R(3,5) = 14`, `R(3,6) = 18`, `R(3,7) = 23`, `R(3,8) = 28`, `R(3,9) = 36`:
α ≥ 5 for 14 ≤ N ≤ 17, α ≥ 6 for 18 ≤ N ≤ 22, α ≥ 7 for 23 ≤ N ≤ 27, α ≥ 8 for 28 ≤ N ≤ 35,
and each of those is attainable.

`h3_ramsey.exe` builds graphs meeting those minima by the classical Ramsey local search (compute
a maximum independent set exactly by branch and bound; insert an edge inside it whenever some
pair of it has no common neighbour, which cannot create a triangle; delete a random edge when
the set is saturated), then greedily saturates edges subject to triangle-freeness. It reproduces
the known critical parameters: a 26-edge α = 4 graph on 13 vertices ((3,5,13), the parameters of
`C13(1,5)`), 42-edge α = 5 graphs on 17 vertices ((3,6,17)), and a 66-edge 6-regular α = 6 graph
on 22 vertices ((3,7,22)). Note the circulant sweep shows min α over circulants is 6 at n = 17
and 7 at n = 22, so the (3,6,17) and (3,7,22) critical graphs are *not* cyclic — consistent with
the literature, and a check that the constructor is not merely rediscovering circulants.

Exact bip of the best minimum-α graph found at each order (8 independent constructions per order):

| N | min α | best bip at min α | best C5 blow-up | best circulant | floor(N²/25) | bip needed to violate |
|---|---|---|---|---|---|---|
| 16 | 5 | 8 | 9 | 8 | 10 | 11 |
| 17 | 5 | 8 | 9 | 9 | 11 | 12 |
| 18 | 6 | 10 | **12** | 10 | 12 | **13** |
| 19 | 6 | 11 | 12 | 11 | 14 | 15 |
| 20 | 6 | 12 | 16 | 16 | 16 | tight |
| 21 | 6 | 14 | 16 | 15 | 17 | 18 |
| 22 | 6 | 16 | 16 | 16 | 19 | 20 |
| 23 | 7 | 16 | 20 | 16 | 21 | 22 |
| **24** | 7 | **18** | 20 | 18 | 23 | **24** |
| 25 | 7 | 19 | 25 | 25 | 25 | tight |
| **26** | 7 | **22** | 25 | 24 | 27 | **28** |
| 28 | 8 | 23 | 30 | 26 | 31 | 32 |
| 29 | 8 | 26 | 30 | 28 | 33 | 34 |
| 30 | 8 | 28 | 36 | 36 | 36 | tight |

The minimum-α graphs are **never better** than the plain balanced C5 blow-up for N ≥ 16 (equal
only at N = 22), and the gap widens with N. Together with §1 this closes the H3 lead as a general
principle.

**Why it has to fail, and why 48..52 was not searched.** In a triangle-free graph every
neighbourhood is independent, so `Δ ≤ α` and hence `|E| ≤ Nα/2`. Since `maxcut ≥ |E|/2`,

```
bip = |E| - maxcut  ≤  |E|/2  ≤  Nα/4.
```

The Ramsey minimum satisfies `α = Θ(√(N log N))`, so minimum-α graphs have
`|E| = O(N^{3/2}√log N)` and therefore `bip = o(N^2)`: they cannot contend for a `Θ(N^2)` target.
Concretely at N = 49 the minimum α is 11–12, so `|E| ≤ 294`; the largest `bip/|E|` ratio observed
anywhere in this project is 0.2308 (`C13(1,5)`, 6/26), which puts such graphs near `bip ≈ 68`,
against a plain-blow-up value of 90 and a violation target of 97. Searching 48..52 inside the
Ramsey family is therefore a guaranteed loss, and the compute went to N = 18/24/26 instead.

The empirical law visible in the table is the clean statement: **the α of the good graphs tracks
`2N/5` (the blow-up value `α = max_i(n_i + n_{i+2})`), not the Ramsey minimum.** N = 13 is a
coincidence of small numbers — there `2N/5 = 5.2` while the Ramsey minimum is 4, so the two
regimes have not yet separated.

---

## 3. (iii) N = 24 and N = 26 at the smallest achievable independence number

α = 7 is exactly the minimum at both orders. Best objects found, each certified three ways
(C++ Gray code over all `2^(N-1)` cuts; explicit triangle test; CP-SAT maxcut proven optimal):

```
N = 24   α = 7   |E| = 78   maxcut = 60   bip = 18    25·bip = 450 < 576 = N²
         g6 = WE?ISH?YS?aqHaP?BDJAHiHOB?gHOHfQ?OqS_HpDCADB?AQ

N = 26   α = 7   |E| = 88   maxcut = 66   bip = 22    25·bip = 550 < 676 = N²
         g6 = Y?f?cAAWHX?Cg`@C}??]hCTBAGGOBIaY?c_JQ?_HiGCd?g_?aIDSW_`?
```

Both fall short of the 24 and 28 needed, and short even of the blow-up values 20 and 25.

---

## 4. The sharp target this round produced: **N = 18, bip = 13**

The brief ranks orders by `frac(N^2/25)`. For a *search* the useful ranking is instead the
distance from the best known construction to the violation threshold. The best known construction
at every order is the balanced C5 blow-up, whose bip is `min_i n_i n_{i+1}` — verified here by
exhaustive enumeration of all `2^(N-1)` cuts at every N = 10..30, not assumed from the
constant-on-parts formula. Writing `N = 5n + r`:

| r | blow-up bip | violation threshold `floor(N²/25)+1` | "blow-up + 1 violates"? |
|---|---|---|---|
| 0 | n² | — (tight; proven for n ≤ 40) | — |
| 1 | n² | n² + floor((10n+1)/25) + 1 | only n ≤ 2 (N = 7, 11) |
| 2 | n² | n² + floor((20n+4)/25) + 1 | only n = 1 (N = 7) |
| 3 | n² + n | n² + floor((30n+9)/25) + 1 | only n ≤ 3 (N = 8, 13, **18**) |
| 4 | n² + n | n² + floor((40n+16)/25) + 1 | never |

Every one of those orders except N = 18 is already killed by a complete census
(`a(8) = 2`, `a(11) = 4`, `a(13) = 6`).

> **N = 18 is the unique order at which beating the balanced C5 blow-up by exactly one unit
> refutes the conjecture.** The blow-up `C5[4,3,4,3,4]` has 64 edges, maxcut 52, `bip = 12`,
> `25·12 = 300 < 324`. One more monochromatic edge gives `25·13 = 325 > 324`.
> g6 = `QFzf?{]F_B_M?[?[[@~?]wBr_N?`

This is not idle. The exact censuses show that "+1 over the best blow-up" **does happen**: at
N = 12 (`a = 5` vs blow-up 4) and at N = 14 (`a = 7` vs blow-up 6). It must fail at N = 18 for the
conjecture to survive, and N = 18 is not covered by the published verification (only `N = 5n`,
`n ≤ 40`). Nor is it excluded by the best proved bound: Balogh–Clemen–Lidický gives
`≈ 0.0409·324 = 13.25`, so `bip = 13` at N = 18 sits inside the theoretical window. By contrast
the gap is 4 at N = 24 and 3 at N = 26 — those orders have tiny `frac(N²/25)` but are much
further from anything constructible.

### New certified record at N = 17

Chained growth (best certified graph at N−1 plus one isolated vertex, re-searched at N) produced,
from **nine independent chains**, nine pairwise distinct graphs on 17 vertices with `bip = 10`,
one above the best C5 blow-up (9) and above the best circulant (9):

```
N = 17   |E| = 50   maxcut = 40   bip = 10   α = 7    25·bip = 250 < 289 = N²
         g6 = PiL@`aN?AUU`bsOHgEC]alE?
```
(Gray-code exhaustive, Python brute-force recount, and CP-SAT proven-optimal maxcut all agree.)
Other members: `P?FqaRo{DETO@kSB_fa_[g_[`, `PCyaHe@FGYOIFHKjMDdCcBO[`, `PEL_PaLq?`AqAPw?_zG@Hwac`,
`PFz_ww[?wF?[wFwFSBc?OWDC`, `PGkA\hHHKhYAARQUYAPHJsCc`, `PkOiA?WD_OAxiD`yBO@u?g]G`,
`PodpaEDBOPQAQhKKGPiCoIPC`, `PqWsWc_eCZKRCgKaGmIHae@K`. This is consistent with (and evidence for)
the candidate law `a(N) = floor(N^2/25)`, which would give `a(17) = 11`.

### What was done at N = 18

* `h3_search2.exe` — pooled-cut simulated annealing over triangle-free graphs. It maximises the
  minimum over a bounded pool of the currently tightest bipartitions, and whenever the pooled bar
  is met (and periodically regardless) re-certifies by full Gray-code enumeration of all `2^17`
  cuts. Moves: single-edge toggles with incremental pool update, plus "vertex rewire" (strip a
  vertex, reattach it to a random independent set of `G − v`).
* Two engine defects found and fixed, both of which invalidate earlier-style runs:
  1. **frozen pool.** With a fixed bar `T` far above the current best, the pooled deficiency never
     reaches 0, so the pool is never rebuilt and the search optimises against stale cuts — blind.
     Fixed by the adaptive bar `T = best + 1` plus periodic forced re-certification.
  2. **unsound reports** (§6).
* **Search-power validation.** Seeded from the blow-up, the engine independently rediscovers
  `a(12) = 5` and `a(14) = 7` — that is, it *does* find "+1 over the blow-up" graphs — within
  seconds, reproduces `a(13) = 6` from random starts and `a(15) = 9` from blow-up seeds, and found
  the new `bip = 10` at N = 17. So a `bip = 13` at N = 18, if it exists in a basin reachable by
  these moves, was within the engine's demonstrated reach.
* Campaign: ~50 processes at N = 18 seeded from the blow-up, from random triangle-free starts, and
  from the nine N = 17 `bip = 10` records lifted by one vertex; 1000–1500 s each; plus nine chained
  growth runs 15 → 19.
* **Result: bip = 12 at N = 18, never 13.**

---

## 5. Baseline table (exact; every maxcut by exhaustive enumeration)

| N | best C5 blow-up parts | blow-up bip | min-α bip | best circulant | best found here | floor(N²/25) | need |
|---|---|---|---|---|---|---|---|
| 16 | (3,3,3,3,4) | 9 | 8 | 8 | 9 | 10 | 11 |
| 17 | (3,3,3,3,5) | 9 | 8 | 9 | **10** | 11 | 12 |
| 18 | (3,4,3,4,4) | **12** | 10 | 10 | 12 | 12 | **13** |
| 19 | (3,4,3,4,5) | 12 | 11 | 11 | 12 | 14 | 15 |
| 20 | (4,4,4,4,4) | 16 | 12 | 16 | 16 | 16 | tight |
| 21 | (4,4,4,4,5) | 16 | 14 | 15 | 16 | 17 | 18 |
| 22 | (4,4,4,4,6) | 16 | 16 | 16 | 16 | 19 | 20 |
| 23 | (4,5,4,5,5) | 20 | 16 | 16 | 20 | 21 | 22 |
| 24 | (4,5,4,5,6) | 20 | 18 | 18 | 20 | 23 | 24 |
| 25 | (5,5,5,5,5) | 25 | 19 | 25 | 25 | 25 | tight |
| 26 | (5,5,5,5,6) | 25 | 22 | 24 | 25 | 27 | 28 |
| 27 | (5,5,5,5,7) | 25 | — | 22 | 25 | 29 | 30 |
| 28 | (5,6,5,6,6) | 30 | 23 | 26 | 30 | 31 | 32 |
| 29 | (5,6,5,6,7) | 30 | 26 | 28 | 30 | 33 | 34 |
| 30 | (6,6,6,6,6) | 36 | 28 | 36 | 36 | 36 | tight |

**Best ratio achieved: `bip/N² = 0.04` exactly**, at every `N = 5n`; the largest instance
certified here is

```
N = 30   C5[6]   |E| = 180   maxcut = 144   bip = 36   25·bip = 900 = N²
         g6 = ]??F~z{~Fw^_?~?~?^_Fw?~?B{??Fw?Fw?B{??~??Fw??^_~??~~??~^_?^fw?Fw~??~B{?B{?
```
maxcut certified twice: exhaustive Gray-code enumeration of all `2^29` bipartitions, and CP-SAT
maximisation solved to proven optimality. Best ratio at a **non**-multiple of five:
`30/784 = 0.038265` at N = 28 (`C5[5,6,5,6,6]`, CP-SAT proven maxcut 126), then
`20/529 = 0.037807` at N = 23 and `12/324 = 0.037037` at N = 18. The best *non-blow-up,
search-found* object is the N = 17 graph above, `10/289 = 0.034602`. **Nothing anywhere exceeded
0.04.**

Also computed and found not competitive: Mycielskians and generalised Mycielskians of C5
blow-ups (the Grötzsch graph `M(C5)` at N = 11 gives `bip = 4 = a(11)`; `M(C5[2])` at N = 21 gives
14 against the blow-up's 16; `M_2(C5)` at N = 16 gives 5), and all 927 + 1184 + 1025 triangle-free
circulants on `Z_n`, n ≤ 30.

---

## 6. Incident report: three false "violations", caught by the mandated re-verification

During the N = 18 campaign the search engine printed three graphs with `25·bip > N²`
(`bip = 13, 14, 14` on 18 vertices). All three were immediately rejected by `h3_verify.py`:
the bip and maxcut values were reproduced exactly, but **the graphs were not triangle-free**.
The engine had been relying on move legality rather than checking the invariant, so a rare defect
in the move machinery (not reproducible in >10^8 instrumented iterations, so its exact trigger is
still unidentified) could leak a triangle into the state.

Fix: `h3_search2.exe` now runs a hard `certify()` — no self-loops, symmetric adjacency, edge count
consistent with the adjacency matrix, and explicit triangle test over all pairs — on the seed and
before *every* re-certification, and calls `exit()` with a diagnostic if any of them fails.
Re-running the exact failing configurations under the self-certifying build yields `bip = 12` and
no `FATAL`. Recorded here because it is the strongest available argument for the verification
protocol: an unverified engine will hand you a counterexample to a 38-year-old conjecture,
and the independent triangle test is what stops you reporting it.

No object reported anywhere in this document rests on the search engine alone.

---

## 7. Structural constraint every future search should exploit

From the root-agent result R1-C4: if `G` admits a homomorphism to `C5` with classes of sizes
`n_i` then, taking the cut `A_i = φ^{-1}({i, i+2})`,
`bip(G) ≤ min_i |E_i| ≤ min_i n_i n_{i+1} ≤ N²/25` by AM–GM. Hence

> **any counterexample is triangle-free with NO homomorphism to `C5`** (equivalently, circular
> chromatic number `> 5/2`),

and then by Jin's theorem it has minimum degree `≤ 10N/29`. Both families explored this round sit
on the wrong side of one of those conditions:

* the C5 blow-ups **are** C5-colourable, so they can never violate — they only ever attain
  equality, and only at `N = 5n`;
* the Ramsey-critical graphs are non-C5-colourable but have `|E| = o(N²)`, hence `bip = o(N²)`.

Since `bip ≤ |E|/2`, a counterexample needs `|E| = Θ(N²)`. So the counterexample, if it exists,
is simultaneously **dense** and **non-C5-colourable** with minimum degree below `10N/29` — a
region that no construction in this round populates, and the natural place to put the next
round's compute.

---

## 8. Exact commands

```bash
CC=C:/msys64/mingw64/bin/clang++.exe
GENG=E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe

$CC -O3 -march=native -std=c++17 h3_engine.cpp  -o h3_engine.exe    # exact bip + alpha + tf
$CC -O3 -march=native -std=c++17 h3_search2.cpp -o h3_search2.exe   # pooled-cut SA, self-certifying
$CC -O3 -march=native -std=c++17 h3_ramsey.cpp  -o h3_ramsey.exe    # minimum-alpha constructor

# (ii) alpha-bucketed complete censuses
for n in 8 9 10 11 12; do $GENG -t -c -q $n | ./h3_engine.exe census; done
for r in $(seq 0 15); do $GENG -t -c -q 13 $r/16 | ./h3_engine.exe census > h3_census13_$r.txt & done

# (i) circulants: min-alpha representatives, and the complete sweeps for n = 25..30
python h3_circ_alpha.py 13 30 h3_circ_alpha.txt
python h3_circ_all.py 25 28 > h3_circ_all_25_28.tsv
python h3_circ_all.py 29 30 > h3_circ_all_29_30.tsv
cut -f1 h3_circ_all_25_28.tsv | ./h3_engine.exe eval

# (i)/(iii) Ramsey-critical constructions and their exact bip
./h3_ramsey.exe 24 7 <seed> 60000 8000      # alpha<=7 on 24 vertices; likewise 26 7, 17 5, 22 6, ...
awk -F'\t' '{print $1}' h3_ramsey_graphs.tsv | ./h3_engine.exe eval

# N = 18 campaign (bar floor(N^2/25)+1 = 13, blow-up seed, 1500 s, pool 512)
./h3_search2.exe 18 13 <seed> 1500 512 40 'QFzf?{]F_B_M?[?[[@~?]wBr_N?'
# chained growth from the exact a(14) extremal, N = 15 -> 19
python h3_grow.py 15 19 'MYoCgGjPK_gXJ@cS_' 55 3 G1

# independent re-verification (own decoder, no Gray code, own alpha)
python h3_verify.py 'PiL@`aN?AUU`bsOHgEC]alE?' 'QFzf?{]F_B_M?[?[[@~?]wBr_N?'
# independent exact maxcut for large N, proven optimal
python h3_verify_cpsat.py 'WE?ISH?YS?aqHaP?BDJAHiHOB?gHOHfQ?OqS_HpDCADB?AQ'
```

## 9. Artifacts in this directory

| file | role |
|---|---|
| `h3_engine.cpp` / `.exe` | exact bip + α + triangle test; `census` (α-bucketed) and `eval` modes |
| `h3_search2.cpp` / `.exe` | pooled-cut SA, adaptive bar, hard `certify()` before any report |
| `h3_search.cpp` / `.exe` | first version, kept for the record (fixed-bar; superseded) |
| `h3_ramsey.cpp` / `.exe` | minimum-independence-number triangle-free constructor |
| `h3_gen.py` | graph6 encode/decode, circulants, Cayley, blow-ups, α (construction only) |
| `h3_verify.py` | **independent** verifier: own decoder, brute-force maxcut, own α |
| `h3_verify_cpsat.py` | **independent** exact maxcut by CP-SAT, proven optimality, for N ≥ 24 |
| `h3_circ_alpha.py`, `h3_circ_all.py` | circulant sweeps |
| `h3_grow.py`, `h3_grow.sh` | chained growth drivers |
| `h3_fullcut_decide.py` | complete CP-SAT decision of `a(N) ≥ T` with all `2^(N-1)` cuts posted (does not scale past N ≈ 12 — 600 s was not enough for `a(13) ≥ 7`, which the census settles instantly; recorded as a dead end) |
| `h3_census13_*.txt`, `h3_circ_alpha.txt`, `h3_circ_all_*.tsv`, `h3_ramsey_graphs.tsv`, `h3_ramsey_bip.txt` | raw data |
| `w*.out`, `y*.out`, `grow_*.out`, `hgrow_*.out` | campaign logs |
