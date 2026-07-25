# R3-C19 — RESOLVED: `And(4)` is **not** weakly bipartite. My open item is withdrawn.

Root-agent entry, 2026-07-26. Supersedes `R3C19_ANDRASFAI4_OPEN_ITEM.md`, which recorded a tension
between Round 7's odd-`K5` minor at `And(4)` and my own failure to find any integrality gap there.
The tension is resolved **against my searches**. Round 7 and R3-C17/C18 were right.

## 1. The odd-`K5` minor is genuine — verified at the signed level, not merely as a `K5` minor

`claude_gate_and4_oddk5.py --and4`. All edges of `Γ_11` are odd, so the signed-minor conditions are:

* a branch set may be contracted **iff** it induces a connected **bipartite** subgraph (balanced,
  since with all edges odd, balanced ⟺ bipartite);
* switching to make that subgraph all-even labels it by its 2-colouring `ℓ`;
* a connecting edge `uv` survives as **odd** exactly when `ℓ(u) = ℓ(v)`; all others are deleted.

For `Γ_11` (`u ~ v ⟺ 3·circdist > 11 ⟺ circdist ∈ {4,5}`, 22 edges) and the claimed branch sets:

```
  {0,4,8}   induces the path 0–4–8    bipartite,  ℓ = {0:0, 4:1, 8:0}
  {1,5,9}   induces the path 1–5–9    bipartite,  ℓ = {1:0, 5:1, 9:0}
  {2,6,10}  induces the path 2–6–10   bipartite,  ℓ = {2:0, 6:1, 10:0}
  {3}, {7}  singletons
```

with the all-zero flip vector, **all ten pairs** carry an odd connecting edge:

```
  (0,1)→(1,8)  (0,2)→(2,8)  (0,3)→(3,8)  (0,4)→(0,7)  (1,2)→(2,9)
  (1,3)→(3,9)  (1,4)→(1,7)  (2,3)→(3,10) (2,4)→(2,7)  (3,4)→(3,7)
```

The colour choices are **forced**, not free: `N(3) = {7,8,9,10}` and `N(7) = {0,1,2,3}`, so each
singleton meets each 3-set in exactly one vertex, giving `a = b = c = e = f`.

Independently, the clutter minor `C∖Z/Y` was built explicitly and has **22 members of sizes 3 and 5**
— exactly the 10 triangles and 12 five-cycles of odd-`K5` — with `τ = 4`, matching odd-`K5`.

## 2. An explicit finite gap weight — non-weak-bipartiteness proved directly, without Guenin

`claude_gate_and4_gap.py`. On `Γ_11` put

```
  w = M  on the 6 contracted edges (0,4),(1,5),(2,6),(4,8),(5,9),(6,10)
  w = 1  on the 10 kept edges above
  w = 0  on the 6 deleted edges (0,5),(0,6),(1,6),(4,9),(4,10),(5,10)
```

Then for every `M ∈ {5, 10, 100, 1000}`:

| quantity | value | how certified |
|---|---|---|
| `τ_w` | **4** | exact integer minimum over all 1024 bipartitions |
| `τ*_w` | **≤ 10/3** | explicit rational cover `y = 1/3` on the kept edges, `1` on the free edges; **0** of the 596 odd cycles violated |

`4 > 10/3`, so the odd-cycle covering LP on `And(4)` has an integrality gap at a **finite** weight.
This is a direct proof, independent of Guenin's theorem, that `And(4)` is not weakly bipartite.

## 3. Why 8500 random trials found nothing — and the correction to my own reasoning

The gap weight is **degenerate**: 6 edges at weight 0, 6 at a large weight, 10 at weight 1. Weights
drawn at random are strictly positive and generic, and product weights `w_uv = x_u x_v` cannot
produce the required contraction/deletion pattern at all. Random sampling is not a test for
idealness; the certificates live on a thin face. **My three search families were non-conclusive, and
I withdraw the doubt they raised.**

I also had the clutter correspondence backwards on first attempt, which is why my initial gap search
failed even when aimed straight at the minor. For a covering clutter:

```
   weight 0  on e   <->   DELETION      (a free element covers every member through it)
   weight oo on e   <->   CONTRACTION   (covers may not use e, so they must hit C \ {e})
```

I had assigned weight `0` to the contracted edges, which gives `τ_w = τ*_w = 3` and no gap. Recorded
because the same slip would silently void any future clutter-minor computation.

## 4. Contrast case: Wagner has no odd-`K5` minor, exhaustively

`claude_gate_and4_oddk5.py --wagner`. Over **every** canonical 5-tuple of disjoint branch sets of
`Γ_8` — 2646 of them, and `Σ_j C(8,j)·S(j,5) = 56 + 420 + 1120 + 1050 = 2646` confirms the
enumeration is complete — **zero** odd-`K5` minors. So `And(3)` is weakly bipartite, and R3-C17's
Wagner ceiling `max_x ψ(And(3)) = 1/25` now rests on an exhaustive combinatorial check plus Guenin
plus Theorem A, with **no dependence on the SOS certificate** whose Gram blocks I was still verifying.

## 5. BUG in my earlier tooling, and its (harmless) direction

My earlier `And(4)` runs used **451** odd cycles of lengths 5, 7, 9. The true count is **596**:

```
      length  5:  33      length 7: 154      length 9: 264      length 11: 145
```

Every odd **Hamiltonian** cycle was missing (`596 − 451 = 145`, exactly the 11-cycles).

Direction of the error, stated before re-running: fewer covering constraints ⟹ **smaller** `Λ`.
Since `Λ ≤ ψ` always, an under-computed `Λ` that already equals `ψ` forces the true `Λ` to equal `ψ`:
`Λ_short ≤ Λ_true ≤ ψ = Λ_short`. So R3-C18's conclusion should survive — and it does.
`claude_gate_and4_recert.py` re-ran it against the complete list, upgraded from a float LP to **exact
rational packing certificates** (a feasible packing of value `ψ` proves `Λ = ψ`, since
`packing ≤ Λ ≤ ψ`), in integer weights `w_uv = a_u a_v`:

```
        31 of 32 weightings CERTIFIED Lambda = psi exactly
        (uniform: psi = 4/121; the C5-concentration: psi = 1/25; 29 of 30 random)
```

The single exception is my rationaliser failing to find a small denominator, not a counterexample.

## 6. Registry consequence: the general form of this route is BLOCKED, the `And(k)` form is not

**Blocking lemma, verbatim.** *For every triangle-free `H` and every `x ≥ 0`,
`τ_{w(x)}(H) = τ*_{w(x)}(H)`, where `w(x)_uv = x_u x_v`* ("product-weight integrality", PWI).

With Theorem A (`Λ ≤ 1/25` for every triangle-free `G` and every `x`), PWI yields `ψ ≤ 1/25` for
every triangle-free `H` — the **whole conjecture**. So PWI in general form is at least as strong as
the conjecture and is **BLOCKED** under search-discipline rule 4.

**And in fact PWI is FALSE** (`claude_gate_find_n14_gap.py`, my own witness). Of the 1274 maximal
triangle-free 14-vertex patterns, **exactly one** attains `τ = 7 = ⌊196/25⌋` — graph6
`M?AE@bH{AYN_LgBs?`, 32 edges — and on it

```
        tau  = 7      exact integer minimum over all 8192 bipartitions
        tau* <= 32/5  exact rational cover, denominator 1/5, feasible against all 10204 odd cycles
```

a gap of `35/32`. Uniform weights *are* product weights, so the covering/packing route fails at an
extremal object, not at some pathological auxiliary graph. This independently reproduces registry
entry A5's decisive fact, which I had failed to reproduce earlier in this same tick and had flagged
as unverified. Note the witness is **not** a `C5` blow-up: `C5[3,3,3,3,2]` gives only `τ = 6`, so
`a(14) = 7` is attained off the extremal family — the `N = 14` instance of the A12 phenomenon.

The restriction to `And(k)` is **not** blocked: it delivers only the Andrásfai half of the `δ > N/3`
reduction, not the conjecture. That half remains the live target, and Guenin is now provably
unavailable for it from `k = 4` on — so it needs a different certificate.

## 7. What this points at next

`max_x ψ(And(k)) ≥ 1/25` automatically for every `k ≥ 2` (plateau: `And(4)` contains the induced
`C5` `[0,3,7,10,4]`, verified). The task is therefore exactly to show **no weighting beats the
`C5`-concentration**. Round 7's family Q4 did this for Wagner with an exact rational
Positivstellensatz certificate; the same machinery aimed at `Γ_11` is the next concrete finite
target, with `Γ_14` after it.
