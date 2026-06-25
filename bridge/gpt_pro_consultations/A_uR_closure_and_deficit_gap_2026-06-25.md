# GPT Pro: the u_R LP = exact convex closure of the 8-anchor cut (Step-2 closure mechanism); deficit gap = same wall

chat 6a3b5aba.

## Step-2 closure: the u_R formulation (GPT CONFIRMED "exact convex closure", much stronger than single aggregate sigma-cut)
For each canonical 8-vertex root graph R (410 triangle-free), I(R)={A subset V(R): A independent in R} (profiles;
fresh-vertex neighborhood among anchors must be independent; if 2 fresh adjacent then A cap B = empty). |I(R)|<=256,
<=3281 unordered profile pairs, only self-loop A=B=empty (peel it, add back as forced-monochromatic).
  w_R(A,B;q) = sum_{J in T10} theta_{J,R,A,B} q_J  (linear in q).
  L_{R,c}(q) = sum_{A,B} w_R(A,B;q) 1{c(A)=c(B)}  for a coloring c:I(R)->{0,1}.
  U_8(q) = sum_R min_c L_{R,c}(q).
LP: variables x,q,eta,u_R>=0; constraints E10 (Dq=x)+band+order-9 rows; d_mono <= sum_R u_R (eta <= sum u_R - 2/25);
and u_R <= L_{R,c}(q) for every coloring c. SEPARATION (per-R cutting-plane, the strong part): for current q,
per R compute c*_R = argmin_c L_{R,c}(q) by weighted MaxCut; if u_R > L_{R,c*}(q) add row u_R <= L_{R,c*}(q).
Add ALL violated root rows each round (up to 410) -- separate u_R rows permanently build each root's lower envelope
(one aggregate sigma-cut lets the solution escape; this does not). MaxCut subproblems: drop 0-weight pairs, peel
empty-loop, split into connected -> biconnected blocks, bipartite blocks give 0, solve only non-bipartite. Do NOT
quotient by Aut(R) unless the quotient MaxCut is proved exact. NO THEOREM yet that U_8(q)<=2/25 on the band => the
u_R LP is a DECISIVE EXPERIMENT (closes iff eta<=0).

## VALIDATION already done: U_8(C5-graphon)=0.08=d_mono EXACTLY (tight), U_8(witness)=4.83e-4 (166x). d_mono<=U_8 valid.

## Step-1 DEFICIT GAP (agent-1/GPT-G4): same cut-looseness wall, deficit side. dual_cert_n9 deficit weight 98% on
C5-rooted k=5 cuts; g_r(W)=t_ind(sigma)*(cond deficit), t_ind(C5)~0.0016 => sum lam g_r(W) >= (sum lam t_sigma)(d_mono-2/25),
sum lam t<=1 => does NOT bound d_mono-2/25 when d_mono>2/25; per-flag check passes only bc finite d_mono(H)<=0.0556<2/25;
blind to non-C5 odd cycles (C11: g_C5=0, d_mono>0). Cert NOT a proof (bound true, brute n<=12). GPT deficit-fix
answer PENDING (separate question sent). KEY INSIGHT: the 8-anchor cut U_8 IS a VALID graphon bound (d_mono<=U_8,
validated) -- so if the u_R LP closes (eta<=0), it RIGOROUSLY proves the band bound, fixing BOTH Step-2 closure AND
the Step-1 deficit transfer (replace C5-conditioned deficits with the 8-anchor cut). => implement the u_R LP next.
