# H2 / MC4 core attack — findings (workflow wf_ff5f1a5a-420, 2026-06-20)

A 9-strategy, adversarially-verified multi-agent attack on the peeling lemma H2 and
its frozen-pair equivalent MC4. **No proof of H2** (0 confirmed proofs). But it
produced one verified new lemma, several decisive method-class dead-ends, one
conditional lemma, and a sharp unifying obstruction. Step-2 INDEPENDENTLY
re-verified the headline lemma (below).

## ★ NEW PROVED LEMMA — MERGE-PRESERVES-BETA  (independently verified by Step-2)
Let `H` be a graph, `uv` a NONEDGE with codegree 0 (`N(u) ∩ N(v) = ∅`), such that
SOME maximum cut of `H` places `u,v` on the same side. Form `H'` by identifying
`u,v` into one vertex `w` with `N(w)=N(u) ⊔ N(v)`. Then **`β(H') = β(H)` exactly.**

Proof (airtight, both directions; Step-2 re-derived):
- codeg-0 ⟹ the edge map is a bijection, `e(H')=e(H)` (no doubled edge). LOAD-BEARING.
- (≤) push a common-side max cut `σ` (`u,v∈X`) to `σ'=(X∖{u,v}∪{w},Y)`: every edge
  keeps both endpoints' sides, so `mono(σ')=mono(σ)=β(H)` ⟹ `β(H')<=β(H)`.
- (≥) pull any `β(H')`-optimal cut back, giving `u,v` the side of `w`: `mono` preserved
  ⟹ `β(H)<=β(H')`.
The common-side hypothesis is NECESSARY (without it, merge can RAISE β `0→1`).
**Step-2 independent check:** 0 violations over 15 717 codeg-0 + common-side pairs
across ALL triangle-free graphs on 7,8,9 vertices (`merge` re-implemented from
scratch). Status: **PROVED + VERIFIED.**

## NEW PROVED LEMMA — STRICT SINGLE-FLIP
If a codeg-0 nonedge `uv` is frozen on the same side in EVERY max cut of triangle-free
`H`, then in every max cut `2·m(u) < c(u)` and `2·m(v) < c(v)` (m=mono-degree,
c=total degree): else flipping `u` alone (mono change `c(u)-2m(u) <= 0`) yields another
max cut SEPARATING `u,v`, contradicting frozenness. Verified 0/26646 frozen pairs N≤10.

## DECISIVE DEAD-ENDS — method-classes that PROVABLY cannot give the exact constant
(These prune future effort. All have explicit witnesses; none adversarially re-verified
but each is a concrete refutation, high confidence.)
- **SDP / convex (Strategy 4, conf 93):** `β=e−MaxCut`; upper-bounding β = lower-bounding
  the MaxCut MAXIMISATION, but convex weak duality only UPPER-bounds a maximisation, so
  every SDP value LOWER-bounds β (wrong direction). On `C5[n]`, `SDP_MaxCut=4.52254n²`,
  GW rounding gives `3.973n² < 4n²` (C5 is the GW-tight graph); best triangle-free GW
  `0.884` gives `3.998n²<4n²`. No MaxCut-SDP scheme reaches the exact constant.
- **Spectral (Strategy 7):** β is NOT an adjacency-spectral invariant — explicit
  cospectral triangle-free pair on N=12, e=22 with β = 3 vs 4 (all eigenvalues agree to
  1e-15, so all `trace(A^k)` incl. `#C5=trace(A^5)/10` agree). Cospectrality persists
  under blow-up (`A(G[t])=A(G)⊗J_t`), so the obstruction holds in the `n²` regime.
- **Local-count / flag (Strategy 9):** β is NOT a function of subgraph counts up to `C6`
  (odd-girth is invisible to bounded-length counts) — explicit same-profile pairs with
  β 0 vs 1. Any exact local certificate must be ASYMPTOTIC (as BCL is).
- **Weighted symmetrization (Strategy 3):** any vertex-partition quotient β `>= β`
  (relaxation makes the target HARDER); vertex-cloning is NOT β-monotone (strict decrease
  on ~24% of triangle-free graphs); `C5` is rigid (every clone drops β `1→0`).

## REFUTED specific ideas
- **Uniform 5-set averaging (Strategy 1):** for a fixed max cut, `E[mono_S] = 2n(5n-3)/
  (5n-1) → 2n − 4/5 > 2n−1`. Overshoots the target by ~1/5 for ALL n. (And `mono_S` is a
  LOWER bound on `pc(S)`, wrong direction.)
- **Induced-C5 measure averaging (Strategy 6):** REFUTED by a concrete witness — a
  triangle-free graph on N=15 (n=3), `β=6` (in the nontrivial band `2n<=β<=n²`), 103
  induced C5's, with `E_mu[pc]=5.32 > 5 = 2n−1`. Also a logic fix: H2 must hold for ALL
  `G` on 5n, and is trivial when `β<=2n−1` (then `pc<=β<=2n−1`); the nontrivial band is
  `2n <= β <= n²`.

## CONDITIONAL lemma — WYZ low-codegree extraction (NOT yet verified)
Strategy 2: every triangle-free `G` on `5n` with `β>=n²+1` has a nonedge of codegree
`<= ⌊5n/8⌋`. Proof modulo **Wang–Yang–Zhao arXiv:2408.05547** (codeg `> N/8` ⟹
homomorphic to C5) + C5HOM. This is the general-n lift of Codex's n=30 lemma V10.
CAVEAT: WYZ's `N/8` threshold is SHARP (Wagner/Möbius-ladder `M8` blow-up is
triangle-free, non-hom-C5, codeg `N/8`, `β=(25/32)(N/5)²` = 78% of target), so codegree
ALONE cannot bridge `N/8 → N/5`; must combine with another route. **ACTION: independently
verify WYZ exists and is finite-N (not asymptotic) before relying on it.**

## THE UNIFYING OBSTRUCTION
Upper-bounding `β` = lower-bounding `MaxCut` = exhibiting a near-optimal cut. The needed
quantity is the cut RE-ALIGNMENT gain after peeling, and `C5[n]` sits at EVERY static
threshold simultaneously (GW-tight 0.878, WYZ codeg-threshold-sharp, GW gap 1.13,
odd-girth-blind). So all value/spectral/local/convex certificates fail; only a route that
captures realignment (the merge lemma, or a stability/robust-extremal argument) can work.

## MOST PROMISING NEXT STEPS (from synthesis + completeness critic)
1. **Stability / robust-extremal framing** (biggest omission): near-extremal `G` (β close
   to n²) is structurally close to `C5[n]`; split FAR (β<n² with finite margin, peel
   greedily) vs CLOSE (transversal-C5 peeling + finite correction). Natural home for the
   merge lemma. Needs a FINITE stability constant (BCL is asymptotic; BU3 uniqueness may
   give it directly).
2. **Extremality-conditioned triangle-safety** (cheap, decisive): the merge route's only
   gap is that merging a frozen pair can create a triangle. Nobody conditioned on `β=n²`.
   Enumerate triangle-free graphs with `β=(small n)²` having a frozen codeg-0 pair; test
   whether SOME such pair is always triangle-safe. If yes-at-extremality, the merge route
   may close. Also extract the PAIR-FLIP inequality (frozen ⟹ flipping u,v together is
   non-improving) coupling u,v through the cross-edges that create triangles.
3. **Verify WYZ**; combine WYZ (high-codeg ⟹ hom-C5) with merge/extraction (low-codeg).
4. **Entropy / probabilistic cut construction** — lower-bounds MaxCut DIRECTLY (the
   correct direction, the one thing all 9 strategies lacked).

---

# H2 core attack — SECOND workflow (wf wbnn6tj9s, 2026-06-20) + Step-2 verification

6-attack adversarial workflow. **Again 0 confirmed proofs of H2.** One genuinely new
proved lemma, several sharper obstructions, and a synthesis/critic CONTRADICTION that
Step-2 resolved by exact computation (below).

## ★ Step-2 DECISIVE VERIFICATION — H2 is TRUE & TIGHT at C5[n] (critic REFUTED)
`bridge/experiments/verify_h2_5set_c5n.py` — exact brute MaxCut over ALL C(5n,5)
5-sets of C5[n], `min_S [β(C5[n]) − β(C5[n]−S)]`:

| n | β | target 2n−1 | **min drop** | mean | max | #minimizers |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | **1** | 1.00 | 1 | 1 = 1⁵ |
| 2 | 4 | 3 | **3** | 3.87 | 4 | 32 = 2⁵ |
| 3 | 9 | 5 | **5** | 7.19 | 9 | 243 = 3⁵ |

- **min 5-set drop = 2n−1 EXACTLY** ⟹ H2 holds with EQUALITY at the extremal family.
  The synthesis (Attack 6 "diagonal S → 2n−1, tight") is RIGHT; the completeness
  critic's "all 220 5-sets of C5[2] drop 4 → H2 FAILS at C5[2]" is **WRONG** — its
  harness still had a MaxCut bug (it even miscounted C(10,5)=252 as 220). The min is 3.
- **Minimizers = exactly n⁵ C5-transversals** (one vertex per part). Removing one turns
  C5[n] into C5[n−1] (rigorous), dropping β by n²−(n−1)²=2n−1. So the RIGHT peeling
  object is a "blown-down C5", linking H2 to the C5-hom structure (Attack 6), NOT to
  single-vertex/one-root certificates.
- **Averaging/LP route is DEAD** (critic idea #3 refuted): H2 needs min ≤ 2n−1, but the
  mean drop (3.87, 7.19) is STRICTLY ABOVE 2n−1 for n≥3, so no lower-bound-on-mean
  argument can deliver the minimum (only an n⁵-thin family achieves it). Confirms the
  first workflow's Strategy-1 refutation (E[mono]→2n−4/5 > 2n−1).

## NEW PROVED LEMMA (Attack 3) — Deletion-saturation  (= V1 iterated + f)
For triangle-free G on M vertices and any vertex v: `β(G)=β(G−v)+d(v)−g_v`,
`g_v∈[⌈d/2⌉,d]`, hence `β(G) ≤ f(M−1)+⌊δ/2⌋` where `f(M)=max β over triangle-free
M-vtx graphs`. (Sound: β=e−MaxCut; e drops by d(v); MaxCut(G)≥MaxCut(G−v)+⌈d/2⌉. This
is exactly Codex PROOF_STATE V1, already audited SOUND, plus the definition of f.)
With AES `δ≤2n` ⟹ `f(5n) ≤ f(5n−1)+n`, so #23-at-5n FOLLOWS from `f(5n−1) ≤ n²−n`.
Exact f(5..13)=1,1,1,2,2,4,4,5,6 (workflow data; not separately re-counted).
**OFF-BY-ONE, wrong granularity:** single-vertex deletion has ZERO slack at C5[n]
(g_v=n=d/2), so this reduction provably cannot close the unit gap; and f(12)=5 >
blowup(12)=4 means f(5n−1)≤n²−n is itself a non-multiple-of-5 instance of the same
hard problem. Keep as a TOOL, not a path. (Superseded by the tight 5-set H2 above.)

## SHARPER OBSTRUCTIONS (all rigorous, this workflow)
- **Σ_v S_v = Q** (handshake): the flat-averaged one-root bound = the radius-2 scalar
  relaxation = the documented 1/16 dead end. Aggregating one-root by a UNIFORM weight
  cannot beat 1/17.2.
- **Deficiency anti-correlates with realignment gain** (corr −0.39..−0.46); C5[n] has
  total codegree-deficiency 0. So GPT Q8's "deficiency-sum → gain" frontier has the
  WRONG SIGN. The C-S slack lives in the band 1.25n²<e<5n² (C5[n] on the upper edge).
- **Per-ball A7 is circular** (Attack 5): the smallest c with β(H)≤|H|²/c over all
  triangle-free H is c=25 (= the conjecture); A7's c=32 is the wrong direction; C5[n]
  has diameter 2 so every radius-2 ball = whole graph (contains C5). Dead.
- **C5-hom cut is correct-but-circular** (Attack 6): optimizing over all homs+colorings
  recovers MaxCut exactly but only reproves WYZ/C5HOM territory; the hard core is the
  NON-C5-hom triangle-free graphs (Petersen β=3, Grötzsch β=5), where a near-hom must
  deviate on a set S and the deviation-cost ≤ gain accounting IS H2 again.

## Step-2 H2-COUNTEREXAMPLE SEARCH at n=3 (native MT C++, `h2_ce_search.cpp`)
Tested **794,500** triangle-free 15-vtx graphs with β≥6 (random-maximal + β-hill-climbed
+ all C5-blowup compositions + Petersen+5 and Grötzsch+4 NON-C5-hom hard cores + their
hill-climbs): **0 H2 violations**, worst `min_S drop − (2n−1) = 0` (i.e. every graph has a
5-set with drop ≤ 2n−1, worst-case TIGHT). β-distribution b6=679270/b7=114358/b8=387/b9=485.
Strong evidence H2 is TRUE at n=3 across the hard core; β=8 thinly sampled (387) — the
focused workflow's structured red-team graphs target that gap. Flexible exact verifier
`h2_check_edgelist.cpp` (validated on C5[3]: β=9, min drop=5) machine-checks any explicit
candidate. (3rd focused workflow wf_67b8bb6b-50e: results pending.)

## NET after two workflows
H2 remains OPEN for arbitrary triangle-free G, but is now PINNED DOWN: it is TRUE and
TIGHT at C5[n] (min drop 2n−1 via C5-transversal → C5[n−1]); the only viable route is a
STRUCTURAL existence argument for a near-C5-transversal good 5-set (NOT averaging, NOT
single-vertex, NOT per-ball, NOT uniform-aggregate — all rigorously excluded). The
live frontier = couple WYZ (high-codeg ⟹ hom-C5, peel a real C5-transversal) with a
deviation/extension inequality on the non-hom exceptional set (the honest medium-density
Erdős #23 core; do NOT fabricate).

---

# H2 — THIRD focused workflow (wf_67b8bb6b-50e, 2026-06-20) + Step-2 machine-check

Sharpened 6-angle attack (4 theory + 2 red-team), each adversarially verified; Step-2
INDEPENDENTLY machine-checked every candidate graph with `h2_check_edgelist.exe`.
**Still 0 proofs of H2.**

## Verdicts (after adversarial verification)
- **discharging — REFUTED.** Claimed H2 ⟺ a separable "deficiency" condition
  `drop(T) ≤ Σ_t min(e(t,X'),e(t,Y')) + (e(H_T)−maxcut(H_T))`. FALSE: the decomposition
  lets each t∈T optimize external and internal edges independently, but one side-choice
  serves both and they CONFLICT, so it overcounts the gain (explicit 8-vtx witness:
  drop=1 > formula=0; 9248/27776 failing pairs). The "=2n−1 at C5[n]" calibration held
  only because the conflict vanishes for an EXACT transversal — camouflaging the error.
- **stability — OBSTRUCTION** (and its "Branch B is easy" step refuted: deficiency CANNOT
  be added to the 2n−1 budget; the hard band is ALL of (2n−1, n²], not an o(n²) shell).
  The needed enabler = an EFFECTIVE (explicit ε,C) WYZ/BCL stability theorem for relative
  deficiency→0; NOT in the literature, plausibly tower-type.
- **nonhom-deviation — PARTIAL (valid but not new).** Clean "Lightest-Link Lemma": G hom
  to C5 with fibers V_i ⟹ delete the min link E*=min_i e(V_i,V_{i+1}) ⟹ G−E* hom to P5 ⟹
  bipartite ⟹ β ≤ E* ≤ min_i n_i n_{i+1} ≤ n² (AM-GM). Verified 2000/2000 + 400/400. But
  this only re-proves the known C5HOM bound; does NOT touch the non-hom core.
- **min-counterexample — PARTIAL.** Threshold-Drop Obstruction `T(5n)−T(5n−1)=n` ⟹ MERGE
  strictly raises a minimal counterexample's excess over the residue threshold ⟹ MERGE
  alone cannot close (true negative, consistent with the known triangle-safety gap).
- **redteam-A / redteam-B — OBSTRUCTION (no counterexample).** redteam-A claims a CERTIFIED
  EXHAUSTIVE negative over ALL 286,699 triangle-free 15-vtx graphs with ≥42 edges, 0
  breakers (agent-claimed geng enumeration; NOT independently re-run by Step-2 — provenance
  noted). 14 explicit candidate graphs produced.

## ★ Step-2 INDEPENDENT MACHINE-CHECK of all 14 candidates (`h2_check_edgelist.exe`)
ALL 14 confirmed triangle-free; ALL β-values match the agents' claims EXACTLY (agents'
harness correct THIS round); **H2 holds for every one.** Key NEW n=4 (N=20) data on the
genuine NON-C5-hom hard core (target 2n−1=7):
- **Petersen[2]** (non-C5-hom), β=12, **min 5-set drop = 5 < 7** ✓ (slack 2)
- **Cay(Z20,{1,4,9})** (vertex-transitive), β=12, **min drop = 5 < 7** ✓
- **C5[4]−1edge** (near-extremal), β=15, **min drop = 6 < 7** ✓ (slack 1)
- Cay(Z15,{1,4,6}), Cay(Z15,{2,3,7}): both ≅ C5[3] (β=9, drop=5 tight); 4×C5: β=4 trivial.
- **★ C5[4] itself** (Step-2 added, `c5_4.txt`): β=16=n², **min 5-set drop = 7 = 2n−1
  EXACTLY** — extends the headline "H2 true & TIGHT at C5[n]" result to n=4.
So H2 verified to HOLD on every non-hom / vertex-transitive / near-extremal hard core at
n=4, tight only at C5[4]. No counterexample at n=2 (exhaustive), n=3 (794500 + agent's
286699-graph claim), or n=4 (structured hard core).
**Step-2 BULK n=4 search (`h2_ce_search_param.cpp`, N=20):** all C5[4] blowup compositions
(worstMargin=0) + **16,143 high-β (β 8–16) tri-free 20-vtx graphs** (random-maximal +
β-hill-climbed + Petersen[2] perturbations): **0 H2 violations, worst margin 0** (tight only
at C5[4], β=16). β-hist b8=2716/b9=3218/b10=3044/b11=1839/b12=5309/b13=16/b16=1 (random
rarely reaches the near-extremal b14,15 — those checked directly via C5[4]−edge β=15 drop=6).

## Surviving honest reformulation (rigorous but ≈tautological; SUFFICIENT only)
`β(G) ≤ β(G−T) + [e(T,V) − gain_T^joint(X',Y')]` for any 5-set T and any optimal cut
(X',Y') of G−T, where gain_T^joint = max edges cut by JOINTLY placing all of T into
(X',Y') (NO decomposition). One line from MaxCut(G) ≥ MaxCut(G−T)+gain_T^joint. So a
SUFFICIENT condition for H2: ∃ near-C5-transversal T with `e(T,V)−gain_T^joint ≤ 2n−1`.
(NOT equivalent to H2 — G's optimal cut may realign the G−T part, making the true drop
smaller; this bound can be loose. The discharging error was separating gain_T^joint.)

## FOURTH workflow (barrier: density-B + effective-stability + red-team, wf_d5aec945, 2026-06-20)
Launched after the GPT Q9 Clebsch reduction. **0 proofs** (all 5 angles obstruction/refuted).
Step-2 machine-verified the key candidates (`h2_check_edgelist.exe`). Net:
- **Deliverable B (density<0.32 ⟹ β<n²) is DEAD via MaxCut surplus** (verifier is_valid=TRUE — a
  rigorous NEGATIVE). β=e/2−surplus; β≤N²/25 needs surplus ≥ a CONSTANT fraction of e in the band,
  but the only triangle-free surplus theorem (Alon) gives MaxCut−e/2 = Θ(e^{4/5}) = o(e) — sublinear,
  a vanishing fraction. The missing ingredient = a constant-fraction surplus for dense triangle-free
  graphs = effective stability ("β=N²/25 forces density≈0.4"). Same wall as everything.
- **★ NEW PROVEN L3 master bound** (verifier-airtight, 0/2380, tight at C5[n]): deletion lemma
  `β(G−D) ≤ β(G) ≤ β(G−D)+|D|`; hence for every C5-coloring φ:V→Z₅ with deviation-edge set D_φ,
  `β(G) ≤ |D_φ| + min_i e_{G−D_φ}(V_i,V_{i+1})`, so **#23 ⟺ min_φ[|D_φ| + min-link] ≤ n²** ("RI*").
  This is the **C5-version of GPT Q9's Clebsch τ_K reduction** (Clebsch refines it with 5 cuts+parity).
  Clean, unconditional, "worth formalizing in Lean" — but RI* itself is "as hard as #23" (unproven).
- **Band-extremal data (VERIFIED):** the `h8[k]` family (density 0.3125, in band) has β=2k², N=8k,
  ratio β/(N²/25)=50/64=**0.781**; N=15 redteam β=7 (ratio 0.778). So band-extremal triangle-free
  graphs reach only ~78% of the conjecture boundary N²/25 — the band is "safe" (corroborates the
  β-vs-density profile + CF margins). NOT a proof (finite; the finite→∞ extrapolation is the gap).
- Concavity/usc of φ(W)=t_edge−MC on graphons is TRUE but useless (max is interior, not extreme-point;
  Lagrangian extreme-point step refuted). Lagrangian-blowup route dead.

**Convergence:** both the Clebsch τ_K route (Q9) and the C5 master-bound route (this workflow)
reduce #23 to the SAME object — a "deviation/frustration ≤ budget" inequality (CF / RI*) — and both
bottom out at the SAME wall: an effective constant-fraction MaxCut surplus / stability for dense
triangle-free graphs. CF (the Clebsch refinement) is the more concrete, flag-algebra-amenable form.

## NET after three workflows
H2 is now empirically TRUE wherever checkable (n≤4 incl. the non-hom hard core) and TIGHT
only at C5[n]; every static/separable/averaging certificate is rigorously excluded; the
sole route is a STRUCTURAL existence proof of a low-joint-imbalance near-C5-transversal,
which needs an effective (explicit-constant) stability theorem for triangle-free MaxCut
near C5[n] — a research-grade open problem (only BCL-asymptotic exists). GPT brief Q9 (the
realignment crux) queued. DO NOT fabricate; the medium-density core stays open.
