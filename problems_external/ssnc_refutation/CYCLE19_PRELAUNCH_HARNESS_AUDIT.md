# Cycle-19 final pre-launch harness audit

Date: 2026-07-21 (Europe/Istanbul)

Scope: `engine/run_cycle19_cadical.ps1`, `engine/decode_cycle19_model.py`, and
micro-instance SAT/UNSAT/timeout/refusal calibrations only.  The production
`cycle19.cnf` was hashed but never passed to a solver.

## Audited hashes

- launcher: `DD753A4C38EC91E9C8C0A0804C955270C2044F19A77D02E838F423C229E8DBA2`
- decoder: `E0E43B151F32B4659D779FACCFCAA106ADC3B3CED6052BBB858AB8102C4E44F6`
- frozen CNF (read-only hash): `A030330116CF8C7F1DA9A4A84C868D375A8177FDAA3E57B924936113E095EA38`
- frozen manifest: `4CF5469273AD6F2DF524EC21B30379151D174B2533AF0BC463A33A6DDA4D687E`
- CaDiCaL executable: `896177DF9C0C3FCA0A50ED09BB04C6301804C267374DE4DAA006F984D26A1DD7`
- `drat-trim.c`: `3346DBAFA47541EDFD6C1680C46B545ADBB3FE189C39C5B3C99FE9606553F824`
- compiled audit `drat-trim.exe`: `1317EBF80DD38ADA168E0C30FCB2E02993826F44BA10C629026B50C7F087E7E2`
- timeout stub: `C2FE33A7AB810A9AF113BB35D3DA9A8B396487ED2B5CF0281E59810160B06DA2`

## Result

PASS after remediation.  No remaining launch-blocking defect was found.

Two defects in launcher hash
`11843FDA5101391B05FE2442E8401E50D63D92B0534692F844A6778B4F6CFDD3`
were found before launch: a bad CNF hash left an empty run directory, and a
timeout returned wrapper exit code 0.  The root-owned launcher was changed;
the replacement hash above was re-read in full and both defects were retested.

Final-hash observations:

- wrong expected CNF hash: wrapper exit 1; requested `audit-final-hash-refusal-v2`
  directory was not created;
- existing nonempty run directory: wrapper exit 1; its only sentinel remained
  byte-for-byte unchanged;
- out-of-scope run directory: wrapper exit 1 and no directory created;
- timeout: wrapper exit 124, summary `TIMEOUT`, `independently_verified=false`,
  solver exit `-1`, and the recorded solver PID was no longer alive;
- SAT micro-instance: wrapper exit 0, solver exit 10, summary
  `SAT_UNVERIFIED`, 24-byte witness, empty stderr, and decoder parser assignment
  `{1: true, 2: true}` satisfying both unit clauses;
- nontrivial UNSAT micro-instance: wrapper exit 0, solver exit 20, summary
  `UNSAT_PROOF_UNCHECKED`, 8-byte proof, and empty stderr;
- independent `drat-trim` replay of that nontrivial proof: exit 0 and exact
  `s VERIFIED`; replay with an empty proof: exit 1 and exact `s NOT VERIFIED`.

## Decoder audit

The frozen manifest says that positive `edge(a,b)` means `a->b` and negative
means `b->a`.  The decoder implements that convention exactly.  The 152 edge
names are precisely the complement of the 19 listed cycle edges.  Positive and
negative parser probes decoded correctly; a conflicting assignment was
rejected.  The emitted object has exactly the verifier schema keys `n` and
`out_neighbors`, with rows generated in increasing order.  A deterministic
regular mixed-sign orientation passed support, symmetry, and degree handling
and was then correctly rejected at the semantic frontier (`1` unreachable
target at vertex 0 rather than `3`).

The decoder does not authenticate the manifest or CNF itself.  This does not
permit a false SAT claim because it recomputes the target graph predicate and
the result still requires both independent graph verifiers, but the production
invocation must use the frozen manifest hash above and must supply the frozen
CNF hash through `-ExpectedCnfSha256`.

## Reproduction commands

```powershell
clang -O2 -Wall -Wextra -Werror -o engine/tests/audit_fake_timeout_solver.exe engine/tests/audit_fake_timeout_solver.c
clang -O2 '-Dgetc_unlocked=getc' -o engine/tests/audit_drat_trim.exe ../../third_party/cadical/test/cnf/drat-trim.c
python engine/tests/audit_cycle19_decoder.py
engine/tests/audit_drat_trim.exe engine/tests/audit_nontrivial_unsat.cnf engine/logs/audit-final-nontrivial-unsat-v1/proof.drat
engine/tests/audit_drat_trim.exe engine/tests/audit_nontrivial_unsat.cnf engine/logs/audit-final-sat-v2/proof.drat
```

The launcher cases used `pwsh -NoProfile -File engine/run_cycle19_cadical.ps1`
with the named micro-CNF, a fresh child of `engine/logs`, the recorded SHA-256,
and 10 seconds (1 second for the timeout stub).  No command in this audit named
the frozen production CNF as launcher input.
