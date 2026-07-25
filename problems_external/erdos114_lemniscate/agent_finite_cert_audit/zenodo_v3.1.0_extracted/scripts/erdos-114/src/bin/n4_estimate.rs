//! EHP n=4 Feasibility Estimator
//! ==============================
//! For p(z) = z⁴ + az² + bz + c (a,b,c ∈ ℂ), 6 real parameters.
//! Sample a small fraction, measure time, extrapolate full B&B runtime.

use rayon::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

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

// Lemniscate length for degree-4: p(z) = z^4 + a*z^2 + b*z + c
fn lemniscate_length_n4(
    ar: f64, ai: f64, br: f64, bi: f64, cr: f64, ci: f64, res: usize
) -> f64 {
    let a = C64::new(ar, ai);
    let b = C64::new(br, bi);
    let c = C64::new(cr, ci);
    // Bound: roots within r where r^4 > |a|*r^2 + |b|*r + |c|
    let r_bound = (a.norm_sq().sqrt() + b.norm_sq().sqrt() + c.norm_sq().sqrt()).powf(0.25) + 2.0;
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
                let z4 = z3 * z;
                let pz = z4 + a * z2 + b * z + c;
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

            let interp = |fa: f64, fb: f64| {
                if (fa - fb).abs() < 1e-30 { 0.5 } else { fa / (fa - fb) }
            };

            let s = (x0 + interp(fsw, fse) * step, y0);
            let e = (x1, y0 + interp(fse, fne) * step);
            let n = (x0 + interp(fnw, fne) * step, y1);
            let w = (x0, y0 + interp(fsw, fnw) * step);

            let seg = |a: (f64, f64), b: (f64, f64)| {
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

fn main() {
    println!("============================================================");
    println!("  EHP n=4 FEASIBILITY ESTIMATOR");
    println!("  p(z) = z^4 + az^2 + bz + c, (a,b,c) in C^3 = R^6");
    println!("============================================================");

    // ── Step 1: Reference value L*(z^4-1) ──
    println!("\n  === STEP 1: REFERENCE L*(z^4-1) ===");

    let resolutions = [200, 400, 800];
    let mut l_refs = Vec::new();
    for &res in &resolutions {
        let t = Instant::now();
        // z^4 - 1: a=0, b=0, c=-1
        let l = lemniscate_length_n4(0.0, 0.0, 0.0, 0.0, -1.0, 0.0, res);
        let dt = t.elapsed().as_secs_f64();
        println!("    res={}: L(z^4-1) = {:.10} [{:.4}s]", res, l, dt);
        l_refs.push((res, l, dt));
    }

    let l_richardson = (4.0 * l_refs[2].1 - l_refs[1].1) / 3.0;
    println!("    Richardson: L* = {:.10}", l_richardson);

    // ── Step 2: Single-eval timing ──
    println!("\n  === STEP 2: TIMING PER EVALUATION ===");

    let test_res = 200;
    let n_timing = 1000;
    let t_timing = Instant::now();
    let _: Vec<f64> = (0..n_timing)
        .into_par_iter()
        .map(|i| {
            let x = (i as f64) * 0.01;
            lemniscate_length_n4(x, 0.0, 0.0, 0.0, -1.0, 0.0, test_res)
        })
        .collect();
    let dt_timing = t_timing.elapsed().as_secs_f64();
    let time_per_eval_us = dt_timing / n_timing as f64 * 1e6;
    let evals_per_sec = n_timing as f64 / dt_timing;
    println!("    {} evals at res={} in {:.3}s", n_timing, test_res, dt_timing);
    println!("    Time per eval: {:.0} us ({:.0} evals/s parallel)", time_per_eval_us, evals_per_sec);

    // ── Step 3: Coarse 6D sweep (small sample) ──
    println!("\n  === STEP 3: COARSE 6D SAMPLE ===");

    let radius = 4.0;
    let sample_res: usize = 8; // 8^6 = 262,144 -- manageable sample
    let step = 2.0 * radius / sample_res as f64;
    let n_total = sample_res.pow(6);
    println!("  {}^6 = {} evaluations at res={}", sample_res, n_total, test_res);

    let counter = AtomicUsize::new(0);
    let l_ref_coarse = lemniscate_length_n4(0.0, 0.0, 0.0, 0.0, -1.0, 0.0, test_res);

    let t_sweep = Instant::now();

    // Generate all 6D grid points
    let params: Vec<(f64, f64, f64, f64, f64, f64)> = (0..sample_res)
        .flat_map(|i0| {
            let ar = -radius + (i0 as f64 + 0.5) * step;
            (0..sample_res).flat_map(move |i1| {
                let ai = -radius + (i1 as f64 + 0.5) * step;
                (0..sample_res).flat_map(move |i2| {
                    let br = -radius + (i2 as f64 + 0.5) * step;
                    (0..sample_res).flat_map(move |i3| {
                        let bi = -radius + (i3 as f64 + 0.5) * step;
                        (0..sample_res).flat_map(move |i4| {
                            let cr = -radius + (i4 as f64 + 0.5) * step;
                            (0..sample_res).map(move |i5| {
                                let ci = -radius + (i5 as f64 + 0.5) * step;
                                (ar, ai, br, bi, cr, ci)
                            })
                        })
                    })
                })
            })
        })
        .collect();

    let results: Vec<(f64, f64, f64, f64, f64, f64, f64)> = params
        .par_iter()
        .map(|&(ar, ai, br, bi, cr, ci)| {
            let l = lemniscate_length_n4(ar, ai, br, bi, cr, ci, test_res);
            counter.fetch_add(1, Ordering::Relaxed);
            (ar, ai, br, bi, cr, ci, l)
        })
        .collect();

    let dt_sweep = t_sweep.elapsed().as_secs_f64();

    // Find max and competitors
    let (max_ar, max_ai, max_br, max_bi, max_cr, max_ci, max_l) = results
        .iter()
        .cloned()
        .max_by(|a, b| a.6.partial_cmp(&b.6).unwrap())
        .unwrap();

    let max_dist = (max_ar.powi(2) + max_ai.powi(2) + max_br.powi(2) + max_bi.powi(2)
        + (max_cr + 1.0).powi(2) + max_ci.powi(2)).sqrt();

    // Competitors: away from extremizer
    let mut competitors: Vec<&(f64, f64, f64, f64, f64, f64, f64)> = results
        .iter()
        .filter(|&&(ar, ai, br, bi, cr, ci, _)| {
            let d = (ar.powi(2) + ai.powi(2) + br.powi(2) + bi.powi(2)
                + (cr + 1.0).powi(2) + ci.powi(2)).sqrt();
            d > 0.5
        })
        .collect();
    competitors.sort_by(|a, b| b.6.partial_cmp(&a.6).unwrap());

    // Count counterexamples
    let n_above = results.iter().filter(|r| r.6 > l_ref_coarse).count();

    println!("  Time: {:.2}s ({:.0} evals/s)", dt_sweep, n_total as f64 / dt_sweep);
    println!("  L*(z^4-1) at res={}: {:.8}", test_res, l_ref_coarse);
    println!("  Global max: L={:.8} at ({:.2},{:.2},{:.2},{:.2},{:.2},{:.2}) dist={:.3}",
        max_l, max_ar, max_ai, max_br, max_bi, max_cr, max_ci, max_dist);
    println!("  Counterexamples (L > L_ref): {}/{}", n_above, n_total);

    if !competitors.is_empty() {
        let c = competitors[0];
        let margin = l_ref_coarse - c.6;
        let margin_pct = margin / l_ref_coarse * 100.0;
        println!("  Closest competitor: L={:.8} margin={:.6} ({:.3}%)", c.6, margin, margin_pct);
    }

    println!("\n  Top 5 competitors:");
    for (i, c) in competitors.iter().take(5).enumerate() {
        println!("    #{}: L={:.8} at ({:.2},{:.2},{:.2},{:.2},{:.2},{:.2})",
            i+1, c.6, c.0, c.1, c.2, c.3, c.4, c.5);
    }

    // ── Step 4: Extrapolate full B&B runtime ──
    println!("\n  === STEP 4: FULL B&B RUNTIME ESTIMATE ===");

    // For n=3, B&B used 20^4 = 160K initial boxes, eliminated 98.9% at level 0
    // For n=4, initial grid would be 20^6 = 64M boxes (at coarse res=200)
    // But with aggressive elimination, we expect similar 98-99% elimination per level

    let full_grid_20: usize = 20_usize.pow(6);
    let full_grid_15: usize = 15_usize.pow(6);
    let full_grid_10: usize = 10_usize.pow(6);

    let actual_evals_per_sec = n_total as f64 / dt_sweep;

    // Estimate elimination rate from our sample
    let threshold_80 = l_ref_coarse * 0.80;
    let n_above_threshold = results.iter().filter(|r| r.6 > threshold_80).count();
    let survival_rate = n_above_threshold as f64 / n_total as f64;

    println!("  Grid dimensions for n=4 (6D):");
    println!("    10^6 = {} boxes", full_grid_10);
    println!("    15^6 = {} boxes", full_grid_15);
    println!("    20^6 = {} boxes", full_grid_20);
    println!("  Eval rate: {:.0} evals/s (parallel, res={})", actual_evals_per_sec, test_res);
    println!("  Survival rate at 80% threshold: {:.4} ({}/{})",
        survival_rate, n_above_threshold, n_total);

    // Time estimates
    for (name, n) in [("10^6", full_grid_10), ("15^6", full_grid_15), ("20^6", full_grid_20)] {
        let t_level0 = n as f64 / actual_evals_per_sec;
        let survivors = (n as f64 * survival_rate) as usize;
        let t_level1 = survivors as f64 * 64.0 / actual_evals_per_sec; // 2^6=64 subdivisions
        let t_total_est = t_level0 + t_level1;

        println!("\n  {} initial boxes:", name);
        println!("    Level 0: {:.1}s ({} boxes)", t_level0, n);
        println!("    Survivors: ~{} ({:.2}%)", survivors, survival_rate * 100.0);
        println!("    Level 1: ~{:.1}s ({} sub-boxes)", t_level1, survivors * 64);
        println!("    Estimated total: ~{:.0}s ({:.1} min)", t_total_est, t_total_est / 60.0);
    }

    // n=3 comparison
    println!("\n  === COMPARISON WITH n=3 ===");
    println!("  n=3 (4D): 160K boxes, 50s, 4 levels, 98.9% elimination");
    println!("  n=4 (6D): {}x more boxes, ~{:.1}x more params per box",
        full_grid_20 as f64 / 160000.0, 6.0 / 4.0);

    // Save results
    let results_json = serde_json::json!({
        "experiment": "EHP_n4_feasibility",
        "reference_l_star": l_ref_coarse,
        "reference_l_star_richardson": l_richardson,
        "reference_resolution": test_res,
        "sample_grid": format!("{}^6", sample_res),
        "sample_total": n_total,
        "sample_time_secs": dt_sweep,
        "evals_per_sec": actual_evals_per_sec,
        "counterexamples": n_above,
        "survival_rate_80pct": survival_rate,
        "global_max": {
            "l_value": serde_json::json!(max_l),
            "params": serde_json::json!([max_ar, max_ai, max_br, max_bi, max_cr, max_ci]),
            "dist_to_extremizer": serde_json::json!(max_dist),
        },
        "closest_competitor_l": if !competitors.is_empty() { competitors[0].6 } else { 0.0 },
        "margin": if !competitors.is_empty() { l_ref_coarse - competitors[0].6 } else { 0.0 },
        "runtime_estimates": {
            "grid_10_6_secs": serde_json::json!(full_grid_10 as f64 / actual_evals_per_sec),
            "grid_15_6_secs": serde_json::json!(full_grid_15 as f64 / actual_evals_per_sec),
            "grid_20_6_secs": serde_json::json!(full_grid_20 as f64 / actual_evals_per_sec),
        },
    });

    let json = serde_json::to_string_pretty(&results_json).unwrap();
    std::fs::write("EHP_N4_ESTIMATE.json", &json).expect("Failed to write");
    println!("\n  Saved to EHP_N4_ESTIMATE.json");
}
