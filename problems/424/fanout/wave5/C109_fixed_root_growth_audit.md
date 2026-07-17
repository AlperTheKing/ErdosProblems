# C109 fixed-root growth audit

## Verdict

Accepted as finite exact evidence only.  C109 neither proves a uniform
fixed-root bound nor constructs an unbounded family, and it does not prove
C104-BIN.

## Independent replay

All 21 manifest entries match their pinned SHA-256 values.  The independently
rerun Python verifier, normally and under `python -O`, is byte-identical to
the submitted output with SHA-256 `699AEC50...895D`; it refactors and audits
all 16 record events.

The C++ bin scanner was independently rebuilt and rerun through
`4,000,000,000`.  Its output is byte-identical with SHA-256
`4D5620B3...AE67`, reproducing `106,360,959` hard sources, classification
digest `08eb5810482ec820`, and zero eventwise C104-BIN failures.

The fixed-root record scanner was independently rebuilt and rerun through
the same endpoint.  All mathematical JSON fields are identical; the only
differences are the two elapsed-time measurements.  It reproduces maximum
`d=16` for root `54` at `h=1,559,219,514` and root `62` at
`h=298,274,514`.

## Scope

Both roots lie in dyadic bin `j=5`, so one root alone violates the linear
C104-BIN inequality only at threshold `D>=33`, requiring a witnessed source
with `d>=34`.  The observed records do not reach this.  The finite chain of
missing endpoints for a fixed root does not bound the pair count of sources
divisible by one such endpoint, so it supplies no asymptotic theorem.

