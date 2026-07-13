# R29 Gamma / shortest-row gate — d04

## Verdict

**NOT VERIFIED (input-underdetermined).** I do not accept `Gamma = 34575`, the
`707 = 676 + 28 + 3` rigid-atom histogram, or the claim that each of 676
selector atoms has exactly 680 shortest rows. The workspace has no complete
R29 graph constructor, edge list, atom list, or selected-row tuple bearing the
claimed `00186166...` prefix. The R29 archive is a 3,433-byte prose summary.

Accordingly, no shortest-path enumeration was possible from graph data. This
is a proof gap, not a counterexample to the numerical claims.

## Exact audit performed

`python audit_inputs.py` searched the relevant R29 production, coordination,
and fanout text/code trees with ripgrep for the claimed SHA prefix and defining
count phrases, then SHA-256-hashed every hit of at most 20 MB. It used no
floating-point operations or theorem-prover evaluation. Machine-readable
output is `input_audit.json`.

The only production sources containing the R29 claim are:

- `problems/23/writeup/WALL_ATTACK_R29_GPTPRO56.md`, 3,433 bytes, SHA-256
  `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`;
- `coordination/CLAUDE_TO_CODEX.md`, 1,287,539 bytes at audit time, SHA-256
  `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`.

Both repeat aggregate assertions. Neither supplies the 2,943 labeled vertices,
8,422 labeled edges, atom endpoints/classes, nor the selector source-target
pairs required to run BFS and enumerate all shortest paths.

## Explicit falsifiers / witnesses required

For a supplied graph `G`, a checker must reject the histogram with any one of:

1. an atom endpoint pair whose BFS distance differs from the asserted row
   length;
2. an explicit shortest vertex sequence absent from the claimed unique-row
   set (extra-row witness);
3. a claimed row containing a non-edge, repeated vertex, wrong endpoints, or
   length greater than the BFS distance (missing/invalid-row witness);
4. a rigid atom having shortest-path multiplicity other than 1;
5. a selector atom having shortest-path multiplicity other than 680;
6. atom-class totals different from double-star 676, circuit 28, cable-seed 3,
   selector 676.

For Gamma, an independently checkable certificate must define Gamma from the
graph/row data and provide either an exact exhaustive computation or matching
integer lower/upper certificates. A value unequal to 34575 is the explicit
numeric falsifier. No such inputs or certificates are present.

## Missing incidences visible from the archive

The prose aggregate decomposition mentions 3,380 selector-C5 edges, 15 private
cable-seed-C5 edges, and 6 cable edges, but gives no endpoint lists. It also
omits the left/right selector partition, the pairing of lock vertices into 676
C5s, the three private C5 layouts, and exact cable attachment labels. Distinct
endpoint assignments preserve the prose counts while changing BFS rows, so the
requested histogram is not determined by the available source.

## Proof gaps

- complete canonical graph bytes and full SHA-256;
- exact atom endpoint list and class labels;
- definition and certificate for Gamma-minimality;
- exhaustive BFS predecessor-DAG enumeration for all 1,383 atoms;
- claimed row serialization to permit set difference and explicit
  extra/missing-row witnesses.

## Lane artifact hashes

- `audit_inputs.py`: `1dfde0ac733084519580dc1e4cd1ffbb9552e97a8a81e89db9fb63164afda8c5`
- `input_audit.json`: `0b998a6192dc40d4e6b5903b6a38b70bc0da7efcc5181b5e103c6c3ee8996e74`

The audit JSON includes references to other fanout reports/event logs and this
lane's prompt/script because they repeat the phrases; none is treated as graph
data. I did not edit production, coordination, Lean, or `PROGRESS_CODEX.md`.
