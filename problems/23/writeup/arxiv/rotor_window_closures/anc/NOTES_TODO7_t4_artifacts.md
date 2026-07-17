# NOTES — TODO-7: five t=4 census artifacts shipped in anc/t4_artifacts/

Date: 2026-07-17. Agent: Claude (Fable 5), TODO-7 subagent. No .tex, CLAIMS_LEDGER.md,
or anc/SHA256SUMS file was modified; this note and anc/t4_artifacts/ are the only additions.

## What was shipped

The five canonical JSON artifacts of the sixteen-atom (t=4) census, copied byte-for-byte
from the 2026-07-17 referee replay (this machine, Python 3.12.4, NetworkX 3.6.1, geng from
`tools/nauty2_8_9/geng.exe`, archived scripts from
`problems/23/archive/tmp_text_sources_20260712/fanout/r42_graph_specific_exclusion/`;
replay tree preserved in the session scratchpad under
`t4_verifyrun/` and `replay/tmp/fanout/r42_graph_specific_exclusion/`).

Total size: 1,977,105 bytes (~1.9 MB), well under the 100 MB inclusion threshold.

## Hash discipline (two different hashes per file — do not confuse them)

Each artifact embeds a field `canonicalSha256` = SHA-256 of
`json.dumps(payload, sort_keys=True, separators=(",", ":"))` computed BEFORE the field is
inserted (see `enumerate_t4_support_graphs.py` lines 179-180). The hashes printed in
`sections/sixteen_atom_closure.tex` (verification record) and quoted in the review are
these EMBEDDED canonical hashes, not whole-file hashes. The whole-file hashes below are
what belongs in anc/SHA256SUMS (integrator action).

| file (anc/t4_artifacts/) | bytes | embedded canonicalSha256 (matches paper) | whole-file SHA-256 (for SHA256SUMS) |
|---|---|---|---|
| t4_support_graph_census.json | 20875 | 40f16a84559ace4827e366f152026f2b7868bdaed31ff9afb36184a29b48046d | e4401d000e76d7520c04064ea0d9d1f36031ebd6f10c1bdf476acc8919a2ce3c |
| t4_atom_circuit_census.json | 1951880 | 302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652 | 022648522760c5c458604a8f97c08bac025cb3a5163590c8eed019c2ba48c752 |
| t4_profile_transition_census.json | 1359 | b464682b4142a9db2396dc39ac9a0ffd8ff638aba1b9270734667c8f0a543114 | 51e7dab2b045cf69045433060b86fd1ad77c9020baabf3c84d6f8479c234861a |
| t4_cross_outer_exclusion.json | 1304 | 79db75b95e8401064f1b6159bb980ee0149f0fb3a602a607306a7f0e501a5d49 | 2b2e669a78ca20fd4859fdb190c931115058c3c6c59702452d4a3c0c4aa78f4f |
| t4_support_circuit_hit.json | 1687 | 5b386cd90b795bf1e6f8f174e21aa559e37c9f682e5dff373dae6bf74f3b9641 | 50bf503f6ead32f0b1fe9e0add98f3be065c6de488756d45b3a20f851cbd4623 |

All five embedded canonical hashes were independently RECOMPUTED (sort-keyed compact JSON,
sha256, exact integer/string arithmetic) on the shipped copies and equal both the embedded
field and the values printed in sections/sixteen_atom_closure.tex. Verdict line:
`SHIPPED_COPIES_ALL_FIVE_CANONICAL_HASHES_MATCH` (exit 0).

## Verifier replays against these exact artifacts (2026-07-17, this machine)

Run in a clean scratch tree (scripts + artifacts side by side, geng at
`<root>/tools/nauty2_8_9/geng.exe` as the scripts' relative layout requires). All exit 0:

- `verify_t4_support_census.py` -> `"verdict": "PASS_INDEPENDENT_NETWORKX_SUPPORT_CENSUS"`,
  graphs=153978, ownerEmbeddings=34, candidatePayloadsEqual=true.
- `verify_t4_atom_census.py` -> `"verdict": "PASS_INDEPENDENT_NETWORKX_ATOM_CENSUS"`,
  hits=576, countsEqual=true, hitSetsEqual=true.
- `verify_t4_profile_exclusion.py` -> `"verdict": "PASS_T4_RAW_MIDDLE_SWAP_EXCLUSION"`,
  rawMiddleSwaps=0, forced histograms {8:255, 9:193, 10:101, 11:26, 12:1} for both v and m,
  supportIsomorphismTypes=4.
- (bonus) `verify_t4_cross_outer_exclusion.py` -> `"verdict": "PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY"`,
  totalLiveCrossOuterCandidates=0, multiplicities 180/190/190/16; the artifact it REGENERATED
  is byte-identical to the shipped t4_cross_outer_exclusion.json (determinism confirmed).
- (bonus) `verify_t4_support_circuit.py` -> `"verdict": "PASS_ABSTRACT_SUPPORT_CIRCUIT"`,
  properSubsetsChecked=65534, worstProperDefect=0, tightProperSubsets=19, minEdgeDegree=2.

## Integrator actions recommended (NOT applied here)

1. main.tex, Section "Reproducibility" (currently lines 215-220), replace the paragraph
   OLD: "The five canonical JSON artifacts of the census carry the embedded canonical
   hashes printed in the verification record of Section~\ref{sec:t4}; the entire pipeline,
   all five artifacts, and the \texttt{geng} counts of Table~\ref{tab:t4:geng} were
   regenerated bit-exactly from the archived scripts on 2026-07-17."
   NEW: "The five canonical JSON artifacts of the census are included in
   \texttt{anc/t4\_artifacts/} and carry the embedded canonical hashes printed in the
   verification record of Section~\ref{sec:t4}; the entire pipeline, all five artifacts,
   and the \texttt{geng} counts of Table~\ref{tab:t4:geng} were regenerated bit-exactly
   from the archived scripts on 2026-07-17."
2. anc/SHA256SUMS: append the five whole-file entries (format `<sha256>  t4_artifacts/<name>`)
   using the whole-file column of the table above.
3. Optionally note in anc/README.md that the verify_t4_*.py scripts expect the artifacts in
   the SAME directory as the scripts; with artifacts in t4_artifacts/ a reproducer should
   either copy them beside the scripts or run the scripts from a merged scratch copy
   (geng resolved at `HERE.parents[2]/tools/nauty2_8_9/geng.exe` by verify_t4_support_census.py).
