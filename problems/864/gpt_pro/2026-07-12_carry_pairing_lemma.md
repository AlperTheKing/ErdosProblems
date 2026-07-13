# Carry-pairing lemma for an unwrapped perfect difference set

Source: GPT-Pro response relayed by the user on 2026-07-12. Reconstructed
locally from the conversation after the browser copy disappeared.

Let `D subset Z_v` be a perfect difference set and let

    B={0=b_0<...<b_{p-1}=L} subset [0,v-1]

be a cyclic unwrapping. Write `S=S(B)` for unordered sums including
diagonals and `Delta=Delta_+(B)` for ordinary positive differences. Since
`v` is odd, perfect difference uniqueness gives the skew partition

    Delta disjoint_union (v-Delta)={1,...,v-1}.            (1)

For an integer `X>2L-v`, put `M=v+X` and

    E_X={s-X : s in S, s>X}.

Then

    M notin S+Delta  iff  E_X subset Delta.                (2)

Indeed, a representation requires `delta=v+X-s`. For `s<=X` this is at
least `v`. For `s>X`, writing `e=s-X` gives `delta=v-e`, and (1) says
`delta in Delta` iff `e notin Delta`.

Let `Y_X=S intersect (X,2L]` and `iota_X(s)=v+2X-s`. Whenever both `s`
and `iota_X(s)` lie in `Y_X`, their candidate differences add to `v`, so
exactly one belongs to `Delta`. Hence

    M notin S+Delta  =>  2M-v notin 4B.                    (3)

Put `C=L-B`. Reflection of fourfold sums gives, whenever
`M<=2L+v/2`,

    M notin S+Delta
      => y=4L+v-2M notin 4C,  0<=y<v.                      (4)

Equivalently, with `d=v+2L-M`, every hole with `d>v/2` forces

    2d-v notin 4(L-B).                                     (5)

The direct deficit-coordinate form is

    E_X={d-alpha-beta : alpha,beta in C, alpha<=beta,
                         alpha+beta<d}.                    (6)

If `2d-v=alpha+beta+gamma+eta` with all four terms in `C`, then
`e=d-alpha-beta` and `e'=d-gamma-eta` are positive complementary members
of `E_X`, contradicting (1). Thus every hole satisfies the dichotomy

    either M>2L+v/2,
    or 4L+v-2M is a genuine missing low carry in 4(L-B).    (7)

Two exact boundary consequences are

    {2L+1,...,v+L-1} subset S+Delta,                        (8)

and, if `c=b_{p-2}`,

    M_*=v+L+c notin S+Delta.                                (9)

Writing terminal gaps `g_0=v-L`, `g_1=L-c`, the forced hole is
`M_*=3v-2g_0-g_1`; standard character discrepancy bounds give
`g_0,g_1=o(v)`, so this universal hole is eventually above `5v/2`.

Interpretation. Any Singer carry hole below the `2(v-L)` top boundary must
be accompanied by a missing low integer in `4(L-B)`. This identifies the
integer-carry obstruction but does not itself provide an infinite
sub-3 construction. P29+P35 subsequently prove that all affine Singer
holes have submacroscopic deficit, so the Singer coefficient tends to 3.