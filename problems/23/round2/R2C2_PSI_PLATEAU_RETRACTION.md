# R2-C2 — the ψ landscape has a plateau at 1/25, and several of my own recorded results are RETRACTED

Root-agent finding, 2026-07-25. This is a **correction of my own work**, and it is the most
consequential item of the session because the retracted statements would have misdirected the next
agent.

## The lemma I missed

**Lemma (induced-subgraph monotonicity).** For any graph `H` and any `S ⊆ V(H)`,

```
        max_x ψ(H,x)  ≥  max_y ψ(H[S], y).
```

*Proof.* Let `x` be supported on `S`. For any cut `(A,B)` of `H`, only monochromatic edges with both
ends in `S` contribute to `Σ_{uv mono} x_u x_v`. As the cut ranges over all cuts of `H`, its
restriction to `S` ranges over **all** cuts of the induced subgraph `H[S]`, because the vertices
outside `S` may be 2-coloured arbitrarily and freely. Hence `ψ(H,x) = ψ(H[S], x|_S)` exactly, and
taking the maximum over `x` supported on `S` gives the claim. ∎

**Corollary.** `max_y ψ(C5,y) = 1/25` (AM–GM, proved earlier), so **every triangle-free graph
containing an induced `C5` has `max_x ψ ≥ 1/25`.** And a shortest odd cycle is always induced, so
every triangle-free graph of odd girth exactly 5 contains one.

## Verification

`claude_induced_c5.py` locates an induced `C5`, puts weight `1/5` on each of its vertices, and
evaluates `ψ` exactly over **all** `2^(n−1)` cuts of the ambient graph:

| pattern | n | induced C5 | exact ψ at that point | value I had recorded |
|---|---|---|---|---|
| Wagner C8(1,4) | 8 | 0,1,2,3,4 | **1/25 = 0.040000** | 0.038652 |
| Petersen | 10 | 0,1,2,3,4 | **1/25** | 0.030879 |
| Grötzsch | 11 | 0,1,2,3,4 | **1/25** | 0.037700 |
| C11(1,3) | 11 | 0,1,2,5,8 | **1/25** | 0.036426 |
| C13(1,5) | 13 | 0,1,2,3,8 | **1/25** | 0.035170 |
| And(4) | 11 | 0,1,4,5,8 | **1/25** | 0.034666 |
| And(5) | 14 | 0,1,5,6,10 | **1/25** | 0.032746 |

Every recorded value was strictly below the value achieved by a single explicit rational point.

## RETRACTED

1. **R1-C8 table and its conclusion.** The ψ values listed there for Wagner, Petersen, Grötzsch,
   C11(1,3), C13(1,5) are poor local optima, not maxima. The statement *"C5 is the unique maximiser
   among the patterns tested, with Wagner the closest rival at 0.0387"* is **FALSE**: every one of
   those patterns attains `1/25` exactly.
2. **R2/G1 Andrásfai reading.** *"The family recedes monotonically from the ceiling, with equality
   only at And(2) = C5"* is **FALSE**. `And(k)` for `k ≥ 2` has odd girth 5, hence an induced `C5`,
   hence `max_x ψ ≥ 1/25`. The "monotone recession" was an artifact of a hill-climb whose budget
   shrank as `n` grew. (The narrower claim that **no** Andrásfai graph was found to *exceed* `1/25`
   survives, but it is now near-vacuous — nothing in that computation could have exceeded it.)
3. **"Wagner is the tightest open case at 0.038652."** Retracted. Its value is `≥ 1/25`, and `= 1/25`
   if the conjecture holds; there is no `0.0013` gap to close.
4. **The reading of F8's "max ψ = 1/25 for all 573 reduced patterns".** That statement is now
   *explained and largely automatic*: the `≥` direction holds for every pattern containing an
   induced `C5`, which is essentially all of them. Whatever content it has lies entirely in the `≤`
   direction, and the report gives no certificate for that.

## What this actually teaches

**The ψ reformulation is degenerate.** For every triangle-free `H` of odd girth 5,
`max_x ψ(H,x) ≥ 1/25` automatically, and the conjecture asserts equality. So the landscape is a huge
plateau at exactly `1/25`, reached by concentrating on any induced `C5`. Consequences:

* **Hill-climbing over patterns is worthless as evidence.** My R1-C8 "no refutation found" showed
  nothing: the search never even climbed onto the plateau, let alone probed above it. Any future
  search must start *at* an induced-`C5` point and ask whether it can be improved.
* **The counterexample target is now sharp**: find a triangle-free `H` and a weighting that beats
  concentrating on an induced `C5`, i.e. `max_x ψ(H,x) > 1/25` strictly. Equivalently — and this is
  the useful form — find `H` where spreading weight beyond a single induced `C5` *helps*.
* **It explains the SDP failure quantitatively.** The relaxations stall near `0.053` because the true
  optimum is a plateau value attained on a low-dimensional face; a relaxation that cannot see the
  combinatorial structure of cuts has no reason to come down to it.

## Discipline note

The error was mine and it was avoidable: I accepted hill-climb output as an estimate of a maximum
without first checking the obvious lower-bound construction. The rule that follows, and that I have
applied above: **before reporting any optimisation result, evaluate the obvious explicit candidate
and check the optimiser at least matches it.**
