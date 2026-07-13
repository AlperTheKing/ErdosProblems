# Erdos Problem 23: Final Handoff and Restart Record

Date frozen: 2026-07-12
Repository: E:\Projects\ErdosProblems
Status: full conjecture OPEN; work stopped by user after the final R58 audit.
Purpose: preserve the exact proof boundary for a future stronger model.

## 1. Statement and honest status

For a graph G, let bip(G) be the minimum number of edges whose deletion makes
G bipartite. Let

    a(N) = max{bip(G) : G is triangle-free and |V(G)| = N}.

Erdos Problem 23 asks for the sharp universal bound

    bip(G) <= N^2/25

for every finite triangle-free graph G. For N=5n, balanced blow-ups of C5 give
equality n^2.

What is proved:

    a(5n) = n^2 for every integer 1 <= n <= 40.

Equivalently, the conjecture is proved exactly for the multiples of five up
to N=200. This is published as arXiv:2606.28041.

What is not proved:

    the bound for all N, or even for all multiples N=5n.

The finished finite computation and the 108 chart certificates do not imply
the missing all-order theorem. No unconditional top-level Lean theorem for
the full conjecture exists in this workspace.

## 2. Completed and independently checked work

### 2.1 Published finite theorem

Paper:

    Alper Ferudun,
    "The Erdos n^2/25 max-cut conjecture for small multiples of five,
    via a per-root-MaxCut envelope and blow-up integrality",
    arXiv:2606.28041 [math.CO], 2026.

Scope: a(5n)=n^2 for 1 <= n <= 40, not all n.

### 2.2 Exact 108-chart certificate batch

The near-band chart batch is complete:

    certified rows: 108/108
    failed rows: 0
    arithmetic: exact rational
    canonical ledger SHA-256:
    981D353F88C8148DEC975DF75CBEDCC4975505F2ADF2345E6A6A9329FD3BD1AF

Claude independently reverified the aggregate and accepted this ledger on
2026-07-09. The preserved archive contains every manifest, exact solution,
check summary, modular summary, and repair summary referenced by the ledger:

    problems/23/archive/chart_v108/

Archive facts:

    441 files
    456.96 MiB
    437 ledger-referenced artifacts
    0 missing references
    0 SHA-256 mismatches
    archive SHA list:
    problems/23/archive/chart_v108/SHA256SUMS
    SHA256SUMS SHA-256:
    84EBDBA3FFA6DEEC3AF135763856F95D3936BC1E6058BB6FD5A8AA9A700ACDD1

This closes the finite chart side only. It does not provide the graph-derived
provider required for arbitrary order.

### 2.3 Compiled downstream wall machinery

The repository contains downstream interfaces and algebraic consumers for a
full-bank certificate, including:

    FullBankRelaxedCoverCert
    FullBankGlobalPackage
    FullBankGlobalPackage.Checked
    fullBankGlobalPackage_sound
    gammaUpper_from_fullBankGlobalPackage
    chargeCertProviderOfFullBankLedger_ok

The canonical source-level map is:

    problems/23/writeup/CODEX_GAP1_GROUNDING_MAP_20260709.md
    SHA-256:
    B31AD8325083D8D163F69E9264483D5D398300529D70E2F348203560F1CE5F23

These consumers are not providers. Their existence must never be reported as
a proof of the conjecture.

## 3. The exact remaining wall

There are two complete ways to resume.

### Route A: W3 plus restricted Farkas

For every concrete forced-ell=5 wall instance, construct

    Q : ClosedShore.AbstractEscapeQuotient I
    Allowed : I.Cut -> Prop

and prove:

    ClosedShore.ClosedWeightedHallCompleteness Q
    ClosedShore.PositiveRootBlockClosedExtraction Q
    ClosedShore.ClosedRootCutViolatesD1 Allowed Q d Z.portLoad

for every relevant checked dual and almost-squeeze. In addition, prove the
missing finite-rational restricted-Farkas bridge supplying the required
DualAlmostSqueeze for every strict restricted dual.

The existing W3 theorem then handles the remaining bookkeeping:

    ClosedShore.noStrictRestrictedDual_of_closedHall_and_exchange

### Route B: direct checked package

Bypass restricted duals and construct directly either:

    P : Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows
    hP : P.Checked

or an equivalent:

    cert : Ell5FullBankInterface.FullBankRelaxedCoverCert
      S F O J K sep dB inc kap

The construction must contain real graph-derived incidence, closed-Hall
completeness, no-double-spend, reserve identities, and final bank
superadditivity. Aggregate token counts alone are insufficient.

The shortest honest description of the unresolved mathematics is:

    build the real graph-derived full-bank provider.

## 4. Final R55/R57 audit: why the last shortcut failed

Canonical verdict:

    problems/23/writeup/WALL_ATTACK_R58_FINAL_R55_R57_VERDICT.md
    SHA-256:
    B295C2D082D970134E9AA77AACAC55EFCA233FE591FACEB32D92AF2B7703A082

Two exact obstructions were established.

### 4.1 Current-interface graph counterexample

A genuine 16-vertex graph satisfies the current R57 interface but defeats the
claimed negative-switch conclusion. The replay exhausts 2^15 normalized cuts
and 65,536 mask pairs and finds no negative four-corner margin.

Conclusion: the proposed branch-to-prefix interface omitted necessary
incidence data.

### 4.2 Positive-defect abstract countermodel

A nine-copy exact integral grouped-flow model has positive defect and a
saturated exclusive fork satisfying the compiled R55/R57 hypotheses. It is
not a graph counterexample because it violates:

    CompleteShortestRowDB.badKeys_nodup

which was absent from the proposed bridge.

Conclusion: R55/R57 do not prove the graph theorem. The missing concrete
object is an external incidence injection of the form

    ExtPos(X,Y) -> ExtNeg(X,Y)

or an equivalent graph-derived full-bank construction.

Do not revive the R55/R57 route without adding and proving that incidence
structure.

## 5. New mathematical result extracted from the failed route

The failed bare-Hall idea produced a publishable counterexample family.

For every integer t >= 1, there is a triangle-free graph G_t with:

    |V(G_t)| = 7t+3
    bip(G_t) = t^2
    a unique maximum cut, up to global complementation
    t^2 bad edges
    one unique length-four cut-geodesic for every bad edge
    support-union size = 2t+2

Hence the shortest-support Hall inequality fails for t >= 3, with unbounded
ratio.

Primary writeup:

    problems/23/writeup/SHORTEST_SUPPORT_HALL_COUNTEREXAMPLE_FAMILY.md
    SHA-256:
    0A1B9167F3E06535C3D7B57EF22D6FA536CD92D09593C64BDC8B025EE3EA864A

Verifier:

    problems/23/writeup/_codex_support_hall_family_verify.py

The independent referee checker verified:

    all labeled cuts for t=1,2
    all cut-count orbits for t=3,4
    the structural theorem through t=8
    the all-t packing and uniqueness proof

It also confirmed the finite footprint classification:

    no footprint with at most 8 atoms
    one footprint with 9 atoms
    three footprint isomorphism classes with 10 atoms

### 5.1 Paper submission

Title:

    Shortest-geodesic supports in triangle-free maximum cuts:
    an infinite Hall obstruction and the first minimal footprints

arXiv submission:

    submit/7816436
    status at freeze: on hold for moderation
    primary category: math.CO
    license: CC BY 4.0

Preserved release artifacts:

    output/pdf/shortest_geodesic_support_obstructions.pdf
    SHA-256:
    67DD92FEF8376B81091327CDA1CDA5690603BBAC7C4E0A8B6AEEB4BF0E7BBCFB

    output/pdf/shortest_geodesic_support_obstructions_arxiv.zip
    SHA-256:
    6831828B86D5151DCEC5C29869536E65D2B4B1D5EF0ABA96498E4BF4DBF2943C

Source and ancillary files:

    problems/23/writeup/arxiv/shortest_support_obstructions/

The paper explicitly states that it does not solve Erdos Problem 23.

## 6. Preserved exact replay bundle

The final nine-replay audit is archived at:

    problems/23/archive/20260712_replay_audit/

It records and replays:

    local footprints m=6,...,10
    the connected triangle-free census n=5,...,10
    the genuine 24-vertex bare-Hall obstruction
    the genuine 8-vertex zero-defect rotor
    the 16-vertex R57 interface counterexample
    the positive-defect R57 abstract interface countermodel
    the C5[3] no-two-row-exchange result
    the C5[3] global collision minimum
    the exact Hoffman-Singleton singleton identities

Final post-cleanup audit verdict:

    9/9 expected exits
    exact integer/rational arithmetic
    no hidden floating-point acceptance
    manifest SHA-256:
    2A2B06FB4DFF54BEE472E1CE8A3B459D7714A2C502C2868D8FBCB0C3454418C7
    report SHA-256:
    B225BCB558519E162ED5B1229D62D585D0307FFB3EC747E440BF30AAEDF69581

The archive includes the former tmp input scripts. The full suite was rerun
successfully after tmp was deleted, proving that this replay bundle is
self-contained.

## 7. Lean status at freeze

### 7.1 Proven/compiled surface

Many downstream interfaces, bookkeeping lemmas, chart payloads, and local
kernels were compiled during the project. The detailed record is append-only
in:

    PROGRESS_CODEX.md
    coordination/CLAUDE_TO_CODEX.md
    coordination/CODEX_TO_CLAUDE.md

No statement in those logs upgrades the missing graph provider to a theorem.

### 7.2 Unverified new generic fixture

The source

    problems/23/lean/Erdos23Delta0/LayeredHallObstructionBankAbsorbed.lean
    SHA-256:
    E693CD8A7FA3E92FA478372CF686FD4155ED5F82E6D8E7C42D7D9C731A784F5D

constructs an abstract bank-absorbed relaxed-cover fixture for the G_t matrix.
It does not encode the ambient graph and does not solve the wall.

Post-cleanup compile attempt:

    FAILED BEFORE ELABORATION:
    missing Ell5FullBankAssignedSink.olean

The dependency olean cache had already been intentionally deleted as
regenerable bulk. Therefore the source has no final compile claim. A future
run must rebuild its import chain before judging it.

Other unique untracked Lean sources preserved:

    problems/23/lean/Erdos23Delta0/Gamma/GraphDataSignedCut.lean
    problems/23/lean/Erdos23Delta0/Gamma/OutsideBoundaryP1Injection.lean
    problems/23/lean/Erdos23Delta0/Gamma/SameAtomRowPairShapes.lean

Their exact status must be read from PROGRESS_CODEX.md; do not infer a compile
result merely from file existence.

## 8. Dead routes that must not be repeated unchanged

1. Bare shortest-support Hall/SSE is false, even for a unique maximum cut.
   The family G_t is an infinite counterexample.

2. Current R55/R57 branch-to-prefix extraction is false at its compiled
   interface. See the 16-vertex gate and nine-copy interface model.

3. Aggregate counts without a graph incidence map cannot establish the
   required external positive-to-negative injection.

4. A downstream FullBankGlobalPackage consumer is not a construction of a
   checked package.

5. The 108 chart batch is finite certificate data; it is not the missing
   all-order provider.

6. An abstract LP/Farkas shell is incomplete unless either the restricted
   almost-squeeze existence theorem or a direct primal package is supplied.

The broader dead-end history is in the R1-R58 wall notes under:

    problems/23/writeup/WALL_ATTACK_R*_GPTPRO*.md

## 9. Minimal restart sequence for a future model

Read, in order:

    1. problems/23/ERDOS23_FINAL_HANDOFF_20260712.md
    2. problems/23/writeup/CODEX_GAP1_GROUNDING_MAP_20260709.md
    3. problems/23/writeup/WALL_ATTACK_R58_FINAL_R55_R57_VERDICT.md
    4. problems/23/writeup/CODEX_ENDGAME_DEPENDENCY_MAP_20260709.md
    5. problems/23/writeup/WIRING_SPECS_GPTPRO.md
    6. problems/23/writeup/SHORTEST_SUPPORT_HALL_COUNTEREXAMPLE_FAMILY.md

Then run:

    python -B problems/23/writeup/_codex_support_hall_family_verify.py
    python -B problems/23/archive/20260712_replay_audit/run_audit.py
    python -B problems/23/archive/20260712_replay_audit/finalize_audit_v2.py
    python -B problems/23/archive/20260712_replay_audit/verify_manifest.py

For the 108 charts, restore archived files to tmp if an old verifier expects
the historical paths:

    Copy-Item problems/23/archive/chart_v108/* tmp/ -Force

Verify every referenced SHA against:

    problems/23/archive/chart_v108/
      eq_odl1_rung2_chart_batch_ledger_v108_codex.json

Only then attack one of the two complete wall deliverables in Section 3.
Do not restart from a(30)=36, the chart batch, bare Hall, or R55/R57.

## 10. Cleanup and regeneration policy

Preserved permanently:

    handwritten and non-generated source under problems/23
    the complete 108-chart exact certificate archive
    the self-contained final replay archive
    3,327 source-like files recovered from tmp, with SHA-256 inventory
    the new paper source, ancillary scripts, PDF, and source ZIP
    the append-only progress and coordination logs

Temporary source archive:

    problems/23/archive/tmp_text_sources_20260712/
    3,328 files including SHA256SUMS
    458.12 MiB
    SHA256SUMS SHA-256:
    B1246199AE34617498773EC0662C9C1611D9800987797572C13BF077D8F23514

Deleted as reproducible bulk:

    temporary .olean caches
    temporary executables and Python bytecode
    solver .tmp shards and stale logs
    intermediate generated JSON/JSONL column pools
    43,136 generated O14 Lean files and 277 compact-pilot payload files

The first cleanup pass removed approximately 1.129 TB of logical temporary
build data. The final pass removed the remaining 9.1 GB tmp tree and about
35.0 GB of generated O14 Lean payloads after archiving their sources and exact
certificates.

Final measured state:

    drive E free space: 1,062.15 GB
    problems/23 size: 1.05 GB
    tmp files: 0

## 11. Final scientific conclusion

The project produced:

    a published exact finite theorem through N=200
    a complete 108-chart exact certificate archive
    substantial compiled downstream proof infrastructure
    an infinite counterexample family to bare shortest-support Hall expansion
    a finite minimal-footprint classification
    a second arXiv paper submission with two independent exact verifiers
    a precise, falsifier-tested description of the remaining universal wall

It did not prove the full Erdos Problem 23. The surviving mathematical task is
a genuinely new graph-incidence theorem: construct the real full-bank provider
or its exact closed-shore/Farkas equivalent.
