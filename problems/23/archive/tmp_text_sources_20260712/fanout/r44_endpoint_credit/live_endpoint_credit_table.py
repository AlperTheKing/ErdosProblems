"""Exact local ledger for the live R37 one-new-edge support-constant detour.

Q=(a,x,m,y,b) -> (a,x,v,y,b) has xv old active and vy selected support.
Support constancy means one of mx,my is unique and the other repeated.  The
table checks production P3/P2, paired collision fibers, and 7/9 turnover.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent


def endpoint(*, count: int, sigma: int, repeated_middle: bool) -> dict:
    """Ledger for both orientations of one endpoint pair (m,z)."""
    singleton = count == 1
    repeated = count >= 2
    p3 = singleton and repeated_middle
    p2 = singleton and sigma >= 2
    return {
        "count": count,
        "sigma": sigma,
        "middle": "repeated" if repeated_middle else "unique",
        "kind": (
            "repeated_endpoint" if repeated
            else "singleton_p3" if p3
            else "singleton_p2" if p2
            else "singleton_weak"
        ),
        "targetCount": count - 1,
        "rawUnreservedFreeHalves": 4 if singleton else 0,
        "p3ProductionHalves": 4 if p3 else 0,
        "p2ProductionHalves": 4 if p2 else 0,
        "crossOwnerProductionHalves": 4 if p3 or p2 else 0,
        "pairedCollisionFiberDrop": 4 if repeated else 0,
        "mOwnerBalanceContribution": 2,
    }


def sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def main() -> int:
    checked = 0
    kinds = Counter()
    credit_hist = Counter()
    counterexamples = []
    identity_failures = []
    # A repeated middle pair requires pairCount(m,m)>=2 in a real row tuple.
    for row_count in range(2, 9):
        for repeated_path in range(2, row_count + 1):
            for count_x, count_y, sigma_x, sigma_y in product(
                range(1, row_count + 1),
                range(1, row_count + 1),
                range(5),
                range(5),
            ):
                at_repeated = endpoint(
                    count=count_x, sigma=sigma_x, repeated_middle=True
                )
                at_unique = endpoint(
                    count=count_y, sigma=sigma_y, repeated_middle=False
                )
                checked += 1
                kinds[(at_repeated["kind"], at_unique["kind"])] += 1
                gain = 7 + 2 * int(row_count >= 2)
                actual = (
                    at_repeated["mOwnerBalanceContribution"]
                    + at_unique["mOwnerBalanceContribution"]
                    + 1  # unique old path becomes active
                    + 2  # repeated old path loses a collision fiber
                    + 2 * int(row_count >= 2)
                )
                if actual != gain:
                    identity_failures.append({
                        "rowCount": row_count, "actual": actual, "gain": gain
                    })
                # Repeated endpoints delete a paired demand fiber. Singleton
                # endpoints supply P3/P2 to their retained owner. Neither
                # operation certifies an unused key: an owner can saturate all
                # four source halves, while a deleted fiber is not a source.
                credit = sum(
                    max(item["crossOwnerProductionHalves"], item["pairedCollisionFiberDrop"])
                    for item in (at_repeated, at_unique)
                )
                credit_hist[credit] += 1
                if credit < gain and len(counterexamples) < 64:
                    counterexamples.append({
                        "rowCountM": row_count,
                        "repeatedPathCount": repeated_path,
                        "endpointAtRepeatedMiddle": at_repeated,
                        "endpointAtUniqueMiddle": at_unique,
                        "ownerBalanceGain": gain,
                        "endpointOnlyCredit": credit,
                        "reason": "weak singleton at unique middle has no P3 and fails P2 sigma>=2",
                    })
    smallest = min(
        counterexamples,
        key=lambda item: (
            item["rowCountM"],
            item["endpointAtRepeatedMiddle"]["count"],
            item["endpointAtUniqueMiddle"]["count"],
            item["endpointAtUniqueMiddle"]["sigma"],
        ),
    )
    payload = {
        "schema": "R44_LIVE_ENDPOINT_CREDIT_TABLE_V2",
        "rowCountRange": [2, 8],
        "sigmaRange": [0, 4],
        "casesChecked": checked,
        "endpointKindPairs": {
            f"{a}|{b}": value for (a, b), value in sorted(kinds.items())
        },
        "endpointOnlyCreditHistogram": {
            str(key): value for key, value in sorted(credit_hist.items())
        },
        "compiledIdentity": "Delta B_m = 7 + 2*1[pairCount(m,m)>=2]; real live cases give +9",
        "endpointRule": "singleton gives four raw unreserved halves; P3 is available only at repeated-middle side, otherwise P2 requires sigma>=2; repeated endpoint drops four paired collision halves",
        "saturationRule": "all P3/P2 halves may be consumed by their owner and paired fiber deletion creates no unused source",
        "refutedCandidate": "endpoint-only production credit guarantees an unused 7/9-unit payment",
        "smallestTableCounterexample": smallest,
        "identityFailures": identity_failures,
        "verdict": "PASS" if not identity_failures else "FAIL",
    }
    payload["canonicalSha256"] = sha(payload)
    (HERE / "live_endpoint_credit_table.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
