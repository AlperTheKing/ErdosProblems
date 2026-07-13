[2026-07-13T09:53:03+03:00] > PLAN | NEXT: Build an exact SR-S census separating splitless shifts from G2-blocked shifts and test weighted moment contraction.

# C21: shifted-smooth red team

Audit in progress. All reported claims below this line will be tied to the C21
source and deterministic output.

[2026-07-13T10:05:45+03:00] OK ATTACK | DID: Exact smoke audit, s<=1000 | RESULT: result_smoke.json SHA-256 071ecafc..., all C++/Python assertions pass | D: none
[2026-07-13T10:05:45+03:00] > ATTACK | NEXT: Run exact C21 census with s<=10^7, G<=30000001, z in 14 fixed cutoffs, rational scale 10^18.
[2026-07-13T10:06:51+03:00] FAIL ATTACK | DID: Ran s<=10^7 audit | RESULT: WinError 32 unlinking open G memmap; no result.json written | D: wrapper fix
[2026-07-13T10:06:51+03:00] > ATTACK | NEXT: Rerun identical census using byte-prefix verification with no persistent mmap handle.
[2026-07-13T10:07:56+03:00] FAIL ATTACK | DID: Repeated s<=10^7 audit | RESULT: WinError 32 persisted without mmap; no result.json written | D: cleanup retry
[2026-07-13T10:07:56+03:00] > ATTACK | NEXT: Rerun identical census with 50x100ms bounded unlink retry for transient Windows locks.
[2026-07-13T10:12:19+03:00] OK ATTACK | DID: Exact s<=10^7 census | RESULT: result.json SHA-256 ce78217c..., 70 rows and all assertions pass | D: finite certificate
[2026-07-13T10:12:19+03:00] > VERIFY | NEXT: Rerun after adding character-formula and total blocker-mass assertions at identical parameters.
