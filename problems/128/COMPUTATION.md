# Erdős Problem 128 — Computation Ledger

Append exact commands, parameters, solver versions, hashes, and outcomes below. No search has yet been launched under this target record.


## 2026-07-13 — declared one-wave terminal run

### CP-SAT formulation

- Model: 190 Boolean edge variables, 1,140 triangle constraints, and 184,756 exact ten-set lower-bound constraints.
- Resources: 8 workers, 8 GB, 600 seconds.
- Result: `UNKNOWN`; zero candidate graphs; no UNSAT proof.
- Full record: `COMPUTATION_CPSAT.md`.
- Log SHA-256: `48F939467C72D64A956EDE49C64AE5BA9E79A0E96F0D20CB07816D2D4ABDB4DF`.
- Model-proto SHA-256: `08AC150B1A8FEF18344186A1304F86614126609662D65F59CAB1301FF71DFDB6`.

### Independent PySAT wave

- Resources: 6 workers for 590.094 seconds; one full MiniCard model and five cut-generation variants.
- Exact audit: 1,338 solver models were checked against all 184,756 ten-sets.
- Result: zero candidates; five lanes `UNKNOWN`, one lane stopped at its declared outer wall; no UNSAT certificate.
- Best audited intermediate graph had minimum ten-set edge count 6, below the required 9.
- Full record: `COMPUTATION_PYSAT.md`.
- Summary SHA-256: `EAA197E10B48574C4B870270BBF93348F23C0CC691B60173D3FD0681AC6FFC54`.

### Independent certificate auditor

`verify/audit_verify.py` independently enumerates all 1,140 triples and all 184,756 ten-sets. Its empty-graph, complete-graph, `C5[4]`, Petersen blow-up, and malformed-input self-tests pass. No candidate was available to certify.

- Audit report: `ADVERSARIAL_AUDIT.md`.
- Verifier SHA-256: `FB8BBFAF5D81A6CBD6E869624D21FDED74BD63263EB4CC53ECABF22D0AD13CBC`.
- Test-log SHA-256: `5B1371BB3DFBF68303A5764ED9F900A47D50C337B28F03761079A1C4CC723F2A`.

### Exact conclusion

The declared finite wave produced neither a counterexample nor an impossibility proof. Per the precommitted exit rule, no next order, new encoding, asymptotic relaxation, or special-family cascade is authorised. The already-running GPT-Pro audit is the sole pending exception; only an explicit graph that passes both local exact verifiers can reopen the route.

## GPT-Pro closure — 2026-07-13

The independent browser generation completed with the sole rendered answer `Thinking failed`. It produced no candidate graph or mathematical claim. The complete output is archived at `gpt_pro/bridge_audit_answer.md` (SHA-256 `D73C26DD8276EB0E0F905F92CEA5774E91CDF438AB48630BB0C5A4D938639742`). No exception to the one-wave exit was triggered.
