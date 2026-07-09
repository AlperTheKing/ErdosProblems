import Mathlib

example {α} (l : List α) {a : α} (h : a ∈ l) : ∃ i : Fin l.length, l.get i = a := by
  induction l with
  | nil => simp at h
  | cons b bs ih =>
      simp at h
      rcases h with hba | ha
      · refine ⟨⟨0, by simp⟩, ?_⟩
        simp [hba]
      · rcases ih ha with ⟨i, hi⟩
        refine ⟨⟨i.val + 1, by simp [i.isLt]⟩, ?_⟩
        exact hi
