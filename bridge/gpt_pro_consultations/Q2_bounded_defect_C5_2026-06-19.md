# Q2 — GPT-Pro follow-up: bounded-defect induced C5 (the stability crux)

Sent as a follow-up in chat c/6a35992e (preserves Q1 context). Date 2026-06-19.
Status: **STALLED / FAILED.** Sent in chat c/6a35992e; the generation entered an
extended literature-search mode then FROZE for ~30+ min (reasoning trace and a
literature snippet identical across multiple polls) and yielded only a 1-char "A"
stub. Stopped manually — no recoverable partial answer. Not re-sent immediately
(Q1 already delivered the core results MC2-MC4; the Q2 sub-questions are
nice-to-have and partly self-answered: C7-blowup gives `{C3,C5}`-free `β≈0.51n^2`,
n=2 exhaustive gives `β<=1`). May re-attempt in a fresh chat later. Continuing
another branch per the fallback rule.

## Context (GPT already has Q1 in this chat)

We adopted (and independently audited) from Q1: MC2 (every 5-set boundary
`>= 4n-2`; `<=4` vertices of degree `< (4n-2)/5`), MC3 (a 2-dominating induced
C5 ⟹ `β<=n^2`; root defect `def(S)=Σ(2-d_S(v))`), MC4 (frozen-pair: `a(5n)<=n^2`
⟺ no triangle-free `β=n^2` graph has a codegree-0 nonedge frozen on one side of
every max cut). New: MC5 — a counterexample has `e >= 2(n^2+1)` (since
`maxcut>=e/2`), so average degree `>= 4n/5` and edge density `>= 0.16`; with BCL
this forces density into the open window `(0.2486, 0.3197)`.

We caught and REJECTED Q1's Lemma 5 (its proof used the R(3,3) triple's degree
LOWER bound `>=4n/5` as an upper bound). We do not use it.

## Exact questions

1. **Existence of an induced C5.** Does a triangle-free graph `H` on `5n`
   vertices with `β(H) >= n^2` necessarily contain an induced C5 (odd-girth = 5)?
   A `{C3,C5}`-free non-bipartite graph has odd-girth `>= 7`. Can such a graph
   have `β = Θ(n^2)` on `5n` vertices given MC5's density `>= 0.16`? Please give
   either a proof that `β >= n^2` forces an induced C5, or an explicit dense
   `{C3,C5}`-free graph with large `β` (a falsification of this route).

2. **Bounded root defect.** If an induced C5 exists, is there always one with
   root defect `def(S) = o(n)` (ideally `O(1)`)? With `def(S)` defect vertices,
   the exact C5-template cleanup (your eq 39-44) should finish the induction —
   please state that cleanup precisely and the largest `def(S)` it tolerates.

3. **Direct frozen-pair attack.** Alternatively, prove the frozen-pair
   saturation statement (MC4) directly under the inherited constraints (MC2 high
   boundary, MC5 density, MC3 no 2-dominating C5, codegree-0 frozen pair, the
   unit-slack terminal-separating cover from your eq 38). Identify the single
   smallest remaining obstruction, or a minimal falsifying template.

4. **Per-graph vs numerical.** You warned per-graph H2 may fail even if the
   conjecture holds. Is the frozen-pair statement (MC4) the right exact object
   (it is equivalent to the conjecture), and does it avoid that pitfall? 

Please be exact and flag any step whose inequality direction is delicate.
