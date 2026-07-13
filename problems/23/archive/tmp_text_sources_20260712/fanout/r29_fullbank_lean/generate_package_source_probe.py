#!/usr/bin/env python3
"""Generate a one-file current-source compatibility probe for the final provider seam."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ROOT / "problems" / "23" / "lean" / "Erdos23Delta0"
OUT = HERE / "CurrentPackageSourceProbe.lean"


def without_imports(path: Path) -> str:
    return "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("import ")
    )


OUT.write_text(
    "import Erdos23Delta0.CertGraph\n"
    "import Erdos23Delta0.Rows.RowPartition\n\n"
    + without_imports(LEAN / "FCBridge.lean")
    + "\n\n"
    + without_imports(LEAN / "PackageProviderSkeleton.lean")
    + "\n\n"
    + "#print axioms Erdos23Delta0.CertGraph.erdos23_fcForm_of_graphDataInputs\n"
    + "#print axioms Erdos23Delta0.CertGraph.erdos23_fcForm_of_partitionInputs\n"
    + "#print axioms Erdos23Delta0.CertGraph.erdos23_rationalDeletion_of_partitionInputs\n",
    encoding="utf-8",
)
print(OUT)
