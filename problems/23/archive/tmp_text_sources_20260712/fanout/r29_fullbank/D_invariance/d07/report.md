# Hostile referee report: R29 selector invariance

## Verdict

No falsifier exists under the exact conventions implemented by the current R29 owner-Hall reconstruction. The universal claim is true for the canonical `N=2943` incidence object:

```text
for every choice in the product of 676 selector families of size 680,
demand({0,1,2}) = 19953,
|sameFirst/sameOwner union rowCompanion| = 19925.
```

The exact split is collision `3*6650`, HitNeed `3*1`, sameFirst-only `3*5775=17325`, rowCompanion-only `2600`, overlap `0`, with exactly three removed reservations. Hence the defect is `19953-19925=28`.

## Lemma (explicit hypotheses)

Let the graph, bad edges, rigid rows, selector families, ordered FreeHalf source identity, signs, active-scope rules, and reservation rule be exactly those reconstructed by `r29_lead_gate.py` and `rebuild_owner_hall.py`. Assume:

1. each of the 676 chosen selector rows is one of the 680 shortest rows for its designated atom;
2. every selector option avoids owners `H={0,1,2}` and every edge incident with `H`;
3. the 676 fixed traffic rows contain every owner and give each owner the same 55-vertex pair-support;
4. the fixed cable/seed/circuit vertices and non-row edges keep `H` in an active component containing a bad edge for every selector tuple;
5. source IDs are set-valued ordered triples `(x,y,half)`, `half in {0,1}`, unioned across owners and source reasons; reversal is distinct;
6. the `half=0` source is removed exactly when its normalized edge is active and its first endpoint is active; Nat subtraction in HitNeed is truncated.

Then selector choices cannot change owner row-load, owner pair counts, owner-incident row support, owner active status, owner demanded degree, owner companion sets, or the three reservations. Collision, HitNeed, sameFirst, and rowCompanion predicates therefore have identical inputs for every tuple, proving the two displayed constants.

## Exact audit

`verify.py` enumerates all `676*680=459680` selector options and checks every row has zero intersection with the owner set. This is the decisive per-option dependency test, not sampling. It also checks every family has exactly 680 rows and exactly four non-anchor rows.

Eight complete simultaneous signatures are then rebuilt from scratch: all-anchor; each of the four all-local ranks; alternating local ranks; a left-anchor/right-local split; and the four extreme families local with all others anchor. Every signature returns the same demand, reach, split, activity, degree, load, source-ID uniqueness, and reservation count.

The simultaneous tests are adversarial checks, while universality follows from the lemma: arbitrary combinations cannot create an owner occurrence or owner-incident support edge because none occurs in any individual option. The fixed cable supplies the owner component independently of all selector rows.

## Referee audit of conventions

- Counting is over distinct ordered source triples, not a multiset of owner claims. Duplicate triples across owners/reasons are collapsed by dictionary key and retain bit masks only as provenance.
- `(x,y,h)` and `(y,x,h)` are distinct; `h=0` and `h=1` are distinct.
- sameFirst excludes `y=owner` and nonzero owner-pair entries before reservation removal.
- rowCompanion uses ordered distinct companion pairs, requires zero selected-row co-occurrence and nonnegative signed degree, then applies the same reservation rule.
- Active scope is recomputed from selected vertices and blue edges absent from selected-row support; components qualify only when they contain both ends of a bad edge.
- The three reservations are removed before the reason/owner union. There are no sameFirst/rowCompanion duplicate IDs in the final split (`both=0`).
- Source vertex labels are canonical integers. The verifier checks final key uniqueness; repeated provenance cannot inflate `19925`.

## Replay

From this directory:

```powershell
python verify.py > verify.out
python make_hashes.py
Get-FileHash -Algorithm SHA256 -Path prompt.txt,verify.py,verify.out,result.json,report.md,make_hashes.py
```

All arithmetic is integer/set arithmetic. `result.json` is the machine-readable audit; `hashes.sha256` authenticates local deliverables. The canonical lead input hash recorded by the verifier is `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`.

## Scope warning

This lemma certifies only the current sameFirst/sameOwner plus rowCompanion FreeHalf pool. It does not assert invariance for additional FullBank source kinds (Door, vertexSlack, c5Base, prune) whose legality may depend on attachment boundaries or capacities not used in this count.
