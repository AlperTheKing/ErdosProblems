CONTEXT:
We are attacking Erdős #944 / Dirac k=4,r=1. A target is a finite 6-regular
graph G that is 4-vertex-critical and has no critical edge. Fix v, H=G-v, and
a 3-colouring phi of H. In any target the six neighbours of v have colour
multiplicities (2,2,2). For every terminal x in N(v), the terminal list
assignment L_x on H is globally critical: H is not L_x-colourable, but H-y is
L_x-colourable for every y in H.

VERIFIED FACTS:
1. Kempe balance and accounting hold for every two-colour Kempe component.
2. For a mate (A,B)-Kempe component K containing a forbidden mate terminal,
   boundary-support-criticality holds: if R_C(K) is the set of vertices in K
   touching C outside K, then K is not colourable from L_x restricted to K with
   colour C also forbidden on R_C(K).
3. Support-to-multiplicity is not implied by one/two terminal list-criticality
   alone. A verified 9-vertex obstruction has a type-(1,1) component K with
   e_H(K,C)=7>4, support-critical for L_a and L_b', and one-deletion critical
   for L_a and L_b'. It fails target-level hypotheses because it is not
   6-regular after adding v, has N(c') subset N(gamma), and is not critical for
   all six terminal assignments.

NEW QUESTION:
Attack the domination/synchronisation lemma that would close the gap.

Type (1,1) version:
Let K be an (A,B)-Kempe component of terminal type (1,1), containing a' in A
and b in B. Let a be the other A-terminal and b' the other B-terminal. Suppose
K is boundary-support-critical for both L_a and L_b'. Suppose also the
target-level conditions hold locally: G is 6-regular, all six terminal list
assignments are globally one-deletion critical on H, and there are no
same-colour nonadjacent comparable-neighbour pairs. Prove that e_H(K,C) <= 4,
or construct a genuine obstruction satisfying these local target-level
conditions with e_H(K,C) >= 5.

Type (2,2) version:
Let K contain all four A/B terminals. Suppose K is boundary-support-critical
for L_a, L_a', L_b, and L_b'. Under the same target-level conditions, prove
e_H(K,C) <= 2, or construct an obstruction with e_H(K,C) >= 3.

REQUIREMENTS:
- Do not repeat the 9-vertex obstruction except as a starting point.
- Focus on the exact extra ingredients that killed the 9-vertex obstruction:
  6-regularity, all six terminal assignments, and comparable-neighbour
  exclusion.
- If proving the lemma, give a complete argument, not a heuristic.
- If disproving it, give an explicit finite graph/list certificate and state
  exactly which full target hypotheses it still fails, if any.
- End with weakest steps and a go/no-go route assessment for #944.
