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
