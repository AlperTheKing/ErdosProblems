# C61: exact Boolean falsification lane for SCB

## Verdict

No Boolean counterexample to

\[
H_T(X)\le Q_T(X) \tag{SCB}
\]

was found at any tested cutoff.  CP-SAT returned exact `INFEASIBLE` with
zero branches and zero conflicts at

\[
X\in\{125004,200000,250004,333344,500000,750006,999984,1000000\}.
\]

The cutoffs other than `200000`, `500000`, and `1000000` are hard-shaped
event cutoffs selected near irregular round targets.  This is a finite
negative search, not a proof for arbitrary `X`.

The continuous relaxation, which is stronger than the Boolean statement,
has separately replayed integer dual certificates at `X=200000` and
`X=1000000`.  Their exact margins are respectively `3030` and `19066`.
The `X=1000000` certificate is therefore a compact finite mathematical proof
that no Boolean counterexample exists at that cutoff; it does not rely on the
CP-SAT verdict.

## Exact Boolean reduction

For allowed `m>2`, the distinct factorization

\[
2m=(2)m
\]

gives the closure implication

\[
t_m\le t_{2m-1}. \tag{1}
\]

The seeds give the same inequality at `m=2`.  Consequently the boundary
indicator is not an auxiliary product:

\[
q_{2m-1}=t_{2m-1}-t_m\in\{0,1\}. \tag{2}
\]

Thus a Boolean falsifier is exactly a solution of the Horn closure clauses

\[
t_a+t_b-t_{ab-1}\le1 \qquad(a<b) \tag{3}
\]

with the seed and splitless fixed values, together with

\[
|\mathcal H_X|-\sum_{h\in\mathcal H_X}t_h
-\sum_{2m-1\le X}(t_{2m-1}-t_m)\ge1. \tag{4}
\]

`C61_scb_boolean.py` submits only Boolean/integer constraints (3)-(4) to
OR-Tools CP-SAT.  A returned witness would be checked from the original set
definitions by the separate script `C61_scb_verify.py`.

## Chain telescope lemma

The directed graph with edges `m -> 2m-1` is a disjoint union of chains,
each rooted at an even integer.  Equation (1) says that membership along a
chain is a suffix: zeros followed by ones.  Therefore each chain contributes
at most one boundary to `Q_T`.

Let `U_T(X)` be the number of hard-rooted chains which are entirely outside
`T` through `X`, and let `V_T(X)` be the number of non-hard-rooted chains
which change from outside to inside `T`.  Then the exact identity is

\[
\boxed{H_T(X)-Q_T(X)=U_T(X)-V_T(X).} \tag{5}
\]

Indeed, a missing hard root contributes `1` to `H`.  If its chain later
enters `T`, the unique transition contributes the cancelling `1` to `Q`;
otherwise it contributes to `U`.  A transition on a non-hard-rooted chain
contributes only the negative `Q` term and is counted by `V`.

This removes all boundary-product variables and gives a necessary structural
condition for a counterexample:

\[
U_T(X)\ge V_T(X)+1. \tag{6}
\]

## First-failure constraint

Define

\[
F(X)=\max_T\bigl(H_T(X)-Q_T(X)\bigr)
\]

over the C61 class.  If `X` is not hard-shaped, restriction of any feasible
`T` at `X` to `[2,X-1]` preserves all hypotheses, leaves `H` unchanged, and
can only delete a boundary.  Hence

\[
X\notin\mathcal H\quad\Longrightarrow\quad F(X)\le F(X-1). \tag{7}
\]

At a hard-shaped cutoff, restriction deletes at most the one new hard hole,
so

\[
F(X)\le F(X-1)+1. \tag{8}
\]

It follows that a minimal failing cutoff must be hard-shaped.  Every witness
at such a first cutoff has `X` outside `T`, and its restriction at `X-1` is
tight:

\[
H_{T\cap[2,X-1]}(X-1)=Q_{T\cap[2,X-1]}(X-1). \tag{9}
\]

Thus future exact searches need inspect only hard event cutoffs and may start
from tight predecessor states, rather than arbitrary forward-closed sets.

## Search statistics

| `X` | Boolean vars | closure pairs | hard | result | branches |
|---:|---:|---:|---:|:---|---:|
| 125004 | 68575 | 289748 | 13020 | UNSAT | 0 |
| 200000 | 110180 | 484482 | 21294 | UNSAT | 0 |
| 250004 | 138000 | 618056 | 26890 | UNSAT | 0 |
| 333344 | 184444 | 845422 | 36294 | UNSAT | 0 |
| 500000 | 277570 | 1313166 | 55350 | UNSAT | 0 |
| 750006 | 417641 | 2037450 | 84307 | UNSAT | 0 |
| 999984 | 558005 | 2780465 | 113570 | UNSAT | 0 |
| 1000000 | 558013 | 2780532 | 113571 | UNSAT | 0 |

All runs used 16 workers, below the 64-worker project limit.  `UNSAT` means
CP-SAT status `INFEASIBLE`, not a floating objective comparison.

## Independent exact dual replay

After eliminating `q` by (2), minimize

\[
\sum_{h\in\mathcal H_X}t_h+
\sum_{2m-1\le X}(t_{2m-1}-t_m) \tag{10}
\]

over the continuous box and (3).  A lower bound by `|H_X|` proves SCB for
all Boolean points.  HiGHS is used only to discover multipliers.
`C61_scb_verify.py`, run under `python -O`, independently reconstructs the
number-theoretic model and checks with Python integers:

1. every listed closure factorization;
2. every multiplier sign and duplicate key;
3. every stationarity coordinate;
4. the dual objective and all model counts.

| `X` | hard | exact dual objective | exact margin | nonzero closure rows |
|---:|---:|---:|---:|---:|
| 200000 | 21294 | 24324 | 3030 | 63841 |
| 1000000 | 113571 | 132637 | 19066 | 325361 |

The reduced formulation was also cross-checked against C56 at
`X=54,1000,100000`; it reproduced exact margins `0,3,1301`.

## Reproduction

~~~powershell
python problems/424/compute/wave5/C61_scb_boolean.py `
  --limits 200000 500000 1000000 --workers 16 --seconds 600 `
  --output problems/424/compute/wave5/C61_boolean_large.json

python problems/424/compute/wave5/C61_scb_dual.py `
  --limits 1000000 `
  --output problems/424/compute/wave5/C61_dual_1m.json `
  --summary problems/424/compute/wave5/C61_dual_1m_replay.json

python -O problems/424/compute/wave5/C61_scb_verify.py `
  --certificate problems/424/compute/wave5/C61_dual_1m.json
~~~

## SHA-256

~~~text
C61_scb_boolean.py
C633D920B860FCAA65296AD43D8A1DBC3B0CC63A80835315B15804E6690376B8

C61_scb_dual.py
BA8FBCB71D53B68F3453C75140902728AC209D359E5DE6364752A62320EEEC67

C61_scb_verify.py
C2BF16FDDFF4553CBB2A74F5B91AE56ED5ED3D4C1C994C6A87B736FF09DF4388

C61_boolean_large.json
5839DE2104BF5003AFB53A8E735386332D65A1DF96FB9F21A18009B1FE782527

C61_boolean_irregular.json
C41857149B768AC9B15FD40BC9AA9FEEFD69F9EB06E3E8BA9A26FC6C70C05AA4

C61_dual_1m.json
32A9CBEBD500C1ABE7AEC868687742551DCC97C949C0767788F814D868E62878

C61_dual_1m_replay.json
F12E5518B9FC368F9361CCAADDADBD59B044A56AC585080B93B424C46D4FAAAB
~~~

## Scope

C61 supplies no asymptotic proof.  It falsifies SCB counterexamples at eight
new cutoffs, gives independently checkable finite UNSAT certificates at two
new cutoffs, and reduces any first failure to the hard-event/tight-predecessor
configuration (9).  Arbitrary-`X` control remains open.
