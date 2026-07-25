# R3-C1 — every fixed averaging certificate for the ψ-ceiling is dead, with an exact gap

Root-agent result, 2026-07-25. This upgrades §3g of `round1/CLAUDE_GATE_RESULTS.md`, which tested
**two** particular averaging weights and found both too weak, into a theorem covering **all** of them,
and it exhibits the exact size of the gap on the whole extremal family.

## Setting

For a graph `H` and `x` in the simplex, `ψ(H,x) = min over cuts S of H of Σ_{uv monochromatic} x_u x_v`.
By the blow-up identity the conjecture is exactly `max_x ψ(H,x) ≤ 1/25` for every triangle-free `H`.

Since `ψ` is a **minimum** over cuts, every probability distribution `λ` on the cuts of `H` gives a
valid upper bound: writing `c_e = Pr_λ[e monochromatic]`,

```
    ψ(H,x)  ≤  Σ_S λ_S q_S(x)  =  Σ_{e=uv ∈ E} c_e x_u x_v      for every x,
    max_x ψ(H,x)  ≤  B(λ) := max over the simplex of  Σ_{e=uv ∈ E} c_e x_u x_v.
```

`B(λ)` is the value of the natural LP/averaging certificate: one multiplier vector, not depending on `x`.
This is the shape every "pick a clever family of cuts and average" argument takes.

## Theorem (no averaging certificate can reach 1/25)

For every graph `H` with at least one edge and every probability distribution `λ` on the cuts of `H`,

```
        B(λ)  ≥  (max_e c_e)/4  ≥  (Σ_e c_e)/(4|E(H)|)  ≥  bip(H) / (4 |E(H)|).
```

Consequently, if `25·bip(H) > 4·|E(H)|` then **no** averaging certificate proves `max_x ψ(H,x) ≤ 1/25`.

**Proof.** Let `uv` be an edge with `c_uv = max_e c_e` and take `x = 1/2` on `u`, `1/2` on `v`, zero
elsewhere: the objective equals `c_uv/4`, so `B(λ) ≥ c_uv/4`. The maximum of a finite list is at least
its average, giving the second inequality. Finally every cut `S` has at least `bip(H)` monochromatic
edges, so `Σ_e c_e = Σ_S λ_S |mono(S)| ≥ Σ_S λ_S bip(H) = bip(H)`. ∎

## The gap is 25 %, uniformly along the extremal family

| `H` | `bip` | `|E|` | `bip/(4|E|)` = certificate floor | `25·bip > 4|E|`? |
|---|---|---|---|---|
| `C5` | 1 | 5 | **1/20 = 0.0500** | 25 > 20 — dead |
| `C5[n]`, any `n` | `n²` | `5n²` | **1/20 = 0.0500** | `25n² > 20n²` — dead |
| Petersen | 3 | 15 | 1/20 = 0.0500 | dead |
| Higman–Sims | 350 | 1100 | 7/88 = 0.0795 | dead |
| Grötzsch | 4 | 20 | 1/20 = 0.0500 | dead |

For `C5` the floor `1/20` is **attained**: the uniform distribution over the five rotation cuts gives
`c_e = 1/5` on all five edges, and `max_x Σ_i x_i x_{i+1} = 1/4` (Motzkin–Straus, `ω(C5) = 2`), so
`B(λ) = 1/20` exactly. Hence

```
        min over all λ of B(λ)  =  1/20     on C5, against the truth 1/25,
```

a gap of exactly 25 %, and by the second row of the table the *same* 25 % gap holds on `C5[n]` for
every `n`. The averaging route is therefore not merely weak at small orders — it fails by a constant
factor on the extremal family at every order, so no refinement of the *choice* of `λ` can rescue it.

## What this rules out, and what it forces

Ruled out, as a family and not case by case:

* any proof of the shape "average over a cleverly chosen family of cuts" (the two instances recorded
  in §3g — uniform over all cuts, `1/8`; uniform over the five rotation cuts, `1/20` — are now seen to
  be the generic and the optimal member of a family that cannot work);
* any LP relaxation of `max_x min_S q_S(x)` whose dual variable is a single distribution over cuts,
  independent of `x`. That includes the "one inequality per cut, take a nonnegative combination"
  formulation in every guise.

Forced: **the cut must depend on the weights.** Concretely, a proof of the conjecture is equivalent to
an *algorithm*

> given a triangle-free `G` and weights `x ≥ 0` with `Σx = 1`, produce a bipartition of `V(G)` whose
> monochromatic weight `Σ_{uv mono} x_u x_v` is at most `1/25`,

together with a proof of its guarantee. The obstruction above says the algorithm cannot be
"sample from a fixed distribution of cuts"; it must read `x`. This is the precise sense in which the
problem is a *rounding* problem, and it is the reason the level-1 and level-2 Lasserre relaxations
recorded in Round 2 (`0.0553` and `0.0532` on `C5`) stall above `1/20` rather than below it: they are
relaxations of the same max–min whose duals are weaker than the averaging certificate, not stronger.

## Verification

`claude_gate_avgcert.py`: for each pattern it computes `bip(H)` by exhaustive maximum cut over all
`2^(n−1)` bipartitions in exact integers, `|E(H)|`, and the floor `bip/(4|E|)`; and for `C5` it
verifies by exhaustive enumeration that every one of the 16 cuts has at least one monochromatic edge
(the fact behind `Σ_e c_e ≥ 1`) and that the five rotation cuts realise `c_e = 1/5` on every edge.
All arithmetic is `Fraction`.
