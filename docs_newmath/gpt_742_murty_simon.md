# GPT-5.5 Pro collaboration — pivot to #742 (Murty–Simon, diameter-2-critical) — 2026-06-09

Chat: chatgpt.com/c/6a284fca (browser cb342d47, "Kapsamlı Pro" = GPT-5.5 Pro). User directive: consult GPT, collaborate.

## GPT's answer (round 2, after I gave #617 r=5 calibration)
- **Dropped #617**: "no genuine r=5/K_26 collapse." Near-Turán view (each colour class ≥55 edges) has slack 50,
  doesn't force a tight classification; without a new exact stability theorem, my K17/r4 calibration is decisive. HONEST.
- **Pivot: #742 Murty–Simon diameter-2-critical**, the n=25, m=157 finite check. CLAIMED Fan did n≤24,n=26;
  Füredi large n; n=25 the live gap. ⚠ GPT CLAIMED resolving n=25 "completes the conjecture" — **FALSE** (see gate).

## GPT's STRUCTURAL LEMMA (to verify)
G diameter-2-critical, v any vertex of degree d, A=N(v) (|A|=d), B=V∖(A∪{v}) (|B|=b=n−1−d).
e_A=e(G[A]), e_AB=e(A,B). Claim:  **e_A + e_AB ≤ d·b = d(n−1−d)**,  i.e. e_A ≤ db − e_AB.
Proof (GPT): edge xy∈G[A]: since x,y∼v, deleting xy keeps d(x,y)≤2 via x–v–y, so xy is critical for some OTHER pair
{s,t} (nonadjacent, unique common neighbour) and xy lies on that unique length-2 path. ⟹ ∃ z: z∼x, z≁y,
N(z)∩N(y)={x}. z∉A (else v∈N(z)∩N(y), contra uniqueness), z≠v (v∼y, z≁y) ⟹ z∈B. So edge xy ↦ A–B nonedge (y,z).
Injective (two A-edges → same nonedge yz ⟹ y,z have two distinct unique common neighbours, impossible).
⟹ e_A ≤ |A||B| − e_AB.  [VERIFY computationally on small diam-2-critical graphs + then Lean.]

## ⚠ GATE VERIFICATION (mine, 2026-06-09) — GPT OVER-CLAIMED
- erdosproblems.com/742: Murty–Plesník/Murty–Simon conj (diam-2-critical ⟹ ≤n²/4 edges). Status DECIDABLE
  ("resolved up to a finite check"). Füredi [Fu92] proved large n. NOT formalised. Low activity (1 comment, 0 workers).
- Literature: Fan proved n≤24 AND n=26. Füredi proved n > n₀ where **n₀ = tower of 2's of height ~10¹⁴** (astronomical).
  ⟹ OPEN for n=25 AND ALL 27..tower(10¹⁴). So **resolving n=25 does NOT complete the conjecture** (GPT wrong).
- SILVER LINING (verified): Fan's bound m < n²/4 + (n²−16.2n+56)/320; at n=25 = 156.25+0.8625 = 157.11 ⟹ m ≤ 157.
  Conjecture wants ≤156 = ⌊625/4⌋. So the ENTIRE open n=25 case = "∃ diam-2-critical graph on 25 vtx with exactly 157 edges?"
  UNSAT ⟹ Murty–Simon holds for n=25 (a narrow, genuine, verifiable open SUB-CASE; modest — does NOT finish the conjecture).
- Crowded-ish: Haynes–Henning (maximum degree theorem), Foucaud et al. "Strengthening the Murty–Simon conjecture" (2019).
  MUST check whether n=25 was already computationally settled before claiming novelty.

## STATUS / NEXT
1. VERIFY GPT's lemma computationally (small diam-2-critical graphs) — IN PROGRESS.
2. Check literature: is n=25 (m=157) already computationally resolved? (scoop gate)
3. Assess feasibility of the n=25 m=157 exact search (heavy structural pruning needed; my K17/r4 calibration ⟹ be skeptical).
4. Correct GPT's over-claim; decide whether n=25 m=157 is a worthwhile modest target or pivot again.
