export const meta = {
  name: 'sse-fullbankhall-assault',
  description: 'Exhaustive multi-angle assault on the DEFINITIVE gap#1 core ShortestSupportExpansion / FullBankHall: prove it, or construct a DEFICIENT counterpattern (the decisive falsifier), or rigorously sharpen',
  phases: [
    { title: 'Ground', detail: 'precise ShortestSupportExpansion/FullBankHall statement + exact bank defs + deficient-cage constraint system' },
    { title: 'Attack', detail: '8 angles: b-matching Hall, sunflower-free, LP-Farkas, stability, spectral, DEFICIENT-refutation, entropy-counting, novel' },
    { title: 'Verify', detail: 'adversarial skeptics per candidate: correctness / exact-recompute / deficient-cage-consistency' },
    { title: 'Synthesize', detail: 'proof / decisive DEFICIENT falsifier / sharpened-open + next concrete step' },
  ],
}

const REPO = 'E:/Projects/ErdosProblems'
const FILES = `Working dir = ${REPO}. READ FIRST: problems/23/writeup/GAP1_SHORTESTSUPPORTEXPANSION_ESCALATION.md (self-contained: the theorem, compiled scaffolding, full dead-end map, untried angles). Also: GAP1_LEDGER_SEPARATION_GPTPRO.md (the escape-closure dichotomy that reduced gap#1 to this). Compiled Lean (axiom-clean): problems/23/lean/Erdos23Delta0/{NeutralLensLedger,MaxCutVertexIneq,Ell5AtomBase,PathRigidity,CageSuperadditivity}.lean. Exact gate infra to reuse: problems/23/writeup/_claude_residual_hall_gate.py (residuals, geos_paths, k2_components), _h.py (maxcut_all, geng, gmin). You may Read files and write+run Python with Fraction (NEVER float).`

const CORE = `THE THEOREM (definitive gap#1 core): ShortestSupportExpansion == FullBankHall.
ShortestSupportExpansion: in a REDUCED triangle-free Gamma-minimal MAXIMUM cut, for every set S of ell=5 atoms (bad edges at blue-distance 4) of a K2-component, |S| <= |E_short(S)|, where E_short(S) = union over atoms in S of the cut edges of ALL their shortest blue geodesics.
FullBankHall (Hall/b-matching form): for all A subset of OwnedAtoms(C), Demand(A) <= DoorCap(A)+VertexSlackCap(A)+C5BaseCap(A)+PruneCap(A), where Demand(A)=sum_{a in A}(ell(a)^2-25); DoorCap=25*sigma-neighborhood (sigma=#cutedges-m); VertexSlackCap=support-constrained sum max(0,N-T(v)); C5BaseCap=independent base-density tokens ONLY (single full-support leaves from ell<=|V_D|); PruneCap=balances of strict proper descendant subcages. *** NEVER use the top cage's own reserve eta_C=N^2/25-m (that begs the conjecture). *** FullBankHall(C) <=> Balance(C)>=0 => Gamma=sum ell^2 <= N^2 => beta<=N^2/25 (Erdos #23 delta=0).

WHY THIS IS THE CORE: the whole gap#1 reduces here via the escape-closure dichotomy (proper closure => killed by compiled minimality no_ledgerSep_in_minNeg; FULL closure => this theorem). GPT-Pro proved NO local shortcut forces the closure proper (not maximality, not Gamma-minimality, not deficiency, not reducedness). So this is the irreducible core, = the ORIGINAL difficulty, precisely stated.

*** COUNTERFACTUAL WARNING *** The binding case is a DEFICIENT cage (Gamma>N^2), which exists in NO real triangle-free graph (that IS the conjecture). Empirical batteries show feasibility on 71910 cages, 0 fail, precisely because no gate reaches the binding regime. REASON DEDUCTIVELY. You CAN build ABSTRACT configs and test internal consistency with exact Fraction arithmetic; real-graph search is futile.

DEAD ENDS -- do NOT re-tread (all refuted with exact facts): surplus-sign nonneg (sign error: Surplus is demand, lowers Balance); NoEscapingAtomAtMaxCut / direct-maximality (FALSE, exact 11-vtx max-cut escaping atom with alternate outside geodesic); deficiency/minimality-forces-closure-proper (FALSE, full closure genuinely live, D=C realized at a max cut); switch premise (counterfactual 0/71910); cut-cover (FALSIFIED, strictly stronger than Hall); m*Q<=T^2 (sufficient not necessary, sunflower breaks it); S1ThetaPattern via Gamma-decrease (FALSE, balanced ell=5 is Gamma-neutral); medium-band BCL bypass (length-square density != edge-density).`

const GROUND_SCHEMA = { type:'object', additionalProperties:false, properties:{
  statement:{type:'string'}, bank_defs:{type:'string', description:'exact definitions of Demand + the 4 bank caps, machine-usable'},
  deficient_constraint_system:{type:'array', items:{type:'string'}, description:'the exact constraints an abstract DEFICIENT minimal-neg cage violating FullBankHall must satisfy (for the refutation angle)'},
  exact_hooks:{type:'array', items:{type:'string'}}, subtleties:{type:'array', items:{type:'string'}} },
  required:['statement','bank_defs','deficient_constraint_system','exact_hooks','subtleties'] }

const ANGLES = [
  { key:'bmatching-hall', title:'Full mixed-bank Hall via fractional b-matching / max-flow',
    task:'Prove Demand(A) <= sum of bank caps by constructing an explicit FRACTIONAL MATCHING / max-flow from atoms (demand ell^2-25) to the bank tokens (Door=25/interior-cut-edge, vertexSlack max(0,N-T(v)), C5-base, Prune), respecting the SUPPORT restriction (an atom routes only to banks its shortest support touches). Use girth-4 + max-cut (MaxCutVertexIneq |deltaM(U)|<=|deltaB(U)|) to bound overlaps. Find the exact Hall-tight weighting (NOT m*Q<=T^2, NOT cut-cover). Validate the flow feasibility on census Gamma-min cages exactly (Fraction).' },
  { key:'sunflower-free', title:'Sunflower-freeness of the shortest-support hypergraph',
    task:'Show the shortest-geodesic support hypergraph (atoms -> their 4-edge supports) is SUNFLOWER-FREE / has bounded core multiplicity, forced by triangle-free + max-cut, and that this yields |E_short(S)|>=|S| directly. Precisely: bound the number of atoms whose supports share a common cut edge (column degree d(c)), and show sum d(c)<=... gives the expansion. Test column-degree bounds on census cages exactly.' },
  { key:'lp-farkas', title:'Exact Farkas / LP-dual certificate for Gamma<=N^2',
    task:'Construct an explicit dual (Farkas) certificate proving the single-commodity Gale-Hoffman expansion / Gamma<=N^2 for triangle-free Gamma-min max cuts, WITHOUT the eta_C token. The dual is a fractional vertex/edge potential; find a valid one from the max-cut + girth-4 structure. Must be exactly Hall-tight (tight at C5[t]). Test the dual feasibility exactly on census cages + C5[t].' },
  { key:'stability', title:'Stability / compactness near the extremal',
    task:'Argue by stability: a cage that is near-deficient (Balance near 0, Gamma near N^2) must be structurally CLOSE to the extremal C5[t] (graphon/removal-lemma style), where the expansion is TIGHT but holds with equality. Then a strict deficiency (Gamma>N^2) is impossible by a compactness/continuity argument. Identify precisely what stability statement is needed and whether it is provable (or is itself the crux).' },
  { key:'spectral', title:'Signless-Laplacian / induced P3:P4 ratio (FullBankHall framing)',
    task:'Apply the spectral method (arXiv 2204.00093, signless-Laplacian, induced P3:P4 ratio) to the FullBankHall/support-hypergraph, not the whole graph. The ell=5 geodesic is an induced P4. Derive a spectral bound implying Demand(A)<=bank caps or |E_short(S)|>=|S|. Assess honestly whether it reaches the bound or falls short (prior workflow found spectral ||T||^2<=N*Gamma DEAD via two-lane L=12 sum R[v]=-540<0 -- avoid that dead form; try the RATIO bound instead).' },
  { key:'deficient-refutation', title:'RIGOROUS refutation: construct a DEFICIENT counterpattern (the decisive falsifier)',
    task:'Try HARD to construct an ABSTRACT DEFICIENT (Gamma>N^2) reduced minimal-negative-balance triangle-free max-cut cage whose escape closure is FULL and that VIOLATES FullBankHall (some A with Demand(A) > sum bank caps). This is the /goal decisive falsifier. Build the abstract cage (vertices/sides/atoms/lengths/banks) and verify EVERY constraint with exact Fraction: triangle-free, all bad ell>=5, MAX cut (|deltaM(U)|<=|deltaB(U)| for all U -- brute force), reduced, minimal-negative-balance, Gamma>N^2, full escape closure, and Demand(A)>caps. BE RIGOROUS: prior counterpatterns (11-vtx escaping atom) were NON-deficient (Gamma<N^2) hence consistent with delta=0 -- a DEFICIENT one would refute the conjecture. If the constraints are UNSATISFIABLE (cannot make it deficient while max+reduced+min-neg), that is strong evidence the theorem is TRUE -- report the precise obstruction to satisfiability.' },
  { key:'entropy-counting', title:'Entropy / double-counting with the right Hall-tight measure',
    task:'Double-count (atom, support-edge) incidences with a cleverly weighted measure that is exactly Hall-tight, or an entropy-compression on the geodesic supports, to prove |E_short(S)|>=|S|. The RIGHT measure is the open point (m*Q<=T^2 with uniform weight is sufficient-not-necessary; find the correct non-uniform one). Test any counting identity exactly on census cages.' },
  { key:'novel', title:'Novel angle',
    task:'A genuinely NEW angle not above and not in the dead-end list: e.g. matroid/polytope structure of the support hypergraph; a removal/regularity argument; induction on cage size with a non-prune reduction; a connection to a known max-cut / triangle-free extremal theorem. Carry the sharpest idea as far as rigor allows; be honest if it does not pan out.' },
]

const ATTACK_SCHEMA = { type:'object', additionalProperties:false, properties:{
  angle:{type:'string'}, verdict:{type:'string', enum:['proof_candidate','partial','refutation_candidate','dead_end']},
  summary:{type:'string'}, key_construction:{type:'string'}, argument:{type:'string'},
  checkable_claims:{type:'array', items:{type:'string'}}, exact_test_done:{type:'string'},
  honest_gaps:{type:'array', items:{type:'string'}}, confidence:{type:'number'} },
  required:['angle','verdict','summary','key_construction','argument','checkable_claims','exact_test_done','honest_gaps','confidence'] }

const VERDICT_SCHEMA = { type:'object', additionalProperties:false, properties:{
  target_angle:{type:'string'}, lens:{type:'string'}, survives:{type:'boolean'},
  decisive_flaw:{type:'string'}, check:{type:'string', description:'for refutation: is the DEFICIENT cage genuinely consistent (max+reduced+min-neg+Gamma>N^2) AND does it violate FullBankHall? recompute. for proof: does it cover the FULL closure / all A, not a special case?'},
  exact_recheck:{type:'string'}, severity:{type:'string', enum:['fatal','serious','minor','none']} },
  required:['target_angle','lens','survives','decisive_flaw','check','exact_recheck','severity'] }

const SYNTH_SCHEMA = { type:'object', additionalProperties:false, properties:{
  outcome:{type:'string', enum:['proof_found','decisive_deficient_falsifier','sharpened_open','no_progress']},
  headline:{type:'string'}, surviving_proofs:{type:'array', items:{type:'string'}}, surviving_refutations:{type:'array', items:{type:'string'}},
  decisive_finding:{type:'string'}, exact_verification_status:{type:'string'}, next_concrete_step:{type:'string'}, confidence:{type:'number'} },
  required:['outcome','headline','surviving_proofs','surviving_refutations','decisive_finding','exact_verification_status','next_concrete_step','confidence'] }

phase('Ground')
const ground = await agent(`${FILES}\n\n${CORE}\n\nTASK: Read the escalation brief, then produce the canonical precise statement of ShortestSupportExpansion/FullBankHall, the EXACT machine-usable bank definitions, the constraint system an abstract DEFICIENT counterpattern must satisfy (for the refutation angle), exact-checkable hooks, and subtleties. Return the schema.`,
  { label:'ground:sse', schema:GROUND_SCHEMA, effort:'xhigh' })
const g = JSON.stringify(ground)
log('Ground complete. Launching 8-angle assault on ShortestSupportExpansion/FullBankHall.')

const LENSES = [
  { k:'correctness', instr:'Attack the logic: find a gap, unjustified step, or a case (subset A, or a closure configuration) silently skipped.' },
  { k:'exact-recompute', instr:'Write+run Python with Fraction to recompute every numeric claim (flow feasibility, bank caps, Demand, column degrees, the deficient-cage constraints, census checks). A single exact mismatch is fatal.' },
  { k:'deficient-consistency', instr:'For a refutation candidate: does the abstract DEFICIENT cage satisfy ALL constraints simultaneously (triangle-free, all ell>=5, MAXIMUM cut by brute force, reduced, minimal-negative-balance, Gamma>N^2, and Demand(A)>caps)? Recompute each; a NON-deficient or non-max config is not a falsifier. For a proof: does it use the eta_C token illegitimately, or only cover non-deficient/real cases?' },
]

const results = await pipeline(ANGLES,
  (a) => agent(`${FILES}\n\n${CORE}\n\nGROUNDING: ${g}\n\nYOUR ANGLE: ${a.title}\nTASK: ${a.task}\n\nBe maximally rigorous and exhaustive (ultracode). WRITE+RUN exact Python (Fraction, never float) where testable. Do NOT re-tread the dead ends. Brutal honesty about gaps -- a false proof is worse than an honest partial. Return the schema.`,
    { label:`attack:${a.key}`, phase:'Attack', schema:ATTACK_SCHEMA, effort:'xhigh' }),
  (atk, a) => (atk && atk.verdict !== 'dead_end')
    ? parallel(LENSES.map(L => () => agent(`${FILES}\n\n${CORE}\n\nGROUNDING: ${g}\n\nCandidate for angle "${a.title}" (verdict=${atk.verdict}, conf=${atk.confidence}):\nsummary: ${atk.summary}\nkey_construction: ${atk.key_construction}\nargument: ${atk.argument}\ncheckable_claims: ${JSON.stringify(atk.checkable_claims)}\nexact_test_done: ${atk.exact_test_done}\nhonest_gaps: ${JSON.stringify(atk.honest_gaps)}\n\nYOUR REFUTATION LENS = ${L.k}: ${L.instr}\nDefault survives=false on any fatal issue; survives=true only if you genuinely cannot break it. Return the schema.`,
        { label:`verify:${a.key}:${L.k}`, phase:'Verify', schema:VERDICT_SCHEMA, effort:'high' })))
      .then(vs => ({ angle:a.key, title:a.title, attack:atk, verdicts:vs.filter(Boolean) }))
    : { angle:a.key, title:a.title, attack:atk, verdicts:[] })

const clean = results.filter(Boolean)
const live = clean.filter(r => r.attack && r.attack.verdict !== 'dead_end')
const survivors = live.filter(r => { const vs=r.verdicts||[]; return vs.filter(v=>v&&v.severity==='fatal').length===0 && vs.filter(v=>v&&v.survives).length>=2 })
log(`Attack+verify done: ${live.length} live, ${survivors.length} survived (0 fatal + >=2/3 survive).`)

phase('Synthesize')
const digest = clean.map(r => ({ angle:r.angle, verdict:r.attack?r.attack.verdict:'null', confidence:r.attack?r.attack.confidence:0, summary:r.attack?r.attack.summary:'', key_construction:r.attack?r.attack.key_construction:'', survived:survivors.some(s=>s.angle===r.angle), verdicts:(r.verdicts||[]).map(v=>({lens:v.lens,survives:v.survives,severity:v.severity,flaw:v.decisive_flaw,check:v.check})) }))
const synth = await agent(`${FILES}\n\n${CORE}\n\nGROUNDING: ${g}\n\nALL 8 ATTACK RESULTS + ADVERSARIAL VERDICTS:\n${JSON.stringify(digest,null,1)}\n\nSURVIVORS (0 fatal, >=2/3 survive): ${JSON.stringify(survivors.map(s=>s.attack),null,1)}\n\nTASK: Synthesize honestly. (a) proof_found: a proof of ShortestSupportExpansion/FullBankHall survived adversarial pressure AND covers the full closure (not a special/non-deficient case) AND uses no eta_C -- specify the exact lemma to formalize; (b) decisive_deficient_falsifier: a fully-constraint-verified DEFICIENT (Gamma>N^2) minimal-neg cage violating FullBankHall survived -- give it exactly (this refutes the conjecture, a huge claim: demand triple-checked deficiency+maximality+minimality); (c) sharpened_open: state the reduced sub-obstruction + exactly what the stronger model needs; (d) no_progress. Do NOT overclaim. Give the single most important takeaway + next concrete step. Return the schema.`,
  { label:'synth:sse', schema:SYNTH_SCHEMA, effort:'xhigh' })

return { outcome:synth.outcome, headline:synth.headline, synth, survivors:survivors.map(s=>s.angle), ground, digest }
