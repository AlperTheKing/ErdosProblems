# Round 3 — root-agent (Claude) results, exactly verified

Continues `round1/CLAUDE_GATE_RESULTS.md`. Everything here is either a complete proof or an object
verified in exact rational/integer arithmetic by my own implementation. Agent reports are NOT in
this file until I have re-derived them.

---

## R3-C1 — every fixed averaging certificate is dead, with an exact 25 % gap

Full write-up: `R3C1_AVERAGING_CERTIFICATES_DEAD.md`. Verified by `claude_gate_psi_structure.py`.

**Theorem.** For every graph `H` with an edge and every probability distribution `λ` on the cuts of
`H`, writing `c_e = Pr_λ[e monochromatic]`, the certificate value
`B(λ) = max_{x ∈ Δ} Σ_{e=uv} c_e x_u x_v` satisfies

```
        B(λ)  ≥  (max_e c_e)/4  ≥  (Σ_e c_e)/(4|E|)  ≥  bip(H)/(4|E(H)|).
```

Hence no averaging certificate proves `max_x ψ ≤ 1/25` for any `H` with `25 bip(H) > 4|E(H)|`.

| `H` | `bip` | `|E|` | floor `bip/4|E|` | averaging certificate |
|---|---|---|---|---|
| `C5`, `C5[2]`, `C5[3]` | 1, 4, 9 | 5, 20, 45 | **1/20 = 0.0500** | DEAD at every order |
| Petersen | 3 | 15 | 1/20 | DEAD |
| Grötzsch | 4 | 20 | 1/20 | DEAD |
| extremal `N=12`, `N=13` | 5, 6 | 25, 30 | 1/20 | DEAD |
| Wagner `= And(3)` | 2 | 12 | 1/24 = 0.0417 | DEAD |
| `And(4)`, `C11(1,3)` | 4 | 22 | 1/22 = 0.0455 | DEAD |
| `C13(1,5)` | 6 | 26 | 3/52 = 0.0577 | DEAD |
| `C7` | 1 | 7 | 1/28 = 0.0357 | not excluded (truth 1/49) |

On `C5` the floor is attained (`λ` uniform over the five rotation cuts gives `c_e = 1/5`, and
`max_x Σ x_i x_{i+1} = 1/4`), so `min_λ B(λ) = 1/20` exactly against the truth `1/25`: a 25 % gap,
**identical at every order along `C5[n]`**. This supersedes §3g of the Round-1 ledger, which tested
two particular `λ` and drew the conclusion from those two instances.

Consequence, stated as the campaign's working constraint: **a proof must read the weights.** The
conjecture is equivalent to the existence of an *algorithm* that maps a triangle-free `G` with
weights `x` to a bipartition with monochromatic weight `≤ (Σx)²/25`; no fixed distribution of cuts
can be that algorithm.

---

## R3-C2 — interior reduction (LEMMA, complete proof)

**Lemma.** For every `H`, `max_{x ∈ Δ} ψ(H,x) = max( max over v of max ψ(H − v), sup over interior
critical points of ψ )`, where "interior" means every coordinate strictly positive.

**Proof.** `Δ` is compact and `ψ` continuous, so the maximum is attained at some `x*`. If `x*` has a
zero coordinate `u`, then `ψ(H,x*) = ψ(H[supp x*], x*)` — a cut of `H` restricts to an arbitrary cut
of the induced subgraph and vertices off the support contribute nothing — so the value is at most
`max ψ(H − u)`. Otherwise `x*` is interior and the KKT conditions hold with equality in every
coordinate: there is a distribution `λ` on the **active** cuts (those attaining the minimum) with
`Σ_{v ∈ N(u)} c_uv x*_v = 2c` for **every** vertex `u`, where `c = ψ(H,x*)` and `c_uv = λ{S : uv
monochromatic}`. (Euler's identity for the quadratic `f = Σ λ_S q_S` fixes the multiplier: `x*·∇f =
2f = 2c` forces the common value `2c`.) ∎

Why it matters: it converts "certify `max ψ(H) ≤ 1/25`" from a global optimisation over the whole
simplex into (i) a recursion over induced subgraphs and (ii) a search for **interior** critical
points only, where the optimality conditions are *equalities in every coordinate* — a much smaller
and better-structured system. This is the concrete replacement for the branch-and-bound engine that
§3i of Round 1 recorded as failing.

Verified (`claude_gate_psi_structure.py`): `ψ(H,x) = ψ(H[supp x], x)` re-checked exactly on every
named pattern with `n ≤ 12`, 30 random rational supports each.

---

## R3-C3 — transfer concavity, and twin balancing (LEMMA, complete proof)

**Lemma (transfer concavity).** For every graph `H`, every `x`, and **every** pair `u ≠ v`, the map
`t ↦ ψ(H, x + t(e_u − e_v))` is concave.

**Proof.** For a cut `S`, `q_S(x + td) = q_S(x) + t·⟨∇q_S(x), d⟩ + t² q_S(d)` with `d = e_u − e_v`,
and `q_S(d) = Σ_{ab monochromatic} d_a d_b = −[uv monochromatic under S] ≤ 0`, because the only pair
with both coordinates nonzero is `(u,v)`. So every `q_S` is concave along the line, and a minimum of
concave functions is concave. ∎

Two consequences, both used below.

**(a) Support reduction is impossible.** In Motzkin–Straus one shifts weight between two
non-adjacent vertices because the objective is *affine* on that line, so an endpoint is at least as
good and the support shrinks. Here the objective is *concave* on every such line, so the optimum sits
in the interior of the segment. This is a structural explanation of why `C5`'s maximiser has full
support and why every naive "push weight to a smaller support" argument fails.

**(b) Twin balancing.** If `u,v` are twins (`N(u) = N(v)`, `u ≁ v`) then `ψ` is invariant under
exchanging the coordinates `x_u,x_v` (a cut separating them maps to another cut), and concave along
their transfer line; a concave function symmetric about the midpoint of a segment attains its maximum
there. Hence **some maximiser is constant on every twin class**, and therefore

```
        max_x ψ(H[a], x) = max_x ψ(H, x)   for every blow-up H[a] with all a_i ≥ 1.
```

So the ψ-ceiling only ever has to be checked on **twin-free** patterns. In this campaign that fact
was previously assumed ("573 reduced patterns"); it is now proved.

Verified (`claude_gate_psi_structure.py`): 508 exact midpoint-concavity checks over 12 named patterns
with random rational points and random pairs — 0 failures; 300 exact twin-balancing checks on `C5[2]`
and `C5[3]` — `ψ` never decreased; `ψ(C5[2], uniform) = 1/25` exactly.

---

## R3-C4 — exhaustive exact blow-up search: no pattern beats an induced C5

Engine `claude_blowup_zero.cpp` (mine; the Round-2 engine `round2/claude_blowup_sup.cpp` enumerated
only **strictly positive** weight vectors, which is the exact cause of the values retracted in
`round2/R2C2_PSI_PLATEAU_RETRACTION.md` — with zeros forbidden it could not even see the induced-`C5`
point). For each pattern it enumerates **all** `a ≥ 0` with `Σa = q` and computes
`bip(H[a]) = min over cuts of Σ_{mono} a_u a_v` in exact integers, with canonical-form pruning under
the rotation/reflection group for circulants.

Calibration: on `C5` the maximum of `25·bip(H[a])/q²` equals 1 exactly at `q = 5,10,15,…` and is
strictly below 1 at every other `q` — i.e. the engine reproduces `a(5n) = n²` and the strictness at
non-multiples.

| pattern | `n` | `q` range searched | max `bip(H[a])/q²` | attained at |
|---|---|---|---|---|
| Wagner `= And(3)` | 8 | 1..45 | **exactly 1/25** | `(0,0,0,t,t,t,t,t)` — an induced `C5` |
| Petersen | 10 | 1..45 | **exactly 1/25** | induced `C5` `{0,4,5,7,9}` |
| `And(4)` | 11 | 5..24 | **exactly 1/25** | induced `C5` |
| `And(5)` | 14 | 5..19 | **exactly 1/25** | induced `C5` |
| Grötzsch | 11 | 5..24 | **exactly 1/25** | induced `C5` |
| `C11(1,3)` | 11 | 5..24 | **exactly 1/25** | induced `C5` |
| `C13(1,5)` | 13 | 5..20 | **exactly 1/25** | induced `C5` |
| extremal `N=12` (both) | 12 | 5..20 | **exactly 1/25** | induced `C5` |
| extremal `N=13` | 13 | 5..20 | **exactly 1/25** | induced `C5` |
| extremal `N=14` | 14 | 5..19 | **exactly 1/25** | induced `C5` |

Zero violations. In every case the whole value sequence `q ↦ max_a bip(H[a])` is **identical** to the
`C5` sequence, and every maximiser is a concentration on an induced `C5`. Under GOAL rule (d) this is
a disproof probe, not progress; its content is that the sharpened disproof target of the plateau
retraction — beat an induced `C5` strictly — survives an exhaustive exact search of every weighting
of these twelve patterns on up to 45 vertices.

---

## R3-C5 — CORRECTION to an inherited literature claim (refuted by an explicit family)

Round-1 §3b states: *"the known theorem of Jin (triangle-free with min degree > 10N/29 admits a
homomorphism to C5)"*. **That form is false**, and it needs no reference to settle:

`And(k)` for `3 ≤ k ≤ 9` is triangle-free and vertex-transitive with
`δ/n = k/(3k−1) > 10/29`, yet is **not** homomorphic to `C5`, since a homomorphism cannot increase
the fractional chromatic number and `χ_f(And(k)) = n/α = (3k−1)/k > 5/2` for `k ≥ 3`.

Verified exactly (`claude_gate_andrasfai_facts.py`): brute-force independence number, brute-force
triangle count, and an exhaustive backtracking search for a homomorphism to `C5`:

| `k` | `n` | `δ` | `α` | `χ_f = n/α` | `δ/n` | `> 10/29` | `> 3/8` | `hom → C5` |
|---|---|---|---|---|---|---|---|---|
| 2 | 5 | 2 | 2 | 5/2 | 0.4000 | yes | yes | **yes** |
| 3 | 8 | 3 | 3 | 8/3 | 0.3750 | yes | no | no |
| 4 | 11 | 4 | 4 | 11/4 | 0.3636 | yes | no | no |
| 5 | 14 | 5 | 5 | 14/5 | 0.3571 | yes | no | no |
| 6..8 | 17,20,23 | 6,7,8 | 6,7,8 | 17/6, 20/7, 23/8 | 0.3529..0.3478 | yes | no | no |

The correct statements are: **Jin 1995 gives 3-colourability** at `δ > 10n/29`, and the
`C5`-homomorphism threshold is **Häggkvist's `δ > 3n/8`**, which is best possible exactly because
`And(3) = Wagner` sits at `δ/n = 3/8` and is not `C5`-colourable. The accepted base of the GOAL is
unaffected (it cites only Häggkvist), but the Round-1 commentary is corrected here, and every
Round-3 agent quoting Jin must use the 3-colourability form.

Also recorded: for every `k`, `N(v)` is a **maximum** independent set of `And(k)` (`|N(v)| = k = α`),
verified above — that is the defining property of the Andrásfai family and the reason it is the
extremal family for these thresholds.

---

## Standing consequence for the open band

The top of the band is Häggkvist's `δ > ⌊3N/8⌋`, tight at `And(3)`. The next structural theorem down
is Brandt–Thomassé (maximal triangle-free with `δ > N/3` is homomorphic to an Andrásfai or a Vega
graph). By R3-C3(b) the ψ-ceiling for those targets is a statement about twin-free patterns only, and
by R3-C2 it reduces to interior critical points. **Closing `max_x ψ(And(k),x) = 1/25` for all `k`
plus the Vega list would prove the conjecture unconditionally for every triangle-free graph with
`δ > N/3`** — an explicit min-degree range, which GOAL rule (c) admits as real progress. That is the
current primary target.

---

## R3-C6 — the independent-set covering family is DEAD (exact falsifiers, earliest at N=8)

Gate: `claude_gate_r3b.py` (mine; graphs constructed independently — Clebsch as the Cayley
graph on `(F_2)^4` with `S = {e1,e2,e3,e4,1111}`, `And(k)` as the circulant on `Z_{3k-1}`
with connection set `{i : i = 1 mod 3}`).

Every independent set `I` gives a bipartition `(I, V-I)`, so

```
        bip(G)  <=  e(G - I)     for every independent I,   hence  bip(G) <= M2(G) := min_I e(G - I).
```

`M2` is exactly tight on the extremal family, which is what made it look alive: `M2 = bip = n^2`
on `C5[n]` for `n = 1,2,3`. It nevertheless exceeds `N^2/25`, so it cannot prove the conjecture:

| `H` | `N` | `alpha` | `bip` | `M2` | `N^2/25` | verdict |
|---|---|---|---|---|---|---|
| `And(2) = C5` | 5 | 2 | 1 | 1 | 1 | tight |
| `C5[2]`, `C5[3]` | 10, 15 | 4, 6 | 4, 9 | 4, 9 | 4, 9 | tight |
| `And(3) = Wagner` | 8 | 3 | 2 | **3** | 64/25 = 2.56 | **BREAKS** |
| `And(4)` | 11 | 4 | 4 | **6** | 121/25 = 4.84 | **BREAKS** |
| `And(5)` | 14 | 5 | 6 | **10** | 196/25 = 7.84 | **BREAKS** |
| Clebsch (folded 5-cube) | 16 | 5 | 8 | **15** | 256/25 = 10.24 | **BREAKS**, worst ratio 15/256 = 0.0586 |

The earliest falsifier is **Wagner at `N = 8`**, and `bip <= M2` and `bip <= N^2/25` held in every
row, so the mechanism dies while the conjecture is untouched. Since `min_v e(G - N(v))`,
the BFS-layer bound and `|E| - (1/N) sum d(v)^2` are all `>= M2` on these graphs (`M1 = M3 = M2`
on every Andrasfai member, ratio `5/3` vs `bip`), the whole family — **delete an independent set,
a neighbourhood, or a BFS layer, then bound the rest** — is DEAD. This is the exact dual of
R3-C1: averaging certificates fail *on* `C5[n]`, covering certificates are tight on `C5[n]` and
fail *off* it. Note `Kneser(7,3)` and Hoffman-Singleton do NOT falsify it (`M2/N^2` = 0.0082 and
0.0280), so sparse witnesses are useless here; the falsifiers must be small and dense.

---

## R3-C7 — corpus contamination found and fixed: Kneser(7,2) is not triangle-free

Gate 2 of `claude_gate_r3b.py` audited all 3440 entries of `G10_named.txt` for triangles.
Exactly one is contaminated: **`Kneser72`, `N = 21`, `|E| = 105`, triangle `(0, 11, 18)`** — as it
must be, since `{1,2}, {3,4}, {5,6}` are pairwise disjoint 2-subsets of `[7]`, so `Kneser(7,2)`
contains a triangle. Root cause: `G10_corpus.py` filtered its *circulant* family through
`is_triangle_free` but applied no filter to the named/Kneser additions.

Fixed at the source: `named_graphs()` now returns `[g for g in out if is_triangle_free(g)]`, so the
corpus cannot be contaminated by a future addition. `G10_named.txt` regenerated; the diff against
the contaminated file is exactly the single deleted `Kneser72` line (3440 -> 3439 entries), and the
re-run audit reports 0 triangles. `Kneser(8,3)` is genuinely triangle-free (three pairwise-disjoint
3-sets need 9 > 8 points) and survives.

No accepted result depended on the bad entry: the only consumer was the corpus builder itself, and
`Kneser72` appears in no ledger table. Recorded because a triangle-free corpus that is not
triangle-free will silently manufacture a false counterexample, which under the GOAL is the one
outcome that must never be produced in error.

---

## R3-C8 — density-band theorem: GATED, with the posted band CORRECTED

Gate: `claude_gate_r3c.py` (mine). The G12 agent posted the chain plus the band
"`|E| >= N^2/5` or `|E| <= 2N^2/25`". The chain is right, the sparse endpoint is not.

**Theorem (gated).** For every triangle-free `G`,

```
        bip(G)  <=  min_v e(G - N(v))  <=  |E| - (1/N) sum_v d(v)^2  <=  |E| - 4|E|^2/N^2.
```

Proof: `N(v)` is independent, so `(N(v), V - N(v))` is a bipartition and
`bip(G) <= e(G - N(v)) = |E| - sum_{u in N(v)} d(u)`; averaging the subtracted term over `v`
replaces `max_v` by the mean `(1/N) sum_u d(u)^2`; Cauchy-Schwarz gives `sum d^2 >= 4|E|^2/N`.
Verified exactly on 23 graphs (odd cycles `C5..C25`, `And(2..7)`, `C5[1..4]`, Petersen,
Clebsch), 0 violations of the chain and 0 violations of the conjecture.

**Corollary (gated, exact).** With `x = |E|/N^2` the last bound is `N^2(x - 4x^2)`, so it
certifies `1/25` iff `4x^2 - x + 1/25 >= 0`. The discriminant `1 - 16/25 = 9/25` is a
rational square, so the roots are **exactly** `x = 1/20` and `x = 1/5`:

```
        bip(G) <= N^2/25   is PROVED UNCONDITIONALLY whenever   |E| <= N^2/20   or   |E| >= N^2/5.
        OPEN BAND:   N^2/20 < |E| < N^2/5.
```

**Correction.** The posted sparse endpoint `2N^2/25` is wrong: `2/25 = 0.08` lies strictly
inside the open interval `(1/20, 1/5) = (0.05, 0.2)`, and `x - 4x^2 = 34/625 = 0.0544 > 1/25`
there. Explicit falsifiers of the posted claim, all satisfying `|E| <= 2N^2/25`:

| `G` | `N` | `|E|` | `2N^2/25` | `|E| - 4|E|^2/N^2` | `N^2/25` |
|---|---|---|---|---|---|
| `C13` | 13 | 13 | 338/25 | **9** | 169/25 = 6.76 |
| `C15` | 15 | 15 | 18 | **11** | 9 |
| `C17` | 17 | 17 | 578/25 | **13** | 289/25 = 11.56 |
| `C19` | 19 | 19 | 722/25 | **15** | 361/25 = 14.44 |

The conjecture is untouched (`bip = 1` on every odd cycle); only the certificate fails there.

**Why the dense side is worth having.** `C5[n]` sits *exactly* on the upper endpoint:
`|E| = 5n^2` and `N^2/5 = 5n^2`, so `|E|/N^2 = 1/5` for every `n`, and the entire chain holds
with **equality** (`bip = M1 = M4 = |E| - 4|E|^2/N^2 = n^2 = N^2/25`, checked for `n <= 5`).
So the closed half `|E| >= N^2/5` is closed *including* the extremal family — this is not a
vacuous range, it is the range containing the sharp case.

**Consequence for the minimal-counterexample frontier.** Combining with base (6):
a minimal counterexample has `delta > (4N-2)/25 > 0.16N`, hence `|E| >= delta N/2 > 0.08N^2`,
so the sparse branch can never apply to it, and by the dense branch it must satisfy
`|E| < N^2/5`. Writing `dbar = 2|E|/N` for the average degree,

```
        a minimal counterexample satisfies    0.16 N  <  delta  <=  dbar  <  0.4 N.
```

The upper constraint is now on the **average** degree, not the minimum degree, which is
strictly stronger information than the Haggkvist end of base (6) gave.

---

## PROVENANCE NOTE (root agent, 2026-07-25)

Sections R3-C6, R3-C7 and R3-C8 above were appended to this file by Round-3 agents, not by me;
their "(mine)" refers to the writing agent. I have re-derived all three independently
(`claude_gate_r3_c9c10.py`, own graph constructions, own exhaustive maximum cut, exact integers):

* **R3-C6 confirmed.** `M2 = min over independent I of e(G−I)` equals `bip` on `C5[n]` (n ≤ 3) but
  gives `3 > 64/25` on Wagner, `6 > 121/25` on `And(4)`, `10 > 196/25` on `And(5)`, `15 > 256/25` on
  Clebsch. By hand at the earliest falsifier: `α(Wagner) = 3`, every independent 3-set is a
  neighbourhood, so `M2 = 12 − 3·3 = 3`.
* **R3-C7 confirmed** (trivially: `{1,2},{3,4},{5,6}` are pairwise disjoint, so `Kneser(7,2)` has a
  triangle).
* **R3-C8 confirmed**, including the correction of the posted sparse endpoint: the whole chain
  `bip ≤ min_v e(G−N(v)) ≤ |E| − (1/N)Σd(v)² ≤ |E| − 4|E|²/N²` was re-verified on 11 graphs, the
  roots of `4x² − x + 1/25` are exactly `1/20` and `1/5`, and at the posted endpoint `x = 2/25` the
  bound is `34/625 = 0.0544 > 1/25`, with `C13, C15, C19` as explicit witnesses.

I had derived the same chain independently before reading the section (it is the "neighbourhood-cut"
bound: `ψ ≤ E[D]/2 − E[D²] ≤ m/2 − m²`, maximised at `1/16`), which is why it is accepted here
rather than merely recorded. Labels R3-C9 and R3-C10 below are mine and do not collide.

---

## R3-C9 — every C5-plateau point is a first-order local maximum, in EVERY triangle-free H

**Theorem.** Let `H` be triangle-free, `T = {t_0,…,t_4}` an induced `C5` of `H`, and `x⁰` the point
carrying weight `1/5` on each `t_i` and `0` elsewhere (so `ψ(H,x⁰) = 1/25`). Then for **every**
feasible direction `d` (`Σd = 0`, `d_u ≥ 0` off `T`) the one-sided derivative of `ψ` at `x⁰` along
`d` is `≤ 0`.

**Proof.** The cuts active at `x⁰` are exactly the extensions of the five rotation cuts
`S_i = {t_i, t_{i+2}}` of `T`, the vertices off `T` placed arbitrarily; each has value
`x⁰_{t_i}x⁰_{t_{i+1}} = 1/25`, while any other cut restricts to a cut of `T` with at least two
monochromatic `C5`-edges, hence value `≥ 2/25`. For a minimum of smooth functions the one-sided
derivative is the minimum of the derivatives over the active set, and
`∂q_S/∂x_u(x⁰) = (1/5)·|N(u) ∩ T ∩ side_S(u)|`. Off `T` we have `d_u ≥ 0`, and the contributions of
distinct outside vertices are independent (edges between them carry weight `0` at `x⁰`), so the
minimising active cut places each outside vertex on its lighter side. Hence

```
   D(d) = min over i of [ (1/5)(d_{t_i} + d_{t_{i+1}}) + (1/5) Σ_{u ∉ T} d_u · sep_i(u) ],
   sep_i(u) = min over the two sides of |N(u) ∩ T ∩ side| .
```

**Triangle-freeness enters here and only here:** `N(u)` is independent and `α(C5) = 2`, so
`|N(u) ∩ T| ≤ 2`, giving `sep_i(u) ∈ {0,1}`, equal to `1` exactly when `N(u) ∩ T` is one of the five
non-adjacent pairs and `S_i` separates it. Each non-adjacent pair is separated by exactly **two** of
the five rotation cuts, and each vertex of `T` lies in exactly **two** of the five monochromatic
edges (both verified exhaustively in `claude_gate_c5local.py`), so

```
   Σ_i bracket_i = (2/5)·( Σ_{t∈T} d_t + Σ_{u ∉ T, |N(u)∩T| = 2} d_u )  ≤  (2/5)·Σ_v d_v  =  0,
```

using `d_u ≥ 0` off `T`. Five numbers with non-positive sum have a non-positive minimum. ∎

**Consequence.** No local perturbation of a `C5`-concentration beats `1/25`, in any triangle-free
graph whatsoever. A counterexample cannot be produced by improving a plateau point: it must sit far
from every induced-`C5` concentration, or escape along a direction where the derivative is exactly
zero.

**The flat directions, and an exact probe along them.** `D(d) = 0` forces `bracket_i = 0` for all
`i`, i.e. `r_{i+3} + r_{i+4} = p_{t_i} + p_{t_{i+1}}`, where `p` is the distribution of removed mass
on `T` and `r_a` the mass added to outside vertices attached to the pair `P_a`. `I + P` is invertible
on `Z_5`, so each `p` has exactly one `r`; for uniform `p` the solution is uniform `r`, realisable
exactly when all five pair-classes are occupied — the Mycielski configuration `C5 + {u_0..u_4}` with
`N(u_a) ∩ T = P_a`. Along that entire flat line `ψ` was maximised **exactly** (every one of the `2^n`
cut polynomials in the parameter `δ`, all stationary points and all pairwise crossings, sympy exact
arithmetic):

| graph | pair-vertices | distinct cut polynomials | exact max along the flat line |
|---|---|---|---|
| `μ(C5) − apex` (10 vtx) | 5 | 14 | **1/25, at δ = 0** |
| Grötzsch | 5 | 14 | **1/25, at δ = 0** |
| `And(4)` | 4 | 24 | **1/25, at δ = 0** |
| `C11(1,3)` | 4 | 41 | **1/25, at δ = 0** |
| Wagner, `C13(1,5)` | 2 | 13 | **1/25, at δ = 0** |

plus 300 random feasible directions × 5 exact step sizes on each of eight patterns, largest value
seen `998001/25000000 = 0.039920 < 1/25`.

---

## R3-C10 — the general concavity lemma (LEMMA, complete proof)

**Lemma.** `ψ(H,·)` is concave along every direction `d` whose positive support `{u : d_u > 0}` and
negative support `{u : d_u < 0}` are **each independent sets** of `H`.

**Proof.** `q_S(x + td) = q_S(x) + t⟨∇q_S(x),d⟩ + t²q_S(d)` and
`q_S(d) = Σ_{ab monochromatic} d_a d_b`. Any edge `ab` with `d_a, d_b ≠ 0` joins the positive support
to the negative support, since each is independent, so `d_a d_b < 0`; every other term vanishes.
Hence `q_S(d) ≤ 0` for every cut, each `q_S` is concave along `d`, and so is their minimum. ∎

Corollaries:

* **Transfer concavity** (R3-C3) is the case of two singleton supports; **twin balancing** follows.
* `ψ` **is concave in the coordinates of any independent set** with the rest of `x` fixed — and since
  `H` is triangle-free, in the coordinates of **every neighbourhood** `N(v)`.
* Therefore block ascent over independent sets has no spurious local optima *inside* a block. That is
  the correct architecture for a `max_x ψ` optimiser — alternate exact concave maximisations over
  independent blocks (colour classes, or neighbourhoods) — and it replaces the naive hill-climbing
  whose output had to be retracted in Round 2.
* Averaging `x` over the orbit of an automorphism that moves only an independent set never decreases
  `ψ`.

Verified (`claude_gate_indep_concavity.py`): 1590 exact midpoint-concavity checks, random rational
points and random independent-support directions over 7 patterns, 0 failures. The control direction
tried (positive support an edge of `C5`) happened to remain concave, so the experiment confirms the
hypothesis is *sufficient* and says nothing about necessity.


---

## R3-C13 — the low-degree constant 4/25 is EXACTLY optimal for the deletion mechanism (GATED)

Round-3 family G9 produced this; I re-derived and re-verified it independently
(`claude_gate_r3_c9c10.py` companion run, blow-up identity plus a from-scratch enumeration of all
`2^24` cuts of the explicit 25-vertex graph).

**Witness family.** `W_t := C5[7t, 2t, 7t, 7t, 2t]` (parts around the 5-cycle).

| `t` | `N` | `bip` | `δ` | drop at a minimum-degree vertex | budget `(2N−1)/25` | step fails |
|---|---|---|---|---|---|---|
| 1 | 25 | 14 | 4 = `4N/25` | 2 | 49/25 = 1.96 | **yes** |
| 2 | 50 | 56 | 8 = `4N/25` | 4 | 99/25 = 3.96 | **yes** |
| 3 | 75 | 126 | 12 = `4N/25` | 6 | 149/25 = 5.96 | **yes** |

`bip(W_t) = min_i a_i a_{i+1} = 14t²` (products `14, 14, 49, 14, 14` in units of `t²`), and the
independent brute force at `t = 1` gives `bip = 14` and `bip(W_1 − v) = 12` for `v` in the
minimum-degree part, matching the identity exactly. `W_t` is maximal triangle-free (any `C5`
blow-up with all parts nonempty is), so the WLOG of accepted fact 5 does not escape it.

**Consequence.** Every vertex of `W_t` has degree exactly `4N/25`, and at every one of them the
one-vertex deletion step misses its budget by exactly `1/25`. Therefore the constant `4/25` in
`δ > (4N−2)/25` **cannot be raised by the deletion mechanism** — not by single vertices, not by
independent sets, not by arbitrary sets with greedy re-insertion, since all of those are dominated
by the per-vertex accounting that `W_t` saturates. The conjecture itself is untouched:
`bip(W_t) = 0.0224 N² < N²/25`.

**Strategic consequence, recorded because it redirects the campaign.** The *lower* end of the open
band `0.16N < δ ≤ 0.375N` is a hard barrier for every deletion-style argument. The band can only be
attacked from the *upper* end — which is exactly where the arc-cut mechanism (R3-C11) and the
Brandt–Thomassé structure theory operate.


---

## R3-C14 — the first x-DEPENDENT certificate, exact and root-gated (accepted)

Round-4 family H5 produced an exact rational Positivstellensatz certificate for `C5`; I verified it
with my own implementation (`round5/claude_gate_sos_cert.py`: polynomials as dicts
`{exponent -> Fraction}` expanded by hand, positive semidefiniteness by my own rational LDL^T with
symmetric pivoting, no sympy, no code shared with the constructor or with the agent's own verifier).

**The certificate.** Quadratic forms `λ_e(z)`, one per edge of `C5`, with

```
   (1)  Σ_e λ_e(z) = (Σ_j z_j)²                                    [verified: every entry of Σ_e L_e is 1]
   (2)  every λ_e has nonnegative coefficients                     [verified]
   (3)  eleven Gram blocks, sizes 15 and 5, all symmetric PSD      [verified, own rational LDL^T]
   (4)  (Σ_j y_j²)⁴ − 25 Σ_{e=(u,v)} λ_e(y²) y_u² y_v²  =  Σ_b Σ_{i,j} G_b[i,j] y^{m_i} y^{m_j}
                                                                   [verified: exact, zero residual]
```

Substituting `x_j = y_j² ≥ 0` with `Σx = 1`: by (1) and (2) the numbers `λ_e(x)` form a probability
distribution **over the edges, depending on `x`**, and (3)+(4) give
`Σ_e λ_e(x)·x_u x_v ≤ 1/25`, hence `min_e x_u x_v ≤ 1/25`, which for `C5` is exactly
`ψ(C5,x) ≤ 1/25`. Sharpness re-checked: uniform `x` gives exactly `1/25`.

**Why this is a methodological unlock, not just a new proof of a known case.** R3-C1 proves that no
`x`-*independent* distribution over cuts can certify `1/25` — the floor is `1/20` on every `C5[n]`.
This certificate is the first object in the campaign of the required shape: the multiplier is a
*quadratic form in `x`*, so the distribution over cuts genuinely reads the weights. The construction
(Lasserre level 3 in epigraph form, dual rounded to rationals, exactly repaired) is not `C5`-specific
and is the concrete route to rigorous ψ-ceilings for the Andrásfai family, i.e. to the `δ > N/3`
range. The corresponding certificate for `And(3) = Wagner` is the next object to produce; it did not
exist at the time of this entry.
