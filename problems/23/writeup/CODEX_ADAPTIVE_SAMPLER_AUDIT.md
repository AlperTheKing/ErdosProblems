# Adaptive Sampler Audit

Date: 2026-07-01.

## Verdict

The adaptive harmonic sampler certificate is algebraically sound, but it is
not a separate strengthening of the current target. It is exactly the primal
layer-price feasibility problem in the coordinates

```text
q_{f,i} = c_{f,i} = 1 / b_{f,i}.
```

The sampler constraints

```text
q_{f,i} > 0,
sum_i q_{f,i} = 1,
sum_{f,i} P_{f,i}(v) / q_{f,i} <= N
```

are the same as the existing LPD/layer-price constraints

```text
c_{f,i} > 0,
sum_i c_{f,i} <= 1,
sum_{f,i} P_{f,i}(v) / c_{f,i} <= N.
```

If `sum_i c_{f,i} < 1`, increasing one or more `c_{f,i}` to make equality
only decreases the vertex budgets, so the equality form loses no generality.

## Implication Check

For fixed `q`, Cauchy gives

```text
(sum_i sqrt(w_{f,i}))^2 <= sum_i w_{f,i} / q_{f,i}.
```

Thus

```text
2 sum_{i<j} sqrt(w_{f,i} w_{f,j})
<= sum_i (1/q_{f,i} - 1) w_{f,i}.
```

Summing over bad edges and using the vertex budgets gives CORR/LPD. This is
the same proof as the layer-price SOS in `_layerprice.py`.

## KKT Core

The proposed obstruction

```text
W_{f,i} = sum_v lambda_v P_{f,i}(v),
A_f = sum_i sqrt(W_{f,i}),
q^*_{f,i} = sqrt(W_{f,i}) / A_f,
Theta(lambda) = sum_f A_f^2 > N
```

with flat adaptive overload

```text
D_lambda(v) = sum_{f,i} A_f P_{f,i}(v) / sqrt(W_{f,i})
```

is the same KKT core already recorded in `CODEX_LPD_KKT_CORE.md`. Excluding
this core is the live proof obligation; the sampler formulation does not
remove that obligation.

## Current Gates

Commands run on 2026-07-01:

```text
python problems\23\writeup\_layerprice_verify.py
```

Output summary:

```text
FCp`_          N=7  t*=7.0000  pass
I?BD@g]Qo      N=10 t*=9.9446  pass
I?ABCc]}?      N=10 t*=8.8480  pass
J?AEB?oE?W?    N=11 t*=11.0000 pass
J???E?pNu?[2]  N=22 t*=20.4863 pass
full N=8       85 configs, 0 infeasible
full N=9       650 configs, 0 infeasible
stride-5 N=10  1160 configs, 0 infeasible
```

```text
python problems\23\writeup\_rowsum_verify.py
```

Output summary:

```text
key witnesses and C5/C7/C9 blowups pass exactly;
full census N=5..11 has 0 ROWSUM-O violations;
N=11 checked 65244 graphs-with-bad, max(O1-N)=0 at J?AEB?oE?W?.
```

```text
python problems\23\writeup\_gpt_cycle_neighbor_cage_gate.py --g6 'I?BD@g]Qo' --method flow
```

Output:

```text
{'label': 'I?BD@g]Qo[1]', 'n': 10, 'checked': 3, 'fail': None}
```

## Next Use

The sampler is a clean language for asking for exact rational certificates.
The useful exact gate for any proposed formula is:

```text
for every f: q_{f,i} > 0 and sum_i q_{f,i} <= 1,
for every v: sum_{f,i} P_{f,i}(v) / q_{f,i} <= N.
```

All terms are rational because the layer probabilities are shortest-geodesic
counts divided by `|cyc[f]|`. A proof still has to construct such `q`
universally, or equivalently rule out the KKT flat adaptive overload.
