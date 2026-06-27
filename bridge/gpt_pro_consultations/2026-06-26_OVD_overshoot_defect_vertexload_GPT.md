# GPT Pro: the OVD (overshoot-defect) theorem = the right target; reduces to a vertex-load balancing theorem

GPT Pro (Comprehensive), drove browser. Answer to "prove (T1)+(T2)/Overshoot-exchange lemma". CONVERGES with my
exhaustive finding ov(C_min)<=N^2-Gamma (verified N<=11). VERDICT: prove the COMBINED threshold-correct inequality,
NOT T1/T2 separately.

## THE TARGET (= my verified inequality)
   **ov(C_min) <= N^2 - Gamma**   (OVD; equiv. Gamma + ov(C_min)_+ <= N^2).
GPT: "stronger than condition (iii), exactly uses the Gamma>=N^2 hypothesis, explains all sub-tight failures,
equality-sharp on C5[q]. Any proof of T1/T2 that does not first prove a threshold-defect inequality like OVD will
be CIRCULAR, because T1 and T2 are FALSE below threshold." => Gamma>=N^2 => ov(C_min)<=0 => condition (iii).

## RIGOROUS overshoot decomposition (§10, the algebraic spine)
ov(C) = [h^2 + sum_{f in F(C)} ell(f)^2 - Delta(C)] - (2hN - h^2)
      = h(A(C) - 2(N-h)) + H(C) - Delta(C) - R_h(C),  R_h(C)=sum_{F(C)}[h ell + (ell^2-h ell)_+ - ell^2] >= 0.
If every incident edge has ell(f)>=h (true if C chosen with globally MIN ell), R_h=0 and
   ov(C) = h(A(C)-2(N-h)) + H(C) - Delta(C).
On C5[q]: A=2(N-h), H=0, Delta=0 => ov=0.

## REDUCTION to a VERTEX-LOAD balancing theorem (the "missing theorem")
T1 <=> CL: sum_{v in C} p(v) <= 2N, where p(v)=sum_{f ni v} ell(f) (bad-length vertex load); since
sum_{v in C} p(v) = 2h + A(C). Threshold form (CL-defect): Gamma + (sum_{v in C} p(v) - 2N)_+ <= N^2.
Averaging identity: sum_{e in M} h_e P(C_e) = sum_v p(v) T(v),  T(v):=sum_{e: v in C_e} h_e (Gamma-length routed
through v by the chosen shortest cycles). KEY: sum_v T(v) = sum_e h_e |C_e| = sum_e h_e^2 = Gamma. Extremal C5[q]:
T(v)=N for EVERY v. So the hidden theorem =
   **VERTEX-LOAD THEOREM: choose one shortest B-geodesic cycle C_e per bad edge so that T(v) <= N + (N^2-Gamma)
   for every v.**  => LD1: Gamma + (A(C)-2(N-h))_+ <= N^2 => T1 on Gamma>=N^2.
GPT: "exactly the multicommodity/electrical-flow object you have been circling — a vertex-load balancing statement
for shortest odd cycles, NOT a scalar coarea statement."

## T2 corridor form (second-order, §5)
Delta(C) >= sum_{g cap C=empty} ell(g) U_C(g), U_C(g)=max(0, ell_{G-C}(g)-ell_G(g)) (survivor detour). Corridor:
sum_{f long} ell(f)(ell(f)-h) <= sum_g ell(g) U_C(g). Threshold form LD2: Gamma + (H(C)-Delta(C))_+ <= N^2.

## The exchange route (§8-9, the missing final step)
Exchange move: incident witness f=xy (x=v_i in C, y not in C), C_f = shortest cycle of f. Strict decrease
ov(C_f)<ov(C) => C not min. Minimality => ov(C_f)>=ov(C) for all f in F(C). Sum with weights w_f=ell(f)-h
(long) / 1 (anchored). NEEDED (exchange-master-sharp):
   ov(C) + sum_{f in F(C)} lambda_f (ov(C_f)-ov(C)) <= N^2-Gamma,  lambda_f>=0.
Minimality => sum>=0 => ov(C)<=N^2-Gamma. GPT: "I cannot honestly fill in the final exchange-master inequality
without either your incidence traces or a new multicommodity/electrical dual: it is PRECISELY the missing theorem."

## MY NEXT (audit+compute) — provide the incidence/vertex-load traces GPT needs
1. OVD ov(C_min)<=N^2-Gamma: VERIFIED exhaustive N<=11 (0 viol, equality C5[2]). [DONE]
2. Compute T(v)=sum_{e:v in C_e} h_e for chosen shortest cycles; verify VERTEX-LOAD T(v)<=N+(N^2-Gamma);
   check averaging identity sum_v T(v)=Gamma; characterize the tight choice (C5[q]: T(v)=N).
3. Verify the overshoot decomposition ov=h(A-2(N-h))+H-Delta(-R_h) numerically.
4. The flow/routing CHOICE of C_e per bad edge to balance T(v) is the multicommodity object — test if a balanced
   choice always achieves T(v)<=N+(N^2-Gamma).
