# GPT Pro Consultation Prompt — 2026-06-21 q10 idx58 MA Branch

Context: Erdős #23 STEP-1 finite theorem `a(30)<=36`. We are proving no
30-vertex triangle-free graph has `beta=e-MaxCut >=37`.

Current exact branch:

```
K=2, T=2, q=10
labels (c0,c1,c2,c3)=(0,2,2,6), support={S1,S2,D}
R[S1,S2]=K_{2,2}; D vertices isolated
U=16, e_R=4, root_edges=20
side idx58: |A|=|B|=8
edge equation: e(G)=40+p+M, so e<=143 gives p+M<=103
```

Verified constraints already in labelled exact A/B verifier:

- every A/B state is an independent R-subset meeting `U1=S1∪D` and `U2=S2∪D`;
- exact A/B law: `ab` edge iff `I_A∩I_B=empty`; intersection size 1 forbidden;
- root-opposite codegree `d_P>=2`;
- A/R, B/R, A/A, B/B, R/R local codegrees;
- exact `p`, exact `M`, optional exact `MA=sum alpha`, `MB=sum beta`;
- full Psi over all R masks;
- exact-two-root unpaired U1/U2/U3 cuts over all R masks;
- split-C static cuts: for every `T⊆D`,
  `8+alpha(S2)+beta(S1)+alpha(T)+beta(D\T)>=37`
  and the symmetric `S1/S2` version;
- sorted labelled A and B state rows for symmetry breaking.

Do NOT use:

- terminal-touch degree equality;
- H14 anti-tightness unless explicitly conditional;
- any q14 reroot closure not stated above.

Current computation:

`idx56 (A,B)=(6,10)` closed 45/45 INFEASIBLE.
`idx57 (A,B)=(7,9)` closed 45/45 INFEASIBLE after split-C + MA branch.

For `idx58 (A,B)=(8,8)`:

Initial labelled split-C batch over 45 `(p,M)` rows:

```
34 INFEASIBLE, 11 UNKNOWN
UNKNOWN rows:
(33,66),(33,67),(33,68),(33,69),(33,70),
(34,66),(34,67),(34,68),(34,69),
(35,67),(35,68)
```

MA-branch tasks for those 11 rows, with `MA+MB=M`, `MA,MB>=31`,
run at 8 jobs x 8 workers, 180s:

```
partial before runner exit:
25 branch rows written
2 INFEASIBLE, 23 UNKNOWN
```

The UNKNOWN band includes many `p=33` branches, e.g. `(p,M,MA,MB)`:

```
(33,66,31,35),(33,66,33,33),(33,66,35,31),
(33,67,31,36),(33,67,32,35),(33,67,33,34),
(33,68,31,37),(33,68,32,36),(33,68,33,35),
(33,68,34,34),(33,68,35,33),(33,68,36,32),
(33,69,31,38)..(33,69,38,31)
```

Question:

Find the next mathematically safe strengthening for exactly this q10 idx58
hard branch. Prefer a fixed-P-free or labelled-state lemma that targets the
remaining `(p,M,MA,MB)` band, not generic advice.

Possible directions:

1. A side-degree/defect law for `|A|=|B|=8`, `p=33..35`, `M=66..70`.
2. A stronger family of split-root/C cuts beyond the current split-C cuts.
3. A projected max-flow/min-cut block small enough to encode before finding a
   feasible CP-SAT candidate.
4. A small branch on D-column loads or state sizes that should close the band.
5. A hand contradiction if one exists.

Please give:

- lemma statement;
- proof from the listed constraints only;
- exact CP-SAT/count constraints or branch manifest;
- what artifact/result would certify closure.
