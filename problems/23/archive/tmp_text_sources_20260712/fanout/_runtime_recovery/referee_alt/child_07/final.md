Exact fixture result:

For the R29 2943-vertex cage, let \(L_L,L_R\in\{0,\dots,338\}\) count local selector rows and set \(A_s=338-L_s\). The scoped score satisfies

\[
S\ge \Phi(L_L,L_R),
\]

where

\[
\Phi=20411
+2\!\sum_{s=L,R}\!\left(A_s+\max(0,A_s-1)\right)
+200\!\sum_{s=L,R}\!\left\lceil\frac{L_s}{27}\right\rceil
+4\,\mathbf1_{L_L=L_R=0}.
\]

The terms respectively count rigid hub/circuit mass, anchor collision fibres, active D-leaf traffic mass, and cable HitNeed. Exact enumeration of all \(339^2=114{,}921\) count pairs gives

\[
\min\Phi=\Phi(0,0)=23115,
\]

uniquely at \((0,0)\). Choosing anchor rows for all 676 selectors attains this bound. Hence the displayed score-30811 tuple has an exact simultaneous descent

\[
30811-23115=7696.
\]

Thus the 2943 cage is only a strict Hamming-one minimum, not a global minimum.

The single frontier lemma is:

> Every minimal scoped Hall-failing tuple admits trade coordinates \(L_j\), congestion capacities \(c_j\), removable masses \(w_j\), and a jointly selectable rerouting whose score has a lower envelope  
> \[
> C+\sum_j w_j\left\lceil L_j/c_j\right\rceil+\text{anchor penalty},
> \]
> attained at the rerouting and strictly below the original score.

The missing step is deriving these coordinates and disjoint contributions from an arbitrary deficient Hall shore. R29 verifies only the fixture instance \(k=2\), \(c_1=c_2=27\), \(w_1=w_2=200\); therefore no global descent theorem is claimed.

Reproduction used integer arithmetic only:

```text
23115 [(0, 0)] 7696 114921
```

Source hashes:

```text
r29_lead_gate.py
fc2a2840938ac15b15c3ef1c143bd4c74aa2ef8a22fe98db853cb7e813637a59

r29_hamming_gate.py
523a97dcc659750e04d992fb36aa03b4f9549ea49188f8d697ef4556b4d13ae1
```

No production or coordination files were edited. Artifact creation under the requested recovery directory was attempted, but the filesystem rejected file creation there; the launcher can capture this response as `final.md`.