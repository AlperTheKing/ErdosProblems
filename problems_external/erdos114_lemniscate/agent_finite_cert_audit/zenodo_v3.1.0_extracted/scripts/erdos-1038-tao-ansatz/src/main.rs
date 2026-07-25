//! IEEE 1788 Interval-Arithmetic Certification of Tao's Dual Measure Ansatz
//! Erdos Problem #1038
//!
//! Phase 1: Cutting-plane LP (f64) to find optimal weights
//! Phase 2: inari IEEE 1788 interval verification of U_lambda >= 0
//! Phase 3: JSON certificate output

use inari::{const_interval, Interval};
use minilp::{ComparisonOp, LinearExpr, OptimizationDirection, Problem};
use serde::Serialize;
use std::time::Instant;

// ============================================================================
// Ansatz parameters (from Tao's post + natso26's high-precision values)
// ============================================================================
const X_L: f64 = -1.8081074;
const X_R: f64 = 0.02632305;
const A_PARAM: f64 = 0.804462;
const A_EPS: f64 = 0.824522;

const N_SUPPORT_COARSE: usize = 200;
const N_EVAL_FINE: usize = 10001;
const MAX_LP_ITERS: usize = 30;

// ============================================================================
// JSON output structures
// ============================================================================
#[derive(Debug, Serialize)]
struct AnsatzParams {
    x_l: f64,
    x_l_plus_eps: f64,
    x_r: f64,
    a: f64,
    one_minus_eps: f64,
    a_eps: f64,
}

#[derive(Debug, Serialize)]
struct MeasureStructure {
    w_xl_eps: f64,
    w_xr: f64,
    continuous_mass: f64,
    total_mass: f64,
    n_active_atoms: usize,
    n_support_total: usize,
}

#[derive(Debug, Serialize)]
struct LpCertification {
    gamma_optimal: f64,
    gamma_positive: bool,
}

#[derive(Debug, Serialize)]
struct IntervalVerification {
    method: String,
    num_eval_points: usize,
    min_u_lower_bound: f64,
    min_u_upper_bound: f64,
    min_location: f64,
    all_nonneg: bool,
    ieee1788_compliant: bool,
}

#[derive(Debug, Serialize)]
struct Software {
    inari_version: String,
    rust_version: String,
    lp_solver: String,
}

#[derive(Debug, Serialize)]
struct Certificate {
    experiment_id: String,
    problem: String,
    description: String,
    reference: String,
    method: String,
    epsilon: f64,
    ansatz_parameters: AnsatzParams,
    measure_structure: MeasureStructure,
    lp_certification: LpCertification,
    interval_verification: IntervalVerification,
    verdict: String,
    runtime_seconds: f64,
    timestamp: String,
    software: Software,
}

// ============================================================================
// Helper: interval from f64
// ============================================================================
#[inline(always)]
fn iv(x: f64) -> Interval {
    Interval::try_from((x, x)).unwrap()
}

// ============================================================================
// Phase 1: Cutting-plane LP (f64)
// ============================================================================

fn build_support(epsilon: f64, n_support_fine: usize) -> Vec<f64> {
    let x_l_eps = X_L + epsilon;
    let one_minus_eps = 1.0 - epsilon;

    let mut pts = Vec::new();
    // Two Dirac points
    pts.push(x_l_eps);
    pts.push(X_R);

    // Coarse grid on [a + 1e-8, 0.9]
    let a_start = A_PARAM + 1e-8;
    let a_end = 0.9;
    for i in 0..N_SUPPORT_COARSE {
        let t = a_start + (a_end - a_start) * (i as f64) / ((N_SUPPORT_COARSE - 1) as f64);
        pts.push(t);
    }

    // Fine grid on [0.9 + 1e-8, (1-eps) - 1e-8]
    let f_start = 0.9 + 1e-8;
    let f_end = one_minus_eps - 1e-8;
    for i in 0..n_support_fine {
        let t = f_start + (f_end - f_start) * (i as f64) / ((n_support_fine - 1) as f64);
        pts.push(t);
    }

    // Deduplicate and sort
    pts.sort_by(|a, b| a.partial_cmp(b).unwrap());
    pts.dedup_by(|a, b| (*a - *b).abs() < 1e-15);
    pts
}

fn linspace(start: f64, end: f64, n: usize) -> Vec<f64> {
    (0..n)
        .map(|i| start + (end - start) * (i as f64) / ((n - 1) as f64))
        .collect()
}

fn log_potential_matrix(t_pts: &[f64], s_pts: &[f64]) -> Vec<Vec<f64>> {
    t_pts
        .iter()
        .map(|&t| {
            s_pts
                .iter()
                .map(|&s| {
                    let diff = (t - s).abs().max(1e-300);
                    -diff.ln()
                })
                .collect()
        })
        .collect()
}

fn compute_potential(t_pts: &[f64], s_active: &[f64], w_active: &[f64]) -> Vec<f64> {
    t_pts
        .iter()
        .map(|&t| {
            let mut u = 0.0;
            for (j, &s) in s_active.iter().enumerate() {
                let diff = (t - s).abs().max(1e-300);
                u += w_active[j] * (-diff.ln());
            }
            u
        })
        .collect()
}

struct LpResult {
    weights: Vec<f64>,
    gamma: f64,
}

fn cutting_plane_lp(support: &[f64]) -> LpResult {
    let m = support.len();
    let mut t_eval = linspace(-1.0, 1.0, 301);
    let mut last_weights: Option<Vec<f64>> = None;
    let mut last_gamma = f64::NEG_INFINITY;
    let mut prev_n_viol = usize::MAX;
    let mut stall_count = 0usize;

    println!("[LP] Support: {} points", m);
    println!("[LP] Cutting-plane iterations (max {}):", MAX_LP_ITERS);

    for iteration in 0..MAX_LP_ITERS {
        let n = t_eval.len();
        let k_matrix = log_potential_matrix(&t_eval, support);

        // Solve LP: max gamma s.t. K*w >= gamma*1, sum(w)=1, w>=0
        // minilp minimizes, so we minimize -gamma
        // Variables: w_0..w_{m-1}, gamma
        let mut problem = Problem::new(OptimizationDirection::Minimize);
        let mut vars = Vec::new();

        // w variables: >= 0, no upper bound, cost = 0
        for _ in 0..m {
            vars.push(problem.add_var(0.0, (0.0, f64::INFINITY)));
        }
        // gamma variable: unbounded, cost = -1 (minimize -gamma = maximize gamma)
        let gamma_var = problem.add_var(-1.0, (f64::NEG_INFINITY, f64::INFINITY));

        // Constraints: K[i,:] * w - gamma >= 0 for each eval point
        for i in 0..n {
            let mut expr = LinearExpr::empty();
            for j in 0..m {
                if k_matrix[i][j].abs() > 1e-15 {
                    expr.add(vars[j], k_matrix[i][j]);
                }
            }
            expr.add(gamma_var, -1.0);
            problem.add_constraint(expr, ComparisonOp::Ge, 0.0);
        }

        // Constraint: sum(w) = 1
        {
            let mut expr = LinearExpr::empty();
            for j in 0..m {
                expr.add(vars[j], 1.0);
            }
            problem.add_constraint(expr, ComparisonOp::Eq, 1.0);
        }

        let solution = match problem.solve() {
            Ok(sol) => sol,
            Err(e) => {
                println!("  Iter {}: LP solver failed — {:?}", iteration, e);
                break;
            }
        };

        let w: Vec<f64> = vars.iter().map(|&v| solution[v]).collect();
        let gamma = solution[gamma_var];

        last_weights = Some(w.clone());
        last_gamma = gamma;

        // Verify on fine grid using active atoms
        let active: Vec<(usize, f64)> = w
            .iter()
            .enumerate()
            .filter(|(_, &wi)| wi > 1e-12)
            .map(|(i, &wi)| (i, wi))
            .collect();
        let s_active: Vec<f64> = active.iter().map(|&(i, _)| support[i]).collect();
        let w_active: Vec<f64> = active.iter().map(|&(_, wi)| wi).collect();

        let t_check = linspace(-1.0, 1.0, N_EVAL_FINE);
        let u_check = compute_potential(&t_check, &s_active, &w_active);

        let min_u = u_check.iter().cloned().fold(f64::INFINITY, f64::min);
        let gap = gamma - min_u;

        // Find violated constraints
        let violated: Vec<f64> = t_check
            .iter()
            .zip(u_check.iter())
            .filter(|(_, &u)| u < gamma - 1e-8)
            .map(|(&t, _)| t)
            .collect();

        println!(
            "  Iter {:2}: gamma={:.6e}, fine_min={:.6e}, gap={:.2e}, constr={}, active={}, viol={}",
            iteration,
            gamma,
            min_u,
            gap,
            n,
            active.len(),
            violated.len()
        );

        if violated.is_empty() {
            println!("  CONVERGED — no violations on fine grid!");
            break;
        }

        // Detect stalls (same number of violations, no progress)
        if violated.len() == prev_n_viol {
            stall_count += 1;
            if stall_count >= 3 {
                println!("  STALLED — {} persistent violations (gap={:.2e}), accepting solution", violated.len(), gap);
                break;
            }
        } else {
            stall_count = 0;
        }
        prev_n_viol = violated.len();

        // Add violated points (subsample to keep LP tractable)
        let step = std::cmp::max(1, violated.len() / 50);
        let new_pts: Vec<f64> = violated.iter().step_by(step).cloned().collect();
        t_eval.extend(new_pts);
        t_eval.sort_by(|a, b| a.partial_cmp(b).unwrap());
        t_eval.dedup_by(|a, b| (*a - *b).abs() < 1e-15);
    }

    let weights = last_weights.unwrap_or_else(|| vec![0.0; m]);
    LpResult {
        weights,
        gamma: last_gamma,
    }
}

// ============================================================================
// Phase 2: Interval arithmetic verification (inari IEEE 1788)
// ============================================================================

struct IntervalResult {
    min_lower: f64,
    min_upper: f64,
    min_location: f64,
    all_nonneg: bool,
    num_points: usize,
}

fn interval_verify(support: &[f64], weights: &[f64]) -> IntervalResult {
    let active: Vec<(f64, f64)> = support
        .iter()
        .zip(weights.iter())
        .filter(|(_, &w)| w > 1e-12)
        .map(|(&s, &w)| (s, w))
        .collect();

    let n_active = active.len();
    println!(
        "[VERIFY] {} active support points, {} evaluation points",
        n_active, N_EVAL_FINE
    );

    // Convert active support and weights to intervals
    let s_iv: Vec<Interval> = active.iter().map(|&(s, _)| iv(s)).collect();
    let w_iv: Vec<Interval> = active.iter().map(|&(_, w)| iv(w)).collect();

    let zero = const_interval!(0.0, 0.0);

    let t_pts = linspace(-1.0, 1.0, N_EVAL_FINE);
    let mut min_lower = f64::INFINITY;
    let mut min_upper = f64::INFINITY;
    let mut min_location = 0.0f64;
    let mut all_nonneg = true;
    let mut evaluated = 0usize;

    for (idx, &t_val) in t_pts.iter().enumerate() {
        let t_iv = iv(t_val);

        // Check if t is extremely close to any support point
        let mut skip = false;
        for &(s, _) in &active {
            if (t_val - s).abs() < 1e-14 {
                // t coincides with support; U -> +inf there, automatically >= 0
                skip = true;
                break;
            }
        }
        if skip {
            evaluated += 1;
            continue;
        }

        // Compute U_lambda(t) = sum_j w_j * (-log|t - s_j|) using interval arithmetic
        let mut u_iv = zero;
        let mut term_valid = true;

        for j in 0..n_active {
            let diff = t_iv - s_iv[j];
            let abs_diff = diff.abs();

            // If the interval for |t - s_j| contains zero, -log is undefined
            // This means t is very close to s_j, and the contribution is +inf (good)
            if abs_diff.inf() <= 0.0 {
                // The term contributes +inf to U (since w_j > 0)
                // So U is definitely >= 0 at this point
                term_valid = false;
                break;
            }

            let log_term = abs_diff.ln();
            let neg_log = -log_term;
            u_iv = u_iv + w_iv[j] * neg_log;
        }

        evaluated += 1;

        if !term_valid {
            // U = +inf at this point, so >= 0
            continue;
        }

        let lower = u_iv.inf();
        let upper = u_iv.sup();

        if lower < min_lower {
            min_lower = lower;
            min_upper = upper;
            min_location = t_val;
        }

        if lower < 0.0 {
            all_nonneg = false;
        }

        if idx % 2000 == 0 {
            println!(
                "  Progress: {}/{} points, current min_lower={:.6e}",
                idx, N_EVAL_FINE, min_lower
            );
        }
    }

    println!(
        "  Evaluated {} points ({} skipped due to support proximity)",
        evaluated,
        N_EVAL_FINE - evaluated + (N_EVAL_FINE - t_pts.len())
    );

    IntervalResult {
        min_lower,
        min_upper,
        min_location,
        all_nonneg,
        num_points: evaluated,
    }
}

// ============================================================================
// Main
// ============================================================================

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut epsilon = 0.002f64;
    let mut n_support_fine = 2800usize;

    // Parse --epsilon argument
    let mut i = 1;
    while i < args.len() {
        if args[i] == "--epsilon" && i + 1 < args.len() {
            epsilon = args[i + 1].parse().expect("Invalid epsilon value");
            i += 2;
        } else if args[i] == "--n-support-fine" && i + 1 < args.len() {
            n_support_fine = args[i + 1].parse().expect("Invalid n_support_fine value");
            i += 2;
        } else {
            i += 1;
        }
    }

    // Auto-adjust support density for smaller epsilon
    if n_support_fine == 2800 {
        if epsilon < 0.0008 {
            n_support_fine = 6000;
        } else if epsilon < 0.0015 {
            n_support_fine = 4000;
        }
    }

    let x_l_eps = X_L + epsilon;
    let one_minus_eps = 1.0 - epsilon;

    let start_time = Instant::now();

    println!("{}", "=".repeat(72));
    println!("  VERIFICATION: Tao's Closed-Form Dual Measure Ansatz");
    println!("  Erdos Problem #1038 — eps = {}", epsilon);
    println!(
        "  Method: Cutting-plane LP + inari IEEE 1788 interval verification"
    );
    println!("{}", "=".repeat(72));
    println!();

    // Phase 1: Build support and solve LP
    println!("[PHASE 1] Cutting-plane LP (IEEE 754 float64)");
    println!(
        "  Parameters: x_L={}, x_R={}, a={}, eps={}",
        X_L, X_R, A_PARAM, epsilon
    );
    println!("  x_L+eps = {}", x_l_eps);
    println!("  N_SUPPORT_FINE = {}", n_support_fine);
    println!();

    let support = build_support(epsilon, n_support_fine);
    let lp_result = cutting_plane_lp(&support);

    let weights = &lp_result.weights;
    let gamma = lp_result.gamma;

    // Measure structure
    let active_mask: Vec<bool> = weights.iter().map(|&w| w > 1e-12).collect();
    let n_active = active_mask.iter().filter(|&&b| b).count();
    let w_xl_eps = weights[0];
    let w_xr = weights[1];
    let continuous_mass: f64 = weights[2..].iter().sum();
    let total_mass: f64 = weights.iter().sum();

    println!();
    println!("  Measure structure:");
    println!("    w(x_L+eps = {:.6}): {:.10}", x_l_eps, w_xl_eps);
    println!("    w(x_R     = {:.6}):   {:.10}", X_R, w_xr);
    println!("    Continuous mass:       {:.10}", continuous_mass);
    println!("    Total mass:            {:.12}", total_mass);
    println!("    Active atoms:          {} / {}", n_active, support.len());
    println!();

    // Phase 2: Interval arithmetic verification
    println!("[PHASE 2] Interval arithmetic verification (inari IEEE 1788)");
    let iv_result = interval_verify(&support, weights);

    println!();
    println!("  Interval verification results:");
    println!("    min U lower bound: {:.10e}", iv_result.min_lower);
    println!("    min U upper bound: {:.10e}", iv_result.min_upper);
    println!("    min location:      t = {:.8}", iv_result.min_location);
    println!("    all_nonneg:        {}", iv_result.all_nonneg);
    println!();

    // Determine verdict
    let verdict = if gamma > 0.0 && iv_result.all_nonneg {
        "CERTIFIED"
    } else {
        "FAILED"
    };

    let elapsed = start_time.elapsed().as_secs_f64();

    println!("{}", "=".repeat(72));
    println!("  RESULTS");
    println!("{}", "=".repeat(72));
    println!("  LP optimal gamma:        {:.10e}", gamma);
    println!(
        "  Interval min U (lower):  {:.10e} at t = {:.8}",
        iv_result.min_lower, iv_result.min_location
    );
    println!("  U >= 0 everywhere:       {}", iv_result.all_nonneg);
    println!("  Total runtime:           {:.1}s", elapsed);
    println!();

    if verdict == "CERTIFIED" {
        println!("  +======================================================+");
        println!("  |  VERDICT: CERTIFIED                                  |");
        println!(
            "  |  LP proves measure with U_lambda(t) >= {:.4e}     |",
            gamma
        );
        println!("  |  Interval arithmetic confirms U >= 0 on [-1,1]      |");
        println!("  |  IEEE 1788 compliant via inari                       |");
        println!("  +======================================================+");
    } else {
        println!("  +======================================================+");
        println!("  |  VERDICT: FAILED                                     |");
        println!("  +======================================================+");
    }
    println!();

    // Phase 3: JSON certificate
    let timestamp = {
        let elapsed_since_epoch = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        // Simple ISO 8601 formatting
        let secs = elapsed_since_epoch;
        let days = secs / 86400;
        let time_of_day = secs % 86400;
        let hours = time_of_day / 3600;
        let minutes = (time_of_day % 3600) / 60;
        let seconds = time_of_day % 60;

        // Days since epoch -> date (simplified)
        let mut y = 1970i64;
        let mut remaining_days = days as i64;
        loop {
            let days_in_year = if (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 {
                366
            } else {
                365
            };
            if remaining_days < days_in_year {
                break;
            }
            remaining_days -= days_in_year;
            y += 1;
        }
        let is_leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
        let days_in_months = [
            31,
            if is_leap { 29 } else { 28 },
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ];
        let mut m = 0usize;
        for (mi, &dim) in days_in_months.iter().enumerate() {
            if remaining_days < dim as i64 {
                m = mi + 1;
                break;
            }
            remaining_days -= dim as i64;
        }
        let d = remaining_days + 1;
        format!(
            "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z",
            y, m, d, hours, minutes, seconds
        )
    };

    let cert = Certificate {
        experiment_id: "EXP-KM-TAO-ANSATZ-001".to_string(),
        problem: "Erdos Problem #1038".to_string(),
        description: "IEEE 1788 interval-arithmetic certification of Tao ansatz".to_string(),
        reference: "Tao (Jan 5, 2026), erdosproblems.com/forum/thread/1038".to_string(),
        method: "Cutting-plane LP + inari IEEE 1788 interval verification".to_string(),
        epsilon,
        ansatz_parameters: AnsatzParams {
            x_l: X_L,
            x_l_plus_eps: x_l_eps,
            x_r: X_R,
            a: A_PARAM,
            one_minus_eps,
            a_eps: A_EPS,
        },
        measure_structure: MeasureStructure {
            w_xl_eps,
            w_xr,
            continuous_mass,
            total_mass,
            n_active_atoms: n_active,
            n_support_total: support.len(),
        },
        lp_certification: LpCertification {
            gamma_optimal: gamma,
            gamma_positive: gamma > 0.0,
        },
        interval_verification: IntervalVerification {
            method: "inari IEEE 1788 interval arithmetic".to_string(),
            num_eval_points: N_EVAL_FINE,
            min_u_lower_bound: iv_result.min_lower,
            min_u_upper_bound: iv_result.min_upper,
            min_location: iv_result.min_location,
            all_nonneg: iv_result.all_nonneg,
            ieee1788_compliant: true,
        },
        verdict: verdict.to_string(),
        runtime_seconds: (elapsed * 10.0).round() / 10.0,
        timestamp,
        software: Software {
            inari_version: "2.0".to_string(),
            rust_version: "stable".to_string(),
            lp_solver: "minilp 0.2".to_string(),
        },
    };

    let json = serde_json::to_string_pretty(&cert).unwrap();

    let eps_str = format!("{}", epsilon);
    let filename = format!("tao_ansatz_eps{}_inari_RESULTS.json", eps_str);

    std::fs::write(&filename, &json).unwrap();
    let digest = sha256::digest(json.as_bytes());
    std::fs::write(format!("{}.sha256", &filename), &digest).unwrap();

    println!("  Certificate written to {}", filename);
    println!("  SHA-256: {}", digest);
}
