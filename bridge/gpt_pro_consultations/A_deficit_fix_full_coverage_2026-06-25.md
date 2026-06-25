# GPT Pro: Step-1 deficit gap is REAL; FIX = full type-coverage (balanced multipliers). Same obstruction as Step-2.

chat 6a3b5aba. "Your diagnosis is correct. There is no hidden flag-algebra normalization that removes t_ind(sigma,W)."

## The exact mechanism (confirmed)
g_{k,sigma,r}(W) = E_x[1{x induces sigma}(C_{sigma,r}(x)-c)] = p_{k,sigma}(W)*(E[C|sigma]-c), where C_{sigma,r}(x) =
monochromatic density of the rooted profile-cut (>= d_mono, a real cut). So each atom carries the p_{k,sigma}=t_ind
factor; the cert's 98%-C5 multipliers do NOT bound d_mono-2/25.

## THE FIX (exact normalization condition)
Need lambda_{k,sigma,r} >= 0 with:
  (3)  sum_r lambda_{k,sigma,r} = alpha_k   for EVERY sigma in T_k   (same total weight per type, "balanced/full coverage")
  (4)  sum_k alpha_k = 1.
Then  d-c <= sum_{k,sigma,r} lambda g_{k,sigma,r}(W).  Proof: sum lambda g = sum lambda p (C-d) + (d-c) sum_{k,sigma} p_{k,sigma} sum_r lambda
= [>=0] + (d-c) sum_k alpha_k sum_sigma p_{k,sigma} = [>=0] + (d-c) sum_k alpha_k*1 = [>=0] + (d-c) >= d-c.  (uses sum_sigma p_{k,sigma}=1.)
=> the C5 rule MAY STAY but rules must be supplied for EVERY other 5-root (or 7-root) type with the SAME total weight; their
contributions cannot be omitted. Full coverage is the safe repair (unless a separate audited C5-free triangle-free bound exists).

## Will it recover N<=180? COMPUTATIONAL. GPT: "your earlier full k=7 experiment ... exhaustive separation over all 107
## triangle-free 7-root types reduced the numerical excess to ~1.6e-7. If that used the genuine unconditional functional
## G_P(W)=sum_{sigma in T7} g_{sigma,r(sigma)}(W), then it ALREADY has the correct coverage normalization and is exactly the
## right repair." (1.6e-7 << 6e-5 threshold => closes N<=180.) IMMEDIATE AUDIT: check sum_r lambda_{7,sigma,r} is the SAME
## number for all 107 T7 types (=1 if k=7 only; =alpha_7 if mixed, with sum_k alpha_k=1).

## SAME as Step-2: U_8(W)=sum_{sigma in T8} p_sigma(W) min_r E[C_sigma,r|sigma] (covers every 8-root outcome); for a full
## policy r(sigma): U_{8,r}(W)-c = sum_{sigma in T8} g_{sigma,r(sigma)}(W) >= d-c. The defective Step-1 cert kept mostly the
## sigma=C5 summand and treated it as full coverage. Step-1 (k=7) and Step-2 (k=8) are the SAME full-coverage repair.

## MY NEXT: (Step-1, URGENT) find the full k=7 (107-type) coverage run / cert in repo (excess 1.6e-7?); verify the balance
## audit (sum_r lambda_{7,sigma,r} equal for all 107 types); if it holds, that IS the rigorous repair -> tell agent-1. Else
## RE-DERIVE the contradiction LP with constraints (3)+(4) (balanced full-coverage deficits) and report the new delta.
## (Step-2) the u_R LP = full k=8 coverage closure (separate, harder).
