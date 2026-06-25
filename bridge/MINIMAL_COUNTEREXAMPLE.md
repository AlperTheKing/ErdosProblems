# Minimal-counterexample reduction for Erdős #23 (multiples of 5)

Owner: Step-2 lead. Status: Lemma MC1 **PROVED** (rigorous, audited below).
Last updated 2026-06-19.

This is the task-listed "minimal-counterexample reduction" route. It does NOT
close (H2), but it rigorously narrows the class of graphs for which (H2) must be
proved, giving extra structure (edge-criticality) to exploit.

## Setup

Suppose `a(5n) <= n^2` FAILS. Base cases `n <= 6` hold (data + Step 1), so the
minimal failing `n0 >= 7` exists. Among triangle-free graphs on `5 n0` vertices
with `beta >= n0^2 + 1`, let `G` be one with the **fewest edges**.
By minimality of `n0`: `a(5(n0-1)) <= (n0-1)^2`.   (*)

## Lemma MC1 (structure of a minimal counterexample) — PROVED

(a) **`beta(G) = n0^2 + 1` exactly.**
(b) **Every edge is `beta`-critical:** `beta(G - e) = beta(G) - 1 = n0^2` for
    every edge `e`.
(c) **Minimum degree `>= 2`** (no pendant vertices).

### Proof
*Edge deletion moves beta by at most 1.* `beta = e - maxcut`. Deleting an edge
lowers `e` by 1 and lowers `maxcut` by 0 or 1, so
`beta(G-e) ∈ {beta(G), beta(G)-1}`.                                    (1)

*(a),(b).* For any edge `e`, `G-e` is triangle-free on `5 n0` vertices with fewer
edges than `G`; by edge-minimality it is NOT a counterexample, so
`beta(G-e) <= n0^2`. Combined with (1) and `beta(G) >= n0^2 + 1`:
`beta(G-e) >= beta(G) - 1 >= n0^2`, hence `beta(G-e) = n0^2` and (from (1))
`beta(G) = n0^2 + 1`. This holds for every `e`, giving (a) and (b).

*(c).* Suppose `v` is a pendant, edge `vu`. Colour `v` opposite `u`: `v` is never
forced monochromatic, so `beta(G) = beta(G - v)`. Deleting `vu` isolates `v`, so
`beta(G - vu) = beta((G-vu) - v) = beta(G - v) = beta(G)`. This contradicts (b)
(`beta(G-vu)` should be `beta(G)-1`). So no pendant; `delta(G) >= 2`. ∎

### Audited consequences
- Removing any single vertex `v`: `beta(G) <= beta(G-v) + floor(deg(v)/2)` and
  `beta(G-v) <= beta(G)`, and for a degree-2 vertex `v` (neighbours `u,w`,
  non-adjacent by triangle-freeness) criticality of `vu` forces
  `beta(G-v) = beta(G) - 1 = n0^2`.
- Every edge of every component is `beta`-critical within its component
  (restrict (b): for `e` in component `H`, `beta(H-e)=beta(H)-1`).
- **Connectedness is NOT established** and is NOT needed: a disconnected
  minimal-edge counterexample is a priori possible because the `beta`-excess
  `n0^2+1` can split across several non-bipartite components (e.g.
  `beta(H_1)+beta(H_2)=n0^2+1` with neither component alone `>= n0^2+1`), so
  padding a single component need not yield a smaller counterexample. [Earlier
  draft claimed connectedness via such padding — that argument is INVALID and was
  removed. Audit caught it.] The peeling reduction below does not use
  connectedness.

## How MC1 feeds the Peeling Lemma

The Peeling Lemma (H2) applied to this `G` would give a 5-set `S` with
`beta(G-S) >= beta(G) - (2 n0 - 1) = (n0^2 + 1) - (2 n0 - 1) = (n0-1)^2 + 1`.
But `G - S` is triangle-free on `5(n0-1)` vertices, so by (*)
`beta(G-S) <= a(5(n0-1)) <= (n0-1)^2 < (n0-1)^2 + 1`. Contradiction. Hence:

> **It suffices to prove (H2) for the restricted class:** connected,
> edge-`beta`-critical, triangle-free graphs `G` on `5n` vertices with
> `beta(G) = n^2 + 1` and `delta(G) >= 2`.

Equivalently, we must show: **no connected edge-`beta`-critical triangle-free
graph on `5n` vertices has `beta = n^2 + 1` while every 5-vertex deletion drops
`beta` by at least `2n` (i.e. `beta(G-S) <= n^2 - 2n + 1 = (n-1)^2` for all
`|S|=5`).** This is a sharper, more structured target than raw (H2); the
edge-criticality (every edge in a "tight odd structure") is the new leverage,
to be combined with the stability picture (`G` should be forced close to
`C5[n]`, which has `beta = n^2` not `n^2+1`, so the `+1` excess must localise —
a contradiction with criticality is the hoped-for endgame).

## Lemma MC2 (no-light-boundary) — PROVED (from GPT-Pro Q1, independently audited)

For the minimal-edge counterexample `G` (`β(G)=n0^2+1`):

(a) **Every 5-set `S` has `e(S, V∖S) >= 4 n0 - 2`** (and `>= 4 n0` if `G[S]` is
    not `C5`).
(b) **The 5 lowest-degree vertices have degree-sum `>= 4 n0 - 2`**; hence at most
    4 vertices have degree `< (4 n0 - 2)/5 ≈ 0.8 n0`.

### Proof
*Minimality consequence.* For any 5-set `S`, `G-S` is triangle-free on
`5(n0-1)` vertices, so `β(G-S) <= a(5(n0-1)) <= (n0-1)^2`. Hence
`Δ(S) = β(G)-β(G-S) >= (n0^2+1)-(n0-1)^2 = 2 n0`.                       (★)

*Greedy/extension bound (Lemma 4, GPT eq 23, re-derived).* Fix an internal
2-colouring of `S` achieving `β(G[S])` monochromatic internal edges; its global
flip keeps internal mono unchanged, and each external edge of `S` is monochromatic
in exactly one of the two orientations, so the better orientation has `<=
⌊e(S,V∖S)/2⌋` external mono. Therefore
`Δ(S) <= ⌊e(S,V∖S)/2⌋ + β(G[S])`. For triangle-free `G[S]` on 5 vertices,
`β(G[S]) = 1` if `G[S]≅C5`, else `0`.                                   (★★)

Combining (★),(★★): `2 n0 <= ⌊e(S,V∖S)/2⌋ + β(G[S]) <= ⌊e(S,V∖S)/2⌋ + 1`, so
`e(S,V∖S) >= 4 n0 - 2` (and `>= 4 n0` when `β(G[S])=0`). For (b), take `S` = 5
lowest-degree vertices; `e(S,V∖S) = Σ_{v∈S} d(v) - 2 e(S) <= Σ_{v∈S} d(v)`, so
`Σ_{v∈S} d(v) >= e(S,V∖S) >= 4 n0 - 2`. ∎

**Audit note.** GPT's downstream Lemma 5 (`d(u)+d(v) >= 8n/5+2`) is REJECTED —
its proof bounds `Σ_{w∈T} d(w)` from above using a quantity that is actually a
lower bound (the `R(3,3)` triple has degrees `>= 4n/5` each). MC2(a),(b) are the
correct, kept consequences. See `gpt_pro_consultations/Q1_ANSWER_AND_AUDIT`.

## Lemma MC3 (two-dominating C5 / root defect) — PROVED (from Q1, audited)

If `G` (triangle-free, `5n` vertices) contains an induced `C5` `s_0..s_4` such
that every `v∉S` has exactly two (necessarily nonconsecutive) neighbours in `S`,
then partitioning `V_i = {s_i} ∪ {v: N_S(v) = {s_{i-1},s_{i+1}}}` forces (by
triangle-freeness) all edges to run between consecutive `V_i`; so `G` is a
spanning subgraph of a `C5`-blow-up and
`β(G) <= min_i e(V_i,V_{i+1}) <= min_i |V_i||V_{i+1}| <= n^2` (last step = BU3,
`Σ|V_i|=5n`). Hence **a minimal counterexample has no 2-dominating induced C5.**
Root defect `def(S) = Σ_{v∉S}(2 - d_S(v)) = 10n-10 - e(S,V∖S) >= 0`; `def(S)=0`
⟺ 2-dominating. **Stability program (route f):** find an induced `C5` of BOUNDED
root defect, then exact-enumerate only the `def(S)` defect vertices.

## Lemma MC4 (Frozen-pair reformulation) — PROVED equivalent (from Q1, audited)

> **a(5n) <= n^2  ⟺  no frozen pair:** there is NO triangle-free `H` on `5n`
> vertices with `β(H)=n^2` and a nonedge `uv` (automatically `N(u)∩N(v)=∅` by
> triangle-freeness) such that `u,v` lie on the SAME side in EVERY maximum cut of
> `H`.

*Proof.* (⟸) If such `(H,u,v)` existed, then in `G=H+uv` every optimal cut of `H`
keeps `uv` monochromatic, so `β(G)=β(H)+1=n^2+1`, a counterexample. (⟹) In a
minimal-edge counterexample `G`, every edge `e=uv` is critical with `β(G-e)=n^2`
(MC1), and `β(G)=n^2+1` forces `u,v` together in every optimal cut of `H=G-uv`
(else some optimal cut of `H` separates them, extends to `G` without making `uv`
mono, giving `β(G)=n^2`). ∎

This is a **rooted** equivalent — amenable to Codex's rooted-cut / SAT machinery
(see HANDOFF_TO_CODEX). It avoids any global extremal classification.

**Cold-review vs the C5[n] equality case (passes).** The extremal `C5[n]` has
`β=n^2`, but (i) it is **maximal triangle-free** — every nonedge (two vertices in
one part, or in nonconsecutive parts) has a common neighbour, so adding any edge
makes a triangle; and (ii) it has **no codegree-0 nonedge** (within-part nonedges
have codegree `2n`; nonconsecutive-part nonedges have codegree `n`). So the
frozen-pair hypothesis is VACUOUS on `C5[n]`, and `C5[n]` cannot be the `H=G-uv`
of any counterexample. Hence MC4 is consistent with the extremal family, and
moreover any counterexample template `H` is a **non-maximal** triangle-free graph
with `β=n^2` possessing a special codegree-0 nonedge — structurally DISTINCT from
`C5[n]`. This sharpens the search target: not `C5[n]`-like graphs, but `β=n^2`
graphs that are strictly extendable at a codegree-0 nonedge.

## Lemma MC5 (counterexample is medium/high density) — PROVED

For any triangle-free `G` with `β(G) = b`: since every graph has a cut taking
`>= e/2` edges, `maxcut(G) >= e(G)/2`, so `b = e - maxcut <= e/2`, i.e.
`e(G) >= 2 b`. For a counterexample on `5n` vertices (`b = n^2+1`):
```
e(G) >= 2 n^2 + 2,   average degree = 2e/(5n) >= (4n^2+4)/(5n) >= 4n/5.
```
- This **cross-checks MC2** (which gave, by a different route, that all but `<=4`
  vertices have degree `>= (4n-2)/5 ≈ 0.8n`): here the AVERAGE degree is `>= 0.8n`.
- **Density window.** Edge density `d = 2e/N^2` (`N=5n`) satisfies
  `d >= (4n^2+4)/(25n^2) -> 4/25 = 0.16`. ⚠️ The further claim that BCL confines a
  counterexample to the window `(0.2486, 0.3197)` is **ASYMPTOTIC ONLY**: BCL
  Thm 1.3 (the low/high-density `n^2/25` bounds) holds "for n >= n0" with n0
  unspecified (verified verbatim 2026-06-20; see ledger DEP-a25). So the window
  placement is valid only for large `n`, not finite `n`. The unconditional finite
  fact is just `e >= 2n^2+2` (density `>= 0.16`); the medium-window refinement is
  asymptotic context, consistent with (H2)/frozen-pair sitting in the open
  medium-density regime, and closes nothing.
- **Toward an induced C5.** A `{C3,C5}`-free non-bipartite graph has odd-girth
  `>= 7`; such graphs cannot simultaneously be this dense AND have `β = Θ(n^2)`
  (long-odd-girth graphs are far-from-dense-when-far-from-bipartite — NOT yet
  proved here; this is the gap the MC3 stability route must cross to guarantee an
  induced C5). OPEN sub-question handed to GPT Q2.

## Lemma C5HOM (homomorphic-to-C5 ⟹ β ≤ n²) — PROVED (finite, exact)

If a triangle-free graph `G` on `5n` vertices admits a graph homomorphism
`φ: G → C5`, then `β(G) <= n^2`.
*Proof.* Let `V_i = φ^{-1}(i)` (`i ∈ Z/5`); since `φ` is a homomorphism every edge
of `G` runs between consecutive classes `V_i, V_{i+1}`. So `G` is a spanning
subgraph of the blow-up `C5[|V_0|,...,|V_4|]`. The near-proper 2-colouring of
`C5` (classes `A=V_0∪V_2∪V_4`, `B=V_1∪V_3`) leaves monochromatic only the
super-edge `(V_0,V_4)`, so `β(G) <= e_G(V_0,V_4) <= |V_0||V_4|`; minimising over
which super-edge to leave mono, `β(G) <= min_i |V_i||V_{i+1}| <= n^2` (BU3,
`Σ|V_i| = 5n`). ∎

**This is the exact lever the min-degree program would need.** Combined with a
hypothetical "triangle-free + `δ > cN` ⟹ homomorphic to C5" it would prove the
conjecture for `δ > cN` (and repair the BCL high-density base-case gap finitely).
BUT the known min-degree theorems fall just short: AES gives `δ>2N/5 ⟹ BIPARTITE`
(hom to K2, even better — but `β=0` is trivial there), while Jin's `δ>10N/29`
gives only **3-colourability** (hom to K3), which does NOT factor through C5 and
does NOT bound `β` (C5[n] itself is 3-colourable with `β=n^2`). The gap between
"3-colourable" and "homomorphic-to-C5" is exactly where the medium-density
difficulty lives. (Ready to deploy if a finite hom-to-C5 min-degree bound is
found.)

## Lemma MC6 (Andrásfai–Erdős–Sós min-degree cap) — PROVED (finite, exact)

By Andrásfai–Erdős–Sós (1974): every triangle-free graph on `N` vertices with
`δ > 2N/5` is BIPARTITE (`β=0`). A counterexample `G` (`β=n^2+1>0`) is
non-bipartite, so `δ(G) <= 2N/5 = 2n` (`N=5n`). This is an EXACT finite theorem
(no asymptotics), unlike BCL. Complements MC2 (all but `<=4` vertices have degree
`>= 0.8n`): a counterexample has all degrees in roughly `[0.8n, 2n]` with one
`<= 2n`. NOTE: Jin (1995) `δ>10n/29 ⟹ 3-colourable` does NOT help here
(3-colourable allows `β=n^2`, e.g. `C5[n]` itself); and no clean finite
`δ>cN ⟹ homomorphic-to-C5` bound (which WOULD give `β<=n^2`) was found.
AES is also the finite tool offered to Codex to replace BCL's "non-bipartite ⟹
low-degree root" step (HANDOFF), though it does not give BCL's edge-range cut.

## Status / next
- MC1, MC2, MC3, MC4, MC5, MC6 PROVED & audited (MC2/3/4 from GPT-Pro Q1, independently
  re-derived; MC5 elementary). Ledger C10, C12, C13, C14, C15.
- Live target: the Frozen-pair saturation statement (MC4) — prove that in any
  triangle-free `β=n^2` graph, every codegree-0 nonedge is separated by some
  optimal cut. Use MC2 (high boundary), MC3 (no 2-dominating C5), and a
  bounded-defect-C5 + finite cleanup.
- REJECTED (do not use): GPT Lemma 5 (edge degree-sum), GPT eq (7) closed form.
