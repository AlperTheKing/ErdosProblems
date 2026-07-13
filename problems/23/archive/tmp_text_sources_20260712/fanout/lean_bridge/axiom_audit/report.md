Audit could not run because the execution host is missing, and the workspace is read-only.

Attempted command:

```powershell
Get-Location; Get-ChildItem -Force; rg --files ..\..\.. | Select-Object -First 200
```

Working directory:

```text
E:\Projects\ErdosProblems\tmp\fanout\lean_bridge\axiom_audit
```

Exact error:

```text
failed to spawn code-mode host E:\Projects\ErdosProblems\tmp\fanout\lean_bridge\bin\codex-code-mode-host.exe:
The system cannot find the file specified. (os error 2)
```

A second attempt to enumerate alternate command tools failed with the identical error. Consequently, no Lean builds or scratch probes executed, no token scans or hashes were produced, and no conclusion about the global-minimizer proof’s axiom subset can honestly be reported.

Required fix: restore `E:\Projects\ErdosProblems\tmp\fanout\lean_bridge\bin\codex-code-mode-host.exe` and provide write access under `axiom_audit` for probe and log files.