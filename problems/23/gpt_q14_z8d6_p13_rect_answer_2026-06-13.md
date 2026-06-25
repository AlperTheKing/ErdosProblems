# GPT Pro answer summary: q14/t2 clean z8d6 p13/e24 rectangle obstruction

Prompt: `gpt_q14_z8d6_p13_rect_prompt_2026-06-13.md`.

GPT Pro did not claim a pure hand contradiction from the `8 x 6` row-sum-3
`R` matrix alone.  It proposed reducing the incidence layer to an
`A-B` template plus zero-pattern compression plus six local `D` option lists.

Key suggested lemmas:

1. For `p=13`, the bipartite graph `P=E(A,B)` has degree sequence
   `(3,2,2,2,2,2)` on both sides.  Reason: every `a-y` and `b-x` nonedge
   forces at least two neighbours on the opposite side, while total
   `e(A,B)=13`.

2. For every zero-label vertex `z`, if
   `X_z=N_A(z)` and `Y_z=N_B(z)`, then
   `|X_z|+|Y_z| in {5,6}`.  Lower bound comes from
   `deg(z)>=8` and `d_R(z)=3`; upper bound uses `X_z x Y_z subset F`
   and the forced `A-B` degree sequence.

3. If `epsilon` is the number of zero vertices with `|X_z|+|Y_z|=6`, then
   the six doubleton vertices must carry
   `M_D = 34 - epsilon` A/B incidences.

4. For each doubleton `d_j`, define
   `U_j^A = union_{z~d_j} X_z` and
   `U_j^B = union_{z~d_j} Y_z`.  Since `d_j` cannot share A/B neighbours
   with adjacent zeros,
   `X_{d_j} subset A \\ U_j^A` and `Y_{d_j} subset B \\ U_j^B`.
   Hence
   `sum_j (|U_j^A| + |U_j^B|) <= 38 + epsilon`.

5. Local D-option test: for each nonadjacent zero `z not~ d_j`,
   any option `(X,Y)` for `d_j` must satisfy
   `|X cap X_z| + |Y cap Y_z| >= 2`, while also obeying
   `X subset A \\ U_j^A`, `Y subset B \\ U_j^B`, and `X x Y subset F`.

6. Residual two-cover Hall tests can be applied after the zero rectangles:
   each cell of `F` has residual demand `delta(a,b)=max(0,2-rho_Z(a,b))`;
   the six D option lists must cover these residual demands and the A/B
   degree residuals.

Weakest step noted by GPT Pro: these lemmas reduce the row to a much smaller
finite D-option packing problem but do not by themselves prove UNSAT.

Local status: independently of this answer, the p13/e24 row was closed by
the fixed-R incidence solver with A-side lex symmetry:
`search23/q14_t2_z8d6_fixedR/full_p13_e24_lex.err` reports
`FINAL done=3888 unsat=3888 sat=0 unknown=0 cutsum=6`.
