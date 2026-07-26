# R9 — Discharging with a global potential (Erdős #23)

Mechanism assigned: local discharging rules combined with a **global potential** `Φ(G)` —
an amortised argument in which local charge moves are paid for out of a global quantity.

**Verdict: the mechanism is dead in all three shapes it can take, and the deaths are
theorems, not failed searches.** No new bound on `bip` was produced. What was produced:

* an exact structure theorem for the whole family (§2, Theorem 1): *the pointwise-largest
  admissible potential is `Φ*(G) = N²/25 − V(G)`, where `V` is the shortest-path value of
  the reduction system*, so choosing a clever potential is impossible — the potential is
  determined, and the only freedom is the move family;
* an exact evaluation of `Φ*` on the mandated witnesses (§4): `Φ*(C5[2]) = 4 − 6 = −2 < 0`,
  so **no nonnegative potential exists at all**, and `Φ*` is negative on 7 of the 11
  mandated witnesses;
* the quantitative statement of what the potential buys: it upgrades a **minimum**-degree
  hypothesis `δ ≲ 4N/25` to an **average**-degree hypothesis `d̄ ≤ 4N/25 + 2` — an additive
  `O(1)` in the degree threshold, while the extremal family sits at `δ = 10N/25`, a factor
  `2.5` away (§6);
* a general no-go for the static shape (§8): a global potential **cannot** rescue
  discharging with local cut hypotheses, because the potential cannot see the cut;
* the locality radius the max-cut hypothesis must reach: `0.2889 N` at `N = 45` inside the
  blow-up family (§9), i.e. any local rule would have to certify stability against
  `≥ C(N, 0.29N)` switching sets.

All arithmetic is exact (`fractions.Fraction` / integers). Reproduction: §12.

---

## 1. The three shapes a "discharging + global potential" argument can take

**(S1) Amortised process.** Order/reduce the object step by step (delete a vertex, delete a
set, delete an edge, insert a vertex into a growing cut), carry a potential `Φ ≥ 0`, and
prove the strengthened statement `bip(G) + Φ(G) ≤ N²/25` by induction. This is the shape
the assignment calls "amortised/potential-function arguments over a PROCESS". §§2–7.

**(S2) Static local rules + a global term.** Fix the maximum cut, assign charges from the
local cut structure (`σ`-values), move charge by local rules, and add `Φ(G)` to absorb the
deficit. §8.

**(S3) Charging to 5-cycles.** Distribute `bip` over the induced pentagons and ask what each
must pay. §10.

The three are logically independent, and each dies for a different reason.

---

## 2. Theorem 1 (potential = shortest-path value). The potential is never a free parameter

> **Setup.** Let `𝒢` be a class of objects with a well-founded reduction system: each
> non-base `G` has a nonempty set of moves `(G → G′, c)` with `c ∈ ℝ`. The system is
> **sound** if `bip(G) ≤ bip(G′) + c` for every move. Let `f(G) = N²/25` be the target and
> assume the base case `bip ≤ f` there.
>
> Define the DP (shortest-path) value
> ```
>   U(G) = bip(G)                              for base G,
>   U(G) = min over moves (G→G′,c) of [ c + U(G′) ]    otherwise.
> ```
>
> **Theorem 1.** A potential `Φ : 𝒢 → ℝ≥0` satisfying the amortised step
> ```
>   (∗)   for every G there is a move (G→G′,c) with   Φ(G) − Φ(G′) ≤ (f(G) − f(G′)) − c
> ```
> exists **if and only if** `U(G) ≤ f(G)` for every `G`; and every admissible `Φ` satisfies
> `Φ ≤ f − U` pointwise, with `Φ* = f − U` admissible. So the amortised mechanism proves
> exactly the statement `U ≤ f` — no more, no less.

*Proof.* (⇐) Put `Φ = f − U ≥ 0`. For a move attaining the minimum in `U(G)`,
`Φ(G) − Φ(G′) = f(G) − f(G′) − c`, so (∗) holds with equality.
(⇒) Induction along the well-founded order. At a base object `Φ ≥ 0` and `U = bip ≤ f`.
If `Φ(G′) ≤ f(G′) − U(G′)` for the move given by (∗), then
`Φ(G) ≤ Φ(G′) + f(G) − f(G′) − c ≤ f(G) − (U(G′) + c) ≤ f(G) − U(G)`,
the last step because `U(G) ≤ U(G′) + c` by definition. Finally `Φ ≥ 0` forces `U ≤ f`. ∎

*Machine gate* (`R9_discharge_verify.py` (c)): for the deletion system with cost `⌊d/2⌋`,
`Φ* = f − V` was checked to satisfy step (∗) at **every** induced subgraph of every witness
with `N ≤ 11` — 31 / 1023 / 511 / 255 / 1023 / 2047 / 255 / 2047 / 127 / 63 subgraphs,
all `True`.

**Consequence.** "Invent a clever global potential" is not a degree of freedom. The
potential is *determined* by the move family, and the only mathematical content of an
amortised argument is the value of a shortest-path problem.

## 3. Theorem 2 (the mechanism is never a reduction)

> **Theorem 2.** For every **sound** reduction system, `U(G) ≥ bip(G)` for all `G`.

*Proof.* Induction: `bip(G) ≤ bip(G′) + c` for the minimising move, and `bip(G′) ≤ U(G′)`. ∎

So the statement the mechanism must prove, `U ≤ N²/25`, is **always at least as strong as
the conjecture**. Two extreme instantiations bracket the situation, and there is no middle
ground with a formula-computable cost:

| cost function | sound? | `U` | status |
|---|---|---|---|
| `c(G,v) = bip(G) − bip(G−v)` (exact drop) | yes | `U = bip` exactly (verified on all witnesses, `R9_discharge_dp.py` §T2) | **circular**: "`U ≤ N²/25`" is the conjecture verbatim |
| `c(G,v) = ⌊d(v)/2⌋` (greedy insertion; the only non-circular local formula) | yes | `U = V`, computed below | **false** already at `C5[2]` |
| edge deletion, `c = 1` | yes | `U = bip` (min odd-cycle edge transversal) | **circular** |

Quoted verbatim, the circular instantiation's terminal lemma is:
*"for every triangle-free `G`, `min over deletion orderings of Σ_i (bip(G_i) − bip(G_{i+1}))
≤ N²/25"*, which telescopes to `bip(G) ≤ N²/25`. Worthless.

## 4. Theorem 3 (extremality forcing) and the exact value of `Φ*`

> **Theorem 3.** Let `Φ ≥ 0` be admissible and let `G` be **extremal**
> (`bip(G) = f(G)`, i.e. `C5[n]`). Then along the entire path of moves selected by (∗)
> starting at `G`, every inequality is tight:
> `Φ(G_i) = f(G_i) − bip(G_i)` (the exact slack), `U(G_i) = bip(G_i)`, and every cost equals
> the exact drop `bip(G_i) − bip(G_{i+1})`. In particular `Σ_i c_i = bip(G)` exactly.

*Proof.* At `G`: `Φ(G) − Φ(G′) ≤ f(G) − f(G′) − c ≤ slack(G) − slack(G′) = −slack(G′)`,
so `Φ(G′) ≥ slack(G′)`; but `Φ ≤ f − U ≤ f − bip = slack` by Theorems 1–2, so
`Φ(G′) = slack(G′)`, `Φ(G) = 0`, `c = bip(G) − bip(G′)`. The same computation at `G′` (now
using `Φ(G′) = slack(G′)`) gives `Φ(G″) ≥ slack(G″)`, hence equality again, and so on. ∎

**Explicit potential values.** For the canonical cost `⌊d/2⌋`, `Φ*(G) = N²/25 − V(G)` where
`V(G) = min over deletion orderings of Σ_i ⌊d_{G_i}(v_i)/2⌋` (exact subset DP, `2^N` states):

| graph | `N` | `|E|` | `bip` | `V` | `N²/25` | `Φ* = N²/25 − V` | admissible? |
|---|---|---|---|---|---|---|---|
| `C5` | 5 | 5 | 1 | 1 | 1 | `0` | yes (tight) |
| `C5[2]` | 10 | 20 | 4 | 6 | 4 | **`−2`** | **NO** |
| `C5[3,1,2,2,1]` | 9 | 14 | 2 | 3 | 81/25 | `6/25` | yes |
| `C5[2,2,2,2,0]` (zero part) | 8 | 12 | 0 | 3 | 64/25 | **`−11/25`** | **NO** |
| Petersen | 10 | 15 | 3 | 3 | 4 | `1` | yes |
| Grötzsch | 11 | 20 | 4 | 5 | 121/25 | **`−4/25`** | **NO** |
| Wagner `= And(3)` | 8 | 12 | 2 | 3 | 64/25 | **`−11/25`** | **NO** |
| `Γ₁₁ = And(4)` | 11 | 22 | 4 | 7 | 121/25 | **`−54/25`** | **NO** |
| `C7` | 7 | 7 | 1 | 1 | 49/25 | `24/25` | yes |
| `K_{3,3}` | 6 | 9 | 0 | 2 | 36/25 | **`−14/25`** | **NO** |
| `M?AE@bH{AYN_LgBs?` | 14 | 32 | 7 | 10 | 196/25 | **`−54/25`** | **NO** |
| `C5[7,7,12,7,12]` | 45 | 385 | 49 | `≥170` | 81 | **`≤ −89`** | **NO** |

`Φ*` is the *largest* potential the axioms allow (Theorem 1). It is negative on 7 of the 11
mandated witnesses, so **no nonnegative potential exists**: the mechanism is dead, and the
smallest witness is `C5[2]`.

## 5. Theorem 4 (why: a counting identity), and the `1/8` barrier

> **Theorem 4.** In any deletion ordering, `Σ_i d_{G_i}(v_i) = |E|` (each edge is removed
> exactly once, at its first-deleted endpoint), hence
> ```
>   V(G)  ≥  (|E| − N)/2      for every graph.
> ```
> Therefore the amortised mechanism with the greedy insertion cost can succeed only on
> graphs with `|E| ≤ 2N²/25 + N`. The extremal family has `|E| = N²/5`, and
> `5n² > 2n² + 5n ⟺ n ≥ 2`, so it fails on `C5[n]` for **every** `n ≥ 2`.

Exact numbers at the smallest witness: `C5[2]` has `|E| = 20`, `N = 10`,
`(|E| − N)/2 = 5 > 4 = N²/25`, and the exact DP gives `V = 6`.

> **Theorem 4′ (the `1/8` barrier).** `V(K_{m,m}) ≥ (m² − 2m)/2 = N²/8 − N/2` while
> `bip(K_{m,m}) = 0`. Hence `sup_G V(G)/N² ≥ 1/8 − o(1)` over triangle-free `G`, and the
> amortised mechanism **cannot prove `bip ≤ cN²` for any `c < 1/8`** — whatever the
> potential. Since `1/8 > 1/23.5 > 1/25`, the mechanism is behind the published literature.

Exact DP values: `V(K_{2,2}) = 1`, `V(K_{3,3}) = 2`, `V(K_{4,4}) = 5`, `V(K_{5,5}) = 8`,
`V(K_{6,6}) = 13`, `V(K_{7,7}) = 18` (`V/N² = 1/16, 1/18, 5/64, 2/25, 13/144, 9/98 ↗ 1/8`).

## 6. Corollary: exactly what the global potential buys

* **Plain (un-amortised) one-step induction** succeeds at `G` iff
  `⌊δ(G)/2⌋ ≤ (2N−1)/25`, i.e. essentially `δ ≤ 4N/25`. (This is the known A9 death,
  tight at `C5[7t,2t,7t,7t,2t]` with `δ = 4N/25`.)
* **Amortised with an arbitrary `Φ ≥ 0`** requires (Theorem 4) `|E| ≤ 2N²/25 + N`, hence
  `δ ≤ d̄ = 2|E|/N ≤ 4N/25 + 2`.

So the entire effect of the global potential is to replace a **minimum**-degree hypothesis
by an **average**-degree hypothesis at the *same* threshold `4N/25`, up to an additive `2`
in the degree. It does not move the threshold at all, and the extremal family sits at
`δ = 2N/5 = 10N/25`, a factor `2.5` past it.

Census gate (`R9_discharge_census.py`, all triangle-free graphs, exact):

| `n` | graphs | `V ≤ N²/25` | plain step works | max `|E|/N²` where mechanism works | max `δ − 4N/25` there |
|---|---|---|---|---|---|
| 9 | 1380 | 1289 | 944 | 14/81 | 39/25 |
| 10 | 9832 | 9409 | 6347 | 17/100 | 7/5 |

(The two counts differ only by the additive `O(1)` slop, which at `N ≤ 10` is the whole
budget: `4N/25 = 1.6` at `N = 10`. The counting bound `V ≥ (|E|−N)/2` and the soundness
bound `V ≥ bip` were asserted on all 11 212 census graphs and never failed.)

## 7. What a working process would have to look like (and why no formula does it)

By Theorem 3 the mechanism's moves at `C5[n]` must be *exactly* tight. Exhaustive exact
search over all removal vectors `k` (`k_i` vertices from class `i`, all `n ≤ 12`,
371 292 vectors at `n = 12`) shows:

> The **only** removals whose true `bip`-drop fits the quadratic budget
> `(N² − (N−|k|)²)/25` are the balanced ones `k = (j,j,j,j,j)`, and those are tight:
> drop `= n² − (n−j)² =` budget, ratio exactly `1`. Every unbalanced removal overshoots.

So the process is forced to **peel balanced transversal sets** — in particular a
single-vertex deletion never fits, and the smallest admissible move is a 5-set (e.g. an
induced transversal pentagon) with required cost exactly

```
   c(C5[n], pentagon) = 2n − 1 = (2N − 5)/5 ,
```

while the greedy insertion cost of any 5-set there is `5·⌊2n/2⌋ = 5n`. The required
improvement factor is `5n/(2n−1) → 2.5`, which is the same `1/10 → 1/25` factor as
everywhere else in this problem.

**Blocking step, verbatim.** A cost function beating greedy insertion must upper-bound
*"the number of edges from the deleted set `S` to the monochromatic side of an optimal cut
of `G − S`"* without computing that cut; supplying it is equivalent to computing `bip(G)`
from `bip(G−S)`, which is the circular instantiation of §3. No formula in `(G, S)` is known
between the two, and by Theorem 2 any such formula still yields a statement at least as
strong as the conjecture.

---

## 8. Theorem 5 — a global potential does **not** rescue static local-cut discharging

A static discharging proof fixes the maximum cut `(A,B)` and reasons from local data. Using
`s(v)`/`o(v)` for the number of neighbours of `v` on the same/other side and
`σ(v) = o(v) − s(v)`, the exact identity is

```
   bip(G) = |E|/2 − (1/4) Σ_v σ(v),        so the discharging target is
   Σ_v σ(v)  ≥  2|E| − 4N²/25              (equality at C5[n]: 6n² = 6n²).
```

Every local rule verified in bounded neighbourhoods can only use facts valid for *every*
locally optimal cut (`σ ≥ 0`). The global potential `Φ(G)` is a function of the graph, so it
cannot distinguish two cuts of the same graph.

> **Theorem 5.** Let `F` be **any** graph functional (any global potential). A scheme
> proving "*for every locally optimal cut `(A,B)`: `mono(A,B) ≤ F(G)`*" cannot prove
> `bip ≤ N²/25`.

*Proof (exact witness, re-verified here).* `G = C5[7,7,12,7,12]`, `N = 45`, `|E| = 385`,
`bip = min_i a_i a_{i+1} = 49 ≤ 81 = N²/25`. Take the class cut `A = V₀ ∪ V₂`
(`χ = (0,1,0,1,1)`). Its only monochromatic class pair is `(V₃,V₄)`, so
`mono = 7·12 = 84` and `25·mono = 2100 > 2025 = N²`. Its `σ`-vector per class is
`(19, 19, 14, 0, 0) ≥ 0`, so the cut is locally optimal and the scheme's hypothesis holds.
Hence `F(G) ≥ 84 > 81 = N²/25`, and at this very graph the scheme concludes only
`bip ≤ F(G) ≥ 84`. ∎

The smallest improving switch at that cut has size `11 = 0.2444·N`, flipping
`(1,0,0,0,10)` — one vertex of `V₀` and ten of `V₄` (exact, by enumeration over counting
vectors; vertices inside a class are twins so this is exhaustive).

In discharging language: the target `Σ_v σ(v) ≥ 2|E| − 4N²/25` is, at this cut,
`434 ≥ 446` — **false by exactly 12**, with every `σ(v) ≥ 0`. (At a *maximum* cut the
target holds on all 11 witnesses; verified in `R9_discharge_verify.py` (a) together with
the identity `bip = |E|/2 − (1/4)Σσ`.) So the deficit a global potential would have to
absorb is real and lives in a graph where the conjecture itself has slack `81 − 49 = 32`;
no functional of `G` can tell the two cuts apart.

## 9. How global the cut hypothesis must be — the locality radius

If a scheme's cut hypothesis is "no improving switch of size `≤ sN`", it is unusable below
the radius computed here. Exact scan over **all** `C5` blow-up shapes at each `N`, over all
32 class cuts, keeping the pairs with `σ ≥ 0` and `25·mono > N²`:

| `N` | violating locally-optimal class cuts | max radius | witness shape (`χ = (1,0,1,1,0)` throughout) | smallest improving switch |
|---|---|---|---|---|
| 10 | 20 | `3/10 = 0.3000` | `[0,2,3,2,3]` | `(0,0,0,2,1)` |
| 15 | 120 | `4/15 = 0.2667` | `[0,2,5,2,6]` | `(0,0,0,2,2)` |
| 20 | 290 | `1/4 = 0.2500` | `[0,3,6,3,8]` | `(0,1,4,0,0)` |
| 25 | 610 | `7/25 = 0.2800` | `[0,5,7,4,9]` | `(0,0,0,3,4)` |
| 30 | 1100 | `4/15 = 0.2667` | `[0,6,8,5,11]` | `(0,2,6,0,0)` |
| 35 | 2260 | `2/7 = 0.2857` | `[0,9,8,7,11]` | `(0,0,0,6,4)` |
| 40 | 3740 | `11/40 = 0.2750` | `[0,8,11,6,15]` | `(0,0,0,5,6)` |
| 45 | 5440 | `13/45 = 0.2889` | `[0,9,12,7,17]` | `(0,0,0,6,7)` |

The maximisers all have a **zero class**, i.e. they are `P4`-blow-ups (`bip = 0`) — the same
family as the known `W_b` witness, here pushed from `0.27N` to `0.2889N` at `N = 45`. Inside
the *genuine* `C5` blow-ups (no zero class) the record is the `A19` witness at `0.2444N`.

**Reading.** A discharging rule can only certify what it verifies locally; certifying
stability at radius `0.29N` means checking `≥ C(N, 0.29N)` switching sets. No bounded-radius
local rule does this, and by Theorem 5 no global potential substitutes for it.

## 10. Charging to 5-cycles

Exact pentagon census of the mandated witnesses (induced `C5`s, and induced `C7`s):

| graph | `N` | `bip` | `#` induced `C5` | `#` induced `C7` |
|---|---|---|---|---|
| `C5` | 5 | 1 | 1 | 0 |
| `C5[2]` | 10 | 4 | 32 | 0 |
| `C5[3,1,2,2,1]` | 9 | 2 | 12 | 0 |
| `C5[2,2,2,2,0]` | 8 | 0 | 0 | 0 |
| Petersen | 10 | 3 | 12 | 0 |
| Grötzsch | 11 | 4 | 31 | 0 |
| Wagner | 8 | 2 | 8 | 0 |
| `Γ₁₁` | 11 | 4 | 33 | 0 |
| **`C7`** | 7 | **1** | **0** | 1 |
| `K_{3,3}` | 6 | 0 | 0 | 0 |
| `M?AE@bH{AYN_LgBs?` | 14 | 7 | 92 | 0 |

> **Death.** `C7` has `bip = 1 > 0` and **zero** induced pentagons. Every scheme that
> distributes `bip` over induced pentagons — i.e. every bound of the form
> `bip ≤ Φ(pentagon structure)` with `Φ = 0` when there are none — is false on `C7`.

The mass form `ψ ≤ (Σ_{induced C5} Π_{v∈C} x_v)^{2/5}` (tight at `C5`, so the canonical
normalisation) fails, tested exactly at uniform weights via `ψ⁵ ≤ pentmass²`, on
**Petersen** (`ψ = 3/100`, pentmass `= 3/25000`), **Grötzsch**, **`C7`**, and
**`M?AE@bH{AYN_LgBs?`**. Repairing the scheme by charging to *all* odd cycles is the
covering/packing route (A5), already refuted at the same 14-vertex graph
(`bip = 7` vs fractional cover `32/5`, gap `35/32`).

## 11. The one global potential with the right shape — and why it is not new

The natural "global term that absorbs the deficit" is the **Motzkin–Straus deficit**
`Φ(x) = 1/4 − W(x) ≥ 0` (valid because `H` is triangle-free), `W(x) = Σ_{uv ∈ E} x_u x_v`.
Requiring tightness at *both* extremal points — `(W,ψ) = (1/5, 1/25)` on `C5[n]` and
`(W,ψ) = (1/4, 0)` on `K_{m,m}` — determines a **unique** linear certificate:

```
   ψ(H,x) + (4/5) W(x)  ≤  1/5           (MS-deficit certificate)
```

It survived every exact test run here: uniform weights on all 11 witnesses, 3300 random
exact rational weightings (denominators 5, 7, 11, 13, 20), and the blow-up family
(margin exactly `0` on every balanced `C5[n]`, `16/675` at `C5[7,7,12,7,12]`).

**But it is worthless**: it yields `ψ ≤ 1/25` only on `W ≥ 1/5`, i.e. `|E| ≥ N²/5`, and that
half is already closed by Erdős–Faudree–Pach–Spencer (1988), `bip ≤ |E| − 4|E|²/N²`
(both bounds vanish at `|E| = N²/4` and both give exactly `N²/25` at `|E| = N²/5`; the MS
line is very slightly stronger strictly between, e.g. `2/125` vs `23/1250` at
`|E| = 0.23N²`). The complementary low-density piece that would close the problem at the
crossing point — `ψ ≤ W/5`, i.e. `bip ≤ |E|/5` — is **FALSE** on the mandated 14-vertex
witness: `bip = 7 > 32/5`. Nothing here touches the open band `N²/20 < |E| < N²/5`.

---

## 12. What died, on which witness

| shape | killed by | exact witness |
|---|---|---|
| (S1) amortised deletion, any `Φ ≥ 0`, greedy cost | Theorems 1+4 | `C5[2]`: `Φ* = 4 − 6 = −2 < 0`; `(\|E\|−N)/2 = 5 > 4` |
| (S1) same, on the extremal family | Theorem 4 | `C5[n]`, all `n ≥ 2` (`5n² > 2n² + 5n`) |
| (S1) same, general strength ceiling | Theorem 4′ | `K_{m,m}`: `V ≈ N²/8`, `bip = 0` ⟹ no constant below `1/8` |
| (S1) exact-cost / edge-deletion variants | Theorem 2 | `U = bip` identically (verified on 10 witnesses): circular |
| (S1) set deletion of any size | Theorem 3 + exhaustive removal scan | only balanced peels fit, all exactly tight; needed cost `2n−1` vs greedy `5n` |
| (S2) local cut hypotheses + any global potential | Theorem 5 | `C5[7,7,12,7,12]`, class cut `{c₀,c₂}`: `σ = (19,19,14,0,0) ≥ 0`, `25·mono = 2100 > 2025` ⟹ `F(G) ≥ 84 > 81` |
| (S2) bounded-size switching hypotheses | locality radius scan | `C5[0,9,12,7,17]`, `N = 45`: no improving switch below `0.2889N` |
| (S3) charging to induced pentagons | pentagon census | `C7`: `bip = 1`, zero induced pentagons |
| (S3) pentagon-mass form | exact evaluation | Petersen, Grötzsch, `C7`, `M?AE@bH{AYN_LgBs?` |
| MS-deficit global potential | subsumed | consequence = published dense half `\|E\| ≥ N²/5`; the complementary piece `bip ≤ \|E\|/5` is false at `M?AE@bH{AYN_LgBs?` |

**Not killed (out of scope of this mechanism):** nothing in this round bears on the
conjecture's truth. Every witness above satisfies `25·bip ≤ N²`.

## 13. Files

| file | content |
|---|---|
| `R9_discharge_lib.py` | exact library: graph6, witnesses, `bip`, `ψ`, `W`, subset DP, pentagons, `σ`, switching |
| `R9_discharge_dp.py` | Theorems 2–4: `V` table, `C5[n]`, `K_{m,m}`, circularity check, removal-vector scan |
| `R9_discharge_local.py` | Theorem 5 gate (`A19` witness), first locality scan, pentagon charging |
| `R9_discharge_radius.py` | exact locality-radius scan, `N = 10 … 45` |
| `R9_discharge_msline.py` | MS-deficit certificate, 3300 exact rational weightings, EFPS comparison |
| `R9_discharge_census.py` | triangle-free census gate (`n = 9, 10`), soundness + counting assertions |
| `R9_discharge_verify.py` | final gate: `σ`-identity, `A19` deficit, Theorem-1 step check on all subgraphs, `Φ*` table |

Reproduce: `python R9_discharge_dp.py`, `python R9_discharge_local.py`,
`python R9_discharge_radius.py`, `python R9_discharge_msline.py`,
`python R9_discharge_census.py`, `python R9_discharge_verify.py`
(all in this directory; total runtime ≈ 25 min).
