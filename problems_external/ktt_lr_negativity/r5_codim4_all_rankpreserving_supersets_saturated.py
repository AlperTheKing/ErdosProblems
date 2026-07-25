#!/usr/bin/env python3
"""Replay the all-supersets audit with exact lattice saturation enabled."""

import r5_codim4_all_rankpreserving_supersets as audit
import r5_codim4_saturated_normal as saturated


audit.normal.direct_normal_alpha = saturated.saturated_direct_normal_alpha


if __name__ == "__main__":
    audit.main()
