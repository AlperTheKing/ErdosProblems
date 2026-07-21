# WOWII 144 residual direct attack (2026-07-18)

Status: **not a proof of C144**.  This note records one rigorously closed
structural regime, two exact endpoint obstructions, and a bounded falsifier for
the remaining GPT-Pro capacity proposal.  It stays on the W144-R bridge:
every successful item below produces the exact lower bound
`tree(G) >= girth(G)-1+ecc(G,center(G))`.

## 1. Fajtlowicz's ciliate theorem closes every internal parameter

Fajtlowicz's radius-critical theorem states that every connected graph of
radius `r >= 1` contains, as an induced subgraph, an `r`-ciliate

    C(2t,r-t),   1 <= t <= r.

Here `C(p,q)` consists of a cycle on `p` roots, with a pendant path of `q`
edges at every root.  The endpoint conventions are
`C(2,r-1)=P_(2r)` and `C(2r,0)=C_(2r)`.

Assume `2 <= t <= r-1`.  Delete one cycle root together with its whole
pendant path.  What remains is an induced tree of order

    A(t,r) = (2t-1)(r-t+1).

The ciliate contains a cycle of length `2t`, so the girth `g` of the ambient
graph satisfies `g <= 2t`.  Also `e=ecc(G,center(G)) <= r`.  Finally, writing
`u=r-t >= 1`,

    A(t,r) - ((2t-1)+r)
      = (2t-1)u-(t+u)
      = 2u(t-1)-t >= t-2 >= 0.

Consequently

    tree(G) >= A(t,r) >= (2t-1)+r >= (g-1)+e.

Thus C144 is proved whenever one of the radius-`r` ciliates supplied by the
theorem has an internal parameter `2 <= t <= r-1`.

Primary reference: S. Fajtlowicz, *A characterization of radius-critical
graphs*, Journal of Graph Theory 12 (1988), 529--532,
doi:10.1002/jgt.3190120409, Theorem 2.

## 2. Exact obstruction left by the ciliate route

The ciliate theorem alone does not close its two endpoints.

* If `t=1`, the induced ciliate is the tree `P_(2r)`, so it only yields
  `tree(G) >= 2r`.  The uncovered range is exactly

      g-1+e > 2r.

* If `t=r`, the induced ciliate is `C_(2r)`; deleting a vertex yields
  `tree(G) >= 2r-1`.  The uncovered range is exactly

      g-1+e > 2r-1.

An induced endpoint ciliate need not be dominating, and its distances inside
the induced subgraph need not equal ambient distances.  Therefore neither
endpoint can presently be augmented by simply appending an ambient geodesic.
No explicit implication from either displayed endpoint inequality to the
W144-R admissible-forest certificate has been proved here.  This is the single
missing bridge for the ciliate route.

The smallest residual girth-five example `Fh_gG` already lies in the path
endpoint regime: it is a 5-cycle with one leaf at each of two adjacent cycle
vertices, has `(r,e,g)=(2,2,5)`, and requires both leaves for the exact
six-vertex induced-tree certificate.  Thus the endpoint is not a vacuous
technicality.

## 3. GPT-Pro N1 is distinct from the local `proverC/test_n1.py` claim

GPT-Pro's Candidate N1 is the residual window assertion

    e > D-floor(g/2)
      ==> some e-realizer x has d(x,K) >= e-floor(g/2).

The file `proverC/test_n1.py` tests a different one-tail-per-branch assembly
claim and its counterexamples do not falsify the displayed window assertion.
Re-running `proverB/residual_probe3.py` checked 8,845 distinct corpus graphs,
including 562 R1 shortest-cycle instances, and found zero instances with
`delta=e-d(x,K)>floor(g/2)` for every realizer.  This is computational evidence
only; no proof of Candidate N1 is supplied.

## 4. Exact bounded test of GPT-Pro N2

The new scripts

* `proverC/test_gpt_n2.py`, and
* `proverC/test_gpt_n2_corpus.py`

enumerate `M_z(K)` exactly and test the direct disjunction: either the R0 tail
already has `h>=e`, or the proposed reserved-capacity inequality

    sum_H |E_H intersect W| <= 2(M_z(K)-h)

holds for some admissible choice of shortest cycle, realizer/anchor and
z != m.
The broader run restricted to `n-g <= 15` checked 315 residual graphs from the
atlas and the existing deterministic/random/adversarial families.  Result:

    checked = 315, failures = 0.

Both scripts compile with `python -m py_compile`.  This is not a proof.  The
unproved point remains the fixed-tail surplus inequality inside the component
containing the reserved `x`-tail, together with the case in which all usable
attachments of an indispensable witness component are the chosen vertex `z`.

## 5. Rejected metric shortcut

The proposed three-terminal shortcut would require a triameter bound at least
`g+2e`.  The local corpus test recorded 69 counterexamples among 8,446 graphs
(minimum slack `-4`), so that inequality cannot be used.  Merely adding a
fourth terminal has no stated quantitative bridge to `M(K) >= e`; without such
a bridge it would be another reformulation and is not pursued.

## 6. Next falsifiable direct action

Prove or falsify the following single strengthening of the rooted-component
model, with all quantities already defined in GPT-Pro Lemmas 6--10:

> **Reserved rooted-capacity lemma.**  In the residual `g>=5` case, one can
> choose a shortest cycle `K`, an `e`-realizer `x` with anchor `m`, and
> `z != m` so that the exact local rooted capacities satisfy
> `sum_H |E_H intersect W| <= 2(M_z(K)-h)`.

This lemma plus `|W|=2(e-h)-1` gives, by integrality,
`M_z(K)-h >= e-h`, hence `M(K)>=e`, and Lemma M gives the exact C144 target.
Exit this branch immediately upon a verified counterexample to the displayed
reserved inequality; do not replace it by another hierarchy of witnesses.


