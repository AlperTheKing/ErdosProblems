# R29 global selector-trade gate: INDETERMINATE FROM AVAILABLE ARTIFACTS

## Verdict

The workspace does not contain the claimed R29 2943 graph, its 676 selector-row lists, the selected tuple, or a deterministic constructor. Therefore neither “30811 is globally minimal” nor its negation can be certified for the actual instance. Likewise, hub/descendant deactivation cannot be decided.

This is not merely a missing convenience. `audit.py` gives an exact information-theoretic falsifier: two permutation-symmetric compressed landscapes satisfy every numerical selector-trade fact recorded in the R29 archive, but have opposite global answers.

## Exact compressed countermodels

Let `k` be the number of changed selectors, `0 <= k <= 676`. This is the orbit state under `S_676`; exhaustive DP is the scan of all 677 integer states.

* A: `S_A(k)=30811+2k`. Its unique global minimum is 30811 at `k=0`; no hub deactivates.
* B: `S_B(k)=30811+2k` for `k<676`, while `S_B(676)=0`; the hub flag activates exactly at `k=676`. Its explicit descending tuple is: choose any fixed nonbaseline row for every one of the 676 selectors.

Both have baseline 30811, exactly `676*679=459004` nontrivial Hamming-one replacements, and Hamming-one minimum 30813. Thus the archived local facts do not determine any multi-row interaction.

## Reproduction and certificate

Run `python tmp/fanout/r29_gate/d08/audit.py`. It uses integer arithmetic only, asserts all 677 states in each model, and writes `certificate.json`.

The certificate records SHA256 hashes of both source archives. Artifact hashes after generation:

* populated below by `hashes.txt` (SHA256 output for `audit.py`, `certificate.json`, `report.md`)

## Falsifiers

Any one of the following would falsify the indeterminacy conclusion: (1) a canonical graph plus cut and all shortest selector rows; (2) a deterministic constructor whose output hash matches claimed `00186166...`; or (3) a complete table/formula for scoped score and active components for arbitrary simultaneous selector choices. Repository-wide targeted search found none.

## Proof gaps

No claim about the actual global minimum is proved. Model B's tuple is a logical countermodel tuple, not a tuple in the absent R29 row serialization. The archive's truncated SHA prefix cannot identify or reconstruct the missing object. The exact scoped-score definition and component activation rule are also absent from the R29 archive, preventing an instance-level DP transition function.
