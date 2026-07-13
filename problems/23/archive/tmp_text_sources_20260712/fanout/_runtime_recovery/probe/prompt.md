This is a read-only runtime recovery probe. Use the command tool exactly once to run:
Get-Location; Test-Path 'tmp/fanout/_runtime/codex-code-mode-host.exe'; Get-FileHash 'tmp/fanout/_runtime/codex-code-mode-host.exe' -Algorithm SHA256
Do not edit any file. Return the working directory, Boolean, and full SHA256 only, prefixed by CHILD_HOST_PROBE.
