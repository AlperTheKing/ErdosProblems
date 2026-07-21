# W144 MW: nearest-root interval relaxation is false

Date: 2026-07-18.

This note does not refute the registered metric-window lemma `(MW)`. It
rejects a broader relaxation that keeps only the necessary inequalities
against cycle roots realizing `p(y)=d_J(rho,y)` and replaces the actual cover
`E_H` by every window position allowed by those inequalities.

The existing exact script `test_abstract_cap_union.py` checked 491,686 records
through order 12. Its minimum relaxed slack was `-1`. The first
girth-at-least-seven failure is graph6

    J??CB?[s@S?

with `n=11`, `g=7`, `r=e=3`, `K={0,3,4,6,8,9,10}`, `m=8`, `z=3`,
`delta=3`, `W={3,4,8,9,10}`, `H={1,2,7}`, `A(H)={9,10}`. The relaxed
cover is all five vertices of `W`, while `P_z(H)=4` and `lambda=0`; hence

    P_z(H)-|U|-lambda = 4-5-0 = -1.

Therefore any proof of `(MW)` must use the actual distances
`d_G(sigma,y)`, not merely nearest-root depth intervals.
