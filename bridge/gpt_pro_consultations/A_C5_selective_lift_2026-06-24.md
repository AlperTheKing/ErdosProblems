# GPT Pro: take (a) via a SELECTIVE (9->10) marginal lift for the single missing C5 diagonal

chat 6a3b5aba. Decision at the kill-criterion fork: NOT a full order-10 SDP (expensive), NOT (b) (no concrete
band inequality), but a CHEAP selective 9->10 marginal lift testing exactly the first untested identity
t(C5 join C5) = t(C5)^2 (the only multiplicativity identity NOT visible on <=9 vertices). LP-sized: ~12,172
triangle-free 10-vertex graphs (OEIS A006785), ~12k nonneg scalars + <=121,720 sparse incidences, NO new PSD blocks.

## The lift
- Order-9 vars x_H = p_ind(H,W), H in T_9 (1897). Add extension vars q_J = p_ind(J,W), J in T_10 (12172).
- Vertex-deletion marginal D_{H,J} = (1/10)|{v in V(J): J-v ~= H}|.
- (E10) projective consistency:  q_J>=0,  sum_J q_J = 1,  x_H = sum_J D_{H,J} q_J.  (<=10 nonzeros per column.)
- c = p_ind(C5,W) = sum_H p_ind(C5,H) x_H.
- gamma_J = |{A subset V(J): |A|=5, J[A]~=C5, J[V\A]~=C5}| / C(10,5).  z = sum_J gamma_J q_J.
- For a genuine graphon the first 5 and last 5 independent vertices induce C5 independently => z = c^2 (C5-DIAGONAL).
  Uses the TRUE 10-point induced distribution; NO within-sample variance (unlike the unsound naive square).
- On branch c in [a,b]: convex envelope (SQ): z >= 2ac-a^2, z >= 2bc-b^2, z <= (a+b)c-ab. Max gap (b-a)^2/4.

## DIAGNOSTIC FIRST (before any SDP rerun): does the edge-pinned optimizer x* survive?
Freeze x*, c* = sum_H p(C5,H) x*_H. Solve two sparse LPs:
  z_min(x*) = min{ gamma^T q : D q = x*, q>=0 },   z_max(x*) = max{ gamma^T q : D q = x*, q>=0 }.
Compare (c*)^2 with [z_min, z_max].
- If (c*)^2 NOT in [z_min,z_max]: x* has NO 10-extension satisfying the C5 diagonal => selective order-10 route
  VALIDATED. Extract the linear cut and iterate.
- If (c*)^2 in [z_min,z_max]: x* SURVIVES the full 10-vertex lift + the missing diagonal => STOP, move to (c),
  record the medium band as the sharply isolated open wall. (GPT's firm stopping rule.)

## Extracting a machine-verifiable order-9 cut (if (c*)^2 > z_max)
Dual of z_max LP gives rational lambda_H with D^T lambda >= gamma, hence for every graphon z <= sum_H lambda_H x_H.
Since z = c^2 >= 2rc - r^2 for every rational r (tangent), the valid LINEAR ORDER-9 inequality is:
  (C5-pair cut)   2r p_ind(C5,W) - r^2 <= sum_H lambda_H p_ind(H,W),   r ~ rational approx to c*.
Insert into the existing order-9 solver; no order-10 vars in the final certificate. Iterate:
  x* -> 10-extension LP -> dual C5-pair cut -> new order-9 optimum.
Final cuts verified using only: (1) finite rational D^T lambda >= gamma; (2) tangent 2rc-r^2 <= c^2; (3) exact
order-9 induced densities.

## NEXT (mine): run the DIAGNOSTIC. Build T_10, D, gamma, p_ind(C5,.); get x*; solve z_min/z_max; compare (c*)^2.
## Decisive either way. Per [[gpt-pro-decides-path]]. Any closure still needs the exact Fraction cert (6 averted).
