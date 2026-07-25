# R5-K22 — RETRACTION: the moment criterion is FALSE, and the pentagram lemma is not new

Root-agent entry, 2026-07-25, recorded with the same prominence as the claims it withdraws. Round 6
produced the falsifier; I verified it myself before accepting it.

## 1. The criterion `min(A, H) ≤ 1/25` is REFUTED

**Witness.** `Γ_14`, support `S = {0,1,2,5,6,7,10,11}`, uniform weights `1/8`. Verified by my own
implementation, exact rationals:

```
        W = 3/16,        2T = 33/224,        A = W − 2T = 9/224 = 0.0401786  >  1/25
        m(b) = 3/64 for EVERY b in the support        ⇒  Var_μ(m) = 0
        H = 1/E_μ[1/m] = 3/64 = 0.046875,   and  bound_k = 3/64 for every k = 0 … 300
        CRIT = min(A, H) = 9/224 = 0.040179  >  1/25 = 0.04          ← the criterion FAILS
        ARCBOUND = ψ = 1/32 = 0.03125  ≤  1/25                        ← the conjecture is UNTOUCHED
```

The far-graph on the support is 3-regular on 8 vertices — **the Wagner graph `V8 = C8(1,4) = And(3)`**,
the same object that has been the hard case at every stage of this campaign. Round 6's independent
sweep (673 525 748 leaves) pins `max CRIT = 3/64` exactly and finds 1790 such falsifiers, the
smallest on `Γ_14`; every one of them has `ARCBOUND ≤ 4/121 = 0.0331 < 1/25`, so **no counterexample
to Erdős #23 was produced** — only my route to proving the arc-cut conjecture is dead.

**Therefore RETRACTED:** R5-K9 (the moment criterion), R5-K16 (its "final form"), R5-K18 (the
two-term harmonic-mean form, "0 violations in 3606 tests"), and the proof strategy of R5-K20 that
rested on them. The 3606 tests were real but the sampled families never generated a far-regular
`V8` configuration: `Var_μ(m) = 0` there, so *every* weighting of the neighbourhood-cut values —
arithmetic, harmonic, geometric, any `g^k`, the variance refinement — collapses to the same number
`3/64`, and no functional of `{m(b)}` alone can see the good cut. That is the structural reason the
whole family of refinements failed at once.

**Standing lesson, now twice learned this session:** a criterion must be run against adversarially
*constructed* configurations, not sampled ones. The regression set gains a tenth witness:
`Γ_14, S = {0,1,2,5,6,7,10,11}, uniform` — the far-regular Wagner configuration.

## 2. The pentagram lemma (R5-K19) is correct but NOT new

The mathematics is confirmed — `m(b) = x_{i−1}x_{i+1}`, AM–GM twice, equality exactly at the
balanced blow-up. But Round 6's audit checked 36 609 circle supports (`q ≤ 16`, `|S| ≤ 8`) and found
**"pentagonal" ⟺ "homomorphic to `C5`" with zero mismatches**. Graphs homomorphic to `C5` already
satisfy `ψ ≤ 1/25` by the classical AM–GM argument in the accepted base. So the lemma re-proves a
known case; its only new content is that the certifying cut can be taken to be an *arc*.

Decisively: it covers **no** Andrásfai graph. `And(k) = Γ_{3k−1}` for `k = 3..7` is non-pentagonal
and not `C5`-colourable — i.e. the residual class is still exactly what the chain reduces the
conjecture to. The claim that this "shrinks the frontier" is withdrawn.

## 3. What survives

* The arc-cut conjecture itself: **unrefuted**, and now tested far harder — 1790 near-misses all with
  `ARCBOUND ≤ 0.0331`, and `max CRIT = 3/64` is attained by configurations whose true `ARCBOUND` is
  `1/32`.
* Everything in `round3/CLAUDE_GATE_R3.md` (averaging certificates dead, interior reduction,
  independent-support concavity, first-order plateau maximality, density band, low-degree
  optimality, the verified `C5` SOS certificate) — none of it depended on the criterion.
* The Fourier identity R5-K10 (`A = Σ ψ̂(n)|μ̂(n)|²`) — an identity, not a bound, so unaffected. Note
  it *explains* the falsifier: the Wagner configuration on `Γ_14` has strong 5-fold-adjacent
  structure without being pentagonal.

## 4. What this closes off

No functional of the neighbourhood-cut values `{m(b)}` together with `A` can certify the arc-cut
ceiling: the witness has all `m(b)` equal and `A > 1/25`, while the true `ARCBOUND` is well below.
Any future route must use cuts outside `{N(b)} ∪ {half-arcs}` — the two-length family that was
exhaustively verified at the *value* level is not enough at the *certificate* level.
