# Frozen S2 Reduced-Theta Statement

This is the theorem package to hand to Lean/Claude.  It separates the pure
walk-length argument from the application-specific geometry.

The broad row/cap statements are false without their minimality scopes.  This
file states only the common S2 atom and the exact hypotheses an application
must prove before invoking it.

## Ambient Definitions

Let `G` be a finite simple graph and let `B` be the blue/cut subgraph.  A
`B-walk` means every edge of the walk lies in `B`.

For a bad edge

```text
h = ab
```

write

```text
D_h = ell(h)-1 = dist_B(a,b).
```

A shortest row for `h` is a `B`-walk `P` from `a` to `b` of length `D_h`.

The applications always supply terminal-prefix rows, but the pure S2 splice
does not need the switch language.

## S2-Core 1: Shorter Replacement Walk

### Statement

Let `P` be a shortest row for `h=ab`.  Suppose `P` is decomposed as

```text
P = Prefix ++ OldArm ++ Suffix
```

and suppose there is a `B`-walk `NewArm` with the same endpoints as `OldArm`
such that

```text
len(NewArm) + 2 <= len(OldArm).
```

Then the concatenated walk

```text
P' = Prefix ++ NewArm ++ Suffix
```

is a `B`-walk from `a` to `b` with

```text
len(P') <= D_h - 2 = ell(h)-3.
```

Consequently `dist_B(a,b) <= ell(h)-3`, contradicting the definition
`D_h=ell(h)-1`.

### Lean shape

```text
ShortestRow(P,a,b,D_h)
SameEndpoints(OldArm,NewArm)
P = Prefix ++ OldArm ++ Suffix
len(NewArm)+2 <= len(OldArm)
-------------------------------------------------
exists P', BWalk(P',a,b) and len(P') <= D_h-2
```

No triangle-free hypothesis is needed here.  It is pure walk concatenation and
arithmetic.

## S2-Core 2: Triangle Degeneracy

### Statement

In the reduced-theta applications, the only case where the proposed
replacement is not an ordinary blue arm is the length-two degeneration around
one bad edge:

```text
u --B-- x --B-- v
```

together with the bad edge

```text
uv in E(G)\B.
```

Then `u,x,v` form a triangle in `G`.

### Lean shape

```text
BEdge(u,x), BEdge(x,v), BadEdge(u,v)
u, x, v pairwise distinct
------------------------------------
Triangle(G,u,x,v)
```

This is trivial graph theory, but keeping it separate prevents the main splice
lemma from carrying triangle-free baggage.

## S2-Core 3: Strict Reduced Terminal-Theta

### Data

A strict reduced terminal theta for a bad edge `h=ab` consists of:

```text
1. A shortest row P for h, decomposed as
      Prefix ++ OldArm ++ Suffix.

2. A candidate replacement arm NewArm with the same endpoints as OldArm.

3. A strict saving:
      len(NewArm)+2 <= len(OldArm).

4. Terminal-prefix / no-reentry conditions ensuring that every edge of
   NewArm is blue, unless the configuration is exactly the triangle
   degeneration of S2-Core 2.

5. Application-specific reducedness:
   no smaller split/rejoin or earlier shadow interaction should have been
   selected instead.
```

### Conclusion

At least one of the following holds:

```text
1. There is an intermediate terminal door.
2. G contains a triangle.
3. Some involved bad edge h has a blue walk between its endpoints of length
   <= ell(h)-3.
```

Thus, in a triangle-free configuration with shortest rows and no intermediate
terminal door, a strict reduced terminal theta is impossible.

### Lean shape

The first Lean version should not try to encode all geometry at once.  It
should take the following disjunction-producing hypothesis from the
application:

```text
ApplicationGeometry ->
  IntermediateDoor OR
  TriangleDegeneration OR
  ValidReplacementArmSavingAtLeastTwo.
```

Then S2-Core 1 and S2-Core 2 produce the theorem:

```text
ApplicationGeometry ->
  IntermediateDoor OR Triangle OR ShorterBlueRow.
```

`NoIntermediateDoor` is not a core hypothesis. It is only an
application-level case split: if a door exists, the application closes by
minimality; otherwise the triangle/shorter-row alternatives close.

## What Each Application Must Prove

### Row TH-long / EHR

From a genuine minimal two-hole corridor with a high-tier endpoint, prove:

```text
Endpoint slack s_f(e0)>=2
shortest J-corridor reducedness
terminal-prefix hinge rows
--------------------------------
ApplicationGeometry
```

Broad singleton high-tier misses do not satisfy this scope.

### Row TH-rare / RM

From the first interaction of two cost-flat shadows, prove:

```text
first-interaction reducedness
directional near-witness failure
terminal-prefix 5/7 annuli
--------------------------------
ApplicationGeometry OR F1WitnessSetInclusion
```

If `ApplicationGeometry`, S2 closes.  If `F1WitnessSetInclusion`, the
stage-0 alternating exchange closes.

### Cap L=5 Forcing

From a minimal deficient nested core with `L>=7`, prove:

```text
annulus excess >=2
minimal deficient core reducedness
terminal-product / no intermediate door
--------------------------------
ApplicationGeometry
```

S2 then supplies the universal shared blue corridor edge or a direct
contradiction.  The core recut gives the final gamma descent.

## Acceptance Criteria For This File

Before starting Lean on S2, Claude/Codex should agree that:

```text
1. S2-Core 1 is purely a walk-concatenation lemma.
2. S2-Core 2 is purely a triangle lemma.
3. S2-Core 3 is only a wrapper around 1 and 2 plus an
   application-supplied geometry disjunction.
4. No broad HT/RM/H3 statement is embedded in S2 itself.
```

This keeps false broad statements out of the formal core.
