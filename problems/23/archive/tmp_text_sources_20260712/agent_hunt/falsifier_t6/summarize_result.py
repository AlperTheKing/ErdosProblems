#!/usr/bin/env python3
import json
import sys

d = json.load(open(sys.argv[1]))
print(
    sys.argv[1],
    "::",
    d.get("verdict"),
    "hits=" + str(len(d.get("hits", []))),
    "solved=" + str(d.get("supportsSolved")),
    "circ=" + json.dumps(d.get("circuitStatuses", {}), sort_keys=True),
)
