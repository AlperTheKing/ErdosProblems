# Root-agent note — the arc-cut problem in transported coordinates (for H1/H2 and for round 5)

Written after the round-4 launch, so the agents did not have it. It is a clean restatement of the
open arc-cut problem with no measure theory left in it.

## Transport

Push `μ` to Lebesgue by its quantile map. Arcs stay arcs, and the adjacency `d(x,y) > 1/3` becomes:
there is a non-decreasing degree-one circle map `φ` with

```
        φ³ = id + 1 ,           x ~ y  ⟺  y ∈ (φ(x), φ²(x)) .
```

(`φ(x)` is the quantile position of `x + 1/3`.) Everything below is Lebesgue measure on `R/Z`.

## The three-thirds picture becomes three monotone curves in three rectangles

Fix a rotation `c`. The points `c, φ(c), φ²(c)` cut the circle into three arcs of lengths
`ρ₁, ρ₂, ρ₃` with `ρ₁ + ρ₂ + ρ₃ = 1`, and `φ` maps arc 1 onto arc 2 onto arc 3 onto arc 1 (+1),
monotonically. In normalised coordinates write

```
        f₁ : [0,ρ₁] → [0,ρ₂],   f₂ : [0,ρ₂] → [0,ρ₃],   f₃ : [0,ρ₃] → [0,ρ₁]
```

for those three increasing bijections; the *only* constraint is `f₃ ∘ f₂ ∘ f₁ = id`, so the free data
is `(ρ, f₁, f₂)` and `f₃ = (f₂∘f₁)^{-1}`.

Every adjacent pair joins two different arcs, and the three between-arc masses are exactly the areas
**above** the three curves:

```
        A₁ = ρ₁ρ₂ − ∫f₁ ,      A₂ = ρ₂ρ₃ − ∫f₂ ,      A₃ = ∫₀^{ρ₁} f₂(f₁(x)) dx ,
        W  = A₁ + A₂ + A₃ .
```

(The third identity comes from `∫f₃ = ρ₃ρ₁ − ∫ f₃^{-1}` and `f₃^{-1} = f₂∘f₁`.)

The three `1/3`-arc cuts at rotation `c` have values exactly `A₁, A₂, A₃`. Equivalently, in the
original coordinates, the cut through the point `b` has value

```
        m(b) = ∫_{φ(b)}^{φ²(b)} ( b + 1 − φ(x) ) dx ,
        m'(b) = ρ(φ(b)) − ρ(φ²(b)) · φ'(b)   where ρ(u) = φ(u) − u,
```

so its critical points satisfy `φ'(b) = ρ₂/ρ₃`.

## Check on the two anchors

* **Uniform measure**: `φ(x) = x + 1/3`, `ρ = (1/3,1/3,1/3)`, every `f_i` is a translation, and
  `A₁ = A₂ = A₃ = 1/18`. So the three-thirds family alone gives `1/18 > 1/25` — the half-arc is what
  saves the uniform measure (`1/36`). **Any proof must use arcs of at least two different lengths.**
* **Five equal atoms**: at the rotation `c = 0`, `ρ = (2/5, 2/5, 1/5)`, `f₁` and `f₂` are the
  one-step staircases, `∫f₁ = ∫f₂ = 1/25`, and
  `A₁ = 4/25 − 1/25 = 3/25`, `A₂ = 2/25 − 1/25 = 1/25`, `A₃ = 1/25`, summing to `W = 1/5` and with
  minimum exactly `1/25`. So at the extremal measure the three-thirds family alone is already tight.

## The open statement, restated

> For every `(ρ, f₁, f₂)` as above there is an ARC cut — not necessarily one of the three
> `1/3`-arcs — whose monochromatic area is at most `1/25`.

Equivalently, since `mono = W − (separated mass)`: the adjacent pairs form a family of circle arcs
each of length in `(1/3, 1/2]` (each pair's short path, weighted); find two points `a, b` such that
the mass of arcs containing **both or neither** is at most `1/25`.

Recorded refuted specialisations (do not retry): half-arcs alone; the five-block averaging route;
any rule that selects the arc by its mass alone. See `round3/R3C11_ARC_CUT_MECHANISM.md` §8.
