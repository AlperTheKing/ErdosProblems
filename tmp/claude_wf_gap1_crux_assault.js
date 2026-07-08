export const meta = {
  name: 'gap1-crux-assault',
  description: 'Exhaustive multi-angle adversarial assault on the Erdos #23 gap#1 impure-balanced-neutral-lens crux (BalancedNeutralTheta_book_or_reducible): prove it, refute it with a decisive counter-pattern, or rigorously sharpen it',
  phases: [
    { title: 'Ground', detail: 'canonical precise crux statement + machine-usable constraint list + exact-checkable hooks' },
    { title: 'Attack', detail: '9 diverse independent angles: monovariant, direct-reducibility, reducedness-forbids, spectral, discharging/LP-dual, refutation-construction, finite-classification, entropy/probabilistic, novel' },
    { title: 'Verify', detail: 'adversarial skeptics per live candidate: correctness / constraint-validity / exact-recompute' },
    { title: 'Synthesize', detail: 'consolidate survivors into proof / decisive obstruction / sharpened open, with the next concrete step' },
  ],
}

const REPO = 'E:/Projects/ErdosProblems'

const FILES = `Working dir = repo root ${REPO}. READ FIRST: problems/23/writeup/GAP1_IMPURE_LENS_ESCALATION_BRIEF.md (self-contained crux handoff with full definitions, dead-ends, and 4 untried angles). Also available: problems/23/writeup/GAP1_FULLSUPPORT_REDUCTION_GPTPRO.md (the full GPT-Pro archive; replies 27-29 are the impure lens). Compiled Lean base case (the crux reduces the general case to THIS, already proven): problems/23/lean/Erdos23Delta0/{Ell5CSReduction,PathRigidity,Ell5AtomBase,CageSuperadditivity}.lean. Exact gate examples (Python/Fraction) to mimic: problems/23/writeup/_claude_residual_hall_gate.py, _claude_hpair_rigidity_gate.py. You may Read files and write+run Python (use Fraction, NEVER float) to test ABSTRACT configurations for internal consistency.`

const CRUX = `THE OPEN THEOREM (gap#1 crux): "BalancedNeutralTheta_book_or_reducible".
SETTING: a REDUCED, Gamma-minimal, MINIMAL-NEGATIVE-BALANCE ("deficient", Gamma>N^2) cage of a triangle-free MAXIMUM cut. Two ell=5 rows (bad edges) e,f whose shortest blue-geodesic supports form a Gamma-NEUTRAL (the recut swapping the lens W changes Gamma by |deltaM(W)|-|deltaB(W)| = 0), NON-BOOK theta with doors d0,d1 and lens component W = the component of B minus the doors between them.
CLAIM to prove or refute: either (BOOK) the theta is C5-book-parallel (the two rows are layer-compatible about the doors, giving local density |B_C|=4|M_C|), OR (REDUCIBLE) W admits a NONNEGATIVE PRUNABLE SUBCAGE, which contradicts minimality.
THE WALL = the IMPURE lens sub-case: W owns EXTRA atoms beyond e,f (OwnedPositiveSurplus(W)>0), so the obvious prunable subcage is NOT immediately nonnegative. The PURE lens (W owns only e,f) is already proven reducible. Reduction: crux => P4SharedSupportDichotomy => Ell5SupportExpansion => Gamma<=N^2 => beta<=N^2/25.

KEY DEFINITIONS: ell(e)=blue-dist(u,v)+1>=5 (triangle-free forces this); Gamma_C=sum over rows of ell^2; reserve=N^2-Gamma; deficient <=> reserve<0; MINIMAL = no proper prunable subcage has negative balance; a recut/switch of a set W flips the sides of W and changes Gamma by |deltaM(W)|-|deltaB(W)|; NEUTRAL = that change is 0; BOOK vs non-book = whether the two rows are layer-compatible about the doors.

*** CRITICAL COUNTERFACTUAL WARNING *** No deficient cage (Gamma>N^2) exists in ANY real triangle-free graph -- that IS the conjecture being proven. So the impure lens is a COUNTERFACTUAL object: it CANNOT be exhibited or refuted by searching real graphs (every empirical battery shows feasibility everywhere). You MUST reason DEDUCTIVELY in the hypothetical deficient-cage world. HOWEVER: you CAN and SHOULD build ABSTRACT configurations (a theta with two ell=5 rows, doors, a lens W, owned atoms, with explicit lengths/incidences) and test them with EXACT arithmetic for internal consistency: does a config satisfy all the constraints (Gamma-neutral, non-book, has extra owned atoms) simultaneously? Does a proposed monovariant actually strictly decrease on such abstract configs? Does a proposed prunable subcage actually have nonnegative balance? This abstract testing is legitimate and decisive -- it is NOT the same as searching real graphs.

DEAD ENDS -- do NOT re-tread (each already refuted with an exact falsifying fact):
 (1) SWITCH PREMISE (over-congested => switch exists): counterfactual, 0/71910; odd cycle C_N is rigid but is a base leaf.
 (2) PATH-ROUTING: reduces to the same open expansion inequality.
 (3) CUT-COVER (a separating cut per atom with deltaB subset E_short): FALSIFIED exactly -- infeasible with ALL 2^n cuts on 19 N=11 comps while Hall holds; atom (5,9) has no separating cut. Strictly STRONGER than Hall.
 (4) m*Q<=T^2 (Cauchy-Schwarz sufficient condition): SUFFICIENT but NOT NECESSARY -- a sunflower violates m*Q<=T^2 while Hall still holds. Cannot be the theorem.
 (5) S1ThetaPattern via Gamma-DECREASE: FALSE for balanced ell=5 -- the theta is Gamma-NEUTRAL (5^2+5^2 -> 5^2+5^2, verified). The -(4L+4) drop was only for UNEQUAL {L,L+2}. Any monovariant MUST be non-Gamma.
 (6) MEDIUM-BAND BCL BYPASS (deficient => high edge-density => Balogh-Clemen-Lidicky closes it): REJECTED -- deficiency is LENGTH-SQUARE density (sum ell^2), NOT edge-density (a long odd cycle has Gamma=n^2 with O(n) edges); local-to-global gap; the required lemmas are as hard as the original.`

const GROUND_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    canonical_statement: { type: 'string', description: 'The crux stated precisely and self-consistently, resolving any ambiguity in the informal statement.' },
    constraint_list: { type: 'array', items: { type: 'string' }, description: 'The EXACT list of constraints an impure-lens configuration must satisfy simultaneously. Each an explicit, checkable predicate.' },
    key_subtleties: { type: 'array', items: { type: 'string' }, description: 'Subtle points, hidden assumptions, or places the informal statement could be misread.' },
    exact_checkable_hooks: { type: 'array', items: { type: 'string' }, description: 'Specific arithmetic/combinatorial facts that CAN be exact-tested on abstract configs.' },
    minimal_abstract_model: { type: 'string', description: 'A concrete minimal data model for an abstract cage/theta/lens sufficient to instantiate and test in Python with Fraction.' }
  },
  required: ['canonical_statement','constraint_list','key_subtleties','exact_checkable_hooks','minimal_abstract_model']
}

const ANGLES = [
  { key: 'monovariant', title: 'Non-Gamma monovariant (well-founded descent)',
    task: 'Construct an EXPLICIT non-Gamma potential Phi (candidates: lexicographic (Gamma, BookDefect, number of order-inversions, sum of owned-surplus, ...)) that STRICTLY DECREASES under the neutral recut/2-switch that turns an order-inverted non-book pair into a book pair, and is bounded below. Prove well-founded descent => the process terminates at a BOOK configuration (so non-book => reducible via the descent). The known objection: GPT-Pro found a Phi that decreases LOCALLY on the pure two-row lens but can INCREASE elsewhere, so it can cycle. Your job: find a Phi that provably decreases GLOBALLY (or prove none can, ruling this angle out). Test candidate Phi on abstract impure-lens configs with exact arithmetic: does the recut strictly drop Phi even with extra owned atoms in W?' },
  { key: 'reducibility', title: 'Direct reducibility of the impure lens',
    task: 'Show that the EXTRA owned atoms in the lens W contribute NONNEGATIVE surplus that the prune absorbs, so the prunable subcage B-after-W is nonnegative after all. Compute EXACTLY the balance of pruning W: Balance(B)-Balance(B-after-W) = (door/length change) + (owned-surplus of W). The neutral door balance gives 0 from |deltaM(W)|-|deltaB(W)|; determine whether OwnedPositiveSurplus(W)>=0 is FORCED (each owned atom has ell>=5 so ell^2-25>=0, i.e. positive surplus, which should HELP not hurt). Resolve GPT-Pro angle B (unresolved for the impure case). Build abstract impure configs and compute the prune balance with Fraction to confirm/refute nonnegativity.' },
  { key: 'reducedness-forbids', title: 'Reducedness forbids the impure lens (vacuity)',
    task: 'Prove that the REDUCED + MINIMAL-NEGATIVE-BALANCE hypotheses FORCE W to own nothing extra -- i.e. the impure case is VACUOUS. Intuition: an extra owned atom sitting inside W with its own positive surplus would itself constitute (or be part of) a proper prunable subcage with negative balance, contradicting minimality; or reducedness (already-reduced shell) excludes such extra ownership. Make this precise: state exactly what reduced and minimal-neg-balance forbid, and show an extra owned atom violates one of them. Resolve GPT-Pro angle C (unresolved). Test on abstract configs: try to build a config that is reduced + minimal-neg-balance + has an extra owned atom; if impossible (constraints conflict), that PROVES vacuity.' },
  { key: 'spectral', title: 'Induced P3:P4-ratio / signless-Laplacian spectral bound',
    task: 'Use the spectral method of arXiv 2204.00093 (spectrum of triangle-free graphs, signless-Laplacian q_n <= 15n/94 via induced-P3:P4 ratio). The ell=5 geodesic is an induced P4; its sub-paths are P3. Derive a spectral/ratio bound on the shortest-geodesic support hypergraph that yields the support-expansion |E_short(S)|>=|S| (or Gamma<=N^2) DIRECTLY, bypassing the local theta lens entirely. Assess feasibility honestly: does the ratio bound actually imply the needed expansion, or does it fall short? This is a fresh untried angle.' },
  { key: 'discharging', title: 'Global discharging / LP-duality bypassing the lens',
    task: 'Design a GLOBAL charging/discharging or LP-duality argument that proves Gamma<=N^2 (equivalently the support-expansion) DIRECTLY, without the local theta dichotomy at all. Assign charges to bad edges / cut edges / vertices; discharge so every vertex/edge ends nonnegative and the total gives Gamma<=N^2. The dual of the single-commodity Gale-Hoffman expansion is a fractional assignment -- find a valid one. Contrast with the FAILED cut-cover (dead end 3, which was strictly stronger than Hall): your assignment must be exactly Hall-tight, not stronger. Test any explicit charging scheme on the census Gamma-min cages with exact arithmetic (these DO exist as real graphs -- the support-expansion holds on all 71910; a valid global charging must certify it).' },
  { key: 'refutation', title: 'REFUTATION: construct a decisive impure-lens counter-pattern',
    task: 'Try HARD to CONSTRUCT an ABSTRACT impure-lens configuration that satisfies ALL the crux constraints simultaneously (Gamma-neutral theta of two ell=5 rows, NON-book, inside a reduced minimal-negative-balance deficient cage, with EXTRA owned atoms in W) yet has NO nonnegative prunable subcage AND is not book. If such a config exists and is INTERNALLY CONSISTENT (verify every constraint with exact Fraction arithmetic), it is the DECISIVE OBSTRUCTION: the crux is FALSE and this is the exact counter-pattern to Ell5SupportExpansion. BE RIGOROUS about realizability of the ABSTRACT deficient cage (you are NOT searching real graphs -- real graphs have no deficient cages; you are testing whether the abstract constraint system is satisfiable). If you find the constraints are UNSATISFIABLE (no such config exists), that is strong evidence the crux is TRUE (and overlaps reducedness-forbids). Report either the explicit counter-pattern (with all constraints exact-verified) or the precise reason the constraints conflict.' },
  { key: 'classification', title: 'Finite classification of balanced-neutral non-book thetas',
    task: 'Precisely and EXHAUSTIVELY classify ALL balanced-neutral non-book thetas formed by two ell=5 rows: the door positions, lens length, crossing pattern, and owned-atom placements form a FINITE combinatorial space (both rows have length-4 geodesics = 5 vertices). Enumerate the finitely many structural types with exact arithmetic. For EACH type, determine book-or-reducible. If every type is book or reducible, the crux is PROVEN by finite case analysis. Identify precisely which type(s), if any, are the stubborn impure case.' },
  { key: 'entropy', title: 'Entropy / probabilistic / counting argument',
    task: 'Attempt a probabilistic or entropy or double-counting argument for the support-expansion |E_short(S)|>=|S| (single-commodity Hall) or directly Gamma<=N^2, that sidesteps the theta lens. E.g., a random cut / random shift argument, an entropy-compression on the geodesic supports, or a clever double count of (atom, support-edge) incidences using girth-4 + max-cut structure. Note m*Q<=T^2 (Cauchy-Schwarz, dead end 4) is sufficient-not-necessary; find the RIGHT weighting/measure that is exactly Hall-tight. Test any counting identity on census cages with exact arithmetic.' },
  { key: 'novel', title: 'Novel angle not in the above or the dead-end list',
    task: 'Find a GENUINELY NOVEL angle not covered by the other 8 attacks and not in the dead-end list. Consider: (a) local-to-global stability/compactness; (b) a connection to a known extremal theorem (flag algebras applied to the local neighborhood, Ramsey-type, or the C5[t] extremal structure); (c) reformulating the deficient cage as a violated LP and extracting a Farkas certificate; (d) an algebraic/matroid/polytope view of the geodesic support hypergraph; (e) induction on cage size with a cleverly-chosen reduction different from the prune. Propose the sharpest new idea and carry it as far as you rigorously can. Be honest if it does not pan out.' },
]

const ATTACK_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    angle: { type: 'string' },
    verdict: { type: 'string', enum: ['proof_candidate','partial','refutation_candidate','dead_end'] },
    summary: { type: 'string', description: '1-2 sentence result of this angle.' },
    key_construction: { type: 'string', description: 'The precise object produced (monovariant Phi / prune balance / vacuity argument / counter-pattern config / charging scheme / classification), stated exactly enough to be independently checked.' },
    argument: { type: 'string', description: 'The proof sketch or refutation with its key logical steps, in full.' },
    checkable_claims: { type: 'array', items: { type: 'string' }, description: 'Exact-verifiable sub-claims for the adversarial verify phase to test.' },
    exact_test_done: { type: 'string', description: 'What exact (Fraction) computation you actually ran on abstract or census configs, and the numeric result. none if you ran none (say why).' },
    honest_gaps: { type: 'array', items: { type: 'string' }, description: 'What is NOT proven, where it could fail, remaining hand-waves.' },
    confidence: { type: 'number', description: '0-100 confidence this angle closes (or decisively refutes) the crux.' }
  },
  required: ['angle','verdict','summary','key_construction','argument','checkable_claims','exact_test_done','honest_gaps','confidence']
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    target_angle: { type: 'string' },
    lens: { type: 'string' },
    survives: { type: 'boolean', description: 'Does the candidate survive THIS refutation attempt?' },
    decisive_flaw: { type: 'string', description: 'If broken: the specific fatal flaw. If survives: none found -- checked X, Y, Z.' },
    constraint_or_logic_check: { type: 'string', description: 'For refutation candidates: does the constructed config satisfy ALL constraints? which fail? For proofs: does the argument correctly cover the IMPURE case (not just pure)? does the monovariant actually decrease globally?' },
    exact_recheck: { type: 'string', description: 'Any exact Fraction computation you ran to check, and the result. none if not applicable.' },
    severity: { type: 'string', enum: ['fatal','serious','minor','none'] }
  },
  required: ['target_angle','lens','survives','decisive_flaw','constraint_or_logic_check','exact_recheck','severity']
}

const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    outcome: { type: 'string', enum: ['proof_found','decisive_obstruction','sharpened_open','no_progress'] },
    headline: { type: 'string' },
    surviving_proof_approaches: { type: 'array', items: { type: 'string' } },
    surviving_refutations: { type: 'array', items: { type: 'string' } },
    the_decisive_finding: { type: 'string', description: 'The proof approach that survived, OR the exact counter-pattern, OR the sharpened crux -- the single most important takeaway, stated precisely.' },
    exact_verification_status: { type: 'string', description: 'What was exact-verified vs still asserted.' },
    next_concrete_step: { type: 'string', description: 'Formalize which lemma in Lean, or document which obstruction, or escalate with exactly what the stronger model needs next.' },
    confidence: { type: 'number' }
  },
  required: ['outcome','headline','surviving_proof_approaches','surviving_refutations','the_decisive_finding','exact_verification_status','next_concrete_step','confidence']
}

// ---- Phase 1: GROUND ----
phase('Ground')
const ground = await agent(
  `${FILES}\n\n${CRUX}\n\nTASK: Read the escalation brief first, then produce the CANONICAL, precise, self-consistent statement of this crux plus the EXACT machine-usable constraint list an impure-lens configuration must satisfy, the key subtleties/hidden assumptions, the exact-checkable hooks, and a concrete minimal abstract data model (vertices/sides/doors/owned-atoms/lengths) that later agents can instantiate and test in Python with Fraction. Be rigorous: the whole attack depends on attacking the RIGHT problem. Return the schema.`,
  { label: 'ground:crux', schema: GROUND_SCHEMA, effort: 'xhigh' }
)
const groundStr = JSON.stringify(ground)
log('Ground complete: canonical statement + ' + (ground.constraint_list ? ground.constraint_list.length : 0) + ' constraints + abstract model ready. Launching 9-angle attack.')

// ---- Phase 2+3: ATTACK -> adversarial VERIFY, pipelined per angle ----
const LENSES = [
  { k: 'correctness', instr: 'Attack the LOGIC. Find a gap, a non-sequitur, an unjustified step, or a case the argument silently skips. For a proof candidate: does each step actually follow? For a refutation: is the counter-pattern logically a genuine counterexample?' },
  { k: 'constraint-validity', instr: 'Attack the CONSTRAINTS. For a refutation candidate: does the constructed config REALLY satisfy EVERY crux constraint simultaneously (Gamma-neutral AND non-book AND reduced AND minimal-neg-balance AND extra owned atoms)? Recompute each. For a proof candidate: does it correctly handle the IMPURE case (extra owned atoms) and not just the pure lens? Does a claimed monovariant decrease GLOBALLY, not just locally?' },
  { k: 'exact-recompute', instr: 'Attack with EXACT ARITHMETIC. Actually write and run Python with Fraction to recompute every numeric claim (balance of the prune, the neutral condition |deltaM|-|deltaB|, ell^2 sums, monovariant values on abstract configs, census-cage checks). Report the exact numbers. A single exact mismatch is fatal. If nothing is numerically checkable, say so.' },
]

const results = await pipeline(
  ANGLES,
  (a) => agent(
    `${FILES}\n\n${CRUX}\n\nGROUNDING (canonical statement + constraints + abstract model): ${groundStr}\n\nYOUR ANGLE: ${a.title}\nTASK: ${a.task}\n\nBe maximally rigorous and exhaustive (ultracode: token cost is not a constraint). Where testable, WRITE AND RUN exact Python (Fraction, never float) on abstract configs or census cages to support or refute your claims. Do NOT re-tread the 6 dead ends. Be brutally honest about gaps -- a false proof is worse than an honest partial. Return the schema.`,
    { label: `attack:${a.key}`, phase: 'Attack', schema: ATTACK_SCHEMA, effort: 'xhigh' }
  ),
  (atk, a) => (atk && atk.verdict !== 'dead_end')
    ? parallel(LENSES.map(L => () =>
        agent(
          `${FILES}\n\n${CRUX}\n\nGROUNDING: ${groundStr}\n\nA candidate result for angle "${a.title}" is under adversarial review. CANDIDATE (verdict=${atk.verdict}, confidence=${atk.confidence}):\nsummary: ${atk.summary}\nkey_construction: ${atk.key_construction}\nargument: ${atk.argument}\ncheckable_claims: ${JSON.stringify(atk.checkable_claims)}\nexact_test_done: ${atk.exact_test_done}\nhonest_gaps: ${JSON.stringify(atk.honest_gaps)}\n\nYOUR REFUTATION LENS = ${L.k}: ${L.instr}\nDefault to survives=false if you find ANY fatal issue; only survives=true if you genuinely cannot break it after real effort. Return the schema.`,
          { label: `verify:${a.key}:${L.k}`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'high' }
        )
      )).then(vs => ({ angle: a.key, title: a.title, attack: atk, verdicts: vs.filter(Boolean) }))
    : { angle: a.key, title: a.title, attack: atk, verdicts: [] }
)

const clean = results.filter(Boolean)
const live = clean.filter(r => r.attack && r.attack.verdict !== 'dead_end')
const survivors = live.filter(r => {
  const vs = r.verdicts || []
  const fatal = vs.filter(v => v && v.severity === 'fatal').length
  const survivesVotes = vs.filter(v => v && v.survives).length
  return fatal === 0 && survivesVotes >= 2
})
log(`Attack+verify complete: ${live.length} live candidates, ${survivors.length} survived adversarial review (0 fatal + >=2/3 survive votes).`)

// ---- Phase 4: SYNTHESIZE ----
phase('Synthesize')
const digest = clean.map(r => ({
  angle: r.angle, verdict: r.attack ? r.attack.verdict : 'null', confidence: r.attack ? r.attack.confidence : 0,
  summary: r.attack ? r.attack.summary : '', key_construction: r.attack ? r.attack.key_construction : '',
  survived: survivors.some(s => s.angle === r.angle),
  verdicts: (r.verdicts || []).map(v => ({ lens: v.lens, survives: v.survives, severity: v.severity, flaw: v.decisive_flaw }))
}))
const synth = await agent(
  `${FILES}\n\n${CRUX}\n\nGROUNDING: ${groundStr}\n\nALL 9 ATTACK RESULTS + THEIR ADVERSARIAL VERDICTS (digest):\n${JSON.stringify(digest, null, 1)}\n\nFULL surviving candidates (attacks with 0 fatal flaws and >=2/3 survive votes): ${JSON.stringify(survivors.map(s => s.attack), null, 1)}\n\nTASK: Synthesize the DECISIVE outcome. Determine honestly whether (a) a proof approach survived adversarial pressure (=> proof_found; specify the exact lemma to formalize in Lean and how it discharges the impure case), (b) a refutation with a fully-constraint-verified counter-pattern survived (=> decisive_obstruction; give the exact counter-pattern -- this would be the falsifier the goal asks for), (c) the crux is meaningfully SHARPENED but still open (=> sharpened_open; state the reduced sub-obstruction and exactly what the stronger model needs next), or (d) no_progress. Do NOT overclaim: a surviving proof approach must genuinely cover the IMPURE case. Cross-check the exact-verification status. Give the single most important takeaway and the next concrete step. Return the schema.`,
  { label: 'synthesize:crux', schema: SYNTH_SCHEMA, effort: 'xhigh' }
)

return { outcome: synth.outcome, headline: synth.headline, synth, survivors: survivors.map(s => s.angle), ground, allResults: digest }
