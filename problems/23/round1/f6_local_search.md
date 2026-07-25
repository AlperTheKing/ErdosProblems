# Erdős #23 — Family F6 (algorithmic / local search)

**Target.** `G` triangle-free, `N = |V|`, `m = |E|`, `bip(G) = m − maxcut(G)`.
Conjecture: `bip(G) ≤ N²/25`, sharp at `C5[n]`.

All numbers below are exact integers / rationals. Scripts are in this directory; every
claim is either proved in full here or produced by an exhaustive computation whose
command line is given.

---

## 0. Notation: the move calculus

Fix a cut `(A,B)`. Write `M` for the set of monochromatic edges, and for a vertex `v`

* `d_M(v)` = #neighbours on `v`'s own side, `d_C(v)` = #neighbours on the other side,
* **surplus** `s(v) := d_C(v) − d_M(v)`.

For `S ⊆ V` let `Δ(S)` be the change in `|M|` when every vertex of `S` is moved to the
other side. Edges inside `S` and edges outside `S` keep their status; edges with exactly
one endpoint in `S` flip. Counting the edges inside `S` twice in `Σ_{v∈S} s(v)` gives

> **(0.1)  `Δ(S) = Σ_{v∈S} s(v) − 2·( cut_S − mono_S )`**,
> where `cut_S`, `mono_S` are the numbers of cut / monochromatic edges with **both**
> endpoints in `S`.

A cut is *locally optimal for a move class* `𝓒` iff `Δ(S) ≥ 0` for all `S ∈ 𝓒`.
Since `Σ_v s(v) = 2m − 4|M|`,

> **(0.2)  `|M| = m/2 − (1/4)·Σ_v s(v)`.**

Define `F_𝓒(N) = max{ |M(A,B)| : G triangle-free on N vertices, (A,B) a 𝓒-locally-optimal cut }`.
`F_𝓒(N)` is exactly *"the best bound on |M| that the move class 𝓒 alone implies"*: a
local-search algorithm using only moves from `𝓒` can terminate at `|M| = F_𝓒(N)`, and no
argument that uses only the inequalities `{Δ(S) ≥ 0 : S ∈ 𝓒}` plus triangle-freeness can
prove anything smaller.

---

## 1. PROVED — what each move class forces (part (i))

### 1.1 Single vertices
`Δ({v}) = s(v)`. Local optimality ⟺ `s(v) ≥ 0` for all `v`. By (0.2), `|M| ≤ m/2 ≤ N²/8`
(Mantel). **Exactly attained:** `G = K_{N/2,N/2}` with parts `X, Y` split into halves
`X = X₁⊔X₂`, `Y = Y₁⊔Y₂` of size `N/4`, and cut `A = X₁∪Y₁`, `B = X₂∪Y₂`. Then
`d_M(v) = d_C(v) = N/4` for every `v` (so `s ≡ 0`) and `|M| = 2·(N/4)² = N²/8`.

> **Vertex moves alone can never beat `|E|/2`, i.e. `N²/8 = 0.125 N²`; the value is attained.**

### 1.2 Pairs — the *only* new inequality is on cut edges
For `S = {u,v}`, (0.1) gives
* `uv ∉ E`: `Δ = s(u)+s(v) ≥ 0` — automatic;
* `uv ∈ M`: `Δ = s(u)+s(v)+2 ≥ 0` — automatic;
* `uv` a **cut edge**: `Δ = s(u)+s(v) − 2`.

> **Lemma 1.2.** A cut is pair-locally-optimal iff it is vertex-locally-optimal and
> `s(u)+s(v) ≥ 2` for every **cut** edge `uv`. In particular the set `{v : s(v)=0}` spans
> no cut edge, and no cut edge joins `s=0` to `s=1`.

Pairs still do not beat `N²/8`: take `K_{N/2,N/2}` as above and delete one perfect
matching between `X₁,Y₁` and one between `X₂,Y₂`. Now `s ≡ 1`, every cut edge has
`s(u)+s(v) = 2`, and `|M| = N²/8 − N/2`. (This is `G(p,1)` below.)

### 1.3 Neighbourhood moves are **vacuous** in triangle-free graphs
`G` triangle-free ⟹ `N(v)` is an independent set ⟹ `cut_{N(v)} = mono_{N(v)} = 0`, so by (0.1)

> **Proposition 1.3.** `Δ(N(v)) = Σ_{u∈N(v)} s(u) ≥ 0` automatically at any
> vertex-locally-optimal cut. **Flipping a neighbourhood is never an improvement.**

Confirmed computationally: `F_{N(v)}(N) = F_{|S|≤1}(N)` for every `N ≤ 12` (table in §5).

### 1.4 Closed neighbourhoods and the exact **star** inequality
`S = N[v]`: the only edges inside `S` are the `d(v)` edges at `v`, so
`cut_S − mono_S = s(v)` and `Δ(N[v]) = Σ_{u∈N(v)} s(u) − s(v)`.

More generally, for any `S = {v} ∪ T` with `T ⊆ N(v)`,
`Δ = s(v) + Σ_{u∈T∩N_C(v)} (s(u)−2) + Σ_{u∈T∩N_M(v)} (s(u)+2)`.
Since `s ≥ 0`, the minimising `T` is `{u ∈ N_C(v) : s(u) < 2}`. Hence the whole class of
`2^{d(v)}` star moves at `v` collapses to **one** exactly-optimisable inequality:

> **Proposition 1.4 (star inequality).** At a cut locally optimal for all moves
> `S ⊆ N[v]`, `v ∈ S`:
> **`s(v) ≥ Σ_{u ∈ N_C(v)} (2 − s(u))⁺` for every vertex `v`.**
> In particular: if some cut-neighbour of `v` has `s = 0` then `s(v) ≥ 2`; if `s(v)=1`
> then `v` has at most one cut-neighbour with `s ≤ 1` and none with `s = 0`.

### 1.5 General `k`-sets
`Δ(S) ≥ 0` for `|S| = k` is binding exactly when `S` induces many cut and few mono edges.
Since `G` is triangle-free, the extreme case is `S` inducing a **complete bipartite graph
of cut edges** `K_{a,b}` with `a+b = k`, forcing `Σ_{v∈S} s(v) ≥ 2ab`, worst at `a=b=k/2`:
`Σ_{v∈S} s(v) ≥ k²/2`. This is the mechanism exploited in §2.

---

## 2. OBSTRUCTION — every *bounded-size* move class is capped at `N²/8`

### The family `G(p,t)` (`0 ≤ t ≤ p`, `N = 4p`)
`V = X₁ ⊔ Y₁ ⊔ X₂ ⊔ Y₂`, each of size `p`. Put `X = X₁∪X₂`, `Y = Y₁∪Y₂` and take **all**
`X`–`Y` edges **except** the two circulants
`R_i = { x^i_a y^i_b : (b−a) mod p ∈ {0,…,t−1} }` (a `t`-regular bipartite graph inside
`X₁×Y₁` and inside `X₂×Y₂`).
`G(p,t)` is **bipartite** (`X` vs `Y`), hence triangle-free, and `bip(G(p,t)) = 0`.

**Cut:** `A = X₁ ∪ Y₁`, `B = X₂ ∪ Y₂`. Then `M = E(X₁,Y₁) ∪ E(X₂,Y₂)`, so

* `|M| = 2p(p−t) = N²/8 − tN/2`,
* `d_M(v) = p − t`, `d_C(v) = p`, hence **`s(v) = t` for every vertex `v`**.

> **Theorem B.** For every `S ⊆ V` with `|S| ≤ 2t`, `Δ(S) ≥ 0`; and for `t ≥ 1` there is
> an `S` with `|S| = 2t+1` and `Δ(S) < 0`.

*Proof.* Write `S = S∩X₁ ⊔ S∩Y₁ ⊔ S∩X₂ ⊔ S∩Y₂` with sizes `a₁,b₁,a₂,b₂`. There are no
edges inside `X` or inside `Y`; the cut edges inside `S` are exactly the `X₁–Y₂` and
`X₂–Y₁` pairs, all present, so `cut_S = a₁b₂ + a₂b₁`, and `mono_S ≥ 0`. By (0.1),
`Δ(S) ≥ t|S| − 2(a₁b₂ + a₂b₁)`. With `|S| = a₁+b₁+a₂+b₂` we have
`a₁b₂ + a₂b₁ ≤ |S|²/4` (maximised at `a₁ = b₂ = |S|/2`), so `Δ(S) ≥ t|S| − |S|²/2 ≥ 0`
whenever `|S| ≤ 2t`. Conversely take `t` vertices of `X₁` and `t+1` of `Y₂`:
`Δ = t(2t+1) − 2t(t+1) = −t < 0`. ∎

Exhaustively verified (all subsets up to size `2t+1`) for
`(p,t) ∈ {(2,1),(3,1),(3,2),(4,1),(4,2),(4,3),(5,1),(5,2),(6,2),(6,3)}` by
`python f6_family_Gpt.py` — the printed "first improving set has size `2t+1`" confirms
both halves exactly.

> **Corollary B1.** For every fixed `k`, `F_{|S|≤k}(N) ≥ N²/8 − ⌈k/2⌉·N/2` for all
> `N ≡ 0 (mod 4)` with `N ≥ 4⌈k/2⌉`. Hence
> **`lim_{N→∞} F_{|S|≤k}(N)/N² = 1/8` for every fixed `k`** (the upper bound `m/2 ≤ N²/8`
> is §1.1). *No bounded-size move class implies any bound better than `(1/8)N² − O_k(N)`.*

> **Corollary B2 (how large must moves be?).** Let `𝓒` be **any** move class all of whose
> members have size `≤ k`. If `k < 0.34·N − 1` then `𝓒` cannot certify `bip ≤ N²/25`:
> take `t = ⌈k/2⌉ < 0.17N`, and `G(N/4, t)` has a `𝓒`-locally-optimal cut with
> `|M| = N²/8 − tN/2 > N²/25`.
> (`N²/8 − tN/2 > N²/25 ⟺ t < 2N(1/8 − 1/25) = 17N/100`.)
> **Moves of size ≥ 17N/50 = 0.34N are necessary.**

### `G(p,2)` also defeats every *unbounded* "local" class one would write down
For `t = 2` the surplus is `s ≡ 2`, so by Prop. 1.4 the star inequality reads `2 ≥ 0`,
and every star move has `Δ = 2 + Σ_{u∈T}(s(u)−2) = 2 > 0`. Likewise
`Δ(N(v)) = 2d(v) > 0` and `Δ(N[v]) = 2d(v) − 2 > 0`.

> **Theorem B'.** For every `p ≥ 3`, the bipartite graph `G(p,2)` on `N = 4p` vertices has
> a cut with `|M| = N²/8 − N` which is locally optimal for **all** of:
> single vertices, pairs, triples, quadruples, every neighbourhood `N(v)`, every closed
> neighbourhood `N[v]`, and **every** star move `S ⊆ N[v]` — while `bip(G(p,2)) = 0`.
> `|M| = N²/8 − N > N²/25` for all `N ≥ 12`.

Verified for `p = 2..12` by `python f6_moveclasses.py` (prints
`minΔ_{|S|≤4} = 0`, `minΔ_star = 2`, `minΔ_{N(v)} = 4p−4`, `minΔ_{N[v]} = 4p−6`).
Independently, the exhaustive search over **all** 1 262 180 triangle-free graphs on 12
vertices gives `F_{ |S|≤4 & N(v) & N[v] & star }(12) = 6 = N²/8 − N`, matching Theorem B'
exactly and exceeding `N²/25 = 5.76`. **`N = 12` is the smallest `N` at which the full
local class fails.**

The improving set that *does* repair `G(p,t)` is `t` vertices of `X₁` plus `t+1` of `Y₂`,
i.e. **one side of a large bipartite block of cut edges**. So the only local-search moves
that can possibly work are "flip a balanced part of a cut-biclique", and these have size
linear in `N`.

---

## 3. PROVED — the neighbourhood-cut bound, and an unconditional density window

The one genuinely useful consequence of triangle-freeness for cutting is that
neighbourhoods are independent. For an independent set `I`, the cut `(I, V∖I)` has no
monochromatic edge inside `I`, and every edge meeting `I` has its other end outside `I`,
so its monochromatic edges are exactly `E(V∖I)`, of which there are `m − Σ_{u∈I} d(u)`.

> **Theorem A.** Let `G` be triangle-free with `N` vertices and `m` edges. Put
> `w(G) = max{ Σ_{u∈I} d(u) : I independent }` and `D_v = Σ_{u∼v} d(u)`. Then
>
> ```
> bip(G) ≤ min( ⌊m/2⌋ , m − w(G) ) ≤ m − max_v D_v ≤ m − (Σ_v d(v)²)/N ≤ m − 4m²/N² .
> ```
>
> Consequently **`bip(G) ≤ N²/16` for every triangle-free `G` and every `N`**, and
>
> **`bip(G) ≤ N²/25` whenever `m ≤ 2N²/25` or `m ≥ N²/5`.**

*Proof.* `bip ≤ ⌊m/2⌋`: a uniformly random cut makes each edge monochromatic with
probability `1/2`. `bip ≤ m − w(G)`: the independent-set cut above. `w(G) ≥ max_v D_v`:
`N(v)` is independent. `max_v D_v ≥ (1/N)Σ_v D_v = (1/N)Σ_u d(u)²` since each `u` is
counted `d(u)` times; and `Σ d² ≥ (Σd)²/N = 4m²/N` by Cauchy–Schwarz.
Write `x = m/N²` and `f(x) = x − 4x²`. Then `bip ≤ N²·min(x/2, f(x))`. For `x ≤ 1/8`,
`x/2 ≤ 1/16`; for `x ≥ 1/8`, `f` is decreasing so `f(x) ≤ f(1/8) = 1/16`. Hence
`bip ≤ N²/16`. Finally `x/2 ≤ 1/25 ⟺ x ≤ 2/25`, and `f(x) ≤ 1/25 ⟺ 4x² − x + 1/25 ≥ 0
⟺ x ≤ 1/20 or x ≥ 1/5`; since `1/20 < 2/25` the union of the two conditions is
`x ≤ 2/25` or `x ≥ 1/5`. ∎

Theorem A is elementary and I expect it is folklore (the published EFPS bound `N²/18` is
stronger; the current record is `0.0409N²`, Balogh–Clemen–Lidický). Its value here is that
it is **exactly the ceiling of the whole F6 method** and it is **exactly tight on the
extremal example**: for `C5[n]` (`N=5n`, `m=5n²`) one has
`m − max_v D_v = 5n² − 4n² = n² = N²/25`, and every inequality in the chain is an equality
(verified in `f6_moveclasses.py`). The extremal cut of `C5[n]` **is** a neighbourhood cut:
`A = N(v)` for `v ∈ V₁` gives `A = V₂∪V₅` and monochromatic set `E(V₃,V₄)`.

**What Theorem A leaves open** is precisely the density window

> **`2N²/25 = 0.08 N² < m < 0.2 N² = N²/5`.**

Every hard instance below sits inside it.

---

## 4. REFUTED — the independent-set-cut bound cannot prove the conjecture

`bip ≤ m − w(G)` is the strongest possible "neighbourhood-type" bound: it dominates every
inequality in Theorem A and is tight on `C5[n]` and on the Petersen graph. It is
nevertheless **false as a route to `N²/25`**. Exact witnesses (`python
f6_isbound_refutation.py`; Higman–Sims is *built from scratch* from the extended binary
Golay code — the script asserts the weight enumerator `1,759,2576,759,1` and re-derives
`srg(100,22,0,6)`; `α` is proved optimal by CP-SAT):

| graph | `N` | `m` | `α` | `w = ` max deg-weight IS | `m − w` | `(m−w)/N²` | `N²/25` | true `bip` |
|---|---|---|---|---|---|---|---|---|
| Wagner `C8(1,4)` | 8 | 12 | 3 | 9 | **3** | 3/64 = .046875 | 2.56 | 2 |
| Chvátal | 12 | 24 | 4 | 16 | **8** | 1/18 = .055556 | 5.76 | 4 |
| `C13(1,5)` (the (3,5)-Ramsey graph) | 13 | 26 | 4 | 16 | **10** | 10/169 = .059172 | 6.76 | 6 |
| Clebsch `srg(16,5,0,2)` | 16 | 40 | 5 | 25 | **15** | 15/256 = .058594 | 10.24 | 8 |
| Higman–Sims `srg(100,22,0,6)` | 100 | 1100 | 22 | 484 | **616** | 77/1250 = .061600 | 400 | ≤ 550 (Thm A) |

(For Higman–Sims the *combined* certificate is `min(⌊m/2⌋, m−w) = min(550, 616) = 550
= 0.055 N²`; the pure independent-set certificate `616 = 0.0616 N²` is within `1.5 %` of the
absolute ceiling `1/16 = 0.0625` of Theorem A, i.e. on this graph the neighbourhood /
independent-set idea extracts essentially nothing.)

Each row is an infinite family: for the balanced blow-up `H[n]`, `m`, `w` and `bip` all
scale by `n²` (Lemma 4.1), so the ratios above hold for arbitrarily large `N`.

> **Lemma 4.1 (blow-up).** For any graph `H` and `n ≥ 1`, `bip(H[n]) = n²·bip(H)`, and
> `w(H[n]) = n²·w(H)`, `m(H[n]) = n²·m(H)`.
> *Proof.* Vertices in one class of `H[n]` are pairwise non-adjacent with identical
> neighbourhoods. Fix an optimal cut and a class `K`; the sides of the vertices outside `K`
> being fixed, the monochromatic count is `const + Σ_{v∈K} c(side(v))` with the *same*
> function `c` for all `v ∈ K` (no edge lies inside `K`), so moving all of `K` to
> `argmin c` does not increase the count. Repeating over the classes yields an optimal cut
> in which every class is unsplit, i.e. one induced by a 2-colouring of `H`, of cost
> `n²·(#mono edges of H)`. Same argument for `w`. ∎
> Verified by brute force over **all** `2^{N−1}` cuts for `C5[1],C5[2],W8[1],W8[2]`
> (`f6_final_checks.py`).

> **Obstruction (sharp).** The best bound this whole family of arguments can ever give is
> `min(⌊m/2⌋, m − w(G))`. Its worst case over triangle-free graphs is pinned to
> **`[10/169, 1/16] = [0.05917, 0.0625]`**:
> * `≤ 1/16` by Theorem A;
> * `≥ 10/169 = 0.05917` on the blow-ups `C13(1,5)[n]`, where `min(⌊m/2⌋, m−w) = 10n²`
>   while the truth is `bip = 6n² = 0.0355 N²`.
>
> So **no argument using only random/locally-optimal cuts and independent-set cuts can
> prove `bip ≤ cN²` for any `c < 10/169 ≈ 0.0592`, i.e. for any constant within a factor
> `1.48` of the conjecture.**
>
> Exhaustive confirmation that `10/169` is the true optimum for `N ≤ 13`:
> `max_G min(⌊m/2⌋, m−w)/N²` = `.046875, .037037, .040000, .049587, .055556, .059172`
> for `N = 8,…,13`, attained at Wagner, —, —, —, Chvátal, `C13(1,5)`.

Note where these live: `m/N² = 3/16, 1/6, 2/13, 5/32, 11/100 = .1875, .1667, .1538, .1563,
.11` — **all strictly inside the window `(0.08, 0.2)` of Theorem A**. The window is exactly
where the problem is.

---

## 5. Computations (part (iii)) — exhaustive census, `N ≤ 13`

`geng -tq N | ./census.exe` (exact `bip` by Gray-code enumeration of all `2^{N−1}` cuts;
exact max-weight independent set by subset DP). Total 22 178 977 graphs.

| `N` | #triangle-free graphs | `max bip` | `⌊N²/25⌋` | `max bip / N²` | #extremisers |
|---|---|---|---|---|---|
| 3 | 3 | 0 | 0 | 0 | – |
| 4 | 7 | 0 | 0 | 0 | – |
| 5 | 14 | **1** | 1 | **1/25 = .0400** | **1** (`C5`) |
| 6 | 38 | 1 | 1 | .0278 | 3 |
| 7 | 107 | 1 | 1 | .0204 | 19 |
| 8 | 410 | 2 | 2 | .0313 | 7 |
| 9 | 1 897 | **2** | 3 | .0247 | 86 |
| 10 | 12 172 | **4** | 4 | **1/25 = .0400** | **1** (`C5[2]`) |
| 11 | 105 071 | 4 | 4 | .0331 | 14 |
| 12 | 1 262 180 | 5 | 5 | .0347 | 2 |
| 13 | 20 797 002 | 6 | 6 | .0355 | 8 |

**Answers to (iii).**
* The conjecture holds with room to spare for all `N ≤ 13`; `max bip = ⌊N²/25⌋` for every
  `N ≤ 13` **except `N = 9`, where `max bip = 2 < 3 = ⌊81/25⌋`.**
* The ratio `1/25` is attained **only** at `N = 5` and `N = 10`, and in each case by a
  **unique** graph: `C5` (`g6 = DUW`) and `C5[2]` (`g6 = I?rFf_{N?`, the 4-regular
  10-vertex graph, verified `C5`-homomorphic).
* **No non-blow-up graph ties the `C5[n]` ratio for any `N ≤ 13`.** The runner-up families
  are strictly below: the best non-`C5`-homomorphic extremisers are at `N = 12` (two
  graphs, `bip = 5`, ratio `.0347`) and `N = 13` (eight graphs, `bip = 6`, ratio `.0355`),
  neither homomorphic to `C5` or `C7`.

### Exact move-class values `F_𝓒(N)` (`geng -tq N | ./moves.exe`)

| `𝓒` \ `N` | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|
| `|S| ≤ 1` (vertices) | 8 | 8 | 12 | 12 | **18 = N²/8** |
| `|S| ≤ 2` | 4 | 5 | 8 | 8 | 12 |
| `|S| ≤ 3` | 2 | 3 | 5 | 6 | 9 |
| `|S| ≤ 4` | 2 | 2 | 4 | 4 | **6 = N²/8 − N** |
| `|S| ≤ 5` | 2 | 2 | 4 | 4 | – |
| `N(v)` moves | 8 | 8 | 12 | 12 | 18 |
| `N[v]` moves | 8 | 8 | 12 | 12 | 18 |
| cut-star `{v}∪N_C(v)` | 2 | 4 | 5 | 6 | 8 |
| all star moves `S ⊆ N[v]` | 2 | 3 | 4 | 6 | 8 |
| **all of the above combined** | 2 | 2 | 4 | 4 | **6** |
| `⌊N²/25⌋` | 2 | 3 | 4 | 4 | 5 |

Readings:
* `F_{N(v)} = F_{N[v]} = F_{|S|≤1}` at every `N` — Prop. 1.3, and `N[v]` adds nothing either.
* `F_{|S|≤1}(N) = ⌊N²/8⌋` exactly at `N ≡ 0 (mod 4)` (`N=8: 8`, `N=12: 18`) — §1.1.
* `F_{|S|≤4}(12) = 6 = N²/8 − N` — exactly `G(3,2)` of Theorem B'; `6 > 5.76 = N²/25`.
* The combined class first exceeds `N²/25` at `N = 12`, as Theorem B' predicts.

---

## 6. Part (ii) — the algorithm, its guarantee, and its exact stall

**Algorithm NC‑LS.**
1. `C₁ ←` single-vertex local search from an arbitrary cut. Guarantee `|M(C₁)| ≤ ⌊m/2⌋`.
2. `C₂ ←` the best independent-set cut `(I, V∖I)`; polynomial version: `I = N(v)` for the
   `v` maximising `D_v = Σ_{u∼v} d(u)`. Guarantee `|M(C₂)| = m − w(G) ≤ m − max_v D_v`.
3. Run single-vertex local search on both; output the better.

**Termination guarantee (proved, Theorem A):** `|M| ≤ min(⌊m/2⌋, m − 4m²/N²) ≤ N²/16`;
and `≤ N²/25` whenever `m ≤ 2N²/25` or `m ≥ N²/5`.

**Stall 1 — the bound.** The guarantee equals exactly `N²/16` iff `m = N²/8` and `G` is
`(N/4)`-regular. Explicit configuration: `G = K_{N/4,N/4} ⊔ K_{N/4,N/4}` (`N/4`-regular,
`m = N²/8`, `D_v = N²/16`), where the certificate is `N²/16` and the truth is `bip = 0`.
**Stall 2 — the bound, on genuinely non-bipartite graphs.** On `C13(1,5)[n]` the combined
certificate `min(⌊m/2⌋, m−w)` equals `10n² = 0.05917 N²` for every `n`, while the truth is
`bip = 6n² = 0.0355 N²` (Lemma 4.1). On `Higman–Sims[n]` the certificate is `0.055 N²`
(and the pure independent-set certificate `0.0616 N²`), while the conjecture asserts
`0.04 N²`. Neither can be driven lower by any amount of restarting.
**Stall 3 — the algorithm itself.** `G(p,2)` (§2) admits a cut with `|M| = N²/8 − N` that
is locally optimal for single vertices, pairs, triples, quadruples, every `N(v)`, every
`N[v]` and **every** star move — while `bip = 0`. Enlarging the move class to all sets of
size `≤ k` only replaces `G(p,2)` by `G(p,⌈k/2⌉)` and `|M| = N²/8 − ⌈k/2⌉N/2`.

**Conclusion for (ii).** There is no potential-decreasing local-search algorithm with
`O(1)`-size moves, nor with neighbourhood/star moves, whose termination guarantee is
`N²/25`; by Corollary B2 the moves must have size `≥ 0.34 N`, and by §4 the
independent-set restart cannot help below `0.0592 N²`. The unique surviving primitive
identified by the analysis is: *flip a balanced part of a large biclique of cut edges*.

---

## 7. Summary of what is established

| # | type | statement |
|---|---|---|
| 1 | PROVED | `Δ(S) = Σ_{v∈S}s(v) − 2(cut_S − mono_S)`; pairs give exactly `s(u)+s(v) ≥ 2` on cut edges; `N(v)`-moves are vacuous; the whole star class collapses to `s(v) ≥ Σ_{u∈N_C(v)}(2−s(u))⁺`. |
| 2 | PROVED | `bip(G) ≤ min(⌊m/2⌋, m−w(G)) ≤ m − 4m²/N² ≤ N²/16` for all triangle-free `G`, all `N`; equality throughout on `C5[n]` giving exactly `N²/25`. |
| 3 | PROVED | `bip(G) ≤ N²/25` unconditionally whenever `m ≤ 2N²/25` or `m ≥ N²/5`. |
| 4 | PROVED | `bip(H[n]) = n²·bip(H)` for balanced blow-ups. |
| 5 | CONSTRUCTED | `G(p,t)`: `Δ(S) ≥ 0` for all `|S| ≤ 2t`, improving set of size exactly `2t+1`, `|M| = N²/8 − tN/2`, `bip = 0`. |
| 6 | OBSTRUCTION | `F_{|S|≤k}(N)/N² → 1/8` for every fixed `k`; any move class of sets of size `< 0.34N` cannot certify `N²/25`. |
| 7 | OBSTRUCTION | `G(p,2)` additionally defeats all `N(v)`, `N[v]` and star moves, from `N = 12` on. |
| 8 | REFUTED | `bip ≤ m − w(G) ≤ N²/25` is FALSE: Wagner `3 > 2.56`, Chvátal `8 > 5.76`, `C13(1,5)` `10 > 6.76`, Clebsch `15 > 10.24`, Higman–Sims `616 > 400`. |
| 9 | OBSTRUCTION | worst case of `min(⌊m/2⌋, m−w)` lies in `[10/169, 1/16] = [.0592,.0625]` — never within a factor `1.48` of `1/25`. |
| 10 | COMPUTED | exhaustive census `N ≤ 13` (22 178 977 graphs): `max bip = ⌊N²/25⌋` except `N = 9`; ratio `1/25` only at `N = 5, 10`, uniquely by `C5`, `C5[2]`; no non-blow-up tie. |

## 8. Files / commands

```
f6_family_Gpt.py           Theorem B: exhaustive Delta(S) check on G(p,t)
f6_moveclasses.py          Theorem B': G(p,2) vs star/N(v)/N[v]/|S|<=4 ; Theorem A on C5[n],W8[n]
f6_isbound_refutation.py   Wagner/Chvatal/Clebsch/Higman-Sims; HiS built from the Golay code
f6_final_checks.py         C13(1,5) identification; blow-up lemma by full brute force
census.cpp / census.exe    exhaustive bip, m-Dmax, m-w, min(m/2,m-w)
moves.cpp  / moves.exe     exhaustive F_C(N) for all move classes
decode.py                  graph6 -> structure (degrees, girth, hom to C5/C7, exact bip)

clang++ -O3 -march=native -o census.exe census.cpp
clang++ -O3 -march=native -o moves.exe  moves.cpp
for n in 3..13: geng -tq $n | ./census.exe 12
for n in 5..12: geng -tq $n | ./moves.exe 5      # 4 for n=12
python f6_family_Gpt.py ; python f6_moveclasses.py ; python f6_isbound_refutation.py ; python f6_final_checks.py
```

## 9. Where I got stuck — the exact missing statement

Everything above is an upper-bound argument that uses only two facts: *some* cut is at
least as good as random (`m/2`), and *neighbourhoods are independent* (`m − w`). §4 proves
that these two facts **together cannot give a constant below `10/169 = 0.0592`**, and §2
proves that no bounded-size local move can help. The problem is confined to the density
window `0.08 N² < m < 0.2 N²`, and inside it the hard instances are highly symmetric
triangle-free graphs whose maximum independent sets are no larger than a neighbourhood
(`α = Δ`): Chvátal, Clebsch, `C13(1,5)`, `M22`, Higman–Sims.

The exact statement I could not prove, and which would close the gap between the F6
ceiling `1/16` and the conjecture, is:

> **Missing Lemma (the exact gap).** Let `G` be triangle-free, `2N²/25 < m < N²/5`, and let
> `I` be an independent set maximising `Σ_{u∈I} d(u) = w(G)`. The independent-set cut
> `(I, V∖I)` has `m − w(G)` monochromatic edges, all inside `H := G[V∖I]`, which is
> triangle-free on `N − |I|` vertices with `e(H) = m − w(G)` edges. I need
>
> **`bip(G) ≤ m − w(G) − γ(G)` with `γ(G) ≥ m − w(G) − N²/25`**,
>
> i.e. a *quantified* gain from re-cutting `H` and re-inserting `I` optimally. What I can
> prove is only the trivial `bip(G) ≤ (w(G) − e(I,V∖I)·0)/2 + bip(H)`-type recursion,
> which loses everything: at the critical density `m = N²/8`, `d = N/4` it returns
> `N²/32 + c·(3N/4)²`, which exceeds `cN²` for every `c < 1/18`, so it never improves on
> its own hypothesis.
>
> On `C5[n]`, `H = G − I` is *bipartite* and `γ = 0` suffices — the bound is already tight.
> On `C13(1,5)`, Clebsch, Chvátal, `M22`, Higman–Sims — exactly the graphs with `α = Δ`
> that populate the window — `H` is far from bipartite and I have **no** lower bound at all
> on `γ`. That single missing quantity, of size `≈ 0.02 N²` in the window
> `0.08 N² < m < 0.2 N²`, is the whole distance from `N²/16` to `N²/25`.

Quantitatively: I need `bip(G) ≤ m − w(G) − c·(something)` with a correction term of order
`0.02 N²` in the window. Neither local search (§2), nor iterating the independent-set cut
(the recursion `bip(G) ≤ D_v/2 + bip(G − N(v))` is self-defeating: at `m = N²/8`,
`d = N/4` it returns `N²/32 + c·(3N/4)² > cN²` for every `c < 1/18`), produces such a term.
