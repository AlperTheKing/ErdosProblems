# C5-RS Direct Layer-Cake Proof Split

Date: 2026-07-01

This file records the current live route after Claude exact-falsified row-majorization (RM). It is a proof-obligation split, not a completed proof.

## Target

For an all-length-5 K-component row `Q=(q0,...,q4)`, define

```text
s_i = Tw_C(q_i)
tau = 5m/N
eta = N^2/25 - m
B_C5 = (1 + 25/N) eta
```

C5-RS is

```text
sum_i max(0, s_i - tau) <= B_C5.
```

Equivalently, for every nonempty `A subset {0,...,4}`,

```text
L(A) := sum_{i in A}(s_i - tau) <= B_C5.        (subset C5-RS)
```

The full mask is

```text
A = {0,1,2,3,4},
L(A) = row_sum(Q) - 5tau.
```

Since `5tau = N - 25eta/N`, full-mask C5-RS is exactly

```text
row_sum(Q) <= N + eta.                          (full row-sum)
```

Thus the equal-length C5 branch can be split into:

1. proper masks: `A != full`, a genuine layer-set/high-coordinate bound;
2. full mask: row-sum stability.

## Stronger proper-mask candidate

The sharper candidate now isolated for exact testing is:

```text
C5 PROPER-MASK LIFT:
for every nonempty proper A,
  L(A) <= (25/N + 2/3) eta.                     (proper lift)
```

This is stronger than C5-RS on proper masks. It deliberately excludes the full
mask because the full mask is exactly the separate row-sum branch
`row_sum(Q) <= N + eta`; the broad proper-mask gate is not meant to prove that
full-mask inequality.

If C5 PROPER-MASK LIFT is true, then the only remaining all-length-5 obstruction is the full row-sum inequality.

## Full-mask branch

Full-mask C5-RS is:

```text
row_sum(Q) <= N + eta.
```

The sharper C5-HOM/seven-cut/PMS branch asks for

```text
row_sum(Q) <= N + (2/3) eta
```

in the sharp C5-hom/weighted pentagonal setting, tight at the sparse equality atom `I?BD@g]Qo`.

For non-C5-hom components, do not assume C5-LIFT. The safe full-mask target remains `row_sum<=N+eta`.

## Full-mask two-bank flow form

Claude's 2026-07-02T01:33:34Z gate refuted the proposed half-degree excess
bound

```text
I(Q) <= (1/2) sum_{v in Q} deg_G(v) + eta.
```

The exact counterexample is:

```text
graph6 G?`DA_wJ?
N = 10, m = 2, eta = 2
cut = [1,0,1,0,0,1,0,1,1,0]
M_C = {(2,8),(4,9)}
Q = [2,6,0,4,8]
s = (2,2,2,2,1)
deg(Q) = (3,2,2,3,3)
I(Q) = 9
halfdeg(Q) = 13/2
I(Q)-halfdeg(Q) = 5/2 > eta.
```

This row is sparse and non-overloaded (`I(Q)=9<=N`), so it is a guardrail
against proving full-mask stability by eta alone.

The same gate produced two usable exact tools:

1. **Flow identity.**  For a row `Q`, let `C(P)` be the odd cycle formed by
   a shortest row `P` and its bad edge.  For each graph edge `e`, define

   ```text
   F(e) = sum_g (1/|cyc[g]|) * #{P in cyc[g] : e in C(P)}
   a_Q(e) = |e cap Q| / 2.
   ```

   Then

   ```text
   I(Q) - (1/2)sum_{v in Q}deg_G(v)
     = sum_e a_Q(e) * (F(e)-1).
   ```

   Claude gated this identity exactly with 0 failures.

2. **Half-degree bound.**

   ```text
   sum_{v in Q} deg_G(v) <= 2N.
   ```

   Equivalently,

   ```text
   N - (1/2)sum_{v in Q}deg_G(v)
     = (1/2)sum_{x notin Q} (2 - |N_G(x) cap Q|) >= 0.
   ```

Therefore the full-mask target `I(Q)<=N+eta` is exactly equivalent to the
two-bank flow inequality

```text
sum_e a_Q(e) * (F(e)-1)
  <= eta + (1/2)sum_{x notin Q} (2 - |N_G(x) cap Q|).      (2BANK)
```

Interpretation:

```text
flow excess along the row
  <= bad-edge deficit bank eta
     + outside under-attachment bank to Q.
```

Dense equality atoms have outside bank `0`, so eta pays the residual row
excess.  Sparse rows such as `G?`DA_wJ?` can violate the eta-only HDX bound,
but survive because the outside under-attachment bank is positive.  The
full-mask proof target should use this two-bank transport form rather than
the false HDX shortcut.

### Overloaded-HDX refinement

Although `HDX` is false in general, its observed exact counterexamples are
non-overloaded rows.  Since full-mask stability is automatic when `I(Q)<=N`, a
sufficient sharper branch is:

```text
if I(Q)>N, then
  I(Q) <= (1/2)sum_{v in Q}deg_G(v) + eta.       (OHDX)
```

Together with `sum_{v in Q}deg_G(v)<=2N`, this proves `I(Q)<=N+eta` for
overloaded rows; non-overloaded rows already satisfy `I(Q)<=N<=N+eta`.

Codex diagnostic:

```text
python problems/23/writeup/_codex_c5_fullmask_twobank_probe.py --min-n 8 --max-n 10

cuts = 18259
rows = 80320
over_rows = 36
identity_fails = 0
hdx_fails = 4
hdx_over_fails = 0
twobank_fails = 0
over_outside_bank = {0: 34, 1/2: 2}
over_halfdeg = {10: 34, 19/2: 2}
over_active_counts = {4: 2, 5: 34}
```

After adding active-specific margin output and rerunning the census part
`N=8..10 --skip-named`, the overloaded branch separates as:

```text
over_active_counts = {4: 2, 5: 34}

active-5 worst:
  hdx_margin = 1/3
  twobank/full_margin = 1/3
  halfdeg = N
  row_sum = 32/3
  seed = I?BD@g]Qo

active-4 worst:
  hdx_margin = 11/30
  twobank/full_margin = 13/15
  halfdeg = N - 1/2
  row_sum = 152/15
  seed = I?`FAo]]?
```

Full census `N=11` local run:

```text
python problems/23/writeup/_codex_c5_fullmask_twobank_probe.py --min-n 11 --max-n 11 --skip-named

cuts = 171182
rows = 1045374
over_rows = 0
identity_fails = 0
hdx_fails = 9
hdx_over_fails = 0
twobank_fails = 0
```

So through the full local census `N<=11`, every `HDX` failure is
non-overloaded.  All actual overloaded rows occur at `N=10` in the known seed
families and satisfy `(OHDX)`.

Thus the current exact-testable full-mask target is `(OHDX)`, not full `HDX`.
The known `HDX` witness `G?`DA_wJ?` has `I(Q)=9<N=10`, so it is harmless for
full-mask GERSH.

Proof split suggested by the local exact profile:

```text
OHDX-5:
  active set = all 5 coordinates.
  In the local census profile, outside_bank=0 and halfdeg=N.
  It is enough to prove I(Q)-N <= eta.

OHDX-4:
  active set has size 4.
  In the local census profile, outside_bank=1/2 and halfdeg=N-1/2.
  It is enough to prove I(Q)-N <= eta-1/2.
```

The active-5 branch is the sharp branch: it is weaker than the sharp
`C5-LIFT-PMS` target `I(Q)<=N+(2/3)eta` when available, and its worst local
margin is the `I?BD@g]Qo` equality atom plus `1/3`.

The active-4 branch is no longer the numerically tight branch in the local
gate: its worst `OHDX` margin is `11/30` and its full-mask margin is `13/15`.
It still needs a proof mechanism using the inactive-coordinate/half-degree
drain, because proper-mask lift alone only gives `I(Q)<=N+(2/3)eta`, but the
exact evidence says active-4 has substantial extra slack once the inactive
coordinate is accounted for.

For the final C5-RS inequality, however, active-4 does **not** require OHDX.
Let

```text
A(Q)={i:s_i>tau}.
```

If `A(Q)` is proper, then the proper-mask lift for this active set gives

```text
sum_i max(0,s_i-tau)
  = sum_{i in A(Q)}(s_i-tau)
  <= (25/N + 2/3) eta
  <= (25/N + 1) eta,
```

which is exactly C5-RS.  Thus the full-mask burden for final GERSH is only
the active-5 case `A(Q)={0,1,2,3,4}`.  In that case C5-RS is equivalent to

```text
I(Q) <= N + eta,
```

and the sharper active-5 certificate `I(Q)<=N+(2/3)eta` would close it.
So `(OHDX)` is a useful diagnostic, but not the minimal final proof route:
`proper-mask lift + active-5 full-mask stability` is enough.

## Guardrails

Dead routes:

1. Do not use `sum_i(s_i-N/5)_+ <= eta`; Claude exact-falsified it.
2. Do not use row-majorization by C5 class sizes; Claude exact-falsified RM on `H?AFBo]`.
3. Do not assume every length-5 component has a C5 homomorphism; Grotzsch refutes it.
4. Do not use heuristic/non-maximum cuts as evidence. Claude rechecked the
   MycGrotzsch `N=23` stress with true `gmins`; the earlier non-C5-hom
   scale-warning cut had maxcut value `54` while the true maximum is `55`, so
   the claimed sharp-C5-LIFT failure is out of hypothesis and retracted.
5. Do not use reciprocal row-width `(RW)`: it fails by inspection on every
   overloaded row because any pointwise `w >= s` has `sum w >= row_sum > N`.
6. Do not use the real five-variable cyclic reciprocal surplus `CRS5`: Claude
   found the exact real counterexample `N=9, m=3, w=(2,3/2,2,2,3/2)` with gap
   `7/75`.  The integer class-size version may survive, but the real-width
   lemma is false.
7. Do not use the eta-only half-degree excess bound `HDX`.  It is false on
   `G?`DA_wJ?`; keep the outside under-attachment bank in the exact two-bank
   form `(2BANK)`.

## Current exact evidence for proper masks

Local census `N<=11`, positive eta only:

```text
proper-mask C5 PROPER-MASK LIFT: 0 fails.
```

Weighted quotient seeds, qmax only, weights in `{1,2}`:

```text
equality seed: proper-mask C5 PROPER-MASK LIFT 0 fails, full mask tight at all-ones.
sibling seed:  proper-mask C5 PROPER-MASK LIFT 0 fails, full mask min margin 1/3 at all-ones.
```

Claude broad-battery result, 2026-07-02:

```text
C5 PROPER-MASK LIFT:
  census N<=11 all gmins, 814629 rows including both seeds,
  blowups, chains, and Grotzsch N11:
  0 fails, min slack 0.

FULL-mask row_sum <= N+eta:
  same battery:
  0 fails, min slack 0.

MycGrotzsch N23:
  true maxcut value 55, unique gamma-min cut,
  m=16, 570 L5-multi rows:
  proper-mask slack +1.748, full-mask slack +5.53.
```

Thus both the proper-mask branch and the full-mask row-sum branch survive all
legitimate exact tests currently reported.  The live proof obligation is no
longer to explain a non-C5-hom scale failure; it is to prove the proper-mask
layer-cake bound and the full-mask row-sum bound from maxcut/gamma-min
structure.
