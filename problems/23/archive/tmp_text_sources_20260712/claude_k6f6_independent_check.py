#!/usr/bin/env python3
# INDEPENDENT exact-rational re-verification of the k6/F6 source->custom cone certificate.
# I do NOT reuse Codex's checker; I recompute residuals from the raw column/solution/target data.
# Claim under test (Codex eq_odl1_rung2_custom_cone_check_v1):
#   x >= 0, and for every constraint row: (sum_i x_i * col_i[row]) - target[row] >= 0
#   with exactly 158472 zero residuals, 0 negative residuals, over 167960 rows; 2432 nonzero cols.
import json, sys
from fractions import Fraction
from collections import defaultdict

TMP = r"E:\Projects\ErdosProblems\tmp"
cols_p  = TMP + r"\eq_odl1_rung2_k6_F6_known_source_import_cols_v1.json"
sol_p   = TMP + r"\eq_odl1_rung2_k6_F6_known_source_import_solution_v1.jsonl"
tgt_p   = TMP + r"\eq_odl1_rung2_k6_F6_known_source_import_target_beta_v1.json"

with open(cols_p, "r") as f:
    cols_doc = json.load(f)
columns = cols_doc["columns"]
ncols = len(columns)

# solution: source_col (positional index) -> Fraction coefficient
x = {}
xmin = None
xneg = 0
with open(sol_p, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        xi = Fraction(int(d["num"]), int(d["den"]))
        sc = int(d["source_col"])
        x[sc] = xi
        if xi < 0:
            xneg += 1
        if xmin is None or xi < xmin:
            xmin = xi
nsol = len(x)

# target_beta: dense per-row
with open(tgt_p, "r") as f:
    tgt_doc = json.load(f)
tb = tgt_doc["target_beta"]
nrows_tb = len(tb)
target = [None]*nrows_tb
tb_nonzero = 0
for i, e in enumerate(tb):
    v = Fraction(int(e["num"]), int(e["den"]))
    target[i] = v
    if v != 0:
        tb_nonzero += 1

# accumulate A x  (sparse over rows)
acc = defaultdict(Fraction)
max_row_seen = -1
for i, col in enumerate(columns):
    xi = x.get(i)
    if xi is None:
        # column with no solution entry => coefficient 0, skip
        continue
    for t in col["terms"]:
        r = int(t["row"])
        acc[r] += xi * Fraction(int(t["num"]), int(t["den"]))
        if r > max_row_seen:
            max_row_seen = r

# residual per row = (A x)[row] - target[row], over ALL rows in [0, nrows) where
# nrows = max(len(target), max row index touched + 1)
nrows = max(nrows_tb, max_row_seen + 1)
neg = 0
zero = 0
pos = 0
rmin = None
first_neg = []
for r in range(nrows):
    ax = acc.get(r, Fraction(0))
    tv = target[r] if r < nrows_tb else Fraction(0)
    # Codex "support: negative" convention: residual = target - Ax (must be >= 0 for feasibility)
    res = tv - ax
    if res < 0:
        neg += 1
        if len(first_neg) < 8:
            first_neg.append((r, str(res)))
    elif res == 0:
        zero += 1
    else:
        pos += 1
    if rmin is None or res < rmin:
        rmin = res

def bits(fr):
    return f"num_bits={fr.numerator.bit_length()}/den_bits={fr.denominator.bit_length()}"

print(json.dumps({
    "ncols_in_file": ncols,
    "nsol_nonzero": nsol,
    "x_negative_count": xneg,
    "x_min_is_positive": (xmin is not None and xmin > 0),
    "target_nonzero": tb_nonzero,
    "nrows_checked": nrows,
    "residual_negative_count": neg,
    "residual_zero_count": zero,
    "residual_positive_count": pos,
    "residual_min_bits": bits(rmin) if rmin is not None else None,
    "residual_min_sign_nonneg": (rmin is not None and rmin >= 0),
    "first_negatives": first_neg,
    "EXPECTED_codex": {"neg":0, "zero":158472, "rows":167960, "cols":2432, "x_neg":0},
    "MATCH_codex": (neg==0 and zero==158472 and nrows==167960 and nsol==2432 and xneg==0),
}, indent=2))
