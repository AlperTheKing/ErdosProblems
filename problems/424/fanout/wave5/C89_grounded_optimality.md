# C89: grounded-image optimality is false

## Verdict

The true grounded fixed point `G` is not always the worst one-step image for
the C23 shell excess.  The first exact failure is at cutoff `704`:

\[
 \max_S(H_{F(S)}(704)-Q_{F(S)}(704))=-4,
 \qquad H_G(704)-Q_G(704)=-5.
\]

Thus the natural strengthening "the grounded image minimizes shell slack"
is false.  This does not falsify C23: both excesses remain negative.

## Exact scan

At every hard cutoff, the script:

1. rebuilds the grounded set by ascending exact closure;
2. computes its integer shell excess;
3. solves the exact Boolean forward-source/one-step-image model; and
4. requires an `OPTIMAL` CP-SAT status and replays the returned membership
   sets through the C78 exact verifier.

Through `1000`, the grounded set is optimal at `42` of `66` hard cutoffs.
The first difference is `704`, and all later differences in this range are
one unit.

Through `5000`, it is optimal at `141` of `410` hard cutoffs.  The gap

\[
 \max_S(H_{F(S)}-Q_{F(S)})-(H_G-Q_G)
\]

has maximum `4`, average `1.8`, and value `3` at the last tested hard cutoff
`4980`.  These bounded finite values do not prove a uniform bound.

## Consequence

C88's canonical shell backbone at the four zero-slack cutoffs cannot be
promoted by claiming that `G` is globally extremal.  Any proof must control
non-grounded image optimizers directly, although a bounded or sublinear
optimizer-versus-grounded gap remains an exact-testable weaker possibility.

## Reproduction

```powershell
python -O problems/424/compute/wave5/C89_grounded_optimality.py `
  --stop 1000 --workers 64 --seconds 30 `
  --output problems/424/compute/wave5/C89_grounded_optimality_1000.json

python -O problems/424/compute/wave5/C89_grounded_optimality.py `
  --stop 5000 --workers 64 --seconds 30 `
  --output problems/424/compute/wave5/C89_grounded_optimality_5000.json
```

The `1000` run is byte-identical on replay.

```text
68DB42DECC6A6BA77413D88B82429E52BDF16E14FD292C39997A6672B7712405  C89_grounded_optimality.py
B3B35F3E4670D7FC01DB36B618EB4C9DA6E6F264E73ADD519B44BD4E8E1C5A1D  C89_grounded_optimality_1000.json
B3B35F3E4670D7FC01DB36B618EB4C9DA6E6F264E73ADD519B44BD4E8E1C5A1D  C89_grounded_optimality_1000_replay.json
31FA385B78E72F3ACAD5C86D7C99C7038D0593C9F179030FB6D0D3632ADE82AD  C89_grounded_optimality_5000.json
```
