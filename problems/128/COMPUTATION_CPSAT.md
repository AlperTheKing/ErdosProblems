# Erdős Problem 128 — Full CP-SAT wave

## Scope

This artifact records the single permitted full-graph CP-SAT wave at `n = 20`. It neither proves infeasibility nor authorizes a search at any other order.

## Exact model

- Solver: OR-Tools CP-SAT 9.14.6206, Python 3.12.4, Windows 11.
- Primary variables: one Boolean `e_uv` for each of the `C(20,2) = 190` unordered vertex pairs.
- Triangle-free constraints: all `C(20,3) = 1,140` inequalities `e_uv + e_uw + e_vw <= 2`.
- Half-set constraints: all `C(20,10) = 184,756` inequalities requiring at least 9 of the 45 internal edge variables.
- Safe maximal-triangle-free restriction: 3,420 Boolean AND auxiliaries, 10,260 linear AND constraints, and 190 common-neighbour disjunction inequalities.
- Safe symmetry breaking: 19 degree-order inequalities `d(0) >= ... >= d(19)`.
- No special graph family, asymptotic relaxation, or unproved pruning was used.

The initial proto contained 3,610 Boolean variables and 184,965 `LinearN` constraints. The latter split exactly as `184,756 + 190 + 19`; OR-Tools separately reported 6,840 `Linear2` and 4,560 `Linear3` constraints. The serialized model proto was 23,630,236 bytes.

## Command

```powershell
python -B problems/128/search/cpsat_search_full.py --wall-seconds 600 --workers 8 --memory-mb 8192 --seed 128
```

The actual invocation piped output to `problems/128/search/cpsat_full_8w_600s.log` with `Tee-Object`.

## Result

- Status: `UNKNOWN`.
- Candidate count: 0; no `cpsat_candidate.json` was created.
- Build time: 23.563 s.
- Solver time limit after building: 576.343 s.
- Solver-reported wall time: 576.938 s.
- Script-measured total wall time: 601.094 s.
- Search statistics: 5,222 branches, 147,184 Boolean propagations, 185,929 integer propagations, 6,789 LP iterations.
- Feasible-solution repository entries: 0.

The configured total budget was 600 s. CP-SAT exceeded its calculated remaining limit during shutdown, making the measured script total 1.094 s over that budget. This overrun is recorded explicitly; no rerun or follow-on formulation was launched.

`UNKNOWN` is not an UNSAT certificate and supplies no negative result for Problem 128. Under the governing direct-route exit rule, this CP-SAT branch is exhausted.

## Independent verifier

`problems/128/search/cpsat_verify.py` is OR-Tools-free. If a candidate had existed, it would have:

1. checked the edge list and adjacency list for exact agreement;
2. enumerated all 1,140 triples for triangles;
3. enumerated all 184,756 ten-sets;
4. counted every ten-set's internal edges by two independent exact methods (edge-set membership and adjacency bitmasks).

It was not run because no candidate existed.

## SHA-256

- `cpsat_search_full.py`: `af124e230e15a74b0c91aec5883a48e29d49f8b5fee016ee6d966af64c06dd66`
- `cpsat_verify.py`: `bb425c1199ba3e5767df42125351c77c15ba0f108de5ee66c9411baacbadec12`
- `cpsat_full_8w_600s.log`: `48f939467c72d64a956ede49c64ae5ba9e79a0e96f0d20cb07816d2d4abdb4df`
- `cpsat_result.json`: `2889e9ad5718e85d6f557f2145e7f06b28a970983e3a77cf4185126f0082c1fa`
- Model proto (serialized in memory): `08ac150b1a8fef18344186a1304f86614126609662d65f59cab1301ff71dfdb6`
