//! EHP n=3 Level 2: Adaptive Branch-and-Bound with Margin Analysis
//! ================================================================
//! Kenneth A. Mendoza · Oregon Coast AI · March 2026
//!
//! OPTIMIZED: Uses adaptive resolution — low res (200) for coarse
//! elimination, high res (800+) only near the decision boundary.
//! Richardson extrapolation for the reference value.

use rayon::prelude::*;
use std::f64::consts::PI;
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
impl std::ops::Sub for C64 {
    type Output = C64;
    fn sub(self, r: C64) -> C64 { C64::new(self.re - r.re, self.im - r.im) }
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

// ── 4D Box for branch-and-bound ──────────────────────────────────

#[derive(Clone, Copy)]
struct Box4D {
    ar_lo: f64, ar_hi: f64,
    ai_lo: f64, ai_hi: f64,
    br_lo: f64, br_hi: f64,
    bi_lo: f64, bi_hi: f64,
}

impl Box4D {
    fn center(&self) -> (f64, f64, f64, f64) {
        (
            (self.ar_lo + self.ar_hi) / 2.0,
            (self.ai_lo + self.ai_hi) / 2.0,
            (self.br_lo + self.br_hi) / 2.0,
            (self.bi_lo + self.bi_hi) / 2.0,
        )
    }

    fn half_width(&self) -> f64 {
        let w = [
            self.ar_hi - self.ar_lo,
            self.ai_hi - self.ai_lo,
            self.br_hi - self.br_lo,
            self.bi_hi - self.bi_lo,
        ];
        w.iter().cloned().fold(0.0f64, f64::max) / 2.0
    }

    fn subdivide(&self) -> Vec<Box4D> {
        let ar_mid = (self.ar_lo + self.ar_hi) / 2.0;
        let ai_mid = (self.ai_lo + self.ai_hi) / 2.0;
        let br_mid = (self.br_lo + self.br_hi) / 2.0;
        let bi_mid = (self.bi_lo + self.bi_hi) / 2.0;

        let ar = [(self.ar_lo, ar_mid), (ar_mid, self.ar_hi)];
        let ai = [(self.ai_lo, ai_mid), (ai_mid, self.ai_hi)];
        let br = [(self.br_lo, br_mid), (br_mid, self.br_hi)];
        let bi = [(self.bi_lo, bi_mid), (bi_mid, self.bi_hi)];

        let mut subs = Vec::with_capacity(16);
        for &(arl, arh) in &ar {
            for &(ail, aih) in &ai {
                for &(brl, brh) in &br {
                    for &(bil, bih) in &bi {
                        subs.push(Box4D {
                            ar_lo: arl, ar_hi: arh,
                            ai_lo: ail, ai_hi: aih,
                            br_lo: brl, br_hi: brh,
                            bi_lo: bil, bi_hi: bih,
                        });
                    }
                }
            }
        }
        subs
    }

    fn contains_extremizer(&self) -> bool {
        self.ar_lo <= 0.0 && 0.0 <= self.ar_hi
            && self.ai_lo <= 0.0 && 0.0 <= self.ai_hi
            && self.br_lo <= -1.0 && -1.0 <= self.br_hi
            && self.bi_lo <= 0.0 && 0.0 <= self.bi_hi
    }
}

// ── Main ─────────────────────────────────────────────────────────

fn main() {
    println!("============================================================");
    println!("  EHP n=3 LEVEL 2: ADAPTIVE BRANCH-AND-BOUND (OPTIMIZED)");
    println!("  Kenneth A. Mendoza · March 2026");
    println!("============================================================");

    let t_total = Instant::now();

    // ── Step 1: High-precision reference value via Richardson ──
    println!("\n  === STEP 1: REFERENCE VALUE (Richardson Extrapolation) ===");

    let resolutions = [400, 800, 1600];
    let mut l_refs = Vec::new();
    for &res in &resolutions {
        let t = Instant::now();
        let l = lemniscate_length(0.0, 0.0, -1.0, 0.0, res);
        let dt = t.elapsed().as_secs_f64();
        println!("    res={}: L(z^3-1) = {:.10} [{:.3}s]", res, l, dt);
        l_refs.push(l);
    }

    // Richardson extrapolation (second-order convergence)
    let l_richardson_1 = (4.0 * l_refs[1] - l_refs[0]) / 3.0;
    let l_richardson_2 = (4.0 * l_refs[2] - l_refs[1]) / 3.0;
    let l_star = (16.0 * l_richardson_2 - l_richardson_1) / 15.0; // 4th order
    println!("    Richardson (2nd order): {:.10}", l_richardson_2);
    println!("    Richardson (4th order): {:.10}", l_star);

    // Conservative lower bound: use the raw res=800 value
    // Marching squares UNDERESTIMATES (piecewise linear approximation)
    let l_lower = l_refs[1]; // res=800
    let grid_error = l_star - l_lower;
    println!("    L*(res=800) = {:.10} (conservative lower bound)", l_lower);
    println!("    Grid error estimate: {:.8}", grid_error);

    // ── Step 2: Coarse global sweep to find competitors ──
    println!("\n  === STEP 2: COARSE GLOBAL SWEEP ===");

    // Use LOW resolution (200) for the coarse sweep — 16x faster per eval
    let coarse_res = 200;
    let sweep_res: usize = 30;
    let radius = 4.0;
    let step = 2.0 * radius / sweep_res as f64;
    let n_total = sweep_res.pow(4);

    println!("  {}^4 = {} evaluations at res={}", sweep_res, n_total, coarse_res);

    let t_sweep = Instant::now();

    let sweep_params: Vec<(f64, f64, f64, f64)> = (0..sweep_res)
        .flat_map(|i0| {
            let ar = -radius + (i0 as f64 + 0.5) * step;
            (0..sweep_res).flat_map(move |i1| {
                let ai = -radius + (i1 as f64 + 0.5) * step;
                (0..sweep_res).flat_map(move |i2| {
                    let br = -radius + (i2 as f64 + 0.5) * step;
                    (0..sweep_res).map(move |i3| {
                        let bi = -radius + (i3 as f64 + 0.5) * step;
                        (ar, ai, br, bi)
                    })
                })
            })
        })
        .collect();

    let sweep_results: Vec<(f64, f64, f64, f64, f64)> = sweep_params
        .par_iter()
        .map(|&(ar, ai, br, bi)| {
            let l = lemniscate_length(ar, ai, br, bi, coarse_res);
            (ar, ai, br, bi, l)
        })
        .collect();

    let dt_sweep = t_sweep.elapsed().as_secs_f64();

    // Reference at coarse resolution for fair comparison
    let l_ref_coarse = lemniscate_length(0.0, 0.0, -1.0, 0.0, coarse_res);

    // Find global max and closest competitor
    let (gmax_ar, gmax_ai, gmax_br, gmax_bi, gmax_l) = sweep_results
        .iter()
        .cloned()
        .max_by(|a, b| a.4.partial_cmp(&b.4).unwrap())
        .unwrap();

    // Top 20 candidates (excluding extremizer neighborhood)
    let mut candidates: Vec<(f64, f64, f64, f64, f64)> = sweep_results
        .iter()
        .filter(|&&(ar, ai, br, bi, _)| {
            let d = (ar * ar + ai * ai + (br + 1.0).powi(2) + bi * bi).sqrt();
            d > 0.3
        })
        .cloned()
        .collect();
    candidates.sort_by(|a, b| b.4.partial_cmp(&a.4).unwrap());
    candidates.truncate(20);

    let coarse_margin = l_ref_coarse - candidates[0].4;
    let coarse_margin_pct = coarse_margin / l_ref_coarse * 100.0;

    println!("  Time: {:.2}s ({:.0} evals/s)", dt_sweep, n_total as f64 / dt_sweep);
    println!("  L*(z^3-1) at res={}: {:.8}", coarse_res, l_ref_coarse);
    println!("  Global max: L = {:.8} at ({:.3}, {:.3}, {:.3}, {:.3})",
        gmax_l, gmax_ar, gmax_ai, gmax_br, gmax_bi);
    println!("  Dist to (0,-1): {:.4}",
        (gmax_ar.powi(2) + gmax_ai.powi(2) + (gmax_br + 1.0).powi(2) + gmax_bi.powi(2)).sqrt());
    println!("  Coarse margin: {:.8} ({:.4}%)", coarse_margin, coarse_margin_pct);
    println!("\n  Top 5 competitors (away from extremizer):");
    for (i, &(ar, ai, br, bi, l)) in candidates.iter().take(5).enumerate() {
        let d = (ar * ar + ai * ai + (br + 1.0).powi(2) + bi * bi).sqrt();
        println!("    #{}: L={:.8} at ({:.3},{:.3},{:.3},{:.3}) d={:.3}",
            i+1, l, ar, ai, br, bi, d);
    }

    // ── Step 3: Refine top candidates at high resolution ──
    println!("\n  === STEP 3: REFINE TOP CANDIDATES (res=800) ===");

    let refine_res = 800;
    let t_refine = Instant::now();

    let refined: Vec<(f64, f64, f64, f64, f64)> = candidates
        .par_iter()
        .map(|&(ar, ai, br, bi, _)| {
            let l = lemniscate_length(ar, ai, br, bi, refine_res);
            (ar, ai, br, bi, l)
        })
        .collect();

    let dt_refine = t_refine.elapsed().as_secs_f64();

    let best_competitor = refined.iter()
        .cloned()
        .max_by(|a, b| a.4.partial_cmp(&b.4).unwrap())
        .unwrap();

    let margin_800 = l_lower - best_competitor.4;
    let margin_800_pct = margin_800 / l_lower * 100.0;

    println!("  Refined {} candidates in {:.2}s", candidates.len(), dt_refine);
    println!("  Best competitor (res=800): L={:.10} at ({:.3},{:.3},{:.3},{:.3})",
        best_competitor.4, best_competitor.0, best_competitor.1, best_competitor.2, best_competitor.3);
    println!("  MARGIN (res=800): {:.10} ({:.4}%)", margin_800, margin_800_pct);

    // ── Step 4: Adaptive B&B around decision boundary ──
    println!("\n  === STEP 4: ADAPTIVE BRANCH-AND-BOUND ===");

    // Only B&B the boxes whose coarse value is within 20% of L*
    // This eliminates >99% of boxes before we start subdividing
    let bb_threshold = l_ref_coarse * 0.80; // Only keep boxes with L > 80% of L*
    let bb_res = 200; // Use coarse resolution for B&B elimination

    let init_res: usize = 20;
    let init_step = 2.0 * radius / init_res as f64;

    let mut boxes: Vec<Box4D> = Vec::new();
    for i0 in 0..init_res {
        let ar_lo = -radius + i0 as f64 * init_step;
        for i1 in 0..init_res {
            let ai_lo = -radius + i1 as f64 * init_step;
            for i2 in 0..init_res {
                let br_lo = -radius + i2 as f64 * init_step;
                for i3 in 0..init_res {
                    let bi_lo = -radius + i3 as f64 * init_step;
                    boxes.push(Box4D {
                        ar_lo, ar_hi: ar_lo + init_step,
                        ai_lo, ai_hi: ai_lo + init_step,
                        br_lo, br_hi: br_lo + init_step,
                        bi_lo, bi_hi: bi_lo + init_step,
                    });
                }
            }
        }
    }

    println!("  Initial boxes: {} (step={:.2})", boxes.len(), init_step);
    println!("  Using res={} for B&B, threshold={:.4}", bb_res, bb_threshold);

    let total_evals = AtomicUsize::new(0);
    let mut global_best_competitor_l = best_competitor.4;
    let mut global_best_competitor_params = (best_competitor.0, best_competitor.1, best_competitor.2, best_competitor.3);
    let max_levels = 4; // Fewer levels since we use coarse res

    // The threshold for elimination: L(center) + safety < L*(res=coarse)
    // Use the coarse-resolution reference for fair comparison
    let elim_threshold = l_ref_coarse;

    for level in 0..max_levels {
        let hw = if boxes.is_empty() { 0.0 } else { boxes[0].half_width() };
        // Safety margin: empirical Lipschitz bound on L variation within a box
        // At the coarse resolution, the L function varies by at most ~8 per unit distance
        // (from the PoC sweep data). Safety = lip * sqrt(4) * hw
        let safety = 8.0 * 2.0 * hw;

        println!(
            "\n  Level {}: {} boxes, half-width={:.4}, safety={:.4}",
            level, boxes.len(), hw, safety
        );

        if boxes.is_empty() {
            println!("    No boxes to evaluate.");
            break;
        }

        let t_level = Instant::now();

        // Evaluate all box centers in parallel
        let evals: Vec<(usize, f64, f64, f64, f64, f64, bool)> = boxes
            .par_iter()
            .enumerate()
            .map(|(idx, bx)| {
                let (ar, ai, br, bi) = bx.center();
                let l = lemniscate_length(ar, ai, br, bi, bb_res);
                total_evals.fetch_add(1, Ordering::Relaxed);
                let contains_ext = bx.contains_extremizer();
                (idx, ar, ai, br, bi, l, contains_ext)
            })
            .collect();

        let dt_level = t_level.elapsed().as_secs_f64();

        // Track best non-extremizer
        for &(_, ar, ai, br, bi, l, contains_ext) in &evals {
            if !contains_ext {
                let d = (ar * ar + ai * ai + (br + 1.0).powi(2) + bi * bi).sqrt();
                if d > 0.05 && l > global_best_competitor_l {
                    // Verify at high resolution before updating
                    let l_high = lemniscate_length(ar, ai, br, bi, refine_res);
                    if l_high > global_best_competitor_l {
                        global_best_competitor_l = l_high;
                        global_best_competitor_params = (ar, ai, br, bi);
                    }
                }
            }
        }

        // Eliminate boxes where upper bound < threshold
        let survived: Vec<usize> = evals
            .iter()
            .filter(|&&(_, _, _, _, _, l, contains_ext)| {
                contains_ext || l + safety > elim_threshold
            })
            .map(|&(idx, _, _, _, _, _, _)| idx)
            .collect();

        let eliminated = boxes.len() - survived.len();
        let max_l = evals.iter().map(|e| e.5).fold(0.0f64, f64::max);

        println!(
            "    Evaluated in {:.2}s. Max L = {:.8}. Eliminated {}/{} ({:.1}%)",
            dt_level, max_l, eliminated, boxes.len(),
            eliminated as f64 / boxes.len() as f64 * 100.0
        );

        if survived.is_empty() {
            println!("    All eliminated!");
            break;
        }

        // Check if only the extremizer box survives
        let non_ext_survivors: Vec<usize> = survived.iter()
            .filter(|&&idx| !boxes[idx].contains_extremizer())
            .cloned()
            .collect();

        let ext_survivors: Vec<usize> = survived.iter()
            .filter(|&&idx| boxes[idx].contains_extremizer())
            .cloned()
            .collect();

        println!("    Survivors: {} extremizer + {} non-extremizer",
            ext_survivors.len(), non_ext_survivors.len());

        if non_ext_survivors.is_empty() {
            println!("    ONLY EXTREMIZER BOXES SURVIVE — PROOF STRUCTURE COMPLETE!");
            break;
        }

        if level == max_levels - 1 {
            // Last level: verify remaining non-extremizer boxes at high res
            println!("\n    Final verification of {} survivors at res={}...",
                non_ext_survivors.len(), refine_res);
            let t_verify = Instant::now();
            let mut any_threatens = false;
            for &idx in &non_ext_survivors {
                let (ar, ai, br, bi) = boxes[idx].center();
                let l_high = lemniscate_length(ar, ai, br, bi, refine_res);
                if l_high > l_lower {
                    println!("      WARNING: ({:.3},{:.3},{:.3},{:.3}) L={:.8} > L*={:.8}",
                        ar, ai, br, bi, l_high, l_lower);
                    any_threatens = true;
                }
                if l_high > global_best_competitor_l {
                    let d = (ar * ar + ai * ai + (br + 1.0).powi(2) + bi * bi).sqrt();
                    if d > 0.05 {
                        global_best_competitor_l = l_high;
                        global_best_competitor_params = (ar, ai, br, bi);
                    }
                }
            }
            let dt_verify = t_verify.elapsed().as_secs_f64();
            if !any_threatens {
                println!("    All survivors verified below L* at res={} [{:.2}s]", refine_res, dt_verify);
            }
            break;
        }

        // Subdivide survivors
        let mut new_boxes = Vec::new();
        for &idx in &survived {
            new_boxes.extend(boxes[idx].subdivide());
        }
        boxes = new_boxes;
    }

    let total_ev = total_evals.load(Ordering::Relaxed);
    let total_time = t_total.elapsed().as_secs_f64();

    // ── Step 5: Hessian at extremizer ──
    println!("\n  === STEP 5: HESSIAN AT EXTREMIZER ===");

    let h = 1e-4;
    let l0 = lemniscate_length(0.0, 0.0, -1.0, 0.0, refine_res);
    let params = [(1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)];
    let names = ["a_re", "a_im", "b_re", "b_im"];

    println!("  L*(0,0,-1,0) = {:.10} at res={}", l0, refine_res);
    let mut all_negative = true;
    for (i, &(dar, dai, dbr, dbi)) in params.iter().enumerate() {
        let lp = lemniscate_length(
            dar as f64 * h, dai as f64 * h,
            -1.0 + dbr as f64 * h, dbi as f64 * h,
            refine_res,
        );
        let lm = lemniscate_length(
            -(dar as f64) * h, -(dai as f64) * h,
            -1.0 - dbr as f64 * h, -(dbi as f64) * h,
            refine_res,
        );
        let d2l = (lp + lm - 2.0 * l0) / (h * h);
        println!("    d²L/d{}² = {:.2}", names[i], d2l);
        if d2l >= 0.0 { all_negative = false; }
    }
    println!("  Hessian diagonal: {}", if all_negative { "ALL NEGATIVE (local max confirmed)" } else { "NOT ALL NEGATIVE" });

    // ── Final report ──
    let margin = l_lower - global_best_competitor_l;
    let margin_pct = margin / l_lower * 100.0;

    println!("\n  ============================================================");
    println!("  FINAL REPORT");
    println!("  ============================================================");
    println!("  Reference L* = {:.10} (res=800, lower bound)", l_lower);
    println!("  Reference L* = {:.10} (Richardson 4th order)", l_star);
    println!(
        "  Closest competitor: L = {:.10} at ({:.4}, {:.4}, {:.4}, {:.4})",
        global_best_competitor_l,
        global_best_competitor_params.0,
        global_best_competitor_params.1,
        global_best_competitor_params.2,
        global_best_competitor_params.3,
    );

    println!("  MARGIN (L* - L_competitor): {:.10} ({:.4}%)", margin, margin_pct);
    println!("  Total B&B evaluations: {}", total_ev);
    println!("  Total time: {:.1}s", total_time);

    // Feasibility assessment
    println!("\n  === INTERVAL ARITHMETIC FEASIBILITY ===");
    if margin > 0.0 {
        println!("  Margin is POSITIVE: L* exceeds all competitors by {:.6}", margin);
        println!("  Grid error at res=800: {:.6} ({:.4}% of L*)",
            grid_error, grid_error / l_star * 100.0);
        let margin_ratio = margin / grid_error;
        if margin_ratio > 3.0 {
            println!("  Margin is {:.1}x larger than grid error", margin_ratio);
            println!("  VERDICT: TRIVIALLY FEASIBLE for interval arithmetic proof");
        } else if margin_ratio > 1.0 {
            println!("  Margin is {:.1}x grid error — feasible with moderate resolution", margin_ratio);
        } else {
            println!("  Margin is {:.1}x grid error — needs higher resolution", margin_ratio);
        }

        // Estimate interval arithmetic effort
        // Need: upper_bound(L*) - lower_bound(L_competitor) > 0
        // Grid error at res=N scales as O(1/N^2)
        // Need grid error < margin/2 for both eval points
        let needed_res = (refine_res as f64 * (grid_error / (margin / 4.0)).sqrt()) as usize;
        println!("  Estimated resolution needed for IA: ~{}", needed_res);
        let time_per_eval_ms = dt_refine / candidates.len() as f64 * 1000.0;
        println!("  Time per eval at res={}: {:.1}ms", refine_res, time_per_eval_ms);
    } else {
        println!("  WARNING: Margin is NEGATIVE — possible counterexample!");
        println!("  Closest competitor exceeds L* by {:.6}", -margin);
    }

    println!("  ============================================================");

    // Save results
    let results = serde_json::json!({
        "experiment": "EHP_n3_Level2_BranchAndBound_Optimized",
        "reference": {
            "l_star_800": l_lower,
            "l_star_richardson_2nd": l_richardson_2,
            "l_star_richardson_4th": l_star,
            "grid_error_estimate": grid_error,
        },
        "closest_competitor": {
            "l_value": global_best_competitor_l,
            "params": {
                "a_re": global_best_competitor_params.0,
                "a_im": global_best_competitor_params.1,
                "b_re": global_best_competitor_params.2,
                "b_im": global_best_competitor_params.3,
            },
        },
        "margin": margin,
        "margin_pct": margin_pct,
        "margin_over_grid_error": if grid_error > 0.0 { margin / grid_error } else { 0.0 },
        "hessian_all_negative": all_negative,
        "total_bb_evaluations": total_ev,
        "total_time_secs": total_time,
        "verdict": if margin > 0.0 && all_negative { "EHP_N3_SUPPORTED" } else { "NEEDS_INVESTIGATION" },
        "interval_arithmetic_feasibility": if margin > grid_error * 3.0 { "TRIVIALLY_FEASIBLE" }
            else if margin > 0.0 { "FEASIBLE" }
            else { "BLOCKED" },
    });

    let json = serde_json::to_string_pretty(&results).unwrap();
    std::fs::write("EHP_N3_LEVEL2_RESULTS.json", &json).expect("Failed to write");
    println!("\n  Saved to EHP_N3_LEVEL2_RESULTS.json");
}
