# LOAD-PSC Capacity Target

This note records the current proof target after the two-lane guardrail killed the
raw ROWSUM/SPEC objective.

## Status

The stale objective `ROWSUM(f) <= N` / `rho(O) <= N` is false in the standing
gamma-min connected-B max-cut scope. The two-lane family has unique maximum cuts
with `ROWSUM>N` and `rho(O)>N`.

The surviving theorem-sufficient certificate is the load-pressure inequality.
The strongest exact-gated form currently in use is `LOAD-PSC-5`, which implies
`LOAD-PSC-25`, then LRS, then `beta <= N^2/25`.

Latest Codex exact gates:

```text
2026-07-01: _codex_loadpsc_capacity_gate.py --fast --min-n 7 --max-n 10
  cuts=18288, levels=74266, viol5=0, viol25=0.

2026-07-01: _codex_loadpsc_capacity_gate.py --fast --min-n 11 --max-n 11
  cuts=171193, levels=888529, viol5=0, viol25=0, negative_tv_gap=0.

2026-07-01: two-lane stress through L=100
  cuts=50, levels=177, viol5=0, viol25=0, min5_pos=87336/5.

2026-07-01: named blowup/Mycielskian/glued battery without census
  cuts=36, levels=171, viol5=0, viol25=0.
```

Exact dead simplifications:

```text
Pointwise low-band cap D|H_s| >= N sigma_s is false.
  _lowband_cap_proof.py: levels=773214, failures=2466,
  first failure at s/N=5/11.

Unimodality of the LOAD-PSC-5 integrand is false.
  _psc5_unimodal_gate.py: 189459 cuts checked, 5691 upcross cuts.
```

## Notation

Let

```text
N = |V|,
m = |M|,
Gamma = sum_f ell(f)^2,
D = N^2 - 25m,
L = N + D/25 = N + N^2/25 - m.
```

For a load threshold `tau >= 0`, define the truncated load

```text
a_tau(v) = min(T(v), tau).
```

For any vertex function `a`, define

```text
TV_B(a) = sum_{uv in B} |a(u)-a(v)|,
TV_M(a) = sum_{uv in M} |a(u)-a(v)|.
```

By coarea and max-cut domination, `TV_B(a)-TV_M(a) >= 0` for every `a`.

## Exact Equivalence

The prefix LOAD-PSC-5 running balance

```text
Phi(tau) =
int_0^tau ((D + 25N - 50s)|H_s| - 5N sigma_s) ds,

H_s = {v : T(v) > s},
sigma_s = delta_B(H_s) - delta_M(H_s)
```

is exactly

```text
Phi(tau)
= 25 sum_v a_tau(v)(L - a_tau(v))
  - 5N (TV_B(a_tau) - TV_M(a_tau)).
```

Therefore `PREFIX-LOAD-PSC-5` is equivalent to the capacitary TV inequality

```text
5 sum_v a_tau(v)(L - a_tau(v))
>=
N (TV_B(a_tau) - TV_M(a_tau))
```

for every critical threshold `tau in {T(v)}`.

The weaker `LOAD-PSC-25` prefix form would replace the coefficient `5` on the
left by `25`:

```text
25 sum_v a_tau(v)(L - a_tau(v))
>=
N (TV_B(a_tau) - TV_M(a_tau)).
```

The endpoint `tau >= max_v T(v)` gives

```text
sum_v T(v)(T(v)-N)
+ (N/5)(TV_B(T)-TV_M(T))
<= Gamma (N^2/25 - m),
```

which is `LOAD-PSC-5`.

## Proof Target

Prove the following finite statement for every connected-B gamma-min maximum cut
of a triangle-free graph:

```text
For every tau >= 0, with a(v)=min(T(v),tau),

5 sum_v a(v)(L-a(v)) >= N (TV_B(a)-TV_M(a)).
```

This formulation is attractive because:

1. It is exact rational and uses only `B`, `M`, `T`, and max-cut coarea.
2. It is tight at balanced `C5[t]`, where `D=0`, `L=N`, `T=N`, and both sides
   vanish.
3. It survives the two-lane and dense k-lane families that refute ROWSUM,
   B1, and B2.
4. It exposes the real mechanism: the bad-count deficit `D=N^2-25m` supplies
   vertex capacity `a(L-a)`, and cut-pressure is the total-variation demand.

## Next Lemma Shape

The current proof frontier is the older `PRESSURE-SURPLUS-HALL` formulation.
For levels `0=t_0<t_1<...`, width `Delta_j=t_{j+1}-t_j`, and

```text
alpha_j = 25*(N+eta-(t_j+t_{j+1})),
eta = N^2/25-|M|,
H_j = {T>t_j},
sigma_j = delta_B(H_j)-delta_M(H_j),
```

split the positive and negative `alpha_j` bands by K-component `C`:

```text
Source_C(k) = sum_{j<k, alpha_j>0} Delta_j*alpha_j*|H_j cap C|,
Volume_C(k) = sum_{j<k, alpha_j<0} Delta_j*(-alpha_j)*|H_j cap C|,
Pressure(k) = sum_{j<k} 5*N*Delta_j*sigma_j.
```

The proof target is:

```text
Pressure(k) <= sum_C max(0, Source_C(k)-Volume_C(k))
```

for every prefix `k`. This is exactly the component-bank pressure handshake
whose aggregate form is `LOAD-PSC-5`.

The strongest current exact-gated refinement is component-local. Assign each
boundary edge of `H_j` to the K-component of its endpoint lying in `H_j`; this
decomposes `sigma_j=sum_C sigma_C(j)`. Define

```text
Pressure_C(k)=sum_{j<k} 5*N*Delta_j*sigma_C(j).
```

Then test/prove the sharper inequality

```text
Pressure_C(k) <= max(0, Source_C(k)-Volume_C(k))
```

for every component `C` and prefix `k`. Codex exact gates on 2026-07-01:

```text
N<=10 + lanes/blowups: cuts=18283, component-prefix rows=154698, violations=0.
N=11:                 cuts=171193, component-prefix rows=1970704, violations=0.
two-lane L<=100:      cuts=50, component-prefix rows=12953, violations=0.
```

The analogous vertex-local statement is false: assigning boundary pressure to
the high endpoint vertex and asking each vertex bank to pay its own pressure
fails already at `cenG?AEBw`, `N=8`, margin `-239/100`. Thus the component
granularity is not cosmetic; K-component pooling is required.

A plausible proof route is a minimal counterexample / Euler sweep argument.
If the inequality fails for the smallest critical prefix, then the high-load
sets have too much signed boundary variation compared with their component
bank. One should show that this produces either:

```text
1. a neutral connected terminal-shadow switch with lower Gamma, contradicting
   gamma-minimality; or
2. a C5-blow-up quotient certificate, which forces equality rather than failure.
```

This is the corrected version of the earlier switch/Hall attempts: the switch
must be driven by the truncated load capacity `a(L-a)`, not by raw ROWSUM,
harvest, or fixed-depth spectral slack.
