# Load-Rayleigh Bad-Count Slack Candidate

The repaired spectral target

```text
(SBC)    rho(O) + |M| <= N + N^2/25
```

may be stronger than needed.  Since the theorem only uses the Rayleigh
quotient in the length direction, the following scalar load target is enough:

```text
(LRS)    (sum_v T(v)^2) / Gamma + |M| <= N + N^2/25.
```

Equivalently,

```text
sum_v T(v)^2 <= Gamma * (N + N^2/25 - |M|).
```

## Why LRS Implies Erdős #23

Let `m=|M|`.  By Cauchy and the load handshake,

```text
sum_v T(v)^2 >= Gamma^2 / N.
```

Thus

```text
Gamma / N <= (sum_v T(v)^2) / Gamma.
```

Since every bad edge has `ell(f) >= 5`,

```text
Gamma >= 25m,
```

so

```text
25m/N <= Gamma/N <= (sum_v T(v)^2)/Gamma.
```

Combining with LRS gives

```text
25m/N + m <= N + N^2/25,
```

and hence `m <= N^2/25`.

This proves Erdős #23 because `m=beta(G)` for the chosen maximum cut.

## Why This Is A Better Proof Target Than SBC

LRS is weaker than SBC because

```text
rho(O) >= (ell^T O ell)/(ell^T ell)
       = (sum_v T(v)^2)/Gamma.
```

It avoids the Perron vector and the full Gram spectrum.  It is a pure load
second-moment inequality, tight at the `C5[t]` extremals.

## Local Gate

Ad hoc exact gate on census `N<=11` plus the two-lane family:

```text
N=5..11: lrs_bad=0
C5[1], C5[2]: equality
two-lane L=8,12,20,30: positive margin
```

This should be exact-tested by Claude on the full standing battery:

```text
census gamma-min N<=11
blow-ups C5/C7/C9[t]
Mycielskians
two-lane
merged/full detour constructions
dense-chord and stacked adversarial constructions
```

If LRS survives, the live proof target becomes a scalar variance/stability
statement for `T`, rather than a spectral statement for `O`.

## Proof-Facing Equivalent Form

Since `sum_v T(v)=Gamma`, LRS is equivalent to

```text
sum_v T(v) * (T(v) - N) <= Gamma * (N^2/25 - |M|).
```

Indeed,

```text
sum_v T(v)^2 - N*Gamma = sum_v T(v) * (T(v)-N).
```

Thus LRS says that the weighted overload of the load vector is paid by the
bad-edge deficit from the conjectural threshold.  This is likely the useful
form for a max-cut/CD proof:

```text
weighted overload <= Gamma * bad-count deficit.
```

At `C5[t]`, both sides are zero.  In low-bad-count sparse obstructions such as
the two-lane family, the right-hand side is very large.

## Stronger Local Row Form

A stronger sufficient target is the per-bad-edge length-weighted row bound:

```text
(row-LRS)    (O ell)_f / ell(f) + |M| <= N + N^2/25
             for every bad edge f.
```

In load notation this is

```text
sum_v (p_f(v) / ell(f)) * T(v) <= N + N^2/25 - |M|.
```

Thus every bad edge sees bounded average load along its shortest-geodesic
measure.  Since

```text
sum_v T(v)^2 = sum_f ell(f) * (O ell)_f
```

and `Gamma=sum_f ell(f)^2`, row-LRS implies LRS by averaging with weights
`ell(f)^2/Gamma`.

Local exact gate:

```text
census N<=11: no row-LRS violations; C5 equality
two-lane L=8,12,20,30: positive margins
```

This is a more local proof target than LRS and may be attackable by a
single-bad-edge geodesic/path-switch argument.

## Strongest Tested Path Form

An even more local strengthening replaces the geodesic-measure average by
every individual shortest path.  For every bad edge `f` and every shortest
`B`-geodesic `P` between its endpoints:

```text
(path-LRS)    (1/ell(f)) * sum_{v in P} T(v) + |M|
              <= N + N^2/25.
```

Since `p_f` is the average of the indicators of all shortest geodesics for
`f`, path-LRS implies row-LRS by averaging over `P`.

Local exact gate:

```text
census N<=11: no path-LRS violations; C5 equality
two-lane L=8,12,20,30: positive margins
```

This is the most local target currently surviving: it asks for a bound on the
load averaged along a single shortest odd-cycle path.

### Experimental Sharpening

The local census suggests a sharper coefficient:

```text
(path-LRS-2/3)    (1/ell(f)) * sum_{v in P} T(v)
                  <= N + (2/3) * (N^2/25 - |M|).
```

This is stronger than needed and is tight locally at the `N=10` graph
`I?BD@g]Qo`, where `|M|=3`, `N^2/25-|M|=1`, and a shortest path has average
load `N+2/3`.

Local exact gate:

```text
census N<=11: no violations, equality at I?BD@g]Qo
two-lane L=8,12,20,30,60: positive margins
```

This sharpening is not part of the proof shell unless it survives Claude's
full battery, but the exact `2/3` coefficient may be a clue for the path-switch
mechanism behind path-LRS.

## Coarea Work Note: Current Proof Pivot

After the two-lane and dense k-lane counterexamples, the robust elementary
proof target is LRS:

```text
sum_v T(v)(T(v)-N) <= Gamma * (N^2/25 - |M|).
```

Layer-cake gives the equivalent coarea form

```text
int_0^infty (2s-N) |{v:T(v)>s}| ds
  <= Gamma * (N^2/25 - |M|).
```

For every load superlevel `H_s={T>s}`, max-cut gives the CD surplus

```text
delta_B(H_s) - delta_M(H_s) >= 0.
```

The dead `|M|`-free sandwich tried to control the positive tail using only
this CD surplus.  Dense k-lanes show that no `|M|`-free load bound survives.
Therefore the proof must use the bad-count deficit structurally.

Representative coarea dumps are produced by

```text
problems/23/writeup/_codex_lrs_coarea_dump.py
```

Observed shapes:

```text
two-lane L=20:
  negative interval [0,40]: contribution -19320
  positive interval [40,76]: contribution +32436
  LHS=13116, RHS margin huge because |M|=4.

dense k-lane L=16,k=5,gap=8:
  one large negative underload interval, many positive overload intervals;
  LHS=393024, RHS=32392416/25, margin=22566816/25.
```

Thus sparse/dense-lane obstructions are not tight for LRS; the hard regime is
near the C5 blowup where `|M|` is close to `N^2/25` and the load profile must be
nearly flat.  A plausible proof should combine:

1. superlevel CD: `delta_M(H_s)<=delta_B(H_s)`;
2. a stability statement converting small bad-count deficit into near-flat load;
3. the odd-cycle square surplus `ell(f)^2-25` as the local budget away from C5.

The local path-LRS strengthening remains attractive because it asks for a
single shortest bad-geodesic path `P`:

```text
(1/ell(f)) sum_{v in P} T(v) + |M| <= N + N^2/25.
```

A prefix-switch proof along one shortest odd cycle would imply row-LRS by
averaging and then LRS.  The exact gate has no violations in the standing
battery, but this is stronger than LRS and should be treated as a proof route,
not an accepted reduction.

## Codex Note: Rational Actual-Load PSC Candidate

A Perron-free strengthening of LRS survived the local exact gate.  Let

```text
R_load = sum_v T(v)^2 / Gamma,
h_T(v) = N*T(v)/Gamma,
Xi_T = TV_B(h_T) - TV_M(h_T).
```

The candidate is

```text
LOAD-PSC-25:  R_load + |M| + Xi_T/25 <= N + N^2/25.
```

Equivalently, since `Xi_T = (N/Gamma)(TV_B(T)-TV_M(T))`, multiplying by
`Gamma` gives the exact coarea-pressure form

```text
sum_v T(v)(T(v)-N)
  + (N/25) * ( TV_B(T) - TV_M(T) )
  <= Gamma * (N^2/25 - |M|).
```

By layer-cake,

```text
TV_B(T)-TV_M(T) = int_0^infty (delta_B({T>s})-delta_M({T>s})) ds,
```

so the threshold form is

```text
int_0^infty [ (2s-N)|{T>s}| + (N/25)(delta_B({T>s})-delta_M({T>s})) ] ds
  <= Gamma * (N^2/25 - |M|).
```

This is stronger than LRS because max-cut CD gives the integrand correction
nonnegative after integration.  It is fully rational and avoids algebraic
Perron vectors.

Local exact scout:

```text
script: problems/23/writeup/_codex_load_psc_gate.py
census N<=11: cases=189447, LOAD-PSC-25 violations=0, LOAD-PSC-50 violations=0
min_margin=0 at C5[2]-type cenI?rFf_{N? with Gamma=100, R_load=10, Xi_T=0
Mycielskian C5/C7 spot: 8 cuts, violations=0, min LOAD-PSC-25 margin=9860719/4536000
```

This has been posted to Claude as `2026-06-29T21:20:00Z` for full-battery
Fraction validation.

## Codex Note: Prefix Form Of LOAD-PSC-25

LOAD-PSC-25 is equivalent to the full-threshold inequality

```text
25 * sum_v T(v)(T(v)-N) + N * (TV_B(T)-TV_M(T)) <= Gamma * (N^2 - 25|M|).
```

A stronger bottom-prefix form survived local exact tests.  Let
`0=t_0<t_1<...<t_r` be the distinct `T`-levels and
`H_j={v:T(v)>t_j}`.  Put

```text
D = N^2 - 25|M|,
sigma_j = delta_B(H_j)-delta_M(H_j),
w_j = t_{j+1}-t_j.
```

For every prefix `k`, the tested inequality is

```text
sum_{j<k} w_j * ( D*|H_j|
                  - 25*(2*t_j+w_j-N)*|H_j|
                  - N*sigma_j ) >= 0.
```

The full prefix `k=r` is LOAD-PSC-25.  In truncated-TV form, for
`u_v=min(T(v),tau)`, this is

```text
N*(TV_B(u)-TV_M(u)) <= sum_v ((N^2+25N-25|M|)*u_v - 25*u_v^2)
```

for the special nested truncations `u=min(T,tau)`.

Exact scout:

```text
census N<=11: 189447 configs, prefix violations=0, min prefix=0 at C5[2]
structured_cases(): violations=0, min prefix=122400 at two-lane-L8
```

A stronger all-box/all-subset version is false.  Since the margin is concave in
`u`, all-box testing reduces to vertices `u=T*1_S`; it already fails at
`cenG?`F`w`, N=8, `mask=64`, margin `-680`.  Thus any proof must use that
`{T>t}` is a nested superlevel family, not an arbitrary subset family.

Posted to Claude as `2026-06-29T22:15:00Z` for full-battery exact validation.

## Codex Note: Deposit Half Structural Form

For a full-low prefix band `a=t_j`, `b=t_{j+1}` with `2b<=N`, the
`c=25` deposit band is

```text
w * ( [N^2 - 25m + 25(N-a-b)] |H| - N sigma(H) ) >= 0,
```

where `H={T>a}`, `m=|M|`, `sigma=delta_B(H)-delta_M(H)`, and `w=b-a`.

Writing `h=|H|`, `non(H)=# nonedges across H | V\H`, and `dm=delta_M(H)`, we have

```text
h(N-h) - sigma(H) = non(H) + 2 dm.
```

Thus the deposit band is equivalent to the structural cross-slack inequality

```text
N * ( non(H) + 2*delta_M(H) )
  >= h * ( 25m - N h - 25(N-a-b) ).          (DEPOSIT-XSLACK)
```

Only bands with positive right-hand side need work.  Local exact scan:

```text
full-low bands tested: 507834
active right-hand side >0: 1679
minimum structural margin: 57/2
```

The crude sufficient condition `N h >= 25m` is false, and even the corrected
complete-bound condition `N h + 25(N-a-b) >= 25m` is false.  The missing piece
is precisely the cross slack `non(H)+2 delta_M(H)`.

For `c=5`, termwise deposit is false: first local counterexample
`cenJ????B_F~}?`, N=11, m=3, interval `[5/3,5]`, `h=3`, `sigma=16`, band `-890`.
So coefficient-5 prefix requires amortization even within the nominal deposit
region, while coefficient-25 has a clean termwise deposit half.

## Codex Note: LOW-XSLACK Simplification

The threshold-free low-band strengthening posted to Claude as `LOW-XSLACK` has a simpler form.  For any superlevel `H`,

```text
non_cross(H)+2*delta_M(H) = |H|(N-|H|) - sigma(H),
```

where `sigma(H)=delta_B(H)-delta_M(H)`.  Therefore

```text
N*(non_cross(H)+2*delta_M(H)) >= |H|*(25|M|-N|H|)
```

is equivalent to

```text
(N^2-25|M|)*|H| >= N*sigma(H).          (LOW-CD-CAP)
```

Thus the c=25 deposit half would follow from the uniform CD-surplus cap
`D|H| >= N*sigma(H)` for every load band `[a,b]` with `2b<=N`.  The condition is false for arbitrary load superlevels; local exact scan gives 2466 violations, first `cenG?`F`w` with margin `-4`.  Its possible validity is specifically tied to the low-band condition `2*t_{j+1}<=N`.

## Codex Note: LOW-GAMMA-CAP And Pressure-Surplus Hall

Claude full-battery verified both low-half deposit caps:

```text
LOW-XSLACK:    |H|*(N^2-25|M|) >= N*sigma(H)
LOW-GAMMA-CAP: |H|*(N^2-Gamma) >= N*sigma(H)
```

for every consecutive load band `[a,b]` with `2b<=N`, `H={T>a}`.  The second is stronger and is the clean square-deficit form of the deposit half.  It is false outside the low half; local scan gives straddle/high violations, so the threshold condition is exact.

For the withdrawal side, a candidate pressure handshake was posted to Claude.  With `eta=N^2/25-|M|`, band split including `theta=(N+eta)/2`, and

```text
alpha_j = 25*(N+eta-(t_j+t_{j+1})),
```

define per K-component prefix source and volume:

```text
Source_C(k) = sum_{j<k, alpha_j>0} Delta_j*alpha_j*|H_j cap C|,
Volume_C(k) = sum_{j<k, alpha_j<0} Delta_j*(-alpha_j)*|H_j cap C|.
```

The tested pressure Hall inequality is

```text
sum_{j<k} 5*N*Delta_j*sigma_j
  <= sum_C max(0, Source_C(k)-Volume_C(k)).
```

Local exact scout: census `N<=11` plus structured cases, `868318` prefixes, `0` violations, equality only at C5[2]-type zero-pressure prefix.  This would provide the global-pressure part (B) of Claude's corrected two-commodity transport skeleton; same-component volume Hall remains the other half.

## Codex Note: Volume Hall As Component Truncated-Moment Bound

`VOLUME-COMPONENT-HALL` has an equivalent load-only form.  For a prefix ending at level `tau`, let

```text
u_v = min(T(v), tau).
```

For a K-component `C`, the prefix balance is

```text
Bal_C(tau) = 25 * sum_{v in C} ((N+eta)*u_v - u_v^2),
eta = N^2/25 - |M|.
```

Therefore the same-component volume Hall condition is exactly

```text
sum_{v in C} u_v^2 <= (N+eta) * sum_{v in C} u_v       (VOL-TRUNC-COMP)
```

for every K-component C and every truncation level tau drawn from `{0, theta} union T-values`, with `theta=(N+eta)/2`.  The naive pointwise explanation `T(v)<=N+eta` is false: local exact scan gives 1669 violations, first `cenG?`F`w` with max load `10` and `N+eta=214/25`.  Thus volume Hall is a genuine component-level truncated second-moment inequality.

## Codex Note: PRESSURE-SURPLUS Current Frontier

Claude full-battery verified `PRESSURE-SURPLUS-HALL`, and Codex's local mirror also found

```text
configs = 189504
rows    = 868464
violations = 0
min margin = 0 at C5[1]
```

With `eta=N^2/25-|M|`, `theta=(N+eta)/2`, and `u_v=min(T(v),tau)`, the pressure inequality is exactly

```text
N * Xi(u) <= 5 * sum_v u_v * (N + eta - u_v),
Xi(u)=TV_B(u)-TV_M(u).
```

The component-volume side gives

```text
sum_C (Source_C-Volume_C) = 25 * sum_v u_v*(N+eta-u_v).
```

After `VOLUME-COMPONENT-HALL`, each component balance is nonnegative, so `PRESSURE-SURPLUS-HALL` is precisely this prefix-TV inequality. Claude/GPT-Pro also observed the component-volume truncation is unimodal and therefore collapses to the single untruncated component inequality `(CV)`:

```text
sum_{v in C} T(v)^2 <= (N + N^2/25 - |M|) * sum_{v in C} T(v).
```

Useful algebra for pressure: define

```text
P(tau)=5*sum_v u_v*(N+eta-u_v) - N*Xi(u).
```

For `tau >= theta`,

```text
P'(tau)=5*(N+eta-2*tau)*|{T>tau}| - N*sigma({T>tau}) <= 0,
```

so post-theta prefixes are controlled by the endpoint. The hard part is the cumulative pre-theta pressure bound plus the full endpoint; the proof cannot be reduced to any of the following tested shortcuts.

Dead shortcuts:

```text
1. Eta-free pressure bound:
   N*Xi(u) <= 5*sum_v u_v*(N-u_v)
   false: 386 local violations; first in two-lane-L8.

2. TRUNC-BRES + scalar moments:
   the moment implication needed to upgrade Xi(u)<=5*sum(N-u) to pressure
   is false: 961664/962214 local rows violated; first F?bBo.

3. Pre-theta termwise source >= pressure:
   false: 149603 local pre-theta band violations.

4. Monotone sigma(H)/|H| over pre-theta levels:
   false: 39011 local configs with a decrease; first klane12.

5. Minimum-weight simplification
   N*Xi(u) <= 5*(N+eta-2*tau)*sum_v u_v for tau<=theta
   false: 230895 local violations.

6. Full endpoint implies every c=5 prefix:
   false: max full-minus-min-prefix gap 7136018 at klane16.
```

Remaining pressure lemma, in its sharpest form:

```text
For every truncation u=min(T,tau),
N*(TV_B(u)-TV_M(u)) <= 5*sum_v u_v*(N+eta-u_v).
```

Any proof must use the ordered superlevel/coarea structure of `T`; arbitrary box/subset versions and coarse scalar BRES-style bounds are too weak.

## Codex Note: Truncation-TV Cap Hierarchy

For `u=min(T,tau)` and `S=sum_v u_v`, three cumulative TV caps have now survived local exact sweeps:

```text
TRUNC-TV-LOW:  Xi(u) <= 5*S
TRUNC-BRES:    Xi(u) <= 5*(N^2-S)
PARAB-TV:      Xi(u) <= 5*S*(1-S/N^2)
```

`TRUNC-BRES` is full-battery verified by Claude. `TRUNC-TV-LOW` and `PARAB-TV` are posted to Claude for full-battery gates. Local census `N<=11` results:

```text
TRUNC-TV-LOW: rows=962214, violations=0, min=275/19.
PARAB-TV:     rows=962214, violations=0, min=0 at FCp`_.
```

The termwise explanations are false:

```text
sigma(H) <= 5|H|                 false: 1376 local violations.
pre-theta termwise pressure cap   false: 149603 local violations.
```

The scalar bridges from these TV caps to PRESSURE-SURPLUS are also false:

```text
min(TRUNC-TV-LOW, TRUNC-BRES) bridge: 675227 violations.
PARAB-TV + Q <= eta*S + S^2/N:         3779 violations.
PARAB-TV + Q <= eta*S + S(N^2-S)/N:    41952 violations.
```

Thus the pressure proof cannot split into an independent TV cap plus an independent scalar moment inequality.  It must use a coupled load/TV argument along the ordered superlevel family of `T`.

## 2026-06-30 Codex/Claude pressure updates

- `PARABOLIC-TRUNC-TV`, `Xi(u) <= 5*S*(1-S/N^2)`, is false on the full battery. Claude exact result: `rows=962457`, `violations=28`, first `klane-L12k4`, `N=65`, `|M|=15`, `tau=119`, margin `-12711/845`; minimum around `-3295.26` at `klane-L16k5`. Keep only the two linear caps `Xi<=5S` and `Xi<=5(N^2-S)`.
- Local eta-coefficient probe for pressure `N*Xi <= 5*sum u*(N + c*eta - u)` found positive-deficit rows `386` and max required coefficient `c=205/207` at `cenJ???E?pNu\\?`. The eta term is therefore nearly sharp; coefficient-saving shortcuts are unlikely to explain `PRESSURE-SURPLUS-HALL`.
- Submitted `PSC-50` Perron square-coarea certificate to Claude for exact testing. Local structured floating scout: `cases=10`, `violations=0`, worst margin `26.7221833` at `two-lane-L8`; wider floating scout reached census `N<=10` with no violation output before the nonessential structured tail stalled and was stopped.
