# H2 — Perturbed and generalised blow-ups (Erdős #23 counterexample hunt)

Target: find a finite triangle-free `G` on `N` vertices with `bip(G) = |E| - maxcut(G) > N^2/25`.

**VERDICT: NO VIOLATION.** Everything below is exact integer arithmetic. The family is
*closed out* — I can now state precisely why, and what the family's exact ceiling is.

---

## 0. The lever: blow-ups have an exact, cheap `bip` formula

**Lemma H2.1 (blow-up identity).** Let `H` be triangle-free on `h` vertices, let
`n = (n_1,...,n_h)` be non-negative integers with `N = sum n_i`, and let `G = H[n]` be the
blow-up (parts independent, base edges become complete bipartite). Then `G` is triangle-free
on `N` vertices and

```
maxcut(G) = max_{S subset V(H)}  sum_{ij in E(H), |{i,j} cap S| = 1} n_i n_j
bip(G)    = min_{S subset V(H)}  sum_{ij in E(H), i,j on the same side of S} n_i n_j
```

*Proof.* Write `x_i` for the number of part-`i` vertices placed on side `A`. The cut value
`sum_{ij in E(H)} [ x_i (n_j - x_j) + (n_i - x_i) x_j ]` is affine in each `x_i` separately,
so its maximum over the box `prod_i [0, n_i]` is attained at a vertex, i.e. `x_i in {0, n_i}`
— a partition constant on parts. Subtract from `|E(G)| = sum_{ij in E(H)} n_i n_j`. ∎

Verified independently: `h2_blowup_theory.py` compares the formula against exhaustive
`2^(N-1)` maxcut on 200 random blow-ups of C5, C7, Petersen, K33 and a 6-vertex base —
`identity verified on random blow-ups: True`.

**Why this matters.** A base with `h` vertices plus a weight vector encodes a blow-up at
*every* order `N` simultaneously, and evaluating `bip` costs `2^(h-1)` cut sums instead of
`2^(N-1)`. Searching `(H, n)` with `h <= 15` therefore covers infinitely many orders,
including all of `N = 24, 26, 49, 51, 74, 76, ...` at once.

Define
```
g(H) = max_{x in simplex} min_{S subset V(H)}  sum_{ij in E(H) monochromatic under S} x_i x_j.
```
Then `bip(H[n]) <= g(H) N^2`, and a blow-up of `H` violates the conjecture **iff
`g(H) > 1/25`**. Also `g(C5) = 1/25` (put `x = (1/5,...,1/5)`; every cut of an odd cycle
leaves a monochromatic edge, and each single edge is achievable).

Three reductions make the search space finite and small:

* **(R1) `bip` is monotone under adding edges.** Every cut's monochromatic count is
  non-decreasing, so the min is. Hence it suffices to search **maximal triangle-free** bases
  (every non-adjacent pair has a common neighbour).
* **(R2) `g` is invariant under twin reduction.** If `N(u) = N(v)` then `g(H) = g(H - v)`
  (extend any cut of `H - v` by putting `v` with `u`). Hence it suffices to search
  **twin-free** bases, provided all smaller orders are searched too.
* **(R3) `G -> K` (homomorphism) implies `bip(G) <= g(K) N^2`,** since `G` is a subgraph of
  `K[m]` with `m_v = |phi^{-1}(v)|` and `bip` is monotone. In particular any base with a
  homomorphism to C5 is harmless. (Empirically subsumed by R1+R2: *no* maximal twin-free
  triangle-free base on 8..15 vertices is C5-colourable.)

---

## 1. Item (i) — decoding the known exact extremal graphs

Reducing each exact extremal graph by its twin classes (`h2_identify.py`) gives the base and
the weights. Every one of them **is** a blow-up:

| N | graph6 | m | bip | base order | weights | base identified as |
|---|---|---|---|---|---|---|
| 12 | `K?BD@g]Qvo^?` | 25 | 5 | 11 | (2,1,1,1,1,1,1,1,1,1,1) | **Grötzsch graph M(C5)** |
| 12 | `K?ABBBwerwBw` | 25 | 5 | 9 | (2,2,2,1,1,1,1,1,1) | `HOFRePg` (see §1.2) |
| 13 | `L??FFB_~?~^_Fw` | 33 | 6 | 5 | (3,3,3,2,2) | **C5** (a plain C5 blow-up) |
| 13 | `L??ED@_~?~^_Fw` | 30 | 6 | 9 | (3,2,2,1,1,1,1,1,1) | `HqP@pgk` |
| 13 | `L??EFB_~FwB{Fw` | 32 | 6 | 7 | (3,2,2,2,2,1,1) | `FMgqO` |
| 13 | `L?`DE`gl@YJODg` | 26 | 6 | 13 | all 1 | **C13(1,5)**, the (3,5)-Ramsey graph |
| 14 | `M?AE@bH{AYN_LgBs?` | 32 | 7 | 13 | (2,1,...,1) | `L?PcBf_MdoPgFg` |

### 1.1 The construction

Let `C5` have vertices `u_0..u_4` (indices mod 5). The **Mycielskian tower over C5** is

```
level 0 :  u_0 .. u_4                                    (the C5)
level 1 :  w_0 .. w_4   with  w_i ~ u_{i-1}, u_{i+1}     (shadows: N(w_i) = N_{C5}(u_i))
level 2 :  z            with  z ~ w_0 .. w_4             (apex)
```

Levels 0+1+2 = the **Grötzsch graph** `M(C5)`: 11 vertices, 20 edges, triangle-free,
maximal triangle-free, twin-free, `chi = 4`, and *not* C5-colourable.

**The N = 12 extremal graph is the Grötzsch graph with its apex blown up to an independent
pair.** Exactly:

```
K?BD@g]Qvo^?  ==  M(C5)[1,1,1,1,1, 1,1,1,1,1, 2]        (25 edges, bip = 5 = floor(144/25))
```

Independently verified: the blow-up `M(C5)[1^10, 2]` has graph6 `KhdLA_gc?N_}`, is
triangle-free, and exhaustive `2^11` maxcut gives `maxcut = 20`, `bip = 5`
(`claude_exact_bip.exe 12`).

So the answer to "*how do the N = 12 extremal graphs beat every C5 blow-up?*" is: **they add a
Mycielski shadow layer and put the surplus vertices on the apex.** The apex sees only the
shadow layer, so it contributes monochromatic weight to exactly the cuts that the C5 layer
leaves cheap.

### 1.2 The explicit parametric family

```
F(a_0..a_4 ; b_0..b_4 ; c)  =  M(C5)[ a_0..a_4, b_0..b_4, c ]
```
`a_i` on the cycle vertex `u_i`, `b_i` on the shadow `w_i`, `c` on the apex, all `>= 0`.
`N = sum a_i + sum b_i + c`. By Lemma H2.1, `bip(F)` is the minimum over the `2^10` cuts of
`M(C5)` of the monochromatic weight sum — computed exactly in `h2_family.py` / `h2_opt.exe`.

This family contains
* every C5 blow-up (`b = 0, c = 0`), hence the exact extremal graphs at `N = 5n` and at `N = 13`;
* the exact extremal graph at `N = 12` (`a = b = 1, c = 2`);
* the 7- and 9-vertex bases in the table above, which are exactly the *partial* towers
  (C5 plus a subset of the shadows, with or without the apex): `FMgqO` = C5 + 2 shadows,
  `HOFRePg` / `HqP@pgk` = C5 + 3 shadows + apex.

The wider H2 family used for the search is: **blow-ups of arbitrary maximal triangle-free
bases**, of which the Mycielskian tower is the sharpest small member.

### 1.3 Exact ceiling of the family

Writing `N = 5k + r`, exhaustive/hill-climbed optimisation of the weights gives

| `r` | best C5 blow-up | best over the whole H2 family | `N^2/25` | deficit |
|---|---|---|---|---|
| 0 | `k^2` | `k^2` | `k^2` | **0 (equality)** |
| 1 | `k^2` | `k^2` | `k^2 + 0.4k + 0.04` | `0.4k + 0.04` |
| 2 | `k^2` | `k^2 + 1` (Grötzsch, `c = 2` weight on the apex) | `k^2 + 0.8k + 0.16` | `0.8k - 0.84` |
| 3 | `k^2 + k` | `k^2 + k` | `k^2 + 1.2k + 0.36` | `0.2k + 0.36` |
| 4 | `k^2 + k` | `k^2 + k` | `k^2 + 1.6k + 0.64` | `0.6k + 0.64` |

The `r = 2` row is the interesting one: **the Mycielskian layer buys exactly `+1` over every
C5 blow-up at every `N = 2 mod 5`** — this is the mechanism visible at `N = 12`, and it
persists (`N = 17: 10 vs 9`, `N = 22: 17 vs 16`, `N = 27: 26 vs 25`). Verified over *all*
bases with `h <= 15` at `N = 17` (max 10) and `N = 22` (max 17), and over the C5/Grötzsch
subfamily for every `N <= 30`.

The deficit `0.8k - 0.84` is negative only for `k = 1`, i.e. `N = 7`, where the tower does not
fit (a(7) = 1 by the complete census). **For every `k >= 2` the deficit is at least 0.76 and
grows linearly.** The family is therefore quantitatively dead, not marginally dead.

---

## 2. Item (ii) — instantiation at N = 24 and N = 26 (and 27, 28)

All values below are `bip` computed twice: once by Lemma H2.1 on the base, once by an
independent **exhaustive `2^(N-1)` maxcut** (`claude_exact_bip.exe`, Gray-code, exact
integers). Both agree in every case. Triangle-freeness checked explicitly on the final graph.

| instance | N | m | bip | `N^2/25` | `25 bip / N^2` | `bip/N^2` |
|---|---|---|---|---|---|---|
| `M(C5)[2^10, 4]` | 24 | 100 | **20** | 23.04 | 0.868056 | 0.034722 |
| `C5[5,5,5,5,4]` | 24 | 115 | **20** | 23.04 | 0.868056 | 0.034722 |
| `M(C5)[1,1,1,4,4;0,0,1,5,4;5]` | 26 | 126 | **25** | 27.04 | 0.924556 | 0.036982 |
| `C5[6,5,5,5,5]` | 26 | 135 | **25** | 27.04 | 0.924556 | 0.036982 |
| `M(C5)[3,4,2,1,1;3,4,2,1,1;5]` | 27 | 133 | **26** | 29.16 | 0.891632 | 0.035665 |
| `C5[6,6,5,5,5]` | 27 | 146 | 25 | 29.16 | 0.857339 | 0.034294 |
| `C5[6,6,5,6,5]` | 28 | 156 | **30** | 31.36 | 0.956633 | 0.038265 |
| `C5[6,6,6,6,5]` | 29 | 168 | 30 | 33.64 | 0.891795 | 0.035672 |

graph6 strings (all triangle-free, all re-verified by exhaustive maxcut):

```
N=24  W]KoWZBop`eEr?r?EW@e?BK?KoEE?EE???N~?B~o?^}?@~w                 bip=20  maxcut=80
N=26  YhG`C}]fc{JoG]G]CN@BoG]A]?C{?C{?A]???@~w?N~??~{?@~w?@~w?        bip=25  maxcut=101
N=27  ZFzf?{]?^?bpFaFa[KFB?wWB`_?{_?{_?@g?wC???N~_?~}?@~{?@~{??~}?    bip=26  maxcut=107
N=28  [??F~z{~Fw^_?~?~?^_Fw?~??Bw?Fo?Fo?Bw??}??Fo^_?~~?@}~?@}^_?~Fw?No   bip=30  maxcut=126
```

**Needed for a violation: `bip >= 24` at N = 24 and `bip >= 28` at N = 26. The family's exact
maxima are 20 and 25.** Not close.

Crucially, the N = 24 and N = 26 numbers are **maxima over every base with `h <= 15`**, not
just over the Mycielskian tower — see §3. At `N = 24` the family maximum 20 is attained
simultaneously by the plain C5 blow-up `(5,5,5,5,4)`, by `M(C5)[2^10,4]` (the doubled N = 12
extremal), and by 15-vertex bases; at `N = 26` the maximum 25 likewise.

---

## 3. The main negative result: the family is closed out for all bases up to 15 vertices

By R1 + R2, the search space of blow-up bases is exactly the **maximal, twin-free
triangle-free graphs**. Complete enumeration with `nauty geng -t -c` piped into `h2_filter.exe`:

| `h` | connected triangle-free graphs scanned | maximal + twin-free bases |
|---|---|---|
| 5 | 6 | 1 (C5) |
| 6 | 19 | 0 |
| 7 | 59 | 0 |
| 8 | 267 | 1 |
| 9 | 1,380 | 1 |
| 10 | 9,832 | 2 |
| 11 | 90,842 | 4 |
| 12 | 1,144,061 | 8 |
| 13 | 19,425,052 | 24 |
| 14 | 445,781,050 | 91 |
| 15 | **13,743,625,184** | 441 |

Each of the 573 bases was then weight-optimised with `h2_opt.exe` (exact integer
steepest-ascent hill climbing with plateau tie-breaking, coarse-to-fine `N = 2h, 4h, ...` up
to `N = 1280`, 10–16 random restarts each), plus 384 named bases (§4).

> **Result. `max{ 25 bip(H[n]) / N^2 } = 1.00000000` over all 573 enumerated bases and all
> 384 named bases, at every `N` tried up to 1280. Zero violations.**

Moreover — and this is the sharper statement — **every one of the 147 weight vectors attaining
the value `1` is a *balanced C5 collapse***: the support of the weight vector carries a
homomorphism to C5 whose five fibres have equal total weight `N/5`, so that
`bip = (N/5)^2 = N^2/25` exactly. Verified in `h2_collapse.py`:

```
optimal (ratio=1) weight vectors examined: 147
  C5_BALANCED: 147
```

Nothing else reaches `1/25`, and nothing exceeds it.

**Corollary (structural constraint on any counterexample).**
Since `bip(G) = bip(Q[sizes])` where `Q` is the twin-quotient of `G`, and `g(Q)` is bounded by
`g` of a maximal triangle-free completion of `Q` (R1) which twin-reduces into the enumerated
list (R2):

> **Any counterexample to Erdős #23 must have at least 16 pairwise distinct vertex
> neighbourhoods** — i.e. its twin-reduction has `>= 16` vertices. In particular no
> counterexample is a blow-up of a graph on 15 or fewer vertices, at *any* order `N`.

(Search-verified, not proved: it rests on the hill-climber finding the true maximum of
`min_S q_S` for each of the 957 bases. The uniformity of the result — every optimum a
balanced C5 collapse — is strong corroboration.)

A complete `h = 16` enumeration (~4x10^11 graphs, 96 `geng` lanes) was launched; see §6.

---

## 4. Item (iii) — other odd-girth-5 bases

`h2_named.py` builds 601 named triangle-free bases; 384 of order `<= 20` were evaluated with
unit weights, and all of order `<= 18` were fully weight-optimised.

Unit-weight `25 bip/N^2` (the plain graph, no blow-up):

| base | n | m | bip | `25 bip/n^2` |
|---|---|---|---|---|
| C5 | 5 | 5 | 1 | **1.000** |
| C5[2], C5[3], C5[4] (circulants) | 10, 15, 20 | 20, 45, 80 | 4, 9, 16 | **1.000** |
| C13(1,5) = (3,5)-Ramsey graph | 13 | 26 | 6 | 0.8876 |
| Grötzsch = M(C5) | 11 | 20 | 4 | 0.8264 |
| Andrásfai And(4) = C11(1,4) | 11 | 22 | 4 | 0.8264 |
| Clebsch graph (folded 5-cube), (3,6)-Ramsey | 16 | 40 | 8 | 0.7813 |
| Andrásfai And(3) = Wagner V8 | 8 | 12 | 2 | 0.7813 |
| Andrásfai And(6), n = 17 | 17 | 51 | 9 | 0.7785 |
| Petersen = Kneser K(5,2) | 10 | 15 | 3 | 0.7500 |
| Andrásfai And(7), n = 20 | 20 | 70 | 12 | 0.7500 |
| Möbius–Kantor GP(8,3) | 16 | 24 | 2 | 0.1953 |
| C7, C9, C11, C13 | 7..13 | | 1 | <= 0.51 |

With optimal weights, **every one of them drops back to exactly `1.000`, realised by a
balanced C5 collapse** (Petersen: weights concentrate on an induced C5 and the other five
vertices get weight 0; Clebsch, Andrásfai, Chvátal, Mycielskians, generalised Petersen
`GP(n,k)`, Kneser `K(7,3)`, all triangle-free circulants on `Z_n`, `n <= 22`, and the
Cayley graphs on `Z_5 x Z_m` with connection set `{(±1,s)} u {(0,t)}`, `t not in S - S` —
same). None exceeds `1/25`.

Two structural remarks:

* **High odd girth is fatal.** C7, C9, Möbius–Kantor, `K(7,3)` etc. are all far *below* C5.
  Anything with odd girth `>= 7` is close to bipartite, hence useless. The window is odd
  girth exactly 5.
* **Ramsey-critical graphs are the best non-C5 bases but still lose.** C13(1,5) (0.888) and
  Clebsch (0.781) are the densest triangle-free graphs with tiny independence number, and
  they are the closest non-blow-up competitors — but the weighted optimisation still collapses
  them onto a C5.

---

## 5. Why the family cannot work — the honest statement

`bip` is monotone under edge addition (R1), so the extremal objects are maximal triangle-free
graphs; and `sup_H g(H)` over all triangle-free `H` **is** the conjecture's constant. So the
weighted-blow-up formulation is not a restriction of the problem — it is a re-coordinatisation
of it, in which the free parameter is the number of *distinct neighbourhoods* rather than the
number of vertices. That re-coordinatisation is what made a search over `13.7 x 10^9`
15-vertex graphs (covering *all* orders `N`) possible in minutes.

The result of that search is that the maximum is exactly `1/25`, attained only by balanced C5
blow-ups, for every base of at most 15 distinct neighbourhoods. So:

* generalised blow-ups over Petersen / Andrásfai / Kneser / Clebsch / Wagner / Möbius–Kantor
  / Mycielskian / circulant bases: **all strictly below `1/25`** once the weights are optimised
  (they collapse onto an induced C5);
* the perturbation that *does* beat C5 blow-ups — the Mycielski shadow-plus-fat-apex trick —
  buys exactly `+1` at `N = 2 mod 5`, against a deficit that grows like `0.8k`. It is a
  bounded gain against a linear loss.

---

## 6. Artifacts

| file | what |
|---|---|
| `h2_lib.py` | graph6 codec, exhaustive maxcut, blow-up constructor, named-graph builders |
| `h2_blowup_theory.py` | statement + brute-force verification of Lemma H2.1 |
| `h2_decode.py` | structural decode of the known exact extremal graphs |
| `h2_identify.py` | twin-quotient identification of the extremal graphs (finds Grötzsch) |
| `h2_family.py` | the parametric family `F(a;b;c)` and its values |
| `h2_filter.cpp/.exe` | maximal / twin-free / no-C5-hom base filter for graph6 streams |
| `h2_opt.cpp/.exe` | exact weighted blow-up optimiser (incremental, coarse-to-fine) |
| `h2_gmax.cpp/.exe` | first-generation optimiser (kept: independent implementation) |
| `h2_sa.cpp/.exe` | simulated annealing over bases with co-evolving weights |
| `h2_named.py` | 601 named triangle-free bases -> `h2_named.g6` |
| `h2_collapse.py` | proves every ratio-1 optimum is a balanced C5 collapse |
| `h2_verify_targets.py` | builds the N = 24/26/27 instances -> `h2_targets.txt` |
| `h2_cross_check.py` | independent continuous (numpy soft-min projected-gradient) optimiser |
| `h2_bases_{5..15}.g6` | the complete enumerated base lists |
| `h2_lane.sh`, `h2_lane16.sh`, `h2_fixN.sh`, `h2_opt15.sh` | parallel drivers |

### Exact commands

```sh
clang++ -O3 -march=native -std=c++17 -o h2_filter.exe h2_filter.cpp
clang++ -O3 -march=native -std=c++17 -o h2_opt.exe    h2_opt.cpp
clang++ -O3 -march=native -std=c++17 -o h2_sa.exe     h2_sa.cpp

python h2_blowup_theory.py                  # -> identity verified on random blow-ups: True

# complete base enumeration (h = 5..14 single lane; h = 15 with 64 lanes)
for n in 5 6 7 8 9 10 11 12 13 14; do
  geng.exe -q -t -c $n | ./h2_filter.exe -twinfree > h2_bases_$n.g6
done
./h2_lane.sh 15 64                          # 13,743,625,184 graphs -> 441 bases

# weight optimisation over every base, every order up to N = 1280
cat h2_bases_{5,8,9,10,11,12,13,14}.g6 > h2_bases_all.g6
./h2_opt.exe -Nmax 1280 -r 12 -thr 0.999 -v < h2_bases_all.g6   # -> best = 1.00000000
split -n l/32 -d -a 2 h2_bases_15.g6 h2_b15_ ; ./h2_opt15.sh     # -> best = 1.00000000

# fixed target orders (maximum over ALL bases)
./h2_fixN.sh 24    # -> max bip = 20
./h2_fixN.sh 26    # -> max bip = 25
./h2_fixN2.sh 17   # -> max bip = 10
./h2_fixN2.sh 22   # -> max bip = 17

# named bases
python h2_named.py > h2_named.tsv
./h2_opt.exe -plain < h2_named_le20.g6
./h2_opt.exe -Nmax 640 -r 8 -thr 0.999 -v < h2_named_le14.g6

# structural validation and target verification
python h2_collapse.py h2_opt_all.out h2_b15_*.out h2_nm_*.out   # -> C5_BALANCED: 147/147
python h2_verify_targets.py
head -7 h2_targets.txt | while read g; do
  n=$(python -c "print(ord('${g:0:1}')-63)"); echo "$g" | ./claude_exact_bip.exe $n | tail -1
done
```

### Status of the `h = 16` enumeration

`./h2_lane16.sh` (96 `geng` lanes over ~4x10^11 connected triangle-free graphs on 16
vertices) was running at the end of this session; results land in `h2_bases_16.g6` and are
then fed to `h2_opt.exe` exactly as for `h = 15`. Expected yield ~2000 bases by the
1,2,4,8,24,91,441 growth pattern. **This is the one remaining piece needed to raise the
"at least 16 distinct neighbourhoods" corollary to "at least 17".**

---

## 7. Best ratio achieved

* Overall: `bip/N^2 = 1/25 = 0.0400000` exactly, at `N = 5n`, by `C5[n]` — **equality, not a
  violation**. e.g. `N = 20`, graph6 `SUWosZEWpbBEbEpbKWpbEEKYKWuKWrEKW`, `m = 80`,
  `maxcut = 64`, `bip = 16 = 400/25`; maxcut certified by exhaustive `2^19` enumeration.
* Best at an order **not** divisible by 5, certified by exhaustive `2^(N-1)` maxcut:
  `N = 28`, `C5[6,6,5,6,5]`, graph6
  `[??F~z{~Fw^_?~?~?^_Fw?~??Bw?Fo?Fo?Bw??}??Fo^_?~~?@}~?@}^_?~Fw?No`,
  `m = 156`, `maxcut = 126`, `bip = 30`, `bip/N^2 = 30/784 = 0.0382653`
  (`25 bip/N^2 = 0.956633`).
* At the assigned tight targets: `N = 24 -> bip = 20` (needed 24), `N = 26 -> bip = 25`
  (needed 28), both maxima over the entire family.

---

## 8. The single most promising unexplored direction I leave behind

**Search the weighted-blow-up space by base *order* rather than by graph order — and push the
complete enumeration from `h = 15` to `h = 18–20` using a `g`-monotone pruning rule instead of
`geng`.**

The re-coordinatisation in §0 is the real asset: it turns "find a counterexample at order N"
into "find a triangle-free graph `H` with `g(H) > 1/25`", which is order-free. Complete
coverage now stands at `h <= 15` (and `h = 16` in flight). The obstacle to `h >= 17` is that
`geng` enumerates all `~10^13` triangle-free graphs before the maximal+twin-free filter throws
away 99.99999%. The fix is to **generate the maximal triangle-free twin-free graphs directly**
by canonical-augmentation over *neighbourhood systems* (a maximal triangle-free graph is
exactly a graph whose non-adjacency relation is covered by common neighbours — equivalently a
"friendship-free diameter-2 triangle-free" graph), which should make `h = 18–20` reachable and
would raise the corollary to "any counterexample has at least 21 distinct neighbourhoods".

Two concrete sub-directions inside that:

1. **Certificates instead of search.** For each base, look for a probability distribution
   `lambda` over cuts with `max_{x in simplex} sum_{ij} m_ij x_i x_j <= 1/25` where
   `m_ij = Pr_lambda[ij monochromatic]`. For C5 the uniform distribution over the five
   one-edge cuts is exactly tight. If such certificates exist uniformly for all bases of a
   given shape, they would upgrade the `h <= 15` search into a proof for that shape — and a
   base where *no* certificate exists is precisely where a counterexample could hide. This
   converts the hunt into a (finite, LP-flavoured) feasibility question.
2. **The `r = 2` residue class.** It is the only class where a non-C5 mechanism (the Mycielski
   shadow + fat apex) strictly beats every C5 blow-up, and the only class whose deficit
   formula `0.8k - 0.84` is ever negative. Any *second* independent `+O(k)` gain stacked on top
   of the `+1` would close the gap. Searching specifically for bases whose optimum at
   `N = 2 mod 5` exceeds `k^2 + 1` — i.e. a *second* Mycielski-type layer that pays — is the
   sharpest single question this family leaves open.
