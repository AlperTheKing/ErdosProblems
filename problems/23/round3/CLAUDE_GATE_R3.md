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


---

## R3-C15 — the Vega side, gated (accepted, with one agent claim refuted)

Round-6 family P3 built the Vega graphs and ran an exhaustive weighting search; its own auditor
refuted one headline claim. I rebuilt `Υ_2` myself from the Brandt–Thomassé definition quoted
verbatim from the paper (`Γ_i` on `{1..3i−1}` with `j ~ j+i,…,j+2i−1`; add the edge `xy` and the
induced 6-cycle `(a,v,c,u,b,w)`; `x ~ a,b,c`, `y ~ u,v,w`; `N(a),N(u) ⊇ {1..i}`, `N(b),N(v) ⊇
{i+1..2i}`, `N(c),N(w) ⊇ {2i+1..3i−1}`).

**Verified by me, exact integers.** `Υ_2`: `n = 13` (matching `3i+7`), 28 edges, **triangle-free**,
**maximal** triangle-free, degrees 4–5. Exhaustive over **all** integer weightings `a ≥ 0` with
`Σa = q` for `q = 5..12`, zeros allowed: `max 25·bip(Υ_2[a])/q² = 1.0` exactly — the ceiling `1/25`
is attained (the plateau, since `Υ_2` has odd girth 5) and **never exceeded**. `Υ_3` rebuilt and
verified triangle-free and maximal at `n = 16`.

**Accepted from the round-6 pair (report + audit).**

* all 28 Vega graphs for `i = 2..8` constructed and matched byte-for-byte by the auditor;
* no violation of `ψ ≤ 1/25` anywhere in the exhaustive search, with a strengthened equality census;
* **the `m(b)` / `bound_k` machinery fails on the Vega side too** — an exact witness, independent of
  the `Γ_14` Wagner falsifier that killed it on the circle side. Two independent refutations of the
  same machinery.

**Refuted (agent claim).** "The maximum over the whole Vega family is `29/841`, attained at the
regular weight function, so the Vega side carries a uniform 13.8 % margin and is not the hard case."
The auditor exhibits 11 exactly-verified points inside the degree polytope that exceed it, the best
being `4898341/139240000 = 0.0351791` on `Υ_3 − {2i}`. So the Vega side sits at least at `0.0352`,
still below `1/25` but with far less margin than claimed, and it cannot be dismissed as easy.

**Status of the `δ > N/3` reduction.** Both halves — the Andrásfai ceiling and the Vega ceiling —
remain unproved. What is now known is that they resist the *same* machinery, and that the Vega half
is not the soft one.


---

## R3-C16 — discharging/switching schemes cannot reach 1/25: a sharper obstruction on the extremal family itself (GATED)

Round-7 family Q2 produced this; its own auditor corrected the statement, and I verified the witness
independently.

**Witness.** `G = C5[7,7,12,7,12]`, the blow-up of `C5` with those class sizes. Verified by me:
`N = 45`, `|E| = 385`, `bip(G) = min_i a_i a_{i+1} = 49 ≤ 81 = N²/25` — **the conjecture holds
comfortably**. Now take the class-constant cut with classes `{c0, c2}` on one side:

```
        |M| = a_3 a_4 = 7·12 = 84 ,      25|M| = 2100  >  2025 = N² .
```

At that cut every vertex satisfies `σ(v) ≥ 0` (per class: `19, 19, 14, 0, 0`), and the **smallest
switching set with `σ(S) < 0` has size 11 = 0.2444·N** (namely one vertex of `c0` and ten of `c4`).

**Consequence.** Any discharging or switching scheme whose cut hypotheses are the inequalities
`σ(S) ≥ 0` for sets of size below `0.2444 N` — which includes the vertex case, the whole switch-star
family (sets `{v} ∪ T` with `T ⊆ N_B(v)`), and every bounded-radius local rule — is **satisfied by a
cut carrying `25|M| > N²`**. Such a scheme therefore cannot prove `25|M| ≤ N²`; the best it can
reach is `|M| ≤ N²/24.1`.

This strengthens the recorded `P4`-blow-up obstruction (threshold `0.27N`, `bip = 0`) in the way that
matters: the new witness is **a `C5` blow-up**, i.e. it lives inside the extremal family itself, so
no argument that "the extremal structure is a `C5` blow-up" can dodge it, and the threshold drops to
`0.244N`. Adding a global term to the scheme does not help unless that term separates this cut from
a maximum cut of the same graph.

**Also gated from the same round (Q1):** the "union of neighbourhoods" cut family — the natural
closure of the neighbourhood cuts — also fails. On the Grötzsch graph it returns `5` against
`bip = 4`, and `25·5 = 125 > 121 = N²`. A smaller and sharper witness for the plain neighbourhood
family: `C6`, where `bip = 0` but `min_v e(C6 − N(v)) = 2` and `25·2 = 50 > 36 = N²`.


---

## R3-C17 — MILESTONE: `max_x ψ(And(3)) = 1/25` is PROVED (the Wagner case is closed)

Root-agent entry, 2026-07-26. The Wagner graph `V8 = C8(1,4) = And(3) = Γ_8` has been this
campaign's recurring hard case since Round 1: the tightest open pattern in Round 2, the graph whose
far-regular configuration killed my moment criterion in Round 5 (R5-K22), and the first Andrásfai
graph that is **not** `C5`-colourable. Its ceiling is now proved, by two independent routes, and I
verified the decisive one myself.

### The route (Round 7 family Q5), and my verification of it

```
   Guenin / Barahona:  for a signed graph with no odd-K5 minor, the odd-cycle covering LP is
                       integral, i.e.  psi(G,x) = Lambda(G,x)  for every weighting x
   Thm A            :  Lambda(G,x) <= 1/25 for every triangle-free G and every x
   ==>  THEOREM C   :  G triangle-free with no odd-K5 minor  ==>  psi(G,x) <= 1/25 for every x.
```

`V8` is cubic on 8 vertices and is **K5-minor-free** — Wagner's own classical theorem — so Theorem C
applies, and the plateau gives the matching lower bound:

```
        max_x ψ(And(3), x)  =  1/25   exactly.
```

**Verified by me, independently** (`claude_gate_wagner_cert.py` companion run):

* `V8` rebuilt from the circle definition (`3·circdist > 8`): 8 vertices, 12 edges, 3-regular;
* **exhaustive** search over every assignment of the 8 vertices to 5 branch sets plus "unused",
  with connectivity and all-pairs-adjacency checks: **no K5 minor exists** in `V8`;
* the covering LP is integral here: over 25 random exact weightings, `ψ` (minimum over all 128 cuts,
  exact rationals) equals `Λ` (the LP over all 16 odd cycles) in **25 of 25** cases;
* the fractional bound holds where it must: `max Λ` over uniform + 40 random weightings is
  `0.04000000` on `C5` (tight), `0.0204` on `C7`, `0.03125` on `V8`, `0.0331` on `And(4)`, `0.0300`
  on Petersen, `0.0331` on Grötzsch — never above `1/25`.

### What the class contains, and exactly where it stops

* **the extremal family**: `C5[2]` has a `K5` minor but no **odd** `K5` minor (exhaustive search), so
  the theorem covers `C5` blow-ups — it does not dodge the sharp case;
* all planar triangle-free graphs (planar ⟹ no `K5` minor);
* `And(3) = V8`;
* **it stops at `And(4)`**: `Γ_11` carries an explicit odd-`K5` minor with branch sets
  `{0,4,8}, {1,5,9}, {2,6,10}, {3}, {7}`, and `And(4)` is an induced subgraph of `And(k)` for
  `k = 5..8`, so the certificate is provably unavailable from `And(4)` on.

### Independent second proof

Round 7 family Q4 produced an exact rational Positivstellensatz certificate for the same statement —
29 inclusion-minimal cuts, 284 nonnegative degree-2 multiplier coefficients, `Σ_S ν_S = 25 L²`, 99
PSD Gram blocks, zero residual in the polynomial identity — which its auditor verified in full. Note
this also **corrects my own Round-5 conclusion** that degree-2 multipliers are infeasible for Wagner:
they are feasible, and my infeasibility finding was an artefact of restricting the cut family to
arcs. Only 12 of the 29 cuts used are arcs.

### Consequence for the programme

The `δ > N/3` route needs `max_x ψ = 1/25` on every Andrásfai graph and every Vega graph. That is now
**proved for `And(2) = C5` and `And(3) = Wagner`**, and provably out of reach of this particular
mechanism from `And(4)` on. The open part of the Andrásfai side is exactly `And(k)`, `k ≥ 4`.


---

## R3-C18 — the integrality route, and where it now points

Following R3-C17, the Wagner ceiling came from `ψ = Λ` (integrality of the odd-cycle covering LP,
via Guenin/Barahona for odd-`K5`-minor-free signed graphs) plus the fractional bound `Λ ≤ 1/25`.
`And(4) = Γ_11` carries an explicit odd-`K5` minor, so Guenin does **not** apply to it. I tested
whether integrality nevertheless holds.

**Finding (exact, my own computation).** On `And(4)` the covering LP is integral at every weighting
tested — certified the strong way, by exhibiting a fractional odd-cycle **packing** whose value
equals `ψ` (LP duality then forces `packing ≤ Λ ≤ ψ = packing`):

| weighting on `And(4)` | `ψ` (exact, min over all 1024 cuts) | max packing | equal |
|---|---|---|---|
| uniform | `4/121 = 0.03305785` | `0.03305785` | yes |
| a `C5`-concentration | `1/25 = 0.04000000` | `0.04000000` | yes |
| random | `13/500` | `0.02600000` | yes |
| random | `9/968` | `0.00929752` | yes |

and over 30 random weightings each, `ψ = Λ` held in `30/30` cases on `And(3)`, `And(4)`, `And(5)`
and `Γ_10`. So **Guenin's hypothesis is sufficient but not necessary here**: integrality survives
past the odd-`K5` obstruction on this family.

**Why it matters.** If `ψ(And(k), x) = Λ(And(k), x)` for every `k` and every `x`, then with the
fractional bound `Λ ≤ 1/25` one gets `max_x ψ(And(k), x) = 1/25` for **all** `k` — which is the
entire Andrásfai side of the `δ > N/3` reduction, the half that R3-C17 could only reach for
`k = 2, 3`.

**Status.** This is a route, not a theorem: the integrality statement for `And(k)` is unproved, and
under GOAL rule (e) a reduction does not count until it is proved. What has changed is that the
target is now a *classical, well-studied* property (min-max for odd-cycle covering/packing) on a
*highly structured* family (`And(k)` is the circular clique `K_{(3k−1)/k}`), rather than an ad-hoc
inequality of my own devising — and unlike every certificate family tried so far, it is not
contradicted by the far-regular Wagner configuration, because it is exactly what proves that case.


---

## R3-C20 — round 8 stability family: a proved local-exactness ball, and spurious local maxima (GATED)

Root-agent entry, 2026-07-26. Re-verified with my own implementation
(`round5/claude_gate_r8_stability.py`); nothing imported from the family's code.

### Accepted

**Theorem B.** For the complete blow-up `B = C5[V_1..V_5]` and any `x` on the simplex with class
sums `y_i = x(V_i)`, `psi(B,x) = min_i y_i y_{i+1}` exactly, hence `psi(H,x) <= 1/25` for every
`H` subgraph of `B`. Gated on 36 exact weightings including unbalanced blow-ups and one with a
ZERO part: 0 mismatches. (The `rho = 0` case of Theorem D below is exactly this C5-colourable
case, since in a triangle-free graph two full twins of the same class cannot be adjacent.)

**Theorem D — the first quantitative positive result of the campaign in this direction.**
`H` triangle-free, `C` an induced `C5`, `T_i` the full twins of class `i`
(`N(v) ∩ C = {c_{i-1}, c_{i+1}}`), `R` everything else off `C`, `eta = x(V\C)`, `rho = x(R)`:

```
        psi(H,x)  <=  (1-rho)^2/25 + rho*eta
        ==>  psi(H,x) <= 1/25   whenever  25*eta <= 2 - rho,   in particular whenever eta <= 1/13.
```

Gated on 1032 exact rational instances over C5, Petersen, Grotzsch, Wagner, Gamma_11, C5[2] and
C5[3,1,2,2,1], every induced C5 of each: **0 violations of the inequality and 0 violations of the
corollary**. This proves the conjecture in an explicit ball around every C5-concentration.

### Accepted, and it constrains my own methodology

**K-0: `psi` has SPURIOUS LOCAL MAXIMA.** On Petersen, 30 of the 840 arrangements of the multiset
`(1/8 x6, 1/4, 0 x3)` give `psi = 1/32` exactly. For one such `x` the support is
`{1,2,3,4,6,8,9}`, inducing a 7-vertex 8-edge graph with degree sequence `[2,2,2,2,2,3,3]` =
`Theta(2,3,3)`, whose two C5s share the length-2 path. There are 88 active cuts, the first-order
ascent LP returns `t* = 0` (no ascent direction), and 3000 exact rational perturbations produce
**0** improvements.

Consequence I must apply to my own record: **every multistart-optimiser sweep in this campaign is
evidence, not proof.** The n <= 15 exhaustive pattern sweeps and the randomised n = 16..20 hunt
report `max_x psi = 1/25`; those runs always start from C5-concentrations, so the reported values
are valid LOWER bounds, but a local maximum ABOVE 1/25 unreachable from the seeded starts is not
excluded by them. This does not retract any accepted result, since no ceiling was ever accepted on
optimiser output alone -- the proved ceilings (C5, Wagner, Petersen, C5-colourable, odd-K5-minor-free)
all rest on exact certificates.

### Open, stated honestly by the family

`STAB(eps,delta) ∧ LOC(delta) ==> conjecture` is a legal split (neither conjunct alone has strength
>= the conjecture). `LOC` is now partly proved (Theorem D); **`STAB` is completely open and this
round produced no partial result on it.** Blocking step, verbatim: Theorem D's proof uses
`|N(v) ∩ C| <= 1` for `v` in `R`, which has no analogue at a blow-up point with large classes,
where placing an R-vertex costs `Theta(rho/5)` against a `2*rho/25` budget. K-0 additionally forces
`eps < 7/800` in any `STAB(eps,delta)` with `delta < 3/5`. Nothing here improves the published
`n^2/23.5`.


---

## R3-C21 — round 8 entropy/counting family: the obstruction widened to Gibbs, and a divisibility proof (GATED)

Root-agent entry, 2026-07-26. Own implementation, `round5/claude_gate_r8_entropy.py`.

### Accepted: Theorem R8-2 widens the obstruction I recorded in A21

Every aggregator `Phi` with `min <= Phi`, `Phi(c,...,c) = c`, strictly increasing -- all power means
AND the Gibbs / free-energy aggregator `Phi_beta(t) = -(1/beta) log E_nu[e^{-beta t}]` for every
`beta > 0` -- applied to a FIXED cut distribution must be supported on RAINBOW-1 cuts, i.e. cuts
leaving exactly one monochromatic edge inside every induced pentagon. The exponential-moment
upgrade is the sharpest form entropy takes on this problem, and it buys nothing.

Two independent round-8 families (transport, entropy) reached this obstruction by different routes
and converged on the SAME Grotzsch witness, `a = (0,0,0,0,0,1,1,1,1,1,5)` i.e.
`x = (0^5, (1/10)^5, 1/2)`, giving `1/20 > 1/25` while `psi = 0`. I had already gated that witness.

### Accepted: Lemma R8-3, a counting proof of the And(4) kill

Double counting the pairs `(e,K)` with `e` in a rainbow-1 set `F` and `K` an induced pentagon
through `e`:

```
        sum_{e in F} p(e)  =  sum_K |F cap E(K)|  =  P.
```

In `Gamma_11` every edge lies in 5 or 10 induced pentagons and `P = 33`; since `5 | p(e)` for every
edge but `5` does not divide `33`, NO rainbow-1 set exists. This replaces an exhaustive search by
arithmetic. It cross-checks exactly against my own earlier gate: 33 induced pentagons, and 0
rainbow-1 cuts among all 1024 by brute force.

**Scope, stated precisely because the summary could be read too broadly.** The divisibility
obstruction fires ONLY at And(4) in my suite:

```
        C5           P = 1    p(e) = {1}
        Wagner       P = 8    p(e) = {2,4}
        Petersen     P = 12   p(e) = {4}
        Grotzsch     P = 31   p(e) = {7,8,9}
        And(4)       P = 33   p(e) = {5,10}     <-- all divisible by 5, 5 does not divide 33: KILL
        And(5)       P = 98   p(e) = {8,11,20}
        N=14 extremal P = 92  p(e) = {6,13,14,15,16,17}
```

so the kills recorded for And(5), And(6) and `M?AE@bH{AYN_LgBs?` rest on exhaustive enumeration, not
on this lemma. It is a sharp tool, not a general theorem.

### Accepted: PRGM is dead (A25)

The `x`-adapted `Z5`-rotation geometric-mean certificate chooses its cut FROM the weights, so it
escapes the fixed-family obstruction. It still fails. At uniform weights on Wagner, over ALL `5^7`
maps `phi: V -> Z5`, `min_phi prod_r m_r = 162`, and `5^10 * 162 = 1582031250 > 1073741824 = 8^10`.
Valid but exactly tight on C5 (`prod = 1`, `5^10 = 5^10`), valid on Petersen (`972`, `9492187500 <
10^10`). No reweighting repairs it: with class loads `c_i = w_i + w_{i+1}`,
`max_X prod X_i^{c_i} = exp(-2H(c/2))`, so the bound is exactly `H(c/2) >= log 5`, which forces
`c/2` uniform and hence `w = 1/5` uniform.

### Accepted: the recurring 1/20 barrier, explained

Motzkin-Straus caps the edge weight of a triangle-free graph at `1/4`; a balanced 5-fold split gives
`(1/4)/5 = 1/20`. That single fact unifies the value A6 attains on every `C5[n]`, the value in
round1/f3 section 5, and the Grotzsch and Clebsch star witnesses. A geometric mean escapes it only
when some class receives weight 0, which a degree-5 star spread over all five classes prevents.

### Consequence for the programme

Any proof must select its cut as a function of the weights AND be exactly optimal at every
induced-pentagon weighting simultaneously. No fixed cut family can do this, and the one `x`-adapted
family tried (the `Z5` rotations) does not either.


---

## R3-C22 — MILESTONE: Theorem A is PROVED, and the proof is elementary (GATED)

Root-agent entry, 2026-07-26. Round 8's adversarial audit was asked to BREAK
`Lambda(G,x) <= 1/25`; it returned a proof instead. I gated the proof itself, not just its
conclusion (`round5/claude_gate_r8_thmA.py`). This matters because Theorem A is consumed by R3-C17
(the Wagner ceiling) and by the Petersen ceiling, and had never been verified by me.

### Statement

For every triangle-free `G` and every `x >= 0` with `sum_v x_v = 1`, the fractional odd-cycle
covering LP with edge weights `w_uv = x_u x_v` satisfies `Lambda(G,x) <= 1/25`.

### Proof, in full

Write `d(v) = sum_{u in N(v)} x_u`. Restrict to `supp(x)`: edges leaving it have weight `0`, so
`y_e = 1` there is free and covers every odd cycle meeting the complement; vertices isolated in the
restriction lie on no cycle and are dropped. So assume `x_v > 0` and `d(v) > 0` throughout.

**Lemma 1.** If `g >= 0` satisfies `sum_{v in C} g(v) >= gamma` for every odd cycle `C`, then
`Lambda(G,x) <= (1/(2 gamma)) * sum_v g(v) x_v d(v)`.
*Proof.* Put `y_e := (g(u)+g(v))/(2 gamma)` for `e = uv`. Every vertex of a cycle meets exactly two
of its edges, so `sum_{e in C} y_e = (2/(2 gamma)) sum_{v in C} g(v) >= 1`: feasible. Its cost is
`sum_{uv in E} x_u x_v (g(u)+g(v)) / (2 gamma) = (1/(2 gamma)) sum_v g(v) x_v d(v)`. QED

**Lemma 2 (the only place triangle-freeness is used).** For an odd cycle `C` of length `L` in a
triangle-free graph, `sum_{v in C} d(v) <= (L-1)/2`.
*Proof.* `N(u)` is independent, so `N(u) cap V(C)` is an independent set of the cycle `C_L` and has
size at most `floor(L/2) = (L-1)/2`. Double count:
`sum_{v in C} d(v) = sum_u x_u |N(u) cap V(C)| <= ((L-1)/2) sum_u x_u = (L-1)/2`. QED

**Theorem A.** Take `g = 1/d` and `gamma = min_C sum_{v in C} 1/d(v)`. By Cauchy-Schwarz,
`sum_{v in C} 1/d(v) >= L^2 / sum_{v in C} d(v)`, and with Lemma 2 this is `>= 2L^2/(L-1) >= 25/2`
for odd `L >= 5`, the expression being increasing in `L`. Lemma 1 then gives
`Lambda <= (1/(2 gamma)) sum_v x_v = 1/(2 gamma) <= 1/25`. QED

Sharper forms it yields for free: `Lambda <= 1/(2 gamma)` instance-wise, and
`Lambda <= (g-1)/(4 g^2)` for odd girth `g`, so odd girth `>= 7` gives `<= 3/98`.

### My gate

* arithmetic chain: `2L^2/(L-1)` equals `25/2` exactly at `L = 5` and strictly increases; checked for
  all odd `5 <= L <= 31`;
* Lemma 2's combinatorial core over C5, C7, Wagner, Petersen, Grotzsch, Gamma_11 and every odd cycle:
  **8622 `(u,C)` pairs, 0 violations, 2878 tight**. Control: `K4`, which has triangles, violates it
  **16** times, so triangle-freeness is exactly and only what the lemma consumes;
* the constructed cover end to end in exact rationals over 36 weightings: **0 infeasible, 0 cost
  mismatches against `1/(2 gamma)`**, maximum cost `585/14896 = 0.039272 <= 1/25`;
* the auditor's independent exhaustive search: all triangle-free graphs up to isomorphism for
  `n <= 11` (counts matching A006785), `max_x Lambda` exactly `1/25` on every maximal non-bipartite
  one, never above.

### Two consequences that constrain every consumer

1. **Theorem A is tight on a PLATEAU, not at an isolated extremum.** For every triangle-free `G`
   containing a 5-cycle, weight `1/5` on that pentagon gives `Lambda = 1/25` exactly. So any step
   needing `Lambda < 1/25` is unavailable, and any purported proof of Theorem A with slack anywhere
   is wrong.
2. **Theorem A does NOT imply the conjecture**, and the gap is exactly the odd-`K5` obstruction.
   Witness, verified here: `K5` with every edge subdivided twice (`n = 25`, `m = 30`, triangle-free,
   odd girth 9). Odd cycles correspond to odd cycles of `K5`, so `psi = bip(K5)/625 = 4/625` while
   the uniform `y = 1/9` gives `Lambda <= 30/(9*625) = 2/375`: ratio exactly `6/5`. (No
   counterexample: `4/625 = 0.0064 <= 1/25`.)

Combined with Guenin, what is now proved unconditionally is: **every triangle-free `G` whose signed
graph has no odd-`K5` minor satisfies `bip(G) <= N^2/25`** -- covering C5 and all its blow-ups, all
planar triangle-free graphs, Wagner and Petersen.

### Note

The audit reports that no published bound of the form "fractional odd-cycle transversal of a
triangle-free graph `<= n^2/c`" exists for any `c`, so Theorem A is proved here rather than cited.
Its proof is short and elementary and is the most realistic Lean formalisation target the campaign
has produced. NAMING: this "Theorem A" is `Lambda <= 1/25`; the round-8 stability family's
"Theorem D" is the different statement `psi <= (1-rho)^2/25 + rho*eta`.


---

## R3-C23 — round 9: discharging with a global potential is DEAD, structurally (GATED)

Root-agent entry, 2026-07-26. Own re-verification, `round5/claude_gate_r9_discharge.py`.

This was the last form of discharging never tried here (the purely local forms are A8, A9, A19).
It dies not to a witness but to a structure theorem: **the global potential is not a free parameter.**

For any sound reduction system -- every move `G -> G'` satisfying `bip(G) <= bip(G') + c` -- define
the shortest-path value `U(G) = min over moves [c + U(G')]`, with `U = 0` on bipartite graphs. Then a
potential `Phi >= 0` obeying the amortised step `Phi(G) - Phi(G') <= (f(G) - f(G')) - c` exists **iff
`U <= f`**, and the pointwise-largest one is `Phi* = f - U`. So "choose a clever global potential" is
not a degree of freedom; the potential is determined by the move family.

**Corollary 1, circularity.** `U >= bip` always: `U(G) = min[c + U(G')] >= min[c + bip(G')] >=
bip(G)` by soundness. So demanding `U <= f` is at least as strong as `bip <= f`, and the exact-cost
and edge-deletion instantiations have `U = bip` identically. Terminal lemma, verbatim:
*"min over deletion orderings of `sum_i (bip(G_i) - bip(G_{i+1})) <= N^2/25`"*, which telescopes to
the conjecture.

**Corollary 2, strength ceiling (the decisive one, gated by me).** For the only non-circular local
cost `floor(d/2)`, the counting identity `sum_i d_{G_i}(v_i) = |E|` forces `U(G) >= (|E| - N)/2`. On
`K_{m,m}` that equals `N^2/8 - N/2` while `bip = 0`:

```
        m =  4:  U >= 4     vs  N^2/25 = 64/25       c >= 0.0625
        m = 12:  U >= 60    vs  N^2/25 = 576/25      c >= 0.1042
        m = 50:  U >= 1200  vs  N^2/25 = 400         c >= 0.1200   -> floor 1/8 = 0.125
```

so the mechanism **cannot prove `bip <= c N^2` for any `c < 1/8`**, which is behind even the
published `1/23.5`, let alone the target `1/25`.

**Confirmed witnesses.** `Phi*` is negative on the whole extremal family: `C5[2] <= -1`,
`C5[3] <= -6`, `C5[4] <= -14`, `C5[10] <= -125`. (The family reported `-2` for `C5[2]`; my counting
bound gives `U >= 5` hence `Phi* <= -1`. Negative either way, verdict unchanged.) Pentagon charging
dies on `C7`, which has `bip = 1` and **zero** induced pentagons, so the charge has nowhere to go.

**Secondary, gated.** The Motzkin-Straus-deficit line `psi + (4/5)W <= 1/5` has margin exactly `0` on
every `C5[n]` -- but its complementary piece `psi <= W/5` is FALSE at the `N = 14` extremal graph
`M?AE@bH{AYN_LgBs?`: `psi = 1/28 > 8/245 = W/5`, equivalently `bip = 7 > 32/5 = |E|/5`. So the pair
adds nothing in the open band.

**If anyone reopens this**, the blocking step is: a cost function beating greedy insertion must bound
*"the edges from the deleted set to the monochromatic side of an optimal cut of `G - S`"* without
computing that cut -- which is exactly the circular instantiation.


---

## R3-C24 — the two proved theorems meet: a defect proposition, and a coverage map (GATED)

Root-agent entry, 2026-07-26. My own work, `round5/claude_coverage_map.py` and
`round5/claude_residual_margin.py`.

### PROPOSITION (mine, proved). The equality case of Theorem A IS the hypothesis of Theorem D.

For an induced 5-cycle `C` and a weighting `x`, define the DEFECT
`D(C) = sum_u x_u (2 - |N(u) cap V(C)|)`, nonnegative because Lemma 2's core gives
`|N(u) cap V(C)| <= (5-1)/2 = 2`. Then

* **(i)** `rho(C) <= D(C) <= 2 rho(C)`, where `rho(C)` is the weight on non-twin vertices off `C`;
* **(ii)** `D(C) = 0` implies `supp(x)` is `C5`-COLOURABLE, hence `psi(H,x) <= 1/25` unconditionally.

*Proof of (ii).* `D(C) = 0` forces `|N(u) cap C| = 2` for every `u` in `supp(x)`. Triangle-freeness
forbids those two neighbours from being adjacent, so they are at distance 2 on `C` and `u` is a full
twin of some class `i`. Two twins of one class are non-adjacent (else a triangle through `c_{i+1}`),
and twins of classes `i` and `i+2` are non-adjacent (likewise). So every edge of the support joins
consecutive classes and `class(.)` is a homomorphism onto `C5`. QED

Gated: over 3094 `(graph, x, induced C5)` instances, **0 violations of (i)**, and of the **666**
instances with `D = 0`, **0** had a non-`C5`-colourable support.

This is the equality analysis of Theorem A (Cauchy-Schwarz tight, so all `d(v)` agree on `C`; Lemma 2
tight, so every positively weighted vertex has exactly two neighbours on `C`) delivering exactly the
`rho = 0` hypothesis of Theorem D. The two theorems, proved independently by different families,
meet at `D = 0`.

### COVERAGE MAP — measured, not guessed

Call an instance SETTLED if one of the three proved facts applies: the support is `C5`-colourable, or
`D(C) = 0` for some induced `C5`, or Theorem D's `25*eta(C) + rho(C) <= 2`. Sampling the DANGEROUS
region deliberately (perturbing `C5`-concentrations at seven scales, 840 instances per graph, exact
rationals):

```
        graph            max psi SETTLED     max psi UNSETTLED
        Petersen              0.03973          203/6050  = 0.03355
        Grotzsch              0.03947          545/15876 = 0.03433
        Wagner                0.03973          406/13225 = 0.03070
        Gamma_11              0.03960          30/841    = 0.03567   <- worst anywhere
        Gamma_14              0.03973          55/1587   = 0.03466
        N=14 extremal         0.03947          6/175     = 0.03429
        C5[2], C5[3,1,2,2,1]  0.03973          none unsettled
```

The settled region carries the near-extremal instances (up to `0.0397`, approaching `1/25`); the
unsettled region tops out at `30/841 = 0.035672`, a margin of `0.004328`, i.e. `89.18%` of the
target. **The toolkit covers the sharp region and leaves the slack region unproved** -- the reverse
of the usual situation.

### What this is, and what it is NOT

If the margin is real, then off the settled region the conjecture reduces to a NON-SHARP bound, which
is a different kind of statement from the sharp one that has killed every mechanism here (the `1/20`
barrier, the plateau, the tightness of Theorem A everywhere).

But this is a MEASUREMENT, not a theorem, and I record its limits explicitly: the sampling is
heuristic, `psi` is known to have spurious local maxima (R3-C20 K-0) so no sampling certifies a
maximum, and an `11%` margin is modest. It is a direction with a number attached, not a result.

---

## R3-C25 — the residual margin, with the sampling removed: the "room to spare" premise is NOT supported

Answers the open `► RESIDUAL` item of round 9 ("decide whether the 11 % margin off the settled
region is real, since sampling cannot certify a maximum where spurious local maxima exist").
Gate: `round9/claude_gate_r10_residual.py` (the log `round9/R10_residual.log` is local-only per the
repo's `*.log` rule; re-running the script regenerates every number below). `Gamma_11 = And(4)`
rebuilt independently as the circulant on `Z_11` with `3*dist > 11`, cross-checked against the
`{i = 1 mod 3}` construction; 22 edges, `alpha = 4`, 33 induced pentagons, not `C5`-colourable.

**Part 1 — where the residual can live (exhaustive, all `2^11` induced subgraphs).**
Exactly **45** of the 2048 induced subgraphs of `Gamma_11` are not `C5`-colourable, and the
**smallest has 8 vertices** (11 of size 8, 23 of size 9, 10 of size 10, and the whole graph).
Since "support is `C5`-colourable" is one of the settled conditions and `ψ(H,x) = ψ(H[supp x], x)`
by R3-C2, **every weighting of `Gamma_11` supported on at most 7 vertices is settled**, and the
residual is confined to those 45 supports.

This **refutes** the natural expectation that motivated the test: `Gamma_11` is *not* vertex-critical
for `C5`-colourability, so the residual does not collapse onto the interior, and the boundary faces
of dimension 7..9 stay in play.

**Part 2 — the maximum, exhaustively rather than sampled.** By the blow-up identity `ψ` at the
rational point `a/q` is exactly `bip(H[a])/q^2`. Enumerating **every** integer weight vector, not a
sample (1 144 066 interior vectors at `q = 24` alone):

| region | denominators | vectors | exact max | vs `1/25` |
|---|---|---|---|---|
| interior, all `a_i >= 1` | `q = 11..24` | 2 475 970 | **`5/147` = 0.034014** at `q = 21`, `a = [1,2,2,1,3,1,3,1,3,1,3]` | 15.0 % below |
| any support, `a_i >= 0` | `q <= 13` | 2 143 428 | **`6/169` = 0.035503** at `q = 13` | 11.2 % below |

So A24's spurious local maxima cannot be the explanation for the margin: they cannot hide inside an
exhaustive grid, and the grid confirms the sampled order of magnitude.

**But the margin is not a target with room to spare, and the numbers say so.** The R9 sampled point
at `q = 29` reaches `30/841 = 0.035672`, which is **above every exhaustive maximum found here at
`q <= 24`**, interior or not. The residual maximum therefore still **rises as the grid is refined**;
the sequence over `q` is not monotone and shows no sign of settling below a definite ceiling. The
header of `round5/claude_residual_margin.py` proposed reading the margin as a reduction to
`ψ <= 1/25 − ε` off the settled region, "a statement WITH ROOM TO SPARE rather than the sharp one".
**That reading is unsupported**: nothing computed here bounds the unsettled supremum away from
`1/25`, and the refinement trend is against it. Recorded as a caution, not as a kill — the route is
not falsified, its advertised advantage is.

**What is certified:** the Part 1 support classification (exhaustive, exact) and the Part 2 maxima at
every denominator `q <= 24` (exhaustive, exact integer arithmetic). **What is not:** any bound on
`ψ` over the interior, since `ψ` is continuous but not concave and finitely many denominators
constrain nothing between grid points. Removing the *discretisation* gap still needs the interior
KKT system of R3-C2.

**Self-correction.** The first version of this gate's pentagon counter reported **0** induced
pentagons in `Gamma_11`, contradicting the 33 recorded in R3-C21. The graph was right and my counter
was wrong: its cycle walk rejected at the first step, where `prev` is `None` and both neighbours are
candidates. Replaced by the direct criterion (5 vertices spanning exactly 5 edges, all degrees 2,
which on 5 vertices forces a single pentagon); the count is **33**, matching R3-C21. Recorded because
a silent 0 here would have falsely voided the plateau argument on the campaign's wall graph.


---

## R3-C25 — round 9 odd-K5 family, and a RETRACTION of my own residual-margin suggestion (GATED)

Root-agent entry, 2026-07-26. Own gates: `round5/claude_gate_r9_petersen.py`,
`round5/claude_gate_r9_thmD.py`, `round5/claude_gate_a27_exhaustive.py`.

### RETRACTION 1 (already committed, restated here for the record): Petersen is NOT odd-K5-minor-free

R3-C22's consequence sentence listed Petersen among the graphs covered by Theorem A + Guenin. FALSE.
Switching at the inner 5-set makes the five spokes even and leaves all ten outer/inner edges odd;
contracting the spokes, the branch sets `{a_i,b_i}` are joined for all ten pairs of K5, all odd.
Explicit gap weight (w = 1 on outer/inner, 5 on spokes): `tau_w = 4` over all 512 cuts against a
feasible cover of cost `10/3`, gap exactly `6/5`; every odd cycle uses an EVEN number of spokes so
all 32 carry at least 3 non-spoke edges. The Petersen ceiling STILL HOLDS via the round-7 exact SOS
certificate, which never used Guenin. Round 7's own auditor had flagged this and I propagated the
error regardless.

### RETRACTION 2 (mine, and Codex called it): the residual margin has no epsilon

In R3-C24 I measured that weightings the proved toolkit cannot settle appeared to top out near
`30/841 = 0.035672`, about 11% below `1/25`, and suggested this would make the residual target
NON-SHARP -- which would have been a change of character, since sharpness is what has killed every
mechanism here. I flagged it as a measurement, not a theorem. Codex then reported that the unsettled
maximum RISES with grid refinement. **I checked it against my own work and Codex is right.**
Exhaustive over ALL integer weightings on `Gamma_11` with zeros allowed:

```
        q =  8   43758 weightings   max psi unsettled = 1/32  = 0.031250
        q = 10  184756 weightings                     = 3/100 = 0.030000
        q = 12  646646 weightings                     = 1/36  = 0.027778
        q = 14 1961256 weightings                     = 3/98  = 0.030612
```

all BELOW my sampled `q = 29` value of `0.035672`. Since sampling only lower-bounds the maximum at
its grid, the sequence is rising with refinement and nothing bounds it away from `1/25`. **The
residual target is still SHARP and my suggestion is withdrawn.** A27 survives as a decomposition of
the problem, not as a change of its character.

### ACCEPTED from the same round

* **THEOREM F.** `psi <= 1/25` whenever `eta <= 4/25`, doubling Theorem D's `1/13`. Gated on 10471
  exact instances with `eta` strictly inside the new band `(1/13, 4/25]`: 0 violations of `psi <=
  1/25` and 0 of Theorem D's inequality.
* **Theorem D's triangle-freeness is load-bearing.** C5 plus a vertex adjacent to two ADJACENT
  pentagon vertices, `x = (2/5,2/5,0,0,0,1/5)`: `psi = 2/25` against the bound `41/625`.
* **The round-9 family's own withdrawal is upheld.** "BAD_i = 0 for SOME i" fails at
  `y = (1/6,1/4,1/6,1/4,1/6)`, whose cyclic products are `(1/24,1/24,1/24,1/24,1/36)`: the minimum
  over any FOUR is `1/24 > 1/25`. The correct unconditional criterion is BAD_i = 0 for ALL i, i.e. a
  homomorphism to C5, which is classical.
* **THEOREM R9-1.** A triangle-free graph with an odd-K5 minor has `N >= 10`, and **Petersen is the
  unique one on `N <= 10`** (censuses: 1897 nine-vertex graphs, 0 hits; 12172 ten-vertex, exactly 1).
  So `psi = Lambda <= 1/25` for every triangle-free `G` on `N <= 10` except Petersen.
* **A28, gap quantification is DEAD.** An odd subdivision preserves `bip` and `Lambda`, and the twice
  subdivision realises ANY weighted MinUnCut instance exactly, so `sup psi/Lambda` over triangle-free
  graphs EQUALS the general LP gap: triangle-freeness contributes nothing and no constant `c` with
  `psi <= c*Lambda` exists. New exact records at odd girth 5: Higman-Sims `35/22`, Gewirtz `3/2`,
  Hoffman-Singleton `10/7`.
* **A29.** Restricting to the odd-K5 class is NOT a restriction (adjoin a zero-weight Petersen); the
  honest form is full-support `x`.

### Correction issued to Codex

Its Andrasfai profile `C(k-2,2)` should be `C(k-1,2)`: the exhaustive counts are 1, 3, 6, 10 for
`k = 3..6`, which `C(k-1,2)` reproduces and `C(k-2,2)` does not (it gives 0, 1, 3, 6).


---

## R3-C26 — Codex's R10 direct route: bridge GATED SOUND, frontier lemma survives falsification

Root-agent entry, 2026-07-26. Gates `round5/claude_gate_r10_vega.py` and
`round5/claude_gate_r10_arcbound.py`. I asked Codex two questions before gating and then answered
both myself rather than idle.

### Q1: is the Vega branch really discharged at delta > 5N/14? YES, certified exactly.

Brandt-Thomasse Corollary 4.1 says the twin-free maximal triangle-free weighted graphs with
`delta > 1/3` are the `Gamma_i` AND the 4-chromatic VEGA graphs, so the Vega branch cannot simply be
omitted. Weighted minimum degree is `delta*(G) = max_omega min_v omega(N(v))`; by LP duality any
probability vector `p` gives `delta*(G) <= max_u p(N(u))`, so one rational `p` certifies exclusion
exactly. Rebuilding the four Vega families from the verbatim Brandt-Thomasse construction:

```
        Upsilon_2        13 vtx   delta* = 12/35     = 0.342857
        Upsilon_2 - y    12 vtx            11/32     = 0.343750
        Upsilon_2 - {4}  12 vtx            11/32     = 0.343750
        Upsilon_2-{y,4}  11 vtx            10/29     = 0.344828   <- the binding one (Grotzsch)
        Upsilon_3 ...    16 vtx            21/62     = 0.338710
        Upsilon_4 ...    19 vtx          2336/6929   = 0.337134
```

all `< 5/14 = 0.357143`, and `delta_reg(Upsilon_i) = (9i-6)/(27i-19)` decreases to `1/3`, so no Vega
graph anywhere meets `delta > 5/14`. **The t = 5 list is `Gamma_1..Gamma_4` only, exactly as Codex
stated.**

### Q2: does the bridge route through "Guenin covers Petersen"? NO.

The list is `Gamma_1` (bipartite), `Gamma_2 = C5`, `Gamma_3 = And(3) = Wagner` (exact SOS certificate
`round7/Q4_cert_g8_d1.pkl`) and `Gamma_4 = And(4) = Gamma_11` (the frontier lemma). Petersen never
appears, so my Petersen retraction does NOT damage this route.

### The frontier lemma survives my falsification attempt

`ARCBOUND_{Gamma_11}(x) <= (sum x)^2/25` over the 56 cyclic-interval cuts, exhaustive over ALL
integer weightings with ZEROS ALLOWED:

```
        q =  8    43758 weightings   max 25*ARCBOUND/q^2 = 50/64  = 0.781250   0 violations
        q = 10   184756 weightings                       100/100 = 1.000000   0 violations
        q = 12   646646 weightings                       100/144 = 0.694444   0 violations
        q = 14  1961256 weightings                       150/196 = 0.765306   0 violations
```

with the mandatory sanity check tight: a `C5`-concentration gives `25*psi = 25 = q^2` exactly. At
every grid `max 25*ARCBOUND/q^2` EQUALS `max 25*psi/q^2`, i.e. the arc family attains the full
minimum at the maximising weightings. This is a finite check and can only ever falsify, so it is
evidence for the lemma, never a proof of it.

### A BAND MAP I derived while checking, useful for choosing the threshold

`delta*(Gamma_j) = j/(3j-1)`, so at threshold `c` the Andrasfai list is `{Gamma_j : j/(3j-1) > c}`:

```
        c = 5/14  = 0.35714  ->  Gamma_1..Gamma_4   (j < 5)    Vega excluded
        c = 6/17  = 0.35294  ->  Gamma_1..Gamma_5   (j < 6)    Vega excluded
        c = 7/20  = 0.35000  ->  Gamma_1..Gamma_6   (j < 7)    Vega excluded
        c = 10/29 = 0.34483  ->  Gamma_1..Gamma_9   (j < 10)   VEGA ENTERS (Grotzsch)
```

So each step down the threshold buys a smaller band at the cost of exactly one more Andrasfai
certificate, and `10/29` is the hard floor: below it the Vega side must be handled. `5/14` is the
cheapest choice that needs only `Gamma_1..Gamma_4`, which is why Codex picked it.

### Status

The R10 bridge is GATED SOUND. Its single open item is the frontier lemma, unfalsified at these
grids. Under GOAL clause (c) an unconditional theorem on an explicit minimum-degree range DOES count,
so this route would shrink base (6)'s band from `delta <= 0.375N` to `delta <= 0.3571N`.


---

## R3-C27 — Codex's R10 support reduction: GATED, every figure reproduced independently

Root-agent entry, 2026-07-26. Gate `round5/claude_gate_r10_supports.py`, built from my own
`Gamma_11` and my own arc family; nothing imported from Codex's code.

Codex's exact falsifier certificate reports NO strict rational counterexample to
`25 * ARCBOUND_Gamma_11(x) <= (sum x)^2` with cleared denominator `q <= 50` (my own independent
sweep reached `q <= 14`, 2.8M weightings, also clean). The load-bearing part is its structural
support reduction, which I re-derived in full:

```
        nonempty supports                                        2047   (2^11 - 1)
        supports where SOME arc carries no monochromatic
          support edge, hence ARCBOUND = 0                        1474   MATCH
        surviving supports                                         573   MATCH
        D_22 orbits among the survivors                             38   MATCH
        inclusion-minimal survivors                                  33   MATCH
        ... and they are EXACTLY the 33 induced C5s of Gamma_11         confirmed
        D_22 orbits of those pentagons                                3   MATCH
          representatives {0,1,4,5,8}, {0,1,4,6,8}, {0,2,4,6,8}, orbit sizes 11 + 11 + 11 = 33
```

Codex's three representatives fall one per orbit of mine. So the reduction is sound: **any surviving
falsifier must contain one of those three pentagons up to a dihedral automorphism, with cleared
denominator at least 51.**

This matters beyond bookkeeping: it turns the remaining search from "all nonnegative weightings" into
a targeted one over three symmetry classes, and it independently reproduces the 33-pentagon count
that also drives the rainbow-1 obstruction (R3-C21) and my own transport gate.

### Where the R10 route now stands, in full

* bridge GATED SOUND (R3-C26): Vega excluded exactly, no Petersen dependency;
* frontier lemma unfalsified at `q <= 50` (Codex) and `q <= 14` (me), support-reduced to three
  pentagon classes;
* the single open item is a PROOF of the frontier lemma. Codex holds the `D_22`-invariant degree-4
  Positivstellensatz; I am not touching it.

### My next structural target, recorded so we do not collide

The bridge needs only `max_x psi(Gamma_11) <= 1/25`, which is WEAKER than the arc form Codex is
proving. A second, independent route to it: A5b asks whether `psi = Lambda` for every PRODUCT weight
on `Gamma_11` (31 of 32 exact packing certificates so far). `Gamma_11` is NOT weakly bipartite -- I
proved that with an explicit gap weight -- so `psi = Lambda` fails for SOME weight; the open question
is whether it can fail for a PRODUCT weight. If product-weight integrality holds on `Gamma_11`, then
Theorem A closes the frontier without any SDP.


---

## R3-C28 — A5b on Gamma_11: product-weight integrality holds where it matters; pentagons alone do NOT

Root-agent entry, 2026-07-26. My own work, `round5/claude_a5b_product_integrality.py` and
`round5/claude_a5b_pentagon_packing.py`. This is my SDP-free route to Codex's R10 frontier lemma:
if `psi = Lambda` for every product weight on `Gamma_11`, then Theorem A closes it outright.

### Evidence FOR product-weight integrality (not a proof)

Exhaustive over all integer weightings with zeros allowed, taking the top 2500 by `psi` at each grid
-- deliberately the weightings that threaten the ceiling, since a gap at small `psi` cannot:

```
        q =  9    92378 weightings   gaps psi > Lambda: 0   exact packing certificates: 2500
        q = 10   184756 weightings                      0                               2500
        q = 11   352716 weightings                      0                               2500
        q = 12   646646 weightings                      0                               2500
```

**10000 exact rational packing certificates, zero gaps.** Each certificate is a feasible packing of
value exactly `psi`, which proves `Lambda = psi` outright since `packing <= Lambda <= psi`.

This matters because `Gamma_11` is NOT weakly bipartite -- I proved that with an explicit finite gap
weight (`tau_w = 4 > 10/3`). So integrality genuinely FAILS on this graph for some weight. But that
witness needs six edges at weight zero, and a product weight can only zero an edge by zeroing a
VERTEX, which zeroes every edge there. Product weights are a thin subfamily that appears to avoid
every bad face.

### NEGATIVE, and it kills a tempting simplification

I then asked whether the optimal packing can always be taken on the 33 induced pentagons alone, which
would reduce the frontier lemma to a finite 33-variable, 22-constraint bilinear problem -- no SDP, no
cut family. (The rainbow-1 obstruction of R3-C21 would NOT apply, since that is about aggregating
CUT values and this is the dual side.) **It cannot.** With `Lambda_pent` the packing LP restricted to
pentagons:

```
        q =  9   Lambda_pent < psi in  4 of 1500 top-psi weightings
        q = 10                          8
        q = 11                         10
        q = 12                          5
```

e.g. `a = [1,1,0,2,2,0,1,1,0,1,0]` at `q = 9` has `psi = 2` but `Lambda_pent = 1`. So the length
7, 9 and 11 odd cycles are genuinely required and the 33-variable reduction is dead.

**One refinement worth recording:** every shortfall occurs at `25*psi/q^2` between `0.5` and `0.69`,
never near `1`. So pentagons appear to suffice exactly at the near-extremal weightings and fail only
well below the ceiling. That is the opposite of the usual failure pattern and may still be usable,
but I am not adopting it as a target on this evidence.

### Status of the route

A5b remains LIVE and SDP-free in principle, with 10000 exact certificates and no counterexample, but
"psi = Lambda for every product weight on Gamma_11" is UNPROVED and is not implied by anything in the
ledger. Codex keeps the degree-4 Positivstellensatz on the arc form; this is the independent second
route to the same target.


---

## R3-C29 — a PROVED sharpening of A1: `ARCBOUND(And(k)) <= (k-1)W/(3k-1)`, tight at C5

Root-agent entry, 2026-07-26. Mine, proved and verified (`round5/claude_arcbound_sharpened.py`).
The registry records `ARCBOUND <= W/3` for the circle graphs. That is not optimal at any finite `k`.

### Statement

For `And(k) = Gamma_m`, `m = 3k-1`, adjacency `circdist >= k`, and every `x >= 0`:

```
        ARCBOUND(x)  <=  (k-1)/(3k-1) * W,        W = sum over edges of x_u x_v.
```

`(k-1)/(3k-1) < 1/3` for every finite `k` and increases to `1/3`, so this strictly improves the
recorded bound at every `k`, recovering it only in the limit. It is TIGHT at `C5` (`k = 2`).

### Proof

**(1) Intervals of length `k` are independent.** Two vertices inside such an interval are at circular
distance at most `k-1`, below the adjacency threshold `k`. So for the interval cut
`A_i = {i,...,i+k-1}` no monochromatic edge lies inside `A_i`, and every monochromatic edge lies
inside the complementary interval `B_i` of length `m-k = 2k-1`. Hence `ARCBOUND <= min_i e(B_i)`,
where `e(B)` is the weight of edges with both ends in `B`.

**(2) Every edge lies in EXACTLY `k-1` of the `m` intervals `B_i`, whatever its length.** An edge has
`k <= d <= 2k-1`. A `(2k-1)`-interval contains both ends iff it contains one of the two arcs joining
them. The short arc has `d+1` vertices and fits in `(2k-1)-(d+1)+1 = 2k-1-d` positions; the long arc
has `m-d+1 = 3k-d` vertices and fits in `(2k-1)-(3k-d)+1 = d-k` positions. Both counts are
nonnegative exactly on `k <= d <= 2k-1`, and they sum to `(2k-1-d)+(d-k) = k-1`, with **no dependence
on `d`**.

Therefore `sum_i e(B_i) = (k-1)W`, and the minimum is at most the average:
`ARCBOUND <= (k-1)W/m = (k-1)W/(3k-1)`. QED

### Verification

Both combinatorial steps checked exactly for `k = 2..8`: every `k`-interval independent, and the
per-edge incidence count collapsing to the single value `k-1` in each case. The inequality itself:
16000 exact rational weightings across `And(2..5)`, **0 violations**; observed maxima of
`ARCBOUND/W` are `1/5, 115/536, 216/901, 13/50` against bounds `1/5, 1/4, 3/11, 2/7`. On `C5` the
bound is attained: `W = 1/5`, `ARCBOUND = 1/25 = (1/5)W`.

### What it does and does not buy — stated plainly

It is an AVERAGING bound over the `m` rotations, and registry A6 records that fixed averaging cannot
reach `1/25`. Consistent with that, at a `C5`-concentration inside `Gamma_11` it gives
`3W/11 = 3/55 = 0.054545` against the truth `1/25 = 0.04`. **So it cannot close Codex's frontier
lemma**, and I am not proposing it as one.

What it does is shrink the open window. `ARCBOUND <= 1/25` now follows whenever
`W <= (3k-1)/(25(k-1))`, i.e. for `Gamma_11` whenever `W <= 11/75 = 0.146667`, against the previous
`W <= 3/25 = 0.12`. With Motzkin-Straus capping `W <= 1/4`, the open window for `Gamma_11` narrows
from `W in (0.12, 0.25]` to `W in (0.14667, 0.25]`. The improvement is largest at SMALL `k`, which is
exactly where the hard cases sit.


---

## R3-C30 — the natural sequel to R3-C29 is DEAD: length selection does not rescue rotation averaging

Root-agent entry, 2026-07-26. Mine, `round5/claude_arcbound_lengthsel.py`.

R3-C29's bound averages the interval cut over the `m` rotations at the fixed length `L = k`, which
makes it a fixed averaging certificate, and A6 says those cannot reach `1/25`. The obvious repair is
to keep the rotation average but CHOOSE THE LENGTH FROM `x`, which is a weight-reading rule and so
escapes A6. Summing over the `m` rotations of a length-`L` interval,

```
        sum_i q_{S_i}(x) = sum_e x_u x_v f(L, d_e),
        f(L,d) = cnt_L(d) + cnt_{m-L}(d),   cnt_A(d) = max(0, A-d) + max(0, A-m+d),
```

since an edge is monochromatic for the cut iff both ends lie in the interval or both in its
complement. The profiles are worth recording:

```
        Gamma_8 :  L = 4 gives f = [2, 0] on distances [3,4]   -- the only non-constant length
        Gamma_11:  L = 5, 6 give f = [3, 1] on distances [4,5] -- the only non-constant lengths
        every other L gives a CONSTANT profile, i.e. an R3-C29-type family
```

So at `L = 4` on Wagner the antipodal (distance-4) edges are never monochromatic, and at `L = 5, 6` on
`Gamma_11` the distance-5 edges are penalised at one third the rate of distance-4 edges.

**Verdict: the resulting bound `B(x) = (1/m) min_L sum_e x_u x_v f(L,d_e)` FAILS.** Exact rational
weightings, 6000 per graph:

```
        And(2)  B(x) > (sum x)^2/25 in 1756 of 6000   worst ratio 1.2500
        And(3)                          100            worst ratio 1.4323
        And(4)                           18            worst ratio 1.1466
        And(5)                            2            worst ratio 1.0462
```

**The diagnostic is the useful part.** In EVERY failing case the true `ARCBOUND` is still far under
target -- `0` against `196/25`, `0` against `144/25`, `23` against `49`, `32` against `1444/25`. So
the bound is not detecting a real obstruction; it is simply lossy. The loss sits entirely in the
ROTATION average, not in the length choice: the minimum over rotations is far below their mean, and
no refinement that still averages over rotations can recover the gap.

**Consequence for the route.** Any proof of the frontier lemma must select the ROTATION from `x`, not
merely the length -- averaging over rotations is now exhausted in both its fixed (R3-C29) and
weight-reading-in-length (here) forms. That is the same conclusion the campaign reached globally in
R3-C21 ("a proof must read the weights"), now localised to the one open lemma.


---

## R3-C31 — the 11 length-k interval cuts do NOT suffice; the full arc family is needed

Root-agent entry, 2026-07-26. Mine, `round5/claude_kinterval_suffices.py`.

R3-C30 showed any proof of the frontier lemma must select the ROTATION from `x`. The natural
follow-up is whether the ROTATIONS ALONE suffice at the single length `k` -- i.e. whether the
`m` cuts of the R3-C29 family already give the bound, which would shrink Codex's target from 56 arc
cuts to eleven, each with the clean description "weight of the edges inside a 7-interval".

Define `KBOUND(x) = min over the m rotations of e(B_i)`, `B_i` the complementary `(2k-1)`-interval.
Always `ARCBOUND <= KBOUND`. Exhaustive over all integer weightings, zeros allowed:

```
        And(3) = Gamma_8   q =  8   6435 weightings     1 violation of KBOUND <= q^2/25
        And(4) = Gamma_11  q =  8   43758                11 violations
                           q = 12   646646               11
                           q = 14   1961256             165
```

The Wagner violation is at the UNIFORM weighting `a = (1,1,1,1,1,1,1,1)`: `KBOUND = 3` against
`q^2/25 = 2.56`, while the true `psi = 2` is comfortably under. On `Gamma_11`,
`a = (2,1,1,1,1,1,1,1,1,1,1)` at `q = 12` gives `KBOUND = 6 > 5.76` with true `psi = 4`.

**So the length-`k` family is genuinely insufficient and the other arc lengths are load-bearing.** In
every violation the true `psi` remains far below target, so this is a deficiency of the restricted
family, not a threat to the conjecture. Recorded so that neither of us re-aims the `D_22` degree-4
Positivstellensatz at a reduced cut family: **the 56 cuts are needed.**

### Where the arc route now stands, precisely

* `ARCBOUND <= (k-1)W/(3k-1)` proved and tight at C5 (R3-C29), but averaging-limited (A6);
* length selection does not rescue it, and all the loss is in rotation averaging (R3-C30);
* rotations at a single length do not suffice either (here);
* so the frontier lemma needs a rule that selects BOTH the length and the rotation from `x`, over
  the full 56-cut family. That is exactly the object Codex's degree-4 Positivstellensatz encodes,
  which is now the better-motivated of the two live routes.


---

## R3-C32 — Theorem F's pentagon-centred ball misses equality cases; they sit at C5-BLOW-UPS

Root-agent entry, 2026-07-26. Mine, `round5/claude_thmF_residual.py` and
`round5/claude_thmF_witness.py`.

I asked whether the region Theorem F leaves open on `Gamma_11` carries a MARGIN, since that is what a
branch-and-bound closure of `max_x psi(Gamma_11) <= 1/25` would need: Theorem F settles everything
within `eta(C) <= 4/25` of a pentagon, including every `C5`-concentration, so if the rest were
bounded away from `1/25` the remainder could be closed by crude interval bounds.

It is not. Exhaustive over all integer weightings, zeros allowed, restricted to
`x(C) < 21/25` for EVERY one of the 33 induced pentagons:

```
        q =  8   17116 unsettled   max 25*psi/q^2 = 25/32 = 0.781250
        q = 10  112706             max            = 1      = 1.000000   <- the ceiling, exactly
        q = 12  487861                              25/36 = 0.694444
        q = 14 1193907                              75/98 = 0.765306
```

**An explicit equality case Theorem F cannot see** (22 of them at `q = 10`, one orbit
representative):

```
        a = (2,1,1,0,2,0,1,1,2,0,0)   support {0,1,2,4,6,7,8}, size 7
        psi = 1/25 EXACTLY;  the heaviest pentagon carries only 8/10 = 0.8 < 21/25
```

so Theorem F's hypothesis fails at every induced pentagon simultaneously while `psi` sits exactly on
the ceiling.

### The honest reading, stated carefully

The support of that witness is **`C5`-COLOURABLE**, so the FULL toolkit does settle it, via Theorem B
/ the accepted base. My test applied Theorem F alone. **So this witness does NOT by itself kill a
branch-and-bound closure** -- that question needs the full toolkit and was already answered
negatively in R3-C25, where Codex showed the unsettled maximum rises with grid refinement and I
confirmed it against my own exhaustive data.

What it DOES establish is structural and sharper: the equality set of the conjecture on `Gamma_11` is
strictly larger than the 33 `C5`-concentrations, and the extra extremal weightings are `C5`-BLOW-UP
weightings on larger supports (here 7 vertices). **An exactness ball centred on pentagons therefore
cannot cover the extremal set, however large its radius is made.** Theorems D and F would have to be
re-centred on blow-up weightings, which is exactly the extension the round-9 family attempted and
reported blocked, with the obstruction named: a distance-0 bad edge costs in 5 cuts and a distance-2
one in 3, while the compensating credit is charged in only 2, and at a balanced blow-up point the
AM-GM slack is exactly 0.

So the blow-up recentering is not an optional improvement of Theorem D/F -- it is forced by the
geometry of the equality set, and its obstruction is already recorded.


---

## R3-C33 — Codex's degree-4 D_22 run: BLOCKED, and its face argument GATED SOUND

Root-agent entry, 2026-07-26. Gate `round5/claude_gate_r10_d22face.py`, my own construction.

Codex ran the `D_22`-invariant degree-4 multiplier Positivstellensatz at `c = 25` on the 56 arc cuts
of `Gamma_11`. Reduction sizes: 2611 multiplier orbit scalars, 8647 Gram orbit scalars, 52 parity
block orbits, representative PSD orders `{286:1, 66:5, 11:20, 1:26}`. CLARABEL returned
`optimal_inaccurate` after 1627 s with minimum representative Gram eigenvalue `-6.5e-07`.

**Codex did not call the iterate a certificate, and it is right not to.** Its stated reason is an
exact FACE argument, which I re-derived independently and confirm in every checkable part:

```
        arc minimum of q_S(1_U) over the 33 induced pentagons          1        MATCH
        number of TIGHT arc cuts per pentagon                       24..25      MATCH
        parity-zero block order = degree-3 monomials in 11 vars       286       MATCH
        EXACT RATIONAL RANK of the 33 evaluation vectors               33       MATCH
```

The rank being FULL is the load-bearing fact: tightness gives `T(1_U) = 0` at every induced `C5`
support `U`, so an exact PSD parity-zero Gram block must vanish on a **33-dimensional subspace of a
286-dimensional space**. The returned numerical block has only 16 eigenvalues below `1e-5` and
`max |QK| ~ 9.8e-3`, so it is nowhere near that mandatory face and **entrywise rational rounding of
it is invalid** -- exactly Codex's conclusion.

I also verify the forced-zero mechanism, though not Codex's orbit count (which depends on its `D_22`
indexing, and I did not reconstruct that): **1034 of the 1848 (arc cut, pentagon) pairs have
`q_S(1_U) > 1`**, and for each, coefficientwise nonnegativity of `nu_S` together with the tightness
identity `nu_S(1_U) q_S(1_U) = 0` forces every degree-4 multiplier monomial supported inside `U` to
vanish for that cut. The mechanism is sound; Codex reports it kills 1147 of 2611 orbit coefficients.

### Verdict and the registered exit rule

Status is **BLOCKED, not DEAD**: numerical failure does not kill the route, and the registered exit
condition requires either an exact rational weighting violating the frontier lemma or an exact dual
separating `c = 25` from the degree-4 cone. Neither exists. Codex's stated next step -- impose the
exact induced-`C5` multiplier and Gram face BEFORE any further feasibility computation, then
reconstruct in `Fraction`s -- is the correct one, and is now quantified: the face has codimension at
least 33 in the 286-block and zeroes over half the `(cut, pentagon)` incidences.

**No escalation up the degree hierarchy** is warranted; the registered rule forbids it, and the
diagnosis here is that the solve was aimed off the face, not that degree 4 is too low.
