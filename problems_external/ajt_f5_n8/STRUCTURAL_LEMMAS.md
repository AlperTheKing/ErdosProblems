# Exact structural lemmas for AJT over F5 in dimension 8

Status: internally derived and independently algebra-checked on 2026-07-21. These are pruning lemmas for the direct counterexample search, not a claim that AJT is settled.

## Theorem: every column has at least five nonzero entries

Let `A in GL(8,F5)` be a counterexample, so the eight row kernels cover `T=(F5*)^8`. Then every column of `A` has at least five nonzero entries.

### Proof

The known AJT theorem in dimensions below 8 over `F5` is available from Yu's bound `n < 2^(5-2)`.

Assume a column has exactly four nonzero entries. Permute rows and columns and scale the four active rows so that, writing the distinguished coordinate as `x` and the other seven coordinates as `y`, the rows are

`x+c_1(y), x+c_2(y), x+c_3(y), x+c_4(y), d_1(y),...,d_4(y)`.

Put `u_i=c_i-c_4` for `i=1,2,3`. Invertibility of `A` says that

`d_1,d_2,d_3,d_4,u_1,u_2,u_3`

is a basis of the dual seven-dimensional space. Define

`v_1=u_2+u_3, v_2=u_1+u_3, v_3=u_1+u_2`.

The change-of-basis determinant from the `u_i` to the `v_i` is `2 mod 5`, so `d_1,...,d_4,v_1,v_2,v_3` is also a basis. AJT in dimension 7 gives a `y in (F5*)^7` for which every `d_s(y)` and every `v_t(y)` is nonzero.

For this fixed `y`, the four values `x in F5*` must all be killed by the four active rows. Hence `{-c_i(y):1<=i<=4}=F5*`. Therefore

`sum_i c_i(y)=0` and `sum_i c_i(y)^2=0`.

Let `s=u_1+u_2+u_3`. Since `4=-1 mod 5`, the first equality gives `c_4(y)=s(y)`. The second then gives

`0=sum_i c_i(y)^2=sum_i u_i(y)^2+s(y)^2=sum_t v_t(y)^2`.

Each nonzero square in `F5` is `1` or `-1`. A sum of three elements from `{1,-1}` is never zero modulo 5, contradicting the choice of `y`. Thus degree four is impossible. Earlier fiber counting already gives degree at least four, so every column has degree at least five. QED.

## Immediate consequences

- `A` has at least 40 nonzero entries.
- The previously derived pair-column neighborhood lower bound is automatic.
- Any exact search may impose column degree at least five without excluding a counterexample.
- The same statement applies to `A^{-1}`, since the counterexample property is invariant under inversion.

## Theorem: every row has at least three nonzero entries

Assume the first row is supported on columns 1 and 2, and let `r0=-a_11/a_12`. For each `r in F5*`, parametrize the torus slice `x_2=r*x_1` by `t in (F5*)^7`. The other seven row forms become a `7 by 7` matrix `M(r)` acting on `t`. Only its first column depends on `r`, and it does so affinely, so `det M(r)` has degree at most one in `r`.

At `r=r0`, the slice is the kernel of the first row. Invertibility of `A` implies that `M(r0)` is invertible. For each of the other three nonzero ratios, invertibility of `M(r)` plus AJT in dimension 7 would give `t` and `M(r)t` both nowhere zero. The first row is also nonzero because `r!=r0`, producing an AJT witness for `A`. Thus a counterexample would force `det M(r)=0` at three distinct ratios while `det M(r0)!=0`, impossible for a polynomial of degree at most one. Hence support two is impossible. Support one was already excluded by the dimension-7 permanent theorem, so every row has support at least three. QED.

The support-two theorem above, together with the next theorem, strengthens this bound.

## Theorem: every row has at least four nonzero entries

Assume a row has support three. Permuting and scaling columns, write that row as `L=x_1+x_2+x_3`.

Let `R:F5^8 -> F5^7` be the map given by the other seven rows. Since the eight rows of `A` are independent, `R` has rank seven, so `ker R=<z>` is one-dimensional. Moreover `L(z)!=0`, since otherwise `Az=0`.

Consider the three seven-dimensional hyperplanes

`H_12={x:x_1+x_2=0}`, `H_13={x:x_1+x_3=0}`, and `H_23={x:x_2+x_3=0}`.

The map `(t_1,...,t_7) -> (t_1,-t_1,t_2,...,t_7)` parametrizes `H_12` and maps the seven-dimensional torus bijectively onto `H_12` intersected with the eight-dimensional torus. On this slice `L=x_3=t_2`, so `L` is automatically nonzero on the torus.

If `R|H_12` were invertible, AJT in dimension seven applied in this torus-preserving coordinate chart would give an `x in H_12` for which both `x` and `R(x)` are nowhere zero. The row `L` is also nonzero there, yielding an AJT witness for `A`, a contradiction. Therefore `R|H_12` is singular. Since `ker R=<z>`, this is equivalent to `z in H_12`.

The same argument on `H_13` and `H_23` gives

`z_1+z_2=z_1+z_3=z_2+z_3=0`.

The first two equations give `z_2=z_3=-z_1`; the third gives `2*z_1=0`. Since the characteristic is five, `z_1=z_2=z_3=0`, contradicting `L(z)!=0`.

Therefore support three is impossible. Together with the previous theorem, every row has support at least four. QED.

The current exact support box is therefore: row degrees `4..8`, column degrees `5..8`, and at least 40 nonzero entries in total.
