# Erdős #23 — Round 8, mechanism: **STABILITY**

Everything below is stated for the weighted (pattern) form and is verified in **exact rational
arithmetic** (`fractions.Fraction`) or **exact integer arithmetic** (the C++ census). Floating point
appears only inside search loops; nothing floating decides a claim.

## 0. Notation

`H` is a finite simple **triangle-free** graph on `V`, `Δ(V) = {x ≥ 0 : Σ x_v = 1}`.
For `S ⊆ V` write `mono_H(S;x) = Σ_{uv ∈ E(H), |{u,v} ∩ S| ≠ 1} x_u x_v` and

```
psi(H,x) = min_{S ⊆ V} mono_H(S;x),        Psi(H) = max_{x ∈ Δ(V)} psi(H,x).
```

The conjecture is `Psi(H) ≤ 1/25` for every triangle-free `H`. For an induced 5-cycle
`C = (c_1,…,c_5)` of `H`, `u_C ∈ Δ(V)` is the **C5-concentration**: `1/5` on each `c_i`, `0` elsewhere;
`psi(H,u_C) = 1/25`.

Because `H` is triangle-free and `C` is induced, `N(v) ∩ C` is an independent set of `C_5` for every
`v ∉ C`, so `|N(v) ∩ C| ≤ 2`, and a 2-element `N(v) ∩ C` is one of the five distance-2 pairs
`{c_{i-1}, c_{i+1}}`. Call such a `v` a **full twin of class `i`**, write `T_i` for that set,
`T = ⋃ T_i`, `R = V ∖ (C ∪ T)`. Thus `v ∈ R ⟺ |N(v) ∩ C| ≤ 1`. **Triangle-freeness is used here and
is used again in every result below; without it every statement fails.**

---

## 1. Theorem B — the extremal set is an exact PLATEAU

**Theorem B.** Let `V = V_1 ⊔ … ⊔ V_5` and let `B = C5[V_1,…,V_5]` be the *complete* blow-up
(all edges between consecutive classes, none else). For `x ∈ Δ(V)` with class sums `y_i = x(V_i)`,

```
psi(B, x) = min_{i ∈ Z_5} y_i y_{i+1},
```

and for every spanning subgraph `H ⊆ B`, `psi(H,x) ≤ min_i y_i y_{i+1} ≤ 1/25`.
Consequently `Psi(B) = 1/25` and the **maximiser set is exactly** `{x ∈ Δ(V) : y_i = 1/5 for all i}`,
a product of five simplices of dimension `|V_i| − 1`.

*Proof.* (≤) Pick `a` minimising `y_a y_{a+1}` and 2-colour the classes `a, a+1, a+3` / `a+2, a+4`.
Exactly one consecutive class pair, namely `(a, a+1)`, is monochromatic, so the corresponding cut
has `mono = ` (weight of `V_a`–`V_{a+1}` edges) `≤ y_a y_{a+1}`, with equality for the complete `B`.

(≥) Fix any `S`. Put `t_i = x(V_i ∩ S)/y_i ∈ [0,1]` (irrelevant if `y_i = 0`). Then

```
mono_B(S;x) = Σ_i y_i y_{i+1} f(t_i,t_{i+1}),   f(s,t) = st + (1−s)(1−t) ≥ 0.
```

With `m = min_j y_j y_{j+1}`, `mono ≥ m · g(t)` where `g(t) = Σ_i f(t_i,t_{i+1})`. `g` is **multilinear**
in each `t_i`, so `min_{[0,1]^5} g` is attained at a vertex `t ∈ {0,1}^5`, where `g(t)` is the number of
monochromatic edges of `C_5` under the 2-colouring `t`, hence `≥ 1` (odd cycle). So `mono ≥ m`.

(AM–GM) `m^5 ≤ Π_i (y_i y_{i+1}) = (Π_i y_i)^2 ≤ ((Σ y_i)/5)^{10} = 5^{-10}`, so `m ≤ 1/25` with
equality iff all `y_i = 1/5`. ∎

Verified exactly: `R8_stability_local.py` (L2, L2b), `R8_stability_verify.py` (V4) — including
**unbalanced** blow-ups `C5[3,1,2,2,1]`, `C5[3,3,3,3,2]` and blow-ups **with a zero part**
`C5[2,0,2,2,2]`.

**Lemma R (rigidity).** Every complete blow-up `C5[V_1,…,V_5]` with all `V_i ≠ ∅` is a **maximal**
triangle-free graph. *(A non-edge inside `V_i`, or between `V_i` and `V_{i+2}`, has both endpoints
adjacent to all of `V_{i+1} ≠ ∅`; adding it creates a triangle.)* Verified: `L6`.
Consequence: inside the triangle-free world one cannot perturb a complete blow-up by *adding* edges;
the only perturbations are deleting blow-up edges or adding new vertices.

---

## 2. Theorem C — the exact local structure at a C5-concentration

Let `d` be a feasible direction at `u = u_C` (`Σ_v d_v = 0`, `d_v ≥ 0` for `v ∉ C`). Set

```
W_i = Σ_{v ∈ T_i} d_v,     a_i = d_{c_i} + W_i,     W' = Σ_{v ∈ R} d_v ≥ 0.
```

**(i) Active cuts.** `mono(S;u) = (#monochromatic C-edges)/25`, and every cut makes an odd number
`≥ 1` of `C`-edges monochromatic. So the active set at `u` is exactly `{S :` exactly one `C`-edge
monochromatic`}`: `5·2^{n−5}` bipartitions. *Verified exactly:* Petersen 160, Grötzsch 320,
Wagner `Γ_8` 40, `Γ_11` 320, `Γ_14` 2560, `C5` 5, `C5[2]` 160, `C5[3,1,2,2,1]` 80 — all `= 5·2^{n−5}`.

**(ii) Directional derivative (exact formula).**

```
D_d psi(H,u) = (1/5) · min_{i ∈ Z_5} ( a_i + a_{i+1} ),        Σ_i a_i = −W'.
```

*Proof.* By Danskin, `D_d psi = min` over active `S` of `⟨∇ mono(S;u), d⟩`. For an active `S` whose
monochromatic `C`-edge is `c_i c_{i+1}`, only edges meeting `C` contribute, giving
`(1/5)[ d_{c_i} + d_{c_{i+1}} + Σ_{v ∉ C} m_v(S) d_v ]` with `m_v(S) = |N(v) ∩ C ∩ (\text{side of } v)|`.
The sides of `V∖C` are free, and `d_v ≥ 0`, so each `v` is minimised independently: `m_v = 0` unless
`N(v) ∩ C` is a distance-2 pair *split* by the colouring, in which case `m_v = 1`. The colouring
attached to the monochromatic edge `c_i c_{i+1}` splits exactly the two pairs
`{c_{i−1},c_{i+1}} = p_i` and `{c_i,c_{i+2}} = p_{i+1}`. Hence the derivative for that `S` equals
`(1/5)(d_{c_i} + W_i + d_{c_{i+1}} + W_{i+1}) = (1/5)(a_i + a_{i+1})`. Summing over `i`,
`Σ_i(a_i+a_{i+1}) = 2 Σ_i a_i = 2(Σ_{C} d + Σ_{T} d) = 2(−W')`. ∎

*Verified exactly against brute-force Danskin on Petersen, Grötzsch, Wagner, `Γ_11`, `C5[2]`,
`C5[3,1,2,2,1]`, `C5`:* `R8_stability_local.py` (L3).

**(iii) The flat cone is exactly the TWIN-SPLITTING cone.**
Since `Σ_i (a_i+a_{i+1}) = −2W' ≤ 0`, we get `D_d psi(u) ≤ 0` (this re-proves first-order local
maximality), and `D_d psi(u) = 0` forces `W' = 0` and `a_i + a_{i+1} = 0` for all `i`; on an **odd**
cycle that forces `a ≡ 0`. Hence

```
FlatCone = { d : d_v = 0 for all v ∈ R,   and   d_{c_i} = −Σ_{v ∈ T_i} d_v for all i }.
```

In words: *the only first-order-free motion is transferring weight from `c_i` to full twins of class
`i`* — i.e. exactly the motions that preserve the five class sums `= 1/5`. In particular the
C5-concentration is a **strict** first-order local maximum **iff `T = ∅`** (e.g. Petersen).
Verified: L4, and by the exact argmax counts in §4.

**(iv) Quantitative first order (sharp constant `1/60`).** With `b = a − (Σ_i a_i /5)·𝟙`,

```
D_d psi(H,u)  ≤  −(2/25)·W'  −  (1/60)·‖b‖_1   ≤   −(1/60)·dist_1(d, FlatCone),
```

where `dist_1(d,FlatCone) ≤ 2W' + ‖b‖_1` via the canonical projection
`d̃_v = d_v (v ∈ T)`, `d̃_v = 0 (v ∈ R)`, `d̃_{c_i} = −W_i`. The constant `1/60` comes from Lemma K
below and is sharp. *Verified exactly:* L5, V5.

**(v) Second order on the flat cone — exact strictness criterion.**
If `d ∈ FlatCone` then `supp(u+td) = C ∪ {v ∈ T : d_v > 0}` and `H` restricted to it is a **subgraph
of the complete blow-up** with classes `{c_i} ∪ (T_i ∩ supp)`. *(Triangle-freeness: two full twins of
classes `i,j` can be adjacent only if `|i−j| = 1`; if `i = j` or `|i−j| = 2` they share a `C`-neighbour.)*
Therefore, by Theorem B, the class sums stay `1/5` and

```
psi(H, u+td)  ≤  1/25  −  t^2 · max_{i ∈ Z_5} Miss_i(d),
Miss_i(d) = Σ  d_v d_w   over  v ∈ T_i, w ∈ T_{i+1}  with  vw ∉ E(H).
```

So `psi ≡ 1/25` along `d` **iff the twin structure carried by `supp(d)` is complete**; otherwise the
drop is exactly second order. *Verified with equality:* on `H = C5 + (twin v of class 1) + (twin w of
class 2)` with `vw` **deleted** (graph6 `FhdL?`, triangle-free), for all rational `t,s`,

```
psi(H, x) = 1/25 − t·s      exactly,     x = (1/5−t, 1/5−s, 1/5, 1/5, 1/5, t, s),
```

while with `vw` present (graph6 `FhdLG` `= C5[2,2,1,1,1]`) `psi ≡ 1/25`. (`S1a`, `S1b`.)
The exact maximiser sets on the `q = 20` grid confirm this: `FhdLG` has `5^2 = 25` maximisers (the
full plateau), `FhdL?` has exactly `9 = |{(t,s) ∈ {0..4}^2 : ts = 0}|`.

---

## 3. Proposition 1 — sharp quantitative stability for the pattern `C_5`

Write `u = (1/5,…,1/5)`, `d = x − u`, `D = ‖x − u‖_1`, `s_i = d_i + d_{i+1}`, `δ = max_i(−s_i)`.

**Lemma K.** `{s : Σ s_i = 0, s_i ≥ −δ}` is a 4-simplex whose 5 vertices are the rotations of
`δ·(−1,−1,−1,−1,4)`. Since `s = (I+P)d` and `(I+P)^{−1} = (I − P + P^2 − P^3 + P^4)/2` on `Z_5`, those
vertices correspond to `d = δ·` (rotations of) `(2,−3,2,−3,2)`, and `‖d‖_1` is convex in `s`, so

```
‖d‖_1 ≤ 12·δ,      sharp, with equality exactly on those five rays.
```

**Proposition 1.** For every `x ∈ Δ_5`,

```
psi(C5,x)  ≤  1/25 − D/60 + D^2/576   ≤   1/25 − D/72.
```

*Proof.* `psi(C5,x) = min_i x_i x_{i+1}` (any cut of `C_5` has an odd number `≥1` of monochromatic
edges, and a sum of `≥1` of the five products is `≥` their minimum; verified L1). Let `(a,b)=(i,i+1)`
attain `−s_i = δ`. Then `1/25 − psi ≥ 1/25 − x_a x_b = δ/5 − d_a d_b ≥ δ/5 − δ^2/4`, using
`d_a d_b ≤ ((d_a+d_b)/2)^2`. The map `φ(δ) = δ/5 − δ^2/4` increases on `[0,2/5]`, and `δ ≤ 2/5`
(as `d_i ≥ −1/5`); by Lemma K, `δ ≥ D/12 ≤ 8/60 < 2/5`, so `1/25 − psi ≥ φ(D/12) = D/60 − D^2/576`.
Finally `D ≤ 8/5` gives `D^2/576 ≤ D/360`, and `D/60 − D/360 = D/72`. ∎

**Sharpness.** Along `x = u + t(2,−3,2,−3,2)` (`0 ≤ t ≤ 1/15`) one has *exactly*

```
psi = 1/25 − t/5 − 6t^2,      D = 12t,      (1/25 − psi)/D = 1/60 + t/2,
```

so `inf_{x ≠ u} (1/25 − psi)/D = 1/60`, **not attained**. Exact rational grid search confirms this:
the minimum of the ratio over all `x` with denominator `q` is `1/40` (at the corner `x = e_1`) for
`q ≤ 60`, and `1/60 + 1/(2q)` for `q ≥ 75` — `7/300` at `q = 75`, `13/600` at `q = 100`, attained at
`(17,22,17,22,22)/100`, a rotation of the extremal ray. (`R8_stability_c5sharp.py`, `V1`, `V2`.)

The same picture holds for `C_7`: `psi(C7,x) = min_i x_i x_{i+1}`, `Psi(C7) = 1/49` at the uniform
point (verified V3, and by exact grid at `q=21`: `bestM = 9`, unique argmax `(3,3,3,3,3,3,3)`).

---

## 4. Theorem D — an unconditional LOCAL EXACTNESS BALL (the main new positive result)

**Theorem D.** Let `H` be triangle-free with an induced 5-cycle `C`, let `T, R` be as in §0, and let
`x ∈ Δ(V)`. Put `ρ = x(R)`, `η = x(V∖C)` (so `ρ ≤ η`). Then

```
psi(H,x)  ≤  (1−ρ)^2 / 25  +  ρ·η.
```

Consequently `psi(H,x) ≤ 1/25` whenever `25η ≤ 2 − ρ`; in particular

* **(a)** whenever `ρ = 0` (all off-`C` weight sits on full twins) — with **no constraint at all** on `η`;
* **(b)** whenever `η ≤ 1/13`; and since `η ≤ ‖x − u_C‖_1`, whenever `‖x − u_C‖_1 ≤ 1/13`.

*Proof.* Set classes `P_i = {c_i} ∪ T_i`, `y_i = x(P_i)`, so `Σ y_i = 1 − ρ`. **Every edge of
`H[C ∪ T]` joins consecutive classes**: `c_i c_{i+1}` does; `c_i` is adjacent to `v ∈ T_j` iff
`c_i ∈ {c_{j−1},c_{j+1}}`, i.e. `|i−j| = 1`; and two full twins of classes `i,j` with `i = j` or
`|i−j| = 2` share a `C`-neighbour, so triangle-freeness forbids them to be adjacent.

Choose `a` minimising `y_a y_{a+1}` and colour `P_a, P_{a+1}, P_{a+3}` side `A`, `P_{a+2}, P_{a+4}`
side `B`. Place each `v ∈ R` on the side **not** containing its unique `C`-neighbour (arbitrarily if it
has none) — possible because `|N(v) ∩ C| ≤ 1`. The monochromatic edges of this bipartition are:

* inside `C ∪ T`: exactly the `P_a`–`P_{a+1}` edges, of weight `≤ y_a y_{a+1}`;
* between `R` and `C`: **none**, by the placement rule;
* everything else has one endpoint in `R` and the other in `T ∪ R`: total weight
  `≤ Σ_{v ∈ R} x_v · x((T ∪ R)∖{v}) ≤ ρ(τ + ρ) = ρη`, `τ = x(T)`.

Hence `psi ≤ min_i y_i y_{i+1} + ρη ≤ ((Σ y_i)/5)^2 + ρη = (1−ρ)^2/25 + ρη`, the middle step by the
same AM–GM as in Theorem B. Finally `(1−ρ)^2/25 + ρη ≤ 1/25 ⟺ ρη ≤ (2ρ − ρ^2)/25 ⟺ 25η ≤ 2 − ρ`
(for `ρ > 0`; for `ρ = 0` the bound reads `psi ≤ (1)^2/25` directly). If `η ≤ 1/13` then
`25η ≤ 25/13 = 2 − 1/13 ≤ 2 − ρ`. ∎

Verified exactly on **16 320** instances spanning `C5`, `C5[2]`, `C5[3,1,2,2,1]`, `C5[3,3,3,3,2]`,
Petersen, Grötzsch, Wagner, `Γ_11`, `C_7`, `K_{3,3}` and both 7-vertex twin graphs, over **every**
induced `C_5` of each (`V6`; also `S2a`, `S2b`).

**What Theorem D is.** It is a *local exactness* statement: the conjecture is proved outright, for
every triangle-free `H` and every `n`, on an explicit `ℓ_1`-ball of radius `1/13` around **every**
C5-concentration, and on the *whole* twin-plateau through it. It contains no threshold `N ≥ N_0`,
so it is not vulnerable to the `a(tN) ≥ t^2 a(N)` objection (registry A11). It is strictly weaker than
the conjecture: it says nothing about `x` far from a C5-concentration.

**Radius.** `1/13 = 2/(25+1)` is an artifact of the crude `ρη` bound on `R`-incident edges; no
witness is known that limits it (if the conjecture holds the true radius is `∞`). §6 explains exactly
why the obvious improvement fails.

---

## 5. Exact census — global maxima, maximiser sets, and stability profiles

Exact integer engine `R8_stability_census.cpp`: for `a ∈ Z_{≥0}^n` with `Σ a = q`,
`M(a) = min_S Σ_{mono} a_u a_v` is an integer and `psi(H,a/q) = M(a)/q^2`; the conjecture reads
`25·M(a) ≤ q^2`. **All compositions are enumerated, zeros included.**

### 5.1 All connected triangle-free graphs (nauty `geng -tc`)

| `n` | #graphs | `q` | violations of `25M ≤ q²` | # with induced `C_5` | # attaining `psi = 1/25` | sets equal? |
|---|---|---|---|---|---|---|
| 5 | 6 | 20 | 0 | 1 | 1 | **yes** |
| 6 | 19 | 20 | 0 | 2 | 2 | **yes** |
| 7 | 59 | 20 | 0 | 14 | 14 | **yes** |
| 8 | 267 | 20 | 0 | 83 | 83 | **yes** |
| 9 | 1380 | 10 | 0 | 632 | 632 | **yes** |

Moreover **every** argmax vector inspected is a *balanced C5-blow-up weighting*: its support admits a
partition into 5 classes of weight `q/5` each, with every edge of the induced subgraph joining
consecutive classes. (Checker: `is_balanced_blowup_weighting` in `R8_stability_analyze.py`.)

**Gap for `C_5`-free graphs.** In a triangle-free graph every 5-cycle is induced, so "no induced
`C_5`" = "odd girth `≥ 7`". Among connected triangle-free graphs on `n ≤ 8` the best such graph is
`C_7` with `Psi = 1/49` exactly — i.e. `25/49 ≈ 0.5102` of the extremal value. This is a large,
explicit, *unconditional-at-this-size* stability gap: the "far" case (no `C_5` at all) is nowhere near
`1/25`. (`R8_c5free7.g6`, `R8_c5free8.g6` at `q = 35`: `bestM = 25`, `q² = 1225`, `25M = 625`.)

### 5.2 Named graphs (exact)

| graph | `n` | `q` | `Psi` | `#argmax` on the grid | structure of the maximiser set |
|---|---|---|---|---|---|
| `C_5` | 5 | 25, 35 | `1/25` | 1 | the unique C5-concentration |
| `C_7` | 7 | 21 | `1/49` | 1 | uniform |
| Wagner `Γ_8 = And(3)` | 8 | 25 | `1/25` | 40 | C5-concentrations + their twin splittings |
| **Petersen** | 10 | 20 and 15 | `1/25` | **12** | **exactly the 12 C5-concentrations** (`T = ∅`) |
| `C5[2]` | 10 | 20 | `1/25` | **3125 = 5^5** | the *entire* plateau `{class sums = q/5}` |
| Grötzsch | 11 | 15 | `1/25` | 191 | blow-up weightings |
| `Γ_11 = And(4)` | 11 | 15 | `1/25` | 264 | blow-up weightings |
| `C5[2,2,1,1,1]` (`FhdLG`) | 7 | 20 | `1/25` | `25 = 5^2` | the plateau |
| same minus one twin–twin edge (`FhdL?`) | 7 | 20 | `1/25` | `9` | exactly `{ts = 0}`, the two complete sub-blow-up faces |

The Petersen row reproduces exactly the known data point (maximiser set = the 12 C5-concentrations)
and is *explained* by Theorem C(iii): Petersen has no full twins of any induced `C_5`, so the flat
cone is trivial and the maxima are isolated.

### 5.3 Exact stability profiles

`env[d] = max{ q^2·psi(H,x) : x` on the grid at unit-transfer distance `d` from the argmax set `}`;
note `‖x − x*‖_1 = 2d/q`. These are the exact "either close, or bounded below" curves.

```
C5,                q=35:  49 42 42 40 40 36 36 30 27 22 20 16 16 12 12 9 9 6 6 4 4 2 2 1 1 0 …
Wagner Γ8,         q=25:  25 24 21 21 20 20 18 18 16 13 12 8 6 4 4 2 1 1 0 0 0
Petersen,          q=15:   9  6  6  6  6  7  6  5  3  1  0 0 0        (NOT monotone in d)
C5[2,2,1,1,1],     q=20:  16 12 12 10 10 6 6 4 4 2 2 1 1 0 0 0 0
… minus one edge,  q=20:  16 15 12 12 12 10 10 6 6 4 4 2 2 1 0 0 0
C7,                q=21:   9  6  6  6  5  4 4 2 2 2 1 1 1 0 …
```

Two facts worth recording. (1) `env[6] = 36` for `C_5` at `q = 35` is attained at `(9,4,9,4,9)`, i.e.
`u + (1/35)(2,−3,2,−3,2)` — the extremal direction of Lemma K, and the ratio there is exactly
`13/420 = 1/60 + 1/70`, matching Proposition 1's sharpness statement to the last digit.
(2) Petersen's profile is **not monotone** (`env[5] = 7 > env[4] = 6`): the distance-to-extremal-set
functional is not a potential, so no monotone descent argument can be built on it.

### 5.4 Local maxima: values, supports, and a strong negative

Grid-local maxima (no single unit transfer improves) with `M > 0`, for `C_5` at `q = 25`:
`25:1, 20:30, 18:15, 16:5, 15:15, 14:5, 12:50, 10:15, 9:10, 8:35, …` and for Wagner at `q = 25`:
`25:40, 21:24, 20:2064, 19:72, 18:1424, …`. **These are grid artifacts.** Applying the exact
continuous test (`R8_stability_localmax.py`: solve `max t` s.t. `⟨∇q_S(x),d⟩ ≥ t` over active `S`,
`Σd = 0`, `d_v ≥ 0` where `x_v = 0`; if `t* > 0`, exhibit `d` and verify `psi(x+εd) > psi(x)` in exact
rationals) gives:

| point | `psi` | `#active` | verdict |
|---|---|---|---|
| `C5 (5,5,5,5,5)/25` | `1/25` | 5 | first-order local max |
| `C5 (4,5,4,5,7)/25` | `4/125` | 3 | **not** a local max — witness `psi(x+d/50) = 171/5000` |
| `C5 (4,5,4,6,6)/25` | `4/125` | 2 | **not** — `187/5000` |
| `C5 (3,6,3,6,7)/25` | `18/625` | 3 | **not** — `161/5000` |
| `C5 (4,4,4,4,9)/25` | `16/625` | 3 | **not** — `27/1000` |
| Wagner `(0,5,0,5,5,0,5,5)/25` | `1/25` | 40 | first-order local max |
| Wagner `(1,4,4,1,4,5,1,5)/25` | `21/625` | 4 | **not** — `2663/75000` |
| Wagner `(0,4,0,4,5,0,5,7)/25` | `4/125` | 24 | **not** — `171/5000` |
| Petersen C5-concentration | `1/25` | 160 | first-order local max |
| Petersen `(1,0,0,0,0,3,4,4,4,4)/20` | `3/100` | 32 | **not** — `81/2500` |
| `C5[2]` two plateau points | `1/25` | 160, 44 | first-order local max |
| `FhdL?` `(4,4,4,4,4,0,0)/20`, `(4,0,4,4,4,0,4)/20` | `1/25` | 20, 20 | first-order local max |
| `FhdL?` `(3,3,4,4,4,1,1)/20` | `3/80` | 3 | **not** — `1521/40000` |

**Observed law (tested, not proved): on every graph examined, every continuous first-order local
maximum of `psi` is a GLOBAL maximum.** Equivalently `psi` appears to have no spurious local maxima —
which, if it could be proved, would be a genuine stability mechanism (it converts local certificates
into global ones). No counterexample was found.

---

## 6. Three explicit KILLS

### K-1. Quantitative monotonicity in the naive metric is FALSE at `ε = 0`.

The proposed shape was: *"if `psi(H,x) ≥ 1/25 − ε` then `dist(x, {C5-concentrations}) ≤ f(ε)`."*

**Witness (exact).** `H = C5[2]` (10 vertices), `x` uniform (`1/10` each): `psi = 1/25` **exactly**
(`S3`), while the `ℓ_1` distance from `x` to the nearest C5-concentration of `H` is exactly `1`.
On `C5[N/5]` the same distance is `2 − 10/N → 2`, which is the **diameter** of `Δ` in `ℓ_1`.
So `f(0)` would have to equal the diameter: the statement is vacuous for every `ε ≥ 0`.

The metric must be *distance to the blow-up manifold* (equivalently, `ℓ_1` distance modulo the
twin-splitting cone of Theorem C(iii)). Theorem C makes that precise: the flat directions at a
C5-concentration are exactly the twin splittings, so no metric that separates twins can appear in a
true stability statement.

### K-2. The unweighted (removal / edit-distance) form is FALSE at `N = 14`.

*"`bip(G)` close to `N²/25` ⟹ `G` close in edit distance to a `C_5` blow-up"* needs, at minimum, the
maximisers of `bip` to be blow-ups. Recomputed here from scratch (`R8_stability_editdist.py/.cpp`):

* `G = ` graph6 `M?AE@bH{AYN_LgBs?`, `N = 14`, `|E| = 32`, triangle-free, 92 induced `C_5`s;
* `bip(G) = 7` (exhaustive over all `2^13` bipartitions); `25·7 = 175 ≤ 196 = N²`, so the conjecture
  holds — but `N²/25 = 7.84`, so `G` attains `⌊N²/25⌋`;
* **the best `C_5` blow-up on 14 vertices has `bip = min_i n_i n_{i+1} = 6`** (exhaustive over all
  compositions of 14 into 5 parts; e.g. `(3,3,2,4,2)`), and `bip(C5[3,3,3,3,2]) = 6` confirms;
* the **exact** minimum edit distance from `G` to the `C_5`-blow-up family on the same vertex set is
  **15 edges** (branch-and-bound over all `5^13` class maps), i.e. `15/32 ≈ 47%` of `E(G)`.

So at `N = 14` the unique `bip`-maximiser strictly **beats** every blow-up (`7 > 6`) and is far from
all of them. Any removal/stability lemma phrased at the graph level, at finite `N`, is refuted.
(This independently reproduces the registry's A5 witness, from a different direction.)

### K-3. The natural induction that would remove the `ρη` term dies on an exact `2ρ/25 = 2ρ/25` collision.

In Theorem D the only lossy term is `ρη`. The natural fix is to recurse: `H[R]` is triangle-free and
smaller, so *by induction* `mono_{R–R} ≤ ρ²/25`, and `(1−ρ)²/25 + ρ²/25 ≤ 1/25 ⟺ ρ ≤ 1` — always
true. The recursion is blocked because it demands the `R`-optimal bipartition of `H[R]`, which
conflicts with "place `v ∈ R` opposite its `C`-neighbour". Charging the conflict exactly:

* gain from imbalance: `1/25 − (1−ρ)²/25 = (2ρ − ρ²)/25`;
* `R`–`C` cost, averaged over the 5 choices of monochromatic class-pair `a`: for the colouring
  attached to `a`, the side `A = {a, a+1, a+3}` contains `c_j` for exactly **3** of the 5 values of
  `a`, so the mean `R`–`C` monochromatic weight is `≥ (2/5)·Σ_{v∈R} x_v x_{c_{j(v)}}`, which for a
  near-extremal `x` (`x_{c_j} ≈ 1/5`) is `≈ 2ρ/25`.

`2ρ/25` (cost) `= 2ρ/25` (gain), identically, to first order in `ρ`. The two cancel and the argument
yields nothing. The obstruction is precisely that `min_a y_a y_{a+1}` and `avg_a (R\text{-cost})`
cannot be evaluated at the same `a` — the same wall as registry entry **A6** (fixed averaging
certificates, DEAD, value `1/20` on every `C5[n]`), now localised to a single arithmetic identity.

---

## 7. Accounting: what stability can and cannot legally deliver here

Define, for a metric `dist(·, BlowUp(H))` on `Δ(V)`:

* `STAB(ε,δ)`: for every triangle-free `H` and every `x`, `psi(H,x) ≥ 1/25 − ε ⟹ dist(x,BlowUp(H)) ≤ δ`;
* `LOC(δ)`: for every triangle-free `H` and every `x` with `dist(x,BlowUp(H)) ≤ δ`, `psi(H,x) ≤ 1/25`.

Then `STAB(ε,δ) ∧ LOC(δ) ⟹` the conjecture, for any `ε > 0`. Neither conjunct alone has strength
`≥` the conjecture (`STAB` bounds nothing near the manifold; `LOC` bounds nothing away from it), so
this **is** a legal two-step decomposition under the anti-reformulation rule.

The statement that is **illegal** and must never be adopted as a target lemma, quoted verbatim:

> "for every triangle-free `H` and every `x`, either `psi(H,x) ≤ 1/25 − ε` or `x` lies within `δ` of a
> `C_5` blow-up and `psi(H,x) ≤ 1/25`"

— that is the conjecture written out, and it is the shape the assignment's slogan
("either `G` is close to a `C5` blow-up, or `bip(G)` is bounded strictly below `N²/25`") collapses to
if the two halves are not kept separate.

**Status of the two halves after this round.**

* `LOC`: **partially proved, unconditionally** — Theorem D, around every C5-concentration, radius
  `1/13` in off-`C` mass, and radius `∞` along the twin plateau. Not yet available around a general
  blow-up point with large classes: the proof of Theorem D uses `|N(v) ∩ C| ≤ 1` for `v ∈ R`, which
  has no analogue when the classes are large (an `R`-vertex can then meet a whole class, and choosing
  its side costs `Θ(ρ/5)`, far above the `2ρ/25` budget). This is the concrete open step.
* `STAB`: **completely open**, and the round produced no partial result on it. The only new inputs
  are negative: K-1 fixes the metric that a true `STAB` must use, K-2 shows `STAB` cannot be phrased
  at the graph/edit-distance level at finite `N`, and §5.3 shows the natural potential function
  (distance to the extremal set) is not monotone even on Petersen.

**Also note:** neither Theorem B, C, D nor Proposition 1 gives *any* upper bound on `psi` for a
weighting far from every C5-concentration, so nothing here improves the published `n²/23.5`.
No statement in this document should be read as progress on the global bound.

---

## 8. Files (all in `problems/23/round8/`)

| file | contents |
|---|---|
| `R8_stability_core.py` | graphs, exact `psi`, graph6 I/O, named test graphs, SLP multistart optimiser |
| `R8_stability_local.py` | L1–L6: `psi(C5)`, Theorem B + plateau, derivative formula, flat cone, Lemma R |
| `R8_stability_secondorder.py` | S1: second-order strictness `psi = 1/25 − ts`; S2: Theorem D; S3: kill K-1 |
| `R8_stability_c5sharp.py` | Lemma K, the sharp `1/60`, exact ratio grids `q ≤ 100` |
| `R8_stability_verify.py` | exact regression gate V1–V6 (all PASS) |
| `R8_stability_census.cpp/.exe` | exact integer census: `M(a)`, argmax sets, grid-local maxima, stability profiles |
| `R8_stability_analyze.py` | census post-processing, blow-up-weighting checker |
| `R8_stability_localmax.py` | exact continuous local-maximum certificates / refutations |
| `R8_stability_editdist.py/.cpp/.exe` | the `N = 14` kill K-2 (bip, blow-up optimum, exact edit distance) |
| `R8_stability_multistart.py` | multistart ascent under OPTIMISER DISCIPLINE |
| `R8_tf{5..9}.g6`, `R8_census_n*_q*.txt`, `R8_*_q*.txt`, `R8_verify.log`, `R8_c5sharp.log` | data |

Reproduce: `python R8_stability_verify.py` (exact gate, prints `ALL PASS`);
`clang++ -O2 -std=c++17 -o R8_stability_census.exe R8_stability_census.cpp`;
`./R8_stability_census.exe R8_tf8.g6 20 3 0`.
