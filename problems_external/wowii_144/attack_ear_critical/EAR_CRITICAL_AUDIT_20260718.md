# W144 eta deletion: 2-connected ear/UEP audit

Date: 2026-07-18.

## Status

This note proves the registered eta-nondecreasing deletion lemma for every
2-connected graph of cycle rank two.  It does **not** prove the lemma for
arbitrary cycle rank.  The first unsupported higher-ear implication is stated
in Section 6; no surrogate hierarchy is opened.

The exact frontier remains

```text
beta(G)>=2, girth(G)>=5
  ==> exists v such that G-v is connected and cyclic and
      eta(G-v)>=eta(G).                                      (EDEL)
```

The bridge is the registered one.  Vertex deletion cannot decrease girth, so
iteration of (EDEL) reaches the proved unicyclic theorem without decreasing
`girth+eta`, and the resulting induced tree remains induced in `G`.

## 1. Complete cycle-rank-two theorem

`THETA_ETA_DELETION_THEOREM_20260718.md` proves:

> If `G` is simple and 2-connected, `beta(G)=2`, and `girth(G)>=5`, then
> `G=Theta(a,b,c)` for `1<=a<=b<=c` and `a+b>=5`.  Deleting the first
> internal vertex of the `b`-path leaves a connected unicyclic graph `H`
> with `eta(H)>=eta(G)`.

The proof is explicit.  It establishes

```text
rad(Theta(a,b,c)) = floor((a+c)/2),
eta(Theta(a,b,c)) <= ceil(b/2),
eta(Theta(a,3,c)) <= 1,
```

and computes the exact eta of the cycle-plus-tail graph left by the deletion.
The independent verifier checked all 4,844 triples with path lengths at most
30, with minimum eta change zero and no failure.

Consequently W144 itself is closed for the 2-connected cycle-rank-two case:
the deletion leaves a unicyclic graph of at least the old girth and eta, to
which the proved unicyclic theorem applies.

## 2. Exact bad-deletion dichotomy

Let `G` be 2-connected, let `v` be such that `G-v` is cyclic, and write

```text
r=rad(G), r_v=rad(G-v), e=eta(G), e_v=eta(G-v),
C=C(G), C_v=C(G-v).
```

Suppose `e_v<e`.

### 2.1 Nonincreasing deletion radius

If `r_v<=r`, then `r_v=r`, and every `u in C_v-C` satisfies

```text
ecc_G(u)=r+1 and v is the unique eccentric vertex of u.       (2.1)
```

Moreover, for every surviving eta-realizer `x`, some such new center obeys

```text
d_G(x,u) <= d_{G-v}(x,u) <= e_v < e.                          (2.2)
```

For distinct deleted vertices, the sets `C_v-C` occurring in (2.1) are
disjoint, since one vertex cannot have two different unique eccentric
vertices.  The only possible deletion not forced to have a new center by
(2.2) is the deletion of the sole eta-realizer.  Thus, in an eta-critical
graph, all other radius-nonincreasing admissible deletions consume distinct
noncentral unique-eccentric-point witnesses.

### 2.2 Increasing deletion radius

If `r_v>r`, then for every old center `c in C` there is a surviving vertex
`y=y(v,c)` with

```text
d_{G-v}(c,y)>=r+1 while d_G(c,y)<=r.                          (2.3)
```

Hence every `c`--`y` path of length at most `r` in `G` uses `v`.  This is the
exact replacement-path witness left by a radius-increasing bad deletion.  In
particular, such a deletion is not covered by the UEP description (2.1).

Proof of (2.3): `ecc_{G-v}(c)>=rad(G-v)>=r+1`, so choose an eccentric-enough
`y` in `G-v`.  Since `c` is central in `G`, `d_G(c,y)<=r`; any path of that
length avoiding `v` would survive in `G-v`, a contradiction.

For an internal degree-two vertex of an ear in a 2-connected graph,
connectivity after deletion is automatic and

```text
beta(G-v)=beta(G)-1.
```

Thus every such vertex is admissible when `beta(G)>=2`, and every bad ear
deletion must leave exactly one of the two witness types above.

## 3. Exact local audit

`audit_terminal_ears.py` used the complete `geng -ctfq` corpus through order
12.  It found 973 biconnected multicyclic girth-at-least-five graphs.  Among
them, 129 were eta-tight: their best admissible deletion change was exactly
zero.  Their maximal degree-two ears gave:

```text
ears inspected                                      521
ears whose every internal deletion lowered eta      142
all-bad ears with every deletion radius-increasing  106
all-bad ears with every deletion radius-nonincreasing 36
all-bad ears with mixed radius behavior                0
maximum internal length of an all-bad ear              3
```

The zero mixed count is finite evidence only; it is not used as a theorem.

Across all 973 graphs there were 408 bad radius-nonincreasing admissible
deletions.  In 101 cases no new center furnished an admissible eta-good
deletion.  Thus the tempting exchange

```text
v is bad and u is a new UEP center  ==>  deleting u is good
```

is false.  In `H?B@dPW`, deleting `5` lowers eta from two to one and creates
new center `6`, while deleting `6` symmetrically lowers eta and creates new
center `5`.  Both deletion radii equal the old radius three.  Good deletions
exist elsewhere (`0,1,2,3`), so the reciprocal UEP pair is not itself a
counterexample to (EDEL); it kills the local exchange step.

The graph `FCR`o` supplies the other witness type.  On the ear `[5,2,6]`,
deleting its only internal vertex `2` changes `(r,eta)=(2,1)` to `(3,0)`.
Again, good deletions occur on different ears.  Therefore neither witness
type can be discarded.

## 4. Why the girth hypothesis matters

`find_short_girth_obstructions.py` enumerated every biconnected graph through
order nine and retained cycle rank at least two.  It checked 201,208 graphs
of girth three, 496 of girth four, 13 of girth five, and 3 of girth six.  The
unique eta-deletion obstruction was

```text
graph6 C^ = K4 minus one edge = Theta(1,2,2).
```

It has eta one, and each admissible deletion leaves a triangle with eta zero.
This is exactly the theta parameter excluded by `a+b>=5`.  No girth-four
obstruction occurred in this corpus.  These counts are falsification evidence;
the theta theorem itself is proved in Section 1's companion note.

## 5. Existing bounds do not remove the higher-ear case

For the W144 target `T=g-1+eta`, the proved P2 bound is

```text
P2 = diameter + ceil(g/2)-1.
```

`audit_biconnected_bounds.py` checked every biconnected multicyclic
girth-at-least-five graph through order 13, a total of 5,644 graphs.  It found

```text
P2 residuals                                      350
residual after P2 and weak W141 degree bound      303
residual after P2 and the stronger Delta+g-3 bound 206
```

The smallest residual is `H?B@dPW`, the theta graph of path lengths `(2,4,4)`:

```text
g=6, D=4, eta=2, Delta=3, target=7,
P2=6, weak-W141=5, strong-W141=6.
```

It is now closed by the theta theorem, not by those bounds.

The smallest residual of cycle rank at least three is `H?bB@qQ`:

```text
n=9, beta=3, g=5, D=3, eta=2, Delta=3, target=6,
P2=5, weak-W141=4, strong-W141=5.
```

This graph has both behaviors in the same higher-ear core.  Deleting `3`
raises the radius from two to three and collapses eta from two to zero, while
deleting `1`, `2`, `4`, or `5` preserves eta two.  It is the first exact
higher-ear residual that a structural comparison must handle.

## 6. First unsupported implication

Assume for contradiction that a 2-connected graph of cycle rank at least
three is eta-critical for all admissible deletions.  Every internal
degree-two ear vertex is admissible.  Sections 2.1--2.2 then attach to each
such vertex either

1. a disjoint family of new centers having that vertex as unique eccentric
   point, covering all surviving eta-realizers within distance `e-1`; or
2. for every old center, a replacement-path pair whose every path of length
   at most `r` uses that vertex.

What is not proved is the exact global comparison:

> In a 2-connected girth-at-least-five graph of cycle rank at least three,
> the simultaneous UEP and replacement-path witness families above force
> some admissible vertex to have nondecreasing eta.

The reciprocal pair in `H?B@dPW`, the radius-increasing ear in `FCR`o`, and
the mixed higher-ear core `H?bB@qQ` show why raw witness counting, deleting a
new center, and treating only one radius behavior do not prove this statement.
An open-ear decomposition also permits a minimum-degree-three terminal core,
so a proof restricted to internal degree-two vertices cannot close the
general case.

This witness-family incompatibility is the first unsupported implication.
Asserting it would assert the remaining 2-connected part of (EDEL), so this
audit stops here rather than introducing a weaker location rule or another
witness hierarchy.

## 7. Reproduction

From the repository root:

```text
python problems_external/wowii_144/attack_ear_critical/verify_theta_deletion_theorem.py --max-length 30
python problems_external/wowii_144/attack_ear_critical/audit_terminal_ears.py --max-n 12 --show 20
python problems_external/wowii_144/attack_ear_critical/find_short_girth_obstructions.py --max-n 9 --show 50
python problems_external/wowii_144/attack_ear_critical/audit_biconnected_bounds.py --max-n 13 --show 20
```

The corresponding JSON files in this directory record exact graph6 codes,
invariants, deletion rows, and aggregate counts.
