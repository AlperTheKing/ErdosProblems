# Direct averaging bridge: exact counterexample

The proposed bridge

    sum_(z != m) 2(M_z(K)-h)
      >= (g-1) sum_H |E_H cap W|

fails on graph6 `Fh_gG`, already the smallest residual girth-five graph.
Its exact parameters are

    n=7, g=5, r=2, D=3, e=2,
    K={0,1,2,4,5}, x=m=0, h=0,
    W={0,1,4}, sum_H |E_H cap W|=4,
    (M_0,M_1,M_2,M_4,M_5)=(2,2,1,2,1).

The shortest cycle and the `e`-realizer are unique, so the maximum over all
admissible `(K,x,m)` is the displayed choice.  Hence the left side is

    2(2+1+2+1)=12,

whereas the right side is `4*4=16`; the exact maximum slack is `-4`.

Candidate N2 itself still holds: either `z=1` or `z=4` gives
`4 <= 2 M_z = 4`.  Thus uniform averaging over all `z != m` loses precisely
on the two roots carrying sole-attachment witness components.
