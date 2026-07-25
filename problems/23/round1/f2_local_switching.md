# Erdős #23, family F2: local switching and discharging

**Author key:** `f2_local_switching`
**Date:** 2026-07-25
**Scripts (this directory):** `switch_lib.py`, `p4_obstruction.py`, `c5_tight_sets.py`,
`c5_tight_profiles.py`, `witness_verify.py`, `witness_odd.py`, `lemma_check.py`,
`edge_ratio_search.py`.  All acceptance-path arithmetic is exact integer arithmetic;
no floating point is used in any claim (floats appear only in printed diagnostics).

---

## 0. Setting and notation

`G` is a finite simple triangle-free graph, `N = |V(G)|`. Fix a **maximum cut** `(V_0,V_1)`;
`B` = crossing edges, `M` = monochromatic edges, so `bip(G) = |M|`.
For `v ∈ V`, `d_B(v)`, `d_M(v)` are the numbers of `B`- and `M`-edges at `v` and

> `σ(v) = d_B(v) − d_M(v)`.

For `S ⊆ V`, `σ(S) = #{B-edges with exactly one end in S} − #{M-edges with exactly one end in S}`
is the **switch loss**: switching `S` changes the cut size by `−σ(S)`. Maximality of the cut is
*equivalent* to `σ(S) ≥ 0` for all `S ⊆ V`. `e_B(S)`, `e_M(S)` denote the numbers of `B`- resp.
`M`-edges with **both** ends in `S`.

Everything below is stated for an arbitrary cut; where maximality is used it is said explicitly.

---

## 1. The switch calculus (three identities) — PROVED

**Lemma 1 (decomposition).** For every `S ⊆ V`,
> `σ(S) = Σ_{v∈S} σ(v) − 2 e_B(S) + 2 e_M(S)`.

*Proof.* In `Σ_{v∈S} σ(v)` a `B`-edge with exactly one end in `S` is counted once with sign `+1`,
a `B`-edge with both ends in `S` twice with sign `+1`; symmetrically for `M`-edges with sign `−1`.
Hence `Σ_{v∈S}σ(v) = σ(S) + 2e_B(S) − 2e_M(S)`. ∎

**Lemma 2 (additivity and complementation).**
(a) If `S = S_1 ⊔ S_2` with no `G`-edge between `S_1` and `S_2`, then `σ(S) = σ(S_1) + σ(S_2)`.
(b) `σ(S) = σ(V∖S)`.

*Proof.* (a) Both `e_B, e_M` and the boundary counts split. (b) `S` and `V∖S` produce the same
new bipartition, hence the same change in cut size; alternatively the boundary edge sets coincide. ∎

Consequence of 2(a): **only sets inducing a connected subgraph give binding constraints**, and the
switching family is closed under taking connected components.

**Lemma 3 (mass identity).** `4|M| = 2|E| − Σ_{v} σ(v)`.

*Proof.* `d_M(v) = (d(v) − σ(v))/2`, so `2|M| = Σ_v d_M(v) = (2|E| − Σ_vσ(v))/2`. ∎

So the conjecture `|M| ≤ N²/25` is *arithmetically* the statement `Σ_v σ(v) ≥ 2|E| − 4N²/25`.
(This is bookkeeping, not progress; it is recorded only because every bound below is produced
in this form.)

*Machine check:* `lemma_check.py` verifies Lemma 1, Lemma 3, `σ(v) ≥ 0` and Lemma A below on
**every maximum cut** of **all 355 connected triangle-free graphs on ≤ 8 vertices** (nauty `geng -t -c`)
plus 300 random triangle-free graphs on 9–13 vertices: 655 graphs, 1387 maximum cuts, 0 failures.

---

## 2. Lemma A: the sharp star inequality — PROVED

The vertex inequality is `σ(v) ≥ 0`. The star inequality quoted in the task,
`σ({v} ∪ N_B(v)) = σ(v) + Σ_{a∈N_B(v)} σ(a) − 2 d_B(v) ≥ 0`, is **not** the strongest form,
because a `B`-neighbour `a` with `σ(a) > 2` *weakens* it. Optimising the neighbour set gives:

> **Lemma A (sharp star).** Let `G` be triangle-free and `(V_0,V_1)` a maximum cut. Then for every
> vertex `v`,
> ```
> Σ_{a ∈ N_B(v)}  max(2 − σ(a), 0)   ≤   σ(v).
> ```
> Equivalently: `σ(v) + Σ_{a∈A}(σ(a) − 2) ≥ 0` for **every** `A ⊆ N_B(v)`.

*Proof.* Fix `A ⊆ N_B(v)` and put `S = {v} ∪ A`. Since `G` is triangle-free, `N(v)` is independent,
hence `A` is independent, so the only edges inside `S` are the `|A|` edges from `v` to `A`, and all of
them lie in `B`: `e_B(S) = |A|`, `e_M(S) = 0`. Lemma 1 gives
`σ(S) = σ(v) + Σ_{a∈A} σ(a) − 2|A| ≥ 0`, i.e. `σ(v) ≥ Σ_{a∈A}(2 − σ(a))`.
Choosing `A = {a ∈ N_B(v) : σ(a) < 2}` maximises the right-hand side. ∎

**Corollary A1 (matching structure of the low-`σ` set).** Put `Z = {v : σ(v) ≤ 1}`,
`Z_0 = {σ(v)=0}`, `Z_1 = {σ(v)=1}`. Then
* no vertex of `Z_0` has a `B`-neighbour in `Z`;
* every vertex of `Z_1` has at most one `B`-neighbour in `Z`, and it lies in `Z_1`.

Hence **the `B`-edges induced on `Z` form a matching, all of whose ends have `σ = 1`.**

*Proof.* Immediate: each `a ∈ N_B(v) ∩ Z` contributes at least `2 − σ(a) ≥ 1` to the left side of
Lemma A, and `≥ 2` if `σ(a) = 0`. ∎

**Corollary A2 (a proved bound).** At a maximum cut of a triangle-free graph,
> `4|M| ≤ 2|E| − Σ_{a ∈ Z_0} d(a) − Σ_{a ∈ Z_1} (d(a)+1)/2`.

*Proof.* Summing Lemma A over all `v` and exchanging the order of summation,
`Σ_v σ(v) ≥ Σ_a (2−σ(a))^+ d_B(a) = Σ_{a∈Z_0} 2 d_B(a) + Σ_{a∈Z_1} d_B(a)`.
If `σ(a)=0` then `d_B(a) = d(a)/2`; if `σ(a)=1` then `d_B(a) = (d(a)+1)/2`. Insert into Lemma 3. ∎

This is a genuine improvement on the trivial `|M| ≤ |E|/2`: on the extremal graph `C5[n]` it gives
`|M| ≤ 1.5 n²` instead of `2.5 n²` (see §5 for the exact shortfall).

---

## 3. Task (ii): the tight sets of `C5[n]`, exactly, for all `n` — PROVED

Let `C5[n]` have parts `V_1,…,V_5` in cyclic order, each of size `n`. Take the canonical maximum cut
```
side 0 = V_1 ∪ V_3 ,      side 1 = V_2 ∪ V_4 ∪ V_5 ,
```
so `B` = pairs `(1,2),(2,3),(3,4),(5,1)` and `M = V_4 × V_5` (`|M| = n² = N²/25`).
Consecutive parts induce complete bipartite graphs, so `σ(S)` depends only on the profile
`x_i = |S ∩ V_i|`, and with `f_{ij} = x_i(n−x_j) + x_j(n−x_i)`:

> **`σ(S)/2 = n(x_1+x_2+x_3) − x_1x_2 − x_2x_3 − x_3x_4 − x_5x_1 + x_4x_5`.**  (★)

(Direct expansion of `f_{12}+f_{23}+f_{34}+f_{51}−f_{45}`; note the `n`-coefficients of `x_4,x_5` cancel.)

**Proposition 3.1 (maximality with equality analysis).** `σ(S) ≥ 0` for all `S`, and `σ(S) = 0`
exactly for the following `10n` profiles (`0 ≤ t ≤ n`):
```
(0,0,0,0,t)   (0,0,0,t,0)   (0,0,t,n,0)   (0,t,n,n,0)   (t,n,n,n,0)
(n,n,n,n,t)   (n,n,n,t,n)   (n,n,t,0,n)   (n,t,0,0,n)   (t,0,0,0,n)
```
(the second row is the complement of the first).

*Proof.* Two regroupings of (★):
```
(G1)  σ/2 = x_1(n−x_2) + x_2(n−x_3) + x_3(n−x_4) + x_5(x_4−x_1)
(G2)  σ/2 = x_3(n−x_2) + x_2(n−x_1) + x_1(n−x_5) + x_4(x_5−x_3)
```
((G2) is (G1) under the reflection `4↔5, 3↔1` which preserves (★)). If `x_4 ≥ x_1`, all four terms of
(G1) are `≥ 0`. If `x_5 ≥ x_3`, all four terms of (G2) are `≥ 0`. Otherwise `x_4 < x_1` and `x_5 < x_3`;
then the complement `x' = (n−x_i)` satisfies `x'_4 > x'_1`, and `σ(S) = σ(V∖S)` by Lemma 2(b), so (G1)
applies to `x'`. This proves `σ ≥ 0`.

Equality: in the case `x_4 ≥ x_1`, (G1) forces `x_1(n−x_2) = x_2(n−x_3) = x_3(n−x_4) = x_5(x_4−x_1) = 0`.
If `x_1 = 0`: either `x_4 = 0`, forcing `x_3 = 0` then `x_2 = 0`, giving `(0,0,0,0,x_5)`; or `x_4 > 0` and
`x_5 = 0`, giving `x_3 = 0 ⟹ x_2 = 0` i.e. `(0,0,0,x_4,0)`, or `x_4 = n` and then `x_2 = 0` or `x_3 = n`,
i.e. `(0,0,x_3,n,0)` and `(0,x_2,n,n,0)`. If `x_1 > 0`: `x_2 = n`, then `x_3 = n`, then `x_4 = n`, then
`x_5 = 0` or `x_1 = n`, i.e. `(x_1,n,n,n,0)` and `(n,n,n,n,x_5)`. The case `x_5 ≥ x_3` is the mirror
image, and the remaining case is handled by complementation, producing exactly the listed families. ∎

*Machine check.* `c5_tight_profiles.py` enumerates all profiles for `n = 1..7`: the number of tight
profiles is exactly `10n` (10, 20, 30, 40, 50, 60, 70), the list agrees with Proposition 3.1, and no
profile has `σ < 0`. `c5_tight_sets.py` does the harder check for `n = 1,2,3`: it enumerates **every**
maximum cut of `C5[n]` (all `2^{N−1}` bipartitions) and **every** subset `S` (all `2^N`). Results:
`bip(C5[n]) = n²` for `n = 1,2,3`; the numbers of maximum cuts (vertex `0` pinned to side `0`) are
`5, 15, 35`; and **every one of those maximum cuts has exactly the same number of tight sets**,
namely `10, 30, 70` for `n = 1,2,3` — matching Proposition 3.1, whose `10n` profiles carry
`Σ_profiles Π_i C(n, x_i) = 10, 30, 70` sets respectively.

**Reading of Proposition 3.1 (this is the answer to (ii)).** The tight sets are exactly the members of
**two maximal chains** in the subset lattice:
```
∅ ⊂ · · · ⊂ V_4 ⊂ V_4∪(part of V_3) ⊂ V_4∪V_3 ⊂ · · · ⊂ V_4∪V_3∪V_2∪V_1 ⊂ · · · ⊂ V
∅ ⊂ · · · ⊂ V_5 ⊂ V_5∪(part of V_1) ⊂ V_5∪V_1 ⊂ · · · ⊂ V_5∪V_1∪V_2∪V_3 ⊂ · · · ⊂ V
```
i.e. **sweeps around the pentagon starting at one end of the monochromatic pair**, one vertex at a time.
Consequences for a discharging scheme (which, to prove a sharp bound, may only put weight on
inequalities that are tight at `C5[n]`, up to `o(N²)` total slack):

* the only tight sets of size `< n` are subsets of `V_4` and of `V_5`; by Lemma 2(a) these are just sums
  of the vertex inequalities `σ(v) = 0` and carry **no information beyond `σ(v) ≥ 0`**;
* the smallest tight set that is *not* such a sum is `{v} ∪ V_4` for `v ∈ V_3` (equivalently `{v} ∪ V_5`
  for `v ∈ V_1`), of size `n+1` — precisely the **sharp star** set of Lemma A with `A = N_B(v) ∩ Z`;
* the ball `B(v,2)` for `v ∈ V_1` equals `V∖V_4` and is tight (profile `(n,n,n,0,n)`);
* `C5`-shaped sets (one vertex per part, profile `(1,1,1,1,1)`) have `σ = 2(3n−3)`: **slack `Θ(N)`**, so
  they must carry weight `0` in any asymptotically sharp scheme, for `n ≥ 2`;
* independent sets `V_1∪V_3` (profile `(n,0,n,0,0)`) have `σ = 4n²`: **slack `Θ(N²)`**, weight `0`;
* **no tight set contains a vertex of `V_2` unless it contains all of `V_3 ∪ V_4` (or all of `V_1∪V_5`).**
  This last point is the crux; see §5.

---

## 4. Task (i): the obstruction — CONSTRUCTED, exactly verified

### 4.1 A reduction that makes blow-ups finite — PROVED

**Lemma 4 (multilinearity / whole-part reduction).** Let `H` be a graph on `h` vertices with a
2-colouring `c`, let `G = H[n_1,…,n_h]` be the blow-up with the induced ("blow-up") cut, and put
`ε_{ij} = +1` if `c_i ≠ c_j`, `−1` if `c_i = c_j`. For `S ⊆ V(G)` with profile `x_i = |S ∩ P_i|`,
```
σ(S) = F(x) := Σ_{ij ∈ E(H)} ε_{ij} ( x_i(n_j − x_j) + x_j(n_i − x_i) ).
```
`F` is **affine in each `x_i` separately** (no `x_i²` occurs). Hence `min_{0≤x≤n} F` is attained at a
vertex of the box, i.e. at some `x` with `x_i ∈ {0, n_i}`. **Therefore the blow-up cut is maximum iff
`σ(U) ≥ 0` for the `2^h` sets `U` that are unions of whole parts**, and if some switch improves the cut
then some union of whole parts improves it.

*Proof.* The only terms containing `x_i` are `ε_{ij}(x_i n_j + x_j n_i − 2 x_i x_j)` for `j ∼ i`, each
affine in `x_i`; a multilinear function attains its extrema over a box at a vertex of the box. ∎

Lemma 4 says that for blow-ups the *needed* switch sets are exactly the unions of parts — sets of
**linear** size. The witnesses below are the quantitative form of this remark.

### 4.2 The witness `W_b`

> **Definition.** For `b ≥ 3` let `W_b = P_4[b+1, b, b, b+1]`, the blow-up of the path `p_1p_2p_3p_4`
> with part sizes `n_1 = n_4 = b+1`, `n_2 = n_3 = b`, and take the cut
> `V_0 = P_1 ∪ P_4`, `V_1 = P_2 ∪ P_3`.

Then `N = 4b+2`, `|E| = 3b²+2b`, `M = P_2 × P_3`, `|M| = b²`, and the vertex data is
`σ(v) = b` for `v ∈ P_1 ∪ P_4`, `σ(v) = 1` for `v ∈ P_2 ∪ P_3`.
From (Lemma 4's formula), for a profile `s = (s_1,s_2,s_3,s_4)`,
```
σ(s) = b(s_1+s_4) + s_2 + s_3 − 2 s_1 s_2 + 2 s_2 s_3 − 2 s_3 s_4.        (†)
```

> **THEOREM 4.1 (OBSTRUCTION).** For every `b ≥ 3`:
> 1. `W_b` is triangle-free (it is bipartite) and `25|M| = 25b² > (4b+2)² = N²`, i.e. **`|M| > N²/25`**;
>    `|M|/N² = b²/(4b+2)² → 1/16` as `b → ∞`.
> 2. `σ(S) ≥ 0` for **every** `S` with `|S| ≤ κ(b) − 1`, where
>    `κ(b) = min_{1 ≤ u ≤ b+1} ( ⌊b u/(2u−1)⌋ + 1 + u ) = b/2 + √b + O(1) = N/8 + Θ(√N)`,
>    and `κ(b)` is exactly the size of the smallest improving switch set.
> 3. `σ(S) ≥ 0` for every `S` in each of the following families:
>    single vertices; **all sharp stars** `{v} ∪ A`, `A ⊆ N_B(v)` (hence all star inequalities and all of
>    Lemma A); open neighbourhoods `N(v)`; closed neighbourhoods `N[v]`; **balls `B(v,2)`**;
>    edge neighbourhoods `N[u] ∪ N[v]`; **all independent sets**; all `C5`-shaped sets (vacuous: `W_b`
>    has no `C5`); each single part.
>
> **Consequently, for every family `𝓕` of switch sets contained in the union of the families in 2. and 3.,
> the implication “`σ(S) ≥ 0` for all `S ∈ 𝓕(G)` `⟹` `|M| ≤ N²/25`” is FALSE.**
> No discharging scheme whose only input is `σ(S) ≥ 0` over such an `𝓕` can prove the conjecture.

*Proof of 1.* `P_4` is bipartite hence triangle-free, and a blow-up of a triangle-free graph is
triangle-free. `25b² > (4b+2)² ⟺ 5b > 4b+2 ⟺ b > 2`. ∎

*Proof of 2.* By (†) the cross term `+2s_2s_3` is non-negative, so a profile with `σ < 0` and minimum
`Σ s_i` has `s_2 = 0` or `s_3 = 0`; by the symmetry `(s_1,s_2) ↔ (s_4,s_3)` assume `s_1 = s_2 = 0`. Then
`σ = b s_4 + s_3 − 2 s_3 s_4 < 0 ⟺ s_3(2s_4 − 1) > b s_4 ⟺ s_3 > b s_4/(2 s_4 − 1)`, so the least
`Σ s_i` equals `κ(b)`. Calculus on `u ↦ bu/(2u−1) + u` gives the minimum at `2u−1 = √b`, value
`(√b+1)²/2 = b/2 + √b + 1/2`. ∎

*Proof of 3.* Each family is checked exactly, and the check is by profile, which suffices because all
vertices of a part are twins. E.g. the sharp star at `v ∈ P_1`: `A ⊆ N_B(v) = P_2`, `|A| = t ≤ b`, and
`σ({v}∪A) = σ(v) + Σ_{a∈A}σ(a) − 2t = b + t − 2t = b − t ≥ 0`, with equality iff `t = b`;
at `v ∈ P_2`: `A ⊆ P_1`, `σ = 1 + t·b − 2t = 1 + t(b−2) ≥ 0` for `b ≥ 2`. `B(v,2) = P_1∪P_2∪P_3` for
`v ∈ P_1` (`σ = b(b+1) > 0`) and `= V` for `v ∈ P_2 ∪ P_3` (`σ = 0`). Independent sets are subsets of
`P_1∪P_3`, `P_1∪P_4`, `P_2∪P_4` or of one part; e.g. for `S ⊆ P_1∪P_3`, (†) gives
`σ = b s_1 + s_3 ≥ 0`. `witness_verify.py` performs all of these checks mechanically over **all**
profiles. ∎

*Machine verification.* `p4_obstruction.py` brute-forces **all `2^N` subsets** for `b = 2,3,4` (the
`min |S|` with `σ<0` equals `⌊n/2⌋+2` in the uniform version `P_4[n,n,n,n]`, and `κ(b)` in the
`(b+1,b,b,b+1)` version) and the profile formula for larger `b`; `witness_verify.py` prints, for
`b = 3,4,6,8`: `25|M| > N²` (e.g. `b=3`: `N=14, |M|=9, 225 > 196`), all named families satisfied, and
the smallest improving set (`b=3`: `|S| = 5 = 0.357N`; `b=6`: `7 = 0.269N`; `b=8`: `8 = 0.235N`;
asymptotically `→ N/8`).

**Smallest instance:** `b = 3`: `W_3 = P_4[4,3,3,4]`, `N = 14`, `|E| = 33`, `|M| = 9 > 196/25 = 7.84`,
every switch set of size `≤ 4` has `σ ≥ 0`, and every set in every family of 3. has `σ ≥ 0`.

### 4.3 Honest caveats, and how far they can be repaired

`W_b` is bipartite, so `bip(W_b) = 0`: the cut exhibited is simply not maximum, and the conjecture
itself is of course not threatened. The obstruction is about **proof mechanisms**: a scheme that only
ever uses `σ(S) ≥ 0` for `S` in the listed families cannot distinguish `W_b` from a genuine extremal
configuration. A scheme is entitled to also use "`G` is not bipartite". Therefore:

> **THEOREM 4.2 (non-bipartite witness).** For odd `L ≥ 9` and `b ≥ L−1` let
> `W'_{L,b} = C_L[b, b+1, 1, 1, …, 1, b+1, b]` (parts `P_0 … P_{L−1}` in cyclic order, sizes
> `n_0 = n_{L−1} = b`, `n_1 = n_{L−2} = b+1`, the remaining `L−4` parts of size `1`), with the
> alternating colouring `c_i = i mod 2`, so that `(P_{L−1},P_0)` is the unique monochromatic pair.
> Then `W'` is connected, non-bipartite (odd girth `L`), triangle-free, `N = 4b+L−2`, `|M| = b² > N²/25`,
> and `σ(S) ≥ 0` for every `S` with `|S| < κ'(L,b)`, where `κ'(L,b)` is the exact smallest improving
> size, again `b/2 + √b + O(1) = N/8 + Θ(√N)`, and for every set in the families
> *vertices, all sharp stars, `N(v)`, `N[v]`, independent sets, single parts*.

Verified exactly by `witness_odd.py`:
`L=9, b=8`: `N=39`, `25·64 = 1600 > 1521 = N²`, `κ' = 9` (so all `|S| ≤ 8 = 0.205N` are non-negative);
`L=9, b=12`: `N=55`, `25·144 = 3600 > 3025`, `κ' = 11` (all `|S| ≤ 10 = 0.182N`);
`L=11, b=10`: `N=49`, `25·100 = 2500 > 2401`, `κ' = 10` (all `|S| ≤ 9 = 0.184N`).
Taking the disjoint union with `C5[m]` (`σ` is additive over components, Lemma 2(a)) gives a witness of
**odd girth 5** containing many `C5`'s, e.g. `W'_{9,15} ⊔ C5[1]`: `N = 72`, `|M| = 226 > 5184/25 = 207.4`.

**What `W'` does *not* defeat:** balls `B(v,2)` and edge neighbourhoods `N[u]∪N[v]`. Concretely, in
`W'_{9,b}` the ball `B(v,2)` for `v ∈ P_2` equals `P_0∪P_1∪P_2∪P_3∪P_4`, which contains one end of the
heavy monochromatic pair and not the other, and has `σ = 1 − b² < 0`. This is not an artefact of my
construction: **any** design in which a single heavy `M`-pair `(X,Y)` is supported by light structure
has some vertex at distance `2` from `X` and distance `≥3` from `Y`, and the corresponding ball
separates `X` from `Y` across a boundary of weight `≪ |X||Y|`. In `W_b` this cannot happen because the
pattern has diameter `3`, but the price is bipartiteness.

> **This is the sharp form of the answer to (i):** among the families named in the task —
> stars, star-neighbourhoods, balls of radius 2, independent sets, neighbourhoods of edges, `C5`-shaped
> sets, and *all* sets of size `o(N)` — **the only one that survives is the radius-2 ball (with the edge
> neighbourhood, which contains it up to one layer), and it survives only against non-bipartite
> witnesses.** A workable scheme must therefore (a) use switch sets of linear size, and (b) use
> non-bipartiteness essentially — and the only tight linear-size sets at `C5[n]` are the two sweep chains
> of Proposition 3.1, whose members are neither balls, nor stars, nor neighbourhoods, nor independent.

### 4.4 The exact value of the crudest levels

* **Level 1 (vertex inequalities only).** `σ(v) ≥ 0 ∀v` gives exactly `|M| ≤ |E|/2 ≤ N²/8`, and this is
  attained: `K_{m,m}` with the "wrong" balanced cut (`V_0` = half of each side) has `σ(v) = 0` for every
  `v`, `N = 2m` and `|M| = 2·(m/2)² = m²/2 = N²/8`. So the vertex family alone is worth exactly `N²/8`.
* **Level 2.** That example dies at `|S| = 2`: for a `B`-edge `uv`, `σ({u,v}) = σ(u)+σ(v)−2 = −2 < 0`.
* **Level `Θ(N)` (Theorem 4.1).** Still worth `≥ N²/16`.

So the local hierarchy is worth `N²/8 → … → ≥ N²/16`, against a target of `N²/25`. **The local
relaxation loses at least a factor `25/16 = 1.5625`.**

---

## 5. Task (iii): the strongest local bound, and exactly where it falls short

The strongest bound I can prove from the star family is **Corollary A2**:
`4|M| ≤ 2|E| − Σ_{Z_0} d(a) − Σ_{Z_1}(d(a)+1)/2`.

**Evaluation on the extremal graph.** For `C5[n]` with the canonical maximum cut:
`Z_0 = V_4∪V_5` (`2n` vertices of degree `2n`), `Z_1 = ∅`, `2|E| = 10n²`, so
```
Σ_v σ(v) ≥ 4n²      (Corollary A2 input)      while in truth   Σ_v σ(v) = 6n² ,
4|M| ≤ 10n² − 4n² = 6n²   i.e.   |M| ≤ 1.5 n² = 1.5 · N²/25 .
```
**The bound is off by exactly the factor `3/2`, and the deficit `2n²` in `Σσ` is concentrated
entirely on the `n` vertices of `V_2`** — the unique part not adjacent to the monochromatic pair.
Per-vertex slack in Lemma A (`σ(v) − Σ_{a∈N_B(v)}(2−σ(a))^+`):
```
v ∈ V_1 : 2n − 2n = 0     v ∈ V_2 : 2n − 0 = 2n     v ∈ V_3 : 2n − 2n = 0
v ∈ V_4 : 0 − 0  = 0      v ∈ V_5 : 0 − 0 = 0
```
So Lemma A is **tight at four of the five parts and useless at the fifth**, and the entire gap between
the local bound and the truth is the failure to charge `V_2`.

This is not a defect of my particular bound. By Proposition 3.1, **no tight set contains a vertex of
`V_2` unless it contains all of `V_3∪V_4` (or all of `V_1∪V_5`)**. Hence any sharp scheme must charge
`V_2` through an inequality supported on a set of size `≥ 2n + 1 = 2N/5 + 1`, namely a member of a sweep
chain such as `S_t = V_4 ∪ V_3 ∪ (t vertices of V_2)`; and by Theorem 4.1 no inequality of size `< N/8`
(nor any star/ball/neighbourhood/independent set) can substitute for it.

**The exact missing statement** (this is the hole I could not fill):

> Find a family `𝓕` of switch sets, defined in graph-theoretic terms for an arbitrary triangle-free `G`
> at a maximum cut, such that (α) every `S ∈ 𝓕` has `σ(S) = 0` on `C5[n]` — hence `𝓕` must consist of
> sweep sets, e.g. sets of the form `N_B(W) ∪ W ∪ A` for a suitable `W` and `A` — and (β) `𝓕` separates
> `W_b` (Theorem 4.1) and `W'_{L,b}` (Theorem 4.2) from genuine maximum cuts, i.e. some `S ∈ 𝓕(W_b)`
> has `σ(S) < 0`.

---

## 6. A sublemma that is *not* refutable at small size (recorded to save future effort)

`bip(G) ≤ |E|/5` for triangle-free `G` would imply the conjecture for every triangle-free graph with
`|E| ≥ N²/5`, and it is exactly tight for `C5`, `C5[n]` and the Petersen graph. `edge_ratio_search.py`
runs an exhaustive exact search (nauty `geng -t -c`, exact max cut):
```
n ≤ 10 (min degree ≥ 2)  and  n = 11,12 (min degree ≥ 3):  42 303 graphs,
max bip/|E| = 1/5 exactly, attained at C5 (n=5), n=8 (10 edges, bip 2),
Petersen (n=10, 15 edges, bip 3), n=11,12 (20 edges, bip 4);  NO graph with 5·bip > |E|.
```
So no small counterexample exists. (It must nevertheless fail for large sparse graphs, by Alon's
theorem that there are triangle-free graphs with `maxcut = m/2 + O(m^{4/5})`, whence
`bip = m/2 − O(m^{4/5}) > m/5`; that is a literature statement which I did **not** verify here. Note
such graphs have `m = o(N²)` and are therefore harmless for the `N²/25` conjecture.)

---

## 7. Summary of claims and their status

| # | Statement | Status |
|---|---|---|
| 1 | `σ(S) = Σ_{v∈S}σ(v) − 2e_B(S) + 2e_M(S)`; `σ` additive over components; `σ(S)=σ(V∖S)`; `4|M| = 2|E| − Σσ(v)` | **PROVED** (§1), machine-checked |
| 2 | **Lemma A**: `Σ_{a∈N_B(v)}(2−σ(a))^+ ≤ σ(v)` | **PROVED** (§2), machine-checked on 1387 maximum cuts |
| 3 | `B`-edges inside `{v : σ(v) ≤ 1}` form a matching with both ends of `σ` exactly 1 | **PROVED** (§2) |
| 4 | `4|M| ≤ 2|E| − Σ_{Z_0}d − Σ_{Z_1}(d+1)/2` | **PROVED** (§2) |
| 5 | Tight sets of `C5[n]` = two sweep chains, exactly `10n` profiles, all `n` | **PROVED** (§3), verified `n ≤ 7` (profiles) and `n ≤ 3` (all sets, all maximum cuts) |
| 6 | Blow-up cut is maximum ⟺ the `2^h` whole-part switches are non-negative | **PROVED** (§4.1) |
| 7 | `W_b = P_4[b+1,b,b,b+1]`: `|M| > N²/25` with all switch sets of size `< N/8`, all sharp stars, balls `B(v,2)`, edge neighbourhoods, independent sets non-negative | **CONSTRUCTED / OBSTRUCTION** (§4.2), exact |
| 8 | `W'_{L,b} = C_L[b,b+1,1,…,1,b+1,b]`: same but connected, non-bipartite, odd girth `L`; defeats everything except `B(v,2)` and `N[u]∪N[v]` | **CONSTRUCTED / OBSTRUCTION** (§4.3), exact |
| 9 | The local bound of #4 is off by exactly `3/2` on `C5[n]`, with the entire deficit `2n²` on `V_2` | **PROVED / exact** (§5) |
| 10 | No triangle-free graph with `5·bip > |E|` exists on `≤ 12` vertices (min degree `≥3`) / `≤ 10` (min degree `≥2`) | **COMPUTED**, exhaustive |
