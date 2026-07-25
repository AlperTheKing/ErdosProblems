#!/usr/bin/env python3
"""
Experiment 7 — MOR-DISS-001 Leg-3 THIRD-OPERATOR test (tent map)

Confirms / refutes the ε·W^(-1/2) Marchenko-Pastur crossover law on a THIRD
structurally-distinct chaotic operator. EXP1 (salvo 1) self-admits:
  "Run Experiment 4 (tent map or baker's map) to test universality across
   a third operator. If third operator also shows ε·√W ≈ 0.42–0.5, elevate
   to certified power morphism (3-operator generality)."

Operators tested prior:
  EXP-DISS-KVN-001: doubling map D(x) = 2x mod 1         → slope ≈ -0.5 PASS
  EXP1 (salvo 1):   Gauss map G(x) = {1/x}              → slope residual 0.006
  EXP7 (this):      tent map T(x) = 1 - |2x - 1|        → target slope ≈ -0.5

If PASS → MOR-DISS-001 graduates to CERTIFIED POWER MORPHISM (3-operator
universal). This is the trigger for 'validated' confidence in D1.
"""

import json, math
from pathlib import Path
import numpy as np

RNG = np.random.default_rng(20260418)
M_L = math.log(2) ** 2  # ≈ 0.4805
TAU_STAR = 0.5


def build_ulam_tent(W, M=40000):
    """
    Ulam-Galerkin discretization of the tent map T(x) = 1 - |2x - 1|.

    Tent map is piecewise linear, uniformly expanding (|T'(x)| = 2),
    preserves Lebesgue measure, and has a well-studied Ruelle spectrum.
    Structurally distinct from doubling (not a group-translation) and
    Gauss (not continued-fraction arithmetic).
    """
    L = np.zeros((W, W))
    for j in range(W):
        xs = (j + RNG.uniform(0, 1, M)) / W
        ys = 1.0 - np.abs(2.0 * xs - 1.0)
        idx = np.minimum((ys * W).astype(int), W - 1)
        np.add.at(L[:, j], idx, 1.0 / len(xs))
    return L


def tau2(m):
    v = np.sort(np.abs(np.linalg.eigvals(m)))[::-1]
    return float(v[1]) if len(v) > 1 else 1.0


def sweep(L, epsilons, n=24):
    out = []
    for e in epsilons:
        ts = [tau2(L + RNG.standard_normal(L.shape) * e) for _ in range(n)]
        out.append((float(e), float(np.mean(ts)), float(np.std(ts))))
    return out


def find_crossover(sweep_rows, tau_clean, frac=0.5):
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


def main():
    outdir = Path(__file__).parent
    Ws = [20, 40, 80, 160]
    epsilons = np.logspace(-3.5, 0, 30)
    n_realizations = 24

    data = {
        "experiment": "MOR-DISS-001-LEG3-TENT",
        "date": "2026-04-18",
        "map": "tent T(x) = 1 - |2x - 1|",
        "erdos_problem": "#1038 EHP infimum (Leg-3 third operator)",
        "reference_prior": ["EXP-DISS-KVN-001 doubling map", "EXP1 salvo1 Gauss map"],
        "M_L": M_L,
        "tau_star": TAU_STAR,
        "Ws": Ws,
        "epsilon_grid_size": len(epsilons),
        "n_realizations": n_realizations,
        "clean_tau": {},
        "sweep": {},
        "crossover_50": {},
    }

    print("=" * 70)
    print("EXPERIMENT 7: MOR-DISS-001 Leg-3 THIRD-OPERATOR (tent map)")
    print("=" * 70)

    for W in Ws:
        print(f"W = {W}...")
        L = build_ulam_tent(W)
        tc = tau2(L)
        data["clean_tau"][str(W)] = tc
        rows = sweep(L, epsilons, n=n_realizations)
        data["sweep"][str(W)] = [{"eps": r[0], "mu": r[1], "sd": r[2]} for r in rows]
        cx = find_crossover(rows, tc, frac=0.5)
        data["crossover_50"][str(W)] = cx
        if cx is not None:
            print(f"  clean τ={tc:.5f}  crossover(50%)={cx:.4f}  "
                  f"eps*sqrt(W)={cx*math.sqrt(W):.3f}  eps/M_L={cx/M_L:.3f}")
        else:
            print(f"  clean τ={tc:.5f}  crossover NOT FOUND")

    Ws_arr = np.array(Ws, dtype=float)
    cx_list = [data["crossover_50"][str(W)] for W in Ws]
    cx_arr = np.array([c for c in cx_list if c is not None], dtype=float)
    Ws_valid = Ws_arr[np.array([c is not None for c in cx_list])]

    if len(cx_arr) >= 2:
        log_W = np.log(Ws_valid)
        log_cx = np.log(cx_arr)
        slope, intercept = np.polyfit(log_W, log_cx, 1)
        prefactor = math.exp(intercept)

        data["scaling_fit"] = {
            "slope": float(slope),
            "intercept": float(intercept),
            "prefactor": float(prefactor),
        }

        h1_residual = abs(slope - 0.0)
        h2_residual = abs(slope - (-0.5))

        print()
        print(f"Fitted: ε_cross(W) ~ {prefactor:.3f} · W^{slope:.3f}")
        print(f"H1 (M_L constant) slope residual: {h1_residual:.3f}")
        print(f"H2 (RMT -0.5)     slope residual: {h2_residual:.3f}")

        if h2_residual < h1_residual and abs(slope + 0.5) < 0.15:
            verdict = "RMT-THIRD-OPERATOR-PASS"
            msg = ("Tent map exhibits the same Marchenko-Pastur crossover "
                   "as doubling + Gauss. Three-operator universality achieved. "
                   "MOR-DISS-001 is now a CERTIFIED POWER MORPHISM.")
        elif h1_residual < h2_residual and h1_residual < 0.2:
            verdict = "M_L-CONFIRMED-TENT"
            msg = ("Tent crossover is approximately W-independent — "
                   "contradicts doubling + Gauss.")
        else:
            verdict = "MIXED-INCONCLUSIVE"
            msg = "Neither hypothesis fits cleanly on tent map."

        data["verdict"] = verdict
        data["verdict_msg"] = msg
        print(f"\nVERDICT: {verdict}")
        print(msg)
    else:
        data["verdict"] = "INSUFFICIENT_DATA"
        data["verdict_msg"] = "Not enough valid crossover measurements."

    with (outdir / "exp7_results.json").open("w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults: {outdir}/exp7_results.json")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        colors = ["#1F3864", "#2E75B6", "#C00000", "#ED7D31"]
        for W, c in zip(Ws, colors):
            rows = data["sweep"][str(W)]
            e = [r["eps"] for r in rows]; m = [r["mu"] for r in rows]; s = [r["sd"] for r in rows]
            ax1.errorbar(e, m, yerr=s, marker="o", label=f"W={W}", color=c,
                         capsize=2, lw=1.1, ms=4)
        ax1.axhline(TAU_STAR, color="gray", ls="--", lw=1)
        ax1.axvline(M_L, color="#C00000", ls="-.", lw=1.3, label=f"M_L={M_L:.3f}")
        ax1.set_xscale("log")
        ax1.set_xlabel("noise ε"); ax1.set_ylabel("τ₂")
        ax1.set_title("τ₂(ε) by W — tent map")
        ax1.set_ylim(0, 1.05); ax1.grid(True, which="both", alpha=0.3); ax1.legend(fontsize=9)

        cx_valid = np.array([data["crossover_50"][str(W)] for W in Ws])
        ax2.loglog(Ws_arr, cx_valid, "o", ms=10, color="#1F3864", label="measured")
        if len(cx_arr) >= 2:
            W_fine = np.logspace(math.log10(15), math.log10(300), 50)
            ax2.loglog(W_fine, prefactor * W_fine ** slope, "-", color="#2E75B6",
                       label=f"fit: {prefactor:.3f}·W^{slope:.3f}")
            ax2.loglog(W_fine, 0.5 / np.sqrt(W_fine), "--", color="#C00000",
                       label="H2 (RMT): 0.5/√W")
        ax2.axhline(M_L, color="gray", ls=":", lw=1, label=f"H1 (M_L const)")
        ax2.set_xlabel("W"); ax2.set_ylabel("crossover ε")
        ax2.set_title("Scaling: H1 vs H2 — tent")
        ax2.grid(True, which="both", alpha=0.3); ax2.legend(fontsize=9)
        fig.suptitle("EXP7: MOR-DISS-001 Leg-3 — tent map (3rd operator)", y=1.00)
        fig.tight_layout()
        fig.savefig(outdir / "exp7_plot.png", dpi=140, bbox_inches="tight")
        print(f"Plot: {outdir}/exp7_plot.png")
    except Exception as e:
        print(f"Plot skipped: {e}")


if __name__ == "__main__":
    main()
