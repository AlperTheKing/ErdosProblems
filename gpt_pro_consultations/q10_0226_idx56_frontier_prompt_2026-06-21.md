# GPT Pro consultation: K=2/T=2 q=10 `(0,2,2,6)` exact-state frontier

We are proving the finite theorem `a(30)=36`: no 30-vertex triangle-free
graph has `beta(G) >= 37`.  This is STEP 1 only; do not claim the full
Erdos #23 bridge.

## Exact branch

Exact-codegree-two reroot, `K=2`, `T=2`, `q=10`.

Four-label profile:

```
(c0,c1,c2,c3) = (0,2,2,6)
support = {S1,S2,D}
|A|=6, |B|=10    (manifest idx56)
```

Labels are ordered as:

```
R0,R1 = S1={1}
R2,R3 = S2={2}
R4..R9 = D={1,2}
```

Local domination forces

```
R[S1,S2] = K_{2,2}
D vertices isolated in R
e_R = 4
U = 2 + 2 + 12 = 16
root_edges = 30-q = 20
fixed_edges = root_edges + U + e_R = 40
```

The active exact-state row is:

```
p = e(A,B) = 33
M = e(A∪B,R) = 70
total edges = 40 + p + M = 143
```

This is the smallest hard row after scalar cuts.  The P-free master with
unpaired cuts has an aggregate witness:

```
p=33, e_R=4, M=70, M_A=32, M_B=38, total_edges=143
```

where `M_A=sum_r alpha_r`, `M_B=sum_r beta_r`.

## State model architecture

Each A or B vertex receives an independent R-state `I subset R`.
Since `R[S1,S2]=K2,2`, an independent state cannot contain both S1 and S2.
Every state must satisfy root-colour visibility:

```
I meets U1=S1∪D
I meets U2=S2∪D
```

Thus every legal state contains at least one D vertex.  Legal state count is
441.

The exact count quotient uses integer multiplicities:

```
A_I, B_I >= 0
sum_I A_I = 6
sum_I B_I = 10
sum_I |I|(A_I+B_I) = M
p = sum_{I∩J=empty} A_I B_J
```

It enforces:

- forbidden `|I∩J|=1` for used A/B type pairs;
- opposite-root codegree: every used A-state has at least two disjoint B
  copies, and symmetrically;
- same-side A/A and B/B typewise codegrees;
- A/R, B/R typewise codegrees;
- full R/R codegrees;
- full Psi rooted cuts over all R masks;
- exact-two-root unpaired cuts over all R masks:

```
U1(W): 2+L(W)+alpha(W)+beta(R\W)+e_R(W)+... >=37
U2(W): 2+L(W)+beta(W)+alpha(R\W)+e_R(W)+... >=37
U3(W): p+L(W)+alpha(W)+beta(W)+e_R(W) >=37
```

where for this fixed R, `e_R(W)` is the number of R-edges not crossing W.

Additional scalar prefilter added:

```
alpha(R) >= max(37-2-e_R, 7|A|-p)
beta(R)  >= max(37-2-e_R, 7|B|-p)
```

This closed the rows `(p,M)=(33,66),(33,67),(34,66)`.

## Attempts and failures

Short state-count sweep for idx56:

```
45 tasks total
30/45 INFEASIBLE
15 UNKNOWN at 60s
```

After side-sum prefilter:

```
3 more rows closed immediately
12 rows remain UNKNOWN at 60s
```

The remaining idx56 hard rows include:

```
(p,M) =
(33,68),(33,69),(33,70),
(34,67),(34,68),(34,69),
(35,66),(35,67),(35,68),
(36,66),(36,67),
(37,66)
```

The hardest tested row:

```
mask=0xf, p=33, M=70
```

Results:

```
300s, 64 workers, exact state model + quotient rounds + projection cuts
  + defect-block layer -> UNKNOWN after 322s.

600s, 64 workers, p=33 M=66 before side-sum prefilter -> UNKNOWN after 677s.
```

Projection/defect-block attempts that did not close p33/M66 quickly:

```
--projection-cuts '3;1,2' --defect-block-labels '3'
--projection-cuts '1;2;3;1,2;1,3;2,3' --defect-block-labels '1,2'
```

P-free aggregate master with unpaired cuts is still feasible for idx56:

```
OPTIMAL p=33 eR=4 M=70 MA=32 MB=38 edges=143
```

## Need from GPT Pro

Please find the shortest rigorous next path for this exact branch.  Useful
answers include any of:

1. a P-free scalar/linear cut that eliminates the extremal band above;
2. a structural lemma for `R=K2,2 + 6D`, `|A|=6`, `|B|=10`, `p=33`,
   `M=70`;
3. a stronger exact state-count encoding that avoids 441-state CP-SAT
   hardness;
4. a symmetry reduction or branch decomposition with tiny cases;
5. a falsification: a concrete count/state witness showing the exact local
   model is feasible, and which global beta/rooted-cut condition is missing;
6. the best outer-pattern projected max-flow cut to add first.

Please be precise: state the lemma/cut, prove why it is sound from the listed
assumptions, and give an exact CP-SAT/C++ encoding if computation is needed.

Avoid using rejected terminal-touch equalities or anti-tightness unless you
state the extra closure assumptions explicitly.  The current run has
`--disable-anti-tightness`.
