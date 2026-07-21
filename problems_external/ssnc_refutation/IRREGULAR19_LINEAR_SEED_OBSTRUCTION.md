# Independent obstruction to `IRREGULAR19_INCIDENCE_SEED.json`

Status: **THE FIXED JSON ROOT SYSTEM IS CONTRADICTORY**.

This report independently attacks the registered `IRREGULAR ORDER-19
LINEAR-SEED LIFT`.  It reads only the fixed missing graph and declared root
incidence in `IRREGULAR19_INCIDENCE_SEED.json`; the stored orientation is not
used or pinned.

The contradiction lies in the saturated singleton fibres.  It occurs before
an orientation completion or literal two-step reachability model is needed.
The conclusion excludes only this exact JSON seed.

## 1. Independent coarse-data replay

The JSON has SHA-256

```text
B4BFB3000D9F14E7C763764DDF474FECD166DE12CC7F96B9D593F8801DF5EF69
```

Direct replay of the missing graph and incidence gives:

```text
missing degrees = [4,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1]
target sizes    = [7,5,5,5,5,5,5,5,5,1,1,1,1,1,1,1,1,1,1]
source sizes    = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
diagonal root incidences = 0
missing pairs inside root blocks = 0
```

The declared source fibres are exactly the transpose of the target fibres.

Despite the route name, the root system is not linear.  Among the 171 pairs
of target blocks, the intersection-size histogram is

```text
{0:129, 1:31, 2:8, 3:2, 4:1}; maximum intersection = 4.
```

For example,

\[
 R_0\cap R_1=\{3,8,10,12\}.
\]

This terminology issue is not used as a contradiction; larger saturated
blocks are not known here to be linear.

## 2. Exact saturated-block equations

Every vertex has outdegree eight.  For a target `u` of missing degree
`m=mu_u`, define

\[
 U_u=V\setminus(\{u\}\cup N^-(u)),\qquad
 C_v=\{v\}\cup N^+(v).
\]

If the declared root block is the literal unreachable fibre, then for every
`v in R_u`,

\[
 C_v\subseteq U_u,qquad |U_u|=8+m,qquad |C_v|=9.
\]

All declared target sizes saturate the capacity bound:

\[
 |R_u|=2m-1.
\]

Writing `B_v=U_u minus C_v`, equality in the pair-cover count forces:

1. `B_v` is contained in `R_u`;
2. every root pair is covered by exactly one ordered exclusion;
3. no root pair is missing;
4. `R_u` induces a regular tournament; and
5. `B_v=N^-_{R_u}(v)`.

Thus every saturated block obeys the exact indicator equation

\[
 \boxed{
 A_u+M_u=\mathbf e_v+A_v+\mathbf1_{N^-_{R_u}(v)}
 }
 \qquad(v\in R_u),                                  \tag{1}
\]

where `M_u` is the missing-neighbour indicator row.

For a vertex outside `R_u`, all non-adjacency terms on the right of (1)
vanish.  Consequently the roots have identical external adjacency columns:

\[
 A[v,x]=A[w,x]
 \qquad(v,w\in R_u,\ x\notin R_u).                  \tag{2}
\]

The block types specialize to regular tournaments of orders seven, five,
and one.  In particular, if `R_u={v}` is a singleton, (1) becomes

\[
 \boxed{U_u=C_v},\qquad
 \boxed{A_u+M_u=\mathbf e_v+A_v}.                   \tag{3}
\]

## 3. Repeated-singleton contradiction

Target sets are injective in every oriented graph.  If `U_u=U_w` for
distinct targets, then `u notin U_w` forces `u -> w`, while `w notin U_u`
forces `w -> u`, a forbidden digon.

The JSON singleton map is

```text
9->1, 10->15, 11->7, 12->6, 13->4,
14->18, 15->18, 16->0, 17->6, 18->15.
```

It repeats three roots:

```text
root 15: targets 10 and 18
root  6: targets 12 and 17
root 18: targets 14 and 15
```

For example, (3) gives

\[
 U_{14}=C_{18}=U_{15},
\]

contradicting target-set injectivity because `14 != 15`.  Each of the other
two repeated roots gives an independent contradiction of the same form.

## 4. Independent singleton-cycle contradiction

The seed also contains the singleton two-cycle

\[
 R_{15}=\{18\},\qquad R_{18}=\{15\}.
\]

The two instances of (3) are

\[
 A_{15}+M_{15}=\mathbf e_{18}+A_{18},                \tag{4}
\]

\[
 A_{18}+M_{18}=\mathbf e_{15}+A_{15}.                \tag{5}
\]

Adding (4)--(5) cancels the adjacency rows and requires

\[
 M_{15}+M_{18}=\mathbf e_{15}+\mathbf e_{18}.        \tag{6}
\]

In the fixed missing graph, vertex 15 is the leaf at vertex 5 and vertex 18
is the leaf at vertex 8.  Hence

\[
 M_{15}=\mathbf e_5,qquad M_{18}=\mathbf e_8,
\]

and (6) would say

\[
 \mathbf e_5+\mathbf e_8
   =\mathbf e_{15}+\mathbf e_{18},
\]

which is false coordinate by coordinate.  Its sparse residual is

```text
{5:+1, 8:+1, 15:-1, 18:-1}.
```

This potential-cycle certificate does not use target-set injectivity and is
therefore an independent local obstruction.

## 5. Exhaustive audit and exact scope

`audit_irregular19_linear_seed.py` independently verifies the JSON hash,
missing degrees, block and source sizes, transpose relation, zero diagonal,
missing-edge avoidance, and block intersections.  It then emits the repeated
singleton roots, the singleton two-cycle, and the nonzero row-potential
residual, terminating with

```text
certificate=UNSAT_SINGLETON
```

Any lift of the registered JSON seed must satisfy the singleton equations
(3), but the fixed incidence violates them.  Therefore no reorientation of
the fixed present pairs can make the declared fibres the literal unreachable
relation.

This does not exclude a different root system or missing graph with the same
degree multiset.  Under the registered exit condition it closes only this
exact JSON mechanism and does not authorize an incidence or order cascade.

