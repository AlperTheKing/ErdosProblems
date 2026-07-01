# L=5 Forcing Atom for Deficient Cap Cores

Status: frontier proof atom after the stretched-core algebra test.

## Facts Now Fixed

The repaired cap-side classification gives:

```text
deficient cap component
=> nested L/(L+2) core + pure odd-cycle baggage
```

where `L` is odd and at least `5`.

The algebraic sign route cannot be extended to all odd `L`. The natural
stretched core, which matches the canonical `L=5` core exactly, has:

```text
R_local(t or chain vertex) = -2L^2 + (23/2)L + 11
R_local(a1)                = -(3/2)L^2 + (33/4)L + 17/2
```

so it is already negative at `L=7`.

Claude independently tested the concrete `L=7` stretched graph:

```text
triangle-free = true
defcap = 0
```

The intended bad edges do not survive the actual gamma-min maximum cut. The
gamma-min cut places a single bad edge in the shared corridor, cutting the
two intended terminal bad edges.

Thus the cap proof must force:

```text
deficient cap core => L=5.
```

## Candidate Mechanism

For `L>5`, a nested `L/(L+2)` core contains a nonempty internal shared
`B`-corridor segment. Some edge of this segment lies on every shortest row of
both core bad edges. Call such an edge a universal core hit.

If a universal core hit `e` exists, then the two core odd-cycle families have
transversal number `1`: making `e` monochromatic hits every core odd cycle.
The intended deficient cap cut has two crossing bad edges in that component.
Therefore one should be able to switch the core so that:

```text
old core bad edges disappear,
e becomes the only core bad edge,
```

or at least:

```text
the number of bad edges does not increase and Gamma strictly decreases.
```

Either outcome contradicts the completed cap switch being drawn from a
connected-`B`, gamma-minimal maximum cut.

The canonical `L=5` core avoids this because the common region is a theta
with two parallel middle exits; no single `B`-edge is present in all core
rows. The core odd cycles still require two bad edges, and the local sign is
the verified `25/4`.

## Proof Target

Prove the following.

### Shared-Corridor Hit Lemma

In a minimal deficient cap component with nested `L/(L+2)` core, if `L>5`,
then the core row family has a universal core hit `e in B`.

### Core Recut Lemma

If a deficient cap component has a universal core hit `e`, then there is a
switch supported on the core corridor such that the resulting cut is still
maximum and connected-`B`, but either:

```text
|M| decreases,
```

or:

```text
|M| is unchanged and Gamma decreases.
```

This contradicts the selected cut. Hence `L>5` is impossible.

## Exact Gate

For every attempted `L>5` realization:

1. Extract the core bad edges and their shortest row families.
2. Compute the intersection of all core row edge sets.
3. If the intersection is nonempty, test every universal hit `e` by forcing
   `e` monochromatic and reoptimizing the component cut.
4. Accept the forcing atom when the reoptimized cut is maximum and has lower
   core `Gamma`, or fewer core bad edges.

The existing concrete `L=7` stretch passes this pattern: the shared corridor
edge becomes the unique gamma-min bad edge, so the deficient cap vanishes.

## Natural Stretch Gate

Codex gate:

```text
python problems/23/writeup/_codex_l5_forcing_gate.py --max-L 17
```

For every tested odd `L=7,9,11,13,15,17`:

```text
intended_bad = {s-t, u-v}
intended_gamma = L^2 + (L+2)^2
gamma-min bad set = {one shared corridor edge}
gamma-min gamma = L^2
intended_survives = False
```

The gamma-min bad edge is always one of:

```text
c_i c_{i+1}
```

inside the internal shared corridor.

This gives the concrete recut formula. If `e=c_i c_{i+1}` is an internal
shared corridor edge, color the core alternately on the two sides of `e` and
make only `e` monochromatic. Then:

1. all old blue edges except `e` are cut;
2. the intended terminal bad edges `s-t` and `u-v` become cut edges;
3. the new bad edge `e` has a replacement blue path around the shorter
   terminal cycle of length `L-1`, hence new odd length `L`;
4. the core bad-edge count drops from `2` to `1`;
5. the core gamma drops from `L^2+(L+2)^2` to `L^2`.

Thus any realizable deficient cap with an internal universal shared edge is
not gamma-minimal in isolation. The remaining proof issue is to justify that
the same recut is legal inside a completed deficient component with its
outside boundary attachments fixed, or to prove that minimality forces those
attachments to be absent from the internal shared corridor.

## Single-Attachment Stress

Codex gate:

```text
python problems/23/writeup/_codex_l5_forcing_gate.py --single-extra-L 7
```

This enumerates every one-edge triangle-free addition to the `L=7` stretched
core and asks whether any gamma-min connected-`B` max cut preserves the
intended terminal bad edges `{s-t,u-v}`.

Result:

```text
single-extra L 7 intended-survivors 4
```

The four extra edges are:

```text
u-b0, u-b1, x-c0, v-a0
```

and in every survivor the actual intended bad-edge lengths are:

```text
ell(s-t)=5, ell(u-v)=5
min_gamma=50
```

Thus every one-edge attachment that blocks the universal-corridor recut does
so by creating a shorter row for the supposed length-`9` parent. It therefore
destroys the `L/(L+2)=7/9` premise rather than realizing it.

This is the finite shadow of the expected boundary-compatibility lemma:

```text
Any outside attachment that prevents the one-edge shared-corridor recut
creates an intermediate terminal door or a shorter parent row.
```

Claude's independent mirror (`_l5_attach_test.py`) confirms the same
phenomenon:

```text
L=7: one-edge triangle-free attachments tested; 0 preserve lengths (7,9).
     blockers collapse to (5,5).
L=9: one-edge triangle-free attachments tested; 0 preserve lengths (9,11).
     blockers collapse to (5,5).
```

Thus two independent implementations agree: no one-edge attachment preserves
a genuine `L/(L+2)` core for `L>5`; every blocker creates a shorter terminal
row, which is exactly the S2 contradiction.

## Arbitrary-Realization Hit Lemma

The remaining non-computational cap lemma should be stated as follows.

Let a minimal deficient cap component have nested `L/(L+2)` core, with child
bad edge `f0` and parent bad edge `f1`. Then the core row family has a
terminal-product normal form:

```text
left terminal cap  --  common middle corridor  --  right terminal cap
```

where all choices in the shortest-row bundles occur inside the two terminal
caps. No row bundle can split, rejoin, and then split again in the middle.

Reason: two interior splits give a reduced blue theta. The two equal-length
arms of that theta either:

1. expose an intermediate terminal door, contradicting the minimal deficient
   Ferrers block used in the cap classification; or
2. splice to a strictly shorter blue geodesic for `f0` or `f1`,
   contradicting shortestness.

This is exactly the S2 exclusion already used to force the annulus increment
to be `2`: a row crossing the elementary lens or an intermediate terminal
door contradicts minimality.

In the terminal-product normal form, the canonical `L=5` core has a common
middle of one vertex:

```text
left cap -- z -- right cap
```

so there is no universal middle edge. For `L>=7`, the common middle corridor
has at least two vertices and hence contains a `B`-edge used by every shortest
row of both core bad edges. That edge is the universal core hit.

Thus the proof of `L=5` forcing reduces to applying the already accepted S2
geometry to rule out interior branching in an arbitrary realization.
