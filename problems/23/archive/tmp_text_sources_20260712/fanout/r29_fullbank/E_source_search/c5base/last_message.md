The 2943 all-anchor Hall defect is not a genuine obstruction. The current finite checker omits the API-licensed R19 common-blue `c5Base` terminal. Restoring it gives an explicit injective 28-half-slot absorber.

`../COMMON.md` does not exist at `E:\Projects\COMMON.md`; no such file was found under `E:\Projects`. I therefore used the repository’s compiled API and archived R19/R20/R23 contracts.

The missing eligibility rule is exactly [CheckedC5BaseTransfer.lean](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean:35):

\[
x\ne y,\quad B(x,o),B(y,o),\quad
d_M(\{x,y\})+2\le d_B(\{x,y\}).
\]

The `+2` already pays for reserving the two blue destination edges \(xo,yo\). It is not an instruction to delete two FreeHalf source slots. A FreeHalf slot is unavailable only under the separate active-orientation reservation. None of the terminals below conflicts with such a reservation.

The faulty checker is [rebuild_owner_hall.py](E:/Projects/ErdosProblems/tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:100): it enumerates same-first and row-companion candidates but never tests this common-blue predicate.

Exact exhaustive enumeration on the canonical incidence SHA used by the existing certificate gives:

| Owner | Valid ordered terminals | Available halves | New global half keys |
|---|---:|---:|---:|
| \(0\) | 4 | 8 | 4 |
| \(1\) | 704 | 1408 | 106 |
| \(2\) | 704 | 1408 | 106 |

There are zero active-half reservation conflicts.

The complete terminal families are:

- Owner \(0\):
  \[
  (1,55),(55,1),(2,55),(55,2),
  \]
  all with adjusted surplus \(1384-2\ge0\).

- Owner \(1\), writing \(L=\{3,\ldots,28\}\) and \(z_L=2929\):

  \[
  (x,y)\in L^2,\ x\ne y;\qquad
  (x,z_L),(z_L,x)\ (x\in L);\qquad
  (0,z_L),(z_L,0).
  \]

  Their switch surpluses are respectively \(2,3,5\).

- Owner \(2\), writing \(R=\{29,\ldots,54\}\) and \(z_R=2930\):

  \[
  (x,y)\in R^2,\ x\ne y;\qquad
  (x,z_R),(z_R,x)\ (x\in R);\qquad
  (0,z_R),(z_R,0),
  \]

  again with surpluses \(2,3,5\).

Each ordered terminal supplies both half-bits \(h=0,1\). Much of this supply overlaps existing same-first/row-companion keys, which is why global-key union—not summing terminal counts—is essential.

An exact absorber for the missing 28 owner-2 obligations is

\[
A=\{(x,2930,h):x=29,\ldots,42,\ h\in\{0,1\}\}.
\]

For every member:

- `pair[x,2930] = 0`, so it is a FreeHalf source;
- both \(x2\) and \(2930\,2\) are blue;
- \(d_B(\{x,2930\})-d_M(\{x,2930\})=3\), hence the corrected terminal inequality holds;
- neither half is reserved;
- the key was absent from the old 19,925-source relation.

Thus \(|A|=14\cdot2=28\), exactly the old deficiency.

Using the injective global encoding

\[
\operatorname{id}(x,y,h)=2(2943x+y)+h,
\]

the IDs are

```text
176554,176555,182440,182441,188326,188327,194212,194213,
200098,200099,205984,205985,211870,211871,217756,217757,
223642,223643,229528,229529,235414,235415,241300,241301,
247186,247187,253072,253073
```

They are pairwise distinct because the underlying `(x,y,h)` keys are distinct. They are also disjoint from every source used by the old flow certificate. That certificate sends only 6,623 of owner 2’s 6,651 obligations; assigning these 28 new keys to the remaining obligations extends it injectively.

Capacity/no-double-spend follows directly:

- each FreeHalf key has one Hall unit, corresponding to bank capacity \(1/(2K)\);
- no key is reused;
- ordered directions and half-bits are distinct API keys;
- the R19 switch loss is only a validity witness and is never spent;
- typed `c5Base` source identity is global, as required by [TypedFullBankSources.lean](E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean:59).

After adding all omitted terminals, the global union has 20,141 distinct source keys against demand 19,953. Every nonempty owner shore has nonnegative surplus; the former all-owner shore changes from deficiency \(28\) to surplus \(188\).

Verdict: an injective exact 28 absorber exists. The reported 2943 obstruction is caused solely by omission of the compiled R19 common-blue terminal from the finite eligibility checker.