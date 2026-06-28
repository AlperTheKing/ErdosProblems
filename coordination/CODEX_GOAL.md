# GOAL — Codex (working with Claude Step-2) on Erdős Problem #23

## The one thing to achieve
Prove a single scalar inequality. Everything else is already done.

Erdős #23: *every triangle-free graph G on N vertices has β(G) = e(G) − MaxCut(G) ≤ N²/25.*
This has been **fully reduced** (rigorously; every other step is a proven, exact-verified identity) to ONE
inequality, available in three **equivalent** forms — prove **any one** of them and the whole conjecture is closed:

- **(ROWSUM-O)** For every bad edge f:  `Σ_g ⟨p_f,p_g⟩ = (O·1)_f = Σ_v p_f(v)·S(v) ≤ N`,  where `S(v)=Σ_g p_g(v)`.
- **(SPEC)** `ρ(O) ≤ N` for the geodesic-overlap Gram matrix `O = PᵀP`, `P[v,f]=p_f(v)` (entrywise ≥ 0).
- **(LAYER-PRICE FEASIBILITY)** For every connected-B triangle-free max-cut configuration there exist layer prices
  `b_{f,i} > 0` (one per geodesic layer of each bad edge f) with `Σ_i 1/b_{f,i} ≤ 1` (per edge) and per-vertex budget
  `Σ_{f, i : v∈I_i(f)} b_{f,i} p_f(v) ≤ N` (per vertex). Its convex dual is
  **(LPD)** `Σ_f (Σ_i √w_{f,i})² ≤ N·Σ_v y_v` for all `y ≥ 0`, `w_{f,i} = Σ_{v∈I_i(f)} y_v p_f(v)`.

(Notation defined in `coordination/CODEX_ONBOARDING.md`. The chain `any one ⟹ ρ(O)≤N ⟹ Σ_v T(v)²≤N·Γ ⟹
Cauchy–Schwarz ⟹ Γ≤N² ⟹ β≤N²/25` is fully proven; see `problems/23/writeup/ROWSUM_O_reduction.md`.)

## What "done" means
A **rigorous mathematical proof** of one of the forms above, that:
1. Claude Step-2 independently **exact-verifies** (rational `Fraction` arithmetic; this is the only acceptance gate),
   including a stress pass on triangle-free blow-ups up to N ≈ 18–22 (a census-only check already produced one false
   closure this project — see onboarding).
2. Is then assembled into the single arXiv proof and (final target) a **sorry-free Lean** proof for one
   `google-deepmind/formal-conjectures` PR (all-or-nothing: nothing ships until the full proof is sorry-free).

## Honest difficulty
This inequality is **conjecture-equivalent**: its `y=1` case literally *is* `Γ≤N²`. So a proof of it is a proof of
the whole remaining problem. It is **not** reducible to anything easier — Claude Step-2, GPT-Pro, and two multi-agent
workflows have all confirmed this and exhausted every standard certificate method (see onboarding: "What is ruled
out"). What remains needs a genuinely new idea — most likely the triangle-free **corridor-capacity / KKT-core
exclusion** argument made rigorous (onboarding §5). Use GPT-Pro when stuck (so does Claude).

## Division of labor
- **Codex (you):** drive the *proof* of the crux — new mathematical ideas, the corridor/flow/SOS argument.
- **Claude Step-2:** owns the *reduction* (proven) and *exact verification* — will instantly exact-test any lemma,
  identity, flow model, or certificate you propose on the full census + the N=22 witness, and run the independent
  acceptance gate. Co-develop; don't duplicate. Relay through the user (English), or via `coordination/` files.
