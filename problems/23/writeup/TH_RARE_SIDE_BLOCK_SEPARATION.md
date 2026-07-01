# TH-Rare Side-Block Separation Atom

This note isolates the remaining row-side proof obligation after the
no-two-hole gates.

## Verified Scope

The component-local row theorem is:

```text
After the stage-0 rare-cost matching, in every residual connected component
(A,B), every f in A misses at most one exit in B.
```

Exact support:

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182, status={'ok':182}, row_miss={0:989,1:72}
```

Tie robustness:

```text
python problems/23/writeup/_codex_stage0_all_min_rowmiss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119, status={'ok':119}
```

The stronger global statement is false:

```text
python problems/23/writeup/_codex_stage0_all_min_e0miss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

has `e0_miss=3`. Thus one row can miss several unmatched minimum exits
globally; those exits must lie in different residual components.  Component
separation is essential.

## Objects

Let `S` be a completed terminal-shadow switch.  Let

```text
C = delta_M(S),       E = delta_B(S)
```

and `Wit(f)` be the exits witnessed by the crossing bad edge `f`.

Let

```text
L0 = min_{f in C} ell(f)
F0 = {f in C : ell(f)=L0}
F1 = C \ F0
lambda(e) = min{ell(f): f witnesses e}
E0 = {e in E : lambda(e)=L0}.
```

Stage 0 chooses a matching

```text
mu : F0 -> E0
```

minimizing

```text
sum_{h in F0} c(mu(h)),      c(e)=|Wit(e) cap F1|.
```

Then the residual graph is the bipartite graph between `F1` and
`E \ mu(F0)`.

## Flat Alternating Closure

For an unmatched `e in E0`, let `Alt_mu(e)` be the alternating closure in the
`F0-E0` witness graph:

```text
e -> h       if h in F0 witnesses e,
h -> mu(h)  for matched h.
```

If some matched `u in Alt_mu(e) cap mu(F0)` has `c(u)>c(e)`, then replacing
along the alternating path decreases the rare cost, contradicting stage-0
minimality.  The hard case is therefore the flat case:

```text
c(u) <= c(e) for every matched u in Alt_mu(e).
```

The proposed structural conclusion is:

```text
FlatClosure(e) is a terminal side block.
```

Meaning:

1. Every `F1` row that misses an exit of the closure has the same terminal
   side relative to `S`.
2. Any residual co-witness path leaving the closure must pass through an exit
   matched by `mu` at the same rare cost; after deleting `mu(F0)`, that path
   is broken.
3. If a row of another flat closure enters and leaves this block, then the
   first-split/last-rejoin theta gives either an intermediate terminal door or
   a shorter `B`-geodesic.  This is the same S2 theta exclusion used in the
   cap-side proof.

## Lemma Target

### TH-Rare Side-Block Separation

Let `(A,B)` be a residual connected component.  Suppose `f in A` misses two
minimum exits `e0,ek in B cap E0`.  Choose the shortest exit co-witness
corridor

```text
e0, g1, e1, ..., gk, ek
```

whose internal exits are witnessed by `f`.

Then at least one endpoint has a strict rare-cost exchange:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e) cap mu(F0)
with c(u)>c(e),
```

or, more generally, there is a multi-exchange replacing unmatched exits `Z`
by matched exits `U` with

```text
|Z|=|U|,     sum_{z in Z} c(z) < sum_{u in U} c(u).
```

Equivalently, if both endpoints are cost-flat, their flat closures cannot be
in the same residual component.

Claude's 2026-06-30T22:06:30Z classification sharpens the same statement to
the following exact separation form:

```text
Mu-Separation Form.
Let e,e' in E0 be minimum-tier exits missed by the same F1 row f.  If e and
e' are both cost-flat, then every exit co-witness path from e to e' in the
full F1-vs-E graph passes through an exit in mu(F0).  Therefore e and e' are
in different residual components after deleting mu(F0).
```

Equivalently:

```text
There is no residual co-witness path between two cost-flat minimum side
blocks missed by the same row.
```

This is the precise remaining proof burden.  It is not a consequence of
stage-0 min-cost alone; it must use terminal 5/7 geometry.

Exact gate for this precise form:

```text
python problems/23/writeup/_codex_mu_separation_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119, status={'ok':119}, VERDICT=PASS
```

With inherited stress:

```text
python problems/23/writeup/_codex_mu_separation_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182, status={'ok':139,'too_many':43}, fail=0
```

The gate scopes to the residual component of the row `f`.  A broader version
that grouped exits without requiring `f` to lie in the same component failed
on inherited H3, which is exactly the global/component distinction.

## Proof Skeleton

The proof should use the already-isolated 5/7 theta for singleton residual
misses.

For every singleton minimum miss `(f,e)`, the REX gate verifies:

```text
ell(f)=7,
there is g in F0 with ell(g)=5,
and some Q in cyc[g] is a contiguous 5-vertex subpath of some P in cyc[f].
```

Thus each minimum miss supplies a terminal annulus of length two around a
length-5 row.

Now assume a minimal two-hole corridor with both endpoints in `E0`.

1. Apply the singleton 5/7 description to `(f,e0)` and `(f,ek)`.
   Each endpoint gives a length-5 `F0` row embedded in a length-7 row of `f`.

2. If the two terminal annuli cross or one closure re-enters the other, the
   first split and last rejoin form a reduced blue theta.  By the S2
   shortest-row splice principle, one diagonal is a `B`-path shorter by at
   least two edges for `f` or for one of the `F0` rows; the length-2
   degeneracy is a triangle.  This is impossible.

3. If the annuli are disjoint, each endpoint lies in a flat terminal side
   block.  A residual co-witness corridor from one endpoint block to the
   other must cross the matched `F0-E0` exits that separate those blocks:

   ```text
   every full co-witness path from e0 to ek uses some exit in mu(F0).
   ```

   Since matched exits are deleted from the residual graph, the corridor
   cannot exist.  This is the `mu(F0)`-separation form above.

4. Therefore two cost-flat minimum closures cannot be in one residual
   component.  Any genuine two-hole minimum corridor must have a strict
   rare-cost exchange, contradicting the stage-0 matching.

## Exact Falsifier Shape

A falsifier must provide:

```text
S, mu, residual component (A,B), f in A,
two exits e0,ek in B cap E0 missed by f,
no matched exit of larger c in either Alt_mu(e0) or Alt_mu(ek),
and a residual co-witness corridor joining e0 to ek.
```

Additionally it must avoid the S2 theta certificate:

```text
no triangle,
no B-path shorter by >=2 for any involved bad edge,
no intermediate terminal door.
```

No such object appears in the current census/H2/H3/H4 gates.

The inherited H3 examples show why the statement must be component-local:
one F1 row can miss several unmatched `E0` exits globally, but those exits
are separated by matched `E0` exits and land in different residual
components.

## TH-Corridor Formulation

The same atom can be stated without referring first to flat closures.  For an
exit `e=x_e y_e`, with `x_e in S` and `y_e notin S`, and a crossing bad edge
`f=tau_f sigma_f`, with `tau_f in S`, set

```text
D_f = ell(f)-1 = d_B(tau_f,sigma_f)
```

and define the terminal slack

```text
s_f(e) =
d_{B[S]}(tau_f,x_e) + 1 + d_{B[V\S]}(y_e,sigma_f) - D_f.
```

Terminal-shadow validity says

```text
f witnesses e  <=>  s_f(e)=0.
```

Since the blue graph is bipartite, every nonzero slack is at least `2`.

For a residual component `(A,B)`, build the exit co-witness graph `J(A,B)` on
the residual exits `B`:

```text
e ~_J e'  <=>  exists g in A witnessing both e and e'.
```

If a row `f in A` misses two exits in this component, choose a shortest
`J(A,B)` path

```text
e0, e1, ..., ek
```

between missed exits.  Minimality of this path gives

```text
s_f(e0)>0,  s_f(ek)>0,  s_f(ei)=0 for 1<=i<=k-1.
```

Choose hinges `g_i in A` witnessing `e_{i-1}` and `e_i`.  This is the minimal
two-hole residual corridor.  The row-side theorem follows from excluding all
such corridors.

### TH-Corridor Gate

For every residual component `(A,B)`, every `f in A`, and every shortest
two-hole exit co-witness corridor

```text
e0, g1, e1, ..., gk, ek
```

one of the following certificates must exist.

1. Long-lambda lens certificate.  If `lambda(e0)>L0` or `lambda(ek)>L0`, then
   the row-union disk contains a triangle or a blue path for some
   `h in {f,g1,...,gk}` of length at most `ell(h)-3`.  This is the row-side
   version of the S2 first-split/last-rejoin theta.

2. Minimum-lambda rare exchange.  If `lambda(e0)=lambda(ek)=L0`, then the
   stage-0 alternating graph contains a negative rare-cost exchange:

```text
|Z|=|U|,   sum_{z in Z} deg_F1(z) < sum_{u in U} deg_F1(u),
```

   replacing unmatched minimum exits `Z` by matched exits `U`.  The singleton
   version is a reachable matched exit `u in Alt_mu(e)` with
   `deg_F1(u)>deg_F1(e)`.

Current exact gate:

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1

tested=182, status={'ok':182}, row_miss={0:989,1:72}
```

Thus no actual double-miss corridor appears in the verified domain.  The proof
obligation is to show that any hypothetical one must fall into branch 1 or
branch 2 above.  Branch 1 is Atom A/EHR, already reduced to S2.  Branch 2 is
the same TH-rare side-block separation: two cost-flat minimum side blocks for
one row cannot remain in one residual component after deleting `mu(F0)`.

## 2026-06-30 Claude / GPT-Pro Classification

Claude's 2026-06-30T22:33Z reply classifies the Atom B proof skeleton as
complete, subject to auditing the S1/S2 theta hypotheses.

The proof decomposition is:

1. Alternating closure.  For an unmatched minimum exit `e`, the stage-0
   alternating closure `A(e)` consists of paths

```text
e -> F0 row -> matched E0 exit -> ...
```

   Toggling an alternating path from `e` to a matched exit `u` changes the
   stage rare cost by `c(e)-c(u)`.  Stage-0 optimality therefore forbids a
   reachable matched `u` with `c(u)>c(e)`.

2. Rare monotonicity (RM).  Along a reduced row-side corridor, an `F1` row
   witnessing the farther exit `b` but not the nearer exit `a` contributes to
   `Wit_F1(b)\setminus Wit_F1(a)`.  Thus the rare cost increases inward:

```text
c(b)>c(a).
```

   The claimed proof is the same first-split/last-rejoin S2 theta as Atom A
   and the cap-side endpoint-hinge rigidity.

3. Shadow separation.  Each cost-flat minimum miss has a residual shadow
   closed under cost-flat reachability.  If two minimum misses for one row lie
   in one residual component, their closed shadows cannot be disjoint without
   a residual co-witness path crossing `mu(F0)`.  If the shadows interact,
   the first interaction plus RM gives a reachable matched exit of larger
   rare cost, contradicting stage-0 optimality.

Therefore the row-side no-two-hole theorem is reduced to the S1/S2 theta
package:

```text
Atom A / TH-long = endpoint hinge rigidity = S2.
Atom B / TH-rare = rare monotonicity + shadow separation = S2 + stage0 min-cost.
```

Remaining audit before proof-complete status:

```text
Check every RM and EHR application satisfies the reduced-hinge hypotheses of
S2: terminal-prefix rows, no re-entry, shortest co-witness corridor, and no
intermediate terminal door already present.
```
