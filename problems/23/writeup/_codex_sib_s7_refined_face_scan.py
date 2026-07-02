"""Exploratory SLSQP scan for the refined S7 endpoint-fiber faces.

This is not an acceptance gate.  It applies the refinement from
`_codex_sib_s7_endpoint_refine.py`: the broad faces x=1 and y=1 are replaced
by endpoint+endpoint/capacity faces.
"""

from __future__ import annotations

from _codex_sib_s7_14face_scan import Hit, NAMES, run_face

import random


def refined_faces() -> list[tuple[str, ...]]:
    faces: list[tuple[str, ...]] = []
    for endpoint in ["y", "x"]:
        faces.append((endpoint, "u"))
        faces.append((endpoint, "v=e"))
        for s in ["s4", "s5", "s6", "s7"]:
            faces.append((endpoint, s))
    for s in ["s4", "s5", "s6", "s7"]:
        faces.extend([(s, "u"), (s, "v"), (s, "v=e")])
    # Deduplicate while preserving order.
    out: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    for face in faces:
        if face not in seen:
            seen.add(face)
            out.append(face)
    return out


def main() -> None:
    rng = random.Random(20260702)
    hits: list[Hit] = []
    for face in refined_faces():
        hit = run_face(face, rng)
        if hit is not None:
            hits.append(hit)
    hits.sort(key=lambda h: h.value)
    for h in hits:
        ztxt = " ".join(f"{name}={val:.8g}" for name, val in zip(NAMES, h.z))
        active = tuple(i + 1 for i, s in enumerate(h.slacks) if abs(s) < 1e-5)
        print("face", h.face, "phi", f"{h.value:.12g}", "active", active)
        print(" ", ztxt)


if __name__ == "__main__":
    main()
