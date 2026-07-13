# Replay

From `E:\Projects\ErdosProblems`:

```powershell
python tmp/fanout/r56_soft_rotor_gate/gate.py --workers 32 --output tmp/fanout/r56_soft_rotor_gate/results.json
python tmp/fanout/r56_soft_rotor_gate/verify.py --workers 32 --input tmp/fanout/r56_soft_rotor_gate/results.json
```
