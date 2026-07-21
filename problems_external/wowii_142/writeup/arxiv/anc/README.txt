Ancillary verification material for Graffiti.pc / WOWII Conjecture 142
======================================================================

The paper contains a complete mathematical proof.  This ancillary directory
records the two machine-assisted checks described in its verification section.
Neither check is used as a substitute for the proof.

lean/NearestSetDescent.lean
--------------------------

A warning-free, `sorry`-free Lean 4 lemma proving the geodesic/descent
backbone used by the rooted construction: a nearest-set descent is a path,
its support induces a tree, it first reaches the target set at its endpoint,
and vertices at least two steps before the endpoint have no target-set
neighbour.  The full Conjecture 142 theorem is not claimed to be formalized.

computation/problems_external/...
---------------------------------

This preserves the workspace-relative layout needed by
`wowii_142/proverB/constructive_validator.py`, including all local generator
and invariant modules.  From `computation/problems_external/wowii_142/proverB`
run:

    python constructive_validator.py
    python constructive_validator.py --seed=1
    python constructive_validator.py --seed=2

The validator reconstructs every proof certificate and independently checks
inducedness, connectedness, acyclicity, attachment-edge multiplicities, and
the claimed cardinality.  The three checked-in JSON files record zero
failures for 10,776 graphs per run.  The default run was repeated from this
copied ancillary tree on 18 July 2026 and again returned zero failures.

Requirements
------------

Python 3 and NetworkX.  Random and adversarial families use fixed seeds.
