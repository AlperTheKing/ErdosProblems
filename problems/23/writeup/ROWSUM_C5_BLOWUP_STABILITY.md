# ROWSUM on Complete C5 Blow-Ups

This note records the exact coefficient-free guardrail for the extremal
family.  Unlike the discarded Schur quantitative current bounds, this statement
is stable under arbitrary blow-up scale.

Let `G` be a complete blow-up of `C5` with independent cyclic classes

```text
A0,A1,A2,A3,A4
```

of positive sizes

```text
n0,n1,n2,n3,n4.
```

Choose the cut that leaves the edge block `A0-A1` bad and cuts the other four
cyclic edge blocks.  Put

```text
m = n0*n1.
```

For complete blow-ups this loses no generality: the bad-edge count of a cut is
multilinear in the five class split fractions, so a minimum bad-edge cut has an
extreme representative in which every class is placed wholly on one side.
Since an odd cycle assignment leaves at least one cyclic block bad, the above
cut is maximum exactly when `m` is a minimum adjacent product:

```text
m <= n1*n2,
m <= n2*n3,
m <= n3*n4,
m <= n4*n0.
```

Every bad edge `f in A0-A1` has shortest blue paths

```text
A0 - A4 - A3 - A2 - A1.
```

For a fixed bad edge `f`, the ROWSUM-O value is

```text
R_f = (O*1)_f
    = n0 + n1 + m/n2 + m/n3 + m/n4.
```

Indeed, the endpoint contributions are `n1` and `n0`; a vertex in `Ai`,
`i=2,3,4`, is used by a random shortest path of `f` with probability `1/ni`,
and its incidence load `S(v)` is `m/ni`, giving total contribution `m/ni` from
the whole class.

Now the min-product assumptions imply

```text
m/n2 <= n3                         from m <= n2*n3,
m/n3 <= n4                         from m <= n3*n4,
m/n4 <= n2                         from n0 <= n2 and n1 <= n4.
```

The last line uses `m <= n1*n2`, hence `n0 <= n2`, and `m <= n4*n0`, hence
`n1 <= n4`.

Therefore

```text
R_f <= n0+n1+n2+n3+n4 = N.
```

So every complete weighted `C5` blow-up satisfies ROWSUM-O on the bad block of
any maximum cut.

For the recurring guardrail family

```text
[k+1,k,k+1,k,k+1]
```

with bad block between the first two classes,

```text
R_f = 5k+2,
N   = 5k+3,
```

so ROWSUM has slack exactly `1` for every `k`, while the false Schur/HARVEST
coefficient bounds fail for large `k`.

This is the target behavior any global proof should preserve: the true
ROWSUM/SPEC inequality remains scale-stable on the extremal blow-up corridor,
whereas fixed positive-coefficient current strengthenings do not.
