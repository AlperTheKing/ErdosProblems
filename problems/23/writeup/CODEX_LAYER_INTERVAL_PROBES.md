# Layer-Interval ROWSUM Probes

Status: diagnostic.  These exact tests probe possible layer-prefix
mechanisms for ROWSUM-O.

Script:

```text
problems/23/writeup/_codex_layer_prefix_probe.py
```

It uses exact `Fraction` arithmetic and the gamma-min connected-B cut chosen
by `_h.loads`.

## Dead capacity relaxations

On the triangle-free census through `N<=10`:

```text
layer contribution <= layer size: false, 4990 failures
prefix contribution <= prefix vertex count: false, 3362 failures
prefix contribution <= prefix vertex count + cut defect: false, 516 failures
row contribution <= geodesic support size: false, 614 failures
```

Worst exact witnesses from the probe:

```text
layer-size: I?ABCc]}?, f=(6,8), layer 2, excess 5/3
prefix-size: I?AAD@wF_, f=(3,9), excess 4
prefix-size+defect: I?`DA_wJ?, f=(2,8), excess 4
support-size: I?AAD@wF_, f=(3,9), rowsum 9 over support size 5
```

These are the same failure mode as the row-Hall refutation: ROWSUM uses the
full `N` budget, not only geodesic support or local cut boundary.

## Normalized interval probes

Normalize layer contributions by the extremal scale `N/ell(f)`.

Through `N<=10`, two stronger-looking interval patterns survived:

```text
outside-in paired layers: 0 failures
centered intervals of radius >= 1: 0 failures
```

Full `N<=11` kills both:

```text
outside-in paired layers: 1 failure
centered intervals of radius >= 1: 7 failures
proper centered intervals: 7 failures
```

First/worst exact witnesses:

```text
outside-in: J??CE?{{?]?, f=(6,10), ell=7, outer-pair excess 1/14
centered: J?AEB?cu?}?, f=(0,5), ell=5, centered radius 1 excess 2/5
```

The centered witness has layer contributions:

```text
3/2, 8/3, 4/3, 3, 4/3
```

The centered triple exceeds `3N/ell` by `2/5`, while the full row still
satisfies ROWSUM due to low outer-layer contribution.

## Cut-defect interval correction

The all-proper-interval test

```text
sum_{i in interval} a_i <= |interval| * N/ell(f) + cut_defect(interval)
```

is false already through `N<=8`:

```text
proper interval defect failures: 12
worst: G?`F`w, f=(4,7), interval (4,4), excess 2/5
```

So neither pure normalized interval majorization nor adding ordinary
max-cut defect to intervals is enough for ROWSUM-O.
