"""Exhaust the local endpoint ledger for a support-constant two-edge detour.

For Q=(a,x,m,y,b) -> (a,x,v,y,b), support constancy fixes
pairCount(m,x)=pairCount(m,y)=1.  This program has no graph search in it: it
enumerates the remaining integral multiplicities and pair-switch slacks and
checks the exact ledger identities used in R44.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent


def collision_halves(count: int) -> int:
    """CollisionHalf cardinality for one ordered owner/other fiber."""
    return 2 * max(count - 1, 0)


def endpoint_case(count: int, sigma: int) -> dict:
    """The exact alternative for one endpoint z in {a,b}.

    A singleton occurrence becomes two ordered zero bases.  They have four
    physical halves in total and are P2/common-blue arcs to the retained
    owner only at the production threshold sigma >= 2.  A repeated occurrence
    removes one CollisionHalf fiber in each orientation instead.
    """
    singleton = count == 1
    repeated = count >= 2
    p2_keys = 4 if singleton and sigma >= 2 else 0
    paired_fiber_drop = 4 if repeated else 0
    return {
        "count": count,
        "sigma": sigma,
        "kind": (
            "singleton_strong" if singleton and sigma >= 2
            else "singleton_weak" if singleton
            else "repeated"
        ),
        "targetCount": count - 1,
        "orderedZeroBases": 2 if singleton else 0,
        "rawUnreservedFreeHalves": 4 if singleton else 0,
        "productionCommonBlueHalves": p2_keys,
        "pairedCollisionFiberDrop": paired_fiber_drop,
        "mOwnerBalanceContribution": 2,
        "saturableProductionCredit": p2_keys,
    }


def canonical_sha(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    checked = 0
    kinds = Counter()
    raw_credit = Counter()
    candidate_failures = []
    local_identity_failures = []

    # r is pairCount(m,m); endpoint counts cannot exceed r.  This range is
    # deliberately broader than any small real cage needed by the claim.
    for row_count in range(1, 9):
        balance_gain = 6 + 2 * int(row_count >= 2)
        for count_a, count_b, sigma_a, sigma_b in product(
            range(1, row_count + 1),
            range(1, row_count + 1),
            range(5),
            range(5),
        ):
            a = endpoint_case(count_a, sigma_a)
            b = endpoint_case(count_b, sigma_b)
            checked += 1
            kinds[(a["kind"], b["kind"])] += 1

            # R43's owner-m calculation: endpoints contribute four, the two
            # newly active path pairs retain their half-one keys (two), and
            # the diagonal deletes one collision fiber exactly when r >= 2.
            local_balance = (
                a["mOwnerBalanceContribution"]
                + b["mOwnerBalanceContribution"]
                + 2
                + 2 * int(row_count >= 2)
            )
            if local_balance != balance_gain:
                local_identity_failures.append({
                    "rowCount": row_count,
                    "countA": count_a,
                    "countB": count_b,
                    "sigmaA": sigma_a,
                    "sigmaB": sigma_b,
                    "balance": local_balance,
                    "expected": balance_gain,
                })

            # This is the most optimistic endpoint-only cross-owner budget:
            # singleton credit is a production P2 resource only when strong;
            # repeated credit is a paired demand deletion.  It does not count
            # the owner's own P1 balance as a transferable unused key.
            external_credit = (
                a["productionCommonBlueHalves"]
                + b["productionCommonBlueHalves"]
                + a["pairedCollisionFiberDrop"]
                + b["pairedCollisionFiberDrop"]
            )
            raw_credit[external_credit] += 1
            if external_credit < balance_gain and len(candidate_failures) < 64:
                candidate_failures.append({
                    "rowCountM": row_count,
                    "endpointA": a,
                    "endpointB": b,
                    "ownerBalanceGain": balance_gain,
                    "endpointOnlyCredit": external_credit,
                    "reason": "endpoint P2/fiber ledger does not pay the m-owner gain",
                })

    smallest = min(
        candidate_failures,
        key=lambda item: (
            item["rowCountM"],
            item["endpointA"]["count"],
            item["endpointB"]["count"],
            item["endpointA"]["sigma"],
            item["endpointB"]["sigma"],
        ),
    )
    result = {
        "schema": "R44_ENDPOINT_CREDIT_TABLE_V1",
        "rowCountRange": [1, 8],
        "sigmaRange": [0, 4],
        "casesChecked": checked,
        "endpointKindPairs": {
            f"{left}|{right}": value
            for (left, right), value in sorted(kinds.items())
        },
        "endpointOnlyCreditHistogram": {
            str(key): value for key, value in sorted(raw_credit.items())
        },
        "exactLocalIdentity": (
            "Delta B_m = 6 + 2*1[pairCount(m,m)>=2]; "
            "each endpoint pair contributes exactly 2 to B_m"
        ),
        "productionRule": (
            "a singleton endpoint supplies its four paired common-blue halves "
            "to x or y only when sigma(m,z)>=2"
        ),
        "pairedFiberRule": (
            "a repeated endpoint removes 2 CollisionHalves for owner m and "
            "2 for owner z, hence paired demand drop 4"
        ),
        "refutedCandidate": (
            "endpoint-only P2/fiber credit >= Delta B_m without a matching "
            "non-saturation hypothesis"
        ),
        "smallestTableCounterexample": smallest,
        "localIdentityFailures": local_identity_failures,
        "verdict": "PASS" if not local_identity_failures else "FAIL",
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "endpoint_credit_table.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
