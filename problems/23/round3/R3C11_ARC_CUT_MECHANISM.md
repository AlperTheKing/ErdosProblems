# R3-C11 — the ARC-CUT mechanism: a weight-reading certificate that is exactly tight on the whole Andrásfai family

Root-agent result, 2026-07-25. This is the first candidate mechanism in the campaign that satisfies
the constraint imposed by R3-C1 (*a proof must read the weights*) **and** is exactly tight at `1/25`
on an infinite family, and it targets the one place where the literature has reduced the conjecture
on an explicit degree range to a named finite/structured family.

## 1. Where it comes from

`And(k)` is the **circular complete graph** `K_{(3k−1)/k}`: on `Z_m` with `m = 3k−1`,
`u ~ v ⟺ 3·circdist(u,v) > m` (verified independently in `claude_arccut.py`, definition check for
`k = 2..7`; the multiplier `v ↦ kv mod m` carries the residue-`1 mod 3` connection set onto the
"far" relation). Equivalently: **`And(k)` is the circle graph `Γ` on `R/Z` — `x ~ y ⟺ d(x,y) > 1/3` —
restricted to `3k−1` equally spaced points.** Write `Γ_m` for the graph on `m` equally spaced points,
so `And(k) = Γ_{3k−1}` and every finite discretisation of `Γ` is some `Γ_m`.

Two facts make the family a single object rather than infinitely many cases:

* `K_{p/q} → K_{p'/q'}` iff `p/q ≤ p'/q'`, and `(3k−1)/k = 3 − 1/k` increases, so
  `And(2) → And(3) → And(4) → …`; since `H → K` implies `max ψ(H) ≤ max ψ(K)`,
  **`A(k) := max_x ψ(And(k),x)` is nondecreasing with `A(2) = 1/25`.** The Andrásfai question is a
  single limit question.
* `χ_f(And(k)) = (3k−1)/k > 5/2` for `k ≥ 3`, so no `And(k)` with `k ≥ 3` maps to `C5` and the
  elementary AM–GM certificate is unavailable for the entire family.

## 2. The mechanism

For a weighting `x` on `Γ_m` define

```
    ARCBOUND(x) = min over ARCS A = {i, i+1, …, i+ℓ−1} of
                  [ Σ_{u,v ∈ A, u~v} x_u x_v  +  Σ_{u,v ∉ A, u~v} x_u x_v ].
```

Every arc cut is a cut, so `ψ(Γ_m, x) ≤ ARCBOUND(x)` always. The cut is chosen **after** looking at
`x` — the position and the length of the arc both depend on the weights — so this family is not
excluded by R3-C1, unlike every averaging certificate.

**CONJECTURE (arc-cut).** `25·ARCBOUND(x) ≤ (Σx)²` for every nonnegative weighting of every `Γ_m`.

Equivalently, in the continuum: for every probability measure `μ` on the circle there is an arc `A`
with monochromatic mass at most `1/25`.

## 3. Why it would settle an explicitly named open case

The arc-cut conjecture implies `max_x ψ(And(k),x) = 1/25` for **every** `k` — that is Heinig's
Conjecture 6 — and hence `bip(G) ≤ N²/25` for every triangle-free `G` homomorphic to an Andrásfai
graph. By Chen–Jin–Koh (weighted form as quoted by Brandt–Thomassé) the twin-free maximal
triangle-free weighted graphs with `δ > 1/3` are exactly the Andrásfai graphs `Γ_i` and the
4-chromatic **Vega** graphs. So arc-cut + the Vega analogue give the conjecture unconditionally on
`δ > N/3`, shrinking the open band from `(0.16N, 0.375N]` to `(0.16N, N/3]` — which GOAL rule (c)
admits as progress, and which is the sharpest target the literature offers.

## 4. Exhaustive exact evidence

`claude_arccut.cpp`: for a given `m`, enumerate **all** integer weightings `a ≥ 0` with `Σa = q`
(rotation-canonical), compute `ARCBOUND` exactly in integers, and compare `25·ARCBOUND` with `q²`.

| `m` | arc cuts | `q` searched | `max_a 25·ARCBOUND(a) − q²` | tight configurations |
|---|---|---|---|---|
| 5 (`And(2) = C5`) | 11 | 1..16 | `≤ 0`, `= 0` exactly at `q ≡ 0 (mod 5)` | `(t,t,t,t,t)` |
| 8 (`And(3)` = Wagner) | 29 | 1..16 | `≤ 0`, `= 0` at `q ≡ 0 (mod 5)` | `(0,t,0,t,t,0,t,t)` |
| 10 | 46 | 1..16 | `≤ 0`, `= 0` at `q ≡ 0 (mod 5)` | `(0,t,0,t,0,t,0,t,0,t)` |
| 11 (`And(4)`) | 56 | 1..16 | `≤ 0`, `= 0` at `q ≡ 0 (mod 5)` | 5 atoms |
| 13 | 79 | 1..16 | `≤ 0`, `= 0` at `q ≡ 0 (mod 5)` | 5 atoms |

In every case the whole profile `q ↦ max_a ARCBOUND(a)` is **identical to the `C5` profile**
`0,0,0,0,1,1,1,2,2,4,4,4,6,6,9,9,…`, and the maximisers are always five-atom configurations. So on
these graphs the arc family alone already certifies the ceiling, with equality exactly where the
conjecture is sharp.

Two sanity anchors, both exact:

* five equally spaced atoms inside `Γ_20 = And(7)` give `ARCBOUND = 1/25` exactly;
* the uniform weighting gives `1/32, 4/121, 3/98, 9/289, 3/100` on `And(3..7)` — matching the true
  `bip/n²` in each case, and tending to the continuum half-arc value `1/36`, so the family is tight
  in the `5`-atom case and *also* correct on the uniform measure. A cut family that were tight only
  at the extremal point would be suspect; this one is not.

## 5. What is proved, and what is open

Proved here:

* `And(k) = Γ_{3k−1}` exactly (own verification), so the family is one continuum object;
* every arc cut is a cut, hence `ψ ≤ ARCBOUND` and every arc-cut bound is a *valid* upper bound —
  the conjecture above can only ever be **too weak**, never wrong in the dangerous direction;
* the "three thirds" identity: for any rotation `c`, the circle splits into three consecutive arcs
  each of which is independent (an arc of length `≤ 1/3` spans distance `≤ 1/3`), every adjacent pair
  joins two *different* thirds, and the three `1/3`-arc cuts have values exactly the three
  between-thirds masses `S12, S23, S31`, whose sum is the total adjacent mass `W`. Hence
  `ARCBOUND ≤ W/3` for every measure, and the conjecture holds outright whenever `W ≤ 3/25`.

Open (this is the technical target):

> For every probability measure `μ` on `R/Z` with total adjacent mass `W > 3/25`, some arc `A`
> satisfies `mono(A) ≤ 1/25`.

Two boundary cases show what any proof must reconcile, and neither family of arcs alone suffices:

* the **uniform** measure has `W = 1/6 > 3/25`, all three thirds carry exactly `W/3 = 1/18 > 1/25`,
  and it is saved only by the **half-arc**, which gives exactly `1/36`;
* the **five-atom** measure has `W = 1/5`, is saved by a `1/3`-arc giving exactly `1/25`, and the
  crude bound `mono ≤ β₁β₂` is off by a factor two there — the exact "staircase" structure
  `mono = ∫∫_{t<s} dν₁(t) dν₂(s)` between the two remaining thirds is what makes `1/25` appear.

A useful reformulation for the attack: transporting `μ` to Lebesgue by its quantile map turns the
problem into one about a monotone circle map `φ` with `φ³ = id + 1`, adjacency `y ∈ (φ(x), φ²(x))`,
and Lebesgue measure — arcs remain arcs, and the extremal object becomes the five-step `φ`.


---

## 6. STRENGTHENING FOUND AFTERWARDS: `ARCBOUND · (Σx)² ≤ W²`

While looking for the missing mechanism in the `W > 3/25` regime I noticed that the arc bound is
governed by the total adjacent mass `W = Σ_{u~v} x_u x_v` alone, in the sharpest possible way:

> **CONJECTURE (W-square).** For every weighting of every circle graph,
> `ARCBOUND(x) · (Σx)² ≤ W(x)²`; equivalently, for a probability measure, `ARCBOUND ≤ W²`.

Evidence, all exact rational arithmetic (`claude_arccut.py` and the inline gate):

* **uniform weighting, `Γ_m` for every `m = 5..25`** — 21 cases, 0 violations, and **equality for
  every odd `m`**: `(m, ARCBOUND, W²)` = `(5, 1/25, 1/25)`, `(7, 1/49, 1/49)`, `(9, 1/81, 1/81)`,
  `(11, 4/121, 4/121)`, `(13, 4/169, 4/169)`, `(15, 4/225, 4/225)`, `(17, 9/289, 9/289)`,
  `(19, 9/361, 9/361)`, `(21, 1/49, 1/49)`, `(23, 16/529, 16/529)`, `(25, 16/625, 16/625)`;
  even `m` is strictly below (e.g. `Γ_8`: `1/32 < 9/256`);
* 540 random rational weightings over `Γ_5, Γ_7, Γ_8, Γ_10, Γ_11, Γ_13, Γ_14, Γ_16, Γ_17` — 0
  violations.

Why it matters: `W² ≤ 1/25 ⟺ W ≤ 1/5`, so the W-square conjecture would settle the arc-cut
conjecture — hence `max_x ψ(And(k),x) = 1/25` for every `k` — for every measure with
`W ≤ 1/5`, which is far past the `W ≤ 3/25` that the proved three-thirds bound reaches. The
equality family (all odd cycles `C_L`, where `W = 1/L` and `ARCBOUND = 1/L²`) shows it is exactly
the right shape and cannot be improved.

**Open remainder after that:** measures with `W ∈ (1/5, 1/4]`. The endpoint `W = 1/4` is the
Motzkin–Straus maximum, attained only by two antipodal atoms, where `ARCBOUND = 0`; and the samples
in that regime found so far (three atoms at `0, 1/3+ε, 2/3+2ε` with `W = 2/9`; four atoms at the
quarters with `W = 1/8`) all have `ARCBOUND = 0` because the adjacency graph degenerates to a path
or a matching. So the regime looks easy but has no proof yet.

## 7. Extended exhaustive verification

`claude_arccut.exe` over **all** integer weightings, rotation-canonical, zeros allowed:

| `m` | 5 | 8 | 10 | 11 | 13 | 14 | 16 | 17 | 19 | 20 | 22 | 23 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `q` searched | ≤16 | ≤16 | ≤16 | ≤16 | ≤16 | ≤15 | ≤15 | ≤15 | ≤15 | ≤15 | ≤15 | ≤15 | ≤15 |
| violations of `25·ARCBOUND ≤ q²` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

In every one of the thirteen circle graphs the profile `q ↦ max_a ARCBOUND(a)` is identical to the
`C5` profile and the maximisers are five-atom configurations.


## 8. Three selection rules that do NOT work (recorded so the proof is not attempted along them)

The arc must be chosen adaptively (R3-C1), and these three natural adaptive rules are now refuted:

1. **Half-arcs only** (position adaptive, length fixed at `1/2`): fails at `q = 7` on `Γ_8, Γ_11,
   Γ_16, Γ_20`. Witness: the weighting `(1,1,2,2,1)` on an induced `C5` sitting at *unequally spaced*
   positions gives half-arc minimum `2` against `q²/25 = 49/25 = 1.96`, while the full arc family
   gives `1`. So the LENGTH must adapt too.
2. **The 5-block averaging route**: the inequality `ARCBOUND ≤ (1/5)(W + 4P₀ + 2P₁)` is correct
   (verified on 400 random measure/cut-choice pairs, 0 failures) and is exactly tight at the
   five-atom measure, but it cannot be *realised*: on `Γ_11` there is a weighting with `W = 0.1818`
   for which **every** choice of five cut points gives `W + 4P₀ + 2P₁ = 0.2174 > 1/5`. Since the
   route needs `W + 4P₀ + 2P₁ ≤ 1/5`, it is BLOCKED as a proof of the arc-cut conjecture.
3. **Mass-window rules** (choose any arc whose *μ-mass* lies in a fixed window): all of
   `[1/3,1/2]`, `[2/5,3/5]`, `[1/3,2/3]`, `[2/5,1/2]`, `[3/10,1/2]` fail, with 29 to 74 violations
   of `1/25` in ~700 random measures each and worst ratios up to `2.9 × (1/25)`. So the selection
   cannot be a function of the arc's mass alone; the geometry (position and length together) is
   essential.

What survives every probe: the **full** two-parameter arc family. The continuous optimisation over
atom positions *and* weights (`k = 5..9` atoms, 120–200 restarts each, exact re-evaluation) returns
`0.0400000000` for every `k`, with the optima always collapsing onto five effective clusters.
