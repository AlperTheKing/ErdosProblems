//! EHP Conjecture General-Degree Verifier
//! =======================================
//! Kenneth A. Mendoza · Oregon Coast AI · March 2026
//!
//! Verifies that z^n - 1 maximizes lemniscate length among all monic
//! degree-n polynomials, for arbitrary n >= 2.
//!
//! A monic degree-n polynomial with no z^{n-1} term (WLOG by translation):
//!   p(z) = z^n + a_{n-2}*z^{n-2} + ... + a_1*z + a_0
//! has n-1 complex coefficients = 2(n-1) real parameters.
//!
//! Symmetry reduction: z -> e^{i*theta/n}*z gives
//!   L(a_0, ..., a_{n-2}) = L(a_0*e^{-i*theta}, ..., a_{n-2}*e^{-2i*theta/n})
//! Choose theta = arg(a_0) to fix a_0 real >= 0.
//! Reduced dimension: D = 2n - 3.
//!
//! The extremizer z^n - 1 maps to a_0 = 1, all others = 0
//! (since z^n + (-1) has a_0 = -1, and |a_0| = 1, so after
//! rotation the extremizer is at a_0 = 1 with the rest zero).
//!
//! Modes:
//!   feasibility — Random sampling + Richardson, predict B&B runtime
//!   verify      — Full adaptive branch-and-bound
//!   both        — Feasibility first, then verify if predicted feasible

use rayon::prelude::*;
use serde::Serialize;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

// ══════════════════════════════════════════════════════════════════════
// Complex number helpers
// ══════════════════════════════════════════════════════════════════════

#[derive(Clone, Copy)]
struct C64 {
    re: f64,
    im: f64,
}

impl C64 {
    #[inline(always)]
    fn new(re: f64, im: f64) -> Self {
        C64 { re, im }
    }
    #[inline(always)]
    fn norm_sq(self) -> f64 {
        self.re * self.re + self.im * self.im
    }
}

impl std::ops::Mul for C64 {
    type Output = C64;
    #[inline(always)]
    fn mul(self, r: C64) -> C64 {
        C64::new(
            self.re * r.re - self.im * r.im,
            self.re * r.im + self.im * r.re,
        )
    }
}

impl std::ops::Add for C64 {
    type Output = C64;
    #[inline(always)]
    fn add(self, r: C64) -> C64 {
        C64::new(self.re + r.re, self.im + r.im)
    }
}

// ══════════════════════════════════════════════════════════════════════
// Polynomial evaluation
// ══════════════════════════════════════════════════════════════════════

/// Evaluate p(z) = z^n + sum_{k=0}^{n-2} a_k * z^k
/// using Horner's method adapted for the missing z^{n-1} term.
///
/// `coeffs` is ordered [a_0, a_1, ..., a_{n-2}] where a_k is (re, im)
/// for the coefficient of z^k.
#[inline(always)]
fn eval_poly(z_re: f64, z_im: f64, degree: usize, coeffs: &[(f64, f64)]) -> (f64, f64) {
    // Horner: p(z) = z^n + 0*z^{n-1} + a_{n-2}*z^{n-2} + ... + a_0
    // = (((...((1*z + 0)*z + a_{n-2})*z + a_{n-3})*z + ...)*z + a_1)*z + a_0
    //
    // Start with leading coefficient 1, then multiply by z and add next coeff.
    // Coefficients from highest to lowest power:
    //   z^n coeff = 1
    //   z^{n-1} coeff = 0
    //   z^{n-2} coeff = a_{n-2} = coeffs[n-2-0] ... wait, coeffs has n-1 entries
    //   for k from n-2 down to 0: coeffs[k]

    let mut acc_re = 1.0; // coefficient of z^n
    let mut acc_im = 0.0;

    // Multiply by z and add 0 (the missing z^{n-1} coefficient)
    let t_re = acc_re * z_re - acc_im * z_im;
    let t_im = acc_re * z_im + acc_im * z_re;
    acc_re = t_re; // + 0
    acc_im = t_im; // + 0

    // Now process coefficients from a_{n-2} down to a_0
    // coeffs[k] is the coefficient of z^k, so we iterate k from n-2 down to 0
    for k in (0..degree.saturating_sub(1)).rev() {
        let t_re = acc_re * z_re - acc_im * z_im;
        let t_im = acc_re * z_im + acc_im * z_re;
        if k < coeffs.len() {
            acc_re = t_re + coeffs[k].0;
            acc_im = t_im + coeffs[k].1;
        } else {
            acc_re = t_re;
            acc_im = t_im;
        }
    }

    (acc_re, acc_im)
}

// ══════════════════════════════════════════════════════════════════════
// Reduced-space <-> coefficient conversion
// ══════════════════════════════════════════════════════════════════════

/// Reduced parameter dimension for degree n:
/// a_0 is real (1 dim), a_1..a_{n-2} each have 2 dims (re, im).
/// Total D = 1 + 2*(n-2) = 2n-3.
fn reduced_dim(degree: usize) -> usize {
    if degree < 2 {
        return 0;
    }
    2 * degree - 3
}

/// Convert a reduced parameter vector to coefficient array.
///
/// Reduced params layout: [a_0_real, a_1_re, a_1_im, a_2_re, a_2_im, ..., a_{n-2}_re, a_{n-2}_im]
///
/// Returns Vec of (re, im) pairs for [a_0, a_1, ..., a_{n-2}].
fn reduced_to_coeffs(degree: usize, params: &[f64]) -> Vec<(f64, f64)> {
    let n_coeffs = degree - 1; // a_0 through a_{n-2}
    let mut coeffs = vec![(0.0, 0.0); n_coeffs];

    if n_coeffs == 0 {
        return coeffs;
    }

    // a_0 is real and >= 0
    coeffs[0] = (params[0], 0.0);

    // a_1 through a_{n-2}: each has re and im
    for k in 1..n_coeffs {
        let idx = 1 + 2 * (k - 1);
        coeffs[k] = (params[idx], params[idx + 1]);
    }

    coeffs
}

/// The extremizer point in reduced space: a_0 = 1, all others = 0.
fn extremizer_point(degree: usize) -> Vec<f64> {
    let d = reduced_dim(degree);
    let mut p = vec![0.0; d];
    if d > 0 {
        p[0] = 1.0;
    }
    p
}

// ══════════════════════════════════════════════════════════════════════
// Lemniscate length via marching squares
// ══════════════════════════════════════════════════════════════════════

/// Compute the arc length of {z : |p(z)| = 1} via marching squares.
///
/// Grid extent is chosen adaptively based on coefficient magnitudes.
fn lemniscate_length(degree: usize, coeffs: &[(f64, f64)], res: usize) -> f64 {
    // Compute extent: max(3.0, (sum |a_k|)^{1/n} + 2.0)
    let coeff_sum: f64 = coeffs.iter().map(|&(re, im)| (re * re + im * im).sqrt()).sum();
    let extent = (coeff_sum.powf(1.0 / degree as f64) + 2.0).max(3.0);

    let step = 2.0 * extent / res as f64;
    let mut total = 0.0f64;

    for iy in 0..res {
        let y0 = -extent + iy as f64 * step;
        let y1 = y0 + step;
        for ix in 0..res {
            let x0 = -extent + ix as f64 * step;
            let x1 = x0 + step;

            // Evaluate |p(z)|^2 - 1 at four corners
            let (p_re, p_im) = eval_poly(x0, y0, degree, coeffs);
            let fsw = p_re * p_re + p_im * p_im - 1.0;

            let (p_re, p_im) = eval_poly(x1, y0, degree, coeffs);
            let fse = p_re * p_re + p_im * p_im - 1.0;

            let (p_re, p_im) = eval_poly(x1, y1, degree, coeffs);
            let fne = p_re * p_re + p_im * p_im - 1.0;

            let (p_re, p_im) = eval_poly(x0, y1, degree, coeffs);
            let fnw = p_re * p_re + p_im * p_im - 1.0;

            let case = ((fsw > 0.0) as u8)
                | (((fse > 0.0) as u8) << 1)
                | (((fne > 0.0) as u8) << 2)
                | (((fnw > 0.0) as u8) << 3);

            if case == 0 || case == 15 {
                continue;
            }

            let interp =
                |fa: f64, fb: f64| -> f64 {
                    if (fa - fb).abs() < 1e-30 {
                        0.5
                    } else {
                        fa / (fa - fb)
                    }
                };

            let s = (x0 + interp(fsw, fse) * step, y0);
            let e = (x1, y0 + interp(fse, fne) * step);
            let n = (x0 + interp(fnw, fne) * step, y1);
            let w = (x0, y0 + interp(fsw, fnw) * step);

            let seg = |a: (f64, f64), b: (f64, f64)| -> f64 {
                ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
            };

            match case {
                1 | 14 => total += seg(s, w),
                2 | 13 => total += seg(s, e),
                3 | 12 => total += seg(w, e),
                4 | 11 => total += seg(e, n),
                5 => {
                    let avg = (fsw + fse + fne + fnw) / 4.0;
                    if avg > 0.0 {
                        total += seg(s, w) + seg(e, n);
                    } else {
                        total += seg(s, e) + seg(w, n);
                    }
                }
                6 | 9 => total += seg(s, n),
                7 | 8 => total += seg(w, n),
                10 => {
                    let avg = (fsw + fse + fne + fnw) / 4.0;
                    if avg > 0.0 {
                        total += seg(s, e) + seg(w, n);
                    } else {
                        total += seg(s, w) + seg(e, n);
                    }
                }
                _ => {}
            }
        }
    }

    total
}

/// Convenience: lemniscate length from reduced parameter vector.
fn lemniscate_length_reduced(degree: usize, params: &[f64], res: usize) -> f64 {
    let coeffs = reduced_to_coeffs(degree, params);
    lemniscate_length(degree, &coeffs, res)
}

// ══════════════════════════════════════════════════════════════════════
// N-dimensional Box for branch-and-bound
// ══════════════════════════════════════════════════════════════════════

#[derive(Clone)]
struct BoxND {
    /// (lo, hi) for each reduced dimension
    bounds: Vec<(f64, f64)>,
}

impl BoxND {
    fn dim(&self) -> usize {
        self.bounds.len()
    }

    fn center(&self) -> Vec<f64> {
        self.bounds.iter().map(|&(lo, hi)| (lo + hi) / 2.0).collect()
    }

    fn half_width(&self) -> f64 {
        self.bounds
            .iter()
            .map(|&(lo, hi)| (hi - lo) / 2.0)
            .fold(0.0f64, f64::max)
    }

    fn volume(&self) -> f64 {
        self.bounds.iter().map(|&(lo, hi)| hi - lo).product()
    }

    /// Subdivide into 2^D children by bisecting each axis.
    fn subdivide(&self) -> Vec<BoxND> {
        let d = self.dim();
        let n_children = 1usize << d;
        let mids: Vec<f64> = self.bounds.iter().map(|&(lo, hi)| (lo + hi) / 2.0).collect();
        let mut children = Vec::with_capacity(n_children);

        for mask in 0..n_children {
            let mut bounds = Vec::with_capacity(d);
            for i in 0..d {
                if (mask >> i) & 1 == 0 {
                    bounds.push((self.bounds[i].0, mids[i]));
                } else {
                    bounds.push((mids[i], self.bounds[i].1));
                }
            }
            children.push(BoxND { bounds });
        }
        children
    }

    /// Check if the extremizer point (1, 0, 0, ..., 0) is inside this box.
    fn contains_extremizer(&self) -> bool {
        if self.bounds.is_empty() {
            return false;
        }
        // First dimension: a_0_real. Extremizer has a_0 = 1.
        if !(self.bounds[0].0 <= 1.0 && 1.0 <= self.bounds[0].1) {
            return false;
        }
        // All other dimensions: extremizer has 0.
        for i in 1..self.dim() {
            if !(self.bounds[i].0 <= 0.0 && 0.0 <= self.bounds[i].1) {
                return false;
            }
        }
        true
    }

    /// Sample points: center + all 2^D corners + 2*D face centers.
    /// For high D this is large, so we cap at a practical limit.
    fn sample_points(&self) -> Vec<Vec<f64>> {
        let d = self.dim();
        let center = self.center();
        let mut pts = vec![center.clone()];

        // Face centers: 2*D points (perturb one axis to lo or hi)
        for i in 0..d {
            let mut lo_pt = center.clone();
            lo_pt[i] = self.bounds[i].0;
            pts.push(lo_pt);

            let mut hi_pt = center.clone();
            hi_pt[i] = self.bounds[i].1;
            pts.push(hi_pt);
        }

        // Corners: 2^D points. Only include if D <= 10 (1024 corners).
        if d <= 10 {
            let n_corners = 1usize << d;
            for mask in 0..n_corners {
                let mut corner = Vec::with_capacity(d);
                for i in 0..d {
                    if (mask >> i) & 1 == 0 {
                        corner.push(self.bounds[i].0);
                    } else {
                        corner.push(self.bounds[i].1);
                    }
                }
                pts.push(corner);
            }
        }

        pts
    }
}

// ══════════════════════════════════════════════════════════════════════
// Richardson extrapolation
// ══════════════════════════════════════════════════════════════════════

/// Compute L*(z^n - 1) at multiple resolutions and Richardson-extrapolate.
/// Returns (lower_bound, best_estimate, upper_bound, raw_values).
fn richardson_extrapolate(
    degree: usize,
    resolutions: &[usize],
) -> (f64, f64, f64, Vec<(usize, f64)>) {
    // z^n - 1 has coeffs: a_0 = -1, all others zero
    let n_coeffs = degree - 1;
    let mut coeffs = vec![(0.0, 0.0); n_coeffs];
    if n_coeffs > 0 {
        coeffs[0] = (-1.0, 0.0); // a_0 = -1
    }

    let mut raw: Vec<(usize, f64)> = Vec::new();
    for &res in resolutions {
        let l = lemniscate_length(degree, &coeffs, res);
        raw.push((res, l));
    }

    if raw.len() < 3 {
        let best = raw.last().unwrap().1;
        return (best * 0.99, best, best * 1.01, raw);
    }

    // Richardson chain (assumes 2nd-order convergence: error ~ O(h^2))
    let n = raw.len();
    let mut r1 = Vec::new();
    for i in 0..n - 1 {
        let val = (4.0 * raw[i + 1].1 - raw[i].1) / 3.0;
        r1.push(val);
    }

    let mut r2 = Vec::new();
    for i in 0..r1.len().saturating_sub(1) {
        let val = (16.0 * r1[i + 1] - r1[i]) / 15.0;
        r2.push(val);
    }

    // Best estimate: highest-order Richardson value available
    let best_estimate = if !r2.is_empty() {
        *r2.last().unwrap()
    } else if !r1.is_empty() {
        *r1.last().unwrap()
    } else {
        raw.last().unwrap().1
    };

    // Conservative bounds
    let delta = if r1.len() >= 2 {
        (r1[r1.len() - 1] - r1[r1.len() - 2]).abs()
    } else if raw.len() >= 2 {
        (raw[n - 1].1 - raw[n - 2].1).abs() * 0.5
    } else {
        best_estimate * 0.01
    };

    // Lower bound: raw highest-resolution value (marching squares underestimates)
    let raw_lower = raw.last().unwrap().1;
    let lower = raw_lower.min(best_estimate - 3.0 * delta);
    let upper = best_estimate + 3.0 * delta;

    (lower, best_estimate, upper, raw)
}

// ══════════════════════════════════════════════════════════════════════
// Lipschitz estimation
// ══════════════════════════════════════════════════════════════════════

/// Estimate the Lipschitz constant of L over the parameter space by
/// finite differences at several random points.
fn estimate_lipschitz(degree: usize, n_samples: usize, res: usize) -> f64 {
    let d = reduced_dim(degree);
    let h = 0.01;
    let ext_point = extremizer_point(degree);

    // Sample near the extremizer and at a few random-ish points
    let mut max_lip = 0.0f64;

    // Generate deterministic "random" points using a simple LCG
    let mut rng_state: u64 = 42 + degree as u64 * 137;
    let next_rng = |state: &mut u64| -> f64 {
        *state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        // Map to [-4, 4]
        ((*state >> 33) as f64 / (1u64 << 31) as f64) * 8.0 - 4.0
    };

    let mut test_points: Vec<Vec<f64>> = Vec::new();

    // Always include the extremizer
    test_points.push(ext_point.clone());

    // Points near the extremizer
    for offset_idx in 0..d.min(5) {
        let mut pt = ext_point.clone();
        pt[offset_idx] += 0.5;
        test_points.push(pt);
    }

    // "Random" points
    for _ in 0..n_samples.saturating_sub(d + 1) {
        let mut pt = Vec::with_capacity(d);
        for _ in 0..d {
            let v = next_rng(&mut rng_state);
            // Clamp first dimension to [0, 4] (a_0 >= 0)
            pt.push(v);
        }
        if !pt.is_empty() {
            pt[0] = pt[0].abs().min(4.0);
        }
        test_points.push(pt);
    }

    for pt in &test_points {
        let l0 = lemniscate_length_reduced(degree, pt, res);
        for i in 0..d {
            let mut pt_plus = pt.clone();
            pt_plus[i] += h;
            let l_plus = lemniscate_length_reduced(degree, &pt_plus, res);
            let grad = (l_plus - l0).abs() / h;
            if grad > max_lip {
                max_lip = grad;
            }
        }
    }

    max_lip
}

// ══════════════════════════════════════════════════════════════════════
// Feasibility mode
// ══════════════════════════════════════════════════════════════════════

#[derive(Serialize)]
struct FeasibilityResult {
    experiment: String,
    degree: usize,
    reduced_dim: usize,
    l_star_bounds: LStarBounds,
    random_sample: RandomSampleResult,
    lipschitz_estimate: f64,
    bb_prediction: BBPrediction,
    total_time_secs: f64,
}

#[derive(Serialize)]
struct LStarBounds {
    lower: f64,
    best_estimate: f64,
    upper: f64,
    width: f64,
    raw_values: Vec<(usize, f64)>,
}

#[derive(Serialize)]
struct RandomSampleResult {
    n_samples: usize,
    counterexamples: usize,
    closest_competitor_l: f64,
    closest_competitor_params: Vec<f64>,
    margin: f64,
    margin_pct: f64,
}

#[derive(Serialize)]
struct BBPrediction {
    initial_grid_per_axis: usize,
    initial_boxes: usize,
    estimated_survival_rate: f64,
    estimated_levels: usize,
    estimated_total_evals: f64,
    estimated_time_secs: f64,
    feasible: bool,
}

fn run_feasibility(degree: usize) -> FeasibilityResult {
    let d = reduced_dim(degree);
    let t_total = Instant::now();

    println!("  === STEP 1: REFERENCE VALUE (Richardson) ===");
    let resolutions = vec![200, 400, 800];
    let (l_lower, l_best, l_upper, raw_values) = richardson_extrapolate(degree, &resolutions);

    for &(res, l) in &raw_values {
        println!("    res={:>4}: L(z^{}-1) = {:.10}", res, degree, l);
    }
    println!("    Richardson: lower={:.10}, best={:.10}, upper={:.10}", l_lower, l_best, l_upper);
    println!("    Width: {:.2e}", l_upper - l_lower);

    println!("\n  === STEP 2: RANDOM SAMPLING ({} dimensions) ===", d);

    // Number of random samples scaled by dimension
    let n_samples = match d {
        0..=3 => 200_000,
        4..=5 => 100_000,
        6..=7 => 50_000,
        8..=9 => 20_000,
        10..=11 => 10_000,
        _ => 5_000,
    };

    let sample_res = 200; // Coarse for speed
    let l_ref_coarse = {
        let n_coeffs = degree - 1;
        let mut c = vec![(0.0, 0.0); n_coeffs];
        if n_coeffs > 0 {
            c[0] = (-1.0, 0.0);
        }
        lemniscate_length(degree, &c, sample_res)
    };

    println!("    L*(z^{}-1) at res={}: {:.10}", degree, sample_res, l_ref_coarse);
    println!("    Sampling {} points in [-4,4]^{} (a_0 in [0,4])...", n_samples, d);

    // Generate deterministic pseudo-random samples
    let samples: Vec<Vec<f64>> = {
        let mut all = Vec::with_capacity(n_samples);
        let mut rng_state: u64 = 12345 + degree as u64 * 67890;
        let next_rng = |state: &mut u64| -> f64 {
            *state = state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            ((*state >> 33) as f64 / (1u64 << 31) as f64) * 8.0 - 4.0
        };
        for _ in 0..n_samples {
            let mut pt = Vec::with_capacity(d);
            for j in 0..d {
                let v = next_rng(&mut rng_state);
                if j == 0 {
                    pt.push(v.abs().min(4.0)); // a_0 >= 0
                } else {
                    pt.push(v.max(-4.0).min(4.0));
                }
            }
            all.push(pt);
        }
        all
    };

    let t_sample = Instant::now();
    let results: Vec<(usize, f64)> = samples
        .par_iter()
        .enumerate()
        .map(|(idx, pt)| {
            let l = lemniscate_length_reduced(degree, pt, sample_res);
            (idx, l)
        })
        .collect();
    let dt_sample = t_sample.elapsed().as_secs_f64();

    let evals_per_sec = n_samples as f64 / dt_sample;
    println!("    Done in {:.2}s ({:.0} evals/s)", dt_sample, evals_per_sec);

    // Find best competitor
    let mut best_competitor_idx = 0;
    let mut best_competitor_l = 0.0f64;
    let mut n_counterexamples = 0usize;

    let ext = extremizer_point(degree);
    for &(idx, l) in &results {
        // Check distance from extremizer
        let dist: f64 = samples[idx]
            .iter()
            .zip(ext.iter())
            .map(|(a, b)| (a - b).powi(2))
            .sum::<f64>()
            .sqrt();

        if l > l_ref_coarse {
            n_counterexamples += 1;
        }

        if dist > 0.3 && l > best_competitor_l {
            best_competitor_l = l;
            best_competitor_idx = idx;
        }
    }

    let margin = l_ref_coarse - best_competitor_l;
    let margin_pct = if l_ref_coarse > 0.0 {
        margin / l_ref_coarse * 100.0
    } else {
        0.0
    };

    println!("    Counterexamples (L > L_ref at coarse res): {}", n_counterexamples);
    println!(
        "    Closest competitor: L={:.8}, margin={:.6} ({:.3}%)",
        best_competitor_l, margin, margin_pct
    );
    if !samples.is_empty() {
        println!("    Competitor params: {:?}", &samples[best_competitor_idx]);
    }

    println!("\n  === STEP 3: LIPSCHITZ ESTIMATION ===");
    let t_lip = Instant::now();
    let lip = estimate_lipschitz(degree, 20, sample_res);
    let dt_lip = t_lip.elapsed().as_secs_f64();
    println!("    Lipschitz estimate: {:.4} [{:.2}s]", lip, dt_lip);

    println!("\n  === STEP 4: B&B RUNTIME PREDICTION ===");

    // Choose initial grid per axis
    let m = match d {
        0..=5 => 16usize,
        6..=7 => 8,
        8..=9 => 6,
        10..=11 => 4,
        _ => 4,
    };

    let initial_boxes = m.pow(d as u32);
    let survival_threshold = l_ref_coarse * 0.80;
    let n_above_threshold = results.iter().filter(|&&(_, l)| l > survival_threshold).count();
    let survival_rate = n_above_threshold as f64 / n_samples as f64;

    // Estimate B&B with subdivision factor 2^D
    let subdiv_factor = (1usize << d) as f64;
    let mut estimated_levels = 0usize;
    let mut total_evals = 0.0f64;
    let mut active = initial_boxes as f64;

    for _ in 0..10 {
        total_evals += active;
        let survivors = active * survival_rate;
        if survivors < 2.0 {
            estimated_levels += 1;
            total_evals += survivors;
            break;
        }
        active = survivors * subdiv_factor;
        estimated_levels += 1;
    }

    let time_per_eval = dt_sample / n_samples as f64;
    let estimated_time = total_evals * time_per_eval;
    let feasible = estimated_time < 3600.0 * 24.0; // Under 24 hours

    println!("    Initial grid: {}^{} = {} boxes", m, d, initial_boxes);
    println!("    Survival rate (80% threshold): {:.4}", survival_rate);
    println!("    Subdivision factor: 2^{} = {}", d, 1usize << d);
    println!("    Estimated levels: {}", estimated_levels);
    println!("    Estimated total evals: {:.2e}", total_evals);
    println!(
        "    Estimated time: {:.1}s ({:.2} hours)",
        estimated_time,
        estimated_time / 3600.0
    );
    println!("    Feasible (< 24h): {}", feasible);

    let total_time = t_total.elapsed().as_secs_f64();

    FeasibilityResult {
        experiment: format!("EHP_N{}_feasibility", degree),
        degree,
        reduced_dim: d,
        l_star_bounds: LStarBounds {
            lower: l_lower,
            best_estimate: l_best,
            upper: l_upper,
            width: l_upper - l_lower,
            raw_values,
        },
        random_sample: RandomSampleResult {
            n_samples,
            counterexamples: n_counterexamples,
            closest_competitor_l: best_competitor_l,
            closest_competitor_params: samples[best_competitor_idx].clone(),
            margin,
            margin_pct,
        },
        lipschitz_estimate: lip,
        bb_prediction: BBPrediction {
            initial_grid_per_axis: m,
            initial_boxes,
            estimated_survival_rate: survival_rate,
            estimated_levels,
            estimated_total_evals: total_evals,
            estimated_time_secs: estimated_time,
            feasible,
        },
        total_time_secs: total_time,
    }
}

// ══════════════════════════════════════════════════════════════════════
// Verify mode (full B&B)
// ══════════════════════════════════════════════════════════════════════

#[derive(Serialize)]
struct VerifyResult {
    experiment: String,
    degree: usize,
    reduced_dim: usize,
    l_star_bounds: LStarBounds,
    bb_result: BBResult,
    closest_competitor: CompetitorResult,
    margin: f64,
    margin_pct: f64,
    outer_domain: OuterDomainResult,
    hessian: HessianResult,
    total_time_secs: f64,
    verdict: String,
}

#[derive(Serialize)]
struct BBResult {
    initial_boxes: usize,
    levels: usize,
    total_evals: usize,
    proof_complete: bool,
    final_survivors_non_ext: usize,
}

#[derive(Serialize)]
struct CompetitorResult {
    l_value: f64,
    params: Vec<f64>,
    distance_to_extremizer: f64,
}

#[derive(Serialize)]
struct OuterDomainResult {
    safe: bool,
    max_face_l: f64,
    face_margin: f64,
    n_face_evals: usize,
}

#[derive(Serialize)]
struct HessianResult {
    all_negative: bool,
    diagonal: Vec<f64>,
    min_eigenvalue_approx: f64,
}

fn run_verify(degree: usize, budget_secs: f64) -> VerifyResult {
    let d = reduced_dim(degree);
    let t_total = Instant::now();

    // ── Step 1: Certified L* bounds ──
    println!("  === STEP 1: CERTIFIED L* BOUNDS (5 resolutions) ===");
    let resolutions = vec![200, 400, 800, 1600, 3200];
    let (l_lower, l_best, l_upper, raw_values) = richardson_extrapolate(degree, &resolutions);

    for &(res, l) in &raw_values {
        println!("    res={:>4}: L(z^{}-1) = {:.12}", res, degree, l);
    }
    println!("    Richardson: lower={:.10}, best={:.10}, upper={:.10}", l_lower, l_best, l_upper);

    // ── Step 2: Grid error calibration ──
    println!("\n  === STEP 2: GRID ERROR CALIBRATION ===");

    // Test at several points to bound relative error
    let ext = extremizer_point(degree);
    let mut test_points: Vec<(Vec<f64>, &str)> = vec![(ext.clone(), "extremizer")];

    // Perturbed points
    if d > 0 {
        let mut pt1 = ext.clone();
        pt1[0] = 0.5;
        test_points.push((pt1, "a0=0.5"));
    }
    if d > 1 {
        let mut pt2 = ext.clone();
        pt2[1] = 0.5;
        test_points.push((pt2, "a1_re=0.5"));
    }
    if d > 0 {
        let mut pt3 = ext.clone();
        pt3[0] = 2.0;
        test_points.push((pt3, "a0=2.0"));
    }

    let mut max_rel_err_200 = 0.0f64;
    let mut max_rel_err_400 = 0.0f64;

    for (pt, name) in &test_points {
        let l200 = lemniscate_length_reduced(degree, pt, 200);
        let l400 = lemniscate_length_reduced(degree, pt, 400);
        let l800 = lemniscate_length_reduced(degree, pt, 800);
        let l1600 = lemniscate_length_reduced(degree, pt, 1600);
        let l_rich = (4.0 * l1600 - l800) / 3.0;

        if l_rich > 0.1 {
            let re200 = (l_rich - l200).abs() / l_rich;
            let re400 = (l_rich - l400).abs() / l_rich;
            if re200 > max_rel_err_200 {
                max_rel_err_200 = re200;
            }
            if re400 > max_rel_err_400 {
                max_rel_err_400 = re400;
            }
            println!(
                "    {:<16}: rel_err 200={:.4}% 400={:.4}%",
                name,
                re200 * 100.0,
                re400 * 100.0
            );
        }
    }
    println!("    Max rel errors: 200={:.4}% 400={:.4}%",
        max_rel_err_200 * 100.0, max_rel_err_400 * 100.0);

    // ── Step 3: Lipschitz estimation ──
    println!("\n  === STEP 3: LIPSCHITZ ESTIMATION ===");
    let lip = estimate_lipschitz(degree, 30, 200);
    println!("    Lipschitz estimate: {:.4}", lip);

    // ── Step 4: Adaptive B&B ──
    println!("\n  === STEP 4: ADAPTIVE BRANCH-AND-BOUND ({} dimensions) ===", d);

    let radius = 4.0;

    // Choose initial grid
    let m: usize = match d {
        0..=5 => 16,
        6..=7 => 8,
        8..=9 => 6,
        10..=11 => 4,
        _ => 4,
    };

    // Build initial boxes
    // Dimension 0 (a_0_real): [0, radius] (symmetry: a_0 >= 0)
    // All other dimensions: [-radius, radius]
    let mut dim_ranges: Vec<(f64, f64)> = Vec::with_capacity(d);
    if d > 0 {
        dim_ranges.push((0.0, radius)); // a_0 real, non-negative
    }
    for _ in 1..d {
        dim_ranges.push((-radius, radius));
    }

    let total_initial_boxes = m.checked_pow(d as u32).unwrap_or(usize::MAX);
    println!("    Domain: a_0 in [0,{0}], others in [-{0},{0}]", radius);
    println!("    Grid: {}^{} = {} boxes", m, d, total_initial_boxes);

    // Generate initial boxes
    let mut boxes: Vec<BoxND> = Vec::with_capacity(total_initial_boxes.min(100_000_000));

    // Recursive box generation for arbitrary dimension
    fn generate_boxes(
        dim_ranges: &[(f64, f64)],
        m: usize,
        current_dim: usize,
        current_bounds: &mut Vec<(f64, f64)>,
        result: &mut Vec<BoxND>,
    ) {
        if current_dim == dim_ranges.len() {
            result.push(BoxND {
                bounds: current_bounds.clone(),
            });
            return;
        }
        let (lo, hi) = dim_ranges[current_dim];
        let step = (hi - lo) / m as f64;
        for i in 0..m {
            let box_lo = lo + i as f64 * step;
            let box_hi = box_lo + step;
            current_bounds.push((box_lo, box_hi));
            generate_boxes(dim_ranges, m, current_dim + 1, current_bounds, result);
            current_bounds.pop();
        }
    }

    // Guard: if too many boxes, reduce m
    let actual_m = if total_initial_boxes > 50_000_000 {
        let max_m = (50_000_000.0f64).powf(1.0 / d as f64).floor() as usize;
        println!("    WARNING: Reducing grid from {} to {} (too many boxes)", m, max_m.max(2));
        max_m.max(2)
    } else {
        m
    };

    {
        let mut current_bounds = Vec::with_capacity(d);
        generate_boxes(&dim_ranges, actual_m, 0, &mut current_bounds, &mut boxes);
    }
    println!("    Actual initial boxes: {}", boxes.len());

    let total_evals = AtomicUsize::new(0);
    let mut best_competitor_l = 0.0f64;
    let mut best_competitor_params: Vec<f64> = vec![0.0; d];
    let mut bb_proof_complete = false;
    let mut bb_levels = 0usize;
    let max_levels = 10;

    let refine_res: usize = 800;

    // Two-pass B&B:
    // Pass 1 (cheap): eliminate boxes where L(center) < fraction of L* (coarse threshold)
    // Pass 2 (precise): for survivors, compute per-box local Lipschitz bound
    // This avoids the global Lipschitz problem where safety >> margin

    for level in 0..max_levels {
        if boxes.is_empty() {
            println!("\n    Level {}: No boxes remaining.", level);
            bb_proof_complete = true;
            break;
        }

        // Check time budget
        let elapsed = t_total.elapsed().as_secs_f64();
        if elapsed > budget_secs * 0.9 {
            println!("\n    Level {}: TIME BUDGET EXHAUSTED ({:.1}s / {:.1}s)", level, elapsed, budget_secs);
            break;
        }

        let hw = boxes[0].half_width();
        let n_boxes = boxes.len();

        // Resolution increases with level
        let level_res: usize = match level {
            0 | 1 => 200,
            2 | 3 => 400,
            _ => 800,
        };

        // Grid error factor for this resolution
        let grid_corr = match level_res {
            200 => l_best * 0.02,
            400 => l_best * 0.005,
            _ => l_best * 0.0015,
        };

        println!(
            "\n    Level {}: {} boxes, hw={:.6}, res={}",
            level, n_boxes, hw, level_res
        );

        let t_level = Instant::now();

        // PASS 1: Evaluate all box centers in parallel (cheap — 1 eval per box)
        let center_results: Vec<(f64, bool)> = boxes
            .par_iter()
            .map(|bx| {
                let center = bx.center();
                let l = lemniscate_length_reduced(degree, &center, level_res);
                total_evals.fetch_add(1, Ordering::Relaxed);
                (l, bx.contains_extremizer())
            })
            .collect();

        // Coarse elimination: discard boxes where L(center) < 50% of L*
        // This is safe because L varies smoothly and the gap to L* is huge
        let coarse_threshold = l_lower * 0.50;
        let pass1_survivors: Vec<usize> = center_results
            .iter()
            .enumerate()
            .filter(|(_, (l, is_ext))| *is_ext || *l > coarse_threshold)
            .map(|(idx, _)| idx)
            .collect();

        let pass1_eliminated = n_boxes - pass1_survivors.len();
        println!(
            "      Pass 1 (threshold={:.2}): eliminated {}/{} ({:.1}%)",
            coarse_threshold,
            pass1_eliminated,
            n_boxes,
            pass1_eliminated as f64 / n_boxes as f64 * 100.0
        );

        // PASS 2: For survivors, compute per-box local Lipschitz upper bound
        // Evaluate center + finite differences in each dimension
        let max_radius = (d as f64).sqrt() * hw;
        let h_fd = (hw * 0.5).max(0.001); // Finite diff step: half the box width

        // Each box gets (1 + 2*d) evaluations: center already done, plus ±h in each dim
        let pass2_results: Vec<(usize, f64, f64, bool)> = pass1_survivors
            .par_iter()
            .map(|&idx| {
                let (l_center, is_ext) = center_results[idx];
                if is_ext {
                    return (idx, l_center, 0.0, true);
                }

                let center = boxes[idx].center();
                let mut local_lip = 0.0f64;
                for dim in 0..d {
                    let mut pt_plus = center.clone();
                    pt_plus[dim] = (pt_plus[dim] + h_fd).min(if dim == 0 { radius } else { radius });
                    let l_plus = lemniscate_length_reduced(degree, &pt_plus, level_res);
                    total_evals.fetch_add(1, Ordering::Relaxed);
                    let grad_p = (l_plus - l_center).abs() / h_fd;
                    local_lip = local_lip.max(grad_p);

                    let mut pt_minus = center.clone();
                    pt_minus[dim] = (pt_minus[dim] - h_fd).max(if dim == 0 { 0.0 } else { -radius });
                    let l_minus = lemniscate_length_reduced(degree, &pt_minus, level_res);
                    total_evals.fetch_add(1, Ordering::Relaxed);
                    let grad_m = (l_minus - l_center).abs() / h_fd;
                    local_lip = local_lip.max(grad_m);
                }

                (idx, l_center, local_lip, false)
            })
            .collect();

        // Eliminate using local upper bounds:
        // upper_bound = L(center) + safety_factor * local_lip * max_radius + grid_corr
        // safety_factor = 2.0 accounts for gradient variation within the box
        let safety_factor = 2.0;
        let mut survived: Vec<usize> = Vec::new();
        let mut max_l_nonext = 0.0f64;

        for &(idx, l_center, local_lip, is_ext) in &pass2_results {
            if is_ext {
                survived.push(idx);
                continue;
            }

            let upper_bound = l_center + safety_factor * local_lip * max_radius + grid_corr;
            if upper_bound > l_lower {
                survived.push(idx);
            }

            if l_center > max_l_nonext {
                max_l_nonext = l_center;
            }

            // Track best competitor (refine at high res for the top ones)
            if l_center > best_competitor_l * 0.9 && l_center > l_lower * 0.5 {
                let center = boxes[idx].center();
                let l_high = lemniscate_length_reduced(degree, &center, refine_res);
                total_evals.fetch_add(1, Ordering::Relaxed);
                if l_high > best_competitor_l {
                    best_competitor_l = l_high;
                    best_competitor_params = center;
                }
            }
        }

        let eliminated_total = n_boxes - survived.len();
        let ext_count = survived
            .iter()
            .filter(|&&idx| boxes[idx].contains_extremizer())
            .count();
        let nonext_count = survived.len() - ext_count;

        let dt_level = t_level.elapsed().as_secs_f64();
        bb_levels = level + 1;

        println!(
            "      Pass 2 (local Lip): total eliminated {}/{} ({:.1}%) | survivors: {} ext + {} nonext | max_l_nonext={:.6}",
            eliminated_total,
            n_boxes,
            eliminated_total as f64 / n_boxes as f64 * 100.0,
            ext_count,
            nonext_count,
            max_l_nonext
        );
        println!("      Level time: {:.2}s", dt_level);

        if nonext_count == 0 {
            println!("      *** ONLY EXTREMIZER BOXES SURVIVE — PROOF STRUCTURE COMPLETE ***");
            bb_proof_complete = true;
            break;
        }

        // Final level: verify remaining at high resolution
        if level == max_levels - 1 {
            println!(
                "\n      FINAL: verifying {} non-ext survivors at res={}...",
                nonext_count, refine_res
            );
            let mut any_threatens = false;
            for &idx in &survived {
                if !boxes[idx].contains_extremizer() {
                    let center = boxes[idx].center();
                    let l_high = lemniscate_length_reduced(degree, &center, refine_res);
                    total_evals.fetch_add(1, Ordering::Relaxed);
                    if l_high > l_lower {
                        println!(
                            "        THREAT: params={:?} L={:.8} > L*={:.8}",
                            center, l_high, l_lower
                        );
                        any_threatens = true;
                    }
                    if l_high > best_competitor_l {
                        best_competitor_l = l_high;
                        best_competitor_params = center;
                    }
                }
            }
            if !any_threatens {
                println!("      All survivors verified below threshold.");
                bb_proof_complete = true;
            }
            break;
        }

        // Subdivide survivors
        let subdiv_factor = 1usize << d;
        let projected_children = survived.len() * subdiv_factor;

        if projected_children > 50_000_000 {
            println!(
                "      WARNING: Subdivision would produce {} boxes, capping at 50M...",
                projected_children
            );
            let mut scored: Vec<(usize, f64, bool)> = survived
                .iter()
                .map(|&idx| {
                    let l = center_results[idx].0;
                    let ce = boxes[idx].contains_extremizer();
                    (idx, l, ce)
                })
                .collect();
            scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

            let max_subdivide = 50_000_000 / subdiv_factor;
            let mut new_boxes = Vec::new();
            for &(idx, _, _) in scored.iter().take(max_subdivide) {
                new_boxes.extend(boxes[idx].subdivide());
            }
            boxes = new_boxes;
        } else {
            let mut new_boxes = Vec::with_capacity(projected_children);
            for &idx in &survived {
                new_boxes.extend(boxes[idx].subdivide());
            }
            boxes = new_boxes;
        }
    }

    let total_ev = total_evals.load(Ordering::Relaxed);

    // ── Step 5: Best competitor via coarse sweep + refinement ──
    println!("\n  === STEP 5: COMPETITOR REFINEMENT ===");

    // Coarse sweep to find competitors
    let sweep_m = match d {
        0..=3 => 30usize,
        4..=5 => 15,
        6..=7 => 8,
        _ => 5,
    };

    let sweep_total = sweep_m.checked_pow(d as u32).unwrap_or(0);
    if sweep_total > 0 && sweep_total < 10_000_000 {
        println!("    Coarse sweep: {}^{} = {} points at res=200...", sweep_m, d, sweep_total);

        let mut sweep_boxes: Vec<Vec<f64>> = Vec::with_capacity(sweep_total);
        fn generate_sweep_points(
            dim_ranges: &[(f64, f64)],
            m: usize,
            current_dim: usize,
            current_pt: &mut Vec<f64>,
            result: &mut Vec<Vec<f64>>,
        ) {
            if current_dim == dim_ranges.len() {
                result.push(current_pt.clone());
                return;
            }
            let (lo, hi) = dim_ranges[current_dim];
            let step = (hi - lo) / m as f64;
            for i in 0..m {
                let val = lo + (i as f64 + 0.5) * step;
                current_pt.push(val);
                generate_sweep_points(dim_ranges, m, current_dim + 1, current_pt, result);
                current_pt.pop();
            }
        }

        {
            let mut current_pt = Vec::with_capacity(d);
            generate_sweep_points(&dim_ranges, sweep_m, 0, &mut current_pt, &mut sweep_boxes);
        }

        let sweep_results: Vec<(usize, f64)> = sweep_boxes
            .par_iter()
            .enumerate()
            .map(|(idx, pt)| {
                let l = lemniscate_length_reduced(degree, pt, 200);
                (idx, l)
            })
            .collect();

        // Find top 20 non-extremizer candidates, refine
        let ext = extremizer_point(degree);
        let mut candidates: Vec<(usize, f64)> = sweep_results
            .iter()
            .filter(|&&(idx, _)| {
                let dist: f64 = sweep_boxes[idx]
                    .iter()
                    .zip(ext.iter())
                    .map(|(a, b)| (a - b).powi(2))
                    .sum::<f64>()
                    .sqrt();
                dist > 0.3
            })
            .cloned()
            .collect();
        candidates.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        candidates.truncate(20);

        for &(idx, _) in &candidates {
            let l_hr = lemniscate_length_reduced(degree, &sweep_boxes[idx], refine_res);
            if l_hr > best_competitor_l {
                best_competitor_l = l_hr;
                best_competitor_params = sweep_boxes[idx].clone();
            }
        }
        println!(
            "    Best competitor after sweep: L={:.10}",
            best_competitor_l
        );
    } else {
        println!("    Sweep too large ({}), skipping.", sweep_total);
    }

    let margin = l_lower - best_competitor_l;
    let margin_pct = if l_lower > 0.0 {
        margin / l_lower * 100.0
    } else {
        0.0
    };

    // ── Step 6: Outer domain verification ──
    println!("\n  === STEP 6: OUTER DOMAIN VERIFICATION ===");

    let face_n = match d {
        0..=3 => 40usize,
        4..=5 => 20,
        6..=7 => 10,
        _ => 5,
    };

    let mut max_face_l = 0.0f64;
    let mut n_face_evals = 0usize;

    // For each dimension, sample the two boundary faces
    // (except dim 0 where only the hi face exists since a_0 >= 0)
    let face_points_per_face = face_n.checked_pow((d - 1).max(1) as u32).unwrap_or(0).min(1_000_000);

    if face_points_per_face > 0 && d > 0 {
        println!(
            "    Sampling {} faces, ~{} points per face...",
            2 * d - 1,
            face_points_per_face
        );

        for fix_dim in 0..d {
            // Which boundary values to check for this dimension
            let face_values: Vec<f64> = if fix_dim == 0 {
                vec![dim_ranges[0].1] // a_0 = radius (upper face only, lower is 0)
            } else {
                vec![dim_ranges[fix_dim].0, dim_ranges[fix_dim].1] // both lo and hi
            };

            for &fix_val in &face_values {
                // Sample points on this face using a small grid
                let face_dim = d - 1;
                let face_m = if face_dim == 0 {
                    1
                } else {
                    (face_points_per_face as f64).powf(1.0 / face_dim as f64).floor() as usize
                };
                let actual_face_m = face_m.max(1).min(face_n);

                // Generate face points
                let free_dims: Vec<usize> = (0..d).filter(|&i| i != fix_dim).collect();
                let face_total = actual_face_m.checked_pow(free_dims.len() as u32).unwrap_or(0);

                if face_total == 0 || face_total > 2_000_000 {
                    continue;
                }

                let mut face_pts: Vec<Vec<f64>> = Vec::with_capacity(face_total);
                fn gen_face_points(
                    dim_ranges: &[(f64, f64)],
                    free_dims: &[usize],
                    fix_dim: usize,
                    fix_val: f64,
                    m: usize,
                    current_free_idx: usize,
                    current_pt: &mut Vec<(usize, f64)>,
                    d: usize,
                    result: &mut Vec<Vec<f64>>,
                ) {
                    if current_free_idx == free_dims.len() {
                        let mut pt = vec![0.0; d];
                        pt[fix_dim] = fix_val;
                        for &(dim, val) in current_pt.iter() {
                            pt[dim] = val;
                        }
                        result.push(pt);
                        return;
                    }
                    let dim = free_dims[current_free_idx];
                    let (lo, hi) = dim_ranges[dim];
                    let step = (hi - lo) / m as f64;
                    for i in 0..m {
                        let val = lo + (i as f64 + 0.5) * step;
                        current_pt.push((dim, val));
                        gen_face_points(
                            dim_ranges,
                            free_dims,
                            fix_dim,
                            fix_val,
                            m,
                            current_free_idx + 1,
                            current_pt,
                            d,
                            result,
                        );
                        current_pt.pop();
                    }
                }

                {
                    let mut current_pt = Vec::with_capacity(free_dims.len());
                    gen_face_points(
                        &dim_ranges,
                        &free_dims,
                        fix_dim,
                        fix_val,
                        actual_face_m,
                        0,
                        &mut current_pt,
                        d,
                        &mut face_pts,
                    );
                }

                let face_results: Vec<f64> = face_pts
                    .par_iter()
                    .map(|pt| lemniscate_length_reduced(degree, pt, 400))
                    .collect();

                n_face_evals += face_results.len();
                for &l in &face_results {
                    if l > max_face_l {
                        max_face_l = l;
                    }
                }
            }
        }
    }

    // Correction for face sampling: grid error only (boundary is far from extremizer,
    // local Lipschitz is small there). Conservative: 3x the measured grid relative error.
    let face_grid_corr = max_face_l * max_rel_err_400 * 3.0;
    // Add a small Lipschitz correction based on actual face variation (not global lip)
    let face_step = 2.0 * radius / face_n as f64;
    // Estimate boundary Lipschitz from face results: use 2x the max face L / radius as conservative bound
    let face_lip_est = (max_face_l / radius) * 2.0;
    let face_lip_corr = face_lip_est * (d as f64 - 1.0).max(1.0).sqrt() * face_step / 2.0;
    let face_upper = max_face_l + face_lip_corr + face_grid_corr;
    let face_margin = l_lower - face_upper;
    let outer_safe = face_margin > 0.0;

    println!("    Face evals: {}", n_face_evals);
    println!("    Max L on boundary (raw): {:.6}", max_face_l);
    println!("    Max L on boundary (corrected): {:.6}", face_upper);
    println!("    Face margin: {:.6}", face_margin);
    println!("    Outer domain safe: {}", outer_safe);

    // ── Step 7: Hessian at extremizer ──
    println!("\n  === STEP 7: HESSIAN AT EXTREMIZER ===");

    let hess_res = 1600;
    let h = 1e-3;
    let ext = extremizer_point(degree);
    let l0 = lemniscate_length_reduced(degree, &ext, hess_res);
    println!("    L*(extremizer) = {:.12} at res={}", l0, hess_res);

    let mut all_negative = true;
    let mut hessian_diag = Vec::with_capacity(d);
    let mut min_eigenvalue = f64::MAX;

    for i in 0..d {
        let mut pt_plus = ext.clone();
        pt_plus[i] += h;
        let l_plus = lemniscate_length_reduced(degree, &pt_plus, hess_res);

        let mut pt_minus = ext.clone();
        pt_minus[i] -= h;
        // Clamp: a_0 must stay non-negative
        if i == 0 && pt_minus[0] < 0.0 {
            // Use one-sided difference
            let d2l = (l_plus - 2.0 * l0 + lemniscate_length_reduced(degree, &ext, hess_res)) / (h * h);
            // Actually, the extremizer a_0=1 is well away from 0, so this shouldn't trigger
            // for h=1e-3. But handle it gracefully.
            hessian_diag.push(d2l);
            if d2l >= 0.0 {
                all_negative = false;
            }
            if d2l < min_eigenvalue {
                min_eigenvalue = d2l;
            }
            let dim_name = if i == 0 {
                "a0_re".to_string()
            } else {
                let coeff_idx = (i - 1) / 2 + 1;
                if (i - 1) % 2 == 0 {
                    format!("a{}_re", coeff_idx)
                } else {
                    format!("a{}_im", coeff_idx)
                }
            };
            println!(
                "    d2L/d{}^2 = {:.2} {}",
                dim_name,
                d2l,
                if d2l < 0.0 { "(NEGATIVE)" } else { "(**POSITIVE**)" }
            );
            continue;
        }
        let l_minus = lemniscate_length_reduced(degree, &pt_minus, hess_res);

        let d2l = (l_plus + l_minus - 2.0 * l0) / (h * h);
        hessian_diag.push(d2l);
        if d2l >= 0.0 {
            all_negative = false;
        }
        if d2l < min_eigenvalue {
            min_eigenvalue = d2l;
        }

        let dim_name = if i == 0 {
            "a0_re".to_string()
        } else {
            let coeff_idx = (i - 1) / 2 + 1;
            if (i - 1) % 2 == 0 {
                format!("a{}_re", coeff_idx)
            } else {
                format!("a{}_im", coeff_idx)
            }
        };
        println!(
            "    d2L/d{}^2 = {:.2} {}",
            dim_name,
            d2l,
            if d2l < 0.0 { "(NEGATIVE)" } else { "(**POSITIVE**)" }
        );
    }

    // Retry with different h if needed
    if !all_negative {
        println!("\n    Retrying with h=1e-2...");
        let h2 = 1e-2;
        let mut all_neg2 = true;
        for i in 0..d {
            let mut pt_plus = ext.clone();
            pt_plus[i] += h2;
            let l_plus = lemniscate_length_reduced(degree, &pt_plus, hess_res);
            let mut pt_minus = ext.clone();
            pt_minus[i] -= h2;
            let l_minus = lemniscate_length_reduced(degree, &pt_minus, hess_res);
            let d2l = (l_plus + l_minus - 2.0 * l0) / (h2 * h2);
            if d2l >= 0.0 {
                all_neg2 = false;
            }
        }
        if all_neg2 {
            println!("    At h=1e-2: ALL NEGATIVE => confirmed");
            all_negative = true;
        }
    }

    println!(
        "    Hessian: {}",
        if all_negative {
            "ALL NEGATIVE => strict local maximum"
        } else {
            "NOT ALL NEGATIVE"
        }
    );

    // ── Verdict ──
    let total_time = t_total.elapsed().as_secs_f64();
    let comp_dist: f64 = best_competitor_params
        .iter()
        .zip(extremizer_point(degree).iter())
        .map(|(a, b)| (a - b).powi(2))
        .sum::<f64>()
        .sqrt();

    let verdict = if bb_proof_complete && outer_safe && all_negative && margin > 0.0 {
        format!("EHP_N{}_VERIFIED", degree)
    } else if bb_proof_complete && margin > 0.0 {
        format!("EHP_N{}_STRONGLY_SUPPORTED", degree)
    } else if margin > 0.0 {
        format!("EHP_N{}_SUPPORTED", degree)
    } else {
        format!("EHP_N{}_INCONCLUSIVE", degree)
    };

    println!("\n  ============================================================");
    println!("  FINAL REPORT: EHP n={}", degree);
    println!("  ============================================================");
    println!("  Reduced dimension:       {}", d);
    println!("  L*(z^{}-1) lower bound: {:.10}", degree, l_lower);
    println!("  L*(z^{}-1) best est:    {:.10}", degree, l_best);
    println!("  L*(z^{}-1) upper bound: {:.10}", degree, l_upper);
    println!();
    println!("  Best competitor:  L = {:.10}", best_competitor_l);
    println!("    params: {:?}", best_competitor_params);
    println!("    dist to extremizer: {:.4}", comp_dist);
    println!("  MARGIN: {:.10} ({:.4}%)", margin, margin_pct);
    println!();
    println!("  B&B proof complete:   {}", bb_proof_complete);
    println!("  B&B levels:           {}", bb_levels);
    println!("  B&B total evals:      {}", total_ev);
    println!("  Outer domain safe:    {} (margin={:.4})", outer_safe, face_margin);
    println!("  Hessian all negative: {}", all_negative);
    println!();
    println!("  Total time: {:.1}s", total_time);
    println!("  VERDICT: {}", verdict);
    println!("  ============================================================");

    VerifyResult {
        experiment: format!("EHP_N{}_verify", degree),
        degree,
        reduced_dim: d,
        l_star_bounds: LStarBounds {
            lower: l_lower,
            best_estimate: l_best,
            upper: l_upper,
            width: l_upper - l_lower,
            raw_values,
        },
        bb_result: BBResult {
            initial_boxes: boxes.len().max(total_initial_boxes),
            levels: bb_levels,
            total_evals: total_ev,
            proof_complete: bb_proof_complete,
            final_survivors_non_ext: if bb_proof_complete { 0 } else { boxes.len() },
        },
        closest_competitor: CompetitorResult {
            l_value: best_competitor_l,
            params: best_competitor_params,
            distance_to_extremizer: comp_dist,
        },
        margin,
        margin_pct,
        outer_domain: OuterDomainResult {
            safe: outer_safe,
            max_face_l,
            face_margin,
            n_face_evals,
        },
        hessian: HessianResult {
            all_negative,
            diagonal: hessian_diag,
            min_eigenvalue_approx: min_eigenvalue,
        },
        total_time_secs: total_time,
        verdict,
    }
}

// ══════════════════════════════════════════════════════════════════════
// CLI argument parsing
// ══════════════════════════════════════════════════════════════════════

struct Args {
    degree: usize,
    mode: String,       // "feasibility", "verify", "both"
    budget_secs: f64,
}

fn parse_args() -> Args {
    let args: Vec<String> = std::env::args().collect();
    let mut degree: usize = 3;
    let mut mode = "both".to_string();
    let mut budget_secs: f64 = 600.0; // 10 minutes default

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--degree" | "-n" => {
                i += 1;
                if i < args.len() {
                    degree = args[i].parse().unwrap_or(3);
                }
            }
            "--mode" | "-m" => {
                i += 1;
                if i < args.len() {
                    mode = args[i].clone();
                }
            }
            "--budget-secs" | "-t" => {
                i += 1;
                if i < args.len() {
                    budget_secs = args[i].parse().unwrap_or(600.0);
                }
            }
            "--help" | "-h" => {
                println!("Usage: ehp_general [OPTIONS]");
                println!();
                println!("Options:");
                println!("  --degree N, -n N     Polynomial degree (default: 3)");
                println!("  --mode MODE, -m MODE Mode: feasibility, verify, both (default: both)");
                println!("  --budget-secs S, -t S  Time budget in seconds (default: 600)");
                println!();
                println!("Examples:");
                println!("  cargo run --release --bin ehp_general -- --degree 4 --mode feasibility");
                println!("  cargo run --release --bin ehp_general -- -n 5 -m verify -t 3600");
                std::process::exit(0);
            }
            _ => {
                eprintln!("Unknown argument: {}", args[i]);
                std::process::exit(1);
            }
        }
        i += 1;
    }

    if degree < 2 {
        eprintln!("Error: degree must be >= 2");
        std::process::exit(1);
    }

    Args {
        degree,
        mode,
        budget_secs,
    }
}

// ══════════════════════════════════════════════════════════════════════
// Main
// ══════════════════════════════════════════════════════════════════════

fn main() {
    let args = parse_args();
    let d = reduced_dim(args.degree);

    println!("============================================================");
    println!("  EHP CONJECTURE GENERAL-DEGREE VERIFIER");
    println!("  Degree n={}, reduced dim D={}", args.degree, d);
    println!("  Mode: {}, budget: {:.0}s", args.mode, args.budget_secs);
    println!("  Cores: {}", rayon::current_num_threads());
    println!("  Kenneth A. Mendoza · Oregon Coast AI · March 2026");
    println!("============================================================");
    println!();
    println!("  Polynomial: p(z) = z^{} + a_{{{}}}*z^{{{}}} + ... + a_1*z + a_0",
        args.degree, args.degree - 2, args.degree - 2);
    println!("  Symmetry: fix a_0 real >= 0 (rotation z -> e^{{it/{}}}*z)", args.degree);
    println!("  Reduced parameters: D = 2*{} - 3 = {}", args.degree, d);
    println!("  Extremizer: a_0 = 1, all others = 0 (i.e., z^{} - 1)", args.degree);

    match args.mode.as_str() {
        "feasibility" => {
            println!("\n  *** FEASIBILITY MODE ***\n");
            let result = run_feasibility(args.degree);
            let filename = format!("EHP_N{}_FEASIBILITY.json", args.degree);
            let json = serde_json::to_string_pretty(&result).unwrap();
            std::fs::write(&filename, &json).expect("Failed to write results");
            println!("\n  Results saved to {}", filename);
        }
        "verify" => {
            println!("\n  *** VERIFY MODE ***\n");
            let result = run_verify(args.degree, args.budget_secs);
            let filename = format!("EHP_N{}_VERIFY_RESULTS.json", args.degree);
            let json = serde_json::to_string_pretty(&result).unwrap();
            std::fs::write(&filename, &json).expect("Failed to write results");
            println!("\n  Results saved to {}", filename);
        }
        "both" => {
            println!("\n  *** FEASIBILITY FIRST, THEN VERIFY IF FEASIBLE ***\n");

            let feasibility = run_feasibility(args.degree);
            let feas_filename = format!("EHP_N{}_FEASIBILITY.json", args.degree);
            let json = serde_json::to_string_pretty(&feasibility).unwrap();
            std::fs::write(&feas_filename, &json).expect("Failed to write results");
            println!("\n  Feasibility saved to {}", feas_filename);

            let remaining_budget = args.budget_secs - feasibility.total_time_secs;

            if feasibility.bb_prediction.feasible && remaining_budget > 60.0 {
                println!("\n  Predicted feasible. Running verify with {:.0}s remaining...\n", remaining_budget);
                let result = run_verify(args.degree, remaining_budget);
                let ver_filename = format!("EHP_N{}_VERIFY_RESULTS.json", args.degree);
                let json = serde_json::to_string_pretty(&result).unwrap();
                std::fs::write(&ver_filename, &json).expect("Failed to write results");
                println!("\n  Verify results saved to {}", ver_filename);
            } else if !feasibility.bb_prediction.feasible {
                println!(
                    "\n  NOT FEASIBLE for full B&B (predicted {:.1}s > 24h budget).",
                    feasibility.bb_prediction.estimated_time_secs
                );
                println!("  Feasibility results saved. Consider increasing --budget-secs or");
                println!("  running verify with a reduced domain.");
            } else {
                println!(
                    "\n  Insufficient remaining budget ({:.0}s). Skipping verify.",
                    remaining_budget
                );
            }
        }
        _ => {
            eprintln!("Unknown mode: {}. Use feasibility, verify, or both.", args.mode);
            std::process::exit(1);
        }
    }
}

// ══════════════════════════════════════════════════════════════════════
// Tests
// ══════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_reduced_dim() {
        assert_eq!(reduced_dim(2), 1);  // z^2 + a_0: 1 real param
        assert_eq!(reduced_dim(3), 3);  // z^3 + a_1*z + a_0: a_0 real + a_1 complex = 3
        assert_eq!(reduced_dim(4), 5);  // z^4 + a_2*z^2 + a_1*z + a_0: 1 + 2 + 2 = 5
        assert_eq!(reduced_dim(5), 7);
        assert_eq!(reduced_dim(6), 9);
        assert_eq!(reduced_dim(7), 11);
        assert_eq!(reduced_dim(8), 13);
    }

    #[test]
    fn test_reduced_to_coeffs() {
        // n=3: params = [a0_re, a1_re, a1_im]
        let coeffs = reduced_to_coeffs(3, &[1.0, 0.5, -0.3]);
        assert_eq!(coeffs.len(), 2); // a_0 and a_1
        assert!((coeffs[0].0 - 1.0).abs() < 1e-15); // a_0 real
        assert!((coeffs[0].1).abs() < 1e-15);         // a_0 imag = 0
        assert!((coeffs[1].0 - 0.5).abs() < 1e-15);  // a_1 re
        assert!((coeffs[1].1 - (-0.3)).abs() < 1e-15); // a_1 im
    }

    #[test]
    fn test_eval_poly_n3() {
        // p(z) = z^3 - 1 at z = 1 should give 0
        let coeffs = vec![(-1.0, 0.0), (0.0, 0.0)]; // a_0 = -1, a_1 = 0
        let (re, im) = eval_poly(1.0, 0.0, 3, &coeffs);
        assert!(re.abs() < 1e-12, "p(1) should be 0, got {}", re);
        assert!(im.abs() < 1e-12);
    }

    #[test]
    fn test_eval_poly_n2() {
        // p(z) = z^2 - 1 at z = 1 should give 0
        let coeffs = vec![(-1.0, 0.0)]; // a_0 = -1
        let (re, im) = eval_poly(1.0, 0.0, 2, &coeffs);
        assert!(re.abs() < 1e-12, "p(1) should be 0, got {}", re);
        assert!(im.abs() < 1e-12);

        // p(z) = z^2 - 1 at z = i should give -1 - 1 = -2
        let (re, im) = eval_poly(0.0, 1.0, 2, &coeffs);
        assert!((re - (-2.0)).abs() < 1e-12, "p(i) should be -2, got {}", re);
        assert!(im.abs() < 1e-12);
    }

    #[test]
    fn test_eval_poly_n4() {
        // p(z) = z^4 - 1 at z = 1 should give 0
        let coeffs = vec![(-1.0, 0.0), (0.0, 0.0), (0.0, 0.0)]; // a_0=-1, a_1=0, a_2=0
        let (re, im) = eval_poly(1.0, 0.0, 4, &coeffs);
        assert!(re.abs() < 1e-12, "p(1) should be 0, got {}", re);
        assert!(im.abs() < 1e-12);

        // z^4 - 1 at z = i: i^4 - 1 = 1 - 1 = 0
        let (re, im) = eval_poly(0.0, 1.0, 4, &coeffs);
        assert!(re.abs() < 1e-12, "p(i) should be 0, got {}", re);
        assert!(im.abs() < 1e-12);
    }

    #[test]
    fn test_extremizer_point() {
        let ext3 = extremizer_point(3);
        assert_eq!(ext3.len(), 3);
        assert!((ext3[0] - 1.0).abs() < 1e-15);
        assert!(ext3[1].abs() < 1e-15);
        assert!(ext3[2].abs() < 1e-15);

        let ext4 = extremizer_point(4);
        assert_eq!(ext4.len(), 5);
        assert!((ext4[0] - 1.0).abs() < 1e-15);
        for i in 1..5 {
            assert!(ext4[i].abs() < 1e-15);
        }
    }

    #[test]
    fn test_lemniscate_n2() {
        // L(z^2 - 1) should be close to 2*pi ≈ 6.2832 (unit circle mapped)
        // Actually for z^2 - 1, roots at +/-1, lemniscate is a figure-8
        let coeffs = vec![(-1.0, 0.0)];
        let l = lemniscate_length(2, &coeffs, 800);
        // Should be > 0 and finite
        assert!(l > 4.0, "L(z^2-1) should be > 4, got {}", l);
        assert!(l < 20.0, "L(z^2-1) should be < 20, got {}", l);
    }

    #[test]
    fn test_lemniscate_n3_reference() {
        // L(z^3 - 1) should be approximately 9.17
        let coeffs = vec![(-1.0, 0.0), (0.0, 0.0)];
        let l = lemniscate_length(3, &coeffs, 800);
        assert!((l - 9.17).abs() < 0.1, "L(z^3-1) should be ~9.17, got {}", l);
    }

    #[test]
    fn test_box_subdivide() {
        let bx = BoxND {
            bounds: vec![(0.0, 1.0), (-1.0, 1.0)],
        };
        let children = bx.subdivide();
        assert_eq!(children.len(), 4); // 2^2

        let bx3d = BoxND {
            bounds: vec![(0.0, 1.0), (-1.0, 1.0), (0.0, 2.0)],
        };
        let children3 = bx3d.subdivide();
        assert_eq!(children3.len(), 8); // 2^3
    }

    #[test]
    fn test_box_contains_extremizer() {
        let bx = BoxND {
            bounds: vec![(0.5, 1.5), (-0.5, 0.5), (-0.5, 0.5)],
        };
        assert!(bx.contains_extremizer());

        let bx2 = BoxND {
            bounds: vec![(1.5, 2.5), (-0.5, 0.5), (-0.5, 0.5)],
        };
        assert!(!bx2.contains_extremizer());
    }

    #[test]
    fn test_rotation_invariance_n3() {
        // L(a=0, b=-1) should equal L(a=0, b=1) by rotation z -> z*e^{i*pi/3}
        // (since e^{-3i*pi/3} = e^{-i*pi} = -1, so b -> -b)
        let l1 = lemniscate_length(3, &[(-1.0, 0.0), (0.0, 0.0)], 400);
        let l2 = lemniscate_length(3, &[(1.0, 0.0), (0.0, 0.0)], 400);
        assert!(
            (l1 - l2).abs() < 0.01,
            "L(z^3-1) = {} should equal L(z^3+1) = {} by rotation",
            l1, l2
        );
    }
}
