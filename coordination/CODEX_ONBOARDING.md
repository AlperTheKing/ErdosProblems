# ONBOARDING — Codex × Claude Step-2 collaboration (Erdős #23)

Read this once, fully, before starting. It is separate from `CODEX_GOAL.md` (the goal). This explains the **current
state**, **definitions**, **files**, **how we coordinate**, and **what is already ruled out**. Write in English to
me (Claude Step-2) and to the user; the user may send Turkish, that's fine.

## 0. Important context you do NOT yet have
- **Step-1 is FINISHED and PUBLISHED.** The finite-N half — the exact certificate that `a(5n)=n²` (equivalently
  `β(G)≤N²/25` exactly) for all `N ≤ 200`, via an order-10 Horn-LP dual made exact in `Fraction` (δ = 4.7568e-5 <
  5e-5) — is done, independently double-checked, and shipped as the arXiv **v2** paper. **Do not redo Step-1.** You
  personally started Step-1 earlier but ran out of context; a *Claude* agent (not you) finished and published it.
- **Everything now is δ=0** (the "Γ-lemma" = the whole *remaining* conjecture). Reason: `d_mono(W_G) = 2β(G)/N²`
  holds **exactly** for every finite triangle-free G (blow-up multilinearity, no rounding), so proving δ=0 at the
  graphon/band level closes `β≤N²/25` for **all** finite N at once — no peeling, no separate finite obligation.
- **Where Claude Step-2 is right now:** δ=0 has been driven down to the single inequality in `CODEX_GOAL.md`. The
  full reduction is proven and 5×-exact-verified. I am currently consulting GPT-Pro on the proof of the crux (the
  load-balancing / flow-Hall angle). That is the live front.

## 1. The objects (exact definitions)
Fix a maximum cut of G. `B` = cut edges (bipartite, connected). `M` = **bad edges** = monochromatic edges (both
endpoints same side). Triangle-free ⟹ each bad edge `f=(a,b)` closes an odd cycle of length `ℓ(f)=d_B(a,b)+1 ≥ 5`
(`d_B` = distance in B). `Γ := Σ_{f∈M} ℓ(f)²`. The conjecture (δ=0) is **`Γ ≤ N²`** (⟹ `β=|M| ≤ Γ/25 ≤ N²/25`,
using ℓ≥5).

- `p_f(v)` = fraction of shortest a–b B-geodesics through v.  `p_f(v)∈[0,1]`, `Σ_v p_f(v)=ℓ(f)`.
  (Betweenness form, proven: `p_f(v)=σ_a(v)σ_b(v)/σ_ab`, σ = shortest-B-path counts.)
- Geodesic **layers** `I_i(f) = {v : d_B(a,v)=i, d_B(v,b)=ℓ(f)−1−i}`, i=0..ℓ(f)−1. Proven: `Σ_{v∈I_i(f)} p_f(v)=1`.
- `T(v) := Σ_g ℓ(g)p_g(v)` (load).  Proven (P1): `Σ_v T(v) = Γ`.   `S(v) := Σ_g p_g(v)` (incidence).
- `P[v,f]=p_f(v)`;  `O := PᵀP` (Gram, entrywise ≥0, `O_{fg}=⟨p_f,p_g⟩`);  `K := PPᵀ` (`K_{vw}=Σ_f p_f(v)p_f(w)`,
  row sums = `T(v)`, same nonzero spectrum as O).
- **CD (cut-domination, from max-cut):** `δ_M(A) ≤ δ_B(A)` for every vertex set A (`δ_X(A)` = #X-edges crossing ∂A).

## 2. The reduction (every step PROVEN; the file `ROWSUM_O_reduction.md` is the rigorous writeup)
`Γ≤N²  ⟸  ρ(O)≤N` (Rayleigh: `ℓᵀOℓ = Σ_v T(v)² ≤ N‖ℓ‖² = NΓ`, then Cauchy–Schwarz `Σ T² ≥ Γ²/N`).
`ρ(O)≤N  ⟸  ROWSUM-O` (Perron–Frobenius: O entrywise ≥0 ⟹ ρ(O) ≤ max row sum = max_f (O·1)_f).
`ROWSUM-O / ρ(O)≤N  ⟺  Layer-Price Feasibility  ⟺  (LPD)` (exact SOS identity `N·I−K = Σ_f(D_f − p_f p_fᵀ) +
(N·I − Σ_f D_f)`, `D_f(v)=b_{f,layer(v)} p_f(v)`; block PSD ⟺ harmonic, diagonal PSD ⟺ budget). All verified.

## 3. Files you will use (all under `problems/23/writeup/`, run with `python` — has numpy/scipy/fractions)
- **`_h.py`** — the helpers. `dec(g6)->(n,E)`, `loads(n,E)->info`, `GENG` (path to nauty geng.exe). USE THIS, **not**
  `census_GPI.py` (which runs a slow census on import). `info` keys: `n, adj, side, M, ell, cyc, T, Bset, Mset, G`.
  Census of all triangle-free connected graphs on n vertices:
  `subprocess.run([GENG,'-tc',str(n)],capture_output=True,text=True).stdout.split()`.
- **`_rowsum_verify.py`** — exact-rational ROWSUM-O verifier (mine; the trustworthy one).
- **`_layerprice.py` / `_layerprice_verify.py`** — solve the layer-price SOS feasibility (convex), extract prices,
  reconstruct `N·I−K` and check PSD. `layers_of(info,f)` returns the geodesic layers.
- **`_lpd_reform.py`** — verifies `(LPD)` and the reformulation `(LPD')` `⟨T−N,y⟩ ≤ Σ_f Σ_{i<j}(√w_{f,i}−√w_{f,j})²`.
- **`_loadbal.py`** — the load-balancing view (total budget ≥ Γ, spread over N vertices capped at N).
- **`_crofton_lp.py`, `_overlap_lp2.py`, `_dual_analysis.py`** — the REFUTED/CIRCULAR certificates (don't repeat).
- **`ROWSUM_O_reduction.md`** — the self-contained rigorous writeup of the reduction. Read it.
- GPT-Pro consult log: `gpt_pro_consultations/2026-06-27_sandwich_route_gamma_le_N2_CONSULT.md` (full trail).

## 4. What is ALREADY RULED OUT (do not re-attempt — each refuted with an exact witness)
- **CD endpoint-separation cut-metric / "Crofton" LP** — REFUTED (separating-cut multiplicity `m_f≥2` inflates;
  cuts cannot see the vertex-set overlap ⟨p_f,p_g⟩).
- **Combinatorial charging / double-counting** — PROVABLY dead (content is in the p_f measure weighting; every
  set/counting relaxation fails by large census margins).
- **Geodesic flow / Menger / LP-dual on incidence** — dead (collapses to the layer-cover overshoot, or circular).
- **Overlap-packing LP** (max Σ O_fg x_g, x_g≤1, Σ sep_A(g)x_g ≤ δ_B(A)) — CIRCULAR (trivial dual μ_g=O_fg, no cuts).
- **Per-cycle, per-layer, symmetric-pair, simple Cauchy–Schwarz / Gershgorin-on-vertices** — all FAIL (exact).
- The "sandwich" route `U_over ≤ HV_B ≤ U_under` — DEAD: passed census N≤11 but FAILS at an N=22 blow-up. **Lesson:
  stress every candidate inequality on blow-ups to N≥18–22 before trusting it.**

## 5. The live frontier (what a proof probably needs)
The crux is a global spectral anti-concentration fact, tight exactly on the odd-cycle blow-up extremals
`C_{2k+1}[t]` (where `T≡N`, `Γ=N²`). Promising directions, none completed:
- **KKT-core exclusion** (GPT): a counterexample to (LPD) is a maximizer `y` with induced budget `B_y(v) > N` on
  supp(y). Prove **no such "tight core" exists in a triangle-free CD configuration.**
- **Triangle-free mechanism:** the two endpoints of a bad edge have **disjoint B-neighborhoods** (a shared
  B-neighbor would be a triangle), so geodesics enter/leave each f-interval through *separated corridors*. This
  "corridor capacity" should force the harmonic price redistribution / bound the over-demand.
- **Load-balancing / flow-Hall:** total budget `Σ_v B(v) = Σ_f Σ_i b_{f,i} ≥ Γ` (Cauchy–Schwarz on harmonic); uniform
  prices give min total (=Γ) but concentrate it (max=`max_v T(v)>N`); feasibility = can spread it so every vertex
  ≤ N. Looking for a max-flow/min-cut where corridor-disjointness forces min-cut ≥ demand.
- **(LPD')** reduces on coordinate rays `y=e_v` to the easy `S(v)≤N`; the **interior/mixed-y** case is the whole
  content (the LHS is homogeneous-degree-1 *concave*, so the max is interior — not reducible to rays).
- **(CORR) / "Hellinger Hall" — the sharpest concrete target (GPT-Pro, 2026-06-27; verified exact by Claude).**
  Expanding `(Σ_i√w_{f,i})²` makes (LPD) equivalent to a **pair-demand ≤ vertex-slack** inequality:
  `Σ_f Σ_{i<j} √(w_{f,i}·w_{f,j}) ≤ ½·Σ_v (N − S(v))·y_v`  for all `y≥0`  (file `_corr_test.py`, holds, tight at
  extremals). GPT's proposed proof: a **corridor-allocation conic flow** — for each bad edge f and layer pair (i,j),
  route the Hellinger pair-demand `√(w_{f,i}w_{f,j})` through the **B-corridor vertices between layers I_i(f) and
  I_j(f)**, into vertex slack `(N−S(v))y_v`; feasibility for all y ⟹ (CORR) ⟹ (LPD). The allocation MUST depend on y
  (a fixed y-independent flow is too rigid — that's why ordinary subset max-flow/Hall fails). Triangle-freeness
  (disjoint B-neighborhoods of bad-edge endpoints ⟹ separated corridors) is the mechanism that should make every
  corridor have enough slack. This conic-flow feasibility / KKT-core exclusion is, in my (Claude's) view, the most
  concrete attackable form for you to push on. GPT has no complete proof; the corridor argument is unwritten.

## 6. How we coordinate
- **Acceptance gate (non-negotiable):** the ONLY proof that counts is one Claude Step-2 confirms by **exact rational
  `Fraction`** verification + blow-up stress to N≥18–22. No floating-point closure, no `native_decide`. Three false
  closures in this project were caught only by the exact check.
- **Evaluate at the GRAPHON / blow-up level** (i.i.d. blow-up density), never a finite distinct-subset evaluation
  (O(1/n) artifact). `Γ/N²` is blow-up invariant, so a proof valid for all blow-ups transfers to the base graph.
- **Propose lemmas to me in a checkable form.** Give me an explicit inequality / identity / flow model / candidate
  certificate and I will exact-test it on the full census N≤11 + the witness `J???E?pNu\?[2]` (N=22) and report
  numbers immediately. I maintain the verifiers; you push the math.
- **Use GPT-Pro when stuck** (both of us should — every math advance this session came from GPT-Pro consults).
  **Use your OWN SEPARATE GPT-Pro chat** — do NOT post to Claude's thread (ChatGPT `c/6a3e68cf`, "Graph Theory
  Problem"), which Claude drives; two agents on one chat collide. Open a fresh ChatGPT-Pro conversation for your
  consults. Give it full self-contained context (this onboarding + `ROWSUM_O_reduction.md` + the current crux +
  what's ruled out in §4). When GPT-Pro gives you something load-bearing (a lemma, identity, flow model, or
  certificate), post the gist to `CODEX_TO_CLAUDE.md` so Claude can exact-test it and so we both stay in sync.
  (Browser-read tip if you drive ChatGPT in a browser: math symbols can trip a content filter — read
  `main.innerText` stripped to letters-only `[^a-zA-Z .,;:()\-]`; reload the thread if a long answer renders as a
  ~170-char stub while still generating.)
- **Relay** through the user (English), or append to `coordination/STEP2_TO_STEP1.md` / `STEP1_TO_STEP2.md`. Don't
  edit each other's live-run scripts mid-solve.
- **Compute:** native Windows `clang++` MT (never WSL); ≤ 64–100 worker threads (never 128); `geng.exe` is at
  `tools/nauty2_8_9/`.
- **Git:** commit as the **user alone** — NEVER add a `Co-Authored-By: ... anthropic/claude` trailer (it breaks the
  Google CLA on the formal-conjectures PR). Branch off main; commit/push only when the user asks.
- **All-or-nothing:** nothing is published or PR'd until the FULL proof is sorry-free. The reduction alone is not a
  submission; the crux must be proven first.

## 7. First moves I suggest for you
1. Read `ROWSUM_O_reduction.md` and run `python _rowsum_verify.py` and `python _layerprice_verify.py` to see the
   verified state with your own eyes.
2. Pick the form you find most tractable (I lean toward Layer-Price Feasibility / the KKT-core exclusion, because the
   triangle-free corridor structure is most explicit there).
3. Attack the corridor-capacity / flow-Hall argument (§5). When you have a candidate lemma, hand it to me to
   exact-test before investing in the full proof.
