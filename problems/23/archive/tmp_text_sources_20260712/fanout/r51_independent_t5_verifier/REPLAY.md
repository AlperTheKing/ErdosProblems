# Replay

Run from the repository root:

```powershell
cd E:\Projects\ErdosProblems

# Rebuild the three native proof tools into this audit directory only.
& .\tmp\fanout\r51_independent_t5_verifier\build_tools.ps1

# Rebuild all nine CNFs, run three SAT solvers, emit DRAT and LRAT,
# check both proof formats, and regenerate MANIFEST.json.
python .\tmp\fanout\r51_independent_t5_verifier\verify_all.py

# Standard-library integrity replay over all recorded files and hashes.
python .\tmp\fanout\r51_independent_t5_verifier\audit_manifest.py
```

Expected final lines:

```text
MANIFEST 5555438712085653259b65b98c25da17647e41602b1df23494abe4cb6bbbe33a
PASS manifest=5555438712085653259b65b98c25da17647e41602b1df23494abe4cb6bbbe33a splits=9
```

One split can be regenerated independently as follows:

```powershell
python .\tmp\fanout\r51_independent_t5_verifier\independent_t5_cnf.py `
  --left 9 --right 7 `
  --artifact .\tmp\fanout\r42_graph_specific_exclusion\t5_solo_l9_r7_3000.json `
  --cnf .\tmp\fanout\r51_independent_t5_verifier\scratch_n16_l9_r7.cnf `
  --result .\tmp\fanout\r51_independent_t5_verifier\scratch_n16_l9_r7.json
```

The per-split proof commands used by `verify_all.py` are:

```powershell
# Textual DRAT
cadical.exe --no-binary relaxed.cnf proof.drat
drat-trim.exe relaxed.cnf proof.drat -c core.cnf -w

# Native LRAT, independently checked
cadical.exe --lrat --no-binary relaxed.cnf proof.lrat
lrat-trim.exe relaxed.cnf proof.lrat
```

SAT tools conventionally return process code `20` for UNSAT/verified.  Replay
acceptance is based on the exact `s UNSATISFIABLE` and `s VERIFIED` lines, and
the manifest records all process codes and byte hashes.


The stable artifact digest list is `SHA256SUMS.txt` (57 entries). Its own
SHA-256 is printed by `Get-FileHash SHA256SUMS.txt`.
