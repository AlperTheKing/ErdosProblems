# GPT-Pro (Codex's chat) — C-alltie proof route: ZERO-MOAT PREFIX-SWITCH LEMMA

Retrieved 2026-06-28 by Claude via Claude-in-Chrome from chat "Concrete Proof for C-alltie"
(chatgpt.com/c/6a407d40-9d64-83eb-a983-bbc96b4ce848, Kapsamlı Pro, "Thought for 13m 53s").

## Target lemma (C-alltie, mu-free)
In a connected-B maximum cut minimizing Gamma, if O nonempty and a B-edge zv has T(z)=0 and T(v)=N, then v is
positive-K-connected to some overloaded o in O. Contradiction form: O nonempty, T(z)=0, T(v)=N, zv in B, and the
positive-K component C of v disjoint from O => contradiction to maxcut + Gamma-minimality.

## GPT-Pro's route: zero-moat prefix switch (NOT deletion)

**Switch notation.** For S subset V, flip S across the cut. B^S=(B\delta_B(S)) U delta_M(S), M^S=(M\delta_M(S)) U
delta_B(S). Cut-loss Delta_beta(S):=|delta_B(S)|-|delta_M(S)|. Maxcut => Delta_beta(S)>=0 for all S. If
Delta_beta(S)=0 and B^S connected, S is another connected-B max cut, so Gamma-min gives Gamma^S>=Gamma. **To
contradict Gamma-min it suffices to find S with Delta_beta(S)=0, B^S connected, Gamma^S < Gamma.**

**ZERO-MOAT PREFIX-SWITCH LEMMA.** Assume O nonempty, T(z)=0, zv in B, T(v)=N, C=posK-comp(v), C∩O=∅. Then there
exist: a bad edge f=ab in M_C; a shortest B-geodesic P=(x0=a,...,x_{ell-1}=b) with v=x_i in P; one oriented prefix
A^-={x0..x_i} or A^+={x_i..x_{ell-1}}; and a finite connected zero-load moat Z subset {T=0}, z in Z, Z∩C=∅; such that
for S:=A^± U Z: Delta_beta(S)=0, B^S connected, and Gamma^S < Gamma.

**Why (mechanism).** (a) PREFIX SWITCH IS ell^2-NEUTRAL: flipping prefix A={x0..x_i} turns bad edge f into a cut edge,
exposed path edge e_A=x_i x_{i+1} becomes bad; in B^A the replacement path x_i,x_{i-1},..,x0=a,b=x_{ell-1},..,x_{i+1}
has length ell(f)-1, so d_{B^A}(x_i,x_{i+1})+1=ell(f); principal square contribution -ell(f)^2+ell(f)^2=0 (rotates
the bad edge around the odd cycle). (b) MOAT Z ABSORBS THE GATE: since T(z)=0, no bad edge incident to Z and no bad
geodesic uses Z; adding Z changes the cut boundary only through old B-edges, and the gate edge zv (which would be a new
bad edge for prefix-only) becomes internal to S and disappears. Moat gate surplus g_Z(A):=2 e_B(Z,A)-delta_B(Z);
because Z has no bad incident edges, Delta_beta(A U Z)=Delta_beta(A)-g_Z(A). So Z turns a positive-slack prefix switch
into a cut-tight one. Once cut-tight, principal ell^2 still cancels, and the omitted gate edge zv gives a strict square
saving UNLESS some overloaded vertex (T>N) in the SAME posK-component supplies compensating square cost. C∩O=∅ => no
compensator => contradiction.

## Proof skeleton (two-level coarea over prefixes through v)
**Step 1 (average the cut-loss).** Occurrences Omega(v)={omega=(f,P,i,±): f in M_C, P in P_f, x_i=v}. Weight
w(omega)=ell(f)/(2|P_f|). Then sum_{omega} w(omega) = T(v) = N. Maxcut: Delta_beta(A_omega U Z)>=0. Desired coarea:
   **(ZG1)  min_{omega,Z} Delta_beta(A_omega U Z) = 0.**
Plausibility: principal cycle boundary contributes one B-edge + one bad edge -> cancels in Delta_beta; the only
systematic positive contribution near v is the zero gate zv; adding Z subtracts exactly g_Z(A_omega). If every
prefix-moat switch had strictly positive cut-loss, the averaged prefix inequality forces T(v)<N, contradicting T(v)=N.
So saturation forces >=1 cut-tight prefix-moat switch.

**Step 2 (Gamma-min on a cut-tight switch).** Restrict to S=A_omega U Z with Delta_beta(S)=0. Principal pair
f<->e_omega contributes exactly 0 to Gamma^S-Gamma. So
   Gamma^S-Gamma <= sum_{e in delta_B(S)\{e_omega}} ell_S(e)^2 - sum_{h in delta_M(S)\{f}} ell(h)^2,  ell_S(e):=d_{B^S}(e)+1.
Proposed square-coarea:
   **(ZG2)  min over cut-tight (A_omega U Z) of (Gamma^{A_omega U Z}-Gamma) < 0  whenever C∩O=∅.**
Reason: every off-principal square term is charged to the same posK-component C; vertices in C have T(x)<=N, so the
averaged off-principal square balance has NO positive excess reservoir; the zero gate removes >=1 potential new bad
edge (zv), a strict negative term. The only way the averaged square balance fails to be negative is if the same
K-component contains o with T(o)>N -- i.e. the forbidden C∩O != empty.

## EXACT-TEST CHECKLIST (Claude's job)
For each candidate config (T(v)=N, T(z)=0, zv in B): for every f in M_C, every P in P_f, every occurrence v=x_i:
 1. prefixes A^-={x0..x_i}, A^+={x_i..x_{ell-1}}.
 2. for each zero-load connected moat Z subset {T=0} with z in Z: S=A^± U Z.
 3. Delta_beta(S)=|delta_B(S)|-|delta_M(S)|.
 4. keep Delta_beta(S)=0 AND B^S connected.
 5. Gamma^S = sum_{h in M^S}(d_{B^S}(h)+1)^2.
PREDICTED CERTIFICATE: exists S=A^± U Z with Delta_beta(S)=0, B^S connected, Gamma^S < Gamma.
Coarea target: T(v)=N, C∩O=∅  =>  some zero-moat prefix switch is cut-tight and Gamma-decreasing.
