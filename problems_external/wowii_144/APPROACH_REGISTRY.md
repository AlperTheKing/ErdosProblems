# WOWII / Graffiti.pc Conjecture 144 — Approach Registry

## DIRECT ROUTE — W144-S (Steiner diameter, girth at least five)

1. **Exact final deliverable.** A referee-grade proof of the exact Formal Conjectures statement
   `girth(G)-1+ecc(G, center(G)) <= tree(G)` for every finite nontrivial connected simple graph,
   together with a warning-free Lean 4 proof containing no `sorry` or `native_decide`, a
   current prior-art comparison, and the arXiv/DeepMind submission artifacts.
2. **Current frontier lemma or finite certificate.** For every finite connected cyclic graph of
   girth `g>=5`, center set `C`, `e=max_x d(x,C)`, and `k=g-1`, prove the exact Steiner-radius
   bound `srad_k(G)=min_v e_k(v) >= k-1+e`. Exact exhaustive tests cover every cyclic
   girth-at-least-five graph through 13 vertices: 52,000 graphs and 663,650 rooted instances,
   with no failure and minimum slack zero. This strengthens the former vertex-specific frontier.
3. **Explicit logical bridge.** The radius bound gives a `k`-set `S` with
   `d_G(S)>=srad_k(G)>=g-2+e`. Choose a vertex-minimal induced connected connector `J` for
   `S`. The minimal-connector cycle lemma gives a cycle of length at most `|S|=g-1` if `J`
   is cyclic, contradicting girth `g`; hence `J` is an induced tree. Its order is at least
   `d_G(S)+1>=g-1+e`, exactly W144. The proved branches cover `g<=4` and acyclic graphs.
4. **Next falsifiable action.** Fix a vertex `v` minimizing `e_k(v)` and prove directly that it
   has a `k`-terminal set whose every connector uses at least `e` nonterminal vertices.
   Equivalently, with `p=n-g+1`, find a `p`-set `X` avoiding `v` such that at least `e` vertices
   of `X` must be restored before `G[V-(X-Y)]` is connected. Otherwise return an exact
   girth-at-least-five counterexample to the displayed Steiner-radius bound.
5. **Exit condition.** Success when the Steiner-radius lemma, connector bridge, and exact target
   pass an independent referee check and compile in a clean warning-free Lean worktree. Exit
   DEAD on a verified girth-at-least-five counterexample to that exact radius lemma, or on a
   reformulation with no explicit bridge back to it.

## Known exclusions

Per-cycle selection is false at girth three; single-tail and one-stem-per-component routes are
false; the current Angle A/B drafts are incomplete. The inequality written at
`PROOF_144_B.md:388` is false for even girth and must not be used.
A stronger local N1 surrogate is false: `proverC/test_n1_results.json` records violations at
girth 5, 11, and 15. The exact residual-window N1 is also false: an independently checked
36-vertex graph has a unique shortest cycle, `g=14`, `D=14`, `e=8`, and its sole `e`-realizer
lies on that cycle, so `h=0<e-floor(g/2)=1` despite `D<e+floor(g/2)`. Consequently the old
N1+N2 bridge must not be used. The supplied consultation closes `g<=4` on paper,
but those cases are not Lean-closed yet.

The Fajtlowicz ciliate route closes all middle ciliates `C(2t,r-t)`, `2<=t<=r-1`,
but endpoint containment alone is insufficient. The triameter bounds `tri>=g+2e` and
`tri>=g+2e-1`, and the four-terminal bound `W4>=2g+4e-3`, have exact residual
counterexamples and must not be reused.

The active-component capacity cannot be replaced by rooted eccentricity alone: the exact graph in
`attack_144_n2/depth_only_counterexample.md` gives `|E_H intersect W|=13` but
`2(R_z(H)-h)=12`; its true rooted induced-tree capacity is `mu_z(H)=11`.
The stronger active surplus inequality
`q_x+max(0,2*delta-g) <= 2*(mu_z(H_x)-h)` is false. The independently verified graph in
`attack_144_n2/GPT_PRO_ACTIVE_COUNTEREXAMPLE_20260718.md` has `g=9`, `delta=5`, `q_x=0`,
and `mu_z(H_x)=h=1` for both adjacent choices of `z`, so its two sides are 1 and 0.



## DIRECT ROUTE — W144-C (ciliate endpoint augmentation)

1. **Exact final deliverable.** Prove `tree(G) >= girth(G)-1+ecc(G,center(G))` in the two endpoint cases of Fajtlowicz's radius ciliate theorem: an induced `P_(2r)` (`t=1`) or an induced `C_(2r)` (`t=r`), where `r=rad(G);` internal ciliates are already closed.
2. **Current frontier lemma or finite certificate.** Endpoint augmentation lemma: if the bare endpoint ciliate has fewer than `g-1+e` vertices after breaking its unique cycle when needed, augment it to an induced tree of at least `g-1+e` vertices, using the proved `P2`, `g<=4`, and Lemma M certificates.
3. **Explicit logical bridge.** Fajtlowicz supplies an induced `r`-ciliate. Internal parameters `2<=t<=r-1` already give the target. The endpoint augmentation lemma gives the identical target for `t=1` and `t=r`, hence exhausts every `1<=t<=r`.
4. **Next falsifiable action.** In the residual `g>=5` ranges `g-1+e>2r` (path) and `g-1+e>2r-1` (cycle), derive an exact Lemma-M admissible forest from a shortest path/cycle and the endpoint ciliate; otherwise exhibit an exact graph showing that this augmentation datum does not force the required certificate.
5. **Exit condition.** Success when both endpoint implications have referee-grade proofs. Exit DEAD upon a verified endpoint graph for which the stated ciliate-plus-`P2`/Lemma-M data cannot produce the required augmentation, naming the precise missing logical implication; do not open a new surrogate or witness hierarchy.
**W144-C disposition: DEAD as a separate route.** `CILIATE_ENDPOINT_FINAL_AUDIT_20260718.md` gives two infinite exact obstructions. `L_r` falsifies fixed-path retention. `G_m` contains both endpoint ciliates, lies in the P2 residual range, and falsifies every one-outside-component exchange with unbounded deficit. What survives is exactly the full multi-component assertion `M(K)>=e`, so the endpoint route returns to the global capacity frontier rather than closing a smaller lemma.
## DIRECT ROUTE — W144-MW (full-cycle rooted metric capacity, `g>=7`)

1. **Exact final deliverable.** A referee-grade proof of
   `tree(G) >= girth(G)-1+ecc(G,center(G))` for every finite nontrivial
   connected simple graph, followed by a warning-free Lean 4 proof with no
   `sorry` or `native_decide` and the combined arXiv/DeepMind artifacts.
2. **Current frontier lemma or finite certificate.** Let `K` be a shortest
   cycle of length `g>=7`, let `r=rad(G)` and `lambda=2r+1-g`. For a component
   `H` of `G-K` and a reserved cycle vertex `z` for which `H` has a legal
   attachment in `K-{z}`, form `J_z(H)` by adding an apex `rho` adjacent to
   every vertex of `H` incident with `K-{z}`. Put `p(y)=d_J(rho,y)`,
   `P_z(H)=max_{u,v in H}(p(u)+p(v)+d_J(u,v))`, and
   `E_H^K={sigma in K : exists y in H, d_G(sigma,y)>=r+1}`. Prove the exact
   full-cycle metric inequality `|E_H^K|+lambda <= P_z(H)`. Unrestricted exact
   tests through order 12 have no `g>=7` failure; the analogous short-girth
   statement is not part of this frontier.
3. **Explicit logical bridge.** The registered window cover satisfies
   `E_H subseteq E_H^K`, hence the full-cycle inequality gives (MW)
   `q_H+lambda<=P_z(H)`. Girth `g>=7` makes `J_z(H)` triangle-free; the
   three-in-a-tree theorem gives `P_z(H)<=2mu_z(H)`, so (MW) gives the exact
   ordinary inequality (O). Summing (O), using the registered active-component
   inequality for `q_X>0` and using one positive ordinary component to pay the
   wrap correction when `q_X=0`, gives the reserved global inequality
   `S+c<=2(M_z(K)-h)`. Its established counting bridge yields `M(K)>=e`, and
   Lemma M yields `tree(G)>=g-1+e`, namely W144. The separately isolated
   `g=5,6` conversion remains a required short-girth branch of this same exact
   capacity proof, not an asymptotic or surrogate target.
4. **Next falsifiable action.** Enumerate every legal full-cycle record through
   the existing exact order-12 corpus and targeted `g>=7` ear families,
   recording the minimum of `P_z(H)-|E_H^K|-lambda`; if no counterexample
   occurs, prove the inequality directly from intersections of the far-vertex
   cycle arcs and boundary-ear distances, with every use of shortest-cycle
   girth explicit.
5. **Exit condition.** Exit SUCCESS only on a referee-checked proof of the
   displayed full-cycle inequality that composes with the exact registered
   capacity bridge. Exit DEAD immediately on a verified `g>=7` graph6 record
   with complete `K,H,z,r,lambda,E_H^K,p,P_z(H)` data, or if the argument loses
   the stated bridge and becomes a hierarchy of surrogate witnesses.

## DIRECT ROUTE — W144-IND (vertex-deletion induction)

1. **Exact final deliverable.** Prove the exact Formal Conjectures inequality `girth(G)-1+ecc(G,center(G)) <= tree(G)` for every finite nontrivial connected simple graph, with a warning-free Lean proof and the common paper/PR artifacts.
2. **Current frontier lemma or finite certificate.** Prove: if `H=G-v` is connected and cyclic, then `girth(G)+ecc(G,center(G)) <= girth(H)+ecc(H,center(H))`; it is enough that every non-cycle connected cyclic `G` admits one such vertex `v` satisfying the inequality.
3. **Explicit logical bridge.** Delete such vertices until a cycle. Induction gives an induced tree in `H` of order at least `girth(H)-1+ecc(H,center(H))`, which remains induced in `G`; frontier monotonicity makes this at least the W144 target for `G`. A cycle has center all vertices and deleting one cycle vertex gives the base tree of order `g-1`.
4. **Next falsifiable action.** Exhaustively test every vertex deletion `G-v` that stays connected and cyclic through order 9, first the universal lemma and then the existential deletion lemma; return the first exact graph6/vertex obstruction.
5. **Exit condition.** Success on a referee-grade proof of deletion existence plus parameter monotonicity and the exact induction. Exit DEAD on an exact graph with no admissible deletion satisfying the displayed inequality, or if only a surrogate without this induction bridge survives.

**W144-IND disposition: DEAD.** `ECpo` (a 5-cycle with one leaf) has `g+e=6`; deleting its only off-cycle vertex leaves `C5` with `g+e=5`. Thus the registered nonincrease lemma is false. Any induction must pay the one-unit target increase by an actual induced-tree extension; parameter monotonicity alone cannot close W144.

## DIRECT ROUTE — W144-IND2 (paired deletion)

1. **Exact final deliverable.** Prove the exact W144 inequality and formalize it warning-free in Lean, then include it in the single 141–144 paper and DeepMind submission.
2. **Current frontier lemma or finite certificate.** Every non-cycle connected cyclic graph `G` of girth at least five has a vertex `v` such that `H=G-v` is connected and cyclic and `tree(G)-tree(H) >= (girth(G)+ecc(G,C(G)))-(girth(H)+ecc(H,C(H)))`.
3. **Explicit logical bridge.** Induct on order. A largest induced tree of `H` remains induced in `G`; the displayed paired difference and the induction bound for `H` yield `tree(G)>=girth(G)-1+ecc(G,C(G))`. Cycles are the exact base; girths at most four are already proved separately.
4. **Next falsifiable action.** Exhaustively test the displayed existential deletion inequality on all connected girth-at-least-five graphs through order 10, returning the first graph6 with all deletion differences if it fails.
5. **Exit condition.** Success on a structural proof of the paired deletion lemma and the induction. Exit DEAD on an exact graph with no qualifying deletion, or if proving the paired lemma merely restates W144 without a local extension argument.

**W144-MW disposition: DEAD.** The independently verified order-13 graph6
`LhCKK?@?G?_@C?` has `g=7`, `r=5`, shortest cycle `K=C7`, component
`H={12}` attached legally at `3` with reserved `z=0`, `E_H^K=emptyset`,
`lambda=4`, and `P_z(H)=2`. Hence `|E_H^K|+lambda=4>2=P_z(H)`.
The complete construction, invariant calculation, and verifier are in
`attack_144_n2/FULLCYCLE_METRIC_COUNTEREXAMPLE_20260718.md` and
`attack_144_n2/verify_fullcycle_metric_counterexample.py`. Restoring a
nonempty registered-window cover would define a different lemma; this
full-cycle route is closed rather than replaced by another surrogate.

**W144-IND2 frontier update.** Exact tests now show that every multicyclic girth-at-least-five graph through order 13 (44,258 graphs at orders 12–13) has a vertex `v` with `G-v` connected cyclic and `girth(G-v)+ecc(G-v,C(G-v)) >= girth(G)+ecc(G,C(G))`; minimum best slack is zero. Thus the paired deletion lemma reduces to this parameter-only statement for multicyclic graphs plus a direct unicyclic base proof. Neither finite certificate is a proof.

**Registered ordinary `(MW)` disposition: DEAD.** The independently verified
order-25 graph6 record
`XhCGGC@?G?_@?@??o?G??A?C??G??G??C??@???G?G?_??@_???` satisfies every
registered residual, maximum-height, safe-root, ordinary-component, and
two-legal-root hypothesis, but has `q_H=11`, `lambda=0`, and `P_z(H)=10`.
The exact report and verifier are
`attack_144_n2/REGISTERED_MW_COUNTEREXAMPLE_20260718.md` and
`attack_144_n2/verify_registered_mw_counterexample.py`. Its actual capacity
is `mu_z(H)=8`, so this kills only `(MW)`, not `(O)` or W144.

## DIRECT ROUTE — W144-BETA (cycle-rank order bridge)

1. **Exact final deliverable.** Prove `tree(G)>=girth(G)-1+eta(G)` for every finite connected cyclic simple graph, then formalize it warning-free and include it in the single 141–144 paper and DeepMind submission.
2. **Current frontier lemma or finite certificate.** With `n=|V(G)|` and cycle rank `beta=|E(G)|-|V(G)|+1`, prove the exact bound `eta(G)<=n-girth(G)-beta+1` for every connected cyclic graph of girth at least five.
3. **Explicit logical bridge.** Repeatedly delete a non-cut vertex lying on a cycle. Connectivity is preserved and cycle rank drops by at least one, so after at most `beta` deletions the remaining induced connected graph is a tree. Thus `tree(G)>=n-beta`; the frontier gives `girth(G)-1+eta(G)<=n-beta`.
4. **Next falsifiable action.** Evaluate `n-girth-beta+1-eta` on the existing exact connected girth-at-least-five corpus through order 13 and return the first negative graph6 record, or retain the lemma and attack it by a block/ear count.
5. **Exit condition.** Success only on a referee-checked proof of the displayed eta bound plus the deletion bridge. Exit DEAD immediately on an exact negative-slack graph; do not weaken it into a hierarchy of rank corrections.

**W144-BETA disposition: DEAD.** Exact graph6 `I?`acgwg_` has `n=10`,
`girth=5`, `eta=2`, 14 edges, and cycle rank `beta=5`, so
`n-girth-beta+1-eta=-1`. Thus the proposed rank-strengthened center-depth bound
is false. This is the same graph that also falsifies the degree-at-most-two
good-deletion restriction. No rank-correction hierarchy is opened.

## DIRECT ROUTE — W144-FROM142 (periphery-to-center bridge)

1. **Exact final deliverable.** Prove W144, formalize it warning-free, and include it with W141–W143 in the single combined paper and DeepMind submissions.
2. **Current frontier lemma or finite certificate.** For every connected multicyclic graph of girth `g>=5`, with `f=max_x d(x,Per(G))` and `eta=max_x d(x,C(G))`, prove `f>=eta+floor(g/3)-1`.
3. **Explicit logical bridge.** The proved W142 integral bound gives `tree(G)>=ceil(2g/3)+f`. Since `ceil(2g/3)+floor(g/3)=g`, the frontier yields `tree(G)>=g-1+eta`, exactly W144. The unicyclic case is already proved directly.
4. **Next falsifiable action.** Exact-test the displayed periphery-center inequality on every connected multicyclic girth-at-least-five graph through order 13, returning the first negative graph6 record.
5. **Exit condition.** Success only on a referee-checked proof of the displayed bridge composed with W142. Exit DEAD immediately on an exact negative-slack graph; do not add correction terms.

**W144-FROM142 disposition: DEAD.** Exact graph6 `G?`F@w` has order 8,
`girth=5`, cycle rank 2, `eta=2`, and periphery distance `f=1`. Hence
`f-eta-floor(g/3)+1=-1`. The exact W142 bound therefore does not imply W144
through the registered periphery-center inequality, and no correction hierarchy
is opened.

## DIRECT ROUTE — W144-MIN (eta-minimal induced cyclic subgraph)

1. **Exact final deliverable.** Prove W144, formalize it warning-free, and include it with W141–W143 in the single combined paper and DeepMind submissions.
2. **Current frontier lemma or finite certificate.** If `G` is connected cyclic with girth at least five and `H` is vertex-minimal among induced connected cyclic subgraphs satisfying `eta(H)>=eta(G)`, prove that `H` is unicyclic.
3. **Explicit logical bridge.** Induced subgraphs cannot have smaller girth, so `girth(H)>=girth(G)`. The proved unicyclic theorem gives an induced tree in `H`, hence in `G`, of order at least `girth(H)-1+eta(H)>=girth(G)-1+eta(G)`, exactly W144.
4. **Next falsifiable action.** Test every connected cyclic induced vertex subset of each existing girth-at-least-five graph through order 13 and return the first multicyclic inclusion-minimal feasible subgraph, with all invariants.
5. **Exit condition.** Success only on a referee-checked proof of the displayed characterization. Exit DEAD immediately on an exact multicyclic minimal feasible subgraph or at the first unsupported structural implication; do not add surrogate criticality hierarchies.

**W144-MIN frontier update.** The reproducible audit in `attack_minimal_subgraph/ETA_MINIMAL_SUBGRAPH_AUDIT_20260718.md` verifies the stronger eta-nondecreasing one-step deletion statement on all 45,593 multicyclic girth-at-least-five graphs through order 13; corpus and canonical-witness hashes are recorded. This is finite evidence, not a proof.

**W144-MIN proof-attempt disposition: STOPPED, characterization unproved.** A bad radius-nonincreasing deletion creates a genuinely new center whose unique eccentric vertex is the deleted vertex, and distinct deletions create disjoint new-center sets. The unsupported step is to prove that these witnesses, together with radius-increasing bad deletions, force cycle rank one. Exact records kill fixed exterior, degree-two-ear, and peripheral deletion rules; no surrogate hierarchy is opened.

**W144-S GPT Pro consultation update.**  The final answer explicitly did not prove or
refute the registered Steiner-radius lemma.  It proved the shortest-cycle attachment
bound `d_G((Q-{a,b}) union {x})>=g-2+d_G(x,Q)`, which is the already isolated deep-tail
regime.  The stronger root-free terminal reduction is DEAD at exact graph6 `HhEK__D`:
`g=5`, `eta=2`, every triple has Steiner distance at most 4, while every rooted
four-terminal eccentricity equals 5.  The independent verification and proof audit are
in `attack_global/GPT_PRO_STEINER_FINAL_20260718.md`; W144-S itself remains open.

## DIRECT ROUTE — W144-ROOT (rooted unicyclic reduction)

1. **Exact final deliverable.** Prove W144, formalize it warning-free, and include it with W141–W143 in the single combined paper and DeepMind submissions.
2. **Current frontier lemma or finite certificate.** For every connected cyclic graph `G` of girth at least five, put `e=eta(G)`. Prove that some `e`-realizer `x` lies in an induced connected unicyclic subgraph `H` with `d_H(x,C(H))>=e`.
3. **Explicit logical bridge.** The rooted inequality gives `eta(H)>=e`, and inducedness gives `girth(H)>=girth(G)`. The proved unicyclic theorem supplies an induced tree in `H`, hence in `G`, of order at least `girth(H)-1+eta(H)>=girth(G)-1+eta(G)`, exactly W144.
4. **Next falsifiable action.** Exhaustively test all induced connected unicyclic vertex subsets through order 11, with every eta-realizer as a possible root, and return the first graph having no rooted witness with all invariants.
5. **Exit condition.** Success only on a referee-checked proof of the displayed rooted unicyclic lemma. Exit DEAD immediately on an exact graph with no rooted witness or if rooted radius-criticality does not imply the lemma; do not add a hierarchy of rooted surrogates.

**W144-ROOT disposition: DEAD as a rooted radius-critical route.** Exact graph6 `G?`e_w` with fixed eta-realizer `x=1` has girth five, cycle rank two, `C={7}`, and `eta=2`; among all induced connected cyclic subgraphs containing `x`, only the full graph retains `d(x,C)>=2`. Moreover a rooted radius-preserving minimal subgraph can be the induced path `4-0-6-1`, while the rooted cyclic choice `G[{1,3,5,6,7}]=C5` preserves radius two but has `eta=0`. Thus Fajtlowicz's ordinary radius-critical theorem does not retain the prescribed root-center distance or eta. The existential rooted-unicyclic lemma remains finitely true through order 11 but unsupported; no rooted surrogate hierarchy is opened. Exact audit: `attack_rooted_radius/ROOTED_RADIUS_CRITICAL_AUDIT_20260718.md`.

## DIRECT ROUTE — W144-BLOCK (1-sum closure)

1. **Exact final deliverable.** Prove that a vertex-minimal counterexample to W144 of girth at least five is 2-connected, by a referee-grade 1-sum theorem, and compose this reduction with the active direct W144 proof.
2. **Current frontier lemma or finite certificate.** If `G=G1 vee_v G2`, put `tau_i=tree(G_i)` and let `rho_i(v)` be the largest order of an induced tree of `G_i` containing `v`. Prove the exact sufficient bound `max(tau_1,tau_2,rho_1(v)+rho_2(v)-1) >= girth(G)-1+eta(G)` whenever every proper cyclic side satisfies W144; tree sides are allowed.
3. **Explicit logical bridge.** Trees attaining `tau_i` remain induced in `G`, and rooted trees attaining `rho_1,rho_2` glue at `v` to an induced tree of order `rho_1+rho_2-1`. The displayed bound therefore proves W144 for every graph with a cut vertex. Hence any vertex-minimal counterexample has no cut vertex and, being connected with at least three vertices, is 2-connected.
4. **Next falsifiable action.** Exhaustively compute `tau_i`, `rho_i(v)`, girth, centers, and eta for small connected 1-sums of girth at least five; return the first graph6/decomposition violating the displayed sufficient bound, or prove it from exact 1-sum center formulas.
5. **Exit condition.** Success only on a referee-checked proof of the displayed 1-sum sufficient bound and its minimal-counterexample bridge. Exit DEAD on its first exact counterexample; do not replace it by a hierarchy of rooted parameters.

## DIRECT ROUTE - W144-SD (eta-realizer Steiner diameter)

1. **Exact final deliverable.** Prove W144, formalize it warning-free, and include it with W141--W143 in the single combined paper and DeepMind submissions.
2. **Current frontier lemma or finite certificate.** For connected cyclic `G` of girth `g>=5`, center `C`, and `eta=max_x d(x,C)`, prove that some eta-realizer `x` belongs to a `(g-1)`-set `S` with Steiner distance `d_G(S)>=g-2+eta`.
3. **Explicit logical bridge.** A vertex-minimal induced connector of `S` is a tree by the proved minimal-connector cycle lemma, since `|S|=g-1<g`; its order is at least `d_G(S)+1>=g-1+eta`, exactly W144. The acyclic and `g<=4` branches are already closed.
4. **Next falsifiable action.** Choose an eta-realizer and an extremal minimum connector; prove the global center-geodesic exchange, or return an exact counterexample to the displayed eta-realizer statement. Do not replace it by an all-root or local surrogate.
5. **Exit condition.** Success on a referee-grade proof of the displayed lemma and its connector bridge. Exit DEAD on an exact counterexample or the first unsupported global exchange; preserve that obstruction and do not open a surrogate hierarchy.


## DIRECT ROUTE — W144-2DEL (two eta-good deletions)

1. **Exact final deliverable.** Prove W144, formalize it warning-free, and include it with W141--W143 in the single combined paper and DeepMind submissions.
2. **Current frontier lemma or finite certificate.** Every connected multicyclic simple graph `G` of girth at least five has at least two distinct vertices `v` for which `G-v` is connected cyclic and `eta(G-v)>=eta(G)`. Exact enumeration verifies this through order 13 (45,593 graphs), with minimum multiplicity two.
3. **Explicit logical bridge.** Given any prescribed vertex `x`, one of the two deletions avoids `x`. Iteration produces an induced connected unicyclic `H` containing `x`, with `girth(H)>=girth(G)` and `eta(H)>=eta(G)`. The proved unicyclic W144 theorem supplies an induced tree in `H`, hence in `G`, of order at least `girth(G)-1+eta(G)`.
4. **Next falsifiable action.** In a minimal counterexample, classify every admissible bad deletion by its radius change and new-center/unique-eccentric witness; either derive two good deletions, using the proved cycle-rank-two theta base, or return the first unsupported implication with an exact graph6 obstruction.
5. **Exit condition.** Success only on a referee-grade proof of the displayed two-deletion lemma and its induction bridge. Exit DEAD on an exact counterexample or on a concrete unsupported implication not forced by girth; do not open a surrogate hierarchy.**W144-SD proof-attempt disposition: STOPPED, lemma unresolved.** The proved center-geodesic facts and exact audit are in `attack_global/ETA_REALIZER_STEINER_AUDIT_20260718.md`. In the range `2eta<g`, a nearest-center geodesic is unique and has no cross edge to the selected center-eccentric geodesic. The first unsupported step is (3.2): a longer connector path can contain selected terminals internally, so its extra edges need not be extra Steiner vertices. This is the excluded single-pair charge in global form. No counterexample to the eta-realizer lemma was found, and no surrogate hierarchy is opened.


**W144-BLOCK frontier update.**  For a cut vertex `v` with branches
`H_j=G[Q_j union {v}]`, the exact identity
`rho(G,v)=1+sum_j(rho(H_j,v)-1)` makes every 1-sum rooted gluing bound equal
to the single cut-rooted statement
`rho(G,v)>=girth(G)-1+eta(G)`.  Exact eccentricity/center/eta formulas for a
1-sum, the tree-number composition formula, `rho(H,v)>=ecc_H(v)+1`, and the
rooted shortest-cycle bound `rho(H,v)>=girth(H)-1+d(v,K)` are proved in
`attack_block_sum/BLOCK_SUM_FINAL_AUDIT_20260718.md`.  Exhaustive tests of
46,347 separable cyclic girth-at-least-five graphs and 179,705 elementary cut
splits through order 13 found no failure of the cut-rooted statement.  This is
finite evidence, not a proof.

**W144-BLOCK shortcut dispositions.**  The proposed center inequality
`eta(G1 vee_v G2)<=max(eta(G1),d(v,K)+ecc_G2(v))` is DEAD at exact graph6
`F?bao`: its two sides give `eta(G)=2`, `eta(G1)=1`, `d(v,K)=0`, and
`ecc_G2(v)=1`.  The same graph is the first failure of exterior end-block
nondecreasing-`girth+eta` deletion: both eligible leaves change `5+2` to
`5+1`.  The first multicyclic failure of that deletion rule is ``G?`e_w``,
where the sole exterior leaf deletion also changes `5+2` to `5+1`.  The
proved geodesic-plus-cycle rooted lower bounds miss the W144 target by one on
`F?bao`; the exact missing term is rooted off-cycle capacity.  The unsupported
step remains the cut-rooted statement itself, and no surrogate block-parameter
hierarchy is opened.

## DIRECT ROUTE — W144-DEG (2-connected maximum-degree/girth bound)

1. **Exact final deliverable.** Prove W144 for every finite simple connected 2-connected multicyclic graph of girth at least five satisfying `Delta(G)>=eta(G)+1`, by a referee-grade induced-tree construction.
2. **Current frontier lemma or finite certificate.** Prove the sharp structural bound `tree(G)>=Delta(G)+girth(G)-2` for every such graph; first test the stronger candidate with `-1` in place of `-2`.
3. **Explicit logical bridge.** The frontier and `Delta>=eta+1` give `tree(G)>=Delta+g-2>=eta+g-1`, exactly the W144 target in this residual subclass. This removes the subclass from any minimal-counterexample proof.
4. **Next falsifiable action.** Exhaustively compute exact maximum induced-tree order on the biconnected multicyclic girth-at-least-five corpus, returning the first graph6 counterexample to each candidate or retaining the surviving inequality for a maximal-induced-tree proof.
5. **Exit condition.** Success on a referee-checked proof of the surviving exact bound and its displayed W144 bridge. Exit DEAD on an exact counterexample to `tree>=Delta+g-2`, or at the first unsupported maximal-tree exchange; do not add weaker correction parameters.
## DIRECT ROUTE — W144-MET (2-connected metric split)

1. **Exact final deliverable.** Prove the exact metric split `eta(G) <= max(Delta(G),diam(G)-floor(girth(G)/2))` for every finite simple 2-connected cyclic graph of girth at least five, as a load-bearing W144 lemma.
2. **Current frontier lemma or finite certificate.** The displayed metric split; exact enumeration verifies it on all 5,653 biconnected girth-at-least-five graphs through order 13, with minimum slack zero.
3. **Explicit logical bridge.** If the diameter term is at least `eta`, the proved P2 bound gives `tree>=diam+ceil(g/2)-1>=g-1+eta`. Otherwise `eta<=Delta`, and the parallel exact degree-girth branch `tree>=g-1+Delta` gives W144. Together with the registered cut-vertex reduction this closes the graph classes covered by both branches.
4. **Next falsifiable action.** For an eta-realizer `x` and nearest center `c`, use 2-connectivity/Menger to prove that `eta>Delta` forces `diam(G)>=eta+floor(g/2)`; otherwise return an exact counterexample.
5. **Exit condition.** Success on a referee-grade proof of the displayed split and an independent exact verifier. Exit DEAD on a verified counterexample or at the first unsupported Menger/shortest-cycle implication; do not introduce correction terms.
**W144-MET disposition: DEAD.**  The 15-vertex theta graph `Theta(1,7,8)`,
graph6 `NpCGIE??G?_@?@??g?G`, is simple and 2-connected and has `girth=8`,
`Delta=3`, `diameter=7`, center `{0,1}`, and `eta=4`.  Hence
`max{Delta,diameter-floor(girth/2)}=3<4=eta`.  The construction, hand audit,
and independent verifier are in
`attack_ear_critical/METRIC_SPLIT_COUNTEREXAMPLE_20260718.md` and
`attack_ear_critical/verify_metric_split_counterexample.py`.  This kills the
metric split only, not W144; no correction hierarchy is opened.
**W144-DEG theorem update.** `attack_degree_girth/DEGREE_GIRTH_THEOREM_20260718.md` proves `tree(G)>=Delta(G)+girth(G)-2` for every 2-connected noncycle graph of girth at least five. The exact audit and independent verifier cover all 5,644 2-connected multicyclic graphs through order 13. The bound is sharp at `FCR`o`, so the universal `Delta+g-1` strengthening is DEAD. This closes W144 whenever `eta<=Delta-1`. The exact conditional strengthening `tree>=Delta+g-1` on `eta=Delta>D-floor(g/2)` has 104 cases and no failure through order 13, but remains unproved.
## DIRECT ROUTE — W144-MET3 (cycle-rank-at-least-three metric split)

1. **Exact final deliverable.** Prove that every finite simple 2-connected graph `G` of girth `g>=5` and cycle rank `beta>=3` satisfies `eta(G)<=max{Delta(G),diam(G)-floor(g/2)}`, as a referee-grade W144 lemma.
2. **Current frontier lemma or finite certificate.** Equivalently, prove that a 2-connected girth-at-least-five graph satisfying both `eta>Delta` and `diam-floor(g/2)<eta` has `beta<=2`. Exact enumeration verifies the contrapositive through order 13; the unrestricted split fails at cycle rank two.
3. **Explicit logical bridge.** For `beta>=3`, the diameter side and P2 give `tree>=g-1+eta`. Otherwise MET3 gives `eta<=Delta`: the proved degree-girth theorem closes `eta<=Delta-1`, while the parallel conditional branch `eta=Delta>diam-floor(g/2) => tree>=Delta+g-1` closes equality. The theta and unicyclic theorems cover `beta<=2`, and W144-BLOCK is the cut-vertex route.
4. **Next falsifiable action.** Verify the exact order-15 candidate `NhCGGE@?O?_@O@G???g`; if it is not a counterexample, search generalized-theta/open-ear extensions above order 13, then attack the first two independent ears.
5. **Exit condition.** Success on a referee-checked proof and independent verifier. Exit DEAD immediately on an exact `beta>=3` counterexample or the first unsupported Menger/ear implication; do not add correction terms.

**W144-MET3 disposition: DEAD.** Exact graph6 `NhCGGE@?O?_@O@G???g` is a
15-vertex simple 2-connected graph with `beta=3`, `girth=6`, `diameter=5`,
`Delta=3`, center `{0,1}`, and `eta=4`; hence the MET3 right side is three.
Its exact induced-tree order is 13 versus W144 target nine. It has six
eta-good deletions, and deleting vertex 2 leaves a unicyclic graph with
`girth=8,eta=4`, so W144-IND2 survives. See
`attack_ear_critical/METRIC_SPLIT_BETA3_COUNTEREXAMPLE_20260718.md` and its
independent verifier. No corrected metric hierarchy is opened.
## DIRECT ROUTE — W144-COMB (2-connected three-bound cover)

1. **Exact final deliverable.** Prove W144 for every finite simple 2-connected cyclic graph of girth at least five by combining three already proved induced-tree bounds.
2. **Current frontier lemma or finite certificate.** With `n=|V|`, `beta=|E|-|V|+1`, `D=diam(G)`, `Delta=maxdeg(G)`, `g=girth(G)`, and `eta=max_x d(x,C(G))`, prove `eta <= max(Delta-1, D-floor(g/2), n-g-beta+1)` for every 2-connected noncycle; cycles and cycle rank two are already closed separately.
3. **Explicit logical bridge.** The three alternatives combine respectively with the proved bounds `tree>=Delta+g-2`, `tree>=D+ceil(g/2)-1`, and `tree>=n-beta`, and each gives `tree>=g-1+eta`. Together with the cycle base this proves the full 2-connected case of W144.
4. **Next falsifiable action.** Exact-test the displayed three-term inequality on every biconnected girth-at-least-five graph through order 14 and on subdivided high-girth cores, returning the first graph6 counterexample with all terms; if it survives, prove the residual implication `eta>=Delta` and `eta>D-floor(g/2) => eta+beta<=n-g+1` by an ear/rank count.
5. **Exit condition.** Success on a referee-checked proof of the displayed three-term inequality composed with the three exact tree bounds. Exit DEAD on a verified counterexample or at the first unsupported ear/rank implication; do not add correction terms.

**W144-2DEL proof-attempt disposition: OPEN, local completion stopped.**
`TWO_GOOD_DELETION_AUDIT_20260718.md` proves that a radius-decreasing
deletion is eta-good, gives the exact unique-eccentric obstruction for every
radius-preserving bad deletion, and obtains two distinct deletions in the
2-connected cycle-rank-two theta base. Exact graph6 `J??CBBOi?{?` has
`beta=3`, `girth=5`, and five good deletions, but none is forced by either
local metric criterion. The first unsupported implication is that
radius-increasing bad deletions and the disjoint unique-eccentric fibers of
radius-preserving bad deletions cannot cover all but one admissible vertex.
No block/ear theorem presently proves that implication; it is not asserted.
## DIRECT ROUTE — W144-GCOMB (global three-bound cover)

1. **Exact final deliverable.** Prove W144 for every finite simple connected cyclic graph by combining three already proved induced-tree bounds, with no block-rooted strengthening.
2. **Current frontier lemma or finite certificate.** For girth `g>=5`, order `n`, cycle rank `beta`, diameter `D`, maximum degree `Delta`, and center depth `eta`, prove `eta <= max(Delta-2+kappa, D-floor(g/2), n-g-beta+1)`, where `kappa=1` for a 2-connected noncycle and `kappa=0` otherwise.
3. **Explicit logical bridge.** The alternatives combine with `tree>=Delta+g-3+kappa` (proved W141 bound, plus the new 2-connected improvement), P2 `tree>=D+ceil(g/2)-1`, and `tree>=n-beta`. Each gives `tree>=g-1+eta`; acyclic and `g<=4` branches are already proved.
4. **Next falsifiable action.** Exact-test the displayed inequality on every connected girth-at-least-five graph through order 13 and structured larger block sums; return the first graph6 counterexample with all terms or retain it for a block/ear proof.
5. **Exit condition.** Success on a referee-checked proof of the displayed global parameter cover composed with the three exact tree bounds. Exit DEAD on a verified counterexample or unsupported block/ear implication; do not weaken it by new correction parameters.
