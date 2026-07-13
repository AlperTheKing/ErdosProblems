# P81: the outer-fold `K_{6,6}` question

## Verdict

The proposed universal exclusion is **not proved or falsified here**.  No
positive-defect literal-hole ruler with an outer `K_{6,6}` was found, but the
finite searches below are not a theorem.

Two exact boundary results were obtained.

1. The suggested rowwise Erdos--Szekeres mechanism is false: the exact P79
   `K_{5,5}` already contains three rows with the same monotone three-column
   pattern in both inner endpoints.
2. Sidonicity, all 36 complementary inner labels, interval nesting, and the
   full literal hole do not by themselves exclude `K_{6,6}`.  An exact
   85-mark sparse ruler realizes one.  Its defect is negative, so positive
   defect is the essential condition still unused.

Thus this note does not promote the observed threshold 5 to a universal
threshold.  In particular, the absence of `K_{6,6}` in the exact rows is not
reported as a proof.

## 1. What a `K_{6,6}` would force

Put `H=h-1` and define the endpoint phase reflection

\[
                         \theta(x)=h-b-x.               \tag{1}
\]

Suppose the outer graph contains

\[
       \{a_1,\ldots,a_6\}\mathbin\times
       \{v_1,\ldots,v_6\}.                              \tag{2}
\]

For each edge let `(c_ij,u_ij)` be its unique complementary inner
difference pair.  Then

\[
 a_i+c_{ij}+h=u_{ij}+v_j,
 \qquad a_i\le c_{ij}<u_{ij}\le v_j,                    \tag{3}
\]

and hence

\[
 \boxed{u_{ij}-c_{ij}=a_i+h-v_j
        =a_i+\theta(v_j)+b.}                            \tag{4}
\]

All 36 values in (4) are distinct.  Equality of two would repeat a positive
difference; equivalently, their complementary outer lengths would be equal,
which repeats an outer difference.  They form the exact additive grid

\[
 e_{ij}+e_{k\ell}=e_{i\ell}+e_{kj}.                    \tag{5}
\]

The literal hole gives two correlated families of absent marks:

\[
 \boxed{\theta(v_j)\notin B,
        \qquad \theta(u_{ij})\notin B.}                 \tag{6}
\]

Indeed, if `theta(v_j)` belonged to `B`, (4) would put the represented
positive difference `u_ij-c_ij` in `B+B+b`.  Similarly, (3) gives

\[
                 v_j-c_{ij}=a_i+\theta(u_{ij})+b,       \tag{7}
\]

so `theta(u_ij) in B` would violate the same hole.  Equations (4)--(7) use
every inner label and the literal, repetition-allowing hole.  They do not,
however, contradict positive defect.

## 2. Exact failure of the Erdos--Szekeres route

For fixed `a_i` and increasing `v_j`, the lengths in (4) decrease.  Ordinary
Erdos--Szekeres does force a monotone length-three subsequence of either
endpoint sequence, but its threshold is already

\[
                         (3-1)^2+1=5,                   \tag{8}
\]

not 6.  Consequently the existence of the exact P79 `K_{5,5}` is already a
necessary test of this mechanism.

That witness passes the test in a stronger form.  Take the three left marks

```text
7469, 7994, 10294
```

and the three right marks

```text
28303, 28483, 29656.
```

The inner lower endpoints on this `3 x 3` rectangle are

```text
14056  15259  17453
16989  18559  21433
10294  14990  17082
```

and the inner upper endpoints are

```text
22969  23992  25013
26427  27817  29518
22032  26548  27467
```

Every displayed row is strictly increasing in both matrices.  The full
152-mark ruler is integer Sidon, has `(h,b,delta)=(29747,1,4834)`, and
satisfies the literal hole.  Thus a common monotone column triple across
three rows does not produce a repeated sum, repeated difference, or hole
equation.

What this witness avoids is simultaneous monotonicity down the columns in
the fixed order of the left marks.  The exact endpoint-order audit finds no
such fixed-order bimonotone `3 x 3` in either endpoint matrix.  Erdos--Szekeres
applied independently to six rows does not force that two-dimensional
alignment.  An additional arithmetic lemma would be required.

The machine-readable audit is

```text
problems/864/compute/p81/p79_k55_endpoint_orders.json
```

## 3. Positive defect cannot be omitted

The program `construct_sparse_k66.py` gives an exact 85-mark ruler with

\[
 h=10^{15},\qquad b=1,\qquad
 \delta=-999999999989204.                               \tag{9}
\]

All 85 marks are odd.  Therefore every positive difference is even and
every member of `B+B+1` is odd, which proves the full literal hole.  Exact
enumeration gives

\[
 |B+B|={85\cdot86\over2}=3655,
 \qquad |\Delta^+(B)|={85\cdot84\over2}=3570,           \tag{10}
\]

with every representation count equal to one.  Its outer graph contains a
literal `K_{6,6}`, and the artifact stores all 36 outer edges, complementary
inner edges, and fold equations.

```text
problems/864/compute/p81/sparse_k66_witness.json
```

This is not a counterexample to the requested statement because (9) is
negative.  It is an exact counterexample to any proof using only the local
order geometry, the 36 labels, and the hole.  A valid proof must use positive
defect globally.

## 4. Exact finite searches

The new searches use integer sums and differences throughout.  Bicliques are
found by exact neighborhood-subset multiplicities, after reconstructing the
unique nested inner pair for every outer edge.

| domain | rows or shifts | `K5,5` | `K6,6` |
|---|---:|---:|---:|
| P79 positive-defect P20 translations | 165,225 | 1 | 0 |
| Singer first-hole cuts, `q=131,...,167` sampled runs | 38,312 | 66 | 0 |
| Singer `q=167`, 512 sampled unit classes | 86,016 | 320 | 0 |
| all hole shifts on 16 retained `q=167` `K5,5` cuts | 27,902 | 22 | 0 |
| range-separated Singer cuts, `q=191,193,197,199,211` | 31,872 | 13 | 0 |

The first three domains are not asserted to be disjoint; the table reports
the literal audited row counts of each run.  The range-separated rows use

\[
 \gamma=\lfloor W/2\rfloor+1,
 \qquad h=W+\gamma+1.                                  \tag{11}
\]

Since `2 gamma+b>W=max Delta^+`, their literal hole is automatic for both
`b=1,2`.  Every one of the 31,872 cuts also has positive defect.

Two direct CP-SAT models imposed all positive differences distinct and all
36 nested complementary equations.  The P75-guided order-26 model was run
under eight additional seeds, for about 16 million branches in aggregate;
all returned `UNKNOWN`.  The optimization form retained P75's exact
30-of-36 rectangle with bound 36.  These solver outcomes are not
infeasibility certificates.

An exhaustive one-mark odd repair of P75 found only one Sidon-preserving
replacement among all remove/insert attempts, and its rectangle score
remained 30.  The six missing P75 edges are recorded exactly in
`p75_rectangle_repair.json`.

## 5. Claim boundary

The available exact facts establish

\[
 \text{local labels + nesting + literal hole}
 \not\Longrightarrow K_{6,6}\text{-free},              \tag{12}
\]

while every completed positive-defect search remains `K_{6,6}`-free.  They
do not establish

\[
 \delta>0\quad\Longrightarrow\quad K_{6,6}\text{-free}.\tag{13}
\]

The unresolved step is a global use of positive defect that rules out the
36-grid (4) together with the phase holes (6).  Neither rowwise monotonicity
nor an abstract forbidden-subgraph argument supplies that step.

## 6. Reproduction

From the repository root:

```powershell
python -B problems/864/compute/p81/analyze_endpoint_orders.py
python -B problems/864/compute/p81/repair_p75_rectangle.py --steps 10
python -B problems/864/compute/p81/construct_sparse_k66.py --attempts 10000
python -B problems/864/compute/p81/verify_p81_results.py
```

The broader Singer and CP-SAT commands, exact parameters, and result paths
are recorded in `PROGRESS_CODEX.md`.  The final verifier independently
reconstructs the sparse `K_{6,6}`, checks the endpoint-order counts, and
audits every aggregate reported in the table.
