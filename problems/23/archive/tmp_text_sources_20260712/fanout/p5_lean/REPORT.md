# Pattern 5 Lean report

Timestamp: 2026-07-11T19:06:07.5822614+03:00

## Scope

- Created only `problems/23/lean/Erdos23Delta0/Gamma/CheckedQuiescentAttachmentBaseTerminal.lean`.
- Added this report, `Probe.lean`, build logs, and private object-cache artifacts under `tmp/fanout/p5_lean/`.
- Did not edit or revert any pre-existing working-tree change.
- This module does not claim Erdos #23, universal Pattern-5 matching, or a typed FullBank adapter.

## Interface

- `QuiescentAttachment.TerminalData`: two `Fin G.n` source endpoints, half bit, owner, and two active attachments.
- `CheckedQuiescentAttachmentBaseTerminal`: 13 checked geometric fields.
- `QuiescentAttachment.TerminalData.switchSet`: exact union of the two quiescent components.
- `CheckedQuiescentAttachmentBaseTerminal.term`: existing `CanonicalCollisionHall.FreeHalf` key.
- `checkQuiescentAttachment`: exact Bool reflection of the semantic predicate.
- `quiescentAttachmentTerminal_sound`: proves owner eligibility, scoped unreservedness, and max-cut switch nonnegativity.
- `TerminalConsumerSound`: explicit hypothesis required to interpret the terminal in any future matching or typed-bank consumer.

`checkQuiescentAttachment` is noncomputable because the current API exposes `ActiveOwner` and graph reachability as semantic propositions. It is exact and kernel-checked, but this module does not pretend to provide an executable component-label certificate.

## Hashes

- Git HEAD: `da17b8d73c017ea6d9d829dae4f3c4d074926bfd`
- Lean source SHA-256: `93DB65E96BF3588F3C7606676F8B1AA22E4FB837512014228A06DEC10F71E181`
- Lean object SHA-256: `5C3194527457C611AD4AB2233A5B9CCBAA7DBCED56E275D81AFB6E2DD885FA93`
- Probe SHA-256: `96B172AB96AE96E9CB77177AE5C666EFF31B6FC67EF2F7A0E8FAC5BAB51705F3`
- Current `ActiveScopedMinimumExchange.lean` SHA-256: `6AA3FDD19D15A4A5231494C6B92F3659BFCF13CFA1F2D900B6F3857EC1CF019D`
- Rebuilt dependency object SHA-256: `993235814876EFB0B04261A03583D7EA49DB735BBD579AB12321280708C6B473`

## Build

- Existing base cache: `tmp/claude_lean_o_base_v1`.
- Current dependency rebuild: rc `0`.
- Final target build in compact private cache: rc `0`; log `target_build.log`.
- Public import and axiom probe: rc `0`; log `probe_build.log`.
- `git diff --check`: rc `0`.
- Forbidden-token scan for `sorry`, `admit`, `native_decide`, and declared `axiom`: clean.

One sparse-cache attempt returned rc `1` because Lean resolves transitive imports within one `Erdos23Delta0` package root. The final compact cache includes the seven required transitive objects and both final builds return rc `0`.

## Axioms

- `checkQuiescentAttachment_eq_true_iff`: `[propext, Classical.choice, Quot.sound]`
- `checked_of_checkQuiescentAttachment_eq_true`: `[propext, Classical.choice, Quot.sound]`
- `CheckedQuiescentAttachmentBaseTerminal.owner_relation`: `[propext, Quot.sound]`
- `CheckedQuiescentAttachmentBaseTerminal.term_unreserved`: `[propext, Quot.sound]`
- `switchSet_loss_nonneg`: `[propext, Classical.choice, Quot.sound]`
- `quiescentAttachmentTerminal_sound`: `[propext, Classical.choice, Quot.sound]`
- `consumer_accepts_of_check`: `[propext, Classical.choice, Quot.sound]`
- `checkQuiescentAttachment_sound`: `[propext, Classical.choice, Quot.sound]`

No probed declaration depends on `sorryAx`.
