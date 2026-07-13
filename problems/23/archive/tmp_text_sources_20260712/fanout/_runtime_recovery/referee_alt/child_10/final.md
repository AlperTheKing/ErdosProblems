Proved an exact sufficient batch-trade criterion.

For a row tuple \(\omega\), define
\[
I(\omega)=B[U(\omega)]\setminus S(\omega),
\]
and recompute all objects only after every row in the batch has been replaced.

Let \(L\) be the number of previously active obligations lost or deactivated, and \(G\) the number of newly active obligations created. Partitioning the obligation multisets into persistent, lost, and gained elements gives
\[
\operatorname{score}(\omega')-\operatorname{score}(\omega)=G-L.
\]
Therefore \(G<L\) is sufficient for strict descent.

A checkable deactivation certificate for an old active component \(C\) consists of:

1. A partition \(C=C_1\sqcup\cdots\sqcup C_k\).
2. Every old internal edge crossing two parts is absent from \(I(\omega')\), either because it becomes selected or an endpoint leaves \(U(\omega')\).
3. Every component of \(I(\omega')[C_i]\) contains both endpoints of no selected atom.

Conditions 2–3 split \(C\) into owner-free components, hence deactivate it.

For the archived 2943 architecture, exact `Fraction` arithmetic verifies:

- \(19953+52\cdot200+458=30811\).
- Non-hub contribution: \(10400+458=10858\).
- Hall reach: \(17325+2600=19925\), giving gap \(28\).
- \(676\cdot679=459004\) nontrivial one-row replacements.

Thus:

- Full deactivation would give score \(0\), an exact decrease of \(30811\).
- Deactivating the hub contribution \(L=19953\) suffices provided \(G\le19952\).
- With no new obligations and persistent leaf/circuit terms, the new score would be exactly \(10858\).

No 2943 batch witness is established. The archive lacks the selector incidence lists and 679 canonical selected rows needed to recompute \(U'\), \(S'\), and \(I'\). The Hall gap alone does not imply a cutset-covering batch. The global selector-trade landscape therefore remains open.

Exact replay command:

```powershell
@'
from fractions import Fraction as F
h,l,c=F(19953),F(52*200),F(458)
s=h+l+c
assert (l,s,s-h)==(10400,30811,10858)
assert F(17325+2600)==19925 and F(19953-19925)==28
assert F(707+676)==1383 and F(676*679)==459004
print(s,h,s-h,h-1,19953-19925,676*679)
'@ | python -
```

Output:

```text
30811 19953 10858 19952 28 459004
```

R29 SHA-256: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`.

Artifact creation failed in both mandated recovery paths despite their directories existing; no files were modified.