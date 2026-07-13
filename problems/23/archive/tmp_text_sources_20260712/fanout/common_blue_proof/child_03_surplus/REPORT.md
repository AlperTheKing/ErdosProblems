# Corrected two-edge-surplus audit

For finite owner-labelled valid terminals `Q`, require pair freeness and project to the set `P` of distinct ordered pairs. Let `r(x,y)=1` iff `activeGraph.Adj x y` and `ActiveOwner x`, else zero. Exactly:

```
|K(Q)| = sum_{p in P} (2-r(p)), hence |P| <= |K(Q)| <= 2|P|. (E)
|(O union K(Q))|-|O| = |K(Q) \ O|.                         (N)
```

Both are sharp. Surplus `dB-dM-2 >= 0` proves eligibility, not cardinality. The strongest Hall identity is `|N_ext(A)|=|N_old(A)|+|K_A\N_old(A)|`; a separate theorem must lower-bound the difference.

Audit: keys forget owner, so owner-terminal multiplicity cannot be counted. `TerminalData.Valid` omits pair freeness. Common-blue is its own eligibility disjunct: it requires neither `EligibleOwner`, selected-row companion support, nor owner/source component confinement. Validity and freeness are half-independent; reservation deletes only half zero. Ordered orientations are distinct and must not be normalized.

Realizable counterexample: for `k>=2`, use bipartite `K_(2,k)` with left `x,y`, right owners `v_i`, all edges blue under the bipartition maximum cut, and empty bad-edge DB (complete vacuously). It is triangle-free and blue-connected; all `k` records `(v_i,x,y)` are valid because `dB=2k,dM=0`, but only `(x,y,0),(x,y,1)` exist. Active demand is empty, so this falsifies terminal-to-key counting, not Hall.

R29: 2,824 owner-terminal half instances collapse to 216 new keys. Its minimum absorber has 28 distinct `(x,2930,h)` for `29<=x<=42`, both halves, free, unreserved, absent from the old 19,925, each adjusted surplus 1. Formula (N) gives gain 28, closing defect 28; this is fixture-specific.

Remaining lemma for every owner shore `U`:

```
|{surviving FreeHalf keys common-blue for some v in U} \ N_old(U)|
  >= demand(U)-|N_old(U)|.
```

Two-edge surplus proves membership only; it supplies no charging injection.