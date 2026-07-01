# Delta=0 Proof Skeleton Checklist

Status: proof skeleton assembled, not shipped.  The remaining work is a
proof-grade S2 reduced-theta audit and formalization.

## Target

Close the delta=0 remainder of Erdős #23 by proving the remaining equivalent
scalar inequality.  The active finite/geometric route has reduced the proof to
terminal-shadow switches and the S1/S2 shortest-geodesic theta package.

## Cap Side

Claim:

```text
No deficient cap component survives in a completed selected switch.
```

Pieces:

1. Classification.

```text
deficient cap => nested L/(L+2) core + pure odd-cycle baggage.
```

Status: Claude/GPT-Pro classified; finite shadows exact-verified.

2. L=5 forcing.

```text
If L>=7, S2 gives terminal-product normal form with a nonempty shared middle
corridor.  A universal shared blue edge can be recut to replace two bad
terminal edges by one shared-corridor bad edge, contradicting gamma-minimality.
```

Status: canonical stretched cores and one-edge attachments exact-verified;
arbitrary-realization proof reduces to S2 reduced-theta audit.

3. Local sign.

```text
L=5/7 cap atom has R_local = 25/4 >= 0.
```

Status: exact-computed and mirrored.

Cap conclusion:

```text
cap side closed modulo S2 audit.
```

## Row Side

Claim:

```text
After stage-0 rare-cost matching, every residual component row misses at most
one residual exit.
```

Pieces:

1. TH-Corridor reduction.

```text
Any double miss gives a shortest exit co-witness corridor
e0,g1,e1,...,gk,ek
with endpoint terminal slack positive and internal exits f-tight.
```

Status: stated in `NO_TWO_HOLE_RESIDUAL_CORRIDOR.md` and
`TH_RARE_SIDE_BLOCK_SEPARATION.md`.

2. TH-long / endpoint hinge rigidity.

```text
If one endpoint has lambda(e)>L0, the corridor row-union disk contains a
triangle or a blue path for some involved bad edge h of length <= ell(h)-3.
```

Status: Claude/GPT-Pro classify as S2 mirror.

3. TH-rare / rare monotonicity + shadow separation.

```text
If both endpoints have lambda=L0, cost-flat alternating shadows either
interact, where S2 gives rare monotonicity and then a negative rare-cost
exchange, or are disjoint and separated by mu(F0), hence not in one residual
component.
```

Status: Claude/GPT-Pro classify Atom B proof skeleton complete; exact gates
support component-local row-miss and all-min tie robustness.

4. Exact gates.

```text
_slack_gate.py:
  switches=119, f-e pairs=5404, mismatch=0, nonzero_slack_lt2=0.

_codex_th_corridor_gate.py:
  tested=182, ok=182, row_miss={0:989,1:72}.

_codex_stage0_all_min_rowmiss_gate.py:
  H2 tested=119, ok=119.
  inherited enumerated ok=139, too_many=43, row_miss_fail=0.

_codex_mu_separation_gate.py:
  H2 tested=119, ok=119.
  inherited tested=182, ok=139, too_many=43, fail=0.
```

Row conclusion:

```text
row side closed modulo S2/RM hypothesis audit.
```

## Common Remaining Audit

File:

```text
problems/23/writeup/S2_REDUCED_THETA_AUDIT.md
problems/23/writeup/S2_REDUCED_THETA_LEMMA.md
```

Required checks:

1. Terminal-prefix property.
2. Shortest-row property.
3. Reducedness / no smaller split-rejoin pair.
4. Strictness source: positive even slack or annulus excess.
5. No already-existing intermediate terminal door.

Applications to check:

```text
cap L=5 forcing,
row TH-long / endpoint hinge rigidity,
row TH-rare / rare monotonicity.
```

## Shipping Status

Do not mark complete yet.

```text
Proof skeleton: complete.
Exact finite consequences: verified in current gates.
Proof-grade prose: pending S2 audit consolidation.
Lean / formal-conjectures PR: pending.
```
