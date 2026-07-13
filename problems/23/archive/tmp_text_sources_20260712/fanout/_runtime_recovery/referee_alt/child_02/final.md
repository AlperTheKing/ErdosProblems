Falsified the claim that the R29 baseline is a global selector-trade minimizer.

- Exact joint trade: replace all 676 selector rows with their recorded anchor rows.
- Score: \(30811 \to 23115\), a decrease of \(7696\).
- Exact new decomposition: collision \(23108\), HitNeed \(7\).
- Hubs remain active; the reduction comes from deactivating all 52 traffic leaves.

Symmetry-reduced lower model, with \(L_L,L_R\in[0,338]\) local rows and \(A_s=338-L_s\):

\[
20411+
2\bigl(A_L+A_R+(A_L-1)_+ +(A_R-1)_+\bigr)
+200\left(\left\lceil\frac{L_L}{27}\right\rceil+
\left\lceil\frac{L_R}{27}\right\rceil\right)
+4\,1_{L_L=L_R=0}.
\]

All \(339^2=114921\) states were checked exactly. Its unique minimum is \(23115\) at \((L_L,L_R)=(0,0)\).

Artifacts:

- [check_trade.py](E:/Projects/ErdosProblems/tmp/fanout/_runtime_recovery/referee_alt/child_02/check_trade.py)
- [r29_construction.py](E:/Projects/ErdosProblems/tmp/fanout/_runtime_recovery/referee_alt/child_02/r29_construction.py)
- [result.json](E:/Projects/ErdosProblems/tmp/fanout/_runtime_recovery/referee_alt/child_02/result.json)

Reproduction:

```powershell
python tmp/fanout/_runtime_recovery/referee_alt/child_02/check_trade.py
```

SHA256:

```text
check_trade.py       E3D94E128EF2FA9FC00A8493E1CB78AE0A6A2A03F786DA2C7464C0E93D32976F
r29_construction.py  5D29B1D6E35957405C53176FAB1FB21660D727CB334A1E20462EB5EBE36678F6
result.json           C221FAFA4A5876CB4DB1C4ADADE0F3865DDDDE536BC7760BCD5A64F5A841F322
construction payload FC4F3AB94BED810669976B1FDB21743FDD4EBE57EEA15EF52AFCFC2165E2FB1F
```

Proof gap: the reduced bound certifies only selector-row trades with the 707 rigid rows fixed. It does not establish a global minimum over arbitrary replacements of rigid rows. The explicit \(23115\) witness, however, unconditionally proves that \(30811\) is not globally minimal. This supports—rather than falsifies—the broader “no Hall-failing tuple is a global minimizer” route.