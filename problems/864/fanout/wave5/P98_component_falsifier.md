# P98: component falsifier and corrected fold charge

## Verdict

The componentwise strengthening of C84 is false under every frontier gate.
Starting from P94's actual tight row and deleting the single mark `4740`
gives an endpoint-normalized integer Sidon set with positive defect and the
full `b=1` literal hole for which one loose-triangle component has

\[
                 110\text{ triangles}>109\text{ folds}.              \tag{1}
\]

The row still satisfies global C84: `(C_S,T_F)=(132,110)`.  A stronger
two-deletion example has 102 triangles on 96 folds.  Thus componentwise
pseudoforest sparsity cannot close P84, even though the global inequality
survives these examples.

The corrected global candidate

\[
 T_F\le C_S+V_b,\qquad
 V_b=\#\{(a,c,u,v):a+c+h=u+v,\ a+c+b\in\Delta^+(B)\},                 \tag{2}
\]

has no failure in the new P98 domains.  P98 adds 3,014,932 exact
unrestricted `(B,b)` tests beyond the stated width-30 census, and 27,074
full-gate mutation-lane evaluations at the tight P94 boundary.  This is
finite evidence only; (2) is not proved here.

## 1. Exact full-gate component falsifier

Let `B_94` be P94's maximum-ratio row in
`compute/p94/c84_archived_audit.json`, and put

\[
             B=B_{94}\setminus\{4740\},\qquad h=14484,\qquad b=1.     \tag{3}
\]

Exact integer reconstruction gives

```text
p=103, delta=1379, C_S=132, T_F=110, V_1=0.
maximum component: 109 folds, 110 loose triangles.
```

All 5,356 endpoint-preserving one- and two-mark deletions from `B_94`
remain Sidon and pass the literal-hole gate.  Among them, 511 violate the
component bound.  The first one-mark failure is (3).  The largest excess is
obtained by deleting `8015,13277`:

```text
p=102, delta=1072, C_S=133, T_F=104,
maximum component: 96 folds, 102 loose triangles.
```

An independent local transformation also works: deleting `4980` and
inserting `3620` gives `(C_S,T_F)=(147,121)` and a component with 121
triangles on 118 folds.  This row is one of only 18 full-gate rows among all
1,481,140 one-delete/one-insert attempts; two of the 18 violate the
component bound.

Deletion preserves Sidonicity and the literal hole, so no inherited-gate
assumption is hidden in these examples.  The standalone verifier rebuilds
all sums, differences, folds, loose triangles, components, defect, and
`V_1` directly.

## 2. Exact tight-boundary mutation domain

The P94 seed has one nontrivial component with 116 folds and 116 triangles.
Its fold support uses 84 of the 104 marks; 20 marks lie outside that support.
P98 exhausts the following finite domains:

| transformation | attempted | Sidon | full gate | tight | component failures | global failures |
|---|---:|---:|---:|---:|---:|---:|
| delete one or two non-endpoints | 5,356 | 5,356 | 5,356 | 529 | 511 | 0 |
| delete at most five of 20 outside marks | 21,700 | 21,700 | 21,700 | 21,700 | 0 | 0 |
| insert one interior mark | 14,380 | 47 | 0 | 0 | 0 | 0 |
| delete one, insert one | 1,481,140 | 4,841 | 18 | 0 | 2 | 0 |

The second lane contains overlaps with the first and includes the seed, so
27,074 is a count of full-gate lane evaluations, not distinct sets.  Every
full-gate row has `V_1=0`.  There are 513 component failures and no global
failure.  The largest observed global excess `T_F-C_S` is `-19` in the
outside-support lane and `-20` in the unrestricted one/two-deletion lane.

These data identify the exact obstruction to the component conjecture:
deleting a core mark can remove fewer loose triangles than folds from the
tight component, while the isolated/global fold reserve still pays for the
global count.  Deleting only marks outside the tight support leaves the
116-on-116 component unchanged in all 21,700 cases.

## 3. Corrected inequality red team

### Exact CP-SAT interval extension

CP-SAT exhausts every endpoint Sidon set `B subset [0,H]` with `H in B` and
`|B|>=3` for `31<=H<=40`, with no hole or defect assumption.  Each solver
job is single-threaded and returns `OPTIMAL`.  The domain contains 1,245,376
sets and hence 2,490,752 separate `b=1,2` tests of (2).  There are zero
failures.  The maximum corrected excess is zero only on rows with
`C_S=T_F=V_b=0`.

The same interval range under all full frontier gates contains 260,774
rows.  It has zero component failures.  Its only unrestricted nontrivial
tight row occurs at `H=40`:

```text
B={1,3,10,22,26,27,37,40}, h=41,
C_S=7, T_F=4, maximum component=4 folds=4 triangles.
```

That row is not asserted to satisfy the full gates; it records the exact
tight component in the unrestricted interval domain.

### Transformed pure systems

Starting from the smallest archived raw overfull component, P98 exhausts
all 261,836 distinct normalized orientations of all subsets with at least
three marks.  It also exhausts all 254 endpoint-preserving one-mark Sidon
neighbors of both orientations.  The combined corrected domain has 524,180
`(B,b)` tests and zero failures.

The subset domain contains 16 component failures and two global C84
failures.  Its smallest global failure has `p=13,h=370,C_S=7,T_F=8`, but
the correction pays for it.  None of the 43 pure component failures in the
subset and neighbor domains can be recovered to a positive-defect literal
hole by the exact translation and endpoint-affine-lift tests.

For the P88 `p=60,h=3286` pure global counterexample, every one of its 250
overfull-component translations has a supporting core that already violates
both literal holes.  The same core obstruction holds at the endpoint for all
80 archived raw overfull components.  This explains why CP-SAT deletion
cannot preserve those components while repairing the phase.

## 4. Reproduction

```powershell
python -B problems/864/compute/p98/search_transformed_parent.py `
  --output problems/864/compute/p98/transformed_parent.json
python -B problems/864/compute/p98/cpsat_unrestricted_scan.py `
  --min-H 31 --max-H 40 --workers 10 --time-limit 1800 `
  --output problems/864/compute/p98/unrestricted_corrected_H31_H40.json
python -B problems/864/compute/p98/search_tight_mutations.py `
  --workers 16 --output problems/864/compute/p98/tight_mutations.json
python -B problems/864/compute/p98/audit_overfull_cores.py `
  --output problems/864/compute/p98/core_obstruction.json
python -B problems/864/compute/p98/verify_single_deletion_falsifier.py
python -B problems/864/compute/p98/verify_results.py `
  problems/864/compute/p98/transformed_parent.json `
  problems/864/compute/p98/unrestricted_corrected_H31_H40.json `
  problems/864/compute/p98/tight_mutations.json `
  --output problems/864/compute/p98/verification.json
```

`verification.json` independently reconstructs 45 retained extremal rows
and records SHA-256 hashes of every audited result file.  Its status is
`PASS`.  All searches use at most 16 workers, and every combinatorial
acceptance decision uses exact integers.

## 5. Claim boundary

P98 kills only the componentwise strengthening.  It does not falsify global
C84 on a positive-defect literal hole, and it does not prove (2).  The
surviving closing candidate is the global charge (2): fold-local phase
violations pay for pure-order excess, while `V_b=0` specializes it to the
actual literal-hole C84 frontier.
