# Codex Multiagent Proof Registry

This registry adapts the dynamic portfolio protocol from OpenAI's published
Cycle Double Cover prompt to the tooling available in this workspace.

## Capacity

- Available orchestration API: `multi_agent_v1`.
- Observed concurrent-agent ceiling: 6. A seventh spawn is rejected.
- Policy: run repeated six-agent waves; close completed agents immediately;
  preserve mathematical independence during exploratory waves.
- CPU certificate work is separate and may use at most 64 worker threads.

## Acceptance Gate

An agent result advances the proof only if it supplies at least one of:

1. a sorry-free compiled Lean theorem on the production API;
2. an independently replayable exact certificate with stated coverage;
3. an exact counterexample killing a proposed lemma;
4. a real graph-derived provider replacing a hypothesis in the theorem chain.

Status reports and bounded no-hit searches are not closure.

## Approach Families

| ID | Family | Current exact state | Status | Next independent mechanism |
|---|---|---|---|---|
| A | Rooted rotor catalogue | `t=3,t=4` closed; `t=5` orders 15,16 support-infeasible; order 17 first feasible frontier | ALIVE / main lane | Exhaust each split or emit checked intrinsic+extension UNSAT bundles |
| B | FullBank Hall / finite Farkas | Abstract algebra and accepted chart provider compile; real graph-derived provider missing | ALIVE | Construct production transfer ledger and catalogue consumer |
| C | Direct local endpoint/common-blue forcing | Exact N=8 and N=19 weak-endpoint cages refute forced `sigma >= 2` | DEAD as standalone | Reopen only with positive-defect shore occupancy or simultaneous exchange |
| D | Support-monotone rotor potential | 7,600,710 live detours have support delta `-1,0,+1` | DEAD | Reopen only with a new state variable beyond support size |
| E | Gamma-minimal geodesic switching | Many local switch statements falsified; exact switch-capacity certificates kill two `t=5` near-hits | ALIVE as certificate mechanism | Seek a uniform weighted-switch certificate only if catalogue motifs support it |
| F | Global algebraic/spectral reformulation | Prior Schur, fixed Neumann, scalar Hall, and local SOS routes have exact guardrail failures | PARKED | New agent must supply a genuinely different invariant, not a renamed equivalent wall |
| G | Adversarial real-cage construction | No positive-defect active rotor found; 128-cage and N=78 graft sweeps collapse to defect zero | ALIVE / adversarial | Target feasible `t=5` catalogue entries and full production source relations |

## Active Wave

Wave 2 uses all six available LLM slots:

1. M1 production sink/neutral-state interface.
2. M2 detour transport ledger and defect delta.
3. M3 balanced-deficiency rotor interface.
4. M6 checked `t=5` catalogue kernel.
5. Catalogue coverage/termination audit.
6. Independent verifier for the order-15/16 support closures.

In parallel, exact CP-SAT jobs use at most 64 CPU workers across disjoint
`t=5` shore splits.

## Next Exploratory Wave

After Wave 2 is harvested, the next six agents must be mathematically diverse:

1. global finite-field/linear-algebra reformulation of the delta-zero wall;
2. extremal/stability reduction around the balanced `C5` blow-up;
3. matroid/flow interpretation of the physical-half matching and bank ledger;
4. structural induction on minimal bad-edge circuits;
5. adversarial production-cage constructor on the first feasible `t=5` entry;
6. referee agent seeking circularity, missing quantifiers, and false completeness.

No family receives a second agent in that wave until its first agent returns a
concrete lemma, construction, equation, or counterexample.
