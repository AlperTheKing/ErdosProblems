# R8 — Adversarial audit of "Theorem A"

**Claim audited.** For every triangle-free graph `G` and every `x >= 0` on `V(G)` with `sum_v x_v = 1`,
setting `w_uv = x_u x_v`,

```
Lambda(G,x) := min { sum_e w_e y_e : sum_{e in C} y_e >= 1 for every odd cycle C,  y >= 0 }  <=  1/25.
```

**VERDICT: (c) PROVED.** A complete proof is given in §2. It is five lines, it is tight
(equality at `C5` with uniform `x`, and at every balanced `C5` blow-up), and it has been
machine-checked in exact rational arithmetic against the exactly-computed LP optimum on
every instance in §4. The falsification effort of §4 found nothing above `1/25`, as it now
must not.

**Two warnings for the consumer of Theorem A, both established below:**

1. §5: the odd-cycle LP is **not** integral on triangle-free graphs — explicit 25-vertex
   triangle-free witness with `Lambda = 2/375 < psi = 4/625` (ratio `6/5`). So Theorem A does
   **not** imply `psi <= 1/25`, i.e. it does not imply Erdős #23, and no amount of
   strengthening of the LP bound alone will.
2. §3: Theorem A is **tight on a plateau**, not at an isolated extremal graph: for *every*
   triangle-free `G` containing a 5-cycle, `max_x Lambda(G,x) = 1/25` exactly. Any purported
   proof of Theorem A with slack anywhere is therefore wrong, and any consumer step that
   needs a strict inequality `Lambda < 1/25` is unavailable.

All computations: exact `fractions.Fraction`. Floats appear only to steer search; every
reported number was recomputed exactly and certified by a matched primal/dual pair.

---

## 1. Setup, reductions, and the certified LP machinery

`d(v) := sum_{u in N(v)} x_u` (weighted degree), `W := sum_{uv in E} x_u x_v = (1/2) sum_v x_v d(v)`.

**Reduction R1 (support).** `Lambda(G,x) = Lambda(G[supp x], x|_supp)`.
*Proof.* (`<=`) extend an optimal cover of `G[supp x]` by `y_e = 1` on every edge with an
endpoint of weight 0; such edges cost nothing, and an odd cycle meeting `V \ supp(x)` uses at
least two of them, so `sum_{e in C} y_e >= 2 >= 1`. (`>=`) restrict a cover of `G` to
`G[supp x]`; it stays feasible there and its cost only drops. ∎

**Reduction R2 (isolated vertices).** Vertices isolated in `G[supp x]` lie on no cycle and may
be deleted; this changes no other `d(v)`, and leaves `sum_v x_v <= 1`. After R1+R2 we may
assume `x_v > 0` and `d(v) > 0` for all `v`, and `sum_v x_v <= 1`.

**Separation oracle (used everywhere instead of cycle enumeration).** `y >= 0` is feasible iff
in the bipartite double cover (`(v,0),(v,1)`; each edge `uv` giving `(u,0)-(v,1)` and
`(u,1)-(v,0)`, both of length `y_uv`) one has `dist((v,0),(v,1)) >= 1` for every `v`. A
`(v,0)–(v,1)` path projects to a closed odd walk, from which an odd cycle of no larger
`y`-length is extracted by the standard stack contraction. This is exact (exact-rational
Dijkstra) and never enumerates cycles, so it is immune to the enumeration bug flagged in the
task.

**Enumerator validation** (`R8_thmA_selftest.py`, all 20 checks PASS):

| check | expected | got |
|---|---|---|
| `K5` all cycles / odd cycles | 37 / 22 (=10 triangles + 12 pentagons) | 37 / 22 |
| `K5` Hamiltonian cycles `4!/2` | 12 | 12 |
| `K_{3,3}` cycles / odd | 15 (9 `C4` + 6 `C6`) / 0 | 15 / 0 |
| `K6` Hamiltonian cycles `5!/2` | 60 | 60 |
| Petersen cycle spectrum | `{5:12, 6:10, 8:15, 9:20}` | identical |
| **`Gamma_11` odd cycles** | **596** | **596** |
| **`Gamma_11` odd Hamiltonian cycles** | **145** | **145** |
| Dijkstra separation vs brute force min odd cycle | equal, 60 random graphs | equal |
| cutting-plane LP vs full-enumeration LP | equal, 30 random weighted instances | equal |
| `Lambda <= psi` | 20 random weighted instances | holds |

The 596/145 counts reproduce the numbers the task states as correct, so the enumerator does
include Hamiltonian odd cycles. Every `Lambda` below is certified by a **matched pair**: an
exact rational cover `y` verified feasible by the exact separation oracle (upper bound) and an
exact rational odd-cycle packing `z` verified to respect all capacities (lower bound), with
equal objective values.

---

## 2. PROOF of Theorem A

### Lemma 1 (vertex-potential covers)
Let `g : V -> R_{>=0}` and `gamma > 0` satisfy `sum_{v in C} g(v) >= gamma` for every odd cycle
`C`. Then
```
        Lambda(G,x)  <=  (1/(2*gamma)) * sum_v g(v) x_v d(v).
```
*Proof.* Put `y_e := (g(u)+g(v))/(2*gamma)` for `e = uv`. For an odd cycle `C`, every vertex of
`C` is incident to exactly two edges of `C`, so
`sum_{e in C} y_e = (1/(2 gamma)) * 2 * sum_{v in C} g(v) >= 1`; `y` is feasible. Its cost is
`sum_{uv in E} x_u x_v (g(u)+g(v)) / (2 gamma) = (1/(2 gamma)) sum_v g(v) x_v sum_{u ~ v} x_u`,
which is the claim. ∎

### Lemma 2 (degree sum along an odd cycle; weighted Andrásfai–Erdős–Sós counting)
Let `G` be triangle-free and let `C` be a cycle of odd length `L`. Then
```
        sum_{v in V(C)} d(v)  <=  (L-1)/2.
```
*Proof.* `G` is triangle-free, so `N(u)` is an independent set for every `u`. Hence
`N(u) ∩ V(C)` is an independent set of `G` inside `V(C)`; since all `L` edges of `C` are
present in `G`, it is in particular an independent set of the cycle graph `C_L`, so
`|N(u) ∩ V(C)| <= floor(L/2) = (L-1)/2`. Double counting,
```
sum_{v in V(C)} d(v) = sum_{v in V(C)} sum_{u in N(v)} x_u
                     = sum_{u in V} x_u |N(u) ∩ V(C)|
                     <= ((L-1)/2) * sum_u x_u  <=  (L-1)/2.   ∎
```
(For `L = 5` this is exactly the counting in the Andrásfai–Erdős–Sós theorem: no vertex has
three neighbours on an induced `C5`.)

### Theorem A
*For every triangle-free `G` and every `x >= 0` with `sum_v x_v = 1`,* `Lambda(G,x) <= 1/25`.

*Proof.* By R1+R2 assume `x_v > 0`, `d(v) > 0`, `sum_v x_v <= 1`. If `G` is bipartite then
`Lambda = 0`. Otherwise take
```
        g(v) := 1/d(v),        gamma := min over odd cycles C of  sum_{v in C} g(v).
```
Let `C` be any odd cycle, `L = |C| >= 5` (triangle-freeness). Cauchy–Schwarz (AM–HM) and
Lemma 2 give
```
   sum_{v in C} 1/d(v)  >=  L^2 / sum_{v in C} d(v)  >=  L^2 / ((L-1)/2)  =  2L^2/(L-1).
```
`L -> 2L^2/(L-1)` is increasing for `L > 2`, so for all odd `L >= 5`
```
        gamma  >=  2*5^2/(5-1)  =  25/2.
```
Lemma 1 with this `g` gives `sum_v g(v) x_v d(v) = sum_v x_v <= 1`, hence
```
        Lambda(G,x)  <=  1/(2*gamma)  <=  1/(2 * 25/2)  =  1/25.    ∎
```

### What the proof actually gives (all verified in §4)
* **Sharper, instance-wise:** `Lambda(G,x) <= 1/(2*gamma)`, `gamma = min_C sum_{v in C} 1/d(v)`.
* **By odd girth:** if `G` has odd girth `g >= 5` then `Lambda(G,x) <= (g-1)/(4 g^2)`;
  `g=5 -> 1/25`, `g=7 -> 3/98 = 0.03061`, `g=9 -> 2/81 = 0.02469`. So graphs of odd girth `>= 7`
  are strictly below `1/25` with room to spare — the whole content of Theorem A lives at odd
  girth exactly 5.
* **Equality analysis.** `Lambda = 1/25` forces, on some odd cycle `C` attaining `gamma`:
  `L = 5`; equality in Cauchy–Schwarz, i.e. `d(v) = 2/5` for all `v in C`; and equality in
  Lemma 2, i.e. `|N(u) ∩ C| = 2` for `x`-almost every `u`. `C5` with uniform `x` satisfies all
  three (`y_e = 1/5` is exactly the cover the proof outputs, of cost `1/25`).

### Sanity of the constant
For `C5` uniform: `d(v) = 2/5`, `g(v) = 5/2`, `gamma = 5 * 5/2 = 25/2` exactly, the constructed
cover is `y ≡ 1/5` with cost `1/25`, and the packing `z_{C5} = 1/25` matches it — so the proof
is *exactly* tight, with no slack to lose anywhere.

---

## 3. Plausibility at the sharp constant, and the plateau (task 3)

**`C5`.** The only odd cycle is `C5` itself, so `Lambda(C5,x) = min_i x_i x_{i+1}` (LP:
`min sum w_e y_e` s.t. `sum_e y_e >= 1`). Since
`prod_{i=1..5} (x_i x_{i+1}) = (prod_i x_i)^2 <= (5^{-5})^2` by AM–GM,
`min_i x_i x_{i+1} <= 5^{-2} = 1/25`, **with equality iff `x` is uniform**.
Verified: `Lambda(C5, uniform) = 1/25` exactly, certified by cover `y = (1/5,...,1/5)`
(cost `1/25`) and packing `z_{C5} = 1/25`. Over 3000 random rational `x` on `C5`, the formula
matched in every case and the maximum was `182/5041 = 0.03610 < 1/25` (attained at a
near-uniform `x`). **1/25 attained, never exceeded.**

**`C5` blow-ups, unequal and empty parts.** If `G` has a homomorphism to `C5` (equivalently `G`
is a subgraph of a `C5` blow-up), let `P_i` be the `x`-weight of class `i`. The indicator of the
edge set between classes `i` and `i+1` is a feasible cover — an odd cycle projects to a closed
walk of odd winding number, which must traverse every edge of `C5` — so
```
        Lambda(G,x)  <=  min_i P_i P_{i+1}  <=  1/25,
```
the last step again by `prod_i (P_i P_{i+1}) = (prod_i P_i)^2 <= 5^{-10}`, with equality iff
`P_i = 1/5` for all `i`. Exhaustively checked exactly on 200+ blow-up instances (part sizes
0..3, three weight regimes: uniform on vertices / uniform inside unequal parts / fully generic
weights): the block bound was never violated, and the maximum `Lambda` over all of them was
exactly `1/25`, attained only in the balanced case. Sample of uniform-`x` values:

| sizes | `n` | `Lambda` | | sizes | `n` | `Lambda` |
|---|---|---|---|---|---|---|
| `(1,1,1,1,1)` | 5 | `1/25` | | `(2,1,1,1,1)` | 6 | `1/36` |
| `(2,2,2,2,2)` | 10 | `1/25` | | `(2,2,1,1,1)` | 7 | `1/49` |
| `(3,3,3,3,3)` | 15 | `1/25` | | `(3,2,2,2,2)` | 11 | `4/121` |
| `(2,1,2,1,2)` | 8 | `1/32` | | `(3,2,1,2,1)` | 9 | `2/81` |
| `(1,1,1,1,0)` | 4 | `0` | | `(4,1,1,1,1)` | 8 | `1/64` |

(The integral analogue `D(C5[n_1..n_5]) = min_i n_i n_{i+1}` is Erdős–Győri–Simonovits 1992,
Corollary 2; the values above agree with it, i.e. the LP is integral on this family.)

**The plateau (this is the key structural fact).** Let `G` be triangle-free and contain a
5-cycle `C` (in a triangle-free graph every 5-cycle is induced — a chord would create a
triangle). Put `x = 1/5` on `C`, `0` elsewhere. Every edge not inside `C` has weight `0`, so
`y = 1` there is free and covers every odd cycle leaving `C`; the only odd cycle inside `C` is
`C`. Hence `Lambda(G,x) = 1/25` **exactly**. Therefore
```
        for every triangle-free G with a 5-cycle:   max_x Lambda(G,x) = 1/25 exactly
```
(`>=` by this construction, `<=` by Theorem A). Verified exactly, with matched certificates,
for `C5`, Petersen, Grötzsch, Wagner, `Gamma_11/14/17 = And(4/5/6)`, `And(3)`, `Myc(C7)`,
Clebsch and all `C5` blow-ups. So `1/25` is not an isolated peak: it is the value of an
enormous plateau, and every triangle-free graph with a pentagon sits on it.

---

## 4. Falsification search (task 1) — nothing above 1/25

Method per graph: persistent-cycle-pool cutting-plane LP (float, HiGHS) + replicator ascent on
the touching quadratic `x -> sum_e y*_e x_u x_v` from many starts (uniform, Dirichlet with
three concentrations, and **`C5`-concentrated starts with weight deliberately leaked onto the
outside vertices** — pure `C5`-supported starts are useless because replicator dynamics
preserve zero coordinates and can never leave that face); then exact rational re-evaluation of
the best `x` at several denominators, plus an exact `C5`-leak scan over all leak targets and
leak sizes `t in {0, 1/100, 1/50, 1/25, 1/10, 1/5}`.

`max_x Lambda` came out **exactly `1/25`** for every graph containing a `C5`, and strictly below
for every graph of odd girth `>= 7`. Exact uniform-`x` values (all certified):

| graph | `n` | `m` | odd girth | `Lambda(uniform x)` | `max_x Lambda` |
|---|---|---|---|---|---|
| `C5` | 5 | 5 | 5 | `1/25` | `1/25` |
| `C7` / `C9` / `C11` | 7/9/11 | | 7/9/11 | `1/49` / `1/81` / `1/121` | same |
| Petersen | 10 | 15 | 5 | `3/100` | `1/25` |
| Grötzsch | 11 | 20 | 5 | `4/121` | `1/25` |
| Wagner `= circle(8,8) = And(3)` | 8 | 12 | 5 | `1/32` | `1/25` |
| `Gamma_11 = circle(11,11) = And(4)` | 11 | 22 | 5 | `4/121` | `1/25` |
| `Gamma_14 = circle(14,14) = And(5)` | 14 | 35 | 5 | `3/98` | `1/25` |
| `Gamma_17 = circle(17,17) = And(6)` | 17 | 51 | 5 | `9/289` | `1/25` |
| `Myc(C7)` | 15 | 28 | 5 | `1/45` | `1/25` |
| Clebsch `srg(16,5,0,2)` | 16 | 40 | 5 | `1/32` | `1/25` |
| Kneser `K(7,3) = O_4` | 35 | 70 | 7 | (odd girth 7 ⇒ `<= 3/98`) | `< 1/25` |
| McGee `(3,7)`-cage | 24 | 36 | 7 | (odd girth 7 ⇒ `<= 3/98`) | `< 1/25` |

Also searched: `C5` blow-ups with free part weights; random maximal triangle-free graphs on
`n = 6..14` (maximality is WLOG: `Lambda` is monotone under adding edges, so on a fixed vertex
set the maximum over triangle-free graphs is attained at a maximal one), deduplicated by
Weisfeiler–Lehman hash, with multistart ascent + exact `C5`-leak scan for each.
**No instance anywhere exceeded `1/25`.** (See `R8_thmA_partB.log`, `R8_thmA_partC.log`.)

This is as it must be: `Lambda <= psi`, so a falsifier would also refute Erdős #23 — and, now,
would also have to break the elementary chain of §2.

### Machine check of the proof itself (`R8_thmA_proofcheck.py`, no failures)
* Lemma 2 brute-forced over **all** odd cycles for `C5`, `C7`, Petersen, Grötzsch, Wagner,
  `Gamma_11`, Clebsch at uniform and random weights, plus 200 random maximal triangle-free
  graphs: never violated; worst ratio `sum_C d / ((L-1)/2)` was exactly `1.000000` at `C5`
  uniform (equality) and `0.9968`, `0.9949`, `0.9848` at Wagner/`Gamma_11`/Grötzsch.
* `gamma >= 25/2`, `1/(2 gamma) <= 1/25`, cover feasibility (via exact separation), and
  `cost = 1/(2 gamma)`: all exactly true on every instance, including 400 random weighted
  instances on `n = 5..11`, where the worst ratio `Lambda_exact / (proof bound)` was `0.942`.
* Instances where the proof bound is *exactly* the truth: `C5` (`1/25`), `C7` (`1/49`),
  `C9`, `C11`, Petersen (`3/100`), Clebsch (`1/32`), all balanced `C5` blow-ups (`1/25`).

---

## 5. What Theorem A does and does not give (audit of its use)

**It does not imply Erdős #23.** The odd-cycle LP is not integral on triangle-free graphs.
Explicit witness (`R8_thmA_gap2.py`): let `S` be `K5` with **every edge subdivided twice**
(`n = 25`, `m = 30`, triangle-free, odd girth 9,
graph6 `X?AAK?`_?_o?A@O?C?I??C?D???O?H???O?@G???O??a???A??@`). Subdividing an edge twice
preserves all cycle parities, so the odd cycles of `S` correspond to those of `K5`. With `x`
uniform (`w_e = 1/625`):
```
    Lambda(S,x) = (1/625) * (10/3) = 2/375 = 0.005333...   [certified matched primal/dual]
    psi(S,x)    = (1/625) * 4      = 4/625 = 0.006400      [max-cut(K5) = 6, so 4 mono edges]
    psi / Lambda = 6/5.
```
(`psi` here is exact: in an optimal cut each subdivision path `u-a-b-v` can be 2-coloured with
no monochromatic edge iff `u,v` differ, and costs exactly one otherwise, so
`psi = min_cut(K5) mono edges / 625 = 4/625`.) This is the Guenin obstruction: `K5` with all
edges odd is *the* minimal non-weakly-bipartite signed graph.

**Conversely, where it does have teeth.** By Guenin's theorem (B. Guenin, *A characterization of
weakly bipartite graphs*, JCTB 83 (2001) 112–168, proving a conjecture of Seymour 1981): the
polyhedron `{y >= 0 : y(C) >= 1 for all odd circuits}` of a signed graph is integral iff the
signed graph has no odd-`K5` minor. Applied to the all-odd signing `(G, E(G))`, whose minimal
odd-circuit covers are exactly the monochromatic edge sets of cuts, this gives:

> **Corollary.** If `G` is triangle-free and `(G, E(G))` has no odd-`K5` minor, then
> `psi(G,x) = Lambda(G,x) <= 1/25` for every `x`; i.e. Erdős's conjecture holds for `G`
> (`n^2/25` edges suffice). In particular it holds for every triangle-free graph with no `K5`
> minor — though that class is sparse (`m <= 3n-6`), so there the conclusion is anyway weak.

**Two proof routes that are dead — do not spend time on them.**

* *No `x`-independent cover can work.* For `C5`, every feasible cover has `sum_e y_e >= 1`,
  hence `max_e y_e >= 1/5`, hence putting `x = 1/2` on the endpoints of that edge gives
  `max_x sum_e y_e x_u x_v >= 1/20`. So
  `min_y max_x = 1/20 > 1/25 = max_x min_y`. The minimax gap is real already on `C5`: any proof
  must pick the cover as a function of `x` (as §2 does, via `g(v) = 1/d(v)`).
* *No cut-averaging can work.* Any cover of the form `y = sum_j p_j * 1_{mono(S_j)}` (convex
  combination of monochromatic-edge-sets of cuts) is feasible, but costs
  `sum_j p_j q_{S_j}(x) >= min_S q_S(x) = psi(G,x)`. So reaching `1/25` that way *is* the full
  Erdős conjecture. Useful covers must lie outside the cut cone — again as in §2.

**Related bound that is *not* enough.** `y ≡ 1/5` is feasible (odd girth `>= 5`) with cost
`W/5 <= 1/20` by Motzkin–Straus (`W <= (1 - 1/omega)/2 = 1/4` for `omega = 2`). This gives the
easy `Lambda <= 1/20`; the gain in §2 comes entirely from replacing the uniform potential by
`1/d(v)` and using the AES counting.

---

## 6. Literature

* **No published bound of the form "fractional odd-cycle transversal of a triangle-free graph
  `<= n^2/c`" exists**, for `c = 25` or any `c` (searched: fractional odd cycle cover /
  transversal / bipartization, LP over odd cycles + triangle-free, fractional relaxation of the
  Erdős conjecture, arXiv-restricted). The fractional relaxation of Erdős #23 appears to be
  unstudied. Theorem A should therefore be treated as **proved here**, not cited.
* Integral problem: Erdős–Faudree–Pach–Spencer, *How to make a graph bipartite*, JCTB 45 (1988)
  86–98 — Thm 1: `min{ m/2 - 2m(2m^2-n^3)/(n^2(n^2-2m)),  m - 4m^2/n^2 }`; Cor. 2.6: `n^2/18 + n/2`.
  The second branch equals `n^2/25` exactly at `m = n^2/5`, settling `m >= n^2/5`.
  Erdős–Győri–Simonovits (Bolyai Soc. 60, 1992, 239–263) — Conjecture 1 is the `n^2/25`
  statement; Thm 2 reduces `e >= n^2/5` to pentagon-like blow-ups; **Cor. 2:
  `D(C5[n_1..n_5]) = min_i n_i n_{i+1}`** (the integral analogue of §3, and it matches the LP
  values computed here). Balogh–Clemen–Lidický, *Max cuts in triangle-free graphs*
  (arXiv:2103.14179, EUROCOMB 2021) — `n^2/23.5` in general, conjecture proved for edge density
  `<= 0.2486` and `>= 0.3197`. Sudakov, *Making a `K_4`-free graph bipartite*, Combinatorica 27
  (2007) — `n^2/9`.
* Odd girth: Fox–Himwich–Mani (arXiv:2102.10220) give `h(n,k,C_{2r+1}) = O_r(n^2/k^{r+1})` with
  matching lower bounds — order of magnitude only, no constant below `1/25`. §2 here gives the
  clean sharp-shaped fractional statement `(g-1)/(4g^2)` for odd girth `g`.
* The LP itself is the Min-UnCut / weakly-bipartite LP: Grötschel–Pulleyblank (1981),
  Seymour (1981), **Guenin JCTB 83 (2001) 112–168**, Schrijver's short proof; the double-cover
  multicommodity-flow view is used by Agarwal–Charikar–Makarychev–Makarychev (STOC 2005).

---

## 7. Files

| file | contents |
|---|---|
| `R8_thmA_lib.py` | graphs, cycle enumerator, exact double-cover Dijkstra separation, exact rational simplex, exact `Lambda` by cutting planes with matched certificates, exact `psi` |
| `R8_thmA_selftest.py` | 20 validation checks (enumerator counts incl. `Gamma_11` 596/145, oracle vs brute force, cutting-plane LP vs full-enumeration LP, `Lambda <= psi`) |
| `R8_thmA_search.py` | falsification search: blow-ups (part a), named graphs (part b), random maximal triangle-free graphs (part c) |
| `R8_thmA_proofcheck.py` | machine check of Lemma 2, of `gamma >= 25/2`, of cover feasibility, and of `Lambda_exact <= 1/(2 gamma) <= 1/25` |
| `R8_thmA_blowup.py` | task 3: `C5`, unbalanced/empty-part blow-ups, plateau verification |
| `R8_thmA_gap.py`, `R8_thmA_gap2.py` | `psi` vs `Lambda`; explicit non-integral triangle-free witness |
| `R8_thmA_partB.log`, `R8_thmA_partC.log`, `R8_thmA_results_*.json` | raw run output |
