# Exact MaxCut / β bounds for triangle-free graphs (Step-2 toolbox)

Owner: Step-2 lead. Last updated: 2026-06-20.
These are EXACT, unconditional, finite-n facts (no asymptotics, no BCL). They are
used to discharge low-edge-density ranges of the base cases *without* enumeration.

## L0 (universal, any graph)
`MaxCut(G) >= e(G)/2`  ⟹  `β(G) = e - MaxCut <= e/2`  ⟹  `β <= ⌊e/2⌋`.
Corollary at N=30: `e(G) <= 73 ⟹ β(G) <= 36`. (β integer, e=73 ⟹ β ≤ 36.)
This needs NO triangle-free hypothesis.

## L1 (triangle-free strengthening)  — PROVED + exhaustively verified
**Claim.** For every triangle-free graph `G` with max degree `Δ = Δ(G)`,
`MaxCut(G) >= e(G)/2 + Δ/2`, equivalently `β(G) <= ⌊(e(G) − Δ)/2⌋`.

**Proof.** Let `v` attain `deg(v)=Δ`. Since `G` is triangle-free, `N(v)` is an
independent set. Build a cut `(L,R)`: put `v∈L` and all of `N(v)∈R`. All `Δ`
edges at `v` are cut, and there are no edges inside `N(v)` to lose. Let
`W = V ∖ ({v} ∪ N(v))`. Process `W` greedily in any order, placing each vertex on
the side that cuts ≥ half of its edges to already-placed vertices. Every edge of
`G` is either (a) incident to `v` — all `Δ` of them cut — or (b) incident to `W`
(its other endpoint in `N(v)` or `W`) — counted as a back-edge during the greedy
pass, so ≥ half of these are cut; there are no other edges, because the only
remaining possibility, an edge inside `N(v)`, cannot exist (triangle-free). Hence
`MaxCut(G) >= Δ + (e−Δ)/2 = e/2 + Δ/2`. ∎

Equality holds e.g. on every star `K_{1,k}` (e=Δ=k, β=0). Tight family confirms
the constant `1/2` on `Δ` cannot be improved.

**Verification.** `experiments/verify_L1_maxcut_delta.py`: exhaustive over ALL
triangle-free graphs on `n=5..9` vertices via `nauty geng -t` (2466 graphs),
exact MaxCut by brute force. **0 violations**; tight cases match the star family.

## What L1 buys for the base cases (HONEST scope)
- It discharges the **low-edge sub-band unconditionally**: at N=30,
  `e <= 73 ⟹ β <= 36` already from L0; L1 sharpens to `β <= ⌊(e−Δ)/2⌋`, so any
  30-vertex triangle-free graph with `e − Δ <= 72` has `β <= 36`. For a putative
  `β>=37` counterexample this forces `e >= 74 + Δ`.
- It does **NOT** touch the high-density band (`e >= 140` at N=30). There the
  bound is far from `36` (e.g. `e=180, Δ=12 ⟹ ⌊(180−12)/2⌋ = 84`), and indeed the
  extremal `C5[6]` has `e=180, β=36` saturating the conjecture — so high density
  genuinely requires the exact/flag-algebra (Codex enumeration) content. L1 is
  not a shortcut for that, and is not claimed to be.

## Relation to existing tools
- The single-vertex deletion bound used in the a(25) entry, `β(X) <= β(X−x) +
  ⌊d(x)/2⌋`, is the "local" cousin; L1 is the "global one-shot" version anchored at
  the max-degree vertex. They are independent and can be combined.
- L1 ⟹ for any triangle-free `G`, `β(G) <= ⌊(e − Δ)/2⌋ <= ⌊e/2⌋`. Monotone, exact.
