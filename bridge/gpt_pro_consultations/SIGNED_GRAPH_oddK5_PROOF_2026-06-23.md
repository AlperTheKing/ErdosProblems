# GPT MAJOR advance: signed-graph reformulation => COMPLETE proof except an odd-K5 signed-minor obstruction

chat 6a3b5aba. Drop the per-edge electrical-flow route. Reformulate (G,M) as a SIGNED GRAPH (M = negative
edges). This gives a complete proof of Erdos #23 Step-2 EXCEPT one precisely characterized obstruction.

## Signed-graph reformulation
Switching at S subset V: M -> M XOR delta_G(S), and |M XOR delta_G(S)| - |M| = |d_B S| - |d_M S|.
=> CUT-DOMINATION (CD) is EXACTLY "M is a minimum-cardinality SIGNATURE" of (G,M).  (Sig)
B-edges flip max-cut side, M-edges don't => every cycle C has |C| == |C ∩ M| (mod 2) => signed odd circuits
of (G,M) = ordinary odd cycles of G.

## (Q4) the exact quadratic congestion statement (the correct object; NOT per-edge electrical flow)
Route each bad edge e fractionally over its length-4 B-paths P (sum_P f_{e,P}=1). Vertex load
lambda_v = sum_e sum_{P in P_e, v in P} f_{e,P}.  Q4: min_f sum_v lambda_v^2 <= N|M|.
Then sum_v lambda_v = 5|M| (5 vtx/path), Cauchy: 25|M|^2 <= N sum lambda_v^2 <= N^2 |M| => 25|M| <= N^2.
Dual: a SINGLE common nonneg vertex toll z (not commodity electrical voltages). WP5: sum_e ell_z(e) <=
sqrt(N|M|) (sum z_v^2)^{1/2} for all z>=0, ell_z(uv)=min_path sum_{x in path} z_x.
WARNING: CONGESTION-ONE is FALSE under the hypotheses (concrete K_{2,3}-based instance: N=13,|M|=4, all
d_B=4, CD holds, but 4 demands need >=8 central-edge units vs capacity 6). This does NOT refute Q4, only
the stronger unit-multiflow. So Q4 stays a falsifiable conjecture but is NOT the main route.

## THEOREM (PROVED): odd-K5-free P5 theorem  -- the main new result
If (G,M) from a maximum cut of a triangle-free N-vertex graph has NO odd-K5 signed minor, then |M| <= N^2/25.
(No d_B=4 assumption needed.)
PROOF. Odd-cycle-cover LP (P): min sum x_e s.t. sum_{e in C} x_e >= 1 for every odd cycle C, x>=0; dual (D):
max sum y_C s.t. sum_{C ni e} y_C <= 1 per edge. M is a min signature => 1_M is a min integral odd-cycle
cover of value m=|M|. (G,M) weakly bipartite [Guenin: weakly bipartite <=> no odd-K5 minor; Schrijver proof]
=> LP integral => dual y with sum y_C = m. Compl. slackness: y_C>0 => |C ∩ M|=1, and every bad edge
saturated. lambda_v := sum_{C ni v} y_C. Each cycle thru v uses 2 incident edges, congestion<=1 =>
2 lambda_v <= d_G(v). So lambda_v^2 <= (d(v)/2) lambda_v => sum lambda_v^2 <= (1/2) sum d(v) lambda_v.
CYCLE-DEGREE INEQ (6): odd cycle C of length ell in triangle-free G => sum_{v in C} d_G(v) <= N(ell-1)/2.
[For any x, N(x) ∩ V(C) has no two consecutive C-vertices (triangle-free) => independent in C_ell, size
<= (ell-1)/2; double count.] Let L=sum y_C(|C|-1) >= 4m (odd cycles >=5). sum lambda_v = sum y_C|C| = m+L.
sum d(v) lambda_v = sum_C y_C sum_{v in C} d(v) <= (N/2) sum y_C(|C|-1) = NL/2. => sum lambda_v^2 <= NL/4.
Cauchy: (m+L)^2 = (sum lambda_v)^2 <= N sum lambda_v^2 <= N^2 L/4. t=L/m>=4: m <= N^2 t/(4(t+1)^2).
t/(t+1)^2 decreasing for t>=1 => max over t>=4 at t=4 => m <= N^2 * 4/(4*25) = N^2/25.  QED.
Lean-friendly: only imported theorem = weak bipartiteness / odd-K5 exclusion; rest is elementary counting.

## (12) the sharp reduction
25|M| > N^2  =>  (G,M) contains an odd-K5 signed minor.  (much sharper than Sync.)

## Lehman-core end ALSO closed (PROVED, Section 6 counting)
For a primitive minimally-nonideal triangle-free Lehman core: q=|E|, r>=5 min odd-cycle length, s=min
signature; q = rs - k (1<=k<=r-1); each edge in exactly r of the q min odd cycles; 2 c_v = r d(v).
=> sum_i sum_{v in C_i} d(v) = (r/2) sum d(v)^2; with (6): (r/2) sum d^2 <= q N(r-1)/2 => sum d^2 <=
qN(r-1)/r. With sum d = 2q, Cauchy: 4q^2 <= N sum d^2 <= q N^2 (r-1)/r => q <= N^2(r-1)/(4r). Then
s=(q+k)/r <= N^2(r-1)/(4r^2) + (r-1)/r. For r>=5, (r-1)/(4r^2) <= 1/25 (= at r=5), (r-1)/r < 1 => when 5|N,
s < N^2/25 + 1 => s <= N^2/25 (integers). QED.

## THE ONE REMAINING BRIDGE (the single direction to pursue)
LEHMAN-CORE lifting/decomposition lemma: reduce a vertex-minimal counterexample to a minimally-nonideal
Lehman core while preserving the vertex budget, through signed subdivisions and 1/2/3-sums. Replaces the
elusive synchronization set A by the established ideal-clutter structure of signed odd cycles; identifies
odd-K5 core (NOT electrical congestion) as the true obstruction.
Refs: Guenin (homepages.cwi.nl/~lex/files/guenin2.pdf), Geelen even-cycle (math.uwaterloo.ca), arXiv:1203.4041.
