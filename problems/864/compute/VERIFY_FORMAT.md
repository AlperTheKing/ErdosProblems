# Candidate Verification Format

`verify_census.py` accepts a single JSON object, a JSON array of objects, or
one object per nonblank JSONL line. Duplicate JSON keys and non-standard JSON
numbers (`NaN`, `Infinity`) are rejected.

Each candidate has these required fields:

```json
{
  "N": 9,
  "A": [1, 3, 7, 9],
  "exceptional_sum": 10,
  "exceptional_multiplicity": 2,
  "objective": 4,
  "bound": 4,
  "status": "optimal"
}
```

- `N` is a positive integer and `A` is a duplicate-free integer subset of
  `[1,N]`. Booleans and floating-point values are not accepted as integers.
- `exceptional_sum` and `exceptional_multiplicity` claim the unique sum having
  multiplicity at least two. Use `null` and `0` when there is no repeated sum.
- `objective` is the claimed cardinality and must equal `|A|`.
- `bound` is an exact integer upper bound for the maximization objective. It
  must be at least `objective`, and must equal it when `status` is `optimal`.
  The solver-emitted name `diagnostic_best_bound` is accepted as an alias.
  Integer-valued JSON decimals such as `4.0` are parsed exactly and normalized
  to `4`; a fractional value is rejected. If both names occur, they must agree.
- `status` is case-insensitive. Accepted classes are `optimal` (`optimum`,
  `proven_optimal`), `feasible` (`sat`, `satisfiable`, `candidate`), and
  `unknown` (`timeout`, `time_limit`, `not_solved`). A witness cannot carry an
  infeasible status.

The verifier checks metadata consistency only. A record saying `optimal` is
not, by itself, an independently checkable proof of the global upper bound;
the output therefore sets `optimality_certificate_checked` to `false`.

For every valid-domain `A`, the output reports every nonzero unordered-sum
multiplicity, all representations of every repeated sum, collision and
multiplicity statistics, diagonal collisions, reflection pairs about the
actual exceptional sum, and a maximum-cardinality Sidon subset. The latter is
found by an exact conflict-hitting-set search up to `--sidon-limit` (default
24). Larger admissible records use the exact one-exception formula; larger
inadmissible diagnostic records omit that statistic.

Commands:

```powershell
python problems/864/compute/verify_census.py --self-test
python problems/864/compute/verify_census.py candidates.json
python problems/864/compute/verify_census.py candidates.jsonl
Get-Content candidates.jsonl | python problems/864/compute/verify_census.py --input-format jsonl -
```

One compact JSON report is written per record. Exit status is `0` when all
records verify, `1` when any candidate fails, and `2` for input/read errors.
