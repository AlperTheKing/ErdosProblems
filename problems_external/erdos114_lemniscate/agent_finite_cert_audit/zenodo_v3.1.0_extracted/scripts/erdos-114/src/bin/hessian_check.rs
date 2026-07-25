//! Quick Hessian check: verify d²L/da_im² at the extremizer
//! with multiple resolutions and step sizes

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

fn main() {
    println!("=== HESSIAN INVESTIGATION AT EXTREMIZER ===\n");

    // Check L along a_im direction at multiple resolutions
    let resolutions = [400, 800, 1600, 3200];

    for &res in &resolutions {
        println!("Resolution = {}:", res);
        let l0 = lemniscate_length(0.0, 0.0, -1.0, 0.0, res);
        println!("  L(0, 0, -1, 0) = {:.12}", l0);

        for &h in &[0.1, 0.01, 0.001, 0.0001] {
            let lp = lemniscate_length(0.0, h, -1.0, 0.0, res);
            let lm = lemniscate_length(0.0, -h, -1.0, 0.0, res);
            let d2 = (lp + lm - 2.0 * l0) / (h * h);
            let dl = lp - l0;
            println!("  h={:.4}: L(0,+h,-1,0)={:.12}  delta={:+.2e}  d2L/dai2={:+.2e}", h, lp, dl, d2);
        }
        println!();
    }

    // Also check: is L(0, eps, -1, 0) > L(0, 0, -1, 0)?
    println!("=== CRITICAL: Does adding imaginary part to a INCREASE L? ===");
    let res = 1600;
    let l0 = lemniscate_length(0.0, 0.0, -1.0, 0.0, res);
    println!("L(a=0, b=-1) = {:.12}", l0);
    for &ai in &[0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0] {
        let l = lemniscate_length(0.0, ai, -1.0, 0.0, res);
        let diff = l - l0;
        println!("  L(a={}i, b=-1) = {:.12}  diff={:+.10}", ai, l, diff);
    }

    // But wait: the EHP conjecture is about MONIC polynomials of degree n.
    // z^3 + az + b with a = i*epsilon. Roots change.
    // The conjecture says among ALL monic degree-3 polys, z^3-1 is the max.
    // If L(0, eps, -1, 0) > L(0, 0, -1, 0), EHP IS FALSIFIED for n=3!
    println!("\n=== SYMMETRY CHECK: a_im should be equivalent by rotation ===");
    // p(z) = z^3 + i*eps*z - 1
    // Under rotation z -> z*e^{i*theta}, monic polynomial transforms.
    // For degree 3: z^3 + a*z + b -> z^3 + a*e^{-2i*theta}*z + b*e^{-3i*theta}
    // So (a=i*eps, b=-1) is equivalent to (a=eps*e^{i*(pi/2-2*theta)}, b=e^{-3i*theta})
    // Choosing theta=pi/4: a = eps*e^{i*0} = eps (real), b = e^{-3i*pi/4}
    // So L(a_im=eps) = L(some_rotated_polynomial) and we're comparing within the same orbit
    // The key: lemniscate length is a CONFORMAL INVARIANT under rotation!
    // So L(0, eps, -1, 0) = L(eps*cos(alpha), eps*sin(alpha), cos(beta), sin(beta))
    // for appropriate alpha, beta.
    // Check: L should be invariant under z -> z*e^{i*theta}
    println!("Rotation invariance check at res={}:", res);
    let l_original = lemniscate_length(0.0, 0.0, -1.0, 0.0, res);
    // z -> z*e^{i*pi/3}: a -> a*e^{-2i*pi/3}, b -> b*e^{-3i*pi/3} = b*e^{-i*pi} = -b
    // So (0, -1) -> (0, 1)
    let l_rotated = lemniscate_length(0.0, 0.0, 1.0, 0.0, res);
    println!("  L(a=0, b=-1) = {:.12}", l_original);
    println!("  L(a=0, b=+1) = {:.12}  (rotation z->z*w)", l_rotated);
    println!("  Difference: {:.2e}", (l_original - l_rotated).abs());
}
