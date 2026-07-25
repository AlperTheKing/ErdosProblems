import LeanCert
import LeanCert.Tactic.IntervalAuto

open LeanCert.Core LeanCert.Validity Real

/-! ## Smoke test: verify LeanCert works -/

-- Basic: prove exp(x) ≤ 3 on [0, 1]
example : ∀ x ∈ Set.Icc (0 : ℝ) 1, Real.exp x ≤ 3 := by
  certify_bound

-- Basic: prove π < 3.15
example : Real.pi < 3.15 := by
  interval_decide
