Finite LP/Farkas result:

For a fixed graph/cut, let \(\Omega=\prod_f\mathcal R_f\) be the complete set of coupled row tuples. For each \(\omega\), recompute exactly:

- selected support \(S_\omega\);
- internal graph \(I_\omega\);
- active components;
- scoped obligation score \(c_\omega\);
- whether scoped Hall fails.

Let \(F\subseteq\Omega\) be the Hall-failing tuples. The “Hall-failing global minimizer” primal is

\[
z_\omega\ge0,\qquad
\sum_{\omega\in F}z_\omega=1,\qquad
\sum_{\omega\in F}c_\omega z_\omega\le c_\eta
\quad(\eta\in\Omega).
\]

This is feasible exactly when some Hall-failing tuple achieves the global minimum. Thus a rational Farkas certificate of infeasibility proves that no global minimizer Hall-fails.

This formulation respects:

- row-choice coupling, because variables index complete tuples rather than independent row marginals;
- active-component deactivation, because \(I_\omega\), its components, and \(c_\omega\) are recomputed before forming coefficients.

Nontrivial exact fixture:

```text
graph6       G?`F`w
N            8
cut mask     112
Gamma        50
bad edges    (2,7), (3,7)
family sizes 2, 2
```

Edges:

```text
(0,4) (0,6) (1,5) (1,6) (2,6)
(2,7) (3,6) (3,7) (4,7) (5,7)
```

Rows and exact results:

| Choice | Rows | Score | Hall |
|---|---|---:|---|
| 00 | 2-6-0-4-7; 3-6-0-4-7 | 32 | fails, deficiency 12 |
| 01 | 2-6-0-4-7; 3-6-1-5-7 | 8 | passes |
| 10 | 2-6-1-5-7; 3-6-0-4-7 | 8 | passes |
| 11 | 2-6-1-5-7; 3-6-1-5-7 | 32 | fails, deficiency 12 |

The primal reduces to

\[
32(z_{00}+z_{11})\le8,\qquad
-z_{00}-z_{11}\le-1.
\]

The nonnegative Farkas multipliers \((1,32)\) produce

\[
0\le 8-32=-24,
\]

an exact contradiction. Hence neither Hall-failing tuple is globally minimizing. The passing minimum is \(8\).

Canonical certificate payload:

```text
fixture=G?`F`w;mask=112;scores=00:32F,01:8P,10:8P,11:32F;primal=32(z00+z11)<=8,-z00-z11<=-1;farkas=(1,32);sum=0<=-24
```

SHA256:

```text
8f37a73f0b9776072db42c4122017cf6444e139100399cb1bad8b632fbbf6e28
```

Exact census command used:

```powershell
python problems/23/writeup/_codex_r20_global_min_all_ties_gate.py --min-order 5 --max-order 8 --workers 1 --max-falsifiers 0
```

It reported 68 Hall-failing tuples and zero Hall-failing global minimizers over eligible orders \(5\)–\(8\).

Smallest missing step: membership in \(F\) and active-component status are disjunctive reachability properties. Tuple enumeration resolves them exactly for each finite fixture, but no polynomial-size linear description—or graph-size-independent structural Farkas multipliers—is currently proved. Replacing tuple variables by row marginals is invalid: it loses both joint row coupling and component deactivation. Consequently this is a complete finite-instance certificate scheme, not yet a uniform proof for arbitrary graphs.

Relevant source hashes:

```text
WALL_ATTACK_R29_GPTPRO56.md                 fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04
_codex_r20_global_min_all_ties_gate.py      fd4934312b127e77a57ca436c5648c3810b420192639d09973eab5acdfa2f7ec
_codex_r20_two_row_exchange_gate.py         73697b12b1e22a30e320fb970415e79fa90d88d1a6db27f42022cf9ffd9c6d83
```

No production, coordination, Lean, or progress file was edited.