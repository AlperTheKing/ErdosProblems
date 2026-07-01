We are working on Erdős Problem #23, reduced to one scalar inequality
(ROWSUM-O / SPEC / LPD).  The current proof bottleneck is a row-side
residual-Hall geometry lemma.  I need one concrete proof lemma, not a survey.

Do NOT propose these dead routes:

1. Component-local single-miss / no-two-hole.  It is false on the exact hard
   H3 guardrail: `h_blowup(3)`, maxcut side
   `111111111111111100000000000`, vertex `v=18`; row `(0,15)` has two
   high-tier misses.  Residual Hall still holds there.
2. Replacement/corner-only Hall.  A 3x3 witness matrix with
   `N(f0)=N(f1)={e0}`, `N(f2)={e0,e1,e2}` has the local replacement shadow
   but violates Hall for `{f0,f1}`.
3. Scalar leakage/Hall.  The proof must keep the blue-closed prefix hull and
   multidoor fan structure.

What is already machine-checked:

* Lean file `problems/23/lean/ResidualHallScratch.lean` proves the finite
  wrappers sorry-free.
* The live framing is pure descent:

```text
no_hall_deficient_set_of_reduced_descent
```

from:

```text
hdescNonReduced:
  deficient non-reduced core -> smaller deficient core

hdescReduced:
  deficient reduced core -> smaller deficient reduced core
```

The second hypothesis is exactly the no-naked-leaf (NL) geometry below.

Setup:

Triangle-free graph `G`, connected maximum cut.  Blue/cut edges are `B`;
bad/same-side edges are `M`.  For a bad edge `f`, `cyc[f]` is the set of
shortest blue geodesic rows closing `f` into an odd cycle; `ell(f)` is the
row vertex length.

Work inside one completed terminal-shadow switch `S`.

```text
C = delta_M(S)       crossing old bad edges
E = delta_B(S)       old blue boundary exits
```

For `f in C` and `e in E`, write `Wit(f,e)` when `e` is the first exit of a
shortest blue row of `f` through `S`.  For such a witness, `Pref_S(f,e)` is
the terminal prefix inside `S` from the `S`-endpoint of `f` to the inner
endpoint of `e`.

For nonempty `X subset C`, set:

```text
Y  = Wit(X) = union_{f in X} Wit(f)
U0 = union_{f in X, e in Wit(f)} Pref_S(f,e)
U  = cl_B^S(U0)
```

where `cl_B^S` is the union of all blue connected components of `B[S]`
meeting `U0`.

Define extra boundaries:

```text
B+ = delta_B(U) \ Y
M+ = delta_M(U) \ X
```

For `g in M+`, orient `g` from its endpoint in `U` to its endpoint outside
`U`.  Define the extra-door set:

```text
D_U(g) = {
  e=xy in B+ :
    x in U, y notin U, and some shortest blue row Q of g
    has Q cap U equal to the initial segment ending at x
}
```

The extra-door graph is `(B+, M+)`, with `e~g iff e in D_U(g)`.

RFC target:

```text
For every nonempty Z subset B+,
if every g in N(Z) has at least two Z-doors,
then |N(Z)| >= |Z|.
```

Equivalently, no reduced deficient `Z` exists:

```text
|N(Z)| < |Z|
and
|D_U(g) cap Z| >= 2 for every g in N(Z).
```

Exact gates find no reduced deficient `Z` on census + hard H3, but the proof
must be mathematical.

Sharpened target discovered by an exploratory gate:

## CRFE: Componentwise Reduced Fan Expansion

For any reduced nonempty `Z subset B+`, not necessarily deficient, build the
same chosen fan complex.  For a connected fan component `K`, define:

```text
Z_K = doors of Z whose inner endpoints lie in K
H_K = rows g in H=N(Z) with at least one chosen Z-door in K
```

CRFE claims the nonnegative componentwise expansion

```text
|H_K| >= |Z_K|
```

for every nonempty fan component `K`.  Equivalently, no reduced fan component
has positive Euler surplus `|Z_K|>|H_K|`.

This immediately implies RFC, because every row `g` starts all chosen
segments at the same `U` endpoint, so all chosen `Z`-doors of `g` lie in one
fan component.  Summing over components gives

```text
|H| >= |Z|.
```

Sharper version to try first: componentwise SDR.

For each fan component `K`, form the bipartite graph:

```text
left  = Z_K
right = H_K
e -- g iff e in D_U(g)
```

The SDR claim is:

```text
for every reduced Z and fan component K,
this graph has a matching saturating Z_K.
```

This implies CRFE immediately and is a more concrete geometric target: every
door is assigned to one row that actually opens it.

Exact exploratory probe:

```text
python problems/23/writeup/_nl_leaf_broad_probe.py --h-inherited 3 --h3-hard --max-cross 15
```

Current output:

```text
switches: 155
XU: 1776
all reduced Z: 29087
fan components: 29087
min |H_K|-|Z_K|: 0
zero-margin components: 126
positive-Euler components: 0
```

The SDR probe:

```text
python problems/23/writeup/_crfe_matching_probe.py --h-inherited 3 --h3-hard --max-cross 15
```

gives:

```text
switches: 155
XU: 1776
all reduced Z: 29087
fan components: 29087
min |H_K|-|Z_K|: 0
component matching failures: 0
```

Full census through N=11 produced no reduced components:

```text
census N=11: switches=32 XU=0 reduced=0 components=0 fail=0
```

Strict `+1` expansion is false on inherited H3.  A first zero-margin example:

```text
H3-inherited, N=27, side 111111111111111000000000000
X={(15,24)}
Z={(9,25),(10,25),(11,25),(12,25),(13,25),(14,25)}
H={(15,25),(16,25),(17,25),(18,25),(19,25),(20,25)}
margin |H|-|Z| = 0
```

Please try to prove the componentwise SDR first.  If SDR is false, try the
weaker nonnegative CRFE.  If nonnegative CRFE is false, produce a concrete
counter-configuration and then fall back to the weaker NL statement below.

NL, the desired geometric atom:

Assume for contradiction that a reduced deficient `Z subset B+` exists.  Let
`H=N(Z)`.

For each incidence `(g,e)` with `g in H` and `e in D_U(g) cap Z`, choose ONE
shortest row `Q(g,e)` whose initial `U`-segment exits through `e`.  Let
`Q_U(g,e)` be that initial segment.  The executable gate chooses the
lexicographically first clean shortest initial segment; the proof can choose
arbitrarily but must use one chosen segment per incidence.

Build the chosen fan complex:

```text
F_Z = union_{g in H, e in D_U(g) cap Z} Q_U(g,e)
```

with door leaves `Z` and row hyperedges indexed by `H`.

Choose a connected fan component `K` with positive Euler surplus:

```text
|Z_K| > |H_K|.
```

A leaf branch is detected by a splitting row `g in H_K` and two doors
`e0,e1 in D_U(g) cap Z_K`.  Let `P0=Q_U(g,e0)` and `P1=Q_U(g,e1)`.  Let
`s` be their last common prefix vertex from the `U` endpoint of `g`.  The
branch toward `e0` is computed after deleting `s` and deleting the sibling
`e1`-side segment of `g` beyond `s`.  Let `Z0` be the doors of `Z_K` in the
component containing the inner endpoint of `e0`.

NL conclusion:

```text
exists g' in H_K \ {g} such that
  empty != D_U(g') cap Z subset Z0.
```

So every leaf branch contains a strictly trapped bad edge.  Since `Z` is
reduced, the trapped edge has at least two doors in the branch or yields a
smaller reduced deficient core; iterating is impossible.

The only genuine proof gap:

Because `U=cl_B^S(U0)`, some selected prefix from `X` reaches the leaf branch.
There are two cases.

Case 1. It reaches terminally through a door in `Y`.  This contradicts
`Z subset B+ = delta_B(U) \ Y`.

Case 2. It crosses the branch as a middle interval.  Need to prove that
shortest-path exchange among:

* the two chosen `g` rows splitting at `s`;
* the selected row from `X` crossing the branch as a middle interval;

produces the trapped `g'`.

Request:

Give a rigorous proof of Case 2, or a sharper exact-testable replacement
lemma.  Be explicit about:

1. what the trapped edge `g'` is;
2. why `g' in M+` (not in `X`, and crossing `U`);
3. why `D_U(g') cap Z` is nonempty;
4. why all `Z`-doors of `g'` lie in `Z0`;
5. where shortestness is used;
6. where triangle-freeness is used to exclude the degenerate splice;
7. why the proof does not rely on the false single-miss/no-two-hole or
   replacement-only Hall shortcuts.

If NL is false as written, give the smallest concrete counter-configuration
and the exact missing hypothesis.
