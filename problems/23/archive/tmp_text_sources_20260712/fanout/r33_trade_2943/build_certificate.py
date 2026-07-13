"""Build the exact R33 2943 collision-only trade certificate."""

from __future__ import annotations

import json
from pathlib import Path

from certificate_core import HERE, build_certificate


OUTPUT = HERE / "certificate.json"


def main() -> None:
    certificate = build_certificate()
    OUTPUT.write_text(
        json.dumps(certificate, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    summary = {
        "certificate": str(OUTPUT),
        "fromTupleId": certificate["endpoints"]["baselineLocal"]["tuple"][
            "tupleId"
        ],
        "toTupleId": certificate["endpoints"]["metadataAnchor"]["tuple"][
            "tupleId"
        ],
        "fromDemand": certificate["endpoints"]["baselineLocal"]["matching"][
            "demand"
        ],
        "fromMaximum": certificate["endpoints"]["baselineLocal"]["matching"][
            "maximumCoherentMatchingSize"
        ],
        "fromDefect": certificate["endpoints"]["baselineLocal"]["matching"][
            "collisionDefect"
        ],
        "toDemand": certificate["endpoints"]["metadataAnchor"]["matching"][
            "demand"
        ],
        "toMaximum": certificate["endpoints"]["metadataAnchor"]["matching"][
            "maximumCoherentMatchingSize"
        ],
        "toDefect": certificate["endpoints"]["metadataAnchor"]["matching"][
            "collisionDefect"
        ],
        "allAssertions": all(certificate["assertions"].values()),
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
