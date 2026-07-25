# Exact obstruction for incidence-only edits at vertex 12

## Scope

This note concerns the frozen graph
`unrestricted19-q5-twin-fill-objective9.json`, with SHA-256
`32CAB5626FAC027D1BD379A3063D8ADB8C9D4B4B1CC5AB65540323F582B6B6DA`.
Keep every arc whose endpoints are different from 12 fixed.  The only allowed
edits are to the 18 pairs incident with 12, with exactly five of those pairs
left missing.  Thus 13 pairs incident with 12 are oriented.

The claim is that every graph in this incidence-only family satisfying
`d+(12) >= 8` has at least nine vertices with
`|N2+(v)| >= |N+(v)|`.  Consequently no such edit can lower the frozen
objective below nine.

This is a scoped obstruction.  It says nothing about edits among the other
18 vertices or about relocating a missing pair away from vertex 12.

## The fixed 18-vertex core

The vertices other than 12 split into nine ordered pairs `(h_i,l_i)`:

```text
(8,1), (10,4), (16,6), (2,9), (3,13),
(7,14), (0,15), (5,17), (11,18).
```

In every pair `h_i -> l_i`, and

```text
N+_B(h_i) = N+_B(l_i) union {l_i}.
```

Between any two pairs all four arcs have the same direction.  The quotient is
the regular nine-vertex tournament below (each row lists its four successors):

```text
A: B D F G       B: D E F G       C: A B D F
D: E G H I       E: A C H I       F: D E G H
G: C E H I       H: A B C I       I: A B C F
```

Here `A,...,I` correspond in order to the nine pairs displayed above.  In the
core `B`, every high vertex has `(d+,|N2+|)=(9,8)` and every low vertex has
`(d+,|N2+|)=(8,8)`.  The high partner is the sole core vertex unreachable in
at most two steps from its low partner.

## Incidence notation

Let `z=12`.  Let

```text
L = {i : l_i -> z},
H = {i : h_i -> z},
P = L union H,
k = |L intersection H|.
```

There are 13 present pairs incident with `z`.  Since `d+(z) >= 8`, at most
five of them point into `z`, so

```text
|L| + |H| <= 5.                                      (1)
```

Every low vertex not represented in `L` still has outdegree eight and at
least its eight old second out-neighbours.  Hence at least

```text
9 - |L|                                               (2)
```

low vertices fail the strict inequality.

Now consider high vertices.  If `i in L\H`, then `h_i` does not point to
`z`, but `h_i -> l_i -> z`.  Its old gap was exactly one, so the new second
target `z` makes `h_i` fail.  These give `|L|-k` failing highs.

For an index `x` outside `P`, if the quotient arc is `x -> p` for any
`p in P`, then `h_x` points to an in-neighbour of `z`.  Again `z` is a new
second target and `h_x` fails.

Let `X` be the set of indices outside `P` that dominate at least one member of
`P`, and put `p=|P|`.  If `Y=(V(T)\P)\X`, then every member of `P` dominates
every member of `Y`.  Summing the four quotient outdegrees over `P` gives

```text
p*|Y| + p*(p-1)/2 <= 4p,
```

and therefore, when `p>0`,

```text
|X| = 9-p-|Y| >= ceil((9-p)/2).                       (3)
```

Condition (1) gives `k<=2` and `p=|L|+|H|-k<=5-k`.
Thus (3) implies `|X|>=k` (the case `k=0` is immediate).  The indices in
`X` are outside `P`, so their failing highs are disjoint from the
`|L|-k` internal-pair failures.  There are therefore at least

```text
(|L|-k) + |X| >= |L|                                 (4)
```

failing high vertices.

Adding (2) and (4), the 18-vertex core alone contains at least nine failing
vertices.  The status of vertex 12 can only increase that number.

## Rejected sink edit

Reversing all present arcs out of 12 and moving the four low holes to their
high partners does reduce the literal failure count if the degree constraint
is ignored.  It leaves `d+(12)=0`, however, so it is outside the registered
minimum-outdegree-eight domain.  The argument above explains why restoring
`d+(12)>=8` using incidence-only edits cannot retain an objective below nine.

