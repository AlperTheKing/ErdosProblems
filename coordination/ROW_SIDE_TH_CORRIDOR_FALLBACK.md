# Row-Side Fallback: TH-Corridor Atom

Status: row-side fallback, behind the bare cycle-Hardy / ROWSUM target.
The Jacobi-6 / harvest line was retracted after large `C5[k+1,k,k+1,k,k+1]`
blowups.  Do not treat this as a primary route unless the spectral target
stalls.

Source attachment:
`C:/Users/a/.codex/attachments/1f2fe8d7-0003-4441-9e5e-1c722cdb0a98/pasted-text.txt`

## Proposed Atom

For one residual connected component `(A,B)`, put terminal slack on exits:

```text
s_f(e) =
  d_{B[S]}(tau_f, x_e) + 1 + d_{B[bar S]}(y_e, sigma_f)
  - d_B(tau_f, sigma_f).
```

Terminal-shadow gives `f ~ e iff s_f(e)=0`, and parity gives
`s_f(e) in 2 Z_{\ge 0}`.

Define the residual exit co-witness graph `J(A,B)` on exits:

```text
e ~_J e' iff some g in A witnesses both e and e'.
```

Because the residual witness component is connected, `J(A,B)` is connected.
If a row `f` misses two exits, choose a shortest `J`-path

```text
e0, g1, e1, ..., gk, ek
```

with both endpoints slack for `f` and all internal exits tight for `f`.

## TH-Corridor Gate

For every such shortest two-hole corridor, exactly one certificate should exist:

1. Long-lambda endpoint:
   if `lambda(e0)>L0` or `lambda(ek)>L0`, then the row-union disk contains a
   triangle or a shorter `B`-path for one of `f,g1,...,gk`.

2. Minimum-lambda endpoints:
   if `lambda(e0)=lambda(ek)=L0`, then the stage-0 alternating graph contains
   a negative rare-cost exchange:

```text
sum_{z in Z} deg_{F1}(z) < sum_{u in U} deg_{F1}(u).
```

This would imply the component-local single-miss theorem:

```text
forall f in A, |B \ Wit(f)| <= 1.
```

## Triage

This is row-side fallback material.  Claude currently deprioritized Door-Cap /
residual-Hall checks while the Schur / ROWSUM spectral route remains alive.
Do not spend large compute here unless the bare cycle-Hardy target stalls.

2026-07-01 Codex triage:

* The user attachment at the source path is essentially this same TH-Corridor
  proposal.
* Existing gate: `problems/23/writeup/_codex_th_corridor_gate.py`.
* Census smoke test:

```text
python problems/23/writeup/_codex_th_corridor_gate.py --min-n 5 --max-n 10
tested: 21
status: {'ok': 21}
stats: {('row_miss', 0): 21}
VERDICT: PASS
```

This is not proof evidence for the hard case: the smoke test did not exercise a
two-hole corridor.  Broader H-blowup allmax / inherited runs were stopped after
90-120s with no output.  Use Claude's broader residual-Hall ledger before
reviving this route, and keep the known hard-H3 / AtMostOneMiss failure in
scope.

2026-07-01 fresh Codex rerun:

```text
python problems/23/writeup/_codex_th_corridor_gate.py --min-n 5 --max-n 10
tested: 21 no_switch: 0 bad_terminal: 0
status: {'ok': 21}
stats: {('row_miss', 0): 21}
VERDICT: PASS
```

Interpretation unchanged: the attachment's TH-Corridor split is a plausible
row-side proof atom, but the quick gate is vacuous for the two-hole mechanism.
The primary route remains the K2T descent theorem unless a hard two-hole
corridor instance is produced.
