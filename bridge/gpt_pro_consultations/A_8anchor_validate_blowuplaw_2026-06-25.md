# GPT Pro: my U_8 degeneracy "validation" was WRONG (used point mass, not the blow-up/i.i.d. law); U_8(witness) IS a violation

chat 6a3b5aba. GPT: "Neither (1) nor (2). The original two-fresh-vertex U_8 is a valid graphon upper bound. Your
C5[2]/C7[2] tests used finite, without-replacement sampling where 8 anchors remove a MACROSCOPIC fraction -- not
the graphon ten-point law." The correct graphon benchmark is the BLOW-UP / i.i.d. law:
  q_J^{W_H} = |V(H)|^{-10} #{phi:[10]->V(H): H^phi ~= J}  (phi NEED NOT be injective; = H[t], t->inf).
My C5[2] used ONLY the count-vector (2,2,2,2,2) (point mass) => 2 non-anchors => bipartite => U_8=0. The real C5
graphon order-10 density is the FULL multinomial over all count-vectors of 10 into 5 parts.

## The bound (GPT's sharpened): d_mono(W) <= 45 * min_sigma F_sigma  (NOT d_mono <= U_8)
Full 10-vertex sampled cost has 45=C(10,2) pairs: root-root 28/45, root-fresh 16/45, fresh-fresh 1/45. The
fresh-fresh-only F_sigma (= my U_8) gives only d_mono(W) <= 45 F_sigma. For the WITNESS: 45*U_8 = 45*4.83e-4 =
0.0217 < m*=0.08 => GENUINE VIOLATION of d_mono <= 45 U_8; and 0.0217 < 2/25 => would CLOSE. GPT: "your pseudo-state
value U_8(q)=4.83e-4 IS a genuine violation of m <= L_sigma*(q) (sigma* fixed from the witness's aggregated profile
MaxCuts). Add it as an order-10 linear cutting plane. USE THE ORIGINAL LEAVE-TWO-OUT; do not move to order 11 yet."

## GPT's 3 checks my buggy validation must avoid: (a) finite graph instead of blow-up/i.i.d. law; (b) root
## canonicalization using A,B or the full 10-vtx graph (must be R ALONE); (c) omitting the probability weight of R.

## MY NEXT: redo validation on the BLOW-UP LAW. Compute U_8 for C5-graphon (10 iid labels from Z5, all
## count-vectors, multinomial) and C7-graphon; check d_mono <= 45*U_8 holds (U_8 >= d_mono/45: C5 0.08/45=0.00178).
## If real graphons satisfy it AND witness 45*U_8=0.0217 < 0.08 => witness separated => add cut d_mono(x) <=
## 45*L_sigma*(q), re-solve order-10 LP, iterate to closure. EXACT rational + all-band-graphon validity before any
## closure claim (all-or-nothing; 10 false closures averted). Canonicalization = R alone (canon_label OK); weight by q_J.
