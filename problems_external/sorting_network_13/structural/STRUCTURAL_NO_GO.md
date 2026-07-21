# N=13, L=44 structural attack: NO-GO

Date: 2026-07-18T15:28:41+03:00

## Result

No 44-comparator sorting network was produced from the six verified L45 seeds. The output file `candidate_L44.net` is absent, so the two-verifier certificate stage was not triggered.

The expanded single-thread search ended with `NO_HIT_EXHAUSTED` after 217.498 seconds. Its exact terminal record was:

```json
{"status":"NO_HIT_EXHAUSTED","hit":false,"tested":77836090,"duplicates":49972467,"witness_rejected":77835763,"full_rejected":327,"witnesses":327,"elapsed_s":217.498,"phase_tests":{"perm-support-2to5":17202510,"delete-double-half-r6":8485360,"delete-replace-global":598289,"commute-local-exact":15289220,"delete-double-replace-r2":8935269,"delete-local-swap-r8":29817,"delete-replace-r8":295344,"perm-random-global":27000000,"local-exact":11,"single-delete":270}}
```

Each retained network was rejected either by a concrete 13-bit witness or by an exhaustive scan of all 8192 zero-one inputs. The search covered direct deletion, exact local function rewrites on at most four channels, bounded one- and two-comparator edits, all channel permutations with support at most five, 100,000 deterministic random full channel permutations, and 50,000 trace-equivalent commutation rounds.

## Concrete obstruction

**Trace-deletion lemma.** Fix a comparator occurrence in a comparator word. If a second word is obtained by repeatedly swapping adjacent independent comparators, then deleting the fixed occurrence before or after those swaps gives words that are again related by swaps of adjacent independent comparators.

Proof: inspect one generating swap. If it does not involve the deleted occurrence, the same swap remains after deletion. If it does involve that occurrence, deletion removes the swap. Induct over the swap sequence. Independent comparators commute as functions, so the two deleted networks compute the same function.

All 45 single deletions from each of the six seeds were tested (`single-delete: 270`), and none sorts all 8192 inputs. Therefore no sequence consisting only of independent-comparator commutations followed by deletion of one original comparator can produce an L44 sorter from any of these six seeds.

This is a route obstruction, not a nonexistence proof for N13/L44. Any successful construction from these seeds must make a non-commutation-equivalent topology change; the enumerated bounded rewrite and relabeling neighborhoods also yielded no certificate.
