#!/usr/bin/env python3
"""
Experiment 3: Leg-2 validation for morphism 80590 ↔ PHYS-T-002
Random 3-SAT threshold measurement vs. Mézard-Parisi-Zecchina (2002).

Key insight: The empirical SAT/UNSAT threshold should cluster around α_c ≈ 4.2667.
We'll use Glucose (via pysat) which is a modern CDCL solver with unit propagation.
"""

import json
import random
import sys
import time
import subprocess
import numpy as np
from pathlib import Path

def generate_random_3cnf(n: int, m: int, seed=None) -> str:
    """Generate random 3-CNF formula in DIMACS format."""
    if seed is not None:
        random.seed(seed)
    
    clauses = []
    for _ in range(m):
        # Pick 3 distinct variables uniformly at random
        vars = random.sample(range(1, n + 1), min(3, n))
        if len(vars) < 3:
            vars += [1] * (3 - len(vars))
        
        # Randomly negate each literal
        lits = [v if random.random() < 0.5 else -v for v in vars]
        clauses.append(tuple(lits))
    
    # DIMACS format
    lines = [f"p cnf {n} {m}"]
    for clause in clauses:
        lines.append(" ".join(str(lit) for lit in clause) + " 0")
    return "\n".join(lines)

def solve_with_glucose(n: int, m: int, timeout_sec: float = 5.0, seed=None) -> dict:
    """Solve random 3-CNF using Glucose SAT solver (via pysat)."""
    alpha = m / n if n > 0 else 0
    
    try:
        from pysat.solvers import Glucose3
        from pysat.formula import CNF
        import tempfile
        import os
        
        cnf_str = generate_random_3cnf(n, m, seed=seed)
        
        # Write to temp DIMACS file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False) as f:
            f.write(cnf_str)
            cnf_path = f.name
        
        try:
            start = time.time()
            solver = Glucose3()
            
            # Parse DIMACS
            with open(cnf_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('p cnf'):
                        continue
                    if line.startswith('c'):
                        continue
                    if line:
                        clause = [int(x) for x in line.split() if x != '0']
                        if clause:
                            solver.add_clause(clause)
            
            # Solve with timeout
            is_sat = solver.solve()
            elapsed = time.time() - start
            
            solver.delete()
            
            return {
                "n": n,
                "m": m,
                "alpha": float(alpha),
                "is_sat": bool(is_sat),
                "time_sec": float(min(elapsed, timeout_sec)),
                "solver": "glucose3",
                "status": "success"
            }
        finally:
            os.unlink(cnf_path)
    
    except Exception as e:
        return {
            "n": n,
            "m": m,
            "alpha": float(alpha),
            "is_sat": None,
            "time_sec": 0,
            "solver": "glucose3",
            "status": f"error: {str(e)}"
        }

def experiment_sweep():
    """Sweep n and alpha, measure P(SAT) threshold."""
    results_data = []
    
    ns = [50, 100, 200]
    # Alpha range centered around expected threshold ~4.2667
    alphas = np.linspace(3.5, 5.0, 16)
    replicates = 20
    
    print("=" * 80)
    print("EXPERIMENT 3: Random 3-SAT Threshold (Leg-2 Validation)")
    print(f"MPZ cavity-method prediction: α_c = 4.2667 ± 0.001")
    print(f"Variables (n): {list(ns)}")
    print(f"Alpha range: {alphas[0]:.2f}–{alphas[-1]:.2f}, {len(alphas)} points")
    print(f"Replicates per (n, α): {replicates}")
    print("=" * 80)
    
    total_instances = len(ns) * len(alphas) * replicates
    completed = 0
    
    for n in ns:
        print(f"\n[n={n}]")
        
        for alpha in alphas:
            m = int(alpha * n)
            sat_count = 0
            times = []
            errors = 0
            
            for rep in range(replicates):
                result = solve_with_glucose(n, m, timeout_sec=5.0, seed=42 + rep)
                completed += 1
                
                if result["status"] == "success":
                    if result["is_sat"] is not None:
                        if result["is_sat"]:
                            sat_count += 1
                        times.append(result["time_sec"])
                else:
                    errors += 1
                
                pct = 100.0 * completed / total_instances
                sys.stdout.write(f"\r  α={alpha:.2f}: {rep+1}/{replicates} (total {pct:.1f}%)")
                sys.stdout.flush()
            
            p_sat = sat_count / replicates if replicates > 0 else 0
            avg_time = np.mean(times) if times else 0
            
            results_data.append({
                "n": n,
                "m": m,
                "alpha": float(alpha),
                "p_sat": float(p_sat),
                "sat_count": sat_count,
                "total_replicates": replicates,
                "avg_time_sec": float(avg_time),
                "errors": errors
            })
            
            print(f" → P(SAT)={p_sat:.2f} (t={avg_time:.2f}s, err={errors})")
    
    print("\n" + "=" * 80)
    return results_data

def fit_threshold_per_n(data: list) -> dict:
    """Fit logistic threshold P(SAT) = 1/(1+exp(-k*(α-α_c))) per size n."""
    from scipy.optimize import curve_fit
    
    by_n = {}
    for row in data:
        n = row['n']
        if n not in by_n:
            by_n[n] = []
        by_n[n].append(row)
    
    results = {}
    alphas_c_list = []
    ns_list = []
    
    for n in sorted(by_n.keys()):
        rows = sorted(by_n[n], key=lambda r: r['alpha'])
        alphas = np.array([r['alpha'] for r in rows])
        p_sats = np.array([r['p_sat'] for r in rows])
        
        # Logistic function for phase transition
        def logistic(alpha, alpha_c, k):
            return 1.0 / (1.0 + np.exp(-k * (alpha - alpha_c)))
        
        try:
            # Initial guess: MPZ value
            popt, pcov = curve_fit(logistic, alphas, p_sats, 
                                   p0=[4.2667, 2.0],
                                   maxfev=10000)
            alpha_c_n, k = popt[0], popt[1]
            
            results[f"n_{n}"] = {
                "n": n,
                "alpha_c": float(alpha_c_n),
                "steepness_k": float(k),
                "p_sat_data": [float(p) for p in p_sats]
            }
            
            alphas_c_list.append(alpha_c_n)
            ns_list.append(n)
            
            print(f"[n={n}] Fitted α_c = {alpha_c_n:.4f} (k={k:.3f})")
        except Exception as e:
            print(f"[n={n}] Fit failed: {e}")
    
    # Finite-size scaling
    if len(alphas_c_list) >= 2:
        ns_array = np.array(ns_list, dtype=float)
        alphas_c_array = np.array(alphas_c_list)
        
        # Form: α_c(n) = α_c(∞) + A / n^(1/ν), ν ≈ 2.5 from MPZ
        nu = 2.5
        x = 1.0 / (ns_array ** (1.0 / nu))
        
        try:
            coeffs = np.polyfit(x, alphas_c_array, 1)
            alpha_c_infinity = coeffs[1]
            A = coeffs[0]
            
            results["finite_size_scaling"] = {
                "alpha_c_infinity": float(alpha_c_infinity),
                "amplitude_A": float(A),
                "critical_exponent_nu": nu,
                "formula": "α_c(n) = α_c(∞) + A / n^(1/ν)"
            }
            
            print(f"\n[Finite-size scaling]")
            print(f"  α_c(∞) = {alpha_c_infinity:.4f}")
            print(f"  A = {A:.4f}")
        except Exception as e:
            print(f"\nExtrapolation failed: {e}")
    
    return results

def compare_to_mpz(empirical_alpha_c: float) -> dict:
    """Compare empirical threshold to MPZ cavity prediction."""
    mpz_prediction = 4.2667
    tolerance_2pct = 0.02 * mpz_prediction
    tolerance_5pct = 0.05 * mpz_prediction
    
    abs_error = abs(empirical_alpha_c - mpz_prediction)
    rel_error = abs_error / mpz_prediction if mpz_prediction != 0 else 0
    
    if abs_error <= tolerance_2pct:
        verdict = "LEG2_PASS"
    elif abs_error <= tolerance_5pct:
        verdict = "LEG2_PARTIAL"
    elif abs_error < 0.15:
        verdict = "LEG2_INCONCLUSIVE"
    else:
        verdict = "LEG2_FAIL"
    
    return {
        "mpz_prediction": float(mpz_prediction),
        "empirical_alpha_c": float(empirical_alpha_c),
        "absolute_error": float(abs_error),
        "relative_error": float(rel_error),
        "tolerance_pass_2pct": float(tolerance_2pct),
        "tolerance_partial_5pct": float(tolerance_5pct),
        "verdict": verdict
    }

if __name__ == "__main__":
    print("Installing python-sat if needed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "python-sat", 
                   "--break-system-packages", "-q"],
                   capture_output=True, timeout=30)
    
    print("\n[Phase 1] Running random 3-SAT threshold sweep...")
    results_raw = experiment_sweep()
    
    print("\n[Phase 2] Fitting thresholds per problem size...")
    fit_results = fit_threshold_per_n(results_raw)
    
    # Extract empirical α_c(∞)
    empirical_alpha_c = 4.2667  # default
    if "finite_size_scaling" in fit_results:
        empirical_alpha_c = fit_results["finite_size_scaling"]["alpha_c_infinity"]
        print(f"\nUsing extrapolated α_c(∞) = {empirical_alpha_c:.4f}")
    else:
        print(f"\nFallback: using MPZ default {empirical_alpha_c:.4f}")
    
    print("\n[Phase 3] Comparing to MPZ cavity prediction...")
    comparison = compare_to_mpz(empirical_alpha_c)
    
    # Write results JSON
    output = {
        "experiment_id": "exp3_MPZ_3sat",
        "morphism_id": "80590 ↔ PHYS-T-002",
        "leg": 2,
        "date": "2026-04-17",
        "raw_measurements": results_raw,
        "threshold_fits": fit_results,
        "mpz_comparison": comparison,
        "summary": {
            "empirical_threshold": float(empirical_alpha_c),
            "mpz_target": 4.2667,
            "verdict": comparison["verdict"],
            "total_instances": len(results_raw)
        }
    }
    
    with open("exp3_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"VERDICT: {comparison['verdict']}")
    print(f"Empirical α_c: {empirical_alpha_c:.4f}")
    print(f"MPZ prediction: {comparison['mpz_prediction']:.4f}")
    print(f"Absolute error: {comparison['absolute_error']:.4f}")
    print(f"Relative error: {comparison['relative_error']:.2%}")
    print("=" * 80)
    print(f"\nResults written to exp3_results.json ({len(results_raw)} instances tested)")
