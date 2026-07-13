# Replay

Run from `E:\Projects\ErdosProblems`.

```powershell
python problems/23/writeup/_claude_r22_89_gate.py
python tmp/fanout/r53_global_softcap_gate/gate.py
python tmp/fanout/r53_global_softcap_gate/alternate_unscoped_p4.py
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 5 --n-max 10 --workers 16 --chunk-size 32 --output tmp/fanout/r53_global_softcap_gate/census_n5_n10.json
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 11 --n-max 11 --workers 32 --chunk-size 32 --output tmp/fanout/r53_global_softcap_gate/census_n11.json
python tmp/fanout/r53_global_softcap_gate/census.py --n-min 12 --n-max 12 --workers 48 --chunk-size 64 --output tmp/fanout/r53_global_softcap_gate/census_n12.json
python tmp/fanout/r53_global_softcap_gate/verify.py
```

Expected final verifier fields:

```text
allChecksPass=true
censusSystems=992618
```
