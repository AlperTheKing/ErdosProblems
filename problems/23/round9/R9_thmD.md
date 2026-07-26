# Round 9 — Adversarial audit of Theorem D, and its extension

**Scope.** Task 1: try to break Theorem D. Task 2: attack the blocking step and improve the
radius. Everything below is exact (integer / `fractions.Fraction`); floating point was used only
to steer search. Code: `R9_thmD_*.py` in this directory.

---

## 0. Verdicts, up front

| | verdict |
|---|---|
| **Theorem D** | **TRUE.** Independently re-proved here; every step verified exactly; no counterexample in 5 157 802 exact instances in the main battery, plus the proof steps L1–L4 re-verified on a separate battery, plus 163 320 refined-cut checks and 22 920 Theorem-F checks. |
| **Radius `η ≤ 1/13`** | **IMPROVED to `η ≤ 4/25 = 0.16`** (factor 2.08), proved (Theorem F below), sharp radius of the argument `0.1631179…`. |
| **Sharper form** | `50·e_RT + 125·e_RR ≤ 1−(1−ρ)^10` suffices, where `e_RT`, `e_RR` are the *edge* weights from `R` into `T` and inside `R`. In particular `e_RT = e_RR = 0 ⟹ psi ≤ 1/25` with **no constraint on `η`** — strictly contains Theorem D(a). |
| **Blow-up generalisation** | Master inequality proved (Theorem E), valid for **any** 5-partition of **any** graph. Its only *unconditional* corollary is `H → C5`. A ball of positive radius around a *balanced* blow-up point **cannot** be opened by this method, for a reason I can state exactly (§6). |
| **My own first attempt at E** | **RETRACTED** — see §5.2. The criterion "`BAD_i = 0` for *some* `i`" is false; witness `y = (1/6,1/4,1/6,1/4,1/6)`. |

---

## 1. Theorem D, and the proof I checked

> **Theorem D.** `H` triangle-free, `C = (c_0…c_4)` an induced `C5`,
> `T_i = {v ∉ C : N(v) ∩ C = {c_{i−1}, c_{i+1}}}`, `R = V ∖ (C ∪ ⋃T_i)`,
> `ρ = x(R)`, `η = x(V∖C)`. Then `psi(H,x) ≤ (1−ρ)²/25 + ρη`,
> hence `psi ≤ 1/25` whenever `25η ≤ 2−ρ`, in particular whenever `η ≤ 1/13`.

I re-derived it from scratch before reading the author's write-up (`round8/R8_stability.md §4`); the
two proofs agree line for line. Triangle-freeness enters in **exactly three** places:

* **(L1)** `N(v) ∩ C` is independent in `C_5`, so `|N(v) ∩ C| ≤ 2`, and `= 2` forces the twin pair
  `{c_{i−1},c_{i+1}}`. Hence **`|N(v) ∩ C| ≤ 1` for every `v ∈ R`** — this is what lets each
  `R`-vertex be placed opposite its unique `C`-neighbour, making the `R–C` cost exactly `0`.
* **(L2)** two full twins of classes `i, j` with `i = j` or `|i−j| = 2` share a `C`-neighbour, so
  they are non-adjacent: every edge of `H[C ∪ T]` joins **consecutive** classes `P_i = {c_i} ∪ T_i`.
* **(L3)** (not used by the author, used by me in §4) `R_j := {v : N(v) ∩ C = {c_j}}` is
  **independent**, and `N(R_j) ∩ T ⊆ T_j ∪ T_{j+2} ∪ T_{j+3}` — a vertex adjacent to `c_j` cannot
  touch `T_{j±1}`, whose members are also adjacent to `c_j`.

Then `min_i y_i y_{i+1} ≤ ((Σy_i)/5)² = (1−ρ)²/25` (AM–GM, valid with zeros), and everything
`R`-incident is bounded by `Σ_{v∈R} x_v·x((T∪R)∖{v}) ≤ ρ(τ+ρ) = ρη`.

**Integer form used for all testing** (`x = a/q`, all quantities integers):
`25·M(a) ≤ (q−r)² + 25·r·e`, where `M(a) = min_S Σ_mono a_u a_v`, `r = Σ_{v∈R} a_v`,
`e = q − Σ_{c∈C} a_c`.

---

## 2. Task 1 — the audit. No counterexample.

### 2.1 What was run (`R9_thmD_audit.py`, `R9_thmD_adversarial.py`, `R9_thmD_refined.py`)

| battery | scale | violations |
|---|---|---|
| Exhaustive over **all** compositions (zeros included), every induced `C5`: `C5` (q=20,21,13), `C5[2,2,1,1,1]`(12), `C5[3,1,2,2,1]`(10), `C5+K1`(12), Petersen(10), `C5[2]`(10), Wagner(12) | 5 157 802 exact instances, 20 graphs, 503 pentagons | **0** |
| Random sweeps: Grötzsch, `Γ_11`, `Γ_14`, MTF14, `C5[3,3,3,3,2]`, `C5+C5`, `C5+C7`, `Petersen+K1` | 1450 weight vectors × all pentagons | **0** |
| Exact hill-climb **maximising the violation** `25M − (q−r)² − 25re`, started from **every** `C5`-concentration (requirement 5) plus random starts, 8 graphs | max attained `= 0` on every graph, at the `C5`-concentrations | **0** |
| Proof steps **L1–L4** re-verified structurally per (graph, pentagon), incl. `psi ≤` (weight of the proof's own bipartition) `≤` bound | named graphs, 8 purpose-built adversaries, 196 random triangle-free graphs (n = 7…12), 48 750 instances | **0** |

`L4` is the sharp test: it rebuilds the *actual* bipartition the proof constructs and checks both
`psi ≤ its weight` and `its weight ≤ (1−ρ)²/25 + ρη`. Any error in the proof would surface there.

### 2.2 The specific checklist

* **Triangle-freeness genuinely used** — yes, and it is *load-bearing*: dropping it breaks the
  inequality immediately. Smallest witness (`R9_thmD_necessity.py`):
  **graph6 `Ehf?`** = `C5` (0–1–2–3–4–0) **plus a vertex 5 adjacent to `c_0` and `c_1`** (one triangle),
  **`x = (2/5, 2/5, 0, 0, 0, 1/5)`**: here `5 ∈ R` (its `C`-neighbourhood `{c_0,c_1}` is not a twin
  pair), `ρ = η = 1/5`, and
  `psi = 2/25 = 0.08 > 41/625 = 0.0656 = (1−ρ)²/25 + ρη`.
  Similar witnesses: `Ehf_`, `Ehfw`, `FhfE?`.
* **`N` odd, `N` not divisible by 5** — the statement is purely weighted; `N` never appears. Tested
  at `n = 5,6,7,8,9,10,11,12,13,14,17,20` and `q = 10,…,25` incl. `q` coprime to 5. Clean.
* **Disconnected `H`, isolated and low-degree vertices** — `C5+K1`, `C5+C5`, `C5+C7`,
  `Petersen+K1` exhaustively/randomly swept. An isolated vertex sits in `R` with empty
  neighbourhood and costs `0`. Clean.
* **Unbalanced blow-ups, including a part of size 0** — `C5[3,1,2,2,1]`, `C5[3,3,3,3,2]`,
  `C5[2,2,1,1,1]`, `C5[2,1,1,1,1]` clean. A blow-up with a zero part (`C5[2,2,0,2,2]`,
  `C5[3,1,0,2,1]`) is **bipartite**, has **no induced `C5`**, so Theorem D is vacuous there and
  `psi = 0` anyway (checked).
* **The constant is exactly `1/25`, not `1/25+ε`** — the bound is *attained*: at `ρ = 0` with
  `x` uniform on `C` it reads `psi = 1/25 = (1−0)²/25`. So no additive slack exists in Theorem D
  and the hill-climb maximum of the violation is exactly `0`, attained at every `C5`-concentration.
* **Several overlapping induced `C5`s** — every pentagon of every graph is tested independently
  (MTF14 has 92, `C5[3,3,3,3,2]` has 162, `Γ_14` has 98). Clean.
* **`ρ = 0`** — bound `= 1/25` for **every** `η`, including `η = 1` (all weight on twins, `x(C)=0`):
  then `Σ_i y_i = 1` and AM–GM still gives `1/25`. Checked on `C5[2]`, `C5[3,3,3,3,2]`.
* **`η` close to 1** — covered by the above and by the sweeps with `x(C)` small.
* **Which cut attains the minimum** — the proof *exhibits* one bipartition, so it can only
  over-estimate `psi`; `psi` itself is always computed as the exact minimum over all `2^{n−1}`
  bipartitions (`R9_thmD_lib.psi_int`). Verified independently: `psi(C5,u)=1/25`,
  `psi(C7,u)=1/49`, `bip(MTF14)=7` with 92 pentagons, the blow-up identity
  `psi(C5[V_1..V_5],x) = min_i y_i y_{i+1}` on 200 random blow-ups, and Petersen's spurious local
  maximum `1/32` (`R9_thmD_selftest.py`).

**Conclusion: Theorem D stands. No counterexample exists — I have an independent proof.**

---

## 3. Task 2 — the blocking step

Author's blocking sentence, verbatim:

> "Theorem D's proof uses `|N(v) ∩ C| ≤ 1` for `v ∈ R`, which has no analogue at a blow-up point
> with large classes (placing an `R`-vertex then costs `Θ(ρ/5)` against a `2ρ/25` budget)."

Two independent attacks follow: **§4** keeps the single pentagon and kills the crude `ρη` term
(this gives the improved constant); **§5–6** replaces the pentagon by a blow-up.

---

## 4. THEOREM F — the radius `1/13` becomes `4/25`

Notation: `P_i = {c_i} ∪ T_i`, `z_i = x(P_i)`, `τ = x(T)`, `ρ = x(R)`, `η = τ+ρ`, and

* `e_RT = Σ_{uv ∈ E, u∈R, v∈T} x_u x_v`  (edge weight from `R` into the twins),
* `e_RR = Σ_{uv ∈ E, u,v∈R} x_u x_v`  (edge weight inside `R`).

> **Theorem F.** Let `H` be triangle-free with an induced `C5` `C`. If
> `50·e_RT + 125·e_RR ≤ 1 − (1−ρ)^10`  (∗)
> then `psi(H,x) ≤ 1/25`. Since `e_RT ≤ ρτ` and `e_RR ≤ ρ²/4`, (∗) holds whenever
> `50ρτ + (125/4)ρ² ≤ 1 − (1−ρ)^10`, **in particular whenever `η ≤ 4/25`.**
>
> **Corollary F0.** If `e_RT = e_RR = 0` (every `R`-vertex has all of its neighbours inside `C`)
> then `psi ≤ 1/25` for **every** `x`, with no constraint on `η`. This strictly contains
> Theorem D(a) (`ρ = 0`).

### 4.1 Proof

For `i ∈ Z_5` let `σ_i` be the bipartition with sides `X_i = {P_i,P_{i+1},P_{i+3}}`,
`Y_i = {P_{i+2},P_{i+4}}`, each `v ∈ R` placed on the side minimising its monochromatic weight to
`C ∪ T`. Write `d_i(v) = min_{side} x(N(v) ∩ (C∪T) ∩ side)` and `RR_i` = monochromatic `R`–`R`
weight. By (L2) the `C∪T`-internal monochromatic weight is exactly the `P_i`–`P_{i+1}` weight, so

  **(F1)**  `weight(σ_i) ≤ z_i z_{i+1} + K_i`, `K_i := Σ_{v∈R} x_v d_i(v) + RR_i`.

  **(F2)**  `Σ_{i∈Z_5} K_i ≤ 2·e_RT + 5·e_RR`.

*Proof of (F2).* For `v ∈ R_j` (unique `C`-neighbour `c_j`), the placement "opposite `c_j`" is one
of the two sides, so `d_i(v)` is at most its cost there. By (L3), `N(v)∩T ⊆ T_j ∪ T_{j+2} ∪ T_{j+3}`;
`T_j` sits with `c_j`, hence on the far side of `v`, and `T_{j+2}` (resp. `T_{j+3}`) is on `v`'s side
only for `i ∈ {j, j+1}` (resp. `i ∈ {j+3, j+4}`) — for `i = j+2` the vertex pays **nothing at all**.
Hence `Σ_i d_i(v) ≤ 2·x(N(v) ∩ (T_{j+2}∪T_{j+3})) ≤ 2·x(N(v)∩T)`. For `v ∈ R` with no
`C`-neighbour, the two sides split `T` into `{T_i,T_{i+1},T_{i+3}}` and `{T_{i+2},T_{i+4}}`, so
`d_i(v) ≤ x(N(v)∩T_{i+2}) + x(N(v)∩T_{i+4})` and again `Σ_i d_i(v) ≤ 2·x(N(v)∩T)`. Summing,
`Σ_iΣ_v x_v d_i(v) ≤ 2 e_RT`. Finally `RR_i ≤ e_RR` for each of the 5 cuts. ∎

  **(F3)**  If `z_i z_{i+1} + K_i > 1/25` for every `i`, then `25·Σ_i K_i > 1 − (1−ρ)^10`.

*Proof.* (∗) forces `e_RT ≤ 1/50`, `e_RR ≤ 1/125`, so `K_i ≤ e_RT + e_RR ≤ 7/250 < 1/25` and every
`1/25 − K_i` is positive. Multiplying the five inequalities `z_i z_{i+1} > 1/25 − K_i`:
`(∏_m z_m)² = ∏_i (z_i z_{i+1}) > (1/25)^5 ∏_i (1 − 25K_i) ≥ (1/25)^5 (1 − 25Σ_i K_i)`
(Weierstrass, all `25K_i ∈ [0,1]`), while AM–GM gives
`(∏_m z_m)² ≤ ((1−ρ)/5)^{10} = (1/25)^5 (1−ρ)^{10}`. Compare. ∎

(F1)+(F2)+(F3) give Theorem F. **`η ≤ 4/25 ⟹ (∗)`**: with `τ = η−ρ ≤ 4/25 − ρ`, (∗) reduces to
`φ(ρ) := 1−(1−ρ)^{10} − 8ρ + (75/4)ρ² ≥ 0` on `[0, 4/25]`; since `φ(0)=0`, divide by `ρ`:
`φ(ρ)/ρ = Σ_{k=0}^{9}(1−ρ)^k − 8 + (75/4)ρ`, whose derivative is bounded by `255/4` in absolute
value, and an exact rational Lipschitz grid of 4001 points on `[0,4/25]` gives
`min φ(ρ)/ρ = 0.15686…> 0` (`R9_thmD_thmF.py`, function `verify_F4`). ∎

### 4.2 Sharpness of the improvement, and verification

* Old radius `1/13 = 0.076923…`; new radius `4/25 = 0.16`; **ratio 2.08**.
* The **sharp** radius of this chain is `c* = 0.1631179697…` (the fixed point of
  `c = [1−(1−c)^{10} + (75/4)c²]/(50c)`); the argument is verified to fail at `41/250 = 0.164`
  (at `ρ = 0.1355`) and at `17/100`. `4/25` is the clean constant just below `c*`.
* The **first-order ceiling** of the whole per-cut method is `η ≤ 1/5`: for small `ρ`, all five
  `F_i` can exceed `1/25` only if `Σ_j r_j(τ_{j+2}+τ_{j+3}) > ρ/5`, which needs `τ > 1/5`. The gap
  between `0.1631` and `0.2` is entirely the crude `e_RR ≤ ρ²/4` and Weierstrass steps.
* Exact verification: (F1), (F2) and the conclusion checked on **22 920** instances (all named
  graphs × all pentagons × 26 weight vectors, purpose-built adversaries, random triangle-free
  graphs) — **0 failures** (`R9_thmD_thmF.py`). The per-cut refined bound itself was independently
  checked on **163 320** cut-level instances (`R9_thmD_refined.py`) — **0 failures**. The pure
  algebra step (F3) was checked separately on **199 787** exact `(ρ, z, K)` triples, including the
  adversarial distributions "whole `K`-budget in the cheapest cut" and "split over the two cheapest
  cuts" — **0 failures** (`R9_thmD_F3check.py`); equality holds exactly at `ρ = 0`, `z` balanced.

---

## 5. THEOREM E — the blow-up formulation

### 5.1 The master inequality (proved, and needs no hypotheses at all)

> **Theorem E (master inequality).** Let `V(H) = A_0 ⊔ … ⊔ A_4` be **any** partition,
> `y_m = x(A_m)`. For `i ∈ Z_5` put
> `BAD_i =` (weight of edges inside a class) `+` (weight of edges between classes at
> distance 2 whose *centre* — the class between them — is neither `i` nor `i+1`).
> Then  **`psi(H,x) ≤ min_{i∈Z_5} ( y_i y_{i+1} + BAD_i )`.**

*Proof.* Cut `i` = `{A_i,A_{i+1},A_{i+3}}` vs `{A_{i+2},A_{i+4}}`. Distance-1 class pairs are
monochromatic only for `{i,i+1}`, contributing `≤ y_i y_{i+1}`; a distance-2 pair with centre `m`
is monochromatic iff `m ∉ {i,i+1}`; intra-class pairs always are. ∎

For a **complete induced `C5`-blow-up** `B` in a triangle-free `H` the partition is canonical:

* **(E1)** every `v ∉ B` has `N(v) ∩ B ⊆ V_{m−1} ∪ V_{m+1}` for some `m` — because `N(v)∩B` is
  independent and, `B` being complete, its class-support is an independent set of `C_5`. So `W`
  splits into classes `W_m` and one sets `ŷ_m = x(V_m) + x(W_m)`, `Σ_m ŷ_m = 1`.
* Then `psi ≤ min_i (ŷ_i ŷ_{i+1} + BAD_i)`, and `min_i ŷ_iŷ_{i+1} ≤ 1/25` by AM–GM.
* The identity quoted in the task (`psi = min_i y_iy_{i+1}` for a complete blow-up) is the case
  `W = ∅`, and is reproduced exactly on 200 random blow-ups in `R9_thmD_selftest.py`.

Verified: **3 900** (graph, arbitrary partition, weight) instances including graphs *with*
triangles — 0 failures; plus **545 651** exact weight vectors on random blow-up + `W`
constructions — 0 failures (`R9_thmD_thmE.py`, `R9_thmD_thmE2.py`).

### 5.2 RETRACTION (my own error, caught by the audit)

I first concluded: *"if `BAD_i = 0` for **some** `i`, then `psi ≤ 1/25` for every `x`"*, and on
that basis reported that Theorem E settles the Wagner graph, `Γ_11`, `Γ_14`, the whole Andrásfai
family, and every triangle-free graph on `≤ 10` vertices except Petersen. **That inference is
false and all those coverage claims are withdrawn.** `BAD_{i_0} = 0` only gives
`psi ≤ y_{i_0} y_{i_0+1}`, and the AM–GM bound `1/25` is available only for the *minimising* `i`.
Explicit witness, exact:

> `y = (1/6, 1/4, 1/6, 1/4, 1/6)`, `Σy = 1`, cyclic products `(1/24, 1/24, 1/24, 1/24, 1/36)`.
> The minimum over **any four** of the five cuts is `1/24 > 1/25`.

So even `|I_0| = 4` is insufficient; for `|I_0| = 2` consecutive (the Wagner case)
`y = (1/3,1/3,0,0,1/3)` gives `1/9`. The **correct** unconditional criterion is `BAD_i = 0` for
*all* `i`, i.e. every edge joins consecutive classes — that is precisely a homomorphism
`H → C_5`, which is the classical blow-up case and nothing new.

*(Independent confirmation: `CODEX_THEOREM_E_AUDIT.md`, written by another worker in this
directory on the same day, isolates the same failing step — "a minimum distributed over a sum" —
with a different `And(3)` witness `q=10`, `a=(0,0,0,0,0,2,3,5)`. One correction to that note: it
records the Andrásfai profile as `[0, C(k−2,2), …]`; the exhaustive value is
`[0, C(k−1,2), C(k−1,2), C(k−1,2), 0]`, verified for `k = 3,4,5,6` (`1, 3, 6, 10`).)* Among the test graphs, `H → C5`
holds for `C5`, `C7`, `C9`, `K_{3,3}`, all `C5[…]` blow-ups and the disjoint unions, and fails for
Petersen, Grötzsch, Wagner `=And(3)`, `Γ_11`, `Γ_14`, `And(6)`, MTF14.

---

## 6. What exactly blocks a ball around a blow-up point

Take a complete blow-up `B` and `W ≠ ∅`. Set, for `v ∈ W_m`,
`α_v = y_{m−1} − x(N(v)∩V_{m−1}) ≥ 0`, `β_v = y_{m+1} − x(N(v)∩V_{m+1}) ≥ 0`, and
`D_i = Σ_{v∈W_i} x_v β_v + Σ_{v∈W_{i+1}} x_v α_v ≥ 0`. Refining §5.1:

> **(E-def)**  `psi ≤ min_i ( ŷ_i ŷ_{i+1} − D_i + BAD_i )`,
> and triangle-freeness forces, for every BAD edge `uv`:
> `uv ⊆ W_m` ⟹ `α_u+α_v ≥ y_{m−1}` **and** `β_u+β_v ≥ y_{m+1}`;
> `u∈W_m, v∈W_{m+2}` ⟹ `β_u + α_v ≥ y_{m+1}`.

(Verified: 25 300 cut-level checks, 0 failures, `R9_thmD_necessity.py` §X.)

This is the exact quantitative form of the tension the author identified: a `W`-vertex is
expensive against `B` **only when it is a full twin**, and full twins of the same class or of
classes at distance 2 **cannot be adjacent**. So every unit of `BAD` is paid for by a unit of
deficiency `D`. **The obstruction is a bookkeeping mismatch, and it is exact:**

* a distance-0 bad edge inside `W_m` costs in **all 5** cuts and a distance-2 bad edge costs in
  **3** cuts;
* the compensating deficiency `D_i` is credited in only **2** cuts, `i ∈ {m−1, m}`;
* at a *balanced* `ŷ` the AM–GM slack `1/25 − min_i ŷ_iŷ_{i+1}` is exactly **0**, so there is no
  third source of budget.

Consequently the method proves `psi ≤ 1/25` at a blow-up point **iff** some `i` with
`ŷ_iŷ_{i+1} ≤ 1/25` also has `D_i ≥ BAD_i`; it does **not** deliver a ball of positive radius in
`x(W)` around a balanced blow-up point. Concretely, for a single bad edge `uv` inside `W_m` with
weights `s,t`, cut `i = m` works iff `max(s,t) ≤ y_{m+1}`, but cuts `m+1, m+2, m+3` are then
unusable, and the adversary is free to make `m` the cut where `ŷ_mŷ_{m+1}` is *largest*. This is
the same wall as registry entry **A6 / K-3**: *the cut that AM–GM likes and the cut that the
`W`-accounting likes cannot be forced to coincide.*

---

## 7. Can finitely many balls cover the simplex? — the residual, precisely

**No, not with pentagon balls alone.** For any `H` whose weight is spread over more than five
vertices, every induced `C5` has `η ≥ 1 − 5·max_v x_v`; e.g. on `C5[2]` at the uniform point
`η = 1/2` for **every** pentagon, far outside `4/25`. Theorem F balls therefore miss the entire
blow-up plateau — which is exactly why §5 is needed, and §5's unconditional reach is exactly
`H → C_5`.

**The residual is therefore, precisely:**

> the set of pairs `(H,x)` such that (i) every induced `C5` of `H` has `η > 4/25` (more precisely,
> fails (∗)), and (ii) for every complete induced `C5`-blow-up `B` of `H`, every legal class
> assignment `m(·)` and every `i ∈ Z_5`,
> `ŷ_i ŷ_{i+1} − D_i + BAD_i > 1/25`.

Smallest concrete inhabitants (all triangle-free, all containing induced `C5`s, none with a
homomorphism to `C5`). The table gives, over **all** complete induced blow-ups, **all** legal
assignments and each cut, the number of BAD edges left (exact, exhaustive):

| graph | `|W|` | best bad-edge count per cut `(i=0..4)` | #cuts with `BAD_i = 0` |
|---|---|---|---|
| Wagner `= And(3) = C8(1,4)` | 3 | `[0,1,1,1,0]` | 2 |
| `Γ_11 = And(4)` | 6 | `[0,3,3,3,0]` | 2 |
| `Γ_14 = And(5)` | 9 | `[0,6,6,6,0]` | 2 |
| `Γ_17 = And(6)` | 12 | `[0,10,10,10,0]` | 2 |
| `And(k)`, `k ≥ 3` | `3k−6` | `[0,C(k−1,2),C(k−1,2),C(k−1,2),0]` (checked `k ≤ 6`) | 2 |
| Grötzsch | 6 | min over cuts `= 1` | 0 |
| MTF14 `= M?AE@bH{AYN_LgBs?` | 9 | min over cuts `= 1` | 0 |
| Petersen | 5 | min over cuts `= 2` (all 12 pentagons) | 0 |

The whole Andrásfai family sits at `|I_0| = 2`, and `|I_0| = 2` consecutive is exactly the case
killed by `y = (1/3,1/3,0,0,1/3)` in §5.2 — this is the sharpest possible near-miss. Petersen is
the extreme case: it has no twins, so its only complete blow-ups are the 12 pentagons themselves,
`W` is always the pentagram, and every one of the `2^5` admissible assignments leaves at least
**2** bad edges in **every** cut.

**A warning about the natural strengthening.** Let `MB(H,x) = min` over all admissible
`C5`-blow-up partitions **and** all 5 cuts of `(ŷ_iŷ_{i+1} + BAD_i)`, so `MB ≥ psi`. Adversarial
hill-climbing (`R9_thmD_maxbound.py`, started from every `C5`-concentration and every blow-up
weighting, `q ≤ 45`) found `max_x MB(H,x) = 1/25` **exactly**, attained at the `C5`-concentrations,
for `C5`, `C5[2]`, `C5[2,2,1,1,1]`, **Wagner**, **`Γ_11`**, **Petersen** and **Grötzsch** — i.e. the
master inequality *empirically* settles even the residual graphs, once the minimum is taken over
*all* partitions. That is suggestive but it is **not** a legal target, and I flag it explicitly per
the anti-reformulation rule. The lemma it would need, verbatim:

> "For every triangle-free graph `H` containing an induced `C_5` and every `x ∈ Δ(V(H))`,
> `min` over admissible `C5`-blow-up partitions `P` and cuts `i ∈ Z_5` of
> `( y_i y_{i+1} + BAD_i ) ≤ 1/25`."

Since `MB ≥ psi`, this lemma **implies the conjecture for every triangle-free graph with an
induced `C_5`** — i.e. everything except odd girth `≥ 7`, which is the far side of the problem and
is nowhere near tight (`C_7` gives `1/49 ≈ 0.51·(1/25)`). It is therefore *at least as strong as*
the conjecture in the only regime that matters, and must not be adopted as a target lemma. (Its one
genuine merit, worth recording: it replaces the `2^{n−1}`-fold minimum defining `psi` by a minimum
over an explicit finite family of quadratic forms.)

---

## 8. Files

| file | contents |
|---|---|
| `R9_thmD_lib.py` | exact engine: graph6 I/O, exact `psi` by minimisation over all `2^{n−1}` bipartitions (numpy int64), induced-`C5` enumeration, `T_i/R` classification, named graphs (incl. Wagner `= C8(1,4)`, `And(k) = Γ_{3k−1}`, MTF14). |
| `R9_thmD_selftest.py` | 50 sanity checks against known values before anything is trusted. |
| `R9_thmD_audit.py` | Task 1: exhaustive + random + hill-climbing violation search (5 157 802 instances). |
| `R9_thmD_adversarial.py` | Task 1: proof steps L1–L4, purpose-built adversaries, random triangle-free graphs. |
| `R9_thmD_refined.py` | the refined per-cut bound `F_i` and its exact verification (163 320 checks). |
| `R9_thmD_opt.py` | relaxation scan locating the first-order ceiling `η = 1/5`. |
| `R9_thmD_thmF.py` | **Theorem F**: exact `φ(ρ) ≥ 0` verification on `[0,4/25]`, (F1)(F2) checks. |
| `R9_thmD_F3check.py` | isolated exact check of the product/Weierstrass step (F3). |
| `R9_thmD_thmE.py`, `R9_thmD_thmE2.py` | **Theorem E** master inequality, the false-corollary witness, `H → C5` census. |
| `R9_thmD_coverage.py` | partition/assignment search (`hom_exists`, `blowups_from_C5`) — note its `e_covered` implements the **retracted** criterion of §5.2 and is kept only as the search primitive used by `R9_thmD_maxbound.py`. |
| `R9_thmD_maxbound.py` | adversarial maximisation of `MB(H,x)`. |
| `R9_thmD_necessity.py` | triangle-freeness counterexamples; deficiency-refinement verification. |
