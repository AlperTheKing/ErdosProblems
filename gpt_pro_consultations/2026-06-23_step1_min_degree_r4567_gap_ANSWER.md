# GPT Pro Answer — Step-1 a(30)<=36, closing min-degree r=4,5,6,7 (delta>=8)

Source: ChatGPT Pro (Kapsamlı Pro / Extended), fresh chat "Erdos Problem 23 Proof"
https://chatgpt.com/c/6a3aaf8e-1140-83eb-bd9b-7c7b2967afa2 — last assistant msg
(9887 chars), read in full via the fixed slice-reader. ~22 min reasoning.
Prompt: 2026-06-23_step1_min_degree_r4567_gap_prompt.md. **NOT audited yet** — see
CRITICAL ASSUMPTION below; audit before integrating (GOAL rule; 3 prior false closures).

## VERDICT
- **r<=3 step CONFIRMED correct** (MaxCut(G) >= MaxCut(G-v) + ceil(r/2) => beta(G) <= beta(G-v)+floor(r/2)).
- The r0 in {8,9} enumeration does **NOT yet prove a(30)<=36** (gap confirmed).
- **r=4 and r=5 admit short STRUCTURAL proofs (below) => impossible.** Gap shrinks {4,5,6,7} -> {6,7}.
- Cleanest completion = analytic r=4,5 + a dedicated minimum-degree-root certificate for r=6,7
  (extending the K=2,T=2 q-enumeration is valid but more expensive).

## ⚠ CRITICAL ASSUMPTION (must verify before trusting r=4,5)
The lemmas need **delta_2(G) = min over nonedges xy of |N(x)∩N(y)| = 2**, i.e. EVERY nonedge
has codegree >= 2. If "T=2" only records the EXISTENCE of one codegree-2 nonedge, the lemmas
do NOT follow. (Concretely: for min-degree root v and x in B=V\N[v], need codeg(v,x)>=2 so the
state S_x=N(x)∩N(v) has |S_x|>=2. Maximality gives only codeg>=1; codeg(v,x)=1 nonedges are a
separate T=1 situation. CHECK whether the campaign establishes delta_2>=2 or handles t=1 branches.)

## Why iterated deletion alone fails (option a — REJECTED)
Global BCL gives a(29)<=35, a(28)<=33, a(27)<=31; but r=4,5 need a(29)<=34 and r=6,7 need
a(29)<=33, NEITHER of which follows from BCL (35/29^2 < 1/23.5). Second deletion doesn't repair.
Pruning bonus: r=4 => e<=138, r=5 => e<=139, r=6 => e<=140, r=7 => e<=141.

## r=4 closure (RIGOROUS, modulo delta_2>=2)
v deg 4; A=N(v) (|A|=4); B=V\N[v] (|B|=25). State S_x=N(x)∩A. delta_2=2 => |S_x|>=2.
Triangle-free => adjacent B-vertices have DISJOINT states. Size-3 state has no disjoint
A-subset of size>=2 => no B-neighbor => degree 3 < delta=4, impossible. So every state has size
2 or 4. The six 2-subsets of A form 3 complementary pairs (S, A\S); put state-S on side 0,
complement on side 1. Per pair with sizes p,q, monochromatic edges <= 2min(p,q) <= p+q; summing
over the 3 pairs: **beta(G) <= #{x in B : |S_x|=2} <= 25 < 37. => r=4 impossible.**

## r=5 closure (RIGOROUS, modulo delta_2>=2)
|A|=5, |B|=24. |S_x|>=2; B-edges join disjoint states. Size-4 impossible (complement size 1 =>
degree 4 < 5). n2+n3+n5=24. Only B-edge types e22, e23; each size-3 only adjacent to its
complementary size-2 => e23 >= 2 n3. e(G) = 5+2n2+3n3+5n5+e22+e23, with edge window. Average the
5 coordinate cuts (vA-edge contributes 1; size-2 -> 2/5; size-3 -> 6/5; size-5 -> 1; every 2-3
edge cut; every 2-2 edge mono in exactly 1 of 5 cuts): some cut leaves
<= 1 + n5 + 2n2/5 + 6n3 + e22 mono edges; with the window =>
**beta(G) <= 28.6 + n3/5 <= 33.4 => beta<=33 < 37. => r=5 impossible.**

=> delta(G) not in {0,1,2,3,4,5,8,9}. **Only r=6,7 remain.**

## Recommended r=6,7 certificate (option b — BEST)
Root directly at min-degree v. A=N(v) (|A|=r), B=V\N[v] (|B|=29-r), states S_x ⊆ A. Exact cut:
place v on side 0, X⊆A and Y⊆B on side 1; monochromatic edges
  M(X,Y) = (r-|X|) + sum_{x in Y} |S_x ∩ X| + sum_{x in B\Y} |S_x \ X| + e_B(Y) + e_B(B\Y).   (CUT)
Then **beta(G) >= 37  <=>  M(X,Y) >= 37 for all X⊆A, Y⊆B** — solve by an exact MaxCut oracle,
adding each violated (X,Y) as a linear lazy cut. Static cuts: state size r-1 impossible
(r=6 allowed sizes 2,3,4,6; r=7: 2,3,4,5,7). Averaging gives necessary inequalities (C6),(C7).
Subinstances: r=6 e=112..140, r=7 e=112..141 = 59 scalar instances (or 2 interval-e models).
TARGET LEMMA ("Low-degree state lemma"): no state system satisfying (S1)-(S6) + edge window +
(CUT) exists for r=6 or 7. An independently-checked UNSAT certificate completes the degree reduction.

## Other options
(c) Extend K=2,T=2 reroot to r0 in {4,5,6,7}: rigorous but expensive — q_max=30-2r so r=4,5,6,7 give
    q_max=22,20,18,16; q=15..22 has 11890 raw profiles (vs 387 at q<=14); exact count needs rerunning the generator.
(d) Edge-maximality/stability: maximality is WLOG but does NOT force delta>=8 (K_{5,25} is maximal
    triangle-free, 30 vtx, delta=5, beta=0 — the large-beta condition must do the work). A beta>=37
    stability theorem might work but none follows from BCL; treating it as automatic = heuristic.
(e) Genuine gap: YES, but after the two structural lemmas only r=6,7. Until those two state systems
    are certified infeasible, the present finite proof does NOT yet establish a(30)<=36.
