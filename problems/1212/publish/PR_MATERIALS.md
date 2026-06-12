# Publication materials for Erdős #1212 partial results (prepared 2026-06-10)

## A. Public repo (to create): github.com/AlperTheKing/erdos-1212-partial
Local repo ready at problems/1212/publish/erdos-1212-partial (commit fd92595 + v3 README update pending
commit). Contents: README.md (manuscript v3), no_periodic_certificate.md, lean/erdos1212_cores.lean,
code/build_chain.py, data/build_chain.log, data/chain.json.gz.

## B. PR to teorth/erdosproblems — edit data/problems.yaml, entry number "1212"
Change: add/extend the `comments` field (status remains "open"):

  comments: "Partial results (2026): a sufficient 'composite-anchor' reduction (an infinite sequence
  of composites with a_{n+2}-a_n < min(P^-(a_n), P^-(a_{n+2})) yields the desired path); an
  impossibility theorem for periodic certificates; a conditional resolution under an every-interval
  max-gap hypothesis for rough composites; Lean-verified cores and large-scale verified computations:
  https://github.com/AlperTheKing/erdos-1212-partial"

## C. PR description (methodology disclosure)
Title: "#1212: add comment linking verified partial results (reduction + obstruction + conditional)"
Body:
- Adds a comments note for problem 1212 linking a repository with: (1) a sufficient reduction
  (composite-anchor lemma, single roughness criterion), (2) a theorem that no periodic certificate
  exists (two-case proof; cores formalized in Lean 4/Mathlib: 6 theorems, 0 sorry, axioms propext/
  Classical.choice/Quot.sound), (3) a conditional YES under a precise open short-interval supply
  statement for rough composites, with literature status (closest: Matomäki JLMS 2022; Matomäki-
  Teräväinen TAMS 2023), (4) machine-verified anchor chains (797,568 anchors, all path vertices
  checked exactly).
- Methodology: autonomous Claude agent (orchestration, verification, computation) collaborating with
  GPT-5.5 Pro (mathematical reasoning); two adversarial review rounds; human involvement
  non-significant. Status of the problem itself remains OPEN — this PR only records partial progress
  per CONTRIBUTING.md's comments-field usage.

## D. erdosproblems.com/1212 site comment (optional, needs user account)
"Some verified partial results (2026): (1) Sufficient reduction: if composites a_1<a_2<... satisfy
a_{n+2}-a_n < min(P^-(a_n), P^-(a_{n+2})) (least prime factors), the L-paths (a_n,a_{n+1}) ->
(a_n,a_{n+2}) -> (a_{n+1},a_{n+2}) give the desired infinite path; greedy chains satisfy this
empirically with huge margins (797k anchors verified). (2) The natural 'periodic certificate'
approach provably cannot work (an isolation/winding obstruction; Lean-checked cores). (3) The
reduction closes unconditionally given: every interval [x, x+Cx^θ] contains a composite with least
prime factor > x^δ for some θ<δ — an open Maier-Pomerance-strength statement; closest known are the
almost-all results of Matomäki (JLMS 2022) and Matomäki-Teräväinen (TAMS 2023). Details:
github.com/AlperTheKing/erdos-1212-partial."
