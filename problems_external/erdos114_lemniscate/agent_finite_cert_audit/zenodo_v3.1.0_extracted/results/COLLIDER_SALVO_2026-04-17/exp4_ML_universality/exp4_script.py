#!/usr/bin/env python3
"""
EXP4 — Mendoza's Limit Universality Meta-Test
Test whether M_L is universal across three structurally different transfer operators.

Three maps:
  1. Symmetric tent map (M_L_ref = (ln 2)^2 ≈ 0.4805)
  2. Arnold cat map (M_L_ref = log(lambda_golden)^2 where lambda_golden=(3+√5)/2)
  3. Random doubly-stochastic Markov (RMT positive control — pure 1/sqrt(W) scaling)

Protocol: for each map, sweep ε in 24 log-spaced values across [10^-3.5, 1],
W ∈ {20, 40, 80, 160}, 16 noise realizations per (W, ε).
Extract τ_clean, crossover ε, fit ε_cross(W) = C · W^α.
Compare α and C to M_L and RMT predictions.
"""

import json, math, sys
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit

RNG = np.random.default_rng(20260417)

# Physical constants
M_L = math.log(2) ** 2  # ≈ 0.4805 — Landauer-Bennett floor
lambda_golden = (3 + math.sqrt(5)) / 2
M_L_golden = math.log(lambda_golden) ** 2

# Logging
def log_msg(s):
    print(f"[EXP4] {s}", file=sys.stderr, flush=True)

# ============ MAP 1: Symmetric Tent ============

def build_tent_ulam(W, M=10000):
    """Ulam-Galerkin for T(x)=1-2|x-1/2|. Reference τ_clean ≈ 0.4-0.5."""
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0, 1, M)) / W
        ys = 1.0 - 2.0 * np.abs(xs - 0.5)
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / M)
    return L

# ============ MAP 2: Arnold Cat Map ============

def build_arnold_ulam(W, M=10000):
    """Arnold cat (1D projection). Reference τ_clean ≈ lambda_golden ≈ 1.618."""
    # (x, y) |-> (x+y, x+2y) mod 1
    # Project to 1D: return map x_n+1 = (x_n + (x_n + 2*f(x_n))) mod 1 ≈ fractional dynamics
    # Simplified: use matrix eigenvalues [1, lambda_golden]
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0, 1, M)) / W
        # Approximate by mixing—higher return times
        ys = (xs + xs * lambda_golden) % 1.0
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / M)
    return L

# ============ MAP 3: Random Doubly-Stochastic Markov (RMT Control) ============

def build_random_markov(W):
    """Generate random doubly-stochastic matrix (columns and rows sum to 1).
    This should obey pure RMT scaling: ε_cross ~ W^{-1/2} * (1 - τ*).
    """
    # Random matrix with nonnegative entries
    A = RNG.exponential(1.0, (W, W))
    # Column normalization (stochastic)
    A /= A.sum(axis=0, keepdims=True)
    # Project to doubly-stochastic (harder, but use row-balancing)
    for _ in range(3):  # 3 Sinkhorn iterations
        A /= A.sum(axis=1, keepdims=True) / W
        A /= A.sum(axis=0, keepdims=True)
    return A

# ============ Common Machinery ============

def tau2(m):
    """Second-largest eigenvalue (by absolute value)."""
    v = np.sort(np.abs(np.linalg.eigvals(m)))[::-1]
    return float(v[1]) if len(v) > 1 else 0.0

def sweep(L, epsilons, n=16):
    """Noise sweep: for each epsilon, average tau2 over n realizations."""
    out = []
    for e in epsilons:
        ts = [tau2(L + RNG.standard_normal(L.shape) * e) for _ in range(n)]
        out.append((float(e), float(np.mean(ts)), float(np.std(ts))))
    return out

def find_crossover(sweep_rows, tau_clean, frac=0.5):
    """Find epsilon where tau rises to tau_clean + frac*(1 - tau_clean)."""
    thr = tau_clean + frac * (1.0 - tau_clean)
    prev = sweep_rows[0]
    for row in sweep_rows[1:]:
        if row[1] > thr:
            x0, y0 = prev[0], prev[1]
            x1, y1 = row[0], row[1]
            if y1 == y0:
                return x1
            t = (thr - y0) / (y1 - y0)
            return float(math.exp(math.log(x0) + t * (math.log(x1) - math.log(x0))))
        prev = row
    return None

# ============ Main ============

def main():
    outdir = Path(__file__).parent
    outdir.mkdir(parents=True, exist_ok=True)

    Ws = [20, 40, 80, 160]
    epsilons = np.logspace(-3.5, 0, 24)  # 24 log-spaced values

    maps = {
        "tent": {
            "builder": build_tent_ulam,
            "M_L_ref": M_L,
            "description": "Symmetric tent map T(x)=1-2|x-1/2|"
        },
        "arnold": {
            "builder": build_arnold_ulam,
            "M_L_ref": M_L_golden,
            "description": "Arnold cat (1D projection), λ_gold ≈ 1.618"
        },
        "random_markov": {
            "builder": build_random_markov,
            "M_L_ref": None,  # Should be pure RMT
            "description": "Random doubly-stochastic Markov (RMT control)"
        }
    }

    results = {
        "experiment": "EXP4-ML-UNIVERSALITY",
        "date": "2026-04-17",
        "M_L_constant": float(M_L),
        "M_L_golden": float(M_L_golden),
        "lambda_golden": float(lambda_golden),
        "Ws": Ws,
        "n_realizations": 16,
        "maps": {}
    }

    for map_name, map_spec in maps.items():
        log_msg(f"Starting {map_name}...")
        builder = map_spec["builder"]
        M_L_ref = map_spec["M_L_ref"]

        map_data = {
            "description": map_spec["description"],
            "M_L_ref": M_L_ref,
            "clean_tau": {},
            "sweep": {},
            "crossover_50": {},
            "fit": {}
        }

        crossovers = []
        Ws_float = []

        for W in Ws:
            log_msg(f"  W={W}")
            if map_name == "random_markov":
                L = builder(W)  # No M parameter
            else:
                L = builder(W)

            tau_c = tau2(L)
            map_data["clean_tau"][str(W)] = float(tau_c)

            # Sweep
            rows = sweep(L, epsilons, n=16)
            map_data["sweep"][str(W)] = [
                {"eps": r[0], "mu_tau2": r[1], "sd": r[2]} for r in rows
            ]

            # Crossover
            cx = find_crossover(rows, tau_c, frac=0.5)
            map_data["crossover_50"][str(W)] = cx if cx else None
            if cx:
                crossovers.append(cx)
                Ws_float.append(float(W))
                rmt_pred = (1.0 - 0.5) / math.sqrt(W)
                log_msg(f"    τ_clean={tau_c:.5f}  ε_cross={cx:.5f}  "
                       f"ε*√W={cx*math.sqrt(W):.4f}  ε/M_L={cx/M_L:.4f}  "
                       f"RMT(1-τ*)√W={rmt_pred:.4f}")

        # Fit crossover(W) to power law: log ε = a + b log W
        if len(crossovers) >= 2:
            Ws_arr = np.array(Ws_float)
            cx_arr = np.array(crossovers)
            log_W = np.log(Ws_arr)
            log_cx = np.log(cx_arr)

            slope, intercept = np.polyfit(log_W, log_cx, 1)
            prefactor = math.exp(intercept)

            # Residual
            pred = intercept + slope * log_W
            residual = np.sqrt(np.mean((pred - log_cx)**2))

            map_data["fit"] = {
                "formula": "log(ε_cross) = intercept + slope * log(W)",
                "intercept": float(intercept),
                "slope": float(slope),
                "prefactor": float(prefactor),
                "rms_residual": float(residual),
                "Ws_used": [int(w) for w in Ws_float],
                "crossovers_used": [float(c) for c in crossovers]
            }

            log_msg(f"  Fit: slope={slope:.3f}, prefactor={prefactor:.5f}, residual={residual:.5f}")

            # Hypothesis testing
            is_ML_class = abs(slope) < 0.15 and prefactor / M_L_ref < 1.15 if M_L_ref else False
            is_RMT_class = abs(slope - (-0.5)) < 0.15 and abs(prefactor - (1.0 - 0.5)) < 0.15

            if is_ML_class:
                verdict = "M_L_WINS"
            elif is_RMT_class:
                verdict = "RMT_WINS"
            else:
                verdict = "MIXED"

            map_data["hypothesis_verdict"] = {
                "verdict": verdict,
                "is_M_L_class": bool(is_ML_class),
                "is_RMT_class": bool(is_RMT_class),
                "slope_dev_from_0": float(abs(slope)),
                "slope_dev_from_minus_half": float(abs(slope - (-0.5))),
                "prefactor_dev_from_M_L_ref": float(abs(prefactor / M_L_ref - 1.0)) if M_L_ref else None,
                "prefactor_dev_from_RMT": float(abs(prefactor - (1.0 - 0.5)))
            }

        results["maps"][map_name] = map_data

    # Write JSON
    json_path = outdir / "exp4_results.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    log_msg(f"Wrote {json_path}")

    # Determine universality verdict
    verdicts = []
    for name, mdata in results["maps"].items():
        if "hypothesis_verdict" in mdata:
            verdicts.append((name, mdata["hypothesis_verdict"]["verdict"]))

    if verdicts:
        tent_v = next((v for n, v in verdicts if n == "tent"), None)
        arnold_v = next((v for n, v in verdicts if n == "arnold"), None)
        random_v = next((v for n, v in verdicts if n == "random_markov"), None)

        # Universality logic
        if random_v == "RMT_WINS":
            # RMT control behaves as expected
            if tent_v == "M_L_WINS" and arnold_v == "M_L_WINS":
                universality_verdict = "M_L_SCOPE_CONFIRMED"
                explanation = "M_L dominates deterministic maps; RMT dominates random. M_L is real, not universal."
            elif tent_v == "RMT_WINS" and arnold_v == "RMT_WINS":
                universality_verdict = "RMT_UNIVERSAL"
                explanation = "All maps obey RMT scaling. M_L either emergent or subleading."
            else:
                universality_verdict = "MIXED"
                explanation = "Tent and Arnold show different behavior. No clear universality."
        else:
            universality_verdict = "AMBIGUOUS"
            explanation = "RMT control failed or unclear. Cannot assess universality."
    else:
        universality_verdict = "AMBIGUOUS"
        explanation = "Insufficient fits."

    # Create verdict markdown
    verdict_text = f"""# EXP4 — Mendoza's Limit Universality Meta-Test
## Verdict: {universality_verdict}

**Date:** 2026-04-17
**Explanation:** {explanation}

### Per-Map Summary

"""

    for map_name, map_data in results["maps"].items():
        verdict_text += f"#### {map_name.upper()}\n"
        if map_data["clean_tau"]:
            tau_avg = np.mean(list(map_data["clean_tau"].values()))
            verdict_text += f"- Clean τ₂ (average): {tau_avg:.5f}\n"

        if "hypothesis_verdict" in map_data:
            hv = map_data["hypothesis_verdict"]
            verdict_text += f"- **Hypothesis Verdict:** {hv['verdict']}\n"
            verdict_text += f"- Slope: {map_data['fit']['slope']:.4f} (dev from 0: {hv['slope_dev_from_0']:.3f}, dev from -0.5: {hv['slope_dev_from_minus_half']:.3f})\n"
            verdict_text += f"- Prefactor: {map_data['fit']['prefactor']:.5f}\n"
        else:
            verdict_text += "- No fit available.\n"

        verdict_text += "\n"

    verdict_text += """### Interpretation

**M_L Universality Scope:**
- If M_L_SCOPE_CONFIRMED: M_L is a real physical constant, but specific to chaotic maps with positive Lyapunov exponent. Use as atlas codomain only for deterministic chaos problems (Bernstein, sunflower, channel capacity with state-dependent costs).
- If RMT_UNIVERSAL: M_L is an emergent property of large random matrices, not fundamental. Atlas should use 1/√W scaling as default.
- If MIXED or AMBIGUOUS: Further work needed; report results transparently without claiming universality.

### Raw Results
See `exp4_results.json` for full sweep data, per-map fits, and residuals.
"""

    verdict_path = outdir / "EXP4_VERDICT.md"
    with open(verdict_path, "w") as f:
        f.write(verdict_text)
    log_msg(f"Wrote {verdict_path}")

    return results, verdicts, universality_verdict

if __name__ == "__main__":
    results, verdicts, univ_verdict = main()
    log_msg(f"✓ EXP4 complete. Universality verdict: {univ_verdict}")
