# Child 02 semantic audit: outsideAttachment / pattern 4

## Verdict

outsideAttachment is not a Lean production predicate, checker, theorem, or constructor in the current source tree. The final scoped search of every *.lean below problems/23/lean/Erdos23Delta0 for

    OutsideAttachment|outsideAttachment|outside_attachment|
    checkedMatching_withOutsideAttachment_sound|outsideAttachmentTerminal_sound|
    CheckedTransferMatching|checkedTransferMatching_to_activeFullBank

returned no match (rg exit 1). In particular, there is no Lean declaration named CheckedTransferMatching in that scope for pattern 4 to have entered.

The current executable Lean relation is ActiveScopedMinimumExchange.Available:

    EligibleOwner G c (demandOwner d) s ∧ ¬ScopedReserved G c omega s

(problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:144-147). EligibleOwner has exactly two alternatives:

    s.sourceX = owner ∨
      (0 < pairCount omega owner.1 s.sourceX.1 ∧
       0 < pairCount omega owner.1 s.sourceY.1 ∧
       0 ≤ sigma G c [s.sourceX.1, s.sourceY.1])

(problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142). There is no outside-selected-union test, external blue-component identifier, attachment boundary, attachment witness, component-union switch, or component-union loss.

Pattern 4 exists as archive/proposed-interface prose and exact-integer Python flow-gate code. It has not been wired into Lean Available or Matching. The R29 owner-Hall replay enumerates only same-first and row-companion triples. Therefore the R29 defect 28 is evidence about the narrower ActiveScoped relation, not a checked failure of the four-pattern relation.

## Requirement, proposal, and production

1. GOAL_LOOP asks for a future transfer-matching chain with base patterns sameFirst, commonBad, and rowCompanion, then FullBank consumers, while labeling Hall completeness open. Its exact line says “Open research: (a) stage-3 base-pattern Hall-completeness or the slot-transport theorem” (GOAL_LOOP.md:16). This is a mission requirement, not a defining Lean expression.

2. R23 prose defines pattern 4 using U_omega, the selected-row union; K_omega(x), the blue component of an outside vertex in B[V\U_omega]; and Att_omega(x), its blue boundary in U_omega. An outside ordered pair is eligible through attachment vertices co-occurring with the owner (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:7-11).

3. The same archive calls its Lean material “LEAN SHAPES GIVEN” and names CheckedOutsideAttachmentBaseTerminal, outsideAttachmentTerminal_sound, and checkedMatching_withOutsideAttachment_sound (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:29-34). Coordination subsequently assigns compilation of those names as future work (coordination/CLAUDE_TO_CODEX.md:13898-13901). Their absence from Lean resolves their status: archive/proposed interface only.

4. The only exact matching consumer in the audited ActiveScoped path is:

    Matching.available : ∀ d, Available G c d (assign d)

(problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158).

5. A neighboring checker shows what a landed checker looks like. CheckedRowCompanionBaseTransfer.TerminalData.check is:

    decide (T.RawValid G c bads selected activeVertices)

(problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:94-98), and checked_of_check_eq_true concludes CheckedRowCompanionBaseTerminal ... T (problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean:125-130). No analogous outside-attachment declaration exists.

## Lean semantic comparison

### Source universe: indirectly represented

FreeHalf is the generic ordered-pair-half type:

    structure FreeHalf ... where
      sourceX : Fin G.n
      sourceY : Fin G.n
      half : Fin 2
      distinct : sourceX ≠ sourceY
      free : pairCount omega sourceX.1 sourceY.1 = 0

(problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:64-73).

pairCount is the length of selected rows containing both coordinates:

    ((selectedRows omega).filter fun row =>
      decide (x ∈ row.verts ∧ y ∈ row.verts)).length

(problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:78-82). Since R23 requires both coordinates outside the selected union (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:7-10), their pair count is zero. Thus raw outside ordered-pair halves are indirectly present in FreeHalf; there is no outside subtype.

### Outside graph, components, and attachment boundary: absent

selectedVertices is the deduplicated flat-map of selected row vertices (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:63-66). activeEdges instead filters blue graph edges whose two endpoints are selected and which are not selected-support edges (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:91-101). activeGraph wraps those internal edges (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:28-39).

Therefore the external graph B[V\U], its components K(x), and attachment boundaries Att(x) are absent, not aliases for activeGraph or ActiveOwner.

### Attachment eligibility: absent

R23 eligibility uses owner co-occurrence with attachment vertices (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:7-10). Production EligibleOwner checks owner co-occurrence with the source coordinates themselves, plus two-vertex sigma (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142). For an outside coordinate those direct pair counts are zero. For an active selected owner, the first coordinate of a both-outside pair is not the owner. Neither existing disjunct represents attachment eligibility.

### Switch and loss: absent

The archive switch is K(x) ∪ K(y), with recomputed nonnegative loss (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:10-12). EligibleOwner checks only sigma on [sourceX, sourceY] (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:140-142). The component-union switch and its loss certificate are absent.

### Reservation and capacity: present generically

ScopedReserved reserves only half zero on an internal active-graph edge owned by an active endpoint (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-132). Because activeEdges has both endpoints selected (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:93-101), a both-outside pair cannot be active. Both halves are consequently unreserved, but that does not make them eligible.

### Demand and consumers: present, but consume only Available

Demand is exactly:

    ActiveCollisionHalf G c omega ⊕ ActiveHitNeed G c omega

(problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:102-106). Matching requires an injective assignment to FreeHalf and Available for every demand (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158). HallCondition counts neighbors only through Available (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:160-165). The proved equivalence concludes:

    Nonempty (Matching G c omega) ↔ HallCondition G c omega

(problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:167-170). An outside pair failing current EligibleOwner contributes no neighbor and cannot be assigned.

## Exact executable gates and data structures

### Original R23 fixture gate

problems/23/writeup/_claude_r23_outside_attachment_gate.py implements run_flow(N, blue, bad, rows, label, expect_full, extra_checks=None) at problems/23/writeup/_claude_r23_outside_attachment_gate.py:52-53.

- U is a set of selected vertices; compid is a vertex-indexed list; comps is a list of outside-component sets; atts is a parallel list of attachment sets (problems/23/writeup/_claude_r23_outside_attachment_gate.py:62-75).
- loss(S) is integer blue-boundary edges minus bad-boundary edges (problems/23/writeup/_claude_r23_outside_attachment_gate.py:76-79).
- elig_out[v] unions components having an attachment a with n[(v,a)] > 0 (problems/23/writeup/_claude_r23_outside_attachment_gate.py:91-99).
- Old arcs are sameOwner (107-110), commonBad (111-115), and rowCompanion (116-121). Pattern-4 arcs are appended for distinct ordered x,y in elig_out[v] when cached loss(comps[compid[x]] ∪ comps[compid[y]]) is nonnegative (122-133).
- cells maps ordered pairs to ids; arcs_om stores owner-cell incidence (100-105). The network gives every cell capacity two (134-142) and uses dinic (22-50).

This first gate is not full ActiveScoped semantics. Its demand is collision halves only (86-90), every cell has capacity two (138-140), and it has neither half-zero reservation nor HitNeed.

### Corrected full-obligation R23 gate

problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py records those omissions at problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:1-17 and implements full_owner_flow(..., scope="all", include_outside=True) at problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:148-151.

- component_id, components, and attachments are built by BFS in the outside-induced blue graph (229-251).
- eligible_outside[owner] unions component cid exactly when:

      any(counts.get((owner, a), 0) > 0 for a in attachments[cid])

  (253-259).
- loss is the integer blue-boundary count minus bad-boundary count (261-265).
- cell_id and cell_capacity give ordered cells capacity one exactly on a reserved active edge and two otherwise (267-277).
- owner_cell_arcs first receives same-owner and row-companion arcs (279-295). With include_outside true, pattern-4 arcs are added after a component-pair union-loss check (297-311).
- The integer network is owner demand to cell to sink (313-332); the cell-sink arc enforces shared capacity across owners (316-328).
- The returned dict records includeOutside, demand parts, max flow, deficiency, and eligible-outside counts (337-358).

This is executable audit code, not a Lean checker: it returns a Python dict (337-363) and constructs no Lean FreeHalf, Available, or proof object.

### R29 active-scoped replay

The R29 writeup names tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py in its replay list (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:59-64).

owner_sources uses masks[(x,y,h)] for owner bitmasks and reason[(x,y,h)] for reason bitmasks (tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py:100-109). Its first loop emits only same-first triples and sets reason bit 1 (110-119). Its second emits only direct row-companion triples, checks sigma2 ≥ 0, and sets reason bit 2 (120-134). It returns immediately at line 135. The certificate schema says “ordered FreeHalf source triples; owner bit i is owner i” (153-156).

There is no outside component, attachment set, component-union loss, include_outside flag, or third reason. Hence the 19,925-source neighborhood and defect 28 (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:51-55) are for current ActiveScoped Available, not pattern 4.

## Monotonicity and consumer implications

At Python level, pattern 4 is monotone: both gates append outside owner-cell arcs after old arcs and delete none (problems/23/writeup/_claude_r23_outside_attachment_gate.py:105-133; problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:279-311). R23 explicitly states R_new ⊇ R_old and that every old passing fixture remains passing (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:23-24). For fixed demand and capacities, an old feasible flow remains feasible and maximum flow cannot decrease.

There is no compiled Lean monotonicity theorem and no production consumer implication because Available was never enlarged. Matching.available still requests current Available (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158), and HallCondition uses the same predicate (160-165). R23's claim that the consumer could remain unchanged is a proposed-interface statement (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:29-34), not an implemented theorem.

Structurally, an extension could reuse Demand, FreeHalf, ScopedReserved, Matching.injective, and the generic Hall equivalence. No current declaration supplies the required disjunct or soundness proof.

## ActiveScoped comparison matrix

| Pattern-4 class/predicate | Status | Exact production comparison |
|---|---|---|
| Selected row union U | Present upstream | selectedVertices is the selected-row flat-map (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:63-66). |
| Ordered distinct outside pair halves | Indirectly represented | Generic FreeHalf contains any distinct pair with pairCount=0 (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean:64-73). |
| Outside induced graph B[V\U] | Absent | activeGraph uses internal selected-vertex activeEdges (problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean:91-101; problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:28-39). |
| Outside component K(x) | Absent | No such field/function in EligibleOwner or Available (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-147). |
| Attachment boundary Att(x) | Absent | No boundary or attachment witness in the exact relation (134-147). |
| Owner-to-attachment co-occurrence | Absent | Production checks co-occurrence with source coordinates, not attachments (136-142). |
| Component-union switch K(x) ∪ K(y) | Absent | Production sigma uses only [sourceX,sourceY] (140-142). |
| Component-union nonnegative loss | Absent | Python alone computes it (problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:261-265,297-311). |
| Half reservation | Present generically | ScopedReserved (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:125-132). |
| No double spend | Present generically | Matching.injective (154-158). |
| Collision plus HitNeed | Present | Demand is ActiveCollisionHalf ⊕ ActiveHitNeed (102-106). |
| Pattern-4 eligibility in Available | Absent | Available is EligibleOwner ∧ ¬ScopedReserved; EligibleOwner has only the two quoted alternatives (134-147). |

## Contradictions and ambiguities

1. Production-name mismatch. GOAL_LOOP.md:16 and R23 prose speak of CheckedTransferMatching, but no declaration exists in the scoped Lean search. The compiled matching object here is ActiveScopedMinimumExchange.Matching (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:154-158).

2. “Lean shapes” versus Lean code. R23 names three proposed declarations (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:29-34), and coordination asks to compile them (coordination/CLAUDE_TO_CODEX.md:13898-13901). They remain proposed/archive interfaces.

3. Prose-only component equalities. R23 additionally says comp(a)=comp(v)=comp(b) (problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md:9-11). Corrected Python tests only positive owner/attachment co-occurrence and component union (problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:253-259). It has no separate destination-component equality gate. No executable definition of that prose comp was found, so equivalence is unresolved.

4. Old relation presentation changed. The first Python gate explicitly loops over commonBad (problems/23/writeup/_claude_r23_outside_attachment_gate.py:111-115). The corrected gate omits a separate loop and says commonBad is a row-companion subcase (problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py:286-295). ActiveScoped likewise exposes same-first and row-companion only (problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean:134-142).

5. R29 does not replay pattern 4. R29 itself says full-bank capacity is absent from active-scoped FreeHalf matching (problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md:91-96), and owner_sources confirms the omission. Coordination says the CE “deliberately locks” pattern 4 while asking for a fifth pattern (coordination/CLAUDE_TO_CODEX.md:14005), but the scoped search found no R29 pattern-4 computation or four-pattern Hall certificate. Defect 28 must not be reinterpreted as a four-pattern falsifier.

6. Fixture results were not re-executed. The combined R23 Python command yielded no output for approximately 75 seconds and was terminated. Archived numerical verdicts are not used as evidence here; exact source expressions are.

## Unresolved gaps

- No Lean CheckedOutsideAttachmentBaseTerminal, Boolean checker, soundness theorem, eligibility disjunct, matching wrapper, or FullBank consumer exists.
- No executable R29 gate was found that evaluates pattern 4 on the reconstructed 2,943-vertex tuple. Whether R29 has zero pattern-4 eligibility, or remains deficient after adding it, is unresolved.
- The intended executable meaning of R23's comp(a)=comp(v)=comp(b) is unresolved.
- No compiled theorem states monotonicity from old Available to an outside-extended relation.
- No separate active /goal attachment was accessible by filename. GOAL_LOOP.md:1-4 says it reproduces the armable /goal; rg --files | rg "goal_v61_ascii|goal.*attach|attachment.*goal" returned exit 1.

## Commands run

Material scoped searches:

    rg --files | rg "(^|[\\/])(COMMON\.md|CLAUDE_TO_CODEX\.md|R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER\.md)$|outsideAttachment|CheckedTransferMatching|ActiveScopedMinimumExchange|FullBank|R29"
    rg --files | rg "goal_v61_ascii|goal.*attach|attachment.*goal"
    rg -n -S "OutsideAttachment|outsideAttachment|outside_attachment|outside attachment" problems\23\lean\Erdos23Delta0
    git grep -n -I -i -E "outside.?attachment|checkedoutsideattachment|outsideattachmentterminal|checkedmatching_withoutside|pattern.?4" -- "problems/23/lean/**" "problems/23/writeup/**"
    git grep -n -I "CheckedTransferMatching" -- "problems/23/**"
    rg -n -S "CheckedTransferMatching|Checked.*BaseTerminal|BaseTerminal|TransferMatching|transferToken|sameFirst|commonBad|rowCompanion" problems\23\lean\Erdos23Delta0 problems\23\writeup\WALL_ATTACK_R23_GPTPRO56.md
    git grep -n -I -E "CheckedC5BaseTransfer|CheckedRowCompanionBaseTransfer" -- "problems/23/lean/**/*.lean"
    git grep -n -I -E "(structure|abbrev|def) (FreeHalf|CollisionHalf)|namespace FreeHalf|def IsFree|isFree" -- "problems/23/lean/Erdos23Delta0/Gamma/*.lean"
    rg -n -S "outside|attachment|pattern.?4|include_outside|eligibleOutside" tmp\fanout\r29_gate tmp\fanout\global_min_proof problems\23\writeup\_claude_r29_2943_structural_gate.py --glob "*.py" --glob "*.md" --glob "*.json"
    $patterns='OutsideAttachment|outsideAttachment|outside_attachment|checkedMatching_withOutsideAttachment_sound|outsideAttachmentTerminal_sound|CheckedTransferMatching|checkedTransferMatching_to_activeFullBank'; rg -n -S $patterns problems\23\lean\Erdos23Delta0 --glob '*.lean'
    rg -n -S 'outsideAttachment|outside.attachment|include_outside|eligible_outside|elig_out' problems\23\writeup tmp\fanout\r29_gate tmp\fanout\global_min_proof --glob '*.py'

Files were read with Get-Content -LiteralPath and line-numbered in PowerShell. Hashes were computed with Get-FileHash -Algorithm SHA256.

Attempted execution:

    python problems\23\writeup\_claude_r23_outside_attachment_gate.py; python problems\23\writeup\_codex_r23_outside_attachment_full_obligation_gate.py

It was terminated after approximately 75 seconds with no yielded output. No sibling artifact-producing R29 script was executed. Two early over-broad searches timed out/were terminated and were replaced by the scoped commands above.

The patch service failed first on file creation and then reported: “windows unelevated restricted-token sandbox cannot enforce split writable root sets directly.” The empty REPORT.md was created with New-Item, and this report was written directly only to the assigned path as the sole fallback mutation.

## Exact SHA-256 hashes of every cited source

    49c7f1e8dda95ed15fefab7df9cf578cc86e4da773627a6355ceb74f6ea029cf  tmp/fanout/r29_fullbank_semantics/COMMON.md
    e91a2f03bc6774d622d9610b24394a0b4338f6543d7bf19e4464ff5d450e014b  GOAL_LOOP.md
    387daddd459219f8f1d674b16e2d3c1429925a416f09d957c19f69b55404b248  coordination/CLAUDE_TO_CODEX.md
    5508cfcbcfe4d5072b52acecdf0ab8dccbec5cbe2a30c8e0997f6b01dd95ad42  problems/23/writeup/R29_GLOBAL_MIN_SCOPED_HALL_FALSIFIER.md
    45e6533b1cb670ebb8476998bee9904ad0ec8f8943c2753b78a677827358c9d3  problems/23/writeup/WALL_ATTACK_R23_GPTPRO56.md
    e4d216fce19e96416be0842f5410bab0cf8fee9af933ff1160a3b77a3a67b11a  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandRowSelection.lean
    ea36fc95b8fad743dc8c11db510284f6c109ce77319378e47ca56ef40c3eb1a7  problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean
    6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d  problems/23/lean/Erdos23Delta0/Gamma/ActiveScopedMinimumExchange.lean
    84b632c5329ea1205729ff0b95ab124fc573f119f17c50d4aa2f02ac9afdf09a  problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean
    6147ac4c7b501f8ab46597ef210838e1138f0b7cb15910a4712dc5efac844cec  problems/23/writeup/_claude_r23_outside_attachment_gate.py
    26838f666e3c567d8396a89ec4e6540fb1b1fa321eaa434b12f18710a113ace1  problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py
    a0912540f653945eed1eddbc74b191ea2a6ab90ccd075b1395cab552ff574dc0  tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py
