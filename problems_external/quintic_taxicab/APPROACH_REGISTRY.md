# Positive Fifth-Power Taxicab Problem - Approach Registry

Registered: 2026-07-21
Status: QUEUED - audit and calibration only; no main search launched
Initial attack tranche if selected: 8 hours

The active magic-square campaign remains primary until its registered exit.
This file does not authorize a concurrent heavy search.

## Exact target

Find positive integers a, b, c, d such that

    a^5 + b^5 = c^5 + d^5

and the two representations are disjoint:

    {a,b} intersect {c,d} = empty.

Repetition inside one representation is allowed. One such quadruple makes the
set of fifth-power taxicab values nonempty; well-ordering then supplies the
least value required by the Taxicab formal conjecture. A primitive quadruple
is preferred.

## DIRECT ROUTE

### 1. Exact final deliverable

Produce one positive integer quadruple (a,b,c,d) satisfying the equality and
cross-disjointness. Verify it with:

1. a standalone exact-integer Python verifier;
2. an independently implemented C++ multiprecision verifier; and
3. a Lean proof of the concrete witness, the induced least-value step, and
   `Taxicab.taxicab_for_5_2_2`, without sorry or native_decide.

A rational torsor point, a Jacobian point, a rank computation, or a bounded
NO_HIT is not the final deliverable.

### 2. Current frontier certificate

For a nontrivial positive rational solution put

    h = (c+d) - (a+b).

If h = 0, write t=a+b=c+d, u=b-a and v=d-c. Then

    F_t(u)-F_t(v)
      = 5t (u^2-v^2) (u^2+v^2+2t^2),

so u^2=v^2 and the unordered pairs coincide. Hence h is nonzero. Swap the
two sides if necessary and scale homogeneously over Q to h=1.

Put

    t=a+b,  u=b-a,  T=t+1,  v=d-c,
    L=t^5+10t^3u^2+5tu^4.

The finite rational certificate Q5-TORSOR is (t,u,Y) satisfying

    t > 0,
    |u| < t,
    Y^2 = 80T^6 + 20T L,
    Z = (Y-10T^3)/(10T) is a rational square,
    0 < Z < T^2.

For the final positive cross-disjoint target, Darmon--Merel's theorem on
`x^n+y^n=2z^n` rules out equality inside either representation: `u=0` or
`Z=0` would force the trivial equal solution and violate cross-disjointness.
Changing the sign of `u` only swaps `a,b`, while choosing the nonnegative
square root of `Z` only orders `c,d`. Since `T>0`, negative `Y` forces `Z<0`.
Production may therefore require `u>0`, `Z>0`, and positive `Y`; calibration
must still exercise the pruned signs and zero rejection gates.

### 3. Explicit logical bridge

Choose rational v with v^2=Z and set

    a=(t-u)/2,  b=(t+u)/2,
    c=(T-v)/2,  d=(T+v)/2.

The inequalities make all four values positive. The discriminant identity

    Y^2 - (80T^6+20TL)
      = 20T [5TZ^2+10T^3Z+(T^5-L)]

shows that the Q5-TORSOR conditions imply

    t^5+10t^3u^2+5tu^4
      = T^5+10T^3v^2+5Tv^4,

which is exactly 16 times the required fifth-power equality. Since the two
pair sums differ by 1, any equality across the two representations would
force the other entries equal and contradict the sum difference. Clearing a
common denominator gives the positive integer certificate.

For a verified integer quadruple, set x=a^5+b^5 and

    S = {[a,b], [c,d]}.

Positivity, equality, and cross-disjointness give
`IsTaxicabFor' 5 2 2 x`: the two lists are distinct and disjoint, have length
two, avoid zero, and both fifth-power sums are x. Hence

    {x : Nat | IsTaxicabFor' 5 2 2 x}

is nonempty. The well-ordering of Nat supplies a least element x0, which gives
`IsTaxicabFor 5 2 2 x0` and therefore the existential required by
`Taxicab.taxicab_for_5_2_2`. This final step uses the current definitions in
`FormalConjectures/Wikipedia/Taxicab.lean`; it does not require a second
Diophantine search.

Conversely, every nontrivial positive integer certificate has h nonzero and
normalizes to such a rational Q5-TORSOR certificate. Thus the bridge is
lossless for existence.

Asiryan's divisibility `30 | h` applies to integer solutions. It does not
forbid this rational `h=1` normalization. Clearing a rational certificate to
a primitive integer certificate restores an `h` divisible by 30; this is a
post-reconstruction check, not a normalized-box prefilter.

### 4. Next falsifiable action

Before any main launch:

1. build the two exact final-certificate verifiers;
2. use bundled open-source PARI 2.15.4 hyperellratpoints to calibrate direct
   rational-point enumeration on specialized quartics;
3. compare every small calibration box against an independent Fraction/isqrt
   enumerator;
4. test both Y signs, rational-square Z, positivity, denominator clearing, and
   final verifier agreement; and
5. freeze explicit finite bounds P,Q,N,D and a SHA-256 manifest assigning each
   coprime t=p/q specialization to exactly one of 64 single-thread lanes.

Before freezing bounds, apply the current OEIS lower-bound redundancy gate.
For `p<=P`, `q<=Q`, and `d<=D`, denominator clearing gives every reconstructed
integer base below

    B = 2 sqrt(10) Q D^2 (P+Q)^(3/2).

If `2B^5 <= 10^33`, the current A046881 record classifies the whole box as
previously covered, so it is not a priority launch box. Test this without
floating point via

    409600000 Q^10 D^20 (P+Q)^15 <= 10^66.

The OEIS page does not link a reproducible artifact for the `10^33` search;
this is a source-based redundancy/prioritization gate, not an independently
verified exclusion. Failure of the inequality only means that A046881 does
not eliminate the box; it is not evidence that a certificate exists.

A sharper per-cell gate applies before choosing a symmetric box. If the
reduced square is `Z=e^2/f^2`, then

    f | q d s(10(p+q)),

where `s(k)` is the largest positive integer whose square divides `k`. Put

    M(p,q,d) = 2 p q d s(10(p+q)).

The primitive integer taxicab value reconstructed from this cell is strictly
less than `2M^5`. Exact maximization over coprime `p,q` and `d` in a symmetric
box gives:

- `H=46`: `M_max=2942160`, so `2M_max^5 < 10^33`;
- `H=47`: `M_max=5699220`, so `2M_max^5 > 10^33`.

Thus the current A046881 record makes `H<=46` source-redundant, while `H=47`
is the first symmetric box not eliminated by this bound. Darmon--Merel rules
out the within-pair repetitions not covered by A046881. As above, this is a
source-based priority gate, not an independently reproduced exclusion.

A Jacobian-only enumeration is forbidden because a Jacobian point need not
lift to the genus-one torsor. A quartic point is only TORSOR_POINT until the
Z-square and final equality gates pass.

### Post-primary eight-hour tranche protocol

The attack tranche uses at most 64 simultaneous single-thread workers and one
outer exclusive tranche lock. Let `T0` be recorded before Pilot A starts,
`G=T0+28800 seconds`, and `S=G-3600 seconds`. All search workers must stop by
`S`; the final hour is reserved for verifier execution, cleanup, and process
certification. No stage may reset `T0`, `S`, or `G`.

After the active magic-square campaign owns no live search process, run these
pilots sequentially and never overlap supervisors:

1. audit `P=Q=N=D=10`, local limit 120 seconds;
2. canonical `P=Q=N=D=47`, local limit 120 seconds;
3. canonical `P=Q=256, N=D=128`, local limit 600 seconds; and
4. canonical `P=Q=512, N=D=192`, local limit 1800 seconds.

Each local deadline is the earlier of its stated limit and `S`. Pilot A must
finish `FINITE_NO_HIT` with exactly 63 `NO_HIT` lanes and one `NO_WORK` lane.
Pilots B--D must finish with exactly 64 `NO_HIT` lanes. Every pilot also
requires `verified_hit=null`, empty stderr, valid result identities and
digests, `owned_pids=[]`, and no live owned process. A verified hit ends the
tranche. Any timeout, anomaly, survivor, or fail-closed status blocks the main
launch.

For canonical pilot lane `l`, let `e_l` be its integer elapsed milliseconds,
`w_l` its manifest weight, and `b_j=bit_length(R_j)`, where

    R_j = 80(P+Q)^6 D^4
        + 20(P+Q)(P^5 D^4 + 10 P^3 N^2 Q^2 D^2 + 5 P N^4 Q^4).

Choose the maximum exact ratio `rho=e_l/(w_l b_j^2)` by integer
cross-multiplication, with deterministic pilot/lane tie-breaking. This is an
empirical timing rule, not a certified complexity bound. For each symmetric
candidate `H` from 48 through 512, build the deterministic LPT assignment,
let `W_H` be its maximum lane weight, put

    b_H = bit_length(5760 H^10),
    Tpred(H) = ceil(3 rho W_H b_H^2 / 2),

and choose the largest candidate whose balance and OEIS priority gates pass
and whose predicted time fits before `S` with a 300-second setup guard. The
factor `3/2` is a declared empirical safety margin; a timeout remains only
`TIMEOUT_INCOMPLETE`. If no `H>=48` is eligible, Pilot B is retained as the
finite `H=47` result and no duplicate main campaign is launched. Rectangular
pilots and a larger symmetric box may overlap the `H=47` cells; that overlap
is calibration overhead, not new coverage.

Before `T0`, freeze the candidate-table generation and selection rule. Write
an atomic `selection_report.json` containing `T0,S,G`, pilot manifest and
result hashes, every `(e,w,b)`, the exact maximizing ratio and source lane,
the full candidate table, the selected `H`, and the selected main-manifest
digest. The main manifest deadline is exactly `S`. Between stages, require the
previous supervisor to have exited and certify zero owned workers by pinned
path and parent chain. If cleanup and zero-worker certification are not
complete by `G`, close the tranche as `FAIL_CLOSED`.

### Frozen controller and candidate-table contract

The no-launch controller uses the permanent engine-global reservation

    engine/q5_tranche.lock

and the fixed tranche directory

    engine/logs/q5-eight-hour-tranche-v1.

The lock is created with exclusive create and is never deleted or reset.
A crash, orphan transition intent, post-lock process drift, or incomplete
atomic transition closes the tranche; there is no automatic resume or retry.

The symmetric candidate table contains exactly the 465 rows `H=48,...,512`
in increasing order. Each row records the reduced-cell count, minimum and
maximum deterministic LPT lane weights, `b=bit_length(5760 H^10)`, exact
balance result, and source-based OEIS gate result. The frozen artifacts are:

- generator source SHA-256
  `78928E3074A0C50754990FAB6D73C72CDDD63B9EB79936902326FED38FAB766D`;
- reproducible executable SHA-256
  `E4B062DD5273E4510C359F55A39565EFC9FA8E0B19AD2818A5228CE87A663A6C`;
- table file SHA-256
  `C9CB415199BCB60513C8B41B15C866073F806C9DC7116320471FE7C38E3DAC0A`;
- canonical payload SHA-256
  `F3DEFAF9D3AA173C800E82D8AB62F24048CAFC8D6E8FB16B5CE00106A9791CF8`.

The executable is compiled with `--no-insert-timestamp`; two independent
builds must have the same hash. Before a selected main manifest is accepted,
its pinned `balanced_assignments` result must reproduce the selected cached
row exactly.

The primary-campaign handoff may continue only from a clean terminal
`NO_HIT_DECLARED_DOMAINS` with `ALL_COMPLETED` and 64 `NO_HIT` lanes, or a
clean terminal `TIMEOUT_INCOMPLETE` with `ORIGINAL_DEADLINE` and lane statuses
only in `{NO_HIT,TIMEOUT_INCOMPLETE}`. `HIT_VERIFIED` stops the Q5 route.
`RUNNING`, `FAILED`, `INTERRUPTED`, unknown or inconsistent status, candidate
signal, nonempty recovery stderr, artifact drift, survivor, cleanup
uncertainty, or inspection error fails closed.

Immediately before `T0`, the controller must take two identical live
read-only process/artifact snapshots at least 10 seconds apart. The second
must be at most 5 seconds old when the permanent lock is created. Process
identity is PID plus creation time, exact executable, argv, cwd, and parent
chain; PID alone is insufficient. A fresh post-lock snapshot is mandatory.
No production command may accept caller-supplied process evidence.

A separate public-status artifact must be no more than five minutes old when
the selected main manifest is finalized. It binds the live Asiryan, A046881,
and Formal Conjectures observations. Any non-open result blocks launch.

### 5. Exit condition

Do not launch if calibration disagrees, the manifest overlaps or omits work,
the active campaign still owns search processes, or the current-status gate
fails.

If selected, stop immediately on a dual-verified integer certificate and run
the novelty gate again. At eight hours stop all owned lanes. Complete declared
boxes without a certificate are recorded only as finite NO_HIT. Any partial
box is TIMEOUT_INCOMPLETE. Do not infer nonexistence, extend the same box, or
replace the missing Z-square lift by a rank or density surrogate.

## Current-status and priority snapshot

- Valery Asiryan, arXiv:2512.11072v3 (15 March 2026), states that the
  nontrivial positive problem remains open and that Jacobian rank does not
  settle torsor lifting and the square, integrality, and positivity conditions:
  https://arxiv.org/abs/2512.11072
- OEIS A046881, updated 19 July 2026, still has no n=5 value:
  https://oeis.org/A046881

- Google DeepMind Formal Conjectures main commit
  `b8b5208aa5d01f5f91c49ca516bf09cae8d93693` still labels
  `Taxicab.taxicab_for_5_2_2` as research-open with `answer(sorry)`:
  https://github.com/google-deepmind/formal-conjectures/blob/b8b5208aa5d01f5f91c49ca516bf09cae8d93693/FormalConjectures/Wikipedia/Taxicab.lean
- Darmon--Merel rules out a repeated entry in a nontrivial positive witness:
  https://perso.imj-prg.fr/loic-merel/wp-content/uploads/merel-pub/winding.pdf
The status gate must be repeated immediately before a main launch and before
any publication claim.

## Phase-authoritative launch contract

This section is the machine-facing launch procedure. It supersedes the
historical commit snapshot above for launch decisions. Run all commands from
'E:\Projects\ErdosProblems'. None of the commands below may be reordered.
Manifest preparation and status collection do not launch a process.

### Launch-readiness root

The fixed file is
'problems_external\quintic_taxicab\engine\Q5_LAUNCH_READY.json'. It is created
once, outside the production controller, after the exact reviewed files and
test suite have been frozen. Its strict top-level keys are exactly:

    schema_version, kind, tranche_id, created_utc,
    artifacts, tests, referee_verdicts

The identity is schema version 1, kind 'q5-launch-readiness', and tranche id
'q5-eight-hour-tranche-v1'. 'artifacts' has exactly these six keys, each
mapping to the lowercase SHA-256 of the fixed engine file of the same name:

    q5_tranche.py
    q5_supervisor.py
    q5_manifest.py
    q5_manifest_transaction.py
    q5_public_status.py
    run_q5_supervisor_hidden.ps1

'tests' has exactly 'passed', 'failed', 'commands', 'test_files', and
'suite_sha256'; 'passed' is a positive integer, 'failed' is zero, and
'commands' contains exactly this one workspace-root command:

    python -m unittest -v problems_external.quintic_taxicab.engine.test_q5_manifest_supervisor problems_external.quintic_taxicab.engine.test_q5_tranche problems_external.quintic_taxicab.engine.test_q5_public_status problems_external.quintic_taxicab.engine.test_q5_manifest_transaction problems_external.quintic_taxicab.engine.test_q5_candidate_table problems_external.quintic_taxicab.engine.test_scan_torsor_exact problems_external.quintic_taxicab.engine.test_reference_enumerator problems_external.quintic_taxicab.engine.test_verify_certificate problems_external.quintic_taxicab.engine.test_verify_independent problems_external.quintic_taxicab.engine.test_pari_quartic_calibration

'test_files' is an object with exactly the ten corresponding basename keys;
each value is that file's lowercase SHA-256. The suite hash is lowercase
SHA-256 of canonical JSON for the exact object with keys 'passed', 'failed',
'commands', and 'test_files'. The controller rehashes all ten test files as
part of readiness validation.

'referee_verdicts' contains exactly two distinct objects with exact keys
'referee', 'verdict', and 'reviewed_readiness_sha256'. Both verdicts are
'LAUNCH_SAFE'. The reviewed hash is SHA-256 of canonical JSON for the exact
object with keys 'artifacts' and 'tests'. Thus a verdict binds both runtime
files and the executable test record. The controller rehashes all six runtime
files and pins the readiness file hash in the permanent tranche lock. There
is no command that manufactures a referee verdict.

### Public-status gate version 2

The only producer is:

    $py = (Get-Command python).Source
    & $py problems_external\quintic_taxicab\engine\q5_public_status.py collect

The fixed gate is
'logs\q5-eight-hour-tranche-v1\public_status_gate.json' below the Q5 engine.
Its exact keys are:

    schema_version, kind, checked_utc, expires_utc, problem_open,
    oeis_no_n5_value, formal_conjecture_open, formal_main_commit_sha,
    capture_dir, capture_set_sha256, sources, all_open

The identity is schema version 2 and kind 'Q5_PUBLIC_STATUS_GATE'. Validity is
exactly five minutes. The four ordered source roles are 'asiryan_arxiv',
'oeis_a046881', 'formal_conjectures_main_ref', and
'formal_conjectures_taxicab_raw'. Every source has exactly:

    role, requested_url, final_url, fetched_utc, http_status, content_type,
    etag, last_modified, content_path, content_size, content_sha256,
    observed_status, evidence

The main-ref response resolves the live main commit. The raw Taxicab source
URL must contain that 40-hex commit. Final HTTPS host and path are
role-specific and canonical. Exact response bytes and 'capture_index.json'
are stored in a new immutable capture directory. 'capture_set_sha256' is the
SHA-256 of canonical JSON for the ordered capture-index records. The command
atomically replaces the gate only after all four responses are captured and
classified. Its audit command rehashes every response, checks the exact
capture inventory, and reruns every classifier:

    & $py problems_external\quintic_taxicab\engine\q5_public_status.py audit --require-fresh

An explicit non-open observation produces a gate with 'all_open=false'.
Network, parsing, identity, redirect, or classification ambiguity fails
closed and leaves the previous gate unchanged.

### Phase authorization ticket

The controller creates, by exclusive create, exactly one ticket at:

    logs\q5-eight-hour-tranche-v1\authorizations\A.json
    logs\q5-eight-hour-tranche-v1\authorizations\B.json
    logs\q5-eight-hour-tranche-v1\authorizations\C.json
    logs\q5-eight-hour-tranche-v1\authorizations\D.json
    logs\q5-eight-hour-tranche-v1\authorizations\MAIN.json

Each ticket has exactly:

    schema_version, kind, tranche_id, phase, created_utc, expires_utc,
    state_path, state_sha256, manifest_path, manifest_file_sha256,
    manifest_payload_sha256, campaign_id, mode, search_mode, deadline,
    run_dir, readiness_path, readiness_sha256, public_status_path,
    public_status_sha256

The identity is schema version 1, kind 'q5-launch-authorization-v1', and the
fixed tranche id. Expiry is no later than five minutes after creation and no
later than the campaign deadline. Pilot public-status fields are null. MAIN
public-status fields pin the fresh version-2 gate. The supervisor holds the
ticket, state, plan, readiness, public gate where applicable, manifest, and
runtime artifacts under locked read handles while validating and running.
An expired or pre-existing ticket is not refreshed or overwritten.

### Per-run launch claim

The supervisor exclusively creates 'launch.lock' in the fixed phase run
directory before any worker spawn. Its exact keys are:

    schema_version, kind, campaign_id, manifest_payload_sha256,
    launch_readiness_sha256, authorization_sha256,
    authorization_expires_utc, supervisor_pid, claimed_utc

The identity is schema version 1 and kind 'Q5_TORSOR_LAUNCH_LOCK'. Its
manifest, readiness, and authorization hashes must equal the held validated
artifacts. 'claimed_utc' must be strictly earlier than
'authorization_expires_utc'. The supervisor checks expiry after the exclusive
claim and again before every spawn. The controller rehashes and semantically
revalidates the fixed ticket when accepting and auditing the terminal run.

### Sole launch, mutation, and terminal-evidence boundaries

The only normal import-facing route which can execute a search-worker
`subprocess.Popen` is `q5_supervisor.run_campaign`; the command-line launch
branch calls that same function. The complete authorized body is a local
closure and no module attribute exposes an authorized/test launcher.
`run_campaign` independently audits the exact manifest, runtime identity,
machine mutex, fixed phase ticket, current census, and a finite
`poll_seconds` in the closed interval 0.02 through 5.0 seconds.

The mutex serializes cooperating Q5 supervisors. Immediately before and after
each worker spawn the supervisor enumerates all relevant processes. A child is
registered as owned before the post-spawn census or stream close, so every
later exception terminates that child and records any survivor. A
non-cooperating external process can in principle exist entirely between two
process samples; the contract therefore certifies at most 64 owned/cooperating
workers and fail-closed detection, not an absolute atomic claim about arbitrary
external processes.

Before any successful terminal return, and again after the summary/final state
writes, the supervisor requires the run directory to be an exact flat
whitelist: the launch lock and state/summary, stdout and empty stderr for every
spawned lane, one result for every validated terminal producer, and at most one
canonical verified-candidate artifact. Missing, extra, directory, symlink,
reparse, or non-regular entries fail closed. The controller independently
derives the same whitelist, rehashes every member, and pins the exact spawned
lane set and stdout/stderr/result maps.

The public controller mutators have only their documented phase arguments; no
caller-supplied clock, sleeper, census, or evidence hook is accepted. Its
high-level lock, initial-state, transition, and fail-closed writers are
closure-private. A `VERIFIED_HIT` state contains a source binding to exactly
one revalidated magic, pilot, or MAIN evidence record; a bare hit cannot pass
state loading or audit. Every context load also revalidates the pinned
predecessor campaign and frozen runtime hashes. MAIN pre-commit and later audit
replay the raw public-status captures, launch ticket/state pin, exact terminal
inventory, and a fresh clean live census.

### Exact controller and pilot commands

Initialize the shell once:

    Set-Location E:\Projects\ErdosProblems
    $engine = (Resolve-Path problems_external\quintic_taxicab\engine).Path
    $py = (Get-Command python).Source

After the readiness file exists and before any phase artifact exists:

    & $py "$engine\q5_tranche.py" start
    & $py "$engine\q5_tranche.py" audit

For each pilot, use the indicated exact values and complete one row before
starting the next:

    phase  campaign                    mode              search_mode
    A      q5-tranche-v1-pilot-A       CALIBRATION_ONLY  audit_signed_u_both_y
    B      q5-tranche-v1-pilot-B       CALIBRATION_ONLY  canonical_positive_u_positive_y
    C      q5-tranche-v1-pilot-C       CALIBRATION_ONLY  canonical_positive_u_positive_y
    D      q5-tranche-v1-pilot-D       CALIBRATION_ONLY  canonical_positive_u_positive_y

Set '$phase', '$campaign', and '$searchMode' to one row, then run:

    & $py "$engine\q5_manifest_transaction.py" build --phase $phase
    & $py "$engine\q5_tranche.py" authorize $phase
    $base = "$engine\logs\q5-eight-hour-tranche-v1\pilot_$phase"
    $manifest = "$base\manifest.json"
    $ticket = "$engine\logs\q5-eight-hour-tranche-v1\authorizations\$phase.json"
    $envelope = Get-Content -Raw -LiteralPath $manifest | ConvertFrom-Json
    & "$engine\run_q5_supervisor_hidden.ps1" -Python $py -Manifest $manifest -Authorization $ticket -ExpectedDigest ([string]$envelope.payload_sha256) -CampaignId $campaign -Mode CALIBRATION_ONLY -SearchMode $searchMode -Launch

Do not issue the next command until that supervisor is terminal and its owned
process census is empty. Then run the phase-specific acceptance and audit:

    & $py "$engine\q5_tranche.py" accept-pilot $phase
    & $py "$engine\q5_tranche.py" audit

The only legal sequence is A, then B, then C, then D. A verified hit stops the
sequence. A timeout, anomaly, nonempty stderr, survivor, artifact drift, or
fail-closed result also stops it.

### Exact selection and MAIN commands

After Pilot D acceptance, READY_SELECTION has one fixed 'state.updated_utc'
anchor. Preview, MAIN manifest construction, status collection, and finalize
must complete within 300 seconds of that anchor:

    $preview = (& $py "$engine\q5_tranche.py" preview) | ConvertFrom-Json

If '$preview.selected_h' is null, run finalize and stop without a main launch:

    & $py "$engine\q5_tranche.py" finalize
    & $py "$engine\q5_tranche.py" audit

Otherwise run, without recomputing or editing '$preview.selected_h':

    & $py "$engine\q5_manifest_transaction.py" build --phase MAIN --selected-h ([int]$preview.selected_h)
    & $py "$engine\q5_public_status.py" collect
    & $py "$engine\q5_tranche.py" finalize
    & $py "$engine\q5_tranche.py" authorize MAIN
    $base = "$engine\logs\q5-eight-hour-tranche-v1\main"
    $manifest = "$base\manifest.json"
    $ticket = "$engine\logs\q5-eight-hour-tranche-v1\authorizations\MAIN.json"
    $envelope = Get-Content -Raw -LiteralPath $manifest | ConvertFrom-Json
    & "$engine\run_q5_supervisor_hidden.ps1" -Python $py -Manifest $manifest -Authorization $ticket -ExpectedDigest ([string]$envelope.payload_sha256) -CampaignId q5-tranche-v1-main -Mode SELECTED_MAIN -SearchMode canonical_positive_u_positive_y -Launch

After the MAIN supervisor is terminal and its owned process census is empty:

    & $py "$engine\q5_tranche.py" accept-main
    & $py "$engine\q5_tranche.py" audit

### Transaction and idempotence rules

'q5_manifest_transaction.py' accepts only A, B, C, D, or MAIN and derives all
bounds, modes, deadline ceilings, artifact paths, and canonical destinations
from the fixed tranche state and plan. It constructs all 64 lane files and the
envelope in a same-parent staging directory, regenerates every lane TSV using
a deadline no later than min(manifest created time plus the local limit, S),
rebinds every embedded path, rechecks the unchanged state bytes, and commits
by one directory rename. Full 'q5_manifest.audit_manifest' must pass after the
rename.

If the canonical phase directory already contains the exact valid manifest,
the build command returns 'REUSED' without writing. A different or partial
canonical directory fails closed. A handled exception or keyboard interrupt
removes only the current uncommitted staging directory. A staging directory
left by process termination is preserved for inspection and blocks retry; it
is never treated as a manifest.

'start' is not idempotent: its global lock is permanent. 'authorize' is not
idempotent: its fixed ticket is exclusive-create. Supervisor launch is not
idempotent: its fixed run directory and launch lock are exclusive. Acceptance
commands are issued exactly once; later 'audit' calls revalidate the accepted
identical terminal record without rerunning a search. A public-status
collection may be repeated only before MAIN finalize because each successful
capture is immutable and the gate replacement is atomic. Once the selection
report is frozen, its embedded gate hash and the fixed gate file must remain
identical through authorization, launch, acceptance, and audit. No file may be
deleted or rewritten to manufacture a retry.

