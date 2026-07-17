# Audit of GPT-Pro affine obstruction response

## Verdict

The response is fully read and archived in
`R3b_affine_obstruction_raw.md`.  Its four displayed propositions are
mathematically sound after the notation repair below.  They do not decide
Problem 424 and do not discharge any of the three current frontiers F1--F3.

## Accepted statements

1. A nonempty word in `f_d(x)=d*x-1` has the form `P*x-Q` with
   `1 <= Q <= P-1`; if `d` is its outermost multiplier, then
   `Q = 1 (mod d)` and every image value satisfies `d | n+1`.
2. For a fixed finite multiplier set `D`, all nonempty word progressions lie
   in `gcd(n+1,rad(lcm(D)))>1`.  Therefore their union has upper density at
   most `1-phi(R)/R`.  For `D={2,3,5}` this is `11/15`.
3. At a fixed slope `P`, at most `P-1` affine maps occur.  Hence a finite
   one-state equal-slope digit system is strictly subcritical.
4. The fixed-slope saturation criterion is correct: `c0*P_k` distinct maps
   at slopes with `P_{k+1}<=R*P_k`, evaluated at a valid seed `s`, imply
   lower density at least `c0/(sR)`.

The example `D={2,3,5,9,14}`, `s=17` has the stated valid memberships and
its inverse real images cover `[1/13,1]`.  This real cover does not imply the
integer saturation hypothesis.

## Notation repair

The raw answer writes `rad!(lcm ...)`; the intended object is the radical
`rad(lcm_{d in D} d)`.  No factorial is involved.

## Interaction with the live proof

The progression-cover and fixed finite equal-slope mechanisms were already
outside the current primary routes.  The result reinforces CX-R2's strict
finite-state obstruction.  Proposition 4 is a clean sufficient criterion,
but its hypothesis is essentially the offset-support mass gate already being
tested in F2.  It supplies no proof of that gate.

The next GPT-Pro query should therefore target the new exact rank-prefix
frontier from C16/C24, not ask again about finite affine progression covers.
