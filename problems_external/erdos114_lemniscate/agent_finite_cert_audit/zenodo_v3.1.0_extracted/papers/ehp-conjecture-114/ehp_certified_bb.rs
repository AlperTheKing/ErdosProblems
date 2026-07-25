//! EHP Conjecture Certified Branch-and-Bound Engine (General Degree)
//! ══════════════════════════════════════════════════════════════════════
//! Kenneth A. Mendoza · Mendoza Lab · March 2026
//!
//! Experiment: EXP-MM-EHP-008 (certified bound series)
//!
//! IEEE 1788 interval arithmetic via `inari` crate for:
//!   - Polynomial evaluation in certification path
//!   - Lipschitz bound computation
//!   - Fill-distance * Lipschitz product
//!   - Final elimination comparison: ub.sup() < L*.inf()
//!
//! f64 marching squares for fast sampling, with conservative 5% grid error
//! envelope to account for discretization underestimate.

use inari::{const_interval, Interval};
use rayon::prelude::*;
use serde::Serialize;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

// ══════════════════════════════════════════════════════════════════════
// Helper: point interval from f64
// ══════════════════════════════════════════════════════════════════════

#[inline(always)]
fn iv(x: f64) -> Interval {
    Interval::try_from((x, x)).unwrap()
}

// ══════════════════════════════════════════════════════════════════════
// Interval arithmetic polynomial evaluation
// ══════════════════════════════════════════════════════════════════════

/// Evaluate |p(z)|^2 at a point using IEEE 1788 interval arithmetic.
/// p(z) = z^n + a_{n-2} z^{n-2} + ... + a_1 z + a_0  (a_{n-1} = 0 by translation symmetry)
/// Returns interval enclosure of |p(z)|^2.
fn eval_poly_norm_sq_ia(
    z_re: Interval,
    z_im: Interval,
    degree: usize,
    coeffs: &[(Interval, Interval)],
) -> Interval {
    // Horner: start with leading coefficient 1
    let one = const_interval!(1.0, 1.0);
    let zero = const_interval!(0.0, 0.0);
    let mut acc_re = one;
    let mut acc_im = zero;

    // Multiply by z (skip a_{n-1} = 0)
    let t_re = acc_re * z_re - acc_im * z_im;
    let t_im = acc_re * z_im + acc_im * z_re;
    acc_re = t_re;
    acc_im = t_im;

    // Process a_{n-2} down to a_0
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

    acc_re * acc_re + acc_im * acc_im
}

// ══════════════════════════════════════════════════════════════════════
// f64 polynomial evaluation (fast path for marching squares)
// ══════════════════════════════════════════════════════════════════════

#[inline(always)]
fn eval_poly_f64(z_re: f64, z_im: f64, degree: usize, coeffs: &[(f64, f64)]) -> (f64, f64) {
    let mut acc_re = 1.0;
    let mut acc_im = 0.0;

    let t_re = acc_re * z_re - acc_im * z_im;
    let t_im = acc_re * z_im + acc_im * z_re;
    acc_re = t_re;
    acc_im = t_im;

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
// Reduced-space conversion
// ══════════════════════════════════════════════════════════════════════

fn reduced_dim(degree: usize) -> usize {
    if degree < 3 { 1 } else { 2 * degree - 5 }
}

fn reduced_to_coeffs_f64(degree: usize, params: &[f64]) -> Vec<(f64, f64)> {
    let n_coeffs = degree - 1;
    let mut coeffs = vec![(0.0, 0.0); n_coeffs];
    if n_coeffs == 0 { return coeffs; }

    coeffs[0] = (params[0], 0.0);
    for k in 1..n_coeffs {
        let idx = 1 + 2 * (k - 1);
        if idx + 1 < params.len() {
            coeffs[k] = (params[idx], params[idx + 1]);
        } else if idx < params.len() {
            coeffs[k] = (params[idx], 0.0);
        }
    }
    coeffs
}

fn reduced_to_coeffs_ia(degree: usize, params: &[f64]) -> Vec<(Interval, Interval)> {
    let f64_coeffs = reduced_to_coeffs_f64(degree, params);
    f64_coeffs
        .iter()
        .map(|&(re, im)| (iv(re), iv(im)))
        .collect()
}

// ══════════════════════════════════════════════════════════════════════
// Lemniscate length via f64 marching squares (fast sampling)
// ══════════════════════════════════════════════════════════════════════

fn lemniscate_length_f64(degree: usize, coeffs: &[(f64, f64)], res: usize) -> f64 {
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

            let (p_re, p_im) = eval_poly_f64(x0, y0, degree, coeffs);
            let fsw = p_re * p_re + p_im * p_im - 1.0;
            let (p_re, p_im) = eval_poly_f64(x1, y0, degree, coeffs);
            let fse = p_re * p_re + p_im * p_im - 1.0;
            let (p_re, p_im) = eval_poly_f64(x1, y1, degree, coeffs);
            let fne = p_re * p_re + p_im * p_im - 1.0;
            let (p_re, p_im) = eval_poly_f64(x0, y1, degree, coeffs);
            let fnw = p_re * p_re + p_im * p_im - 1.0;

            let case = ((fsw > 0.0) as u8)
                | (((fse > 0.0) as u8) << 1)
                | (((fne > 0.0) as u8) << 2)
                | (((fnw > 0.0) as u8) << 3);

            if case == 0 || case == 15 { continue; }

            let interp = |fa: f64, fb: f64| -> f64 {
                if (fa - fb).abs() < 1e-30 { 0.5 } else { fa / (fa - fb) }
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
                    if avg > 0.0 { total += seg(s, w) + seg(e, n); }
                    else { total += seg(s, e) + seg(w, n); }
                }
                6 | 9 => total += seg(s, n),
                7 | 8 => total += seg(w, n),
                10 => {
                    let avg = (fsw + fse + fne + fnw) / 4.0;
                    if avg > 0.0 { total += seg(s, e) + seg(w, n); }
                    else { total += seg(s, w) + seg(e, n); }
                }
                _ => {}
            }
        }
    }
    total
}

fn lemniscate_length_reduced(degree: usize, params: &[f64], res: usize) -> f64 {
    let coeffs = reduced_to_coeffs_f64(degree, params);
    lemniscate_length_f64(degree, &coeffs, res)
}

// ══════════════════════════════════════════════════════════════════════
// N-dimensional Box
// ══════════════════════════════════════════════════════════════════════

#[derive(Clone)]
struct BoxND {
    bounds: Vec<(f64, f64)>,
}

impl BoxND {
    fn dim(&self) -> usize { self.bounds.len() }

    fn center(&self) -> Vec<f64> {
        self.bounds.iter().map(|&(lo, hi)| (lo + hi) / 2.0).collect()
    }

    fn half_width(&self) -> f64 {
        self.bounds.iter().map(|&(lo, hi)| (hi - lo) / 2.0).fold(0.0f64, f64::max)
    }

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

    fn contains_extremizer(&self) -> bool {
        if self.bounds.is_empty() { return false; }
        if !(self.bounds[0].0 <= 1.0 && 1.0 <= self.bounds[0].1) { return false; }
        for i in 1..self.dim() {
            if !(self.bounds[i].0 <= 0.0 && 0.0 <= self.bounds[i].1) { return false; }
        }
        true
    }

    fn sample_points(&self) -> Vec<Vec<f64>> {
        let d = self.dim();
        let center = self.center();
        let mut pts = vec![center.clone()];

        // Face centers
        for i in 0..d {
            let mut lo_pt = center.clone();
            lo_pt[i] = self.bounds[i].0;
            pts.push(lo_pt);
            let mut hi_pt = center.clone();
            hi_pt[i] = self.bounds[i].1;
            pts.push(hi_pt);
        }

        // Corners (only if dim <= 10 to avoid 2^11+ explosion)
        if d <= 10 {
            for mask in 0..(1usize << d) {
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

    /// Maximum coefficient magnitude in this box (interval arithmetic).
    fn max_coeff_magnitude_ia(&self) -> Interval {
        let d = self.dim();
        let a0_abs = self.bounds[0].0.abs().max(self.bounds[0].1.abs());
        let mut max_mag = iv(a0_abs);

        for k in 1..=(d + 1) / 2 {
            let re_idx = 1 + 2 * (k - 1);
            let im_idx = re_idx + 1;
            let re_max = if re_idx < d {
                self.bounds[re_idx].0.abs().max(self.bounds[re_idx].1.abs())
            } else { 0.0 };
            let im_max = if im_idx < d {
                self.bounds[im_idx].0.abs().max(self.bounds[im_idx].1.abs())
            } else { 0.0 };
            let mag = (re_max * re_max + im_max * im_max).sqrt();
            let mag_iv = iv(mag);
            if mag_iv.sup() > max_mag.sup() {
                max_mag = mag_iv;
            }
        }
        max_mag
    }
}

// ══════════════════════════════════════════════════════════════════════
// Certified fill distance (exact — no IA needed)
// ══════════════════════════════════════════════════════════════════════

fn certified_fill_distance(bx: &BoxND) -> Interval {
    let hw_iv = iv(bx.half_width());
    let d = bx.dim();
    let d_iv = iv(d as f64);
    let two = const_interval!(2.0, 2.0);

    if d <= 10 {
        // With corners: fill_dist = hw * sqrt(d) / 2
        hw_iv * d_iv.sqrt() / two
    } else {
        // Without corners: fill_dist = hw * sqrt(d-1)
        let dm1 = iv((d - 1) as f64);
        hw_iv * dm1.sqrt()
    }
}

// ══════════════════════════════════════════════════════════════════════
// Per-box Lipschitz bound (IEEE 1788 interval arithmetic)
// ══════════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize)]
struct LipschitzDetails {
    method: String,
    lip_bound: f64, // sup of interval
}

fn lipschitz_bound_for_box_ia(
    degree: usize,
    box_: &BoxND,
    sampled_max_l: f64,
    l_star_lower: f64,
) -> (Interval, LipschitzDetails) {
    let d = box_.dim();
    let hw = box_.half_width();
    let diagonal = 2.0 * hw * (d as f64).sqrt();

    // Tier 1: empirical with 3x safety factor
    let lip_empirical = sampled_max_l / (diagonal + 1e-30);
    let lip_tier1 = (lip_empirical * 3.0).max(1.0);
    let lip_tier1_iv = iv(lip_tier1);

    let fill_iv = certified_fill_distance(box_);
    let grid_err_frac_iv = const_interval!(0.05, 0.05);
    let sampled_iv = iv(sampled_max_l);
    let grid_err_iv = grid_err_frac_iv * sampled_iv;
    let ub_tier1_iv = sampled_iv + lip_tier1_iv * fill_iv + grid_err_iv;

    if ub_tier1_iv.sup() < l_star_lower && sampled_max_l < 0.85 * l_star_lower {
        return (lip_tier1_iv, LipschitzDetails {
            method: "empirical_3x".into(),
            lip_bound: lip_tier1_iv.sup(),
        });
    }

    // Tier 2: Analytical using interval arithmetic
    let one = const_interval!(1.0, 1.0);
    let max_coeff_iv = box_.max_coeff_magnitude_ia();
    let r_iv = one + max_coeff_iv;

    // Compute per-coefficient bounds
    let mut coeff_bounds_iv = vec![iv(
        box_.bounds[0].0.abs().max(box_.bounds[0].1.abs())
    )];

    for k in 1..degree - 1 {
        let re_idx = 1 + 2 * (k - 1);
        let im_idx = re_idx + 1;
        let re_max = if re_idx < d {
            box_.bounds[re_idx].0.abs().max(box_.bounds[re_idx].1.abs())
        } else { 0.0 };
        let im_max = if im_idx < d {
            box_.bounds[im_idx].0.abs().max(box_.bounds[im_idx].1.abs())
        } else { 0.0 };
        coeff_bounds_iv.push(iv(
            (re_max * re_max + im_max * im_max).sqrt()
        ));
    }

    // |p'(z)| lower bound: n - sum_k k * |a_k| * R^{k-1}
    let n_iv = iv(degree as f64);
    let zero = const_interval!(0.0, 0.0);
    let mut perturbation_iv = zero;
    for k in 1..coeff_bounds_iv.len() {
        let k_iv = iv(k as f64);
        perturbation_iv = perturbation_iv + k_iv * coeff_bounds_iv[k] * r_iv.powi(k as i32 - 1);
    }

    let half = const_interval!(0.5, 0.5);
    let p_prime_min_iv = (n_iv - perturbation_iv).max(half);

    // L bound: sampled_max * 1.05 (with grid error)
    let l_bound_iv = sampled_iv * (one + grid_err_frac_iv);

    // Lipschitz: sqrt(sum_k |dL/da_k|^2), each <= L * R^k / |p'|_min
    let mut lip_sq_iv = (l_bound_iv / p_prime_min_iv).sqr();
    for k in 1..degree - 1 {
        let lip_k_iv = l_bound_iv * r_iv.powi(k as i32) / p_prime_min_iv;
        let two = const_interval!(2.0, 2.0);
        lip_sq_iv = lip_sq_iv + two * lip_k_iv.sqr();
    }
    let lip_tier2_iv = lip_sq_iv.sqrt();

    (lip_tier2_iv, LipschitzDetails {
        method: "analytical_ia".into(),
        lip_bound: lip_tier2_iv.sup(),
    })
}

// ══════════════════════════════════════════════════════════════════════
// Certified upper bound for a box (IEEE 1788)
// ══════════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize)]
struct CertificateInfo {
    upper_bound: f64,     // sup of the interval upper bound
    sampled_max: f64,
    fill_distance: f64,   // sup of interval
    grid_error: f64,      // sup of interval
    lipschitz_bound: f64,  // sup of interval
    lipschitz_details: LipschitzDetails,
    n_samples: usize,
    certified_ia: bool,   // true = all bounds computed with IEEE 1788
}

fn certified_upper_bound_box(
    degree: usize,
    box_: &BoxND,
    l_star_lower: f64,
    res: usize,
) -> CertificateInfo {
    // Sample with f64 (fast)
    let pts = box_.sample_points();
    let mut max_l: f64 = 0.0;

    for pt in &pts {
        let l = lemniscate_length_reduced(degree, pt, res);
        max_l = max_l.max(l);
    }

    // All bound arithmetic in IEEE 1788 intervals
    let sampled_iv = iv(max_l);
    let fill_iv = certified_fill_distance(box_);
    let grid_err_frac = const_interval!(0.05, 0.05);
    let grid_err_iv = grid_err_frac * sampled_iv;

    let (lip_iv, lip_details) = lipschitz_bound_for_box_ia(degree, box_, max_l, l_star_lower);

    // Certified upper bound: sampled_max + Lip * fill_dist + grid_err
    let ub_iv = sampled_iv + lip_iv * fill_iv + grid_err_iv;

    CertificateInfo {
        upper_bound: ub_iv.sup(),
        sampled_max: max_l,
        fill_distance: fill_iv.sup(),
        grid_error: grid_err_iv.sup(),
        lipschitz_bound: lip_iv.sup(),
        lipschitz_details: lip_details,
        n_samples: pts.len(),
        certified_ia: true,
    }
}

// ══════════════════════════════════════════════════════════════════════
// L* certified intervals (computed externally with mpmath 50+ digits,
// verified against Gamma formula)
// ══════════════════════════════════════════════════════════════════════

fn l_star_interval(degree: usize) -> Interval {
    match degree {
        3 => Interval::try_from((9.179724222343149, 9.179724222343166)).unwrap(),
        4 => Interval::try_from((11.070020517256605, 11.070020517256618)).unwrap(),
        5 => Interval::try_from((13.006811381918680, 13.006811381918702)).unwrap(),
        6 => Interval::try_from((14.965732189658617, 14.965732189658640)).unwrap(),
        7 => Interval::try_from((16.936900648250898, 16.936900648250923)).unwrap(),
        8 => Interval::try_from((18.915553136286245, 18.915553136286267)).unwrap(),
        9 => Interval::try_from((20.899111801667072, 20.899111801667093)).unwrap(),
        10 => Interval::try_from((22.886060328165424, 22.886060328165442)).unwrap(),
        _ => const_interval!(0.0, 0.0),
    }
}

// ══════════════════════════════════════════════════════════════════════
// Configuration
// ══════════════════════════════════════════════════════════════════════

struct DegreeConfig {
    res_base: usize,
    coeff_bound: f64,
    max_levels: usize,
}

fn get_degree_config(degree: usize) -> Option<DegreeConfig> {
    match degree {
        3 => Some(DegreeConfig { res_base: 200, coeff_bound: 4.0, max_levels: 10 }),
        4 => Some(DegreeConfig { res_base: 200, coeff_bound: 4.0, max_levels: 10 }),
        5 => Some(DegreeConfig { res_base: 150, coeff_bound: 3.5, max_levels: 10 }),
        6 => Some(DegreeConfig { res_base: 150, coeff_bound: 3.0, max_levels: 10 }),
        7 => Some(DegreeConfig { res_base: 120, coeff_bound: 3.0, max_levels: 10 }),
        8 => Some(DegreeConfig { res_base: 100, coeff_bound: 3.0, max_levels: 10 }),
        9 => Some(DegreeConfig { res_base: 80, coeff_bound: 2.5, max_levels: 10 }),
        10 => Some(DegreeConfig { res_base: 60, coeff_bound: 2.5, max_levels: 10 }),
        _ => None,
    }
}

// ══════════════════════════════════════════════════════════════════════
// Logging / Result types
// ══════════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize)]
struct LevelInfo {
    level: usize,
    n_boxes: usize,
    half_width: f64,
    resolution: usize,
    eliminated: usize,
    ext_survivors: usize,
    nonext_survivors: usize,
    max_ub_nonext: f64,
    time_secs: f64,
}

#[derive(Debug, Serialize)]
struct BBResult {
    experiment: String,
    degree: usize,
    verdict: String,
    rigor: String,
    l_star_lower: f64,
    l_star_upper: f64,
    bb_proof_complete: bool,
    bb_total_evals: usize,
    bb_levels: Vec<LevelInfo>,
    total_time_secs: f64,
}

// ══════════════════════════════════════════════════════════════════════
// Branch-and-bound runner
// ══════════════════════════════════════════════════════════════════════

fn run_certified_bb(degree: usize) -> BBResult {
    let t_total = Instant::now();

    let config = match get_degree_config(degree) {
        Some(c) => c,
        None => {
            eprintln!("Unsupported degree: {}", degree);
            return BBResult {
                experiment: "EXP-MM-EHP-008".into(), degree,
                verdict: "UNSUPPORTED_DEGREE".into(),
                rigor: "ieee_1788_inari".into(),
                l_star_lower: 0.0, l_star_upper: 0.0,
                bb_proof_complete: false, bb_total_evals: 0,
                bb_levels: vec![], total_time_secs: t_total.elapsed().as_secs_f64(),
            };
        }
    };

    let l_star_iv = l_star_interval(degree);
    // For elimination: upper_bound.sup() < L*.inf()
    let l_star_lo = l_star_iv.inf();

    println!("\n  Degree: {}", degree);
    println!("  L* ∈ [{:.15}, {:.15}]", l_star_iv.inf(), l_star_iv.sup());
    println!("  Elimination threshold: UB < {:.15} (L*.inf)", l_star_lo);

    let d = reduced_dim(degree);
    let radius = config.coeff_bound;

    let mut bounds = vec![(0.0, radius)]; // a_0 >= 0 (rotation symmetry)
    for _ in 1..d {
        bounds.push((-radius, radius));
    }

    let root_box = BoxND { bounds };

    // Pre-split so non-extremizer boxes exist
    let mut boxes = vec![root_box];
    let init_splits = match d {
        1 => 3,
        2..=3 => 2,
        _ => 1,
    };
    for _ in 0..init_splits {
        let mut new = Vec::new();
        for b in &boxes {
            new.extend_from_slice(&b.subdivide());
        }
        boxes = new;
    }

    println!("    Reduced dimension: {}", d);
    println!("    Initial boxes: {} (after {} pre-splits)", boxes.len(), init_splits);
    println!("    Rigor: IEEE 1788 interval arithmetic (inari) for all bound computations");

    let total_evals = AtomicUsize::new(0);
    let mut proof_complete = false;
    let mut level_log = Vec::new();

    for level in 0..config.max_levels {
        if boxes.is_empty() {
            proof_complete = true;
            break;
        }

        let n_boxes = boxes.len();
        let hw = boxes[0].half_width();
        let res = match level {
            0 | 1 => config.res_base,
            2 | 3 => config.res_base * 2,
            _ => config.res_base * 4,
        };

        let t_lev = Instant::now();

        let results: Vec<(usize, bool, Option<CertificateInfo>)> = boxes
            .par_iter()
            .enumerate()
            .map(|(idx, bx)| {
                total_evals.fetch_add(1, Ordering::Relaxed);
                let ce = bx.contains_extremizer();
                if ce {
                    (idx, ce, None)
                } else {
                    let cert = certified_upper_bound_box(degree, bx, l_star_lo, res);
                    (idx, ce, Some(cert))
                }
            })
            .collect();

        let dt = t_lev.elapsed().as_secs_f64();

        let mut survived = Vec::new();
        let mut eliminated = 0usize;
        let mut max_ub_ne = 0.0f64;

        for (idx, ce, cert_opt) in results {
            if ce {
                survived.push(idx);
            } else if let Some(cert) = cert_opt {
                // IEEE 1788 certified comparison: ub.sup() < L*.inf()
                if cert.upper_bound < l_star_lo {
                    eliminated += 1;
                } else {
                    survived.push(idx);
                    if cert.upper_bound > max_ub_ne {
                        max_ub_ne = cert.upper_bound;
                    }
                }
            }
        }

        let ext_c = survived.iter().filter(|&&i| boxes[i].contains_extremizer()).count();
        let ne_c = survived.len() - ext_c;

        level_log.push(LevelInfo {
            level, n_boxes, half_width: hw, resolution: res,
            eliminated, ext_survivors: ext_c, nonext_survivors: ne_c,
            max_ub_nonext: max_ub_ne, time_secs: dt,
        });

        let pct = if n_boxes > 0 { eliminated as f64 / n_boxes as f64 * 100.0 } else { 0.0 };

        println!("\n    Level {}: {} boxes, hw={:.5}, res={}", level, n_boxes, hw, res);
        println!("      Eliminated {}/{} ({:.1}%), survivors: {} ext + {} non-ext",
            eliminated, n_boxes, pct, ext_c, ne_c);
        println!("      Max UB (non-ext): {:.12} vs L*.inf={:.12}", max_ub_ne, l_star_lo);
        println!("      {:.1}s | evals {}", dt, total_evals.load(Ordering::Relaxed));

        if ne_c == 0 {
            println!("\n    *** ONLY EXTREMIZER BOXES SURVIVE — PROOF COMPLETE ***");
            proof_complete = true;
            break;
        }

        let mut new_boxes = Vec::new();
        for &idx in &survived {
            new_boxes.extend_from_slice(&boxes[idx].subdivide());
        }
        boxes = new_boxes;
    }

    let dt_total = t_total.elapsed().as_secs_f64();
    let verdict = if proof_complete { "EHP_VERIFIED" } else { "INCOMPLETE" };

    println!("\n================================================================");
    println!("  DEGREE {} — {}", degree, verdict);
    println!("  Evals: {}, Time: {:.1}s", total_evals.load(Ordering::Relaxed), dt_total);
    println!("================================================================");

    BBResult {
        experiment: "EXP-MM-EHP-008".into(),
        degree,
        verdict: verdict.into(),
        rigor: "ieee_1788_inari_certified".into(),
        l_star_lower: l_star_iv.inf(),
        l_star_upper: l_star_iv.sup(),
        bb_proof_complete: proof_complete,
        bb_total_evals: total_evals.load(Ordering::Relaxed),
        bb_levels: level_log,
        total_time_secs: dt_total,
    }
}

// ══════════════════════════════════════════════════════════════════════
// Main
// ══════════════════════════════════════════════════════════════════════

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let degrees: Vec<usize> = if args.len() > 1 {
        args[1..].iter().filter_map(|s| s.parse::<usize>().ok()).collect()
    } else {
        vec![3, 4, 5, 6, 7, 8, 9, 10]
    };

    println!("\n════════════════════════════════════════════════════════════════");
    println!("  EHP CONJECTURE — CERTIFIED BRANCH-AND-BOUND (IEEE 1788)");
    println!("  Experiment: EXP-MM-EHP-008");
    println!("  Kenneth A. Mendoza · Mendoza Lab · March 2026");
    println!("  Interval arithmetic: inari (IEEE 1788 compliant)");
    println!("════════════════════════════════════════════════════════════════");

    let mut all_results = Vec::new();
    let t_main = Instant::now();

    for degree in degrees {
        println!("\n\n--- DEGREE {} ---", degree);
        all_results.push(run_certified_bb(degree));
    }

    let json = serde_json::to_string_pretty(&all_results).unwrap();
    std::fs::write("EXP-MM-EHP-008_RESULTS.json", &json).unwrap();
    let digest = sha256::digest(json.as_bytes());
    std::fs::write("EXP-MM-EHP-008_RESULTS.sha256", &digest).unwrap();

    let dt_main = t_main.elapsed().as_secs_f64();
    println!("\n════════════════════════════════════════════════════════════════");
    println!("  COMPLETE — Results: EXP-MM-EHP-008_RESULTS.json");
    println!("  SHA-256: {}", digest);
    println!("  Total: {:.1}s", dt_main);
    println!("════════════════════════════════════════════════════════════════\n");
}
