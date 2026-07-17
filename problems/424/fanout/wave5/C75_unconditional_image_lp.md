# C75: unconditional-image LP dual gate

## Verdict

The C23 unconditional one-step image inequality has a substantially stronger
finite certificate than the earlier CP-SAT gate.  For fixed cutoff `X`, relax
every Boolean source, image, pair-witness, and seed-boundary variable to the
interval `[0,1]`, retaining all forward-closure constraints and the standard
convex-hull inequalities.  The resulting LP still satisfies

\[
 \max\bigl(H_{F(S)}(X)-Q_{F(S)}(X)\bigr)\le 0
\]

at every tested endpoint through `10^6`.  Exact rational dual certificates
were reconstructed and replayed at selected endpoints through `200000`.

This is finite evidence and a finite proof at the replayed endpoints.  It is
not a proof for arbitrary `X`.  The dual multipliers back-propagate through
the grounded closure DAG and grow with the cutoff; no cutoff-uniform
multiplier rule is proved here.

## 1. Relaxation

Let `s_n` denote membership in a forward-closed allowed source `S`, and let
`f_n` denote membership in its one-step image `F(S)`.  For every admissible
pair `ab=n+1`, introduce `w_(n,a,b)`.  The LP includes

\[
 s_a+s_b-s_n\le1,
\]

the exact `[0,1]` convex hull of `w=s_a AND s_b`, and

\[
 w_{n,a,b}\le f_n\le\sum_{ab=n+1}w_{n,a,b}.
\]

It also includes the valid inequality `f_n<=s_n`.  Seeds have
`s_2=s_3=f_2=f_3=1`; values with no admissible pair have `f_n=0`.

For every seed-2 edge `p -> c=2p-1`, introduce `q_c` and use the exact
convex hull of

\[
 q_c=(1-f_p)f_c.
\]

If `D_X` is the set of hard-shaped even values through `X`, minimizing

\[
 \sum_{h\in D_X}f_h+\sum_{c\le X}q_c                       \tag{1}
\]

is equivalent on integral points to maximizing the image excess, because

\[
 H_{F(S)}(X)-Q_{F(S)}(X)
 =|D_X|-(1).                                               \tag{2}
\]

Every LP inequality is valid for the original Boolean problem.  Therefore a
dual lower bound of at least `|D_X|` proves the C23 endpoint inequality at
that finite cutoff.

## 2. Results

The HiGHS discovery solve gave the following relaxed endpoint excesses.

| `X` | relaxed `max(H-Q)` |
|---:|---:|
| 54 | 0 |
| 74 | 0 |
| 186 | 0 |
| 362 | 0 |
| 500 | -6 |
| 1,000 | -4 |
| 2,000 | -5 |
| 5,000 | -34 |
| 10,000 | -68 |
| 20,000 | -206 |
| 50,000 | -626 |
| 100,000 | -1,555 |
| 200,000 | -3,488 |
| 500,000 | -9,667 |
| 1,000,000 | -20,810 |

The `500000` and `1000000` rows are floating-point discovery gates only.
The rows through `200000` listed above have exact rational dual replays at
the selected replay cutoffs.  In particular, at `X=200000` the exact dual
objective is `24782`, while `|D_X|=21294`, giving exact margin `3488`.

All reconstructed dual multipliers through `200000` are integers.  The exact
checker verifies, over `Fraction`, every multiplier sign, every stationarity
equation, and equality of the primal and dual objectives.  At `X=10000` the
LP value `-68` agrees with the independently implemented C23 CP-SAT endpoint
optimum `-68`.

An independent Clarabel conic solve at

```text
54, 74, 186, 362, 500, 1000, 5000
```

agrees with the HiGHS objectives to less than `5e-8`.  Clarabel is used only
as a second numerical solver; exact acceptance comes from the rational dual
replay.

## 3. What the dual says

At the tight endpoints `54,74,186,362`, the LP returns an integral optimum
and an integral dual.  The dual uses:

* unit support and boundary multipliers;
* the fixed zero upper bounds on structural splitless image variables;
* seed lower bounds; and
* closure inequalities along grounded derivations.

The closure multipliers are not bounded.  At `X=5000`, the largest ones are

```text
1274 * closure(5 <- 2,3)
 511 * closure(9 <- 2,5)
 300 * closure(14 <- 3,5)
 233 * closure(17 <- 2,9).
```

Thus the finite dual is a back-propagated grounded flow, not a fixed local
identity.  This aligns with C65's ordered-bank formulation: proving a
uniform augmentation rule would close the theorem, while merely emitting
one larger dual per cutoff would not.

## 4. Reproduction

```powershell
python problems/424/compute/wave5/C75_unconditional_image_lp.py `
  --limits 54 74 186 362 500 1000 2000 5000 10000 20000 `
  --output problems/424/compute/wave5/C75_unconditional_image_lp.json

python problems/424/compute/wave5/C75_dual_exact_replay.py `
  --limits 54 74 186 362 500 1000 2000 5000 10000 20000 50000 100000 200000 `
  --output problems/424/compute/wave5/C75_dual_exact_replay_200k.json
```

SHA-256:

```text
2571D39600AD42E2C6F2DCFCFE64315CB6955853A3C43FA274A3182389B8E457  C75_unconditional_image_lp.py
11ED28EF5130832930B9127BEE6990A429A9A03EB6404EEEDDD667FBBAA8D0A1  C75_dual_exact_replay.py
CB0383D1C987460C4D2C03B17015EDBB82259762177D8D5873C625FD0ECBCBC1  C75_dual_exact_replay_200k.json
018170D796C9616F8818B3B46177E319FA7596F27FCD2E4E3E03729CB9C6F513  C75_unconditional_image_lp_1e6.json
```
