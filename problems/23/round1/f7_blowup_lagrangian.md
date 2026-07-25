# Erdős #23 — Family F7 (blow-up reduction / Lagrangian)

**Author key:** `f7_blowup_lagrangian`
**Directory:** `E:/Projects/ErdosProblems/problems/23/round1/`
**Date:** 2026-07-25

Notation. `G` is a finite simple graph, `N = |V(G)|`, `e(G) = |E(G)|`,
`bip(G) = e(G) − maxcut(G) = min_{σ:V→{±1}} #{monochromatic edges}`.
`a(N) = max{bip(G) : G triangle-free, |V(G)| = N}`.
Conjecture (Erdős–Faudree–Pach–Spencer): `a(N) ≤ N²/25`.
`H[n]` denotes the blow-up of `H` on `[k]` with class sizes `n = (n_1..n_k)` (class `i` an
independent set of size `n_i`, complete bipartite between classes joined in `H`).

Everything below that is asserted as PROVED has a complete proof here; everything asserted as
computed was computed in **exact integer / rational arithmetic** with the scripts in this
directory (commands given in §9). No floating point is on any acceptance path.

---

## Summary of results

| # | type | statement |
|---|------|-----------|
| 1 | PROVED | **Blow-up Cut Lemma**: `bip(H[n]) = min_{σ:V(H)→{±1}} Σ_{ij∈E(H), σ_i=σ_j} n_i n_j` — an optimal bipartition of a blow-up never has to split a class. |
| 2 | PROVED | `λ(C_n) = 1/n²` for every odd `n ≥ 5` (uniform weights, uniquely). C5 is the strict maximiser among odd cycles. |
| 3 | PROVED | **Homomorphism monotonicity**: `H → H'` implies `λ(H) ≤ λ(H')`. |
| 4 | PROVED | **If `G → C5` then `bip(G) ≤ min_i |V_i||V_{i+1}| ≤ N²/25` and `bip(G) ≤ e(G)/5`**, for every `N`, with equality in the first only if all five classes have size `N/5`. |
| 5 | PROVED | **Every triangle-free graph on ≤ 7 vertices is C5-colourable**; hence (with 3,4) `λ(H) ≤ 1/25` for all such `H`, `= 1/25` iff `H ⊇ C5`, `= 1/49` iff `H = C7`, `= 0` iff `H` bipartite. This settles F7(ii) **by proof**, not by search. |
| 6 | PROVED | `sup_N a(N)/N² = lim_N a(N)/N²`. Hence a proof of `bip ≤ (1/25+o(1))N²` automatically gives `bip ≤ N²/25` for **every** `N` — this problem has no "sufficiently large N" gap. |
| 7 | REFUTED | **Blow-up optimality is false at finite `N`.** `a(12) = 5`, but the best blow-up of any triangle-free base graph on `≤ 8` vertices at `N = 12` is `4`. Exactly two 12-vertex graphs attain `bip = 5`; they need 9 and 11 twin classes, and **neither is C5-colourable**. |
| 8 | REFUTED | The sharp companion inequality `5·bip(G) ≤ e(G)` (i.e. `maxcut ≥ 4e/5`), true for all C5-colourable `G` and an equality for every balanced `C5[n]`, the Petersen graph, and both `N=12` extremal graphs, is **false**. Smallest counterexamples: `N=12`, `e=19`, `bip=4`. Champion at `N=13`: 4-regular, `e=26`, `bip=6`, `maxcut/e = 10/13 < 4/5`. This kills the natural `(A)&(B)` two-inequality route. |
| 9 | OBSTRUCTION | **The blow-up / Lagrangian reduction is a rename (rule (a)).** `λ(H) ≥ bip(H)/|H|²` with uniform weights, so `sup_H λ(H) = sup_N a(N)/N²`: there is *no Lagrangian gap*, and "solve the finite optimisation for base graphs of order ≤ k" is literally the conjecture for every `k ≥ 5`. The only non-vacuous lever the blow-up view supplies is monotonicity under homomorphism (3), which does give the unconditional Theorem 4. |
| 10| DATA | Exact `a(N)` for `N ≤ 13`: `1,1,1,2,2,4,4,5,6` for `N=5..13` (exhaustive over all 10,193,061 2-connected triangle-free graphs on 13 vertices, plus block additivity). |

---

## 1. The Blow-up Cut Lemma (PROVED)

**Lemma 1.1 (block additivity).** If `B_1,…,B_r` are the blocks of `G` then `bip(G) = Σ_i bip(B_i)`.

*Proof.* `(≥)`: any 2-colouring of `G` restricts to each block, and the monochromatic edges are
partitioned among the blocks. `(≤)`: pick an optimal colouring of each block. Root the block-cut
tree and process blocks in BFS order; each newly processed block meets the already-coloured part in
at most one vertex, and globally flipping that block's colouring (which does not change its
monochromatic set) makes it agree there. The resulting colouring of `G` has `Σ_i bip(B_i)`
monochromatic edges. ∎

**Lemma 1.2 (Blow-up Cut Lemma).** For every graph `H` on `[k]` and all integers `n_i ≥ 0`,
```
bip(H[n])  =  min_{σ ∈ {±1}^k}   Σ_{ij ∈ E(H), σ_i = σ_j}  n_i n_j .
```
Equivalently: *some* maximum cut of a blow-up puts every class entirely on one side.

*Proof.* `(≤)` is clear: the class-respecting colourings realise exactly those values.

`(≥)` Fix any bipartition of `H[n]`. All vertices of a class are twins, so the number of
monochromatic edges depends only on the numbers `a_i` of class-`i` vertices on the `+` side; put
`b_i = n_i − a_i`. Then
```
M(a) = Σ_{ij ∈ E(H)} ( a_i a_j + b_i b_j ).
```
Substituting `s_i = a_i − b_i ∈ [−n_i, n_i]`, i.e. `a_i = (n_i+s_i)/2`, `b_i = (n_i−s_i)/2`,
```
a_i a_j + b_i b_j = ¼[(n_i+s_i)(n_j+s_j) + (n_i−s_i)(n_j−s_j)] = ½ (n_i n_j + s_i s_j),
```
hence
```
M = ½ [ Σ_{ij∈E(H)} n_i n_j  +  Σ_{ij∈E(H)} s_i s_j ].            (∗)
```
`H` has no loops, so the quadratic `Σ_{ij∈E} s_i s_j` contains **no** `s_i²` term: for fixed
`(s_j)_{j≠i}` it is an *affine* function of `s_i`. A function affine in each coordinate separately
attains its minimum over a box `Π_i [−n_i, n_i]` at a vertex of the box, i.e. at some `s` with
`s_i = ±n_i` for all `i`. Such an `s` corresponds to `a_i ∈ {0, n_i}`, an integral,
class-respecting bipartition. So the minimum over all bipartitions equals the minimum over
class-respecting ones. ∎

**Verification.** `python f7_blowup.py verify` builds the actual blow-up graph `H[n]`, computes its
`bip` by exhaustive enumeration of all `2^{|V|−1}` bipartitions, and compares with the formula:
*244 random pairs `(H,n)` tested, 0 failures.*

**Two immediate consequences.**
* `bip(G[t]) = t²·bip(G)` for the uniform blow-up (exact multiplicativity).
* Identity `(∗)` with `n ≡ 1` is the standard `maxcut ↔ ±1 quadratic form` identity; the content of
  Lemma 1.2 is that the *box relaxation* of the spins is attained at the corners, which is exactly
  why `bip` has a genuine finite-dimensional blow-up calculus.

---

## 2. The bip-Lagrangian and the absence of a Lagrangian gap

**Definition.** For a graph `H` on `[k]` and `x ∈ Δ_k = {x ≥ 0 : Σ x_i = 1}` set
```
f_H(x) = min_{σ ∈ {±1}^k}  Σ_{ij ∈ E(H), σ_i = σ_j} x_i x_j ,      λ(H) = max_{x ∈ Δ_k} f_H(x).
```
`f_H(x)` is the minimum monochromatic *weight*; equivalently
`f_H(x) = min { Σ_{ij∈T} x_i x_j : T ⊆ E(H), H − T bipartite }`.

**Proposition 2.1.** (i) For rational `x = n/N` (`n` integral, `Σn_i = N`), `f_H(n/N) = bip(H[n])/N²`;
hence `λ(H) = sup_n bip(H[n])/(Σ n_i)²`.
(ii) `λ(H) ≥ bip(H)/|V(H)|²` (take `x` uniform).
(iii) `sup{ λ(H) : H triangle-free } = sup_N a(N)/N²`.

*Proof.* (i) is Lemma 1.2 divided by `N²`. (ii) is (i) with `n ≡ 1`. (iii) `≥` by (ii); `≤` because
blow-ups of triangle-free graphs are triangle-free, so every `bip(H[n])/N²` is `≤ a(N)/N²`. ∎

**Corollary 2.2 (F7(iii), OBSTRUCTION).** *"`λ(H) ≤ 1/25` for every triangle-free `H`" is
equivalent to the Erdős conjecture.* In particular the Lagrangian formulation has **no gap** to
exploit, and the finite optimisation
`Λ_k := max{ λ(H) : H triangle-free, |H| ≤ k }`
satisfies `Λ_k ≥ a(k)/k²` and `Λ_k ↑ sup_N a(N)/N²`; proving `Λ_k = sup λ` for a fixed `k`
*is* the conjecture, for every `k ≥ 5`. See §7 for the full discussion.

---

## 3. `sup = lim`: the conjecture has no "large N" caveat (PROVED)

**Theorem 3.1.** `a(N)/N² → sup_M a(M)/M²` as `N → ∞`. Consequently, any proof of the asymptotic
statement `bip(G) ≤ (1/25 + o(1))N²` for triangle-free `G` implies `bip(G) ≤ N²/25` for **all** `N`
with no exceptions.

*Proof.* Fix `N` and let `G` be triangle-free on `N` vertices with `bip(G) = a(N)`. For `M ≥ N` put
`q = ⌊M/N⌋` and choose class sizes `n_i ≥ q` with `Σ n_i = M`. By Lemma 1.2,
```
bip(G[n]) = min_σ Σ_{mono} n_i n_j ≥ q² · min_σ #{mono} = q² a(N),
```
and `G[n]` is triangle-free on `M` vertices, so `a(M) ≥ q² a(N)` and
`a(M)/M² ≥ (qN/M)²·a(N)/N² → a(N)/N²` as `M → ∞`.
Hence `liminf_M a(M)/M² ≥ a(N)/N²` for every `N`, so `liminf ≥ sup ≥ limsup`. ∎

(Also: `a(M) ≥ ⌊M/5⌋²` for every `M`.)

This is worth stating because it removes exactly the failure mode that rule (b) of the task warns
about: for *this* problem an asymptotic theorem is automatically an all-`N` theorem.

---

## 4. Homomorphism monotonicity, odd cycles, and the C5-colourable case (PROVED)

**Lemma 4.1.** If there is a graph homomorphism `φ : H → H'`, then `λ(H) ≤ λ(H')`.

*Proof.* Given `x ∈ Δ(V(H))` define `x'_v = Σ_{u : φ(u)=v} x_u ∈ Δ(V(H'))`. Let `σ'` be a
2-colouring of `H'` with `f_{H'}(x') = Σ_{vv' mono} x'_v x'_{v'}`, and let `σ = σ' ∘ φ`. If
`uu' ∈ E(H)` is `σ`-monochromatic then `vv' := φ(u)φ(u') ∈ E(H')` (in particular `φ(u) ≠ φ(u')`) and
`vv'` is `σ'`-monochromatic. Distinct edges of `H` over the same `vv'` are distinct pairs
`(u,u') ∈ φ^{-1}(v) × φ^{-1}(v')`, so
```
f_H(x) ≤ Σ_{uu' σ-mono} x_u x_{u'} ≤ Σ_{vv' σ'-mono} ( Σ_{u↦v} x_u )( Σ_{u'↦v'} x_{u'} ) = f_{H'}(x').
```
Taking the max over `x` gives `λ(H) ≤ λ(H')`. ∎

**Theorem 4.2.** For every odd `n ≥ 5`, `λ(C_n) = 1/n²`, attained **only** at the uniform weighting.

*Proof.* Label `E(C_n) = {i(i+1) : i ∈ Z_n}`. Every 2-colouring of an odd cycle has an odd, hence
positive, number of monochromatic edges; and for each edge `e`, properly 2-colouring the path
`C_n − e` yields a colouring whose unique monochromatic edge is `e`. All terms `x_ix_j` are `≥ 0`,
so a colouring with `≥ 3` monochromatic edges is never better than the best single-edge one:
```
f_{C_n}(x) = min_{i ∈ Z_n} x_i x_{i+1}.
```
By AM–GM,
```
( min_i x_i x_{i+1} )^n ≤ Π_{i∈Z_n} x_i x_{i+1} = Π_i x_i² ≤ ( (Σ_i x_i)/n )^{2n} = n^{−2n},
```
so `f_{C_n}(x) ≤ n^{−2}`, with equality throughout iff all `x_i` are equal. ∎

So among odd cycles, `C5` is the strict maximiser: `λ(C5) = 1/25 > 1/49 = λ(C7) > 1/81 = λ(C9) > …`.

**Theorem 4.3 (C5-colourable graphs, all `N`).** Let `G` admit a homomorphism to `C5` (equivalently
`χ_c(G) ≤ 5/2`), with colour classes `V_1,…,V_5` (so `G ⊆ C5[|V_1|,…,|V_5|]`). Then
```
bip(G) ≤ min_{i ∈ Z_5} |V_i| |V_{i+1}| ≤ N²/25 ,        bip(G) ≤ e(G)/5 .
```
Equality `bip(G) = N²/25` forces `|V_i| = N/5` for all `i`.

*Proof.* Fix `i ∈ Z_5`. The 2-colouring of `C5` that is proper on `C5 − {i,i+1}` (put `V_i, V_{i+1}`
on one side and the other three classes alternately) pulls back to a 2-colouring of `G` whose
monochromatic edges all lie in `E(V_i, V_{i+1})`; hence `bip(G) ≤ |E(V_i,V_{i+1})| ≤ |V_i||V_{i+1}|`.
The five sets `E(V_i,V_{i+1})`, `i ∈ Z_5`, partition `E(G)`, so averaging the five bounds gives
`bip(G) ≤ e(G)/5`. Finally by AM–GM
```
( min_i |V_i||V_{i+1}| )^5 ≤ Π_{i∈Z_5} |V_i||V_{i+1}| = ( Π_i |V_i| )² ≤ (N/5)^{10}. ∎
```

This is unconditional and holds for every `N` (so it is not a finite verification), but it is of
course a statement about a *class* of graphs. Equivalently, `λ(G) ≤ λ(C5) = 1/25` by Lemmas 4.1–4.2.

**Remark.** The second bound `bip ≤ e/5` extends verbatim to all `G` with `χ_f(G) ≤ 5/2`: if `I` is a
random independent set from a fractional colouring covering every vertex with probability `≥ 2/5`,
then `Pr[e meets I] ≥ 4/5` for every edge `e` (the two endpoint events are disjoint), and the cut
`(I, V∖I)` leaves only edges missing `I` monochromatic. This covers e.g. all Kneser graphs
`K(3k−1,k)` and the Petersen graph, which are **not** `C5`-colourable.

---

## 5. F7(ii), settled by proof: the maximiser over base graphs on ≤ 7 vertices

**Theorem 5.1.** Every triangle-free graph on at most 7 vertices admits a homomorphism to `C5`.

*Proof (exhaustive, exact).* `geng -t -q n | f7_c5col.exe` decides `H → C5` by backtracking over the
5 colours with vertex 0 pinned (`C5` is vertex-transitive), for all triangle-free graphs on
`n = 4,…,9` vertices:

| `n` | # triangle-free graphs | # NOT C5-colourable |
|----|----|----|
| 4 | 7 | 0 |
| 5 | 14 | 0 |
| 6 | 38 | 0 |
| 7 | 107 | 0 |
| 8 | 410 | **4** |
| 9 | 1897 | 35 |

(The decision procedure was cross-checked against a brute-force enumeration of all `5^{n−1}` maps in
`networkx` for the 4 graphs of order 8 and for `C5`, `C7`, `K_{3,3}`, Petersen.) ∎

**Theorem 5.2 (complete classification for `|H| ≤ 7`).** Let `H` be triangle-free with `|H| ≤ 7`. Then
```
λ(H) = 1/25   if H contains a 5-cycle      (maximiser: weight 1/5 on that C5, 0 elsewhere)
λ(H) = 1/49   if H = C7
λ(H) = 0      if H is bipartite.
```
In particular `max{λ(H) : H triangle-free, |H| ≤ 7} = 1/25`, attained by `C5` with uniform weights —
**F7(ii) as asked, and with a proof rather than a search.**

*Proof.* Upper bound: Theorem 5.1 + Lemma 4.1 + Theorem 4.2 give `λ(H) ≤ λ(C5) = 1/25`.
If `H` is bipartite, `f_H ≡ 0`. Otherwise `H` has odd girth 5 or 7. If the odd girth is 7 then
`H ⊇ C7` and `|H| = 7`, so `H = C7` (a chord of `C7` joins vertices at distance 2 or 3, creating a
triangle or a 5-cycle), and Theorem 4.2 applies. If `H ⊇ C5` then the 5 vertices of that cycle induce
exactly `C5` (any chord would create a triangle), so putting `x ≡ 1/5` on them and `0` elsewhere gives
`f_H(x) = f_{C5}(uniform) = 1/25`; combined with the upper bound, `λ(H) = 1/25`. ∎

**Where the proof stops.** The four smallest non-C5-colourable triangle-free graphs have 8 vertices:
```
G?q`qg   (10 edges)   GCQb`o (10 edges)   GCR`r_ (11 edges)   GCrb`o (12 edges)
```
`GCrb`o` is the cubic one: the Wagner graph `V8 = C8(1,4)` = Andrásfai graph `And(3)`
(`χ_c = 8/3 > 5/2`). Beyond order 7, Theorem 4.3 no longer covers everything.

---

## 6. F7(i): blow-up optimality is FALSE at finite `N` (REFUTED, exhaustive)

Exhaustive computation over **all** 2-connected triangle-free graphs (nauty `geng -t -C`),
`bip` computed exactly by Gray-code enumeration of all `2^{n−1}` bipartitions
(engine cross-checked against an independent Python brute force on 325 graphs, 0 mismatches):

| `n` | # 2-conn. triangle-free | `a₂(n) = max bip` | # extremal | an extremal graph |
|----|----|----|----|----|
| 5 | 2 | 1 | 1 | `DUW` = `C5` |
| 6 | 6 | 1 | 1 | `ECxo` |
| 7 | 16 | 1 | 8 | `F?bro` |
| 8 | 78 | 2 | 7 | `G?q`qg` |
| 9 | 415 | 2 | 60 | `H?AAFo}` |
| 10 | 3 374 | **4** | **1** | `I?rFf_{N?` = `C5[2]` |
| 11 | 35 860 | 4 | 12 | `J?BD@g]Qvo?` |
| 12 | 524 386 | **5** | **2** | `K?ABBBwerwBw`, `K?BD@g]Qvo^?` |
| 13 | 10 193 061 | **6** | 8 | incl. `L??FFB_~?~^_Fw` = `C5[3,2,3,2,3]` |

With Lemma 1.1, `a(N) = max{ Σ_i a₂(n_i) : n_i ≥ 3, Σ_i (n_i − 1) ≤ N − 1 }`, giving

| `N` | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|----|---|---|---|---|---|---|---|----|----|
| `a(N)` | 1 | 1 | 1 | 2 | 2 | **4** | 4 | **5** | 6 |
| `N²/25` | 1.00 | 1.44 | 1.96 | 2.56 | 3.24 | **4.00** | 4.84 | 5.76 | 6.76 |
| best blow-up, base order ≤ 7 | 1 | 1 | 1 | 2 | 2 | 4 | 4 | **4** | 6 |

**Theorem 6.1 (blow-up optimality fails).** `a(12) = 5`, but
```
max{ bip(H[n]) : H triangle-free, |H| ≤ 8, Σ n_i = 12 } = 4 .
```

*Proof.* `≥ 4`: `C5[2,2,2,2,4]` has `bip = 4` (Lemma 1.2: `min(4,4,4,8,8) = 4`).
`a(12) = 5`: exhaustive, as above (the only block multiset reaching 5 under
`Σ(n_i−1) ≤ 11` with the `a₂` table is a single 12-vertex 2-connected block, so the two graphs listed
are *all* 12-vertex triangle-free graphs with `bip = 5`).
Now suppose `H[n] ` had `bip = 5` with `|H| ≤ 8` and `Σn_i = 12`. Then `H[n]` is a 12-vertex
triangle-free graph with `bip = 5`, hence isomorphic to `K?ABBBwerwBw` or `K?BD@g]Qvo^?`. But the
number of false-twin classes (vertices with equal neighbourhoods) of a blow-up `H[n]` is at most
`|H| ≤ 8`, whereas these two graphs have **9** and **11** false-twin classes respectively (computed
directly; both have 25 edges). Contradiction. ∎

Additional structure of the `N = 12` extremal graphs (all exact):
* both have `e = 25 = 5·bip`, i.e. they meet `bip = e/5` exactly;
* `K?ABBBwerwBw` is the blow-up of the 9-vertex graph `HCRdR_w` with sizes `(1,2,2,1,2,1,1,1,1)`;
  `K?BD@g]Qvo^?` is the blow-up of the 11-vertex graph `J?BD@g]Qvo?` (itself `bip`-extremal at
  `N = 11`) with sizes `(1,…,1,2)`;
* **neither is C5-colourable.** So at `N = 12` the extremal graphs lie entirely outside the reach of
  Theorem 4.3, and outside the blow-up-of-small-graph paradigm.

**Interpretation (honest).** This refutes the *finite-`N`* form of the F7 premise ("the extremal
graph is a blow-up of a small triangle-free graph"). It does **not** refute the asymptotic form: by
Prop. 2.1 the asymptotic question is `sup_H λ(H)`, and `N = 12` merely exhibits the slack
`5 < 144/25` available when `5 ∤ N`. The right lesson is that no finite-`N` optimality statement can
be used as a stepping stone; only the limit object `λ` matters, and that is Corollary 2.2.

---

## 7. F7(iii): what the reduction would need — and why it is a rename

To reduce the conjecture to a finite optimisation one must prove, for some explicit `k`:

> **(R_k)** `sup{ λ(H) : H triangle-free } = Λ_k := max{ λ(H) : H triangle-free, |H| ≤ k }`.

By Proposition 2.1(iii) the left side equals `sup_N a(N)/N² = lim_N a(N)/N²` (Theorem 3.1), and
`Λ_5 = λ(C5) = 1/25` (Theorem 4.2), `Λ_7 = 1/25` (Theorem 5.2). Therefore, for every `k` with
`Λ_k = 1/25` — i.e. every `k` for which the finite optimisation has the "right" answer —
```
(R_k)   ⟺   a(N) ≤ N²/25 for all N   ⟺   the Erdős conjecture.
```
**`(R_k)` is exactly of conjecture strength.** This is the F7 obstruction, and by rule (a) it means
the Lagrangian/blow-up reduction is a *rename*: the Motzkin–Straus mechanism has no analogue here,
because there is no gap between the Lagrangian and the original problem (Prop. 2.1(ii): uniform
weights already realise `bip(H)/N²`). Concretely, the Motzkin–Straus miracle is that
`max_{x∈Δ} Σ_{ij∈E} x_ix_j` depends only on `ω(G)` — a *single small parameter*; here
`λ(H)` is a genuinely `H`-dependent quantity with `λ(H) ≥ bip(H)/|H|²`, so no bounded family of base
graphs can dominate all of them without that domination *being* the theorem.

Two things in this circle of ideas are **not** vacuous and are recorded above:
1. Lemma 4.1 (homomorphism monotonicity) — a property the unweighted formulation does not have,
   and the source of the unconditional Theorem 4.3;
2. Theorem 3.1 (`sup = lim`) — which converts any asymptotic bound into an all-`N` bound.

**Consequent structural reduction of the search space** (proved, but note rule (e)): any
counterexample `H` to `λ(H) ≤ 1/25` may be assumed to be a triangle-free **core** with
`χ_c(H) > 5/2`, since cores are hom-equivalent to their graphs and `C5`-colourable graphs are
excluded by Theorem 4.3.

---

## 8. The two-inequality route, and its exact refutation

Both of the following are equalities for **every** balanced blow-up `C5[n]` (`e = 5n²`,
`bip = n²`, `N = 5n`), and their conjunction would give the conjecture, because they cross exactly
at `e = N²/5`:

* **(A)** `5·bip(G) ≤ e(G)` (i.e. `maxcut ≥ 4e/5`)
* **(B)** `5·bip(G) + 4·e(G) ≤ N²` (i.e. `bip ≤ (4/5)(N²/4 − e)`; a stability form of Mantel)

Indeed `min( e/5, (N²−4e)/5 )` is maximised at `e = N²/5`, where it equals `N²/25`.

**(A) is TRUE for C5-colourable graphs** (Theorem 4.3) and for `χ_f ≤ 5/2` (Remark in §4), and it
is an equality for `C5[n]`, for the Petersen graph (`e=15`, `bip=3`), and for both `N=12` extremal
graphs (`e=25`, `bip=5`).

**Theorem 8.1 (A is REFUTED).** There are triangle-free graphs with `5·bip > e`. Exhaustively over
2-connected triangle-free graphs (`bip` exact):

* `n ≤ 11`: no counterexample (`5·bip ≤ e` always).
* `n = 12`: **exactly 10** counterexamples among 2-connected triangle-free graphs — the complete list
  (`e`, `bip`):
  ```
  K??E@_qi?]Ia  e=18 bip=4      K?AAD?WNBHCs  e=18 bip=4        <- champions, bip/e = 2/9
  K??EDbGIaYAe  e=19 bip=4      K?AA@agRPw@w  e=19 bip=4
  K?AA@b@ZDcPW  e=19 bip=4      K?AA@bGNAY@w  e=19 bip=4
  K?AAD?WXHLN_  e=19 bip=4      K?ABA`ocdQBo  e=19 bip=4
  K?ABAaIs?{TG  e=19 bip=4      K?`D@POd@wAw  e=19 bip=4
  ```
  (all verified triangle-free with `bip = 4` by independent exhaustive Python enumeration).
* `n = 13`: `max(5·bip − e) = 4`, attained by the **4-regular** triangle-free graph
  `L?`DAboUdIF_Bo` with `e = 26`, `bip = 6`, so
  ```
  maxcut / e = 20/26 = 10/13 = 0.769… < 4/5 .
  ```
  (Independently re-verified by exhaustive Python enumeration of all `2^{12}` bipartitions:
  `n=13, e=26, triangles=0, bip=6`. Also `L?`DE`gl@YJODg`: `e=26`, `bip=6`.)

Since `bip` and `e` are both additive over blocks (Lemma 1.1), these are counterexamples among all
triangle-free graphs, not just 2-connected ones. Hence **the (A)&(B) route is dead**. (Consistent
with the literature: Alon's sharp `maxcut ≥ m/2 + Θ(m^{4/5})` for triangle-free graphs indicates
`sup bip/e = 1/2` over all triangle-free graphs, so (A) fails badly for large sparse graphs; the
computation above locates the *smallest* failure exactly.)

**(B) survived every test** (stated as a conjecture, **not** claimed as progress — rule (e)):

* exhaustively true for all triangle-free graphs on `N ≤ 13` vertices
  (max of `5bip + 4e − N²` over 2-connected graphs: `−27` at `n = 13`; the block reduction
  `(n₁−1)+(n₂−1)+1 ⟹ n₁²+n₂² ≤ N²` transfers it to all graphs);
* true on **all blow-ups** of all 573 triangle-free base graphs of order `≤ 8`, at
  `N ∈ {12,17,25,37}` (this covers infinitely many `N`), with maximum ratio exactly `1`;
* equality cases found: balanced complete bipartite `K_{a,a}` (Mantel) and balanced `C5[n]`;
* it implies Mantel, and it implies `bip ≤ N²/25` **whenever `e ≥ N²/5`**; it says nothing when
  `e < N²/5`, so it is strictly weaker than the conjecture in the sparse regime and strictly
  stronger in the dense regime — the two are incomparable;
* since `bip ≤ e/2` always, (B) can only fail for `e > 2N²/13 ≈ 0.1538N²`, and with the published
  bound `bip ≤ 0.0409N²` it can only fail for `e/N² > 0.198875`. So (B) is precisely "the conjecture
  in the dense regime, plus a linear trade-off down to the Mantel point".

---

## 9. Counterexample search: `λ(H) > 1/25` (nothing found)

A single triangle-free `H` with `λ(H) > 1/25` would **disprove the conjecture** (blow up `H`; by
Prop. 2.1 the blow-ups have `bip/N² → λ(H)`). By Theorem 4.3 only non-C5-colourable `H` can qualify,
so the search was restricted to exactly those. `λ` lower bounds were obtained by exact-integer
hill-climbing over class-size vectors `n` (`bip(H[n]) = min_σ Σ_{mono} n_in_j`), for
`Σ n_i ∈ {20, 60, 150}`; every reported value is an exact rational **lower** bound for `λ(H)`.

* **All 6 958 non-C5-colourable 2-connected triangle-free graphs on 8, 9, 10, 11 vertices**
  (4 + 23 + 376 + 6 555): best value found `= 1/25` exactly, attained by graphs containing a `C5`
  (as Theorem 5.2 predicts). **No `H` exceeded `1/25`.**
* Named graphs (`λ ≥` exact rational lower bounds):

  | `H` | `λ(H) ≥` | decimal |
  |----|----|----|
  | `C5` | `1/25` | 0.040000 |
  | Wagner `V8 = C8(1,4)` | `1/25` | 0.040000 |
  | Grötzsch `= M(C5)` (11 v.) | `1/25` | 0.040000 |
  | `C13(1,3)` | `1/25` | 0.040000 |
  | `C11(1,3)` | `29/800` | 0.036250 |
  | `C13(1,5)` | `3601/102400` | 0.035166 |
  | `C16(1,6)` | `21/640` | 0.032813 |
  | Petersen | `201/6400` | **0.031406** (vs `bip/N² = 3/100 = 0.03` at uniform weights) |
  | `C7` / `C9` / `C11` | `1/49` / `1/81` / `1/121` (Thm 4.2, exact) | 0.020408 / 0.012346 / 0.008264 |

  Note the Petersen entry: non-uniform class sizes *do* beat the uniform blow-up
  (`0.03141 > 0.03`), so the natural guess "vertex-transitive ⟹ uniform is optimal" is false; but it
  remains well below `1/25`.

This is a negative result and is reported as such: a lower-bound search cannot certify
`λ(H) ≤ 1/25`, so no upper-bound claim is made for the 6 958 non-C5-colourable graphs. The window
left by the literature is `(0.04, 0.0409]`, which is very thin.

---

## 10. Scripts and exact commands

All in `E:/Projects/ErdosProblems/problems/23/round1/`. `GENG = E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe`.

| file | purpose |
|----|----|
| `f7_bip.cpp` | exact `bip` by Gray-code enumeration of all `2^{n−1}` bipartitions; prints max and all argmax graphs |
| `f7_check_bip.py` | cross-check of the above against an independent Python brute force (325 graphs, 0 mismatches) |
| `f7_ratios.cpp` | exhaustive test of (A) `5bip ≤ e` and (B) `5bip + 4e ≤ N²` with per-graph early exit |
| `f7_c5col.cpp` | decides `H → C5` (backtracking, vertex 0 pinned) |
| `f7_blowup.py` | brute-force **verification of the Blow-up Cut Lemma**; best-blow-up tables `B_k(N)` |
| `f7_lambda.py` | `λ` lower bounds by exact-integer hill-climbing; named graphs and bulk scans |
| `f7_ineqB.py` | tests (B) over all blow-ups of all triangle-free base graphs of order `≤ k` |

```bash
clang++ -O3 -march=native -o f7_bip.exe    f7_bip.cpp
clang++ -O3 -march=native -o f7_ratios.exe f7_ratios.cpp
clang++ -O3 -march=native -o f7_c5col.exe  f7_c5col.cpp

python f7_check_bip.py                                   # engine cross-check
python f7_blowup.py verify                               # Blow-up Cut Lemma, 244 random (H,n)
for n in 5 6 7 8 9 10 11 12 13; do $GENG -t -C -q $n | ./f7_bip.exe; done      # a2(n) + extremals
for n in 5 6 7 8 9 10 11 12 13; do $GENG -t -C -q $n | ./f7_ratios.exe; done   # (A),(B)
for n in 4 5 6 7 8 9;           do $GENG -t    -q $n | ./f7_c5col.exe; done    # C5-colourability
$GENG -t -C -q 10 | ./f7_c5col.exe --list-bad > bad10.txt                      # etc. for 8,9,11
python f7_lambda.py named
python f7_lambda.py scan bad8_10.txt 20,60,150
python f7_lambda.py scan bad11.txt   20,60
python f7_blowup.py detail 7 16                          # best blow-up per N
python f7_ineqB.py 8 12,17,25,37                         # (B) on all blow-ups
```

Runtime note: the `n = 13` sweeps read all 10 193 061 2-connected triangle-free graphs
(`geng -t -C 13`, 4.6 s to generate) and take a few minutes each with early exit.

---

## 11. Where I got stuck — the exact missing statement

The one place where the F7 machinery gets real traction is Theorem 4.3, and it stops **exactly** at
`C5`-colourability. What is missing is an upper bound for `λ` on the complement of that class:

> **Missing statement.** *There is no known handle on `λ(H)` for triangle-free `H` with
> `χ_c(H) > 5/2` (equivalently `H ↛ C5`), other than the trivial `λ(H) ≥ bip(H)/|H|²`.*
> Concretely I could not prove, for any single non-C5-colourable triangle-free `H`, an upper bound
> `λ(H) < 1/25`, not even for `H = ` the Petersen graph — where the exact value of
> `λ(Petersen) = max_{x∈Δ_10} min_{T} Σ_{ij∈T} x_i x_j` (`T` ranging over the inclusion-minimal
> edge sets whose deletion leaves the Petersen graph bipartite) is unknown to me; I only have
> `201/6400 ≤ λ(Petersen) ≤ 1/20`, the upper bound coming from the crude linear certificate
> `λ(H) ≤ t*(H)/4` where `t*(H) = 1/5` is the LP value
> `min_{μ ∈ Δ(𝒯)} max_{e ∈ E} Pr_μ[e ∈ T]` and `1/4 = max_{x∈Δ}Σ_{ij∈E}x_ix_j` (Motzkin–Straus).

Why the obvious certificates fail, precisely: a *linear* certificate (a distribution `μ` over
bipartite-ising edge sets, giving `f_H(x) ≤ Σ_e Pr_μ[e∈T]·x_ix_j`) can never prove `λ ≤ 1/25` for a
graph attaining it, because already for `C5` it yields only `1/5 · 1/4 = 1/20`. The certificate that
*is* tight for `C5` is **geometric** (AM–GM over the five minimal sets, Theorem 4.2), and I have no
general mechanism producing an AM–GM/SONC certificate for an arbitrary family of minimal
bipartite-ising sets. Producing such a mechanism — e.g. proving

> for every triangle-free `H` there is a family `T_1,…,T_m` of edge sets with `H − T_j` bipartite,
> and weights `μ_j ≥ 0`, `Σμ_j = 1`, such that `Π_j ( Σ_{ij∈T_j} x_ix_j )^{μ_j} ≤ (Σ_i x_i)²/25`

— is, as far as I can see, the smallest concrete object that would turn §4 into a general proof; for
`C5` it is exactly the AM–GM step, and for `C5`-colourable graphs it is the pullback of that step.
I could not construct it for `V8`, the Petersen graph, or the two `N = 12` extremal graphs, and I did
not determine whether such a certificate always exists (if it does not, that is itself a clean
obstruction worth recording next round).

Secondary loose ends:
* (B) `5bip + 4e ≤ N²` is unproved (verified `N ≤ 13` + all blow-ups of base order `≤ 8`). A proof
  of (B) would settle the conjecture for all `e ≥ N²/5`; the remaining sparse regime would still be
  open, so (B) alone is not sufficient.
* No rigorous upper bound on `λ(H)` was computed for the 6 958 non-C5-colourable graphs scanned in
  §9; only exact lower bounds. Certified upper bounds there would upgrade §9 from "search found
  nothing" to "the conjecture holds for all blow-ups of triangle-free graphs of order ≤ 11", which
  is an infinite family strictly beyond the published `N ≤ 200` verification.
