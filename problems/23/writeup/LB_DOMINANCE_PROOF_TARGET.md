# LB Dominance Proof Target

This is the current Codex proof target for the last Erdős #23 crux.

## Setup

Fix a connected-`B` maximum cut in a triangle-free graph.  Bad edges are
`M`; for `f in M`, `ell(f)` is one plus the shortest `B`-distance between
the endpoints of `f`, and `cyc[f]` is the set of all shortest `B`-geodesic
rows closing `f`.

Let

```text
T(v) = sum_f ell(f) * Pr_{Q in cyc[f]}[v in Q],
K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q],
R[v] = N*T(v) - (K2*T)[v].
```

Exact identity:

```text
-R[v] =
sum_{f,Q contains v} (sum_{x in Q} T(x) - N*ell(f)) / |cyc[f]|.
```

Thus `R[v] < 0` is exactly positive weighted row-overload through `v`.

## Length-Bundle Switches

For a vertex `v`, a length `L`, and an orientation, collect all rows of all
bad edges of length `L` that contain `v`.  The two candidate switches are:

```text
Pref_L(v) = union of prefixes through v,
Suff_L(v) = union of suffixes from v.
```

## Dominance Selector Lemma

For a switch `S`, define:

```text
C(S) = multiset of lengths ell(f) of bad edges f crossing S.
L(S) = multiset of boundary witness lengths lambda(e),
       one for each old B-boundary edge e crossing S,
       where lambda(e) is the minimum ell(f) among crossing bad edges
       whose shortest row exits S through e.
```

The terminal-shadow rules require every crossing bad row to see `S` as a
terminal prefix/suffix, every boundary edge to have a witness, and every
noncrossing bad edge to retain a shortest row avoiding the boundary.

Target lemma:

```text
R[v] < 0
=> exists a length-bundle switch S through v such that
   (i) boundary_delta(S)=0,
   (ii) B remains connected after flipping S,
   (iii) terminal-shadow rules hold,
   (iv) C(S) strictly tail-dominates L(S).
```

Strict tail domination means

```text
#{c in C(S): c >= t} >= #{l in L(S): l >= t}
```

for every integer threshold `t`, with strict inequality for at least one
threshold.

Since `x^2` is increasing, this implies

```text
Psi(S) = sum_{c in C(S)} c^2 - sum_{l in L(S)} l^2 > 0.
```

Together with the already-gated exact identity `DeltaGamma(S)=-Psi(S)` for
neutral terminal-shadow switches, gamma-minimality forbids `R[v]<0`.

## Exact Gates

Local gate:

```text
python problems/23/writeup/_codex_lenbundle_dominance_gate.py \
  --max-n 10 --h-blowups 3 --random 80 --examples 20
```

Result on 2026-06-30:

```text
negative=56, covered=56, fail=0
Psi histogram {24:21,48:4,96:10,144:6,216:15}
```

Diagnostics:

```text
H?AFBo] base: C=(5,7), L=(5,5).
H?AFBo][2] mixed: C=(5,5,7,7,7,7), L=(5,5,5,5,7,7).
```

So the proof should use tail-count dominance, not merely
`max(C)>max(L)`.

## False Strengthenings

These are exact-disproven and should not be used:

1. Any positive-overload row through `v` gives a switch.
   False at `I?BD@g]Qo`, side `0001111000`, `v=5`, where `R[v]=466/45>0`.

2. A positive same-length bundle average gives a switch.
   False at `H?AFBo]`, side `111110000`, `v=6`: length-5 rows through `v`
   have overload `+3`, but the valid descent comes from the length-7
   enclosing bundle.

3. Arbitrary harmonic two-level terminal shadows bridge to `Psi`.
   False at `H?AFBo]`, `O=[6,7,8]`, unit `o=6`, thin annulus
   `A={6}`, `B={0,1,2,6}`.

## Stronger Matching Atom

The local gate supports a stronger statement that may be easier to prove.

For a terminal-shadow switch `S`, each old `B`-boundary exit `e` has a
witness set

```text
Wit(e) = {crossing bad edges f whose shortest row exits S through e}.
```

For every cutoff `t`, define

```text
C_<t = {f crossing S : ell(f) < t},
E_<t = {boundary exits e : lambda(e) < t}.
```

Matching atom:

```text
For every cutoff t, C_<t can be matched injectively into E_<t
using only witness incidences f -> e with f in Wit(e).
```

This implies `|C_<t| <= |E_<t|` for every cutoff. Because the switch is neutral,
this is equivalent to tail dominance of the crossing lengths over the boundary
witness lengths.

Local gate:

```text
python problems/23/writeup/_codex_lenbundle_matching_gate.py \
  --max-n 10 --h-blowups 3 --random 80 --examples 20
```

Result on 2026-06-30:

```text
negative=56, covered=56, fail=0
Psi histogram {24:21,48:4,96:10,144:6,216:15}
```

This matching atom suggests a proof route by Hall's theorem. It would be
enough to show that for the selected length-bundle switch and every family
`X` of short crossing bad edges, the union of their short exits has size at
least `|X|`. Triangle-free shortest-geodesic geometry should enter exactly
here: two short crossing packets cannot be forced through the same short exit
unless a longer packet supplies the surplus on the crossing side.
