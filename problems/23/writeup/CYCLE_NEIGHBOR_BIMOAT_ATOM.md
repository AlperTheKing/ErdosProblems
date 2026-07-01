# Cycle-neighbor bimoat atom

Status: candidate exact-test target for `ROWSUM-O`.

This is the smallest repair found after the pure cycle-neighbor CAGE atom
failed on `H?AFBo]`.

## Atom

Fix a bad edge `f`.  For every bad edge `g`, row `P in cyc[f]`, row
`Q in cyc[g]`, and shared vertex `x in P cap Q`, create one atom of mass

```text
1 / (|cyc[f]| |cyc[g]|).
```

Let

```text
R = V(P) union V(Q).
```

The atom may route to:

```text
R
union
{vertices in a B-component of V \ R with at least two B-attachments to R}.
```

Call this sink set `Bimoat(P,Q)`.

The proposed Hall certificate is:

```text
for every Y subset V,
  sum_{atoms with Bimoat(P,Q) subset Y} mass(atom) <= |Y|.
```

If this holds for every `f`, then the total atom mass is

```text
sum_g <p_f,p_g> = (O 1)_f,
```

so Hall implies `ROWSUM-O`.

Important caveat: the Hall family includes the full set `Y=V`.  For
`Y=V`, the left-hand side is the total atom mass, exactly `(O 1)_f`.
Thus the full-set Hall inequality is precisely `ROWSUM-O(f)`.  The bimoat
atom repairs **proper-subset/local routing obstructions** such as the
`H?AFBo]` CAGE failure; it does not by itself make the full-set ROWSUM case
easier.  Any proof of the full bimoat Hall theorem must still supply a
genuine argument for the special full-set deficiency, or a Gamma-descent
construction that also works when `Y=V`.

## Why this repair

The failed four-neighbor and row-union atoms die on

```text
graph6 = H?AFBo]
side   = 000111100
f      = (1,7)
Y      = {1,2,3,4,6,7,8}
```

with Hall demand `8 > |Y|=7` even though `ROWSUM(f)=8<N=9`.

The missing vertices are `{0,5}`.  They form a blue side corridor attached to
the row union at two row vertices, via `6-0-5-8`.  The bimoat sink includes
this component and removes the false local Hall obstruction.

This shows the needed capacity is not inside the row pair itself; it is in
two-gate blue complement components.

## Exact gate

Implemented as:

```text
python problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py \
  --ports row-union-bimoat ...
```

The iterated variant is:

```text
python problems/23/writeup/_gpt_cycle_neighbor_cage_gate.py \
  --ports row-union-biclosure ...
```

Current local checks:

```text
H?AFBo]                          PASS
census all-gmins n=7             PASS, checked_cuts=53
census all-gmins n=8             PASS, checked_cuts=280
census all-gmins n=9             PASS, checked_cuts=1916
census all-gmins n=10            PASS, seen=9832, checked_cuts=16016
census all-gmins n=11            PASS, seen=90842, checked_cuts=171182
I?BD@g]Qo                        PASS
I?ABCc]}?                        PASS
C5[k+1,k,k+1,k,k+1] k=2..6      PASS, max N=33
```

Iterated biclosure smoke checks:

```text
H?AFBo]                         PASS
census all-gmins n=9            PASS, checked_cuts=1916
census all-gmins n=10           PASS, seen=9832, checked_cuts=16016
census all-gmins n=11           PASS, seen=90842, checked_cuts=171182
I?BD@g]Qo                       PASS
I?ABCc]}?                       PASS
C5[k+1,k,k+1,k,k+1] k=2..6     PASS, max N=33
```

The direct uncompressed C5 `k=8` flow run was stopped for runtime. A
quotient/compressed gate is the right way to push that family much further.

For the nonuniform C5 family, the quotient picture is simple.  Every shortest
row contains one vertex in each C5 part.  Hence, for every row pair,
`R=V(P) union V(Q)` meets all five parts.  Every blue component of `V\R` has
attachments back to `R` through the two adjacent parts, so `cl_2^B(R)=V`.
The bimoat/biclosure demand has a single sink mask `V`, and its total mass is
`ROWSUM(f)=N-1`.  Thus this whole blowup family satisfies the bimoat Hall
certificate by the one inequality `N-1 <= N`.

## Proof target

The geometric statement should be:

```text
Every Hall-deficient Y for the bimoat atom yields a neutral connected
terminal-shadow switch with negative square-length variation.
```

The two-gate condition is intended to make the missing capacity exactly the
same kind of blue side corridor that appears in Gamma-minimal switch
arguments.  Unlike the false no-two-hole route, this statement does not force
component-local single-miss; fan rows may coexist as long as their two-gate
moats are available as capacity.

More explicitly, fix `f` and suppose `Y subset V` is Hall-deficient:

```text
sum_{(g,P,Q,x): cl_2^B(V(P) union V(Q)) subset Y}
    1/(|cyc[f]| |cyc[g]|)
>
|Y|.
```

Let `A_Y` be the multiset of trapped row-pair atoms. A proof should
canonically construct from `A_Y` a switch `S_Y` satisfying:

```text
|delta_B(S_Y)| = |delta_M(S_Y)|,
B^S_Y is connected,
```

and a replacement-pricing map for the new bad boundary edges with

```text
sum_{h in delta_M(S_Y)} ell(h)^2
>
sum_{e in delta_B(S_Y)} lambda_Y(e)^2.
```

Then flipping `S_Y` preserves maximum-cut size and strictly lowers `Gamma`,
contradicting the chosen gamma-minimal connected-B maximum cut.

The key new geometric burden, compared with the false CAGE atom, is that an
outside blue component attached to a trapped row pair at two or more gates
must be absorbed into the capacity set. Equivalently, a Hall-deficient `Y`
has no outside two-gate blue side corridor relative to any trapped row pair.
That is the switch-shaped hypothesis to exploit.

For **proper** `Y`, this is a local routing/capacity statement.  For
`Y=V`, it is the original ROWSUM contradiction: there is no outside
component and the proof must extract a Gamma-decreasing switch directly from
the assumption `(O 1)_f>N`.

## Closure interpretation

For a vertex set `R`, define the one-step blue bimoat closure

```text
cl_2^B(R) =
  R union {B-components of V\R having at least two B-attachments to R}.
```

The implemented atom uses `Bimoat(P,Q)=cl_2^B(V(P) union V(Q))`.

Thus a Hall set `Y` traps an atom only when

```text
cl_2^B(V(P) union V(Q)) subset Y.
```

Equivalently, every blue component outside `Y` has at most one attachment to
the row-pair union.  This is the switch-shaped feature missing from the false
pure row-union atom: in the `H?AFBo]` witness, the outside component `{0,5}`
has two attachments `6,8`, so it cannot be ignored.

For a proof, the more natural object may be the **iterated** closure obtained
by repeating the same operation until stable.  The current gate is deliberately
one-step; if a counterexample appears whose only problem is a chain of
two-gate blue components, the next repair should be the iterated closure.
