# GPT (chat 6a3b5aba): LP-dual attack on lemma (16) -- DEEP but NOT CLOSED. (16) is the genuine frontier.

GPT pursued route (1) (exact LP dual) for the congestion lemma (16) and produced a sophisticated structure,
but DID NOT close the proof. Honest verdict: (16) is genuinely hard; the residual obstruction is controlling
the dependence of the chosen minimum signature on the dual toll w (the "signature rotation").

## The LP dual (von Neumann minimax)
Omega = finite set of selectors omega=(S, (C_e)_{e in S}) with C_e∩S={e}; L_omega(a)=|{e in S: a in C_e}|.
   kappa* = max_{w>=0, sum_a w_a=1}  min_{omega in Omega}  sum_a w_a L_omega(a).     (1)
For a fixed min signature S, the C_e are independent over e, so
   min_{(C_e)} sum_a w_a L_omega(a) = sum_{e in S} min_{C odd, C∩S={e}} w(C),   w(C):=sum_{a in C} w_a.
So (16) <=> for every edge-toll w (sum w=1) there is a min signature S with sum_{e in S}(cheapest private-cycle
toll for e) <= n^2/(25t). GPT developed a coarea / half-circle-separator representation on cycle blocks
(place block vertices on a circle at cumulative-toll coords; half-circle H_theta separators; d^C_w(x,y) =
(1/2) measure{theta: H_theta separates x,y}), plus a block-cut regional decomposition with excess functions
exc_S(w) = sum_{uv in S} d_w^{B_S}(u,v) - w(B_S).

## WHY IT DOES NOT CLOSE (GPT's own honest list of dead ends -- all stop at the K23/theta obstruction)
- UNIFORM distribution over min signatures discards the essential dependence of S on the toll w; criticality
  guarantees every edge lies in SOME min signature but gives NO canonical uniform measure on signatures.
- ONE-signature shortest-cycle route stops at theta: the fixed K_{2,3} signature has private-path toll 4/3,
  but ROTATING among signatures lowers the selector value to 6/5. (6/5=1.2 = my numerically-computed kappa*
  for K23-N13 -- exact cross-check; the rotation IS essential and controlling it is the open core.)
- cycle-degree inequality (6) controls sum_{v in C} d_G(v) but NOT arbitrary w (the toll may concentrate on
  6 edges of a K_{2,3} core) -- and it bounds the selector congestion from BELOW, the wrong direction.
- Gamma = sum_{e in S}(d_B(e)+1)^2 <= n^2 would itself prove tau <= n^2/25 DIRECTLY -- an alternative
  sufficient lemma, also unproven (we DID verify Gamma<=N^2 numerically over 119702 graphs N<=11).

## STATUS
Erdos #23 Step-2 is now REDUCED (cleanly, no Guenin/Lehman) to lemma (16) [equivalently per-atom
nu*(K)>=25t^2/n^2, equivalently Gamma<=n^2]. Everything else is PROVED: (T)/(T') verified, block-cut
decomposition, private-cycle selector, square-gluing. (16) is numerically TRUE (kappa*<=n^2/25t, 0 violations,
tight only at C5[n]) but its PROOF is the genuine open frontier -- it requires controlling signature-rotation
/ integrality-gap defects, which a deep GPT-Pro attempt could not close. NOT a closure (all-or-nothing).
