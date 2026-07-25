# Round 8 — TRANSPORT AND FLOW FORMULATIONS

Erdős #23: every triangle-free `G` on `N` vertices has `bip(G) = |E| − maxcut(G) ≤ N²/25`.
Weighted form: `ψ(H,x) = min_S Σ_{uv monochromatic} x_u x_v` on the simplex, target `max_x ψ ≤ 1/25`.

Mechanism assigned: min-cost flow, multicommodity flow, transportation/optimal transport,
circulation, metric/embedding formulations — and nothing else.

**VERDICT. The mechanism produced one genuinely new certificate family (the multiplicative /
entropy transport certificate, §4.3), which is strictly stronger than the registry's dead
arithmetic-averaging family A6 — it is *exactly tight* on the whole extremal family `C5[n]`,
where A6 fails — and it is nevertheless DEAD, refuted exactly on two 11-vertex graphs.
Every other transport branch collapses onto an already-dead family by an exact identity.
No new bound on `bip` was obtained. The blocking step is quoted verbatim in §4.3.3.**

All decisive numbers below are exact (`fractions.Fraction` / integers). Anything that is only
numerical is labelled NUMERICAL and is not used to support any claim.

---

## 0. What died, on which witness (ledger first)

| # | transport object | status | exact witness |
|---|---|---|---|
| T1 | exact min-cost-flow / T-join model of `bip` | **impossible in general** | `bip` = min-weight coset rep. in the **co**graphic matroid = MaxCut, NP-hard on triangle-free graphs (double subdivision, GATE 2) |
| T1' | planarise and use the dual T-join | **vacuous** | planar triangle-free ⟹ `\|E\| ≤ 2N−4` ⟹ `bip ≤ \|E\|/2 ≤ N−2 ≤ N²/25` for `N ≥ 23`; `N ≤ 40` already proved |
| T2 | metric / cut-cone / ℓ₁-embedding lower bound on maxcut | **DEAD = A6 identically** | Theorem 2.1: *every* ℓ₁ decomposition bound **is** an arithmetic mean over cuts; cap `1/20` on every `C5[n]` (Prop. 2.2) |
| T3 | multicommodity flow / multicut in the bipartite double cover (= odd-cycle packing) | **DEAD, gap unbounded** | flow/cut gap `≥ (g/2)(1−2√(d−1)/d) → ∞` on triangle-free Ramanujan graphs; and `35/32` at `M?AE@bH{AYN_LgBs?` (registry A5) |
| T4a | mass transport onto `C5` with defect ("pay for non-homomorphism") | **not a relaxation** | degenerate 5-profiles reproduce *every* bipartition, so the "relaxation" equals `ψ` identically (Prop. 4.1) |
| T4b | Motzkin–Straus support-transport LP ("Conjecture T", §4.2) | **FALSE** | uniform `x`: Wagner `1/2`, Petersen `3/5`, Grötzsch `5/11`, And(4) `6/11`, `M?AE@bH{AYN_LgBs?` `4/7` — all `> 2/5` |
| T5 | **multiplicative / entropy transport certificate** (§4.3) — new, strictly stronger than A6 | **DEAD** | (i) **And(4) = Γ₁₁**: *no* cut is optimal on all 33 induced `C5`s; every `λ` gives `≥ 3^{171/2522}/25 = 0.043093`. (ii) **Grötzsch**: all 5 admissible cuts give `ν = 1/20` at `x = (0⁵,(1/10)⁵,1/2)` while `ψ = 0` |

Survivors of T5, both **numerical only**: Wagner `= And(3)` and Petersen, neither of which is
`C5`-colourable; the two explicit polynomial inequalities are displayed in §4.3.6.

---

## 1. Which flow models exist at all (T1)

**Identity 1.1 (coset form).** For `S ⊆ V` let `∂S ∈ GF(2)^E` be the incidence vector of the cut.
The cut space `Cut(G) = {∂S}` is a linear code of length `|E|` and dimension `N − c(G)`. An edge
set `F` makes `G − F` bipartite iff `F = 1_E + ∂S` for some `S`. Hence

> `bip(G) = min { wt(f) : f ∈ 1_E + Cut(G) }`  — the minimum-weight coset leader of the
> all-ones syndrome in the cocycle code, i.e. the frustration index of the all-negative signed graph `(G, E)`.

**Identity 1.2 (planar = T-join = min-cost flow).** If `G` is planar with dual `G*`, then
`Cut(G) = Cycle(G*)`, so `1_E + Cut(G)` is exactly the set of `T`-joins of `G*` with
`T = {odd faces of G}`. Minimum `T`-join is a min-cost flow / matching problem; this is the only
place where a genuine flow model of `bip` exists.

**Obstruction 1.3 (no flow model beyond planar).** MaxCut is NP-hard on triangle-free graphs, so
no polynomial flow/circulation model computes `bip` on the triangle-free class unless P = NP.
*Proof.* Let `G''` be `G` with every edge subdivided twice. Every path `u–a–b–v` carries 3 cut
edges if `u,v` are separated and at most 2 otherwise, both bounds attainable independently, so
`maxcut(G'') = maxcut(G) + 2|E(G)|`, while `girth(G'') = 3·girth(G) ≥ 9`. ∎
(Identity verified exactly for `K3, K4, C5` in `R8_transport_gates.py`, GATE 2.)

**Obstruction 1.4 (planarising is worthless).** For planar triangle-free `G`, `|E| ≤ 2N − 4`, and
`maxcut ≥ |E|/2` gives `bip ≤ |E|/2 ≤ N − 2`. Since `N − 2 ≤ N²/25` for `N ≥ 23` and the
conjecture is already proved for `N ≤ 40` (accepted base (3)), **the planar case of Erdős #23 is
trivial**; a perfect solution of the dual T-join model proves nothing new. And `bip` is not
minor-monotone in any direction that transfers a bound from a planar minor back to `G`.

The correct non-planar analogue of 1.2 is Guenin's odd-`K5` theorem, which is registry A5b and is
already recorded as unavailable from `And(4)` on.

---

## 2. Metric / cut-cone / ℓ₁ embeddings (T2): an exact identification with the dead family A6

Write `w_{uv} = x_u x_v`, `W = Σ_{uv∈E} w_{uv}`, `ν_S(x) = Σ_{uv monochromatic under S} w_{uv}`, so
`ψ(H,x) = min_S ν_S(x) = W − max_S w(δ(S))`. Upper bounds on `ψ` need **lower** bounds on the
weighted maxcut, i.e. **inner** approximations of the cut cone `CUT_N = cone{δ_S}`, i.e. ℓ₁
decompositions. (Outer relaxations — the metric polytope, the GW SDP, `MET_N` — bound maxcut from
above and are therefore useless here; that is the whole content of "the metric polytope is the
wrong direction".)

**Theorem 2.1.** Let `d = Σ_S λ_S δ_S` be any ℓ₁ (cut-cone) decomposition, `λ ≥ 0`, and let
`μ_S = λ_S / Σ_T λ_T`. Then the resulting bound is
`ψ(H,x) ≤ W − ⟨w,d⟩/Σλ = Σ_S μ_S ν_S(x)`,
i.e. **every metric/ℓ₁/cut-cone lower bound on maxcut is literally the arithmetic mean of the
monochromatic weights over the distribution `μ`, and conversely.** The two families are equal, not
merely comparable.
*Proof.* `⟨w,d⟩ = Σ_S λ_S w(δ(S)) ≤ (Σλ) max_S w(δ(S))`, so `max_S w(δ(S)) ≥ ⟨w,d⟩/Σλ`; subtract
from `W` and use `W − w(δ(S)) = ν_S(x)`. ∎

**Proposition 2.2 (the cap).** For every `H` and every distribution `μ` over cuts,
`max_x Σ_S μ_S ν_S(x) ≥ bip(H) / (4|E(H)|)`, which equals `1/20` on every `C5[n]`.
*Proof.* `Σ_S μ_S ν_S(x) = Σ_e p_e w_e` with `p_e = Pr_μ[e monochromatic]`, and
`Σ_e p_e = E_μ[#mono] ≥ bip(H)`, so some `e* = uv` has `p_{e*} ≥ bip/|E|`; take `x_u = x_v = 1/2`. ∎

So the entire metric-embedding branch is the registry's family **A6**, capped at `1/20` against the
truth `1/25` on the extremal object itself. DEAD. (Concretely: the natural `C5` cut decomposition
`d_{C5} = ½ Σ_{i∈Z₅} δ_{\{i,i+1\}}` reproduces exactly the `4W/5` bound, i.e. `1/20`.)

This is the reason §4.3 replaces the arithmetic mean by the **geometric** mean: Prop. 2.2 is an
obstruction to *arithmetic* averaging only.

---

## 3. Multicommodity flow / sparsest-cut duality (T3)

**Formulation 3.1 (the honest flow model).** Let `G×K₂` be the bipartite double cover, vertices
`(v,0),(v,1)`, edges `(u,i)(v,1−i)` for `uv ∈ E`. Odd closed walks of `G` through `v` correspond to
`(v,0)–(v,1)` paths. Under the capacity identification of the two lifts `e₀,e₁` of each edge `e`:

> `bip(G)` is the minimum **multicut** separating the `N` pairs `{(v,0),(v,1)}` in `G×K₂`, and its
> LP dual is the maximum **multicommodity flow** for those `N` commodities — equivalently the
> fractional odd-cycle packing `ν*(G) = τ*(G)`.

This is the exact sense in which #23 has a multicommodity-flow formulation. The assigned question is
whether triangle-freeness controls the flow–cut gap.

**Answer 3.2: no, the gap is unbounded inside the triangle-free class.**
For a `d`-regular graph, `maxcut ≤ (|E|/2)(1 + |λ_min|/d)` (from `Σ_{uv∈E}(1−s_us_v)/2 = m/2 −
¼s^⊤As ≤ m/2 − ¼λ_min n`), so `bip ≥ (|E|/2)(1 − |λ_min|/d)`; and `y ≡ 1/g` is feasible for the
covering LP when the odd girth is `≥ g`, so `τ* ≤ |E|/g`. Hence

> `bip/τ* ≥ (g/2)(1 − |λ_min|/d)`.

Take LPS Ramanujan graphs `X^{p,q}` (`d = p+1 ≥ 20`, `|λ_min| ≤ 2√(d−1)`, girth `g = Θ(log n) ≥ 5`,
hence triangle-free): `bip/τ* ≥ 0.28·g → ∞`. So no triangle-free hypothesis can bound the
integrality gap by a constant, let alone by the `25/20 = 1.25` that the packing bound `τ* ≤ |E|/5 ≤
N²/20` would need. (Cited literature: Lubotzky–Phillips–Sarnak; the spectral maxcut bound is
proved above.) On the finite side, the registry's exact witness `M?AE@bH{AYN_LgBs?` already gives
`τ = 7 > 32/5 = τ*`, gap `35/32`.

Corollary: **`bip ≤ |E|/5` is false for triangle-free graphs** (same witness: `7 > 32/5`), although
it holds with equality on `C5[n]`, Petersen and Grötzsch. Any flow/packing route inherits this.

---

## 4. Mass transport onto the `C5` structure (T4)

### 4.1 The reformulation trap

Let `φ : V → Z₅` be any 5-profile, `X_j = x(φ^{-1}(j))`, and let `D(φ)` be the `ν`-weight of the
edges that are **not** between consecutive classes (the transport defect). Using the five cuts
`S_i = φ^{-1}{i,i+2}` one gets the clean-looking transport bound

> `ψ(H,x) ≤ min_φ [ min_i X_i X_{i+1} + D(φ) ] ≤ 1/25 + min_φ D(φ)`.

**Proposition 4.1.** `min_φ [ min_i X_iX_{i+1} + D(φ) ] = ψ(H,x)` identically: it is not a
relaxation at all. *Proof.* Given any bipartition `(S,S̄)` put `V_1 = S`, `V_0 = S̄`,
`V_2 = V_3 = V_4 = ∅`. Then `min_i X_iX_{i+1} = 0` and `D(φ) = ν_S(x)`. ∎

So "transport `H` onto `C5` and pay for the defect" is a **rename**, matching the GOAL clause (a).
It is recorded here because the formulation is superficially attractive and reappears in several
guises (circular colourings, `χ_c ≤ 5/2` with defect, arc-cut families with error terms).

### 4.2 The support-transport LP ("Conjecture T") — refuted

Motzkin–Straus for triangle-free graphs gives, with `U_S = {v : v meets a monochromatic edge of S}`,
`ν_S(x) ≤ x(U_S)²/4`, tight on `C5` and on `C5[n]`. So `ψ ≤ ¼ (min_S x(U_S))²`, and by LP duality
`max_x min_S x(U_S) = min_λ max_v Pr_{S∼λ}[v ∈ U_S]`. The clean transport statement is:

> **Conjecture T (verbatim, and FALSE).** *For every triangle-free graph `H` there is a probability
> distribution `λ` over bipartitions such that every vertex `v` satisfies
> `Pr_{S∼λ}[ v is incident to a monochromatic edge of S ] ≤ 2/5`.*

It implies the conjecture (`ψ ≤ ¼(2/5)² = 1/25`), is exactly tight on `C5` (uniform on the 5 cuts
`{i,i+2}`; each vertex is touched by exactly 2 of the 5) and on `C5[n]` (Mantel: `|U_S|² ≥
4|mono(S)| ≥ 4bip`, equality iff the monochromatic set is a balanced complete bipartite graph, which
is exactly what the class cut `V_i ∪ V_{i+2}` produces).

It is **false**: already at uniform `x`, `min_S x(U_S)` equals `1/2` (Wagner), `3/5` (Petersen),
`5/11` (Grötzsch), `6/11` (And(4)), `4/7` (`M?AE@bH{AYN_LgBs?`), all `> 2/5`
(`R8_transport_gates.py`, GATE 3, exact). The reason is structural, not accidental: equality in
Mantel forces the monochromatic graph to be a *balanced complete bipartite* graph, which happens
only inside `C5`-blow-ups.

### 4.3 The multiplicative (entropy) transport certificate — the one new object, and its death

#### 4.3.1 Definition and validity

For any probability distribution `λ` over cuts, `min ≤ weighted geometric mean` gives the valid
bound

> **(MC)**  `ψ(H,x) = min_S ν_S(x) ≤ Π_S ν_S(x)^{λ_S}` for all `x`,

so `max_x Π_S ν_S(x)^{λ_S} ≤ 1/25` would prove the conjecture for `H`. This is the multiplicative
analogue of A6/Theorem 2.1 and is **not** covered by Prop. 2.2.

#### 4.3.2 The exact transport/entropy dual (this is the "transport" content)

**Theorem 4.2 (GP duality identity).** With `M_S = mono(S)`, `q_S` a probability distribution on
`M_S`, `c_v(q_S) = Σ_{e ∈ M_S, v ∈ e} q_S(e)`, `C_v = Σ_S λ_S c_v(q_S)` (so `Σ_v C_v = 2`) and
`p = C/2`:

> `max_{x ∈ Δ} Π_S ν_S(x)^{λ_S} = exp( max_q [ Σ_S λ_S H(q_S) − 2 H(p_q) ] )`, `H` = Shannon entropy (nats).
>
> Hence **(MC) certifies `H` iff for every transport plan `q`:  `2H(p_q) − Σ_S λ_S H(q_S) ≥ 2 log 5`.**

*Proof.* Gibbs' variational formula `log Σ_e a_e = max_q [Σ_e q_e log a_e + H(q)]` with
`a_e = x_ux_v` turns `Σ_S λ_S log ν_S(x)` into `max_q [Σ_v C_v log x_v + Σ_S λ_S H(q_S)]`; then
`max_{x∈Δ} Σ_v C_v log x_v = Σ_v C_v log(C_v/2) = −2H(p)` at `x = p`. ∎

`p` is literally the transport of the cut-selection measure down to the vertices; the certificate is
an **entropy ≥ log 5** condition, the exact quantitative form of "the weight must look like five
equal classes".

#### 4.3.3 Exactness on the extremal family, and where it stops

*Positive.* If `H → C5` (equivalently `H ⊆ C5[a]`), take the 5 class cuts `S_i = V_i ∪ V_{i+2}` with
`λ ≡ 1/5`. Then `mono(S_i) ⊆ V_{i+3} × V_{i+4}`, so
`Π_i ν_{S_i}^{1/5} ≤ Π_i (X_{i+3}X_{i+4})^{1/5} = (Π_j X_j)^{2/5} ≤ (5^{-5})^{2/5} = 1/25` by AM-GM,
**with equality exactly at the balanced blow-up.** In the dual of Thm 4.2, for `C5[n]` with `q_i`
uniform on the `n²` edges of `M_i`: `H(q_i) = 2 log n`, `p` uniform on `5n` vertices,
`H(p) = log 5n`, difference `= −2 log 5` exactly. So (MC) is *tight on the whole extremal family*,
precisely where the arithmetic family A6 loses `1/20` vs `1/25`.

*(Caveat for readers of `R8_transport_geomval.py`: `λ` must be the 5 class cuts, not the uniform
distribution over all `C5`-perfect cuts. On the unbalanced blow-up `C5[3,1,2,2,1]` there are 15
`C5`-perfect cuts and uniform `λ` over all of them gives an exact violation
`0.041038 > 1/25` at `x = (1,1,1,2,1,1,1,1,2)/11`, while the 5 class cuts with `λ ≡ 1/5` give
`(Π_j X_j)^{2/5} ≤ 1/25`. Choosing `λ` badly is not a refutation; Lemma 4.3 and §4.3.5 are
statements about **every** `λ`.)*

*The obstruction.* Let `C` be an induced `C5` of `H` and `x_C` uniform on `C`. Then
`ν_S(x_C) = k_S(C)/25` where `k_S(C) = #` monochromatic edges of `S` inside `C`, an **odd** number
`≥ 1`; so `ψ(H,x_C) = 1/25` (this re-derives accepted base (4)) and

> **Lemma 4.3 (plateau rigidity).** If some `S₀ ∈ supp(λ)` has `k_{S₀}(C) ≥ 3` for some induced `C5`
> `C`, then `max_x Π_S ν_S^{λ_S} ≥ (1/25)·3^{λ_{S₀}} > 1/25`.
> Hence **(MC) can certify `H` only if some cut is simultaneously optimal on every induced `C5`**
> (call such a cut *`C5`-perfect*). The same holds for any relaxed values `g_S ≥ ν_S` and for any
> mean `M` with `M(t,…,t) = t` that is strictly increasing in each argument — arithmetic, geometric,
> any power mean.

**BLOCKING STEP, verbatim:** *"there exists a cut `S` of `H` that leaves exactly one monochromatic
edge inside every induced `5`-cycle of `H`"* — this is false for `And(4)`, and even when true it is
not sufficient (Grötzsch).

#### 4.3.4 Witness A — And(4) = Γ₁₁ has no `C5`-perfect cut

`And(4)` = circulant on `Z₁₁` with connection set `{4,5}` (4-regular, 22 edges, triangle-free,
`bip = 4 ≤ 121/25`). Exhaustive over all `2^{10}` cuts and all `33` induced `C5`s: **`0` `C5`-perfect
cuts**; every cut leaves `3` monochromatic edges in some induced `C5`. Verified twice by
independent implementations (`R8_transport_c5perfect.py` — 5-subset enumeration, bitmask cuts;
`R8_transport_verify.py` — DFS cycle search, tuple cuts). Same for `And(5) = Γ₁₄` (98 induced `C5`s)
and for `M?AE@bH{AYN_LgBs?` (92 induced `C5`s). By contrast `C5`, `C5[n]`, Wagner, Petersen,
Grötzsch, and all 31 triangle-free graphs of `round1/base10.g6` **do** have `C5`-perfect cuts, and
exactly one of the 61 graphs of `round1/base11.g6` lacks one, namely `J?bFF\`wN?{?`, which nauty
`labelg` certifies isomorphic to `And(4)` (both canonicalise to `Js\`@IStU\`w?`). Every 10-vertex
induced subgraph of `And(4)` has exactly 5 `C5`-perfect cuts, so `And(4)` is induced-minimal for
this failure.

*Quantitative form.* With `β(H) = max_μ min_S μ({C : k_S(C) ≥ 3})` (a matrix game solved by LP and
re-verified exactly over all cuts with `Fraction`s), `max_C ≥ E_μ` gives for **every** `λ`:

| `H` | verified `β ≥` | `max_x Π ν_S^{λ_S} ≥ 3^β/25` | excess over `1/25` |
|---|---|---|---|
| `And(4) = Γ₁₁` | `171/2522` | `0.043093` | `+7.73 %` |
| `M?AE@bH{AYN_LgBs?` | `1/13` | `0.043527` | `+8.82 %` |
| `And(5) = Γ₁₄` | `2/21` | `0.044412` | `+11.03 %` |

#### 4.3.5 Witness B — Grötzsch: the necessary condition holds and the certificate still dies

The Grötzsch graph (Mycielski of `C5`; `N = 11`, 20 edges, `bip = 4`) has exactly **5** `C5`-perfect
cuts, so `supp(λ)` is confined to them. At the explicit rational point

> `x = (0,0,0,0,0, 1/10,1/10,1/10,1/10,1/10, 1/2)`  (½ on the apex, 1/10 on each shadow vertex)

**all five** have `ν_S(x) = 1/20` exactly, while `ψ(Grötzsch, x) = 0`. Hence for *every* `λ`,
`Π_S ν_S(x)^{λ_S} = 1/20 > 1/25`: a `25 %` failure at a point where the truth is `0`.
(Independently recomputed in GATE 1; a second exact witness `x = (0⁵,(1/9)⁵,4/9)` gives `4/81` for
all five.)

*Why:* the five `C5`-perfect cuts each leave exactly one apex edge `(shadow_i, apex)` monochromatic.
`C5`-perfectness (forced by the `C5`-plateau points) is **incompatible** with separating the apex
from its neighbourhood (forced by the star points). Two families of near-extremal weightings impose
contradictory demands on one cut family. Generally: in a triangle-free graph `N(u)` is independent,
so if `5 ≤ d(u) ≤ 6` and no `C5`-perfect cut separates `u` from `N(u)`, then
`x = ½` on `u`, `1/(2d(u))` elsewhere on `N(u)` gives every admissible cut
`ν_S ≥ 1/(4d(u)) ≥ 1/24 > 1/25`.

**Lemma 4.4 (failure is hereditary upward).** If `H` is an induced subgraph of `H'` and (MC) fails
for `H`, it fails for `H'`: every `C5`-perfect cut of `H'` restricts to a `C5`-perfect cut of `H`,
and for `x` supported in `V(H)` the values `ν` agree. So **every triangle-free graph containing an
induced `And(4)` or an induced Grötzsch kills (MC)** — the failure is structural, not sporadic.

**Consequence for the whole programme.** Lemmas 4.3–4.4 say that no certificate which picks its cut
family (with any weights, any means, any relaxed values) *before seeing `x`* can work — the
`C5`-plateau points and the star points impose contradictory demands. This is the exact,
witness-backed form of the project's recorded rule "a proof must read the weights", now extended
from arithmetic averaging (A6, killed at `C5[n]`) to every mean including the geometric one, which
survives `C5[n]` exactly.

#### 4.3.6 What survives (NUMERICAL ONLY, not proved)

`Wagner = And(3)` and `Petersen` are **not** `C5`-colourable (exhaustive check over all `5^{n−1}`
maps) yet both pass. For Wagner the 5 `C5`-perfect cuts are the four arcs `{j,…,j+3}` and the
alternating cut `{0,2,4,6}`, and `λ` is *forced* to be uniform (restricted to the support of the
induced `C5` `(0,3,6,1,4)` the five quadratics become exactly the five edge-products of that `C5`,
so Thm 4.2 gives `exp(−2H(p))` and `p` must be uniform). The certificate is then the explicit
degree-10 inequality in 8 variables, `x ≥ 0`:

> `(x₀x₃+x₄x₇)(x₀x₅+x₁x₄)(x₁x₆+x₂x₅)(x₂x₇+x₃x₆)(x₀x₄+x₁x₅+x₂x₆+x₃x₇) ≤ 25^{−5} (Σx)^{10}`,

with equality exactly at the 8 induced `C5`s (uniform `1/5`), e.g. `x = (⅕,⅕,0,⅕,⅕,0,⅕,0)`.
Maximisation over **all 255 faces** of the simplex with multistart mirror ascent returns
`0.040000000000` (excess `2.8·10⁻¹⁷`); Petersen likewise returns `0.040000000000`. **Not proved.**
Even if both are true they are of no use: the scheme is already dead at `And(4)` and Grötzsch.

It is worth recording that this boundary — works at `And(3)`, fails at `And(4)` — coincides exactly
with the recorded Guenin/odd-`K5` boundary (memory: "Guenin boundary is exactly And(3) yes / And(4)
no"), reached here by a completely unrelated mechanism.

---

## 5. Relation to the registry

* **A6** (fixed arithmetic averaging) is *strictly extended*: Theorem 2.1 shows the metric/ℓ₁ branch
  IS A6, and Lemma 4.3 kills every mean (geometric, any power mean, any relaxed values), not just
  the arithmetic one. A6's witness was `C5[n]` (`1/20`); the geometric mean survives `C5[n]` exactly
  and needs the new witnesses `And(4)` / Grötzsch.
* **A5 / A5b** (covering–packing) is confirmed dead from a flow angle and strengthened: the gap is
  not merely `35/32` at one graph, it is unbounded inside the triangle-free class (§3.2).
* **A7 / A20** (neighbourhood covering): the *single-root* BFS bound is contained in them. For
  triangle-free `G` of diameter 2, BFS from `v` has `L₁ = N(v)` independent, so the horizontal-edge
  bound is exactly `bip ≤ e(G − N[v])`, i.e. A7, dead on Wagner (`3 > 64/25`). See §7 for the
  *full* distance-level family, which is a rename.
* **A1** (arc cuts) is *not* touched: it is a `min` over a family, not a mean, so Lemma 4.3 does not
  apply to it.

## 7. Metric potentials / distance level sets: a second rename

A `1`-Lipschitz potential `f : V → Z` (equivalently a homomorphism to the infinite reflexive path)
has `|f(u) − f(v)| ≤ 1` on edges, and the cut `f^{-1}(even)` has monochromatic set exactly the
*horizontal* edges `{uv : f(u) = f(v)}`. Distance functions `f = d(·,A)` are the canonical examples,
and the resulting bound `bip(G) ≤ min_A Σ_i e(L_i(A))` is exactly tight on `C5[n]` (take
`A = V_0`: levels `V_0 | V_1∪V_4 | V_2∪V_3`, horizontal edges `= E(V_2,V_3)`, `n²`).

**It is nevertheless a rename.** (i) Two-valued Lipschitz potentials are exactly arbitrary
bipartitions, so the unrestricted Lipschitz family is all of `ψ`. (ii) Even the restricted
*distance-parity* family `{parity classes of d(·,A) : A ⊆ V}` is the full set of `2^{N−1}`
bipartitions on every graph tested — C5, C5[2], Wagner, Petersen, Grötzsch, And(4),
`M?AE@bH{AYN_LgBs?` — and attains `bip` on each. So metric potentials reformulate `bip` without
restricting it, and fall under GOAL clause (a). Only the *sub*families (single root = A7, distance
from an independent set = A20) are genuine restrictions, and those are already dead.

## 6. Files (all in `problems/23/round8/`)

| file | content |
|---|---|
| `R8_transport_lib.py` | exact core: graph6, blow-ups, Andrásfai, Wagner, Mycielski, exact `bip`/`ψ`, testbed |
| `R8_transport_basic.py` | exact `bip`, `min_S \|U(S)\|` table for the mandated testbed |
| `R8_transport_c5perfect.py` | `C5`-perfect cut enumeration (implementation 1) |
| `R8_transport_verify.py` | independent re-implementation of the same (different representation) |
| `R8_transport_blocking.py` | minimum blocking families of induced `C5`s (bitmask) |
| `R8_transport_beta.py` | exact `β(H)` and the constants `3^β/25` |
| `R8_transport_geomval.py` | value of the multiplicative certificate; exact violation search |
| `R8_transport_wagner.py` | forced-`λ` analysis and certificate value for Wagner/Petersen/Grötzsch |
| `R8_transport_wagner_faces.py` | face-by-face (all 255 supports) maximisation for Wagner |
| `R8_transport_gates.py` | GATE 1 Grötzsch witness (independent), GATE 2 subdivision identity, GATE 3 Conjecture T |
| `R8_transport_metric.py` | distance-parity cut family (= all cuts, §7) and the `And(4)` ↔ `J?bFF\`wN?{?` identification |

Reproduce with `python R8_transport_gates.py`, `python R8_transport_c5perfect.py`,
`python R8_transport_verify.py`, `python R8_transport_beta.py`, `python R8_transport_metric.py`
(each < 2 min; `R8_transport_geomval.py` and `R8_transport_wagner_faces.py` are the slow numerical ones).
