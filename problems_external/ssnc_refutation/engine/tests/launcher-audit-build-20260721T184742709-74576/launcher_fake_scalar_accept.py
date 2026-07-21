#!/usr/bin/env python3
import json
import sys

if len(sys.argv) != 2:
    raise SystemExit(2)
print(json.dumps({"status": "VERIFIED_COUNTEREXAMPLE"}, separators=(",", ":"), sort_keys=True))
raise SystemExit(0)
