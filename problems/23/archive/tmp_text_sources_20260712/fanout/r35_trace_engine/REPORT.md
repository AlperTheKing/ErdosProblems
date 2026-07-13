# R35 anchored lock-trace engine

## Delivered

Implemented `problems/23/writeup/_codex_r35_anchored_locktrace_gate.py`.
The checker uses exact finite sets, integer counts, and deterministic graph
search. It has no floating-point or randomized branch.

The corrected state surface retains:

- `CollisionObligation(owner, other, producer_atom, occurrence, copy, half,
  component)`;
- `Source(source_x, source_y, half, component)` with global base/component
  coherence checked across the matching;
- `RowOccurrence(atom, row, position)`;
- a matching-dependent `LockTraceContext` and unmatched root;
- five checked step kinds: eligible source, matched obligation, producer
  occurrence, occurrence obligation, and occurrence source.

Anchoring validation requires every row's endpoint pair to equal its atom,
atom endpoint pairs to be injective, rows to be vertex-simple, and no row to
be shared across families.

## Terminal semantics

The finite search returns exactly one of:

- `augment`: carries a rechecked larger coherent matching;
- `trade`: carries explicit new obligations, eligibility, matching, and
  either strict defect decrease or checked nonincrease plus lower row rank;
- `closedCycle`: carries a reachable directed cycle only;
- `deadEnd`: carries the full reachable acyclic search and checked steps.

Repeated cursors are never interpreted as trades. Neither `closedCycle` nor
`deadEnd` is promoted to progress without a separate graph theorem.

## Exact tests

Command:

```powershell
python problems/23/writeup/_codex_r35_anchored_locktrace_gate.py --workers 8 --output tmp/fanout/r35_trace_engine/gate_result.json
```

Result canonical SHA256:
`ca4aaed58a723588cbccf5e9e1fe96015083521461990b1f948309d2ad247454`.

The self-test exercised all four terminal constructors and confirmed that
obligation half, source, and row-occurrence cursors remain distinct.

The pinned N=12 heavy artifact was reconstructed from graph6
`K?ABBBo}CuBw`, choice `[1,1,8,0]`. The exact counts reproduce demand 64,
matched 46, defect 18, with four endpoint-anchored selected rows. The census
artifact exports only used assignment arcs, so the unmatched-root trace on
that restricted relation honestly returns `deadEnd`; no missing eligibility
arc or trade is inferred.

The available 2943 certificate was integrity-audited: 17 owners, all 131071
nonempty owner shores, demand/flow 23108, minimum shore slack 3, and 28
selected P5 keys. Its pinned file SHA256 is
`08ebc720c3c79306e7a2f46e9460486d1b443b78330884edc8bd60eeb7d93709`.
This is a certificate audit, not a rebuild of the 8,363,362-key relation.

Independent `tmp/fanout/r32_n12_fullbank/verify.py` verdict: `PASS`; all
reported checks are true, including pinned inputs, N=12 coverage, tuple
replay, minimizer completion, battery owner ledgers, and R29 exact checks.

## Hashes

- Engine SHA256:
  `4771b14a96b911834c8ec58cf6a3fac0592a6e01b6eb2f7356c64ee726f4128f`.
- Gate-result file SHA256:
  `ed764c5ba06ab787c2704ea2c041d6a6fcb8ad0db25d3e968b1885af3b548438`.

## Boundary

This artifact implements and tests the corrected anchored checker surface.
It does not prove `closedCycle`/`deadEnd` exclusion or
`realSinkNeutralAttachmentClass_hasAugment`; those remain graph-facing
mathematical obligations.
