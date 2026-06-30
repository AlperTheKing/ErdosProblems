# Spectral Bad-Count Slack Candidate

The universal certificates `ROWSUM-O` and `SPEC` are false for arbitrary
connected-B maximum cuts: the two-lane family in
`_codex_two_lane_p198_counterexample.py` has `rho(O)>N` for length `L>=12`.
However that family has only four bad edges, so it is harmless for Erdős #23
because `beta=|M| << N^2/25`.

This suggests the corrected scalar target:

```text
(SBC)    rho(O) + |M| <= N + N^2/25.
```

There is also a stronger row-sum variant:

```text
(SBC-row)    max_f (O 1)_f + |M| <= N + N^2/25.
```

## Why SBC Implies Erdős #23

Let `m=|M|`.  Since `O` is PSD,

```text
rho(O) >= (ell^T O ell)/(ell^T ell).
```

By the Gram identity,

```text
ell^T O ell = sum_v T(v)^2.
```

By Cauchy and `sum_v T(v)=Gamma`,

```text
sum_v T(v)^2 >= Gamma^2 / N.
```

Also `ell^T ell = Gamma`, so

```text
rho(O) >= Gamma / N.
```

Since every bad edge has odd-cycle length at least `5`,

```text
Gamma >= 25m.
```

Therefore

```text
rho(O) >= 25m/N.
```

Combining with SBC gives

```text
25m/N <= N + N^2/25 - m.
```

Multiplying by `N` and rearranging:

```text
m(25+N) <= N^2(25+N)/25,
```

so

```text
m <= N^2/25.
```

Since `m=beta(G)` for the chosen maximum cut, this proves Erdős #23.

## Equality And Regression Evidence

The candidate is tight at the `C5[t]` extremals:

```text
rho(O)=N,    |M|=N^2/25.
```

Local gate:

```text
python problems/23/writeup/_codex_spectral_badcount_slack.py \
  --max-n 11 --workers 61 --chunksize 64 --two-lane-max 30
```

Result:

```text
census N=5..11 gamma-min loads(): spec_bad=0, row_bad=0
two-lane L=8..30: spec_margin>0, row_margin>0
```

At `N=10`, the C5 blowup equality appears:

```text
min_spec ~= 0 at I?rFf_{N?
min_row = 0 at I?rFf_{N?
```

For the two-lane family, the exact formulas are:

```text
N = 3L+3
|M| = 4
rho(O)=2L-3 + sqrt(4L^2 - 20L + 33)
```

so although `rho(O)>N` for even `L>=12`, the slack term

```text
N^2/25 - |M|
```

dominates the spectral excess.

## Current Status

SBC is only a conjectural repaired certificate.  It is now the highest-value
scalar target because it:

1. survives the two-lane counterexample that killed universal SPEC;
2. is tight at the known extremal family;
3. implies the theorem directly by a one-line algebraic closure;
4. gives spectral excess a place to live when the graph is far below the
   bad-edge threshold.

The proof still needs a new triangle-free/max-cut mechanism.

## Refuted Shortcut: Max Load Slack

Since `rho(K) <= max_v T(v)`, a tempting stronger route was:

```text
max_v T(v) + |M| <= N + N^2/25.
```

This is false in the exact census.

After patching `_codex_spectral_badcount_slack.py` to report the load margin,
the command above gave:

```text
N=8:  load_bad=3
  first: G?`F`w, m=2, Tmax=10, rhs=214/25

N=10: load_bad=11
  first: I?ABCc]}?, m=3, Tmax=40/3, rhs=11

N=11: load_bad=141
  first: J???E?pNu\?, m=3, Tmax=15, rhs=321/25
```

Thus SBC is not a crude Perron row-sum consequence from `K1=T`.  Any proof
must use cancellation/averaging in the bad-edge vector space, or the row-SBC
bound on `O`, not only the largest vertex load.

## Dense-Chord Stress

Script:

```text
problems/23/writeup/_codex_dense_chord_stress.py
```

This starts from the path-plus-two-lanes scaffold and greedily adds many
same-parity path chords while preserving triangle-freeness.  It then checks
whether the displayed parity cut remains maximum.

Observation:

```text
SBC can fail badly on the dense-chord parity cuts,
but all such failures in the tested family are non-maximum cuts.
```

Examples:

```text
L=20, mode=all, limit=24:
  triangle_free=True
  displayed cut=142, CP-SAT optimum=161
  m=24, rho=316.39
  SBC margin=-118.63

L=24, mode=all, limit=24:
  triangle_free=True
  displayed cut=170, CP-SAT optimum=189
  m=24, rho=411.51
  SBC margin=-135.51
```

By contrast, every CP-SAT-verified maximum cut in the same stress family had
positive SBC margin.  This indicates that the missing proof mechanism must use
maximality/CD: triangle-freeness alone does not imply SBC.
