# Q5 — a_7 sub-bound: GPT Pro ANSWER + Step-2 AUDIT (2026-06-20)

User manually relayed the saved `GPT_PRO_QUESTION.md` primary question to GPT Pro.
GPT returned a COMPLETE, EXACT, FINITE proof. Step-2 audited line-by-line AND
verified computationally. **VERDICT: CORRECT — adopted as a proved lemma.**

## Result proved by GPT
For every `{C3,C5}`-free graph `G` (odd-girth >= 7) on `N` vertices:
  **β(G) <= N^2/32.**
Hence `a_7(N) <= N^2/32 < N^2/25` for all `N`; in particular `a_7(5n) <= 25n^2/32 < n^2`.
**Consequence:** any triangle-free graph on `5n` vertices with `β >= n^2` is NOT
`C5`-free, so it contains a `C5` — and in a triangle-free graph every `C5` is INDUCED
(a chord would force a triangle). This is the enabler of the C5-stability route.

## Proof (as given, verified)
Key lemma (the engine): for `{C3,C5}`-free `G`,
  **MaxCut(G) >= e/2 + (1/2N) Σ_u d(u)^2.**
Steps: (1) radius-2 ball `H_v = G[{v}∪L1∪L2]` (L1=N(v), L2=dist-2 set) is BIPARTITE:
L1 independent (tri-free); L2 independent because x,y∈L2 adjacent ⟹ with a∈N(v)∩N(x),
b∈N(v)∩N(y), either a=b (triangle a,x,y) or a≠b (5-cycle v-a-x-y-b-v) — both forbidden.
(2) e(H_v) = Σ_{u∈N(v)} d(u) =: S_v (every edge at u∈N(v) stays in the ball, exactly
one endpoint in N(v)). (3) Proper-bipartition H_v + random outside ⟹ E[cut]=e/2+S_v/2 ⟹
MaxCut >= e/2+S_v/2 ∀v; average and Σ_v S_v=Σ_u d(u)^2 give the key lemma. (4) Cauchy-
Schwarz Σd^2 >= 4e^2/N (subtracted ⟹ correct direction) ⟹ β <= e/2 - 2e^2/N^2 <= N^2/32
(max at e/N^2 = 1/8).

## Step-2 AUDIT — all steps SOUND
- Step 1: the 5 vertices v,a,x,y,b are all distinct (a,b∈L1; x,y∈L2; a≠b by case; L1∩L2=∅)
  so v-a-x-y-b-v is a genuine C5 SUBGRAPH; odd-girth>=7 forbids ALL 5-cycles ⟹ valid. This
  is the ONLY use of C5-freeness, used correctly.
- Step 2: neighbours of u∈N(v) are at distance <=2 (inside H_v); L1 independent ⟹ each edge
  has exactly one N(v)-endpoint ⟹ e(H_v)=Σ_{u∈N(v)} d(u). Correct.
- Step 3: fixed H_v bipartition (S_v edges cross) + independent uniform outside ⟹ each
  non-ball edge crosses w.p. 1/2 ⟹ E[cut]=e/2+S_v/2; MaxCut>=E (probabilistic method);
  averaging valid (MaxCut>=each>=avg); Σ_v Σ_{u∈N(v)} d(u)=Σ_u d(u)^2 (count d(u) per u). ✓
- Step 4: C-S direction correct (Σd^2 subtracted, lower bound improves the β upper bound);
  x/2-2x^2 = 1/32 - 2(x-1/8)^2 <= 1/32. ✓
- Final: every C5 in a tri-free graph is induced (chord ⟹ triangle). ✓

## Step-2 INDEPENDENT computational verification
`(in PROGRESS log)`: all `{C3,C5}`-free graphs (triangle-free via geng -t, filtered by
trace(A^5)=0) on N=7..11 (N=12 running): **0 violations** of MaxCut-lemma AND of
β<=N^2/32. Worst β/N^2 = 0.0204 ≈ 1/49 (C7-blowup lower bound), well below 1/32.

## How this advances Step 2
- It CLOSES the `{C3,C5}`-free case of ANY stability dichotomy EXACTLY and finitely
  (β <= 25n^2/32 < n^2 — far below target, no BCL).
- It proves the C5-stability ENTRY POINT: a counterexample (β>=n^2) has an induced C5,
  so the C5-structure tools (MC3 two-dominating-C5, MERGE/frozen-pair) are always available.
- The bound is NOT tight (C7-blowup gives N^2/49); the method may sharpen, but N^2/32
  already suffices for the `<n^2` consequence.
- NEXT: combine with the merge/MC3 route — show the guaranteed induced C5 can be leveraged
  (ideally to a 2-dominating C5, which by MC3 forces β<=n^2). This is the remaining gap.
