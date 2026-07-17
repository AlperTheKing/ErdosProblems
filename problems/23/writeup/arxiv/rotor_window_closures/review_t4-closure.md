# Adversarial referee review — sections/sixteen_atom_closure.tex ("The sixteen-atom closure (t = 4)")

Reviewed 2026-07-17. Reviewer: independent adversarial pass (Claude, Fable 5).
Scope: every claim in the section against its cited archives; rerun of every cheap
verifier; line-by-line check of all by-hand proofs; standalone-ish LaTeX check
against the companion preamble (`shortest_support_obstructions/main.tex`).

## Replay evidence produced for this review

The three primary census artifacts and both verification-path artifacts were
regenerated from the archived scripts
(`problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/`)
in a clean scratch tree (workers=8, geng from `tools/nauty2_8_9/geng.exe`,
Python 3.12.4, NetworkX 3.6.1). All canonical SHA-256 hashes reproduced
**bit-exactly**:

| artifact | canonical SHA-256 (replayed) | matches paper |
|---|---|---|
| t4_support_graph_census.json | 40f16a84559ace4827e366f152026f2b7868bdaed31ff9afb36184a29b48046d | YES |
| t4_atom_circuit_census.json | 302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652 | YES |
| t4_profile_transition_census.json | b464682b4142a9db2396dc39ac9a0ffd8ff638aba1b9270734667c8f0a543114 | YES |
| t4_cross_outer_exclusion.json | 79db75b95e8401064f1b6159bb980ee0149f0fb3a602a607306a7f0e501a5d49 | YES |
| t4_support_circuit_hit.json | 5b386cd90b795bf1e6f8f174e21aa559e37c9f682e5dff373dae6bf74f3b9641 | YES (regenerated at seed 0, step 0 of the archived search harness) |

Verifier verdicts, all rerun by me and all PASS:
`PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS`, `PASS_INDEPENDENT_NETWORKX_ATOM_CENSUS`,
`PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION` (histograms {8:255, 9:193, 10:101, 11:26, 12:1}
identical for v and m, rawMiddleSwaps=0, 4 support types, all n=15),
`PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY` (multiplicities 180/190/190/16, total 0),
`PASS_ABSTRACT_SUPPORT_CIRCUIT` (65,534 proper subsets, worst proper defect 0,
19 tight subsets, min edge degree 2).

geng per-n counts replayed directly (`geng -u -c -b n 15:15`, n=8..15):
2 / 30 / 496 / 3675 / 15285 / 36337 / 52909 / 45244, sum 153,978 — exact match
with Table `tab:t4:geng`.

Stage counts replayed: extraChoices=74,920; trianglePass=2,299;
unionMultiplicityPass=862; circuitPass=576; rowTuples=16,288; 34 graphs,
34 owner embeddings (one per graph). All match the section verbatim.

Lean source hashes recomputed (`Get-FileHash SHA256`):
R44K2TailOverlap.lean = 12DFB927...066A (match);
LiveMiddleSwapCrossOuter.lean = 3DFF7897...9275 (match);
R44OwnerStarDualHall.lean = A8D39A65...06D3 (match; correctly excluded from the paper).

---

## Per-claim verdicts

### Definition 1 (`def:t4:circuit`) — support circuit — **CONFIRMED**
Matches the companion Definition (m-footprint obstruction: connected bipartite,
m-1 edges, distance-four atoms, triangle-free atom graph, coverage, multiplicity
>= 2) plus the R44 deletion-SDR condition ("deleting any atom leaves a perfect SDR
onto all support edges", R44 §1). No strengthening, no dropped hypotheses.

### Lemma 2 (`lem:t4:transfer`) — **CONFIRMED** (proof complete)
Cited part matches companion Lemma [Minimal footprint] exactly (its four
conclusions are exactly what the proof invokes). The added SDR and connectivity
arguments are complete: Hall on proper subfamilies from inclusion-minimality;
|S\{a}| = m-1 = |E(F)| forces the SDR to be onto; the two-component counting
argument is airtight (each component contains an atom, supports stay in their
atom's component, pigeonhole on sums). Checked line by line; no gap.

### Lemma 3 (`lem:t4:induced`) — **CONFIRMED** (proof complete)
Chord (i,j), j-i>=2 gives a walk of length i+1+(4-j) <= 3 between the atom
endpoints, contradicting distance four. Arithmetic checked.

### Definitions 4–5 (`def:t4:selection`, `def:t4:rotating`) — **CONFIRMED**
The covered-star definition is a deliberate *weakening* of the engine's profile
predicate (drops r=4, drops all-neighbours-selected, drops exactly-one-active);
this only strengthens the theorems proved from it and is consistent with the
transitions script (`tuple_state`: coverage = positive pairCount for every
non-active neighbour). Rotating family matches R44 §3–5.

### Theorem 6 (`thm:t4:crossover`) — **CONFIRMED** (proofs complete, not sketches)
(i) kt disjoint owner-star edges (same-part owners never adjacent) + t distinct
terminal edges at one owner, none owner-incident (partners at distance 4 are not
owners since owners are pairwise at distance 2). (ii) The coverage row Q avoids v
(via row inducedness), has >= 2 non-owner-incident edges (v not in Q, m incident
to <= 2 path edges), and no edge of Q equals a terminal edge f_j (both parity
cases of Q's atom checked; either case makes b_j adjacent to a neighbour of v,
contradicting d(v,b_j)=4; the pigeonhole in the Y-atom case — two 2-subsets of a
3-set intersect — is correct). Matches R44 gate-header pillars (2) and (3) with
every "verified by inspection" step now written out. No gap found.

### Corollary 7 + Table (`cor:t4:table`, `tab:t4:crossover`) — **CONFIRMED**
Arithmetic checked at every table entry: budgets 8/15/24/35; k=2 bounds
11/14/17/20; k=3 bounds 12/16/20/24; k >= t-1 kill via kt+t >= t^2 > t^2-1;
(4,2) sole survivor with margin exactly 1. Matches R44 header/§3–5 and the
R45 slack values 7/4 at t=5.

### Definition 8 (`def:t4:window`) — **CONFIRMED**
Matches the census filter exactly (two same-shore degree-4 owners, >= 2 common
neighbours, exactly four atoms each — the enumerate script chooses exactly four
bad neighbours per owner and the eight extras avoid both owners).

### Lemma 9 (`lem:t4:absorption`) — **CONFIRMED** (proof complete)
The q -> v middle-replacement detour is valid: v not in Q (induced rows + the
non-selected edge vx0), x0/y at even Q-distance, distance 4 excluded because
d_B(x0,y)=2, so distance 2 with middle q != v; replacing q by v gives a second
row of the same atom, and complete supports absorb vx0, vy into F. Matches the
detour mechanism recorded in REPORT and the R45 gate header.

### Proposition 10 (`prop:t4:core`) — **CONFIRMED** (proof complete + Lean verified)
8 + 4 + 4 = 16 > 15 forces a shared terminal edge; equal edges have equal
owner-part endpoints, hence a shared atom-partner. Lean module
R44K2TailOverlap.lean: file SHA recomputed = 12DFB927... (match); the statement
`exists_common_tail_of_support_card_le_fifteen` is exactly the finite incidence
core (4+4+4+4 disjoint <= 15 is contradictory); axioms
[propext, Classical.choice, Quot.sound] are **dual-attested** — asserted in
REPORT.md and independently probed in the session gate
(CLAUDE_TO_CODEX.md 2026-07-11T21:37:27Z, "axiom probes ... = EXACTLY"). The
paper's framing ("structural reduction, not by itself an exclusion") matches
REPORT verbatim.

### Lemma 11 (`lem:t4:vertexrange`) — **CONFIRMED** (proof complete)
Mantel lower bound 16 <= |V|^2/4 correct; tree kill via the forced 4-cycle
v-x-m-y; the unicyclic kill is fully reconstructed (three 4-cycles
v-x0-q_i-y_i-v, pairwise distinct because y_i is in the wrong part to equal any
q_j and distinct from y_j/x0/v), against exactly one available cycle. This
discharges R45 §4's "verified by inspection" completely.

### Theorem 12 (`thm:t4:census`) — **CONFIRMED** (all numbers replayed bit-exactly)
Every count in the statement reproduced by my replay of the full pipeline AND by
the three independent verifiers (see table above). The completeness-of-reduction
paragraph is sound: the filter conditions are all *necessary* for a two-owner
window (degree/atom counts from Definition 8; vertex range from Lemma 11; shared
distance-four partner from Proposition 10; colour-swap invariance of the filter
is real — "same part" is invariant under swapping colour classes). One
equivalence the paper uses silently and I verified by hand: the census checks
triangle-freeness of the *union* graph (support + atom edges), while the
definition demands triangle-freeness of the atom graph only — these coincide,
because a triangle with >= 1 support edge is impossible (3 support edges:
bipartite; 2 support + 1 atom: the atom's endpoints would be at distance <= 2,
not 4; 1 support + 2 atoms: parity contradiction). The counts are numerically
identical either way (2,299).

### Corollary 13 (`cor:t4:closure`) — **CONFIRMED**
Pure modus ponens from Lemma 11 (covered => <= 14 vertices) and Theorem 12(i)
(all windows at 15). The graph-level transfer is correctly assembled: Lemma 2
gives the circuit; Lemma 9 turns crossing stars into F-stars (so common crossing
neighbours become common F-neighbours and deg_F = 4); coverage transfers because
B-rows of the atoms coincide with F-rows. Matches the ledger fact
(CLAUDE_TO_CODEX.md 2026-07-11T22:20:49Z; LOOP_STATE.md TICK-98).

### Proposition 14 (`prop:t4:swapgeometry`) — **CONFIRMED with one provenance caveat**
The Lean statement (`live_middle_swap_has_cross_outer`, source SHA recomputed =
3DFF7897..., match) proves exactly the adjacency and distinctness content: blue
a-x, x-m, x-v, m-y, v-y, y-b, and a,b outside {v,m}, x != y. The distance-four
part of the proposition is definitional (the rows are rows of one atom), so the
"kernel-checked" attribution is fair, though a reader could wish the sentence
said the Lean lemma covers the adjacency/distinctness core. The graph-level
exhaustion replayed PASS with the exact multiplicities and SHA.
**Caveat**: the axiom claim "[propext, Quot.sound]" for this module traces to a
single source (Codex-side REPORT.md / R45 gate header). The session ledger
records the Claude-side rebuild as green (rc=0) but the axiom probe as *queued*
(22:20:49Z item (ii): "axiom probe queued but source claims [propext,Quot.sound]"),
and no later completed probe is recorded anywhere. The build cache
(`tmp/codex_r35_graph_adapter_verify/deps`) no longer exists, so the probe cannot
be cheaply rerun. Impact is low (Proposition 14 is an explicitly redundant
confirmation of Theorem 12(iii), which is dual-verified), but the paper states
the axiom set as unqualified fact.

### Remark 15 (`rem:t4:nearmiss`) — **CONFIRMED** (as corroboration-only)
Catalogue counts (10/11 none; 12 max ten pairs; 13: 280 graphs, zero circuits;
14: 455 graphs, zero covered double stars), the exact distance-four criterion
(Q_L)_{uv}=0<(Q_L^2)_{uv} (which I checked is mathematically correct), the
near-miss invariants (parts, owners 0/1, shared neighbours {7,8}, shared
partners {3,5,6}, shared terminals {3,13},{5,13},{6,13}, budget edges
{2,11},{4,9}, 864 selections, local failure mode) — all match R45 §§3,5–6 and
the gate header word for word. The single-implementation status and
corroboration-only role are stated in the text, and the closure demonstrably
does not use it. The non-reproduction of R45's session-internal eqs (13)/(14)
is honest and correct. Note the checker 4644e5ab itself is not in the repo; the
remark correctly restricts itself to the invariants recorded in the archived
R45 text.

### Remark 16 (`rem:t4:abstract`) — **CONFIRMED** (existence fully re-verified); one wording nit
I regenerated the artifact with the archived search harness — it hits at seed 0,
step 0, and the canonical SHA equals 5b386cd9... exactly; the independent
verifier passes (Hall on all 65,534 proper subsets, worst proper defect 0, min
edge degree 2, deficiency one, forced shared tail). So the load-bearing claim
(support-cardinality axioms alone cannot close the window) is verified.
Wording nit: "Its supports are not realized as geodesics of any one graph" is
stated as bare fact; REPORT says only that a realization was never supplied. The
census corroborates the claim for window-shaped realizations (I checked: none of
the 576 windows has all sixteen footprints of size four — the distribution is
{4: 6578, 6: 2638} — so the all-4-uniform artifact matches no census survivor),
but a realization violating the two-common-neighbour owner filter is not
formally excluded by the census. Suggest "have not been realized" or a
census-scoped statement.

### Verification-record paragraph — **CONFIRMED** with one phrasing caveat
All verdict strings, hashes, engine attributions ("different graph6 decoders,
shortest-path engines, and matching algorithms") and the no-floating-point claim
check out against the scripts (all integer/set/bitmask arithmetic; NetworkX
matching is combinatorial). The session-audit replay claim matches the 21:59:36Z
ledger entry. The formalization-debt sentence is honest and matches R45 §7–8.
Caveat: "two acceptance paths with no shared code" — both paths invoke the same
`geng.exe` binary as generator (the verifier reruns geng without residue
splitting). The processing code is indeed disjoint, but the exhaustive
*generation* layer is a single (standard, McKay–Piperno) tool on both paths; the
phrase would be more accurate as "no shared code beyond the nauty generator".
Also, the sentence "emitted three canonical JSON artifacts" is followed by a
five-entry JSON list; the last two (cross-outer, abstract circuit) are
verification-path artifacts, not census emissions — presentational only.

### Remark 17 (`rem:t4:scope`) — **CONFIRMED**
Margins 7/4 from the table; infeasibility figure matches the measured
194.6M >= 1.9e8 at n=16, 24 edges (R45 gate header; LOOP_STATE TICK-98).

### Excluded-claims list — **CONFIRMED** (all seven exclusions honored)
Grep of the .tex finds no occurrence of 83b1ee2f, A8D39A65/OwnerStarDualHall,
the ambient restriction, the profile-conditioned zero count, or any t=5
computational claim. The 83b1ee2f exclusion is justified: it appears in the
21:59:36Z ledger line with no identifiable artifact. The A8D39A65 exclusion is
justified: the ledger shows "acknowledged, queued for rebuild" and no
gate-accepted rebuild. The r=4 retraction history matches REPORT's audit note,
and the section indeed uses only the r-independent gates.

### LaTeX / compile check — **CONFIRMED** (static; no TeX engine on this machine)
All 34 environments balanced and correctly nested; inline math \( \) balanced
(436/436); display math balanced; brace depth 0 throughout. Every command used
is either standard LaTeX/amsmath/booktabs/enumitem or defined in the companion
preamble (\bip, \supp; \texorpdfstring is safe — the companion loads hyperref;
theorem environments theorem/proposition/lemma/corollary/definition/remark all
exist in the companion's numbering setup). All 14 \ref targets resolve to local
labels. The three bibliography keys are declared for the assembler in the header
comment. No compile blocker found.

---

## Issues ranked

1. **(provenance, low mathematical impact)** Proposition 14's axiom attestation
   for LiveMiddleSwapCrossOuter (3DFF7897): "axioms exactly propext, Quot.sound"
   is single-source (Codex REPORT); the session gate's own probe is recorded as
   queued and never completed, and the Lean build cache needed to rerun it is
   gone. Recommend: rebuild + probe once before submission, or soften to "source
   records axioms [propext, Quot.sound]". The closure itself is unaffected
   (Theorem 12(iii) is dual-verified computationally).
2. (wording) "two acceptance paths with no shared code" — both paths share the
   nauty geng generator.
3. (wording) Remark 16: "are not realized" stated as fact where the archive
   supports "have not been realized" (census corroborates the window-shaped
   case; I verified no census window is all-4-uniform).
4. (presentational) "three canonical JSON artifacts" heads a five-artifact list.

No MISMATCH and no GAP verdicts. Every proof marked "proved" in the manifest is
complete as written; every number, hash, verdict string, and Lean source hash
checked matches its archive; the entire census pipeline and all five artifacts
were reproduced bit-exactly on this machine today.
