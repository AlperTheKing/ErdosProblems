# GPT Pro Answer — Step-1 delta>=8 in the delta_2=1 and delta_2=3 branches

Source: ChatGPT Pro (Kapsamlı Pro), chat "Erdos Problem 23 Analysis"
https://chatgpt.com/c/6a3abb49-1ae0-83eb-b21f-2deb1e3f7de6 — reasoned **55m48s**,
read via main.innerText (assistant-role selector returned empty shells; text reader OK).
Prompt: 2026-06-23_step1_delta2_1_and_3_prompt.md. NOT audited yet (audit before integrating).

Common setup: root at min-degree v; A=N(v) (|A|=r), B=V\N[v] (|B|=29-r), H=G[B], S_x=N(x)∩A.
xy in E(H) => S_x ∩ S_y = ∅; and d_H(x)+|S_x| >= r (degree bound).

## VERDICT
- **delta_2 = 3: FULLY CLOSED BY HAND for r=4,5,6,7 (rigorous).**
- **delta_2 = 1: the GENUINE remaining gap** — needs an exact four-witness finite certificate
  (option (a) invalid; option (b) only partial; option (c) = the complete route).
- (delta_2 = 2 was the previous answer: r=4,5 hand (beta<=25, <=33); r=6,7 small cut-certificate.)

## delta_2 = 3 branch (every x in B has |S_x| >= 3) — ALL rigorous, by hand
- **r=4:** two size-3 subsets of a 4-set always intersect => H empty; size-3 => degree 3<4 =>
  every S_x=A => G = K_{4,26} => **beta=0**.
- **r=5:** analogous => beta bounded well below 37.
- **r=6:** 2-colour each H-component, size-7... (size-6) vertices with v, A opposite; each size-3
  vertex placed with A contributes 3 uncut A-edges; <=23 such => **beta <= 3*floor(23/2) = 33**.
- **r=7:** states sizes 3,4,7 only (5,6 impossible). TRIPLE-STATE LEMMA: occurring size-3 types
  F ⊆ C(7,3) have no two members intersecting in exactly 1 element => disjointness graph is a
  star. No size-4 state: beta<=3*floor(22/2)=33. >=1 size-4 state Q=[7]\T: only one size-4 type;
  occurring triples U satisfy U=T or U∩T=∅; orientation gives 3c or 3ℓ+4q uncut with c+ℓ+q<=22 =>
  (c<=12 => 3c<=36; c>=13 => ℓ+q<=9 => 3ℓ+4q<=36) => **beta <= 36 < 37.**
- => **delta_2=3, r<=7 entirely closed.**

## delta_2 = 1 branch — the genuine remaining gap
(a) Force min-degree root to have all local codeg>=2? **NO** (not structural). Counterexamples
    (refuting the implication, small-beta): C5-blowup (1,1,3,4,21) [min-deg-4 vtx has a codeg-1
    non-neighbour]; (1,2,3,22,2) [min-deg vtx's non-nbrs all codeg>=2 but another nonedge has codeg 1].
(b) Root at a codeg-1 pair: useful PREPROCESSING. If S_x={a}: C=N_H(x), P=A\{a}, R=B\({x}∪C),
    d=d_G(x)=1+|C|, |R|=29-r-d <= 29-2r (=21,19,17,15 for r=4..7). Core G[{v,x}∪A∪C]-ax is bipartite;
    maximality => G[P,C] has no isolated vertices. But does NOT alone bound R's frustration by 35.
(c) **Exact finite certificate (the complete route).** States S_i⊆A (i in B). Maximality:
    a∉S_i => c(a,i)>=1; for nonedge ij in H, c(i,j)=|S_i∩S_j|+|N_H(i)∩N_H(j)| >= 1. The condition
    delta_2=1 = at least one of FOUR witness types occurs (normalized):
      VB: |S_1|=1;  AA: #{i:{a,a'}⊆S_i}=0 with (a,a')=(1,2);  AB: a∉S_i & c(a,i)=1 with (a,i)=(1,1);
      BB: ij∉E(H) & c(i,j)=1 with (i,j)=(1,2).
    Fix v on side 0; for every α in {0,1}^A, γ in {0,1}^B impose
      U(α,γ) = #{a: α_a=0} + Σ_{i∈B} #{a∈S_i: α_a=γ_i} + #{ij∈E(H): γ_i=γ_j} >= 37   (= beta(G)>=37).
    An **UNSAT certificate for these models (r=4,5,6,7)** is logically equivalent to the missing
    delta_2=1 minimum-degree reduction.

## First actions GPT recommends
1. Audit whether the old r=6,7 (delta_2=2) certificate used GLOBAL codegree-2 rows (if so it cannot
   be imported into delta_2=1 just because all v-states have size>=2).
2. Run the new delta_2=1 four-witness model first at r=4.

## NET STATUS of delta(G)>=8 (excluding min-degree 4..7) after BOTH GPT answers
- delta_2 >= 4: G hom C5, done.
- delta_2 = 3: r=4,5,6,7 ALL closed by hand (beta<=36). ✓ RIGOROUS, no computation.
- delta_2 = 2: r=4 (beta<=25), r=5 (beta<=33) hand; r=6,7 = small cut-certificate (~59 instances).
- delta_2 = 1: r=4,5,6,7 = four-witness exact UNSAT certificate (small, |R|<=21).
=> The dominant completeness risk (delta>=8) is now reduced to a few hand-lemmas + TWO small
   certificate computations (delta_2=2 r=6,7; delta_2=1 r=4..7). Tractable. AUDIT TODO: verify the
   delta_2=3 hand bounds (esp. r=7) + build/run the two certificates (CPU now free after idx97/q10).
