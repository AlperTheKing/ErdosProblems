# P88: phase red-team and the pure-order C84 counterexample

## Verdict

The P84 inequality

\[
                         T_F(B,h)\le C_S(B,h)             \tag{C84}
\]

is **false as a pure endpoint-Sidon or nested-interval theorem**.  There is
an exact endpoint-normalized integer Sidon set with positive defect and

\[
                         (C_S,T_F)=(182,200).              \tag{1}
\]

Every one of its 182 folds is a nested pair of complementary intervals, so
that reformulation does not repair C84.  This row does not satisfy either
literal hole.  Along all of its positive-defect endpoint translations, the
75 C84 failures end before either literal hole first appears.

Thus the literal phase is load-bearing for any surviving form of C84.  The
full positive-defect literal-hole statement remains unfalsified.  In
particular, this note does not prove or disprove `T_F=o(p^3)` for the actual
frontier class.

At the abstract level the target can fail maximally: an explicit infinite
family of ordered linear fold shadows has `C_S=Theta(p^2)` and
`T_F=Theta(p^3)`.  Hence neither P82 linearity, the role order, the P83
shared-triple injection, nor a phase-free nested-pair argument can imply the
required little-oh estimate.

## 1. Exact pure-order counterexample

Take `h=3286` and

```text
B = {0,122,163,328,351,488,499,528,553,681,837,838,920,941,
     1051,1070,1117,1322,1340,1414,1449,1520,1608,1613,1617,
     1715,1853,1866,1925,2057,2074,2153,2173,2240,2320,2380,
     2475,2521,2564,2596,2598,2654,2788,2815,2839,2901,2950,
     2958,3026,3070,3076,3131,3170,3184,3200,3212,3215,3222,
     3248,3285}.
```

Then `p=60`, `max(B)=h-1`, all diagonal-inclusive unordered sums are
distinct, and all positive differences are distinct.  The defect is

\[
 {3p^2-p+2\over2}-h=2085>0.                            \tag{2}
\]

Exact enumeration gives (1).  For every canonical fold

\[
                    a+c+h=u+v,\qquad a\le c<u\le v,     \tag{3}
\]

the intervals `[c,u]` and `[a,v]` are nested and their lengths satisfy

\[
                         (u-c)+(v-a)=h.                  \tag{4}
\]

Consequently (1) directly falsifies C84 under endpoint normalization,
integer Sidonicity, positive defect, role order, and the nested
complementary-interval normal form.

The SHA-256 of the comma-separated mark list, with no spaces, is

```text
9e2345da856430f478d63284d6b62b347498b64b4cec4606f8f85c213db08457
```

The source orientation is `singer-natural-aaccd2fd8048` in P46's archived
carry statistics.  Its reflection has `(C_S,T_F)=(182,135)`, so this is also
an exact warning that the loose count is orientation-sensitive while the
fold count is fixed.

## 2. Translation phase audit

Put `B_gamma=B+gamma` and `h_gamma=3286+gamma`.  Positive defect holds for
exactly `0<=gamma<=2084`.  Exhausting these 2,085 translations gives:

```text
C84 failures:                 75
first failure:                gamma=0,   (C_S,T_F)=(182,200)
last failure:                 gamma=327, (C_S,T_F)=(148,155)
first b=1 literal hole:       gamma=1169,(C_S,T_F)=(54,14)
first b=2 literal hole:       gamma=1190,(C_S,T_F)=(60,21)
C84-failure/literal-hole overlap: 0
```

The checked-in P92 translation program does not test the pure-order claim.
It forms `admissible_bs` and skips the row when that list is empty before it
reaches its C84 comparison.  Therefore its zero-failure count applies to
literal-hole translations only; it cannot support a claim of zero failures
without the hole premise.

## 3. Infinite abstract order countermodel

Let `p=2m+1`.  On three labelled copies of `{0,...,p-1}`, take the edges

\[
 E_p=\{(a,a+d,m+d):0\le a<m,\ 0\le d\le m\}.           \tag{5}
\]

Every edge has `a<=c<u`.  Each of its `AC`, `AU`, and `CU` projections is
injective, so this is an ordered linear 3-partite fold shadow.  Direct
summation gives

\[
 |E_p|=m(m+1)={p^2-1\over4},                           \tag{6}
\]

\[
 T_F(E_p)={2m(m+1)(m-1)\over3}
          ={(p^2-1)(p-3)\over12}.                     \tag{7}

Indeed, a shadow triangle is specified by `(a,d_0,d_1)` with

\[
 0\le a<m,\quad 0\le d_0,d_1\le m,\quad
 0\le a+d_0-d_1<m;                                    \tag{8}
\]

the `d_0=d_1` cases are the `m(m+1)` canonical triangles and all others are
loose.  Thus this family has cubic loose density despite exact role order,
linearity, and the P83 injection into ordered shared triples.  It is not an
integer-ruler family because no common set of marks supplies the fourth
fold endpoint; it is the sharp abstract obstruction, not a frontier
counterfamily.

The exact finite rows at `p=11,17,23,31,43,59` agree with (6)--(7).  At
`p=59`, for example, `(C_S,T_F)=(870,16240)`.

## 4. Actual-hole red team

The separate `q=2` archive lift preserves each seed fold shadow while making
the `b=1` literal hole automatic by parity.  It exhausted 622
positive-defect lifted translations from 2,526 oriented archived rulers and
found no C84 failure.  The largest ratio was

\[
                         {T_F\over C_S}={30\over40}      \tag{9}
\]

at `p=24`; the reflected P75 lift gives `37/51`.  Exact one-mark and
two-mark endpoint-preserving reinsertion around the strongest rows found no
alternative folded Sidon neighbor with a larger ratio.

This is consistent with the wider P84/P92 literal-hole censuses but is not a
proof.  P92 independently kills the one-step hexagon-label Hall injection:
eight triangles can have only seven such fold-label targets.  P89 kills
occupancy counting of the P87 stencil on an infinite actual family.  The
remaining version of C84, if true, must therefore use a genuinely global
correlation created by the literal hole, not pure interval order, local
stencil occupancy, constituent-fold matching, or one signed hexagon step.

## 5. Reproduction and claim boundary

Run

```powershell
python -B problems/864/compute/p88/verify_c84_order_counterexample.py
python -B problems/864/compute/p88/phase_redteam.py `
  --output problems/864/compute/p88/phase_redteam.json
```

The first command independently verifies integer Sidonicity, all nested
complementary folds, (1)--(4), the 2,085-translation phase audit, and the
hash.  The second reproduces the abstract rows, the 622 actual parity lifts,
and the local searches.

The proved negative result is that C84 is not a pure order theorem.  The
abstract ordered target `T_F=o(p^3)` is false.  No actual infinite
positive-defect literal-hole family with `T_F=Omega(p^3)` is constructed,
and no full-hypothesis C84 failure is found.
