# Slack-CAGE Proof Target

Status: new exact-supported candidate, not proved.  This replaces the false
uniform DEFICIT-CAGE Hall transport suggested by GPT-Pro on 2026-07-01.

## Definitions

Fix a connected-B gamma-minimum maximum cut.  Let `M` be the bad edges,
`m=|M|`, and `cyc[g]` the shortest B-geodesic rows for `g`.

For a fixed bad row `Q in cyc[f]` and vertex set `U`, define the row-cage
demand

```text
D_Q(U)
  = sum_{g in M} (1/|cyc[g]|)
      * sum_{P in cyc[g], V(P) subset U} |V(P) cap V(Q)|.
```

Let

```text
eta = N^2/25 - m,
sigma(U) = delta_B(U) - delta_M(U).
```

The proposed **slack-CAGE** inequality is:

```text
D_Q(U) <= |U| + sigma(U) + eta
```

for every fixed row `Q` and every `U subset V`.

At `U=V`, this gives rowwise GERSH:

```text
sum_{v in Q} Tw(v) = D_Q(V) <= N + eta.
```

Thus slack-CAGE implies the corrected ROWSUM/GERSH target recorded in
`CV_PERCOMP_SPECTRAL.md`.

## Dead Uniform Hall Variant

GPT-Pro first suggested a uniform-capacity Hall condition:

```text
D_Q(U) <= ((N + eta)/N) * |U|.
```

Exact gate:

```text
python problems/23/writeup/_codex_deficit_cage_gate.py \
  --stop-first --min-n 7 --max-n 9 --two-lane-max 20 \
  --blowup-t 3 --blowup-nmax 20 --max-cuts 4
```

Result:

```text
FAIL at two-lane-L8
N=27, m=4, A=1304/25
Q=(0,1,2,3,4,5,6)
U=(0,1,2,3,4,5,6,7,8)
D_Q(U)=24
((N+eta)/N)|U|=1304/75
excess=496/75
```

The failure shows the deficit budget cannot be spread uniformly over all
vertices.  It must localize through cut slack or a more structured corridor
capacity.

For the same witness,

```text
|U|=9,
sigma(U)=18,
eta=629/25,
```

so slack-CAGE gives `24 <= 9+18+629/25`.

## Surgical Exact Probe

A scratch exact probe tested slack-CAGE on:

- all subsets of pure `C7` and `C9`;
- all subsets of the N=10 PMS equality atom `I?BD@g]Qo` with side
  `0001111000`;
- row/corridor interval subsets for two-lane `L=8,12,20`.

Result:

```text
C7: PASS, min margin 24/25 at U=empty
C9: PASS, min margin 56/25 at U=empty
I?BD@g]Qo: PASS, min margin 1/3 at U=V for row (7,5,8,6,9)
two-lane-L8 rowsets: PASS, min margin 604/25 at U=V for row (0..8)
two-lane-L12 rowsets: PASS, min margin 1296/25 at U=V for row (0..12)
two-lane-L20 rowsets: PASS, min margin 3544/25 at U=V for row (0..20)
```

This is not a full gate; it is a small sanity check before asking Claude to
run a full exact battery.

## Proof Interpretation

The candidate says every row-overlap cage either has enough vertices, enough
max-cut slack on its boundary, or enough global bad-edge deficit.  The full
set `U=V` has zero cut slack and recovers exactly the corrected row cap.

The likely proof shape is a max-cut coarea/Hall argument over cages `U`,
where `sigma(U)` pays local concentration and `eta` pays global sparsity.  It
is strictly weaker than the false uniform-Hall transport but stronger than the
desired rowwise GERSH.
