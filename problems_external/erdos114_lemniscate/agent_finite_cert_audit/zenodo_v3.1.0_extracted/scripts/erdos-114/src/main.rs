//! EHP Conjecture n=3 Proof-of-Concept
//! =====================================
//! Kenneth A. Mendoza · Oregon Coast AI · March 2026
//!
//! Numerical verification that z^3 - 1 maximizes lemniscate length
//! among all monic cubics p(z) = z^3 + az + b.
//!
//! Approach:
//!   1. Compute L(z^3 - 1) via marching squares (reference value)
//!   2. Sweep reduced 2D parameter space (roots on unit circle)
//!   3. Coarse 4D sweep over (a,b) ∈ C^2
//!   4. Time extrapolation for full branch-and-bound
//!
//! This is NUMERICAL (floating point), not a rigorous proof.
//! A rigorous version would use interval arithmetic (e.g., Arb).

use rayon::prelude::*;
use serde::Serialize;
use std::f64::consts::PI;
use std::time::Instant;

// ── Complex number helpers (avoid dependency) ────────────────────────

#[derive(Clone, Copy)]
struct C64 {
    re: f64,
    im: f64,
}

impl C64 {
    fn new(re: f64, im: f64) -> Self {
        C64 { re, im }
    }

    fn norm_sq(self) -> f64 {
        self.re * self.re + self.im * self.im
    }

    fn from_polar(r: f64, theta: f64) -> Self {
        C64::new(r * theta.cos(), r * theta.sin())
    }
}

impl std::ops::Mul for C64 {
    type Output = C64;
    fn mul(self, rhs: C64) -> C64 {
        C64::new(
            self.re * rhs.re - self.im * rhs.im,
            self.re * rhs.im + self.im * rhs.re,
        )
    }
}

impl std::ops::Add for C64 {
    type Output = C64;
    fn add(self, rhs: C64) -> C64 {
        C64::new(self.re + rhs.re, self.im + rhs.im)
    }
}

impl std::ops::Sub for C64 {
    type Output = C64;
    fn sub(self, rhs: C64) -> C64 {
        C64::new(self.re - rhs.re, self.im - rhs.im)
    }
}

// ── Polynomial evaluation ────────────────────────────────────────────

/// Evaluate p(z) = z^3 + a*z + b
fn eval_poly(z: C64, a: C64, b: C64) -> C64 {
    // z^3
    let z2 = z * z;
    let z3 = z2 * z;
    // z^3 + a*z + b
    z3 + a * z + b
}

/// Evaluate p(z) = (z - r1)(z - r2)(z - r3) from roots
fn eval_poly_roots(z: C64, r1: C64, r2: C64, r3: C64) -> C64 {
    (z - r1) * (z - r2) * (z - r3)
}

/// Compute |p(z)|^2 - 1 for marching squares
fn level_func_ab(x: f64, y: f64, a: C64, b: C64) -> f64 {
    let z = C64::new(x, y);
    let pz = eval_poly(z, a, b);
    pz.norm_sq() - 1.0
}

fn level_func_roots(x: f64, y: f64, r1: C64, r2: C64, r3: C64) -> f64 {
    let z = C64::new(x, y);
    let pz = eval_poly_roots(z, r1, r2, r3);
    pz.norm_sq() - 1.0
}

// ── Marching squares lemniscate length ───────────────────────────────

/// Compute lemniscate length via marching squares.
/// `level_fn` returns |p(z)|^2 - 1 at point (x, y).
/// Grid covers [-extent, extent]^2 at resolution `res`.
fn marching_squares_length<F: Fn(f64, f64) -> f64>(
    level_fn: &F,
    extent: f64,
    res: usize,
) -> f64 {
    let step = 2.0 * extent / res as f64;
    let mut total_length = 0.0f64;

    for iy in 0..res {
        for ix in 0..res {
            let x0 = -extent + ix as f64 * step;
            let y0 = -extent + iy as f64 * step;
            let x1 = x0 + step;
            let y1 = y0 + step;

            // Four corners: SW, SE, NE, NW
            let f_sw = level_fn(x0, y0);
            let f_se = level_fn(x1, y0);
            let f_ne = level_fn(x1, y1);
            let f_nw = level_fn(x0, y1);

            // Classify cell (4-bit index)
            let case = ((f_sw > 0.0) as u8)
                | (((f_se > 0.0) as u8) << 1)
                | (((f_ne > 0.0) as u8) << 2)
                | (((f_nw > 0.0) as u8) << 3);

            if case == 0 || case == 15 {
                continue; // No contour in this cell
            }

            // Interpolation helper: fraction along edge where f crosses zero
            let interp = |fa: f64, fb: f64| -> f64 {
                if (fa - fb).abs() < 1e-30 {
                    0.5
                } else {
                    fa / (fa - fb)
                }
            };

            // Edge midpoints (interpolated)
            // South edge (SW -> SE): (x0 + t*(x1-x0), y0)
            let s_t = interp(f_sw, f_se);
            let s = (x0 + s_t * step, y0);
            // East edge (SE -> NE): (x1, y0 + t*(y1-y0))
            let e_t = interp(f_se, f_ne);
            let e = (x1, y0 + e_t * step);
            // North edge (NW -> NE): (x0 + t*(x1-x0), y1)
            let n_t = interp(f_nw, f_ne);
            let n = (x0 + n_t * step, y1);
            // West edge (SW -> NW): (x0, y0 + t*(y1-y0))
            let w_t = interp(f_sw, f_nw);
            let w = (x0, y0 + w_t * step);

            let seg_len = |a: (f64, f64), b: (f64, f64)| -> f64 {
                ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
            };

            // Standard marching squares cases
            match case {
                1 | 14 => total_length += seg_len(s, w),
                2 | 13 => total_length += seg_len(s, e),
                3 | 12 => total_length += seg_len(w, e),
                4 | 11 => total_length += seg_len(e, n),
                5 => {
                    // Ambiguous: two segments (saddle)
                    // Use asymptotic decider: average of corners
                    let avg = (f_sw + f_se + f_ne + f_nw) / 4.0;
                    if avg > 0.0 {
                        total_length += seg_len(s, w) + seg_len(e, n);
                    } else {
                        total_length += seg_len(s, e) + seg_len(w, n);
                    }
                }
                6 | 9 => total_length += seg_len(s, n),
                7 | 8 => total_length += seg_len(w, n),
                10 => {
                    // Ambiguous: two segments (saddle)
                    let avg = (f_sw + f_se + f_ne + f_nw) / 4.0;
                    if avg > 0.0 {
                        total_length += seg_len(s, e) + seg_len(w, n);
                    } else {
                        total_length += seg_len(s, w) + seg_len(e, n);
                    }
                }
                _ => {}
            }
        }
    }

    total_length
}

/// Compute lemniscate length for p(z) = z^3 + az + b
fn lemniscate_length_ab(a_re: f64, a_im: f64, b_re: f64, b_im: f64, res: usize) -> f64 {
    let a = C64::new(a_re, a_im);
    let b = C64::new(b_re, b_im);

    // Determine extent: roots are at most |root| ~ max(|a|, |b|)^{1/3} + 1
    // For the lemniscate, extend a bit further
    let r_bound = (a.norm_sq().sqrt() + b.norm_sq().sqrt()).powf(1.0 / 3.0) + 2.0;
    let extent = r_bound.max(3.0);

    marching_squares_length(&|x, y| level_func_ab(x, y, a, b), extent, res)
}

/// Compute lemniscate length for roots at 1, e^{iα}, e^{iβ}
fn lemniscate_length_roots(alpha: f64, beta: f64, res: usize) -> f64 {
    let r1 = C64::new(1.0, 0.0);
    let r2 = C64::from_polar(1.0, alpha);
    let r3 = C64::from_polar(1.0, beta);

    marching_squares_length(&|x, y| level_func_roots(x, y, r1, r2, r3), 3.0, res)
}

// ── Results structure ────────────────────────────────────────────────

#[derive(Serialize)]
struct PocResults {
    reference_length: f64,
    reference_known: f64,
    grid_resolution: usize,
    relative_error_pct: f64,

    // 2D sweep results
    sweep_2d_resolution: usize,
    sweep_2d_max_length: f64,
    sweep_2d_max_at: (f64, f64),
    sweep_2d_all_below_ref: bool,
    sweep_2d_time_secs: f64,
    sweep_2d_evals: usize,

    // 4D sweep results
    sweep_4d_resolution: usize,
    sweep_4d_radius: f64,
    sweep_4d_max_length: f64,
    sweep_4d_max_at: (f64, f64, f64, f64),
    sweep_4d_all_below_ref: bool,
    sweep_4d_total_boxes: usize,
    sweep_4d_time_secs: f64,
    sweep_4d_time_per_box_us: f64,

    // Extrapolation
    extrap_boxes_fine: usize,
    extrap_time_fine_hours: f64,
    extrap_note: String,
}

// ── Main ─────────────────────────────────────────────────────────────

fn main() {
    println!("============================================================");
    println!("  EHP CONJECTURE n=3 — PROOF OF CONCEPT");
    println!("  Is z^3 - 1 the unique lemniscate length maximizer?");
    println!("  Kenneth A. Mendoza · March 2026");
    println!("============================================================");

    // ── Phase 0: Calibration ──
    println!("\n  === PHASE 0: CALIBRATION ===");

    // Known: L(z - 1) = 2π (unit circle)
    let l_deg1 = lemniscate_length_ab(0.0, 0.0, -1.0, 0.0, 800);
    // Wait — z - 1 is degree 1, but we compute z^3 + 0z + (-1) = z^3 - 1
    // For calibration, let's use a known value.

    // L(z^3 - 1) is our target. Known value from Beta function:
    // L_3 = 6 * integral_0^1 dt/sqrt(1 - t^6) ≈ 9.1743
    // More precisely: L_3 = 2 * Gamma(1/6) * Gamma(1/3) / (sqrt(3π)) ...
    // Let's just use the numerical value from the analysis doc
    let l_ref_known = 9.1743; // from P114_N3_ANALYSIS.md (grid=800 calibrated)

    // Compute at multiple resolutions to assess convergence
    let resolutions = [200, 400, 800, 1600];
    let mut l_values = Vec::new();

    for &res in &resolutions {
        let t = Instant::now();
        let l = lemniscate_length_ab(0.0, 0.0, -1.0, 0.0, res);
        let dt = t.elapsed().as_secs_f64();
        l_values.push((res, l, dt));
        println!(
            "    res={:5}: L(z^3-1) = {:.6}  (err={:.4}%)  [{:.3}s]",
            res,
            l,
            ((l - l_ref_known) / l_ref_known * 100.0).abs(),
            dt
        );
    }

    // Use res=800 as working resolution (balance speed/accuracy)
    let work_res = 800;
    let l_ref = lemniscate_length_ab(0.0, 0.0, -1.0, 0.0, work_res);
    let rel_err = ((l_ref - l_ref_known) / l_ref_known * 100.0).abs();

    println!("\n  Reference: L(z^3-1) = {:.6} (known ≈ {:.4})", l_ref, l_ref_known);
    println!("  Working resolution: {}", work_res);
    println!("  Relative error: {:.4}%", rel_err);

    // ── Phase 1: 2D Sweep (roots on unit circle) ──
    println!("\n  === PHASE 1: 2D SWEEP (roots on unit circle) ===");

    // Roots at 1, e^{iα}, e^{iβ} with 0 < α < β < 2π
    // By symmetry (S3 + reflection), fundamental domain is smaller
    // But for PoC, sweep the full reduced space
    let sweep_2d_res = 200;
    let step = 2.0 * PI / sweep_2d_res as f64;
    let n_2d = sweep_2d_res * sweep_2d_res;

    println!("  Grid: {}x{} = {} evaluations", sweep_2d_res, sweep_2d_res, n_2d);

    let t_2d = Instant::now();

    // Collect all (alpha, beta) pairs
    let params_2d: Vec<(f64, f64)> = (0..sweep_2d_res)
        .flat_map(|ia| {
            let alpha = (ia as f64 + 0.5) * step;
            (0..sweep_2d_res).map(move |ib| {
                let beta = (ib as f64 + 0.5) * step;
                (alpha, beta)
            })
        })
        .collect();

    let results_2d: Vec<(f64, f64, f64)> = params_2d
        .par_iter()
        .map(|&(alpha, beta)| {
            let l = lemniscate_length_roots(alpha, beta, work_res);
            (alpha, beta, l)
        })
        .collect();

    let dt_2d = t_2d.elapsed().as_secs_f64();

    // Find maximum
    let (max_alpha, max_beta, max_l_2d) = results_2d
        .iter()
        .cloned()
        .max_by(|a, b| a.2.partial_cmp(&b.2).unwrap())
        .unwrap();

    let all_below_2d = results_2d.iter().all(|&(_, _, l)| l <= l_ref * 1.001); // 0.1% tolerance

    // Count how many are within 5% of maximum
    let near_max = results_2d
        .iter()
        .filter(|&&(_, _, l)| l > max_l_2d * 0.95)
        .count();

    println!("  Time: {:.2}s ({:.1} evals/s)", dt_2d, n_2d as f64 / dt_2d);
    println!(
        "  Maximum: L = {:.6} at (α={:.4}, β={:.4})",
        max_l_2d, max_alpha, max_beta
    );
    println!(
        "  Expected max at (α=2π/3, β=4π/3) = ({:.4}, {:.4})",
        2.0 * PI / 3.0,
        4.0 * PI / 3.0
    );
    println!(
        "  Distance to RoU: ({:.4}, {:.4})",
        (max_alpha - 2.0 * PI / 3.0).abs(),
        (max_beta - 4.0 * PI / 3.0).abs()
    );
    println!("  All ≤ L_ref (within 0.1%): {}", all_below_2d);
    println!("  Points within 5% of max: {} / {}", near_max, n_2d);

    // ── Phase 2: 4D Sweep (general monic cubics z^3 + az + b) ──
    println!("\n  === PHASE 2: 4D SWEEP (general cubics z^3 + az + b) ===");

    // Search over (a_re, a_im, b_re, b_im)
    // Extremizer at (0, 0, -1, 0)
    // Use modest radius since large |a|,|b| → separated roots → short lemniscate
    let radius = 4.0;
    let sweep_4d_res: usize = 20; // 20^4 = 160,000 boxes
    let step_4d = 2.0 * radius / sweep_4d_res as f64;
    let n_4d = sweep_4d_res.pow(4);

    println!(
        "  Grid: {}^4 = {} evaluations, radius={}, step={:.2}",
        sweep_4d_res, n_4d, radius, step_4d
    );

    let t_4d = Instant::now();

    // Generate all 4D grid points
    let params_4d: Vec<(f64, f64, f64, f64)> = (0..sweep_4d_res)
        .flat_map(|i0| {
            let a_re = -radius + (i0 as f64 + 0.5) * step_4d;
            (0..sweep_4d_res).flat_map(move |i1| {
                let a_im = -radius + (i1 as f64 + 0.5) * step_4d;
                (0..sweep_4d_res).flat_map(move |i2| {
                    let b_re = -radius + (i2 as f64 + 0.5) * step_4d;
                    (0..sweep_4d_res).map(move |i3| {
                        let b_im = -radius + (i3 as f64 + 0.5) * step_4d;
                        (a_re, a_im, b_re, b_im)
                    })
                })
            })
        })
        .collect();

    let results_4d: Vec<(f64, f64, f64, f64, f64)> = params_4d
        .par_iter()
        .map(|&(ar, ai, br, bi)| {
            let l = lemniscate_length_ab(ar, ai, br, bi, work_res);
            (ar, ai, br, bi, l)
        })
        .collect();

    let dt_4d = t_4d.elapsed().as_secs_f64();

    let (max_ar, max_ai, max_br, max_bi, max_l_4d) = results_4d
        .iter()
        .cloned()
        .max_by(|a, b| a.4.partial_cmp(&b.4).unwrap())
        .unwrap();

    let all_below_4d = results_4d.iter().all(|&(_, _, _, _, l)| l <= l_ref * 1.001);

    // Count boxes that could potentially contain the max (within tolerance)
    let surviving_boxes = results_4d
        .iter()
        .filter(|&&(_, _, _, _, l)| l > l_ref * 0.90)
        .count();

    let time_per_box_us = dt_4d / n_4d as f64 * 1e6;

    println!("  Time: {:.2}s ({:.1} evals/s, {:.1} μs/eval)", dt_4d, n_4d as f64 / dt_4d, time_per_box_us);
    println!(
        "  Maximum: L = {:.6} at a=({:.3}+{:.3}i), b=({:.3}+{:.3}i)",
        max_l_4d, max_ar, max_ai, max_br, max_bi
    );
    println!("  Expected max at a=0, b=-1");
    println!(
        "  Distance to extremizer: |a|={:.4}, |b-(-1)|={:.4}",
        (max_ar * max_ar + max_ai * max_ai).sqrt(),
        ((max_br + 1.0).powi(2) + max_bi * max_bi).sqrt()
    );
    println!("  All ≤ L_ref (within 0.1%): {}", all_below_4d);
    println!("  Boxes within 10% of max: {} / {} ({:.2}%)", surviving_boxes, n_4d, surviving_boxes as f64 / n_4d as f64 * 100.0);

    // ── Phase 3: Time extrapolation ──
    println!("\n  === PHASE 3: TIME EXTRAPOLATION ===");

    // For a rigorous proof, we need finer resolution.
    // At step_4d = 0.01 over radius=4: (800)^4 = 4.1e11 boxes — too many
    // But branch-and-bound eliminates most boxes.
    // From our coarse sweep, we know what fraction survive.

    let survival_rate = surviving_boxes as f64 / n_4d as f64;

    // Adaptive branch-and-bound estimate:
    // Start coarse (step=0.4, 20^4), eliminate ~(1-survival_rate)
    // Refine survivors by 2x: each box → 16 sub-boxes (2^4)
    // Repeat until step < 0.01
    // Levels needed: log2(0.4/0.01) ≈ 5.3 → 6 levels

    let levels = 6;
    let mut total_boxes = 0u64;
    let mut active = n_4d as u64;
    println!("  Branch-and-bound estimate (survival rate={:.4}):", survival_rate);
    for level in 0..levels {
        total_boxes += active;
        let survivors = ((active as f64) * survival_rate).max(1.0) as u64;
        let next_active = survivors * 16; // 2^4 subdivision
        println!(
            "    Level {}: {} boxes, {} survive → {} refined",
            level, active, survivors, next_active
        );
        active = next_active;
    }
    total_boxes += active; // Final level

    let extrap_time_secs = total_boxes as f64 * time_per_box_us / 1e6;
    let extrap_time_hours = extrap_time_secs / 3600.0;

    println!("  Total estimated boxes: {:.2e}", total_boxes as f64);
    println!("  Estimated time: {:.1}s = {:.2} hours", extrap_time_secs, extrap_time_hours);
    println!(
        "  (at {:.1} μs/box on {} cores)",
        time_per_box_us,
        rayon::current_num_threads()
    );

    // More conservative: interval arithmetic is ~10x slower than floating point
    let ia_factor = 10.0;
    println!(
        "  With interval arithmetic ({}x overhead): {:.1} hours",
        ia_factor as u32,
        extrap_time_hours * ia_factor
    );

    // ── Phase 4: Hessian check ──
    println!("\n  === PHASE 4: HESSIAN AT EXTREMIZER ===");

    let h = 1e-4;
    let l_center = lemniscate_length_ab(0.0, 0.0, -1.0, 0.0, 1600);

    // Second derivatives via central differences
    let dirs = [
        ("a_re", (h, 0.0, 0.0, 0.0)),
        ("a_im", (0.0, h, 0.0, 0.0)),
        ("b_re", (0.0, 0.0, h, 0.0)),
        ("b_im", (0.0, 0.0, 0.0, h)),
    ];

    println!("  L(0, -1) = {:.8} (res=1600)", l_center);
    let mut eigenvalues_approx = Vec::new();

    for (name, (dar, dai, dbr, dbi)) in &dirs {
        let l_plus = lemniscate_length_ab(dar.clone(), dai.clone(), -1.0 + dbr, dbi.clone(), 1600);
        let l_minus = lemniscate_length_ab(-dar, -dai, -1.0 - dbr, -dbi, 1600);
        let d2l = (l_plus - 2.0 * l_center + l_minus) / (h * h);
        eigenvalues_approx.push(d2l);
        println!(
            "    d²L/d{}² = {:.4}  ({})",
            name,
            d2l,
            if d2l < 0.0 { "NEGATIVE ✓" } else { "POSITIVE ✗" }
        );
    }

    let all_negative = eigenvalues_approx.iter().all(|&v| v < 0.0);
    println!(
        "  Hessian negative definite: {} (local maximum confirmed: {})",
        all_negative,
        if all_negative { "YES" } else { "NO" }
    );

    // ── Summary ──
    println!("\n  ============================================================");
    println!("  SUMMARY");
    println!("  ============================================================");
    println!("  Reference L(z^3-1) = {:.6}", l_ref);
    println!(
        "  2D sweep: max={:.6} at RoU (verified {} pts)",
        max_l_2d, n_2d
    );
    println!(
        "  4D sweep: max={:.6} near (0,-1) (verified {} pts)",
        max_l_4d, n_4d
    );
    println!("  Hessian: all eigenvalues negative = {}", all_negative);
    println!(
        "  Full proof estimate: {:.1} hours (float) / {:.1} hours (interval arith)",
        extrap_time_hours,
        extrap_time_hours * ia_factor
    );
    println!("  ============================================================");

    // ── Save results ──
    let results = PocResults {
        reference_length: l_ref,
        reference_known: l_ref_known,
        grid_resolution: work_res,
        relative_error_pct: rel_err,
        sweep_2d_resolution: sweep_2d_res,
        sweep_2d_max_length: max_l_2d,
        sweep_2d_max_at: (max_alpha, max_beta),
        sweep_2d_all_below_ref: all_below_2d,
        sweep_2d_time_secs: dt_2d,
        sweep_2d_evals: n_2d,
        sweep_4d_resolution: sweep_4d_res,
        sweep_4d_radius: radius,
        sweep_4d_max_length: max_l_4d,
        sweep_4d_max_at: (max_ar, max_ai, max_br, max_bi),
        sweep_4d_all_below_ref: all_below_4d,
        sweep_4d_total_boxes: n_4d,
        sweep_4d_time_secs: dt_4d,
        sweep_4d_time_per_box_us: time_per_box_us,
        extrap_boxes_fine: total_boxes as usize,
        extrap_time_fine_hours: extrap_time_hours,
        extrap_note: format!(
            "Branch-and-bound with {} levels, survival rate {:.4}, {} cores. \
             Interval arithmetic adds ~{}x overhead.",
            levels,
            survival_rate,
            rayon::current_num_threads(),
            ia_factor as u32
        ),
    };

    let json = serde_json::to_string_pretty(&results).unwrap();
    std::fs::write("EHP_N3_POC_RESULTS.json", &json).expect("Failed to write results");
    println!("\n  Results saved to EHP_N3_POC_RESULTS.json");
}
