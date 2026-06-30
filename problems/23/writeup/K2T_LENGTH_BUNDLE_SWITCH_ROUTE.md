# K2T Length-Bundle Switch Route

Status: active proof route for the CSM/K2T certificate.

## Target

For a connected-B maximum cut, define

```text
R[v] = N*T[v] - (K2*T)[v].
```

The exact-gated Collatz certificate is

```text
R[v] >= 0  for every vertex v.
```

This implies `rho(K2) <= N` by Collatz-Wielandt, hence `rho(K) <= N` by
Jensen, hence `Gamma <= N^2`.

It is enough to prove the contrapositive switch statement:

```text
R[v] < 0
=> there exists a cut-neutral B-connected switch S containing v
   with Gamma(after S) < Gamma(before).
```

Then gamma-minimality forbids `R[v] < 0`.

## False Narrow Candidate

The first narrowed switch family used one bad edge at a time:
for a bad edge `f`, union all prefixes or suffixes of shortest rows in
`cyc[f]` that contain `v`.

This is false.

Counterexample:

```text
H?AFBo][2], inherited side from 111110000
N = 18
cut = maxcut = 40
Gamma = 296
bad-edge lengths = {5, 7}
negative residual vertices = 14
per-bad-edge half-switch coverage = 2 / 14
arbitrary neutral Gamma-descent switch coverage = 14 / 14
```

Reason: in a blow-up, the descent switch is not attached to one bad edge.
It flips an entire equal-length row bundle.

## Repaired Candidate

For each length `L` and vertex `v`, collect all shortest rows `Q` of all
bad edges `f` with `ell[f] = L` and `v in Q`.

For each orientation define two candidate switches:

```text
Pref_L(v) = union_Q Q[:index_Q(v)+1]
Suff_L(v) = union_Q Q[index_Q(v):]
```

where the union is over all oriented rows of length `L` containing `v`.

Candidate theorem:

```text
If R[v] < 0, then for some length L and orientation,
Pref_L(v) or Suff_L(v) is cut-neutral, leaves B connected with finite Gamma,
and strictly decreases Gamma.
```

Gate script:

```text
problems/23/writeup/_codex_k2t_lenbundle_switch_gate.py
```

## Local Exact Evidence

Run:

```text
python _codex_k2t_lenbundle_switch_gate.py --max-n 10 --h-blowups 3 --random 80 --examples 16
```

Result:

```text
census N<=10: fail=0
H?AFBo][2]: inherited cut, 14/14 negative vertices covered
H?AFBo][3]: inherited cut stress, 21/21 covered
random 80 connected triangle-free N=11/12: no new negative-residual vertices
```

`H?AFBo][2]` was separately brute-confirmed to have inherited cut maximum:

```text
N=18, cut=40, maxcut=40.
```

## Structural Reading From H?AFBo] And Blow-Ups

For the base obstruction `H?AFBo]`, side `111110000`:

```text
bad edges: (5,8) with ell=7, (6,8) with ell=5
T = [7,6,6,6,6,7,12,12,12]
R = [1,-1,-1,-1,-1,1,-2,-2,-2]
Gamma = 74
```

Rows of length 7 have overload `-1`.
Rows of length 5 have overload `+3`.
The negative residual is caused by the positive length-5 contribution
overwhelming the negative length-7 contribution, but the descent switch is
the length-7 bundle switch.  It replaces the length-7 packet by length-5
bad edges and lowers Gamma to `50`.

In `H?AFBo][2]`, a typical switch at a clone of vertex 1 is

```text
S = {both clones of 5, both clones of 0, both clones of 6, chosen clone of 1}
```

This is exactly `Pref_7(v)` over the whole length-7 bundle, not a single
bad-edge prefix.

## Proof Obligation

The desired proof should show:

```text
R[v] < 0
=> some equal-length geodesic bundle through v has a principal prefix/suffix
   whose switch is neutral and shortens at least one old bad row.
```

Equivalently, prove the contrapositive:

```text
If every length-bundle half-switch through v is either cut-positive or
nondecreasing in Gamma when neutral, then R[v] >= 0.
```

This has the shape of a discrete coarea/uncrossing theorem over the
geodesic row posets of fixed length.  The failed per-bad-edge theorem shows
that the coarea unit must be the equal-length bundle, not an individual
bad edge.

## Strict-Lens Simplification Check

It is tempting to replace the negative-residual hypothesis by the simpler
condition that `v` lies on the short side of a strict bad-geodesic lens.  This
is false.

Gate:

```text
python _codex_k2t_strict_lens_switch_gate.py --max-n 10 --h-blowups 3 --random 80
```

Result:

```text
strict-lens short vertices covered: 386
strict-lens short vertices FAIL: 128
negative vertices covered: 56
negative vertices FAIL: 0
first strict-lens-only failure:
  ('I??CF@wFo', 10, '1111110000', 9, R[9]=10, strict_lens_pairs=1)
```

So strict lenses are not forbidden by gamma-minimality in isolation.  The
current proof target must keep the weighted hypothesis:

```text
R[v] < 0
=> some length-bundle half-switch through v is cut-neutral, B-connected,
   terminal-geodesic/safe, and has Psi(S)>0.
```

The terminal-shadow gates then give the Gamma descent using only old-cut data.

## Psi-Only Refinement

The explicit neutrality filter may not be the structural core.  Local scan:

```text
terminal-shadow length-bundle switches with Psi>0:
  total: 903
  neutral: 903
  nonneutral: 0
```

And the simplified target also passes:

```text
R[v] < 0
=> some length-bundle switch through v has terminal_shadow_psi(S)>0
```

Gate on the same local battery:

```text
negative vertices: 56
covered by terminal_shadow_psi(S)>0: 56
fail: 0
chosen nonneutral or non-B-connected: 0
```

So the proof may split into:

```text
1. R[v]<0 produces a length-bundle terminal-shadow switch with Psi(S)>0.
2. For this switch family, terminal-shadow Psi(S)>0 plus max-cut implies
   boundary_delta(S)=0 and B^S connected, or these are forced by the same
   closure argument.
3. Psi(S)>0 gives Gamma descent by the terminal-shadow replacement lemma.
```

Local auxiliary gate for step 2:

```text
terminal-shadow length-bundle switches with Psi>0:
  total: 903
  boundary_delta=0: 903
  B^S connected: 903
  fail: 0
```

Positive `Psi` is not equivalent to `R[v]<0`; there are positive-residual
vertices with positive-`Psi` switches.  This is harmless and clarifies the
logic:

```text
gamma-minimality forbids every positive-Psi terminal-shadow switch,
while R[v]<0 only has to force existence of one.
```

## Dead Selector: Peak Terminal Overload

The deterministic selector

```text
maximize Omega_{L,sign}(v)/(L*m_L(v))
```

does not choose the descent bundle in general, although its coarea identity is
exact.

Gate:

```text
python _codex_peak_terminal_overload_gate.py --max-n 10 --h-blowups 3 --random 80
```

Result:

```text
Omega identity failures: 0
negative vertices: 56
some peak good: 47
some peak FAIL: 9
```

First failure is the base `H?AFBo]` cut `111110000` at vertex `6`:

```text
R[6] = -2.

Peak bundles:
  L=5 pref:  Omega=3/2, score=3/10, S={6}, delta=2, not B-connected.
  L=5 suff:  Omega=3/2, score=3/10, S={1,2,3,4,6,7,8}, delta=0, Psi=0.

Working descent:
  L=7 pref:  Omega=-5/2, score=-5/14, S={0,5,6}, delta=0, Psi=24.
```

So the correct selector cannot be “positive terminal overload.”  The descent
packet may be a longer enclosing bundle with negative terminal overload whose
crossing square surplus pays for the short overloaded packet.

## Dead Completion: Two-Level Schur Annulus

The Schur/double-coarea algebra is exact, but the literal annulus-completion
bridge is false.

Gate:

```text
python _codex_twoshadow_completion_gate.py --max-free 18
```

Result:

```text
harmonic unit phis: 65
negative two-level shadows: 124
annulus completions pass: 33
annulus completions FAIL: 91
```

First failure is again the base `H?AFBo]` cut `111110000`, overload vertex
`6`, with

```text
A = {6}
B = {0,1,2,6}
1_A^T H 1_B < 0
```

Every completion constrained by

```text
A subset W subset B
```

has positive cut-loss or disconnects `B`.  The actual Gamma-decreasing switch is

```text
W = {0,5,6},
```

which necessarily adds vertex `5` outside the threshold annulus.  A relaxed
diagnostic that merely asks for a length-bundle switch containing `A` is also
false on the Schur shadows:

```text
negative shadows: 124
pass: 54
FAIL: 70
first fail: MycGrotzsch_N23, A={1}
```

So the two-level route is still useful as algebraic intuition, but the
rounding/completion statement must be replaced by a terminal closure that is
allowed to leave the Schur annulus.  The surviving finite theorem remains the
vertexwise length-bundle construction:

```text
R[v] < 0
=> some equal-length prefix/suffix bundle through v has terminal_shadow_psi > 0.
```

## Length-Majorized Terminal Shadow

The winning switches satisfy a stronger finite normal form.

Gate:

```text
python _codex_k2t_switch_signature_gate.py --max-n 10 --h-blowups 3 --random 80 --examples 30
```

Result:

```text
negative vertices: 56
covered: 56
FAIL: 0
sorted crossing lengths majorize boundary prices: 56 / 56
```

For a terminal-shadow switch `S`, let

```text
A(S) = sorted list of ell[f] for f in delta_M(S)
B(S) = sorted list of lambda_S(e) for e in delta_B(S)
```

where `lambda_S(e)` is the minimum length of a crossing bad edge witnessing the
new boundary edge `e`.  In every selected switch:

```text
|A(S)| = |B(S)|,
A_i(S) >= B_i(S) for all i,
and A_i(S) > B_i(S) for at least one i.
```

Thus

```text
Psi(S) = sum_i A_i(S)^2 - sum_i B_i(S)^2 > 0.
```

This is more structured than the raw `Psi>0` inequality.  It suggests the
next proof target:

```text
R[v] < 0
=> there is a length-bundle half-switch through v whose terminal shadow is
   length-majorized in the sense above.
```

The chosen bundle length `L` itself is not enough to state the theorem.  The
winning switch can have crossing lengths both below and above `L`, and boundary
prices can equal `L`.  What survives exactly is the sorted old-crossing versus
new-boundary price domination.

An even cleaner equivalent normal form is a witness-Hall matching.  Build the
bipartite witness graph

```text
left  = crossing bad edges f in delta_M(S)
right = boundary cut edges e in delta_B(S)
f -- e iff some shortest row of f exits S through e.
```

For every selected switch in the same gate:

```text
perfect witness matching: 56 / 56
strict matched witness:   56 / 56
```

Here strict means that for at least one matched pair `(f,e)`,

```text
ell[f] > lambda_S(e).
```

Since every matched edge satisfies `lambda_S(e) <= ell[f]`, a strict perfect
matching immediately gives

```text
sum_{f in delta_M(S)} ell[f]^2
>
sum_{e in delta_B(S)} lambda_S(e)^2.
```

Thus the current most proof-friendly target is:

```text
R[v] < 0
=> there is a length-bundle half-switch S through v such that its terminal
   witness graph has a strict perfect matching.
```

This packages the square surplus as a Hall statement over terminal exits rather
than as a scalar overload selector.

## Lmax Selector

The length parameter can also be fixed more sharply.

For a vertex `v`, let

```text
Lmax(v) = max { ell[f] : some Q in cyc[f] contains v }.
```

Restrict the length-bundle candidates to `L = Lmax(v)`.  Local gate:

```text
census N<=10 + H?AFBo][2,3,4] + 80 random N11/12
negative vertices: 84
covered by Lmax bundle with strict witness matching: 84
FAIL: 0
```

In this battery every negative vertex has `Lmax=7`; the shorter length-5 rows
create the positive row-overload, while the length-7 terminal bundle supplies
the square surplus.

So the current sharpest statement is:

```text
R[v] < 0
=> one of the two terminal half-bundles of the longest rows through v has a
   terminal witness graph with a strict perfect matching.
```

Equivalently, if both longest-row terminal half-bundles fail strict
witness-Hall, then the summed row-overload through `v` is nonpositive.

In fact the gate suggests an even more canonical statement.  For every
negative-residual vertex in the local battery, all four `Lmax` half-bundles
(two row orientations times prefix/suffix) are already neutral and
terminal-shadow valid:

```text
census N<=10 + H?AFBo][2,3,4]
negative vertices: 84
Lmax half-bundles checked: 336
delta_B(S)-delta_M(S)=0: 336 / 336
terminal-shadow valid: 336 / 336
```

Thus the hard part is not finding a legal switch once `Lmax` is chosen.  The
hard part is proving that at least one of the two sides has strict length
surplus whenever `R[v]<0`.

## Witness Component Balance

The Hall condition appears to be a consequence of an even more local balance.
For each selected `Lmax` switch, decompose the witness graph

```text
crossing bad edges  --  boundary exits
```

into connected components.  Local gate:

```text
census N<=10 + H?AFBo][2,3,4]
selected Lmax switches: 84
components with #left < #right: 0
component histogram:
  (2,2): 21
  (8,8): 14
  (18,18): 15
  (32,32): 20
  plus smaller balanced components (4,4),(6,6),(12,12),(20,20)
```

So the matching may not require a global Hall argument.  A sharper structural
lemma is:

```text
Every connected component of the terminal witness graph of an Lmax
length-bundle half-switch has the same number of crossing bad edges and
boundary exits.
```

Then Hall follows componentwise.  The remaining strictness is the assertion
that at least one component contains a crossing bad edge longer than the
minimum witness price of its matched boundary exit whenever `R[v]<0`.

The component balance has a concrete boundary identity behind it.  For a
witness component `C`, let

```text
Y_C = crossing bad edges in C
X_C = boundary cut exits in C
U_C = union of all terminal prefixes, inside S, of all rows of f in Y_C.
```

Gate:

```text
census N<=10 + H?AFBo][2,3,4]
components checked: 84
failures: 0
```

The exact identity is:

```text
delta_M(U_C) = Y_C,
delta_B(U_C) = X_C.
```

Thus max-cut gives `|X_C| >= |Y_C|` for every component.  Since the full switch
has `delta_B(S)=delta_M(S)` in all gated cases, this forces equality component
by component and gives the perfect matching.  The proof obligation has now
split into two local statements:

```text
1. Component boundary identity:
   delta_M(U_C)=Y_C and delta_B(U_C)=X_C.

2. Lmax switch neutrality and strictness:
   the selected Lmax half-switch has delta_B(S)=delta_M(S), and at least one
   component has a strict length surplus.
```

The first looks like pure terminal-geodesic uncrossing.  The second is where
the residual hypothesis `R[v]<0` must enter.

## 2026-06-30 Correction: Strictness Needs The Moat

Claude's all-max-cut battery on `H?AFBo][2]` refutes the bare Lmax strictness
selector.  On the non-gamma-min maximum cut

```text
side = 101111111111000000
```

there are vertices with `R[v]<0` for which the Lmax half-bundles are legal
and neutral but have `Psi=0`.  The Gamma-decreasing switches are completed
seed+moat blocks, for example:

```text
v=2:  S={0,2,12,13},          Gamma 296 -> 200, Psi=96.
v=14: S={0,2,3,4,5,12,13,14}, Gamma 296 -> 200, Psi=96.
```

Thus the current target is no longer:

```text
R[v]<0 => a bare Lmax half-bundle is strict.
```

The surviving target is:

```text
R[v]<0
=> a length-bundle seed has a neutralizing moat completion S
   which is terminal-shadow valid, B-connected after flipping, and Psi(S)>0.
```

The completed-switch exact gate is `_codex_bundle_moat_gate.py`.

## Side-Door Prefix Hull Gate

The proposed Hall correction was tested on the seed+moat completed switches in
`_codex_sidedoor_prefix_hull_gate.py`.

For a completed terminal-shadow switch `S`, crossing bad edges `C`, exits `E`,
cutoff `t`, and `Y subset E_<t`, set:

```text
X = { f in C : ell(f)<t and Wit(f) subset Y },
U = union of the terminal prefixes Pref_S(f,e), f in X, e in Wit(f).
```

The gated SIDE-DOOR residual is:

```text
|delta_B(U) \ Y| <= |delta_M(U) \ X|
```

whenever `|X|>|Y|`.  In the current batteries there are no deficient
right-closed residuals at all:

```text
census N<=10:
  switches=21, Hall pairs=168, deficient=0, fail=0.

H?AFBo][2] all maximum cuts:
  switches=98, Hall pairs=37632, deficient=0, fail=0.
```

So the sharpened proof target is the stronger right-closed Hall statement for
the completed seed+moat switch:

```text
|{f in C : ell(f)<t and Wit(f) subset Y}| <= |Y|
```

for every cutoff `t` and every `Y subset E_<t`.  If a deficient residual ever
appears in a larger battery, the SIDE-DOOR inequality is the backup local
max-cut contradiction.

Claude independently confirmed that the completion moat has size at most one
in the full all-max battery.  Rerunning the side-door gate with `max_add=1`
gives the aligned result:

```text
census N<=10 + H?AFBo][2] all maximum cuts:
  negative vertices=119
  switches=119
  moat-size histogram {0:91, 1:28}
  Hall pairs=37800
  deficient=0
  fail=0
```

The concrete theorem to prove is therefore:

```text
R[v]<0
=> there is an Lmax length-bundle seed A through v and at most one moat vertex z
   such that S=A or A union {z} is neutral, B-connected after flipping,
   terminal-shadow valid, and its witness graph satisfies right-closed Hall.
```

Since every witness length dominates its exit price by definition of
`lambda(e)`, this Hall/SDR theorem plus one strict witness edge gives
`Psi(S)>0` and hence Gamma descent.

The one-moat cases have an even smaller exact signature.  Let `A` be the seed
and `z` the unique moat vertex.  Across the combined `max_add=1` battery:

```text
one-moat switches: 28
delta({z}) = 0
e_M(z,A) = 0
delta(A) = 2 e_B(z,A)
delta(A union {z}) = 0
failures: 0
```

Thus the moat is a zero-loss side-defect vertex whose cut edges into the seed
cancel the positive cut-loss of the seed.  The proof target can be sharpened to:

```text
R[v]<0
=> either an Lmax seed A is already neutral and strict,
   or there is a zero-loss vertex z outside A with e_M(z,A)=0 and
      delta(A)=2e_B(z,A), so S=A union {z} is neutral and strict.
```

The remaining non-computational content is to derive this side-defect vertex
and the right-closed witness Hall property from shortest-geodesic nesting and
max-cut minimality.

The component-boundary identity also survives the completed seed+moat switch.
For each witness component `C0` of the bipartite witness graph, define

```text
Y_C0 = crossing bad edges in C0
X_C0 = boundary exits in C0
U_C0 = union of all terminal prefixes Pref_S(f,e), f in Y_C0, e in X_C0.
```

Exact gate:

```text
census N<=10 + H?AFBo][2] all maximum cuts, max_add=1:
  completed switches=119
  witness components=119
  delta_M(U_C0)=Y_C0 and delta_B(U_C0)=X_C0: 119/119
  failures=0
```

Together with max-cut and neutrality this proves component count balance:

```text
|X_C0| >= |Y_C0|       from max-cut on U_C0
sum |X_C0| = sum |Y_C0| from neutrality of S
=> |X_C0|=|Y_C0| componentwise.
```

The remaining matching content is now purely internal to a balanced terminal
prefix component: prove that no right-closed exit subset can trap more crossing
bad edges than exits.  The SIDE-DOOR hull is the intended local contradiction
if such a trapped subset exists.

## Stronger SDR Gate: Arbitrary Neutral Terminal Shadows

The SDR/Hall phenomenon is not limited to the seed+moat switches in the small
census.  A broader gate enumerates every neutral terminal-shadow-valid switch
on connected-B maximum cuts and tests for a matching saturating boundary exits:

```text
python problems/23/writeup/_codex_terminal_shadow_sdr_gate.py --min-n 5 --max-n 10
```

Result:

```text
N=5  switches=40     fail=0
N=6  switches=52     fail=0
N=7  switches=340    fail=0
N=8  switches=2032   fail=0
N=9  switches=13584  fail=0
N=10 switches=113504 fail=0
total switches=129552
SDR failures=0
```

This suggests a cleaner theorem:

```text
Terminal-Shadow SDR Theorem.
If S is a neutral terminal-shadow switch, then the witness graph
delta_M(S) -- delta_B(S) has a matching saturating delta_B(S).
```

If this theorem is proved, the seed+moat construction only needs to produce a
neutral terminal-shadow switch with one strict witness length.  Hall itself
would be a standalone consequence of shortest-geodesic terminality and max-cut
neutrality.
