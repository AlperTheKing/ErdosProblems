#!/usr/bin/env python3
"""
EXP-DISS-KVN-001 REFINED: finer epsilon grid to identify the crossover-scale law.

Test whether the crossover epsilon scales as:
  (H1) M_L   -- Mendoza-Limit / Landauer scale  (discovery-note prediction)
  (H2) 1/sqrt(W) * (1 - tau*)   -- Marchenko-Pastur RMT scale
"""

import json, math
from pathlib import Path
import numpy as np

RNG = np.random.default_rng(20260417)
M_L = math.log(2) ** 2
TAU_STAR = 0.5


def build_ulam(W, delta=0.01, M=40000):
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0, 1, M)) / W
        ys = (2 * xs + delta * np.sin(2 * np.pi * xs)) % 1.0
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / M)
    return L


def tau2(m):
    v = np.sort(np.abs(np.linalg.eigvals(m)))[::-1]
    return float(v[1])


def sweep(L, epsilons, n=24):
    out = []
    for e in epsilons:
        ts = [tau2(L + RNG.standard_normal(L.shape) * e) for _ in range(n)]
        out.append((float(e), float(np.mean(ts)), float(np.std(ts))))
    return out


def find_crossover(sweep_rows, tau_clean, frac=0.5):
    """epsilon where tau_obs first exceeds tau_clean + frac*(1 - tau_clean)."""
    thr = tau_clean + frac * (1.0 - tau_clean)
    prev = sweep_rows[0]
    for row in sweep_rows[1:]:
        if row[1] > thr:
            # log-linear interpolate
            x0, y0 = prev[0], prev[1]
            x1, y1 = row[0], row[1]
            if y1 == y0:
                return x1
            t = (thr - y0) / (y1 - y0)
            return float(math.exp(math.log(x0) + t * (math.log(x1) - math.log(x0))))
        prev = row
    return None


def main():
    outdir = Path(__file__).parent / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    Ws = [20, 40, 80, 160, 320]
    epsilons = np.logspace(-3.5, 0, 36)  # finer: 10 points per decade

    data = {
        "experiment": "EXP-DISS-KVN-001-REFINED",
        "date": "2026-04-16",
        "M_L": M_L,
        "tau_star": TAU_STAR,
        "Ws": Ws,
        "n_realizations": 24,
        "clean_tau": {},
        "sweep": {},
        "crossover_50": {},
    }

    for W in Ws:
        L = build_ulam(W)
        tc = tau2(L)
        data["clean_tau"][str(W)] = tc
        rows = sweep(L, epsilons)
        data["sweep"][str(W)] = [{"eps": r[0], "mu": r[1], "sd": r[2]} for r in rows]
        cx = find_crossover(rows, tc, frac=0.5)
        data["crossover_50"][str(W)] = cx
        print(f"W={W:>3}  clean tau={tc:.5f}  crossover(50%)={cx:.4f}  "
              f"eps*sqrt(W)={cx*math.sqrt(W):.3f}  eps/M_L={cx/M_L:.3f}")

    # Fit log crossover = a + b log W to test scaling law
    Ws_arr = np.array(Ws, dtype=float)
    cx_arr = np.array([data["crossover_50"][str(W)] for W in Ws], dtype=float)
    log_W = np.log(Ws_arr)
    log_cx = np.log(cx_arr)
    # Linear regression
    slope, intercept = np.polyfit(log_W, log_cx, 1)
    data["scaling_fit"] = {
        "log_crossover = slope * log_W + intercept": True,
        "slope": float(slope),
        "intercept": float(intercept),
        "prefactor (exp(intercept))": float(math.exp(intercept)),
        "interpretation": {
            "H1 (M_L, Mendoza/Landauer)": "predicts slope = 0 (constant crossover)",
            "H2 (RMT / Marchenko-Pastur)": "predicts slope = -0.5, prefactor = (1 - tau*) = 0.5",
        }
    }

    with (outdir / "EXP_DISS_KVN_001_refined_results.json").open("w") as f:
        json.dump(data, f, indent=2)

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        colors = ["#1F3864", "#2E75B6", "#C00000", "#ED7D31", "#70AD47"]
        for W, c in zip(Ws, colors):
            rows = data["sweep"][str(W)]
            e = [r["eps"] for r in rows]
            m = [r["mu"] for r in rows]
            s = [r["sd"] for r in rows]
            ax1.errorbar(e, m, yerr=s, marker="o", label=f"W={W}", color=c,
                         capsize=2, lw=1.1, ms=4)
        ax1.axhline(TAU_STAR, color="gray", ls="--", lw=1, label=f"tau*={TAU_STAR}")
        ax1.axhline(1.0, color="black", ls=":", lw=1)
        ax1.axvline(M_L, color="#C00000", ls="-.", lw=1.3, label=f"M_L={M_L:.3f}")
        ax1.set_xscale("log")
        ax1.set_xlabel("noise epsilon")
        ax1.set_ylabel("observed leading resonance tau_obs")
        ax1.set_title("tau_obs(epsilon) by W")
        ax1.set_ylim(0, 1.05)
        ax1.grid(True, which="both", alpha=0.3)
        ax1.legend(fontsize=9, loc="upper left")

        # scaling plot
        ax2.loglog(Ws_arr, cx_arr, "o", ms=10, color="#1F3864", label="measured crossover")
        W_fine = np.logspace(math.log10(15), math.log10(500), 50)
        ax2.loglog(W_fine, math.exp(intercept) * W_fine ** slope, "-",
                   color="#2E75B6",
                   label=f"fit: eps ~ W^{slope:.3f} * {math.exp(intercept):.3f}")
        ax2.loglog(W_fine, 0.5 / np.sqrt(W_fine), "--", color="#C00000",
                   label="H2 prediction: 0.5 / sqrt(W)")
        ax2.axhline(M_L, color="gray", ls=":", lw=1,
                    label=f"H1 prediction: M_L={M_L:.3f} (constant)")
        ax2.set_xlabel("grid size W")
        ax2.set_ylabel("crossover epsilon")
        ax2.set_title("Scaling of crossover: H1 (M_L) vs H2 (RMT)")
        ax2.grid(True, which="both", alpha=0.3)
        ax2.legend(fontsize=9)

        fig.suptitle("EXP-DISS-KVN-001 REFINED: transfer-operator noise-crossover",
                     fontsize=12, y=1.02)
        fig.tight_layout()
        fig.savefig(outdir / "EXP_DISS_KVN_001_refined.png", dpi=140, bbox_inches="tight")
        print(f"plot -> {outdir/'EXP_DISS_KVN_001_refined.png'}")
    except Exception as e:
        print(f"plot skipped: {e}")

    # Verdict
    # H1 predicts slope=0, H2 predicts slope=-0.5
    # Compute which hypothesis fits better
    h1_residual = abs(slope - 0.0)
    h2_residual = abs(slope - (-0.5))
    prefactor = math.exp(intercept)
    h2_prefactor_residual = abs(prefactor - 0.5)

    print()
    print("=" * 60)
    print(f"Fitted scaling: eps_crossover(W) ~ {prefactor:.3f} * W^{slope:.3f}")
    print(f"  H1 residual (slope=0):   {h1_residual:.3f}")
    print(f"  H2 residual (slope=-0.5): {h2_residual:.3f}")
    print(f"  H2 prefactor residual (expected 0.5): {h2_prefactor_residual:.3f}")
    print()
    if h2_residual < h1_residual and abs(slope + 0.5) < 0.15:
        verdict = "RMT-REFINEMENT"
        msg = ("Leg-4 refined: the crossover is controlled by the "
               "Marchenko-Pastur random-matrix scale epsilon*sqrt(W) ~ 1-tau*, "
               "not by M_L directly. MOR-DISS-001 upgraded: the Mendoza-Limit "
               "reading is replaced by an RMT reading, consistent with the "
               "existing Morphism-A experience on prime gaps / GUE (same class).")
    elif h1_residual < h2_residual and h1_residual < 0.2:
        verdict = "M_L-CONFIRMED"
        msg = ("Crossover is W-independent within this range, consistent with "
               "a fixed M_L-scale prediction.")
    else:
        verdict = "MIXED"
        msg = ("Neither hypothesis is clean; further investigation needed.")

    print(f"VERDICT: {verdict}")
    print(msg)

    data["verdict"] = verdict
    data["verdict_msg"] = msg
    with (outdir / "EXP_DISS_KVN_001_refined_results.json").open("w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
