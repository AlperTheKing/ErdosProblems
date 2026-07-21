# W144 total-cover order lemma

Date: 2026-07-18.

This note proves the exact order bound

    ecc(G,C(G)) <= |V(G)|-girth(G)

for every finite connected cyclic simple graph.  It also proves the stronger
component-cover inequality from which the bound follows.  This is a completed
auxiliary lemma, not by itself a proof of Conjecture 144.

## Statement and notation

Let \(G\) have order \(n\), radius \(r\), center \(C\), girth \(g\), and put

    e=max_x d(x,C),             q=n-g.

Fix a shortest cycle \(K\), a vertex \(x\) with \(d(x,C)=e\), and a nearest
cycle vertex \(m\).  Write

    h=d(x,K),                   delta=e-h.

If \(h>0\), fix a shortest path

    m=p_0,p_1,...,p_h=x.

Thus \(P^\circ=\{p_1,\ldots,p_h\}\) consists of \(h\) vertices outside \(K\).
When \(h>0\), call the unique component of \(G-K\) containing
\(P^\circ\) active and call all other components ordinary.  When \(h=0\),
there is no active component and all components are ordinary.
For \(\delta>0\), let

    W={sigma in K : d_K(sigma,m)<=delta-1}.

For each component \(H\) of \(G-K\), define

    E_H={sigma in W : some y in H has d_G(sigma,y)>=r+1}.

The load-bearing estimate is

    sum_H |E_H| <= 2(q-h)                                      (1)

when \(2\delta\le g\).  When \(2\delta>g\), so that \(W=K\), its
wrap-corrected form is

    sum_H |E_H| + (2delta-g) <= 2(q-h).                         (2)

## Metric preliminaries

A shortest cycle is isometric.  Indeed, a path shorter than the shorter
arc between two of its vertices, together with that arc, contains a cycle
of length less than \(g\).

Also \(g\le 2r+1\).  Root a BFS spanning tree at a center and add any
non-tree edge; its fundamental cycle has length at most \(2r+1\).  Hence

    floor(g/2)<=r.                                             (3)

Finally \(e\le r\), since a nearest center \(c\) to an \(e\)-realizer \(x\)
satisfies \(e=d(x,c)\le ecc(c)=r\).

For every \(\sigma\in W\),

    d(x,sigma)<=h+d_K(m,sigma)<=h+delta-1=e-1.

Thus \(\sigma\notin C\), and so \(ecc(\sigma)\ge r+1\).  A vertex at
distance at least \(r+1\) from \(\sigma\) cannot lie on \(K\), by
isometry and (3).  Consequently every vertex of \(W\) belongs to at least
one \(E_H\):

    |W| <= sum_H |E_H|.                                       (4)

Put

    lambda=2r+1-g >= 0.

## Ordinary components

Let \(H\) be an ordinary component of \(G-K\), of order \(s\).
Choose an attachment edge \(au\), with \(a\in K\) and
\(u\in H\).  Every \(y\in H\) has an \(a\)-\(y\) path through \(H\) of
length at most \(s\).  Hence, if \(\sigma\in E_H\),

    d_K(sigma,a) >= t:=r+1-s.                                 (5)

If \(t\le0\), then \(s\ge r+1\), and

    |E_H|<=g<=2s-lambda.

If \(1\le t\le\lfloor g/2\rfloor\), deleting the cycle ball of radius
\(t-1\) about \(a\) gives

    |E_H| <= g-(2t-1)=2s-lambda.                              (6)

If \(t>\lfloor g/2\rfloor\), then \(E_H\) is empty.  In particular,

    |E_H|<=2s,

and every ordinary component with \(E_H\ne\varnothing\) has the sharper
slack

    2s-|E_H| >= lambda.                                       (7)

## The active component

Assume \(h>0\), and let \(H_0\) be the component containing
\(P^\circ\).  Put

    s_0=|H_0|-h,
    R=max_{y in H_0} d_{H_0}(y,P^\circ).

Every shortest path to \(P^\circ\) has all its other vertices in
\(H_0-P^\circ\), so \(R\le s_0\).  For \(\sigma\in E_{H_0}\), choose a
witness \(y\) and a nearest \(p_i\in P^\circ\).  Then

    r+1 <= d(sigma,y)
        <= d_K(sigma,m)+i+R
        <= d_K(sigma,m)+h+R.

Therefore

    d_K(sigma,m) >= t_0:=r+1-h-R.                             (8)

First suppose \(2\delta\le g\).  Then \(|W|=2\delta-1\).  If
\(t_0\le0\), then

    R>=r+1-h>=delta+1,

and hence \(|E_{H_0}|\le2\delta-1\le2s_0\).  If \(t_0\ge1\) but
\(t_0>\delta-1\), then \(E_{H_0}\) is empty.  Otherwise the vertices
of \(W\) at cycle distance at least \(t_0\) from \(m\) number at most

    2(delta-t_0)
      =2(e-r-1+R)
      <=2R
      <=2s_0.                                                 (9)

Now suppose \(2\delta>g\), so \(W=K\).  If \(t_0\le0\), then again
\(s_0\ge R\ge\delta+1\), and \(g<2\delta<2s_0\).  If \(t_0\ge1\), (8)
and the cycle count give either \(E_{H_0}=\varnothing\), or

    |E_{H_0}| <= g-(2t_0-1)
              = 2R+2h-lambda
              <= 2R
              <= 2s_0,                                      (10)

where the penultimate inequality follows from

    lambda=2r+1-g >= 2h+2delta+1-g > 2h.

Thus the active component always satisfies

    |E_{H_0}| <= 2(|H_0|-h).                                 (11)

Together with the ordinary bounds, (11) proves (1).

## Paying for wraparound

It remains to prove (2).  Suppose first that an ordinary component \(H\)
has \(E_H\ne\varnothing\).  Its slack in (7), together with the nonnegative
slack of every other component, gives

    2(q-h)-sum_H |E_H| >= lambda
      >= 2h+2delta+1-g
      >= 2delta-g.

Suppose instead that every ordinary \(E_H\) is empty.  By (4), \(h>0\)
and \(E_{H_0}=W=K\).  In particular, \(m\in E_{H_0}\).  A witness for
\(m\), together with the definition of \(R\), gives

    r+1 <= h+R,

so \(s_0\ge R\ge r+1-h\ge\delta+1\).  Therefore

    sum_H |E_H|+(2delta-g)
      =g+(2delta-g)
      =2delta
      <=2s_0
      <=2(q-h).

This proves (2).

## The order conclusion

If \(e=0\), the result is immediate.  If \(h\ge e\), the \(h\) vertices
of a shortest \(x\)-\(K\) path outside \(K\) give

    q>=h>=e.

Otherwise \(\delta=e-h>0\).  When \(2\delta\le g\), (4), (1), and
\(|W|=2\delta-1\) yield

    2delta-1 <= 2(q-h),

and integrality gives \(\delta\le q-h\).  When \(2\delta>g\), (4) and
(2) give

    2delta = |W|+(2delta-g) <= 2(q-h).

Again \(\delta\le q-h\).  In both cases

    e=h+delta <= q=n-g.

## Exact audit

The independent script `test_total_cover_order.py` checked both (1) and
the wrap-corrected inequality (2) on every connected
girth-at-least-five graph through order 13: 52,000 graphs and 31,636
cycle/realizer/anchor cases, with zero failures and minimum slack zero for
both the coverage and upper inequalities.

## Quantifier and bridge audit

The proof fixes an arbitrary shortest cycle, an arbitrary \(e\)-realizer,
an arbitrary nearest anchor, and an arbitrary shortest realizer--cycle path.
No optimizing choice among these objects is used.

The sets \(E_H\) may overlap.  This is intentional: (4) uses

    |W| <= |union_H E_H| <= sum_H |E_H|,

while every upper bound is proved separately for its own component before
being summed.  In the wrapped case the sharper ordinary slack
\(\lambda\) is charged only once, from one nonempty ordinary \(E_H\).
If no such component exists, coverage forces the unique active component
to cover all of \(K\), which is the second wrap case.  Thus the
union-versus-multiplicity and wrap quantifiers are exhaustive.

In the earlier shortest-cycle route, \(q=|V(G)-K|\).  The result closes the
unconstrained cardinality step \(q\ge e\) and the corresponding global
cover budget.  It does **not** show that \(q\) outside vertices form an
admissible induced forest, nor that the rooted admissible capacity
\(M_z(K)\) is at least \(e\).  Cycles inside outside components and multiple
attachments are precisely the missing conversion.  Therefore this lemma
does not by itself prove the Steiner-radius frontier or W144.