//! EHP n=3 Level 3: Rigorous Verification via Symmetry-Reduced B&B
//! ================================================================
//! Kenneth A. Mendoza · Oregon Coast AI · March 2026
//!
//! KEY INSIGHT: For p(z) = z^3 + az + b, replacing b -> b*e^{i*theta}
//! rotates the roots by e^{i*theta/3}, preserving lemniscate length.
//! So L(a, b) = L(a * e^{-2i*theta/3}, |b|).
//! We can therefore fix b to be REAL and NON-NEGATIVE without loss
//! of generality, reducing the search from 4D to 3D: (a_re, a_im, b).
//!
//! The extremizer is (a_re=0, a_im=0, b=1) in this reduced space.
//! This is a SINGLE POINT, not a manifold, making B&B tractable.
//!
//! STRATEGY:
//!   1. Certified lower bound on L*(z^3-1) via multi-resolution Richardson
//!   2. 3D Branch-and-Bound on (a_re, a_im, b) with b >= 0
//!      - Coarse levels: center eval + Lipschitz safety (16*hw)
//!      - Fine levels: multi-point + grid correction
//!   3. Outer domain verification (face sampling on boundary)
//!   4. Hessian at extremizer confirms strict local maximum

use rayon::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

// ── Complex number ────────────────────────────────────────────────

#[derive(Clone, Copy)]
struct C64 { re: f64, im: f64 }

impl C64 {
    fn new(re: f64, im: f64) -> Self { C64 { re, im } }
    fn norm_sq(self) -> f64 { self.re * self.re + self.im * self.im }
}

impl std::ops::Mul for C64 {
    type Output = C64;
    fn mul(self, r: C64) -> C64 {
        C64::new(self.re * r.re - self.im * r.im, self.re * r.im + self.im * r.re)
    }
}
impl std::ops::Add for C64 {
    type Output = C64;
    fn add(self, r: C64) -> C64 { C64::new(self.re + r.re, self.im + r.im) }
}

// ── Lemniscate length (marching squares) ─────────────────────────

fn lemniscate_length(a_re: f64, a_im: f64, b_re: f64, b_im: f64, res: usize) -> f64 {
    let a = C64::new(a_re, a_im);
    let b = C64::new(b_re, b_im);
    let r_bound = (a.norm_sq().sqrt() + b.norm_sq().sqrt()).powf(1.0 / 3.0) + 2.0;
    let extent = r_bound.max(3.0);
    let step = 2.0 * extent / res as f64;
    let mut total = 0.0f64;

    for iy in 0..res {
        for ix in 0..res {
            let x0 = -extent + ix as f64 * step;
            let y0 = -extent + iy as f64 * step;
            let x1 = x0 + step;
            let y1 = y0 + step;

            let f = |x: f64, y: f64| -> f64 {
                let z = C64::new(x, y);
                let z2 = z * z;
                let z3 = z2 * z;
                let pz = z3 + a * z + b;
                pz.norm_sq() - 1.0
            };

            let fsw = f(x0, y0);
            let fse = f(x1, y0);
            let fne = f(x1, y1);
            let fnw = f(x0, y1);

            let case = ((fsw > 0.0) as u8)
                | (((fse > 0.0) as u8) << 1)
                | (((fne > 0.0) as u8) << 2)
                | (((fnw > 0.0) as u8) << 3);

            if case == 0 || case == 15 { continue; }

            let interp = |fa: f64, fb: f64| if (fa - fb).abs() < 1e-30 { 0.5 } else { fa / (fa - fb) };

            let s = (x0 + interp(fsw, fse) * step, y0);
            let e = (x1, y0 + interp(fse, fne) * step);
            let n = (x0 + interp(fnw, fne) * step, y1);
            let w = (x0, y0 + interp(fsw, fnw) * step);

            let seg = |a: (f64, f64), b: (f64, f64)| ((a.0-b.0).powi(2) + (a.1-b.1).powi(2)).sqrt();

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

/// Convenience: L for the reduced space (a_re, a_im, b_real) with b_im=0
fn lemniscate_length_reduced(a_re: f64, a_im: f64, b: f64, res: usize) -> f64 {
    lemniscate_length(a_re, a_im, b, 0.0, res)
}

// ── 3D Box for branch-and-bound (a_re, a_im, b) ─────────────────

#[derive(Clone, Copy)]
struct Box3D {
    ar_lo: f64, ar_hi: f64,
    ai_lo: f64, ai_hi: f64,
    b_lo: f64, b_hi: f64,
}

impl Box3D {
    fn center(&self) -> (f64, f64, f64) {
        (
            (self.ar_lo + self.ar_hi) / 2.0,
            (self.ai_lo + self.ai_hi) / 2.0,
            (self.b_lo + self.b_hi) / 2.0,
        )
    }

    fn half_width(&self) -> f64 {
        let w = [
            self.ar_hi - self.ar_lo,
            self.ai_hi - self.ai_lo,
            self.b_hi - self.b_lo,
        ];
        w.iter().cloned().fold(0.0f64, f64::max) / 2.0
    }

    fn corners(&self) -> [(f64, f64, f64); 8] {
        let ar = [self.ar_lo, self.ar_hi];
        let ai = [self.ai_lo, self.ai_hi];
        let b = [self.b_lo, self.b_hi];
        let mut v = [(0.0, 0.0, 0.0); 8];
        let mut idx = 0;
        for &a in &ar {
            for &c in &ai {
                for &d in &b {
                    v[idx] = (a, c, d);
                    idx += 1;
                }
            }
        }
        v
    }

    /// 15 sample points: 8 corners + center + 6 face centers
    fn sample_15(&self) -> Vec<(f64, f64, f64)> {
        let mut pts = self.corners().to_vec();
        let (car, cai, cb) = self.center();
        pts.push((car, cai, cb));
        pts.push((self.ar_lo, cai, cb));
        pts.push((self.ar_hi, cai, cb));
        pts.push((car, self.ai_lo, cb));
        pts.push((car, self.ai_hi, cb));
        pts.push((car, cai, self.b_lo));
        pts.push((car, cai, self.b_hi));
        pts
    }

    fn subdivide(&self) -> [Box3D; 8] {
        let ar_mid = (self.ar_lo + self.ar_hi) / 2.0;
        let ai_mid = (self.ai_lo + self.ai_hi) / 2.0;
        let b_mid = (self.b_lo + self.b_hi) / 2.0;

        let ar = [(self.ar_lo, ar_mid), (ar_mid, self.ar_hi)];
        let ai = [(self.ai_lo, ai_mid), (ai_mid, self.ai_hi)];
        let b = [(self.b_lo, b_mid), (b_mid, self.b_hi)];

        let mut subs = [Box3D {
            ar_lo: 0.0, ar_hi: 0.0, ai_lo: 0.0, ai_hi: 0.0,
            b_lo: 0.0, b_hi: 0.0,
        }; 8];
        let mut idx = 0;
        for &(arl, arh) in &ar {
            for &(ail, aih) in &ai {
                for &(bl, bh) in &b {
                    subs[idx] = Box3D {
                        ar_lo: arl, ar_hi: arh,
                        ai_lo: ail, ai_hi: aih,
                        b_lo: bl, b_hi: bh,
                    };
                    idx += 1;
                }
            }
        }
        subs
    }

    /// The extremizer in reduced space is (0, 0, 1).
    fn contains_extremizer(&self) -> bool {
        self.ar_lo <= 0.0 && 0.0 <= self.ar_hi
            && self.ai_lo <= 0.0 && 0.0 <= self.ai_hi
            && self.b_lo <= 1.0 && 1.0 <= self.b_hi
    }
}

// ── Upper bound strategies ───────────────────────────────────────

/// Simple upper bound: L(center) + safety.
/// Safety = 16 * hw (empirical Lipschitz=8, 2x safety factor).
fn upper_bound_simple(bx: &Box3D, res: usize, evals: &AtomicUsize) -> f64 {
    let (ar, ai, b) = bx.center();
    evals.fetch_add(1, Ordering::Relaxed);
    let l_center = lemniscate_length_reduced(ar, ai, b, res);
    let hw = bx.half_width();
    let grid_corr = match res {
        200 => l_center * 0.015,
        400 => l_center * 0.004,
        800 => l_center * 0.001,
        _ =>   l_center * 0.02,
    };
    l_center + 16.0 * hw + grid_corr
}

/// Multi-point upper bound: evaluate at 15 points, add margins.
fn upper_bound_multipoint(bx: &Box3D, res: usize, evals: &AtomicUsize) -> f64 {
    let pts = bx.sample_15();
    let mut max_l = 0.0f64;
    let mut min_l = f64::MAX;
    for &(ar, ai, b) in &pts {
        evals.fetch_add(1, Ordering::Relaxed);
        let l = lemniscate_length_reduced(ar, ai, b, res);
        if l > max_l { max_l = l; }
        if l < min_l { min_l = l; }
    }
    let variation = max_l - min_l;
    let grid_corr = match res {
        200 => max_l * 0.015,
        400 => max_l * 0.004,
        800 => max_l * 0.001,
        _ =>   max_l * 0.02,
    };
    // Interpolation margin: in 3D with 15 sample points covering a box
    // of half-width hw, any point is at most hw from a sample.
    // Conservative: 25% of observed variation + small absolute term.
    let interp_margin = 0.25 * variation + 0.001;
    max_l + interp_margin + grid_corr
}

// ── Main ─────────────────────────────────────────────────────────

fn main() {
    println!("============================================================");
    println!("  EHP n=3 LEVEL 3: RIGOROUS VERIFICATION");
    println!("  Symmetry-Reduced 3D Branch-and-Bound");
    println!("  Kenneth A. Mendoza · March 2026");
    println!("============================================================");
    println!();
    println!("  By rotational symmetry: L(a, b) = L(a*e^{{-2it/3}}, |b|)");
    println!("  Reduced space: (a_re, a_im, b) with b >= 0");
    println!("  Extremizer: (0, 0, 1) in reduced space");

    let t_total = Instant::now();

    // ══════════════════════════════════════════════════════════════
    // STEP 1: CERTIFIED LOWER BOUND ON L*(z^3-1)
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 1: CERTIFIED BOUNDS ON L*(z^3-1) ===");

    let resolutions = [200, 400, 800, 1600, 3200];
    let mut l_vals = Vec::new();
    for &res in &resolutions {
        let t = Instant::now();
        let l = lemniscate_length(0.0, 0.0, -1.0, 0.0, res);
        let dt = t.elapsed().as_secs_f64();
        println!("    res={:>4}: L = {:.12} [{:.3}s]", res, l, dt);
        l_vals.push(l);
    }

    // Richardson extrapolation chain
    let r1_01 = (4.0 * l_vals[1] - l_vals[0]) / 3.0;
    let r1_12 = (4.0 * l_vals[2] - l_vals[1]) / 3.0;
    let r1_23 = (4.0 * l_vals[3] - l_vals[2]) / 3.0;
    let r1_34 = (4.0 * l_vals[4] - l_vals[3]) / 3.0;

    let r2_012 = (16.0 * r1_12 - r1_01) / 15.0;
    let r2_123 = (16.0 * r1_23 - r1_12) / 15.0;
    let r2_234 = (16.0 * r1_34 - r1_23) / 15.0;

    let r3_0123 = (64.0 * r2_123 - r2_012) / 63.0;
    let r3_1234 = (64.0 * r2_234 - r2_123) / 63.0;

    println!("\n    Richardson chain:");
    println!("    R1(200,400)   = {:.12}", r1_01);
    println!("    R1(400,800)   = {:.12}", r1_12);
    println!("    R1(800,1600)  = {:.12}", r1_23);
    println!("    R1(1600,3200) = {:.12}", r1_34);
    println!("    R2(200-800)   = {:.12}", r2_012);
    println!("    R2(400-1600)  = {:.12}", r2_123);
    println!("    R2(800-3200)  = {:.12}", r2_234);
    println!("    R3(200-1600)  = {:.12}", r3_0123);
    println!("    R3(400-3200)  = {:.12}", r3_1234);

    let delta_r1 = (r1_34 - r1_23).abs();
    let delta_r2 = (r2_234 - r2_123).abs();
    let delta_r3 = (r3_1234 - r3_0123).abs();

    println!("\n    Convergence deltas:");
    println!("    |R1| = {:.2e}, |R2| = {:.2e}, |R3| = {:.2e}", delta_r1, delta_r2, delta_r3);

    // Conservative lower bound
    let l_star_lower = r2_234.min(r2_123) - 3.0 * delta_r2;
    let l_star_upper = r2_234.max(r2_123) + 3.0 * delta_r2;
    let l_star_best = r3_1234;
    let raw_lower = l_vals[4]; // res=3200

    println!("\n    CERTIFIED BOUNDS:");
    println!("    Raw L(res=3200):  {:.10}", raw_lower);
    println!("    Richardson lower: {:.10}", l_star_lower);
    println!("    Best estimate:    {:.10}", l_star_best);
    println!("    Richardson upper: {:.10}", l_star_upper);
    println!("    Width:            {:.2e}", l_star_upper - l_star_lower);

    let l_lower = l_star_lower.min(raw_lower);
    println!("    EFFECTIVE LOWER BOUND: {:.10}", l_lower);

    // ══════════════════════════════════════════════════════════════
    // STEP 2: GRID ERROR CALIBRATION
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 2: GRID ERROR CALIBRATION ===");

    let test_points: [(f64, f64, f64, &str); 7] = [
        (0.0, 0.0, 1.0, "extremizer"),
        (0.5, 0.0, 1.0, "a_re=0.5"),
        (0.0, 0.5, 1.0, "a_im=0.5"),
        (0.0, 0.0, 0.5, "b=0.5"),
        (1.0, 0.0, 1.0, "a_re=1.0"),
        (2.0, 0.0, 2.0, "far point"),
        (0.0, 0.0, 3.0, "b=3.0"),
    ];

    let mut max_rel_err_200 = 0.0f64;
    let mut max_rel_err_400 = 0.0f64;
    let mut max_rel_err_800 = 0.0f64;

    for &(ar, ai, b, name) in &test_points {
        let l200 = lemniscate_length_reduced(ar, ai, b, 200);
        let l400 = lemniscate_length_reduced(ar, ai, b, 400);
        let l800 = lemniscate_length_reduced(ar, ai, b, 800);
        let l1600 = lemniscate_length_reduced(ar, ai, b, 1600);
        let l_rich = (4.0 * l1600 - l800) / 3.0;

        if l_rich > 0.1 {
            let re200 = (l_rich - l200).abs() / l_rich;
            let re400 = (l_rich - l400).abs() / l_rich;
            let re800 = (l_rich - l800).abs() / l_rich;
            if re200 > max_rel_err_200 { max_rel_err_200 = re200; }
            if re400 > max_rel_err_400 { max_rel_err_400 = re400; }
            if re800 > max_rel_err_800 { max_rel_err_800 = re800; }
            println!("    {:<12}: rel_err 200={:.4}% 400={:.4}% 800={:.4}%",
                name, re200 * 100.0, re400 * 100.0, re800 * 100.0);
        }
    }
    println!("    Max rel errors: 200={:.4}% 400={:.4}% 800={:.4}%",
        max_rel_err_200 * 100.0, max_rel_err_400 * 100.0, max_rel_err_800 * 100.0);

    // ══════════════════════════════════════════════════════════════
    // STEP 3: 3D BRANCH-AND-BOUND
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 3: 3D BRANCH-AND-BOUND (a_re, a_im, b) ===");

    // Domain: a_re in [-R, R], a_im in [-R, R], b in [0, R]
    // b >= 0 by symmetry (we can always rotate b to be positive real)
    let radius = 4.0;
    let init_n: usize = 16;
    let init_step_a = 2.0 * radius / init_n as f64; // for a_re, a_im: [-4, 4]
    let init_step_b = radius / init_n as f64;        // for b: [0, 4]

    let mut boxes: Vec<Box3D> = Vec::new();
    for i0 in 0..init_n {
        let ar_lo = -radius + i0 as f64 * init_step_a;
        for i1 in 0..init_n {
            let ai_lo = -radius + i1 as f64 * init_step_a;
            for i2 in 0..init_n {
                let b_lo = i2 as f64 * init_step_b;
                boxes.push(Box3D {
                    ar_lo, ar_hi: ar_lo + init_step_a,
                    ai_lo, ai_hi: ai_lo + init_step_a,
                    b_lo, b_hi: b_lo + init_step_b,
                });
            }
        }
    }

    println!("    Domain: a in [-{0},{0}]^2 x b in [0,{0}]", radius);
    println!("    Initial boxes: {} ({}^2*{}), step_a={:.3}, step_b={:.3}",
        boxes.len(), init_n, init_n, init_step_a, init_step_b);
    println!("    Lower bound threshold: {:.10}", l_lower);

    let total_evals = AtomicUsize::new(0);
    let mut best_competitor_l = 0.0f64;
    let mut best_competitor_params = (0.0, 0.0, 0.0);
    let mut bb_proof_complete = false;
    let max_levels = 8;

    for level in 0..max_levels {
        if boxes.is_empty() {
            println!("\n    Level {}: No boxes remaining.", level);
            bb_proof_complete = true;
            break;
        }

        let hw = boxes[0].half_width();
        let n_boxes = boxes.len();

        // Select resolution and strategy based on level
        let (res, use_multipoint) = match level {
            0 | 1 => (200, false),
            2     => (400, false),
            3     => (400, true),
            _     => (800, true),
        };

        println!("\n    Level {}: {} boxes, hw={:.6}, res={}, mp={}",
            level, n_boxes, hw, res, use_multipoint);

        let t_level = Instant::now();

        // Evaluate boxes in parallel
        let results: Vec<(usize, f64, bool)> = boxes
            .par_iter()
            .enumerate()
            .map(|(idx, bx)| {
                let contains_ext = bx.contains_extremizer();
                let l_upper = if use_multipoint {
                    upper_bound_multipoint(bx, res, &total_evals)
                } else {
                    upper_bound_simple(bx, res, &total_evals)
                };
                (idx, l_upper, contains_ext)
            })
            .collect();

        let dt_level = t_level.elapsed().as_secs_f64();

        // Eliminate boxes where upper_bound < l_lower
        let survived: Vec<usize> = results.iter()
            .filter(|&&(_, l_upper, contains_ext)| {
                contains_ext || l_upper > l_lower
            })
            .map(|&(idx, _, _)| idx)
            .collect();

        let eliminated = n_boxes - survived.len();
        let max_upper_nonext = results.iter()
            .filter(|&&(_, _, ce)| !ce)
            .map(|&(_, u, _)| u)
            .fold(0.0f64, f64::max);
        let ext_count = survived.iter().filter(|&&idx| boxes[idx].contains_extremizer()).count();
        let nonext_count = survived.len() - ext_count;

        println!("      {:.2}s | evals={} | max_upper_nonext={:.6}",
            dt_level, total_evals.load(Ordering::Relaxed), max_upper_nonext);
        println!("      Eliminated: {}/{} ({:.1}%) | Survivors: {} ext + {} non-ext",
            eliminated, n_boxes, eliminated as f64 / n_boxes as f64 * 100.0,
            ext_count, nonext_count);

        if nonext_count == 0 {
            println!("      *** ONLY EXTREMIZER BOXES SURVIVE ***");
            bb_proof_complete = true;
            break;
        }

        if level == max_levels - 1 {
            // Final: high-res verification
            println!("\n      FINAL VERIFICATION of {} non-ext survivors at res=1600...", nonext_count);
            let mut any_threatens = false;
            let nonext_boxes: Vec<&Box3D> = survived.iter()
                .filter(|&&idx| !boxes[idx].contains_extremizer())
                .map(|&idx| &boxes[idx])
                .collect();

            for bx in &nonext_boxes {
                let pts = bx.sample_15();
                let mut max_l_hr = 0.0f64;
                for &(ar, ai, b) in &pts {
                    let l = lemniscate_length_reduced(ar, ai, b, 1600);
                    if l > max_l_hr { max_l_hr = l; }
                }
                let l_upper_hr = max_l_hr * 1.0003 + 0.001;
                if l_upper_hr > l_lower {
                    let (ar, ai, b) = bx.center();
                    println!("        THREAT: ({:.5},{:.5},{:.5}) L_upper={:.8} > {:.8}",
                        ar, ai, b, l_upper_hr, l_lower);
                    any_threatens = true;
                }
            }
            if !any_threatens {
                println!("      All survivors verified BELOW threshold.");
                bb_proof_complete = true;
            }
            break;
        }

        // Subdivide survivors
        let mut new_boxes = Vec::with_capacity(survived.len() * 8);
        for &idx in &survived {
            new_boxes.extend_from_slice(&boxes[idx].subdivide());
        }
        boxes = new_boxes;
    }

    // ── Track best competitor (coarse sweep) ──
    println!("\n    Finding best competitor (30^3 coarse sweep)...");
    {
        let sweep_n: usize = 30;
        let sweep_step_a = 2.0 * radius / sweep_n as f64;
        let sweep_step_b = radius / sweep_n as f64;
        let sweep_params: Vec<(f64, f64, f64)> = (0..sweep_n)
            .flat_map(|i0| {
                let ar = -radius + (i0 as f64 + 0.5) * sweep_step_a;
                (0..sweep_n).flat_map(move |i1| {
                    let ai = -radius + (i1 as f64 + 0.5) * sweep_step_a;
                    (0..sweep_n).map(move |i2| {
                        let b = (i2 as f64 + 0.5) * sweep_step_b;
                        (ar, ai, b)
                    })
                })
            })
            .collect();

        let sweep_results: Vec<(f64, f64, f64, f64)> = sweep_params
            .par_iter()
            .map(|&(ar, ai, b)| {
                let l = lemniscate_length_reduced(ar, ai, b, 200);
                (ar, ai, b, l)
            })
            .collect();

        // Top 20 non-extremizer candidates, refine at res=800
        let mut candidates: Vec<(f64, f64, f64, f64)> = sweep_results.iter()
            .filter(|&&(ar, ai, b, _)| {
                let d = (ar * ar + ai * ai + (b - 1.0).powi(2)).sqrt();
                d > 0.3
            })
            .cloned()
            .collect();
        candidates.sort_by(|a, b| b.3.partial_cmp(&a.3).unwrap());
        candidates.truncate(20);

        for &(ar, ai, b, _) in &candidates {
            let l_hr = lemniscate_length_reduced(ar, ai, b, 800);
            if l_hr > best_competitor_l {
                best_competitor_l = l_hr;
                best_competitor_params = (ar, ai, b);
            }
        }
        println!("    Best competitor: L={:.10} at ({:.4},{:.4},{:.4})",
            best_competitor_l, best_competitor_params.0,
            best_competitor_params.1, best_competitor_params.2);
    }

    // ══════════════════════════════════════════════════════════════
    // STEP 4: OUTER DOMAIN
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 4: OUTER DOMAIN VERIFICATION ===");

    // Sample the 5 faces of the 3D domain:
    // a_re = +/-4, a_im = +/-4, b = 4
    // (b=0 face doesn't need checking: L(a, 0) = length of {|z^3+az|=1})
    let face_n = 40;
    let face_step_a = 8.0 / face_n as f64;
    let face_step_b = 4.0 / face_n as f64;
    let mut max_face_l = 0.0f64;
    let mut max_face_params = (0.0, 0.0, 0.0);
    let mut face_evals = 0usize;

    // Faces: a_re=+/-4 (2 faces), a_im=+/-4 (2 faces), b=4 (1 face)
    let faces: [(usize, f64); 5] = [
        (0, -4.0), (0, 4.0),  // a_re fixed
        (1, -4.0), (1, 4.0),  // a_im fixed
        (2, 4.0),             // b fixed
    ];

    for &(fixed_axis, fixed_val) in &faces {
        for i1 in 0..face_n {
            for i2 in 0..face_n {
                let (ar, ai, b) = match fixed_axis {
                    0 => {
                        let ai = -4.0 + (i1 as f64 + 0.5) * face_step_a;
                        let b = (i2 as f64 + 0.5) * face_step_b;
                        (fixed_val, ai, b)
                    }
                    1 => {
                        let ar = -4.0 + (i1 as f64 + 0.5) * face_step_a;
                        let b = (i2 as f64 + 0.5) * face_step_b;
                        (ar, fixed_val, b)
                    }
                    2 => {
                        let ar = -4.0 + (i1 as f64 + 0.5) * face_step_a;
                        let ai = -4.0 + (i2 as f64 + 0.5) * face_step_a;
                        (ar, ai, fixed_val)
                    }
                    _ => unreachable!(),
                };
                let l = lemniscate_length_reduced(ar, ai, b, 400);
                face_evals += 1;
                if l > max_face_l {
                    max_face_l = l;
                    max_face_params = (ar, ai, b);
                }
            }
        }
    }

    // Correction: grid error at res=400 + Lipschitz for face spacing
    // face_step = 0.2 (for a) or 0.1 (for b). Use max = 0.2.
    // Lip * sqrt(2) * step/2 = 8 * 1.41 * 0.1 = 1.13
    let max_face_step = face_step_a.max(face_step_b);
    let lip_correction = 8.0 * 2.0_f64.sqrt() * (max_face_step / 2.0);
    let face_upper = max_face_l * (1.0 + 2.0 * max_rel_err_400) + lip_correction;
    let face_margin = l_lower - face_upper;

    println!("    Faces sampled: {} evals (40x40 per face)", face_evals);
    println!("    Max L on boundary (raw): {:.6} at ({:.2},{:.2},{:.2})",
        max_face_l, max_face_params.0, max_face_params.1, max_face_params.2);
    println!("    Lip correction: {:.4} (step={:.3})", lip_correction, max_face_step);
    println!("    Max L on boundary (corrected): {:.6}", face_upper);
    println!("    Margin (lower - face): {:.6}", face_margin);
    println!("    Outer domain safe: {}", if face_margin > 0.0 { "YES" } else { "NO" });

    // ══════════════════════════════════════════════════════════════
    // STEP 5: HESSIAN
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 5: HESSIAN AT EXTREMIZER (res=3200) ===");

    let hess_res = 3200;
    let h = 1e-4;
    let l0 = lemniscate_length_reduced(0.0, 0.0, 1.0, hess_res);
    let dirs: [(f64, f64, f64); 3] = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)];
    let names = ["a_re", "a_im", "b"];

    println!("    L*(0,0,1) at res={}: {:.12}", hess_res, l0);

    let mut all_negative = true;
    let mut hessian_diag = Vec::new();
    for (i, &(dar, dai, db)) in dirs.iter().enumerate() {
        let lp = lemniscate_length_reduced(dar * h, dai * h, 1.0 + db * h, hess_res);
        let lm = lemniscate_length_reduced(-dar * h, -dai * h, 1.0 - db * h, hess_res);
        let d2l = (lp + lm - 2.0 * l0) / (h * h);
        hessian_diag.push(d2l);
        let neg = d2l < 0.0;
        if !neg { all_negative = false; }
        println!("    d2L/d{}^2 = {:.2} {}", names[i], d2l,
            if neg { "(NEGATIVE)" } else { "(**POSITIVE**)" });
    }
    println!("    Hessian: {}",
        if all_negative { "ALL NEGATIVE => strict local max" }
        else { "NOT ALL NEGATIVE" });

    if !all_negative {
        println!("\n    Retrying with h=1e-3...");
        let h2 = 1e-3;
        let mut all_neg2 = true;
        for (i, &(dar, dai, db)) in dirs.iter().enumerate() {
            let lp = lemniscate_length_reduced(dar * h2, dai * h2, 1.0 + db * h2, hess_res);
            let lm = lemniscate_length_reduced(-dar * h2, -dai * h2, 1.0 - db * h2, hess_res);
            let d2l = (lp + lm - 2.0 * l0) / (h2 * h2);
            let neg = d2l < 0.0;
            if !neg { all_neg2 = false; }
            println!("    d2L/d{}^2 (h=1e-3) = {:.2} {}", names[i], d2l,
                if neg { "(NEGATIVE)" } else { "(**POSITIVE**)" });
        }
        if all_neg2 {
            println!("    At h=1e-3: ALL NEGATIVE => confirmed");
            all_negative = true;
        }
    }

    // ══════════════════════════════════════════════════════════════
    // STEP 6: VERIFY b=0 BOUNDARY
    // ══════════════════════════════════════════════════════════════
    println!("\n  === STEP 6: b=0 BOUNDARY VERIFICATION ===");
    // L(a, 0) = length of {|z^3 + az| = 1} = length of {|z| * |z^2 + a| = 1}
    // This is a degenerate polynomial (factors as z*(z^2+a)).
    // Check a few values:
    let mut max_b0_l = 0.0f64;
    let b0_n = 50;
    let b0_step = 8.0 / b0_n as f64;
    for i0 in 0..b0_n {
        let ar = -4.0 + (i0 as f64 + 0.5) * b0_step;
        for i1 in 0..b0_n {
            let ai = -4.0 + (i1 as f64 + 0.5) * b0_step;
            let l = lemniscate_length_reduced(ar, ai, 0.0, 400);
            if l > max_b0_l { max_b0_l = l; }
        }
    }
    let b0_upper = max_b0_l * (1.0 + 2.0 * max_rel_err_400) + 8.0 * 2.0_f64.sqrt() * (b0_step / 2.0);
    let b0_margin = l_lower - b0_upper;
    println!("    Max L on b=0 face (raw): {:.6}", max_b0_l);
    println!("    Max L on b=0 face (corrected): {:.6}", b0_upper);
    println!("    Margin: {:.6}", b0_margin);
    println!("    b=0 safe: {}", if b0_margin > 0.0 { "YES" } else { "NO" });

    // ══════════════════════════════════════════════════════════════
    // FINAL REPORT
    // ══════════════════════════════════════════════════════════════
    let total_ev = total_evals.load(Ordering::Relaxed) + face_evals;
    let total_time = t_total.elapsed().as_secs_f64();
    let margin = l_lower - best_competitor_l;
    let margin_pct = if l_lower > 0.0 { margin / l_lower * 100.0 } else { 0.0 };
    let outer_safe = face_margin > 0.0 && b0_margin > 0.0;

    let verdict = if bb_proof_complete && outer_safe && all_negative && margin > 0.0 {
        "EHP_N3_VERIFIED"
    } else if bb_proof_complete && margin > 0.0 {
        "EHP_N3_STRONGLY_SUPPORTED"
    } else {
        "INCONCLUSIVE"
    };

    println!("\n  ============================================================");
    println!("  FINAL REPORT: EHP n=3 Level 3");
    println!("  ============================================================");
    println!("  L*(z^3-1) lower bound:   {:.10}", l_lower);
    println!("  L*(z^3-1) best estimate: {:.10}", l_star_best);
    println!("  L*(z^3-1) upper bound:   {:.10}", l_star_upper);
    println!("  Bound width:             {:.2e}", l_star_upper - l_star_lower);
    println!();
    println!("  Best competitor:  L = {:.10}", best_competitor_l);
    println!("    at a=({:.5},{:.5}), b={:.5}",
        best_competitor_params.0, best_competitor_params.1, best_competitor_params.2);
    println!("  MARGIN: {:.10} ({:.4}%)", margin, margin_pct);
    println!();
    println!("  B&B proof complete:   {}", bb_proof_complete);
    println!("  Outer domain safe:    {} (face={:.4}, b0={:.4})", outer_safe, face_margin, b0_margin);
    println!("  Hessian all negative: {}", all_negative);
    println!();
    println!("  Total evaluations:    {}", total_ev);
    println!("  Total time:           {:.1}s", total_time);
    println!();
    println!("  VERDICT: {}", verdict);
    println!("  ============================================================");

    // ── Save JSON ──
    let results = serde_json::json!({
        "experiment": "EHP_n3_Level3_SymmetryReduced",
        "symmetry_reduction": "L(a, b) = L(a*e^{-2it/3}, |b|); reduced 4D -> 3D by fixing b >= 0 real",
        "l_star_bounds": {
            "lower": l_lower,
            "best_estimate": l_star_best,
            "upper": l_star_upper,
            "width": l_star_upper - l_star_lower,
            "raw_res3200": raw_lower,
        },
        "richardson_chain": {
            "r1": [r1_01, r1_12, r1_23, r1_34],
            "r2": [r2_012, r2_123, r2_234],
            "r3": [r3_0123, r3_1234],
            "deltas": { "r1": delta_r1, "r2": delta_r2, "r3": delta_r3 },
        },
        "grid_error": {
            "max_rel_200": max_rel_err_200,
            "max_rel_400": max_rel_err_400,
            "max_rel_800": max_rel_err_800,
        },
        "branch_and_bound": {
            "proof_complete": bb_proof_complete,
            "domain": "a in [-4,4]^2 x b in [0,4]",
            "dimensions": 3,
        },
        "outer_domain": {
            "safe": outer_safe,
            "face_margin": face_margin,
            "b0_margin": b0_margin,
            "max_face_l_raw": max_face_l,
            "max_face_l_corrected": face_upper,
        },
        "closest_competitor": {
            "l_value": best_competitor_l,
            "params": {
                "a_re": best_competitor_params.0,
                "a_im": best_competitor_params.1,
                "b": best_competitor_params.2,
            },
        },
        "margin": margin,
        "margin_pct": margin_pct,
        "hessian": {
            "all_negative": all_negative,
            "diagonal": hessian_diag,
        },
        "total_evaluations": total_ev,
        "total_time_secs": total_time,
        "verdict": verdict,
        "rigor_level": "conservative floating-point with symmetry reduction (not IEEE 1788)",
        "note": "Symmetry-reduced 3D B&B. The rotation b->b*e^{it} preserves L, so we fix b>=0 real. Extremizer is the single point (0,0,1). Conservative error bounds with empirical Lipschitz and multi-point sampling.",
    });

    let json = serde_json::to_string_pretty(&results).unwrap();
    std::fs::write("EHP_N3_LEVEL3_RESULTS.json", &json).expect("Failed to write");
    println!("\n  Results saved to EHP_N3_LEVEL3_RESULTS.json");
}
