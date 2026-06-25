#!/usr/bin/env python3
"""
Independent item-5 verifier for Codex's Step-1 (H1: a(30)<=36) state-count TSVs.

NOT a completeness (item-1) or solver-correctness check — it ONLY verifies, for
each artifact, the certificate-CONSISTENCY conditions from
bridge/NEEDED_FROM_STEP1.md item 5:
  (a) every row's status is INFEASIBLE  (any FEASIBLE/UNKNOWN/NO_STATUS = RED FLAG);
  (b) report unique task-key count and duplicate rows (rows unioned by key);
  (c) report the status histogram.

It is independent of Codex's own `verify_state_count_union.exe` (re-implemented
from scratch in Python). Run from repo root:
    python bridge/experiments/audit_h1_statecount.py search23/state_count_6195_er16_clean_infeasible_union.tsv
    python bridge/experiments/audit_h1_statecount.py --all          # all search23/state_count_*.tsv

Schema handling (auto-detected from the header line, case-insensitive):
  - state-count tables: key = (mask, p, M)               [p column may be 'P' or 'p']
  - profile tables:     key = (profile_idx, cnt)         [from *_profile_*.tsv]
Exit code 0 iff every file audited has ALL rows INFEASIBLE; 1 if any red flag.
"""
import sys, glob, os

GOOD = "INFEASIBLE"
RED_STATUSES = {"FEASIBLE", "UNKNOWN", "NO_STATUS", "SAT", "", "TIMEOUT", "ERROR"}

def header_cols(line):
    return {c.strip().lower(): i for i, c in enumerate(line.rstrip("\n").split("\t"))}

def pick_key(cols):
    if "mask" in cols and ("p" in cols) and "m" in cols:
        return [cols["mask"], cols["p"], cols["m"]], "(mask,p,M)"
    if "profile_idx" in cols and "cnt" in cols:
        return [cols["profile_idx"], cols["cnt"]], "(profile_idx,cnt)"
    if "cnt" in cols:
        return [cols["cnt"]], "(cnt)"
    return None, None

def audit(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
        cols = header_cols(first)
        if "status" not in cols:
            return (path, None, "no 'status' column (header=%s)" % list(cols))
        iS = cols["status"]
        ki, kname = pick_key(cols)
        rows = 0; keys = set(); st = {}
        maxidx = max([iS] + (ki or [0]))
        for ln in fh:
            p = ln.rstrip("\n").split("\t")
            if len(p) <= maxidx:
                continue
            rows += 1
            s = p[iS].strip()
            st[s] = st.get(s, 0) + 1
            if ki is not None:
                keys.add(tuple(p[k] for k in ki))
        red = [s for s in st if s != GOOD]
        ok = (len(st) > 0) and all(s == GOOD for s in st)
        return (path, dict(rows=rows, unique=len(keys) if ki else None, key=kname,
                           dup=(rows - len(keys)) if ki else None, status=st,
                           red=red, ok=ok), None)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    if args == ["--all"]:
        files = sorted(glob.glob("search23/state_count_*.tsv"))
    else:
        files = args
    any_red = False; n_ok = 0
    for f in files:
        if not os.path.exists(f):
            print("MISSING:", f); any_red = True; continue
        path, res, err = audit(f)
        if err:
            print(f"SKIP  {os.path.basename(path)}: {err}"); continue
        tag = "PASS" if res["ok"] else "*** RED FLAG ***"
        if not res["ok"]: any_red = True
        else: n_ok += 1
        print(f"[{tag}] {os.path.basename(path)}: rows={res['rows']} "
              f"unique{res['key']}={res['unique']} dup={res['dup']} status={res['status']}"
              + (f"  RED={res['red']}" if res["red"] else ""))
    print(f"\n{n_ok}/{len(files)} files PASS item-5 (all INFEASIBLE). "
          f"{'RED FLAGS PRESENT' if any_red else 'no red flags'}.")
    sys.exit(1 if any_red else 0)

if __name__ == "__main__":
    main()
