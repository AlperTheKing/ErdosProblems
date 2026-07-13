# R57 sharp boundary-correction target

## Exact decomposition

Give every blue edge weight +1 and every bad edge weight -1. Let W be an induced branch window and let X,Y be subsets of W. Put A=X\Y and C=Y\X. Write lambda for signed cut loss and mu for signed weight between A and C. Define

```
beta_W(S) = signed weight of E(S, V(G)\W).
```

Since A,C are contained in W, the opposite-corner term has no outside-W contribution. Therefore

```
lambda_G(X)+lambda_G(Y)-2*mu_G(A,C)
 = [lambda_G[W](X)+lambda_G[W](Y)-2*mu_G[W](A,C)]
   + beta_W(X)+beta_W(Y).
```

If the local catalogue margin is m_W(X,Y), strict full-graph overweight is equivalent, over integer weights, to

```
beta_W(X)+beta_W(Y) <= -m_W(X,Y)-1.
```

For every sharp catalogue entry with local margin -1, the missing condition is exactly

```
beta_W(X)+beta_W(Y) <= 0.
```

Writing I=X intersect Y gives the explicit correction

```
beta_W(X)+beta_W(Y)
 = 2*w(E(I,V\W)) + w(E(X symmetric_difference Y,V\W)).
```

Thus an external blue leaf at a symmetric-difference vertex raises the margin by one, and an external blue leaf at an intersection vertex raises it by two. This is sharp and explains the 16-vertex R57 interface counterexample.

## Interface audit

The compiled `CheckedSameAtomExclusiveFork` records only the two checked rows, first-divergence data, and common-blue predecessor edges. `GlobalSoftCapTrace.Payload` adds an abstract eligibility relation, an optimal grouped partial flow, lex minimality, and an unmatched root. `BothHalvesUsed` only supplies two distinct matched demands. None of these fields quantifies over external branch-window boundary edges.

The exact compiled decomposition in `SelectedSupportBoundaryExposure.dB_eq_support_add_exposure` is

```
dB = supportBoundary + activeBoundary + outsideBlueBoundary.
```

The omitted term is `outsideBlueBoundary`. A non-circular repair must derive the displayed signed boundary inequality from concrete residual-core closure and actual six-family eligibility. Adding the inequality as a field is circular, since `GraphDataSignedCut.not_overweight_of_isMaxCut` proves that no full-graph strict overweight pair exists under a maximum cut.

## Final decision gate

Either prove a real graph theorem mapping saturated P1 sources on the residual unit core injectively to enough bad external boundary to make the correction nonpositive, or construct a full positive-unit-defect saturated rotor countermodel. Without one of those outcomes, R54-R57 does not close Erdős #23.