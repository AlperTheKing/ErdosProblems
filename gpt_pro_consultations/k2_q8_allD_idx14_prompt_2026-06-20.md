# GPT Pro Consultation Prompt: K2 q=8 all-D hard branch

We are proving the finite theorem `a(30)=36`: no triangle-free graph on 30
vertices has `beta(G)=e(G)-MaxCut(G) >= 37`.  This is Step 1 only, not the full
Erdos #23 bridge.

## Current safe reduction

We are in the exact-codegree-two rerooted `K=2,T=2` model.  We do **not** use
terminal-touch equalities or the H14 anti-tightness rule; anti-tightness is
disabled because q14/t2 has not yet been reclosed independently through the
cap-143 edge window.

Current branch:

```
q = 8
labels on R: all D = {1,2}
(c0,c1,c2,c3) = (0,0,0,8)
|A| = 7
|B| = 11
R-skeleton: empty
U = 16
root_edges = 22
eR = 0
edge window: 112 <= 22 + U + p + M <= 143
so 74 <= p + M <= 105
```

Every `r in R` is a doubleton label, so `deg(r)=2+m_r >= 8`, hence `m_r>=6`.
Therefore `M=sum_r m_r >= 48`.  Root-opposite codegree gives
`p >= 2*max(|A|,|B|)=22`.  The task grid is:

```
p = 22..57
M = max(48, 74-p)..105-p
656 (p,M) rows total
```

## Exact state-count quotient currently used

For a fixed R-skeleton, an A-state or B-state is a subset `I subset R`.
Since R is empty, every subset of the 8 R-vertices is independent.  Counts
`A_I,B_I` satisfy `sum A_I=7`, `sum B_I=11`.

The verifier imposes typewise:

1. exact `M = sum_r m_r`, where `m_r=sum_{I contains r}(A_I+B_I)`;
2. exact `p = sum_{I cap J = empty} A_I B_J`;
3. A/B law: `|I cap J|=1` forbidden for used cross state pairs; if disjoint
   then the whole state-class pair is an A-B edge, if intersection >=2 it is
   an A-B nonedge with enough R common neighbours;
4. every used A-state has at least two disjoint B-states in total
   (`d_P(a)>=2`), and symmetrically every used B-state has `d_P(b)>=2`;
5. A/R and B/R nonedge-codegree constraints per used state type;
6. A/A and B/B nonedge-codegree constraints per used pair of state types;
7. R/R constraints are automatic here because every pair of R vertices has
   label overlap 2;
8. rooted/Psi cut constraints and a lazy weighted quotient-cut separator
   (`quotient-cut-rounds=3` in the current runs).

No fixed A-B template is enumerated; the quotient is exact for the labelled
A/B-state model once all typewise constraints and cuts are present.

## What closed already

The same verifier closed:

```
q=6 all-D, all side choices: 5200/5200 INFEASIBLE
q=7 all-D, all side choices: 3392/3392 INFEASIBLE
q=7 E+D, all side choices: 19520/19520 INFEASIBLE
q=8 all-D, side (|A|,|B|)=(6,12): 592/592 INFEASIBLE
```

## Current failure

For q=8 all-D, side `(7,11)`, first generic run:

```
8 jobs * 8 workers, 60s task timeout:
51 rows written: 37 INFEASIBLE, 14 UNKNOWN, 0 FEASIBLE
UNKNOWN rows all p=22, M=70..83
```

Stronger rerun:

```
2 jobs * 32 workers, 300s task timeout:
29 more rows closed, all INFEASIBLE; then the run stalled on p=22,M=82.
It was stopped to avoid unproductive compute.
```

Trusted union status:

```
48 rows closed INFEASIBLE
608 rows remaining
0 FEASIBLE
```

Remaining rows by p:

```
p=22: M=81..83                 (3 rows)
p=23: M=70..82                 (13 rows)
p=24: M=50..81                 (32 rows)
p=25: M=49..80                 (32 rows)
p=26: M=48..79                 (32 rows)
p=27: M=48..78                 (31 rows)
...
p=57: M=48                     (1 row)
```

The smallest obstruction is therefore the very low-p/high-M band, especially
`p=22,M=81..83` and `p=23,M=70..82`.

## Ask

Please find the shortest rigorous next path for this exact branch.  I need
concrete, checkable suggestions, not broad advice.

Useful outputs would be one or more of:

1. a scalar contradiction for all or part of q=8 all-D `(A,B)=(7,11)`;
2. a P-free inequality/cut in state-count variables that attacks low `p`,
   high `M`;
3. a stronger exact quotient-cut family or separation target that is likely
   to kill the p=22/23 bands;
4. a symmetry/excess branching scheme that reduces the remaining rows to a
   small certificate;
5. a falsification attempt: a count-level feasible pattern for e.g.
   `(p,M)=(22,82)` showing which current constraint is still missing;
6. a fixed-P or labelled-state encoding that is much smaller than the current
   generic count solver for this all-D branch.

Important: do not use terminal-touch equality, terminal-degree equality, or
H14 anti-tightness.  They are currently rejected/disabled.  Anything proposed
must follow from triangle-freeness, minimum nonedge-codegree 2, beta>=37 cut
constraints, the exact K2 q=8 all-D model above, and ordinary degree lower
bound `deg>=8`.

