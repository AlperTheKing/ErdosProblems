# EDGE-SHADOW-CAP audit

Status: proposed local strengthening is false; saturation-only remnant
survives the N<=11 gamma-min connected-B census.

## Candidate

For a cut edge `e=uv in B`, define

```text
r_e(f)=p_f(u)+p_f(v)-tau_f(e),
```

where `tau_f(e)` is the probability that a shortest `B`-geodesic for
bad edge `f` uses `e`.

The proposed cap was:

```text
sum_f ell(f) r_e(f) <= N.
```

The pointwise strengthening was:

```text
c_e(x)=sum_f r_e(f)p_f(x) <= 1.
```

For zero-mu edges, `tau_f(e)=0` for every `f`, so the proposed
hierarchy was:

```text
PESC-ZMU: sum_f (p_f(u)+p_f(v))p_f(x) <= 1 for all x,
ZMU-CAP:  T(u)+T(v) <= N,
A-alltie gate: mu(uv)=0 and T(u)=N implies T(v)=0.
```

## Exact checker

```text
problems/23/writeup/_codex_edge_shadow_cap.py
```

It enumerates gamma-min connected-B maximum cuts via `gmin_sides` and
uses exact `Fraction` arithmetic.

## Census results

N=9:

```text
gamma_sides=1916
zmu_edges=4824
PESC-ZMU fails=84
ZMU-CAP fails=43
A-alltie gate fails=0
EDGE-SHADOW-CAP fails=2395
POINTWISE-ESC fails=4165
```

First witnesses:

```text
EDGE-SHADOW-CAP:
  g6=H?`cn@w, side=111100000, e=(0,6), value=10>N=9.

PESC-ZMU:
  g6=H?AFBo], side=000111100, zero-mu e=(0,6), x=6, value=2.

ZMU-CAP:
  g6=H?AFBo], side=000111100, zero-mu e=(0,6),
  T(0)=0, T(6)=10, T(0)+T(6)=10>N=9.
```

N=10:

```text
gamma_sides=16016
zmu_edges=48282
PESC-ZMU fails=2247
ZMU-CAP fails=0
A-alltie gate fails=0
EDGE-SHADOW-CAP fails=2302
POINTWISE-ESC fails=59137
```

N=11:

```text
gamma_sides=171182
zmu_edges=575612
PESC-ZMU fails=39504
ZMU-CAP fails=147
A-alltie gate fails=0
EDGE-SHADOW-CAP fails=92665
POINTWISE-ESC fails=932060
```

First N=11 `ZMU-CAP` witness:

```text
g6=J??CE@a}?z?, side=10011101100,
zero-mu e=(5,10),
T(5)=0, T(10)=133/12,
T(5)+T(10)=133/12>N=11.
```

## Conclusion

The proposed edge-shadow cap and its pointwise version cannot prove
`A-alltie`; they are false even on small gamma-min census cuts.

The exact qualitative remnant

```text
mu(uv)=0 and T(u)=N => T(v)=0
```

had zero failures through the N<=11 gamma-min connected-B census in
this checker, matching the older A-alltie diagnostics. Any proof of
A-alltie must use a saturation-specific mechanism rather than the
stronger summed capacity `T(u)+T(v)<=N`.
