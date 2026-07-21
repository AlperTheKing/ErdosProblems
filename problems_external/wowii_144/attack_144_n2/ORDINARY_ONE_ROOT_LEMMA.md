# W144 ordinary one-legal-root lemma

## Statement

Use the registered W144-R residual notation, although the proof below only
needs that `K` is an isometric shortest cycle of order `g`, that `r` is the
radius, and that `E_H` is defined by the threshold `r+1` on a subset `W` of
`K`.  Fix `z in K` and a component `H` of `G-K`.  Suppose

    E_H={sigma in W : some y in H has d_G(sigma,y)>=r+1}

is nonempty and all attachments of `H` outside `z` use one cycle vertex `a`:

    A(H)-{z}={a}.

Then, with `lambda=2r+1-g`,

    |E_H|+lambda <= 2 mu_z(H).                              (O1)

Thus the ordinary-component inequality (O) is proved for every component with
one legal cycle root, in all girths `g>=5`.

## Proof

Form the apex graph `J=J_z(H)`.  For `y in H`, put

    p(y)=d_J(rho,y),             R=max_{y in H} p(y).

Since all legal attachment edges use `a`, a shortest `rho-y` path in `J`
expands, after replacing its first edge, to an `a-y` path in `G` of the same
length `p(y)`.  Therefore, if `sigma in E_H` has witness `y`,

    r+1 <= d_G(sigma,y) <= d_K(sigma,a)+p(y)
                           <= d_K(sigma,a)+R.               (1)

Put `t=r+1-R`.  Equation (1) gives

    E_H subset {sigma in K : d_K(sigma,a)>=t}.              (2)

If `t<=0`, then `R>=r+1`, and

    2R-lambda = 2R-(2r+1-g) >= g+1 >= |E_H|.

Suppose `t>=1`.  Because `E_H` is nonempty and every two cycle vertices have
cycle distance at most `floor(g/2)`, necessarily `t<=floor(g/2)`.  The cycle
vertices at distance at least `t` from `a` are obtained by deleting the
`2t-1` vertices in the cycle ball of radius `t-1`.  Hence (2) gives

    |E_H| <= g-(2t-1)
           = g-2(r+1-R)+1
           = 2R-(2r+1-g)
           = 2R-lambda.                                    (3)

Thus `|E_H|+lambda<=2R` in both cases.

Finally choose `y` with `p(y)=R`.  A shortest `rho-y` path in `J` is induced.
Deleting `rho` leaves `R` vertices in `H`; they form a `z`-admissible tree,
because a chord from `rho` to an internal path vertex would contradict the
geodesicity of the path.  Consequently `mu_z(H)>=R`.  Combining this with (3)
gives

    |E_H|+lambda <= 2R <= 2mu_z(H),

which proves (O1).  QED.

## Scope

The proof also works when `H` has any number of attachment edges to the same
legal cycle vertex `a`, and it permits additional attachment edges to the
reserved vertex `z`, which are unrestricted in `mu_z(H)`.  It does not cover
components with two or more distinct legal roots in `K-{z}`; those are the
remaining ordinary metric-window frontier.